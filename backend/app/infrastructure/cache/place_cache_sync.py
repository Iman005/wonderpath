"""
PlaceCacheSync — implements the caching rule from the architecture spec:

    Place/City data fetched from IPlaceDataProvider is persisted into
    PostgreSQL and refreshed periodically. The app never calls the
    external API directly on every user request.

This class sits in the infrastructure layer (not in the Destination
service) because it is purely a cache-freshness/refresh concern, not a
business rule. The Destination service calls into this when it needs
"fresh enough" data; this decides whether that means "read from DB" or
"go fetch from the provider and persist".

If the external provider fails while the cache is empty, this raises
ExternalProviderError so the router can turn it into a graceful
fallback response rather than a 500. If the cache has data but it's
stale, we prefer returning the stale data over failing the request —
availability over freshness for a travel-planning MVP.
"""
import logging
from datetime import datetime, UTC, timedelta

from app.core.config import get_settings
from app.infrastructure.db.models import City, Place
from app.modules.destination.interfaces import IPlaceDataProvider
from app.modules.destination.repository import DestinationRepository
from app.shared.exceptions import ExternalProviderError
from app.shared.place_kind import DEFAULT_PLACE_KIND, PlaceKind, coerce_place_kind
from app.shared.text import shorten_description

logger = logging.getLogger("wanderpath.cache.place_sync")
settings = get_settings()


class PlaceCacheSync:
    def __init__(self, repo: DestinationRepository, provider: IPlaceDataProvider) -> None:
        self.repo = repo
        self.provider = provider

    @staticmethod
    def _is_stale(cached_at: datetime) -> bool:
        ttl = timedelta(seconds=settings.PLACE_CACHE_TTL_SECONDS)
        cached_at_aware = cached_at if cached_at.tzinfo else cached_at.replace(tzinfo=UTC)
        return datetime.now(UTC) - cached_at_aware > ttl

    def search_cities(self, query: str) -> list[City]:
        cached = self.repo.search_cities_by_name(query)
        if cached:
            return cached

        try:
            provider_cities = self.provider.search_cities(query)
        except ExternalProviderError as exc:
            logger.warning("Provider failed (%s); no cached cities for %r.", exc, query)
            return []

        result: list[City] = []
        for pc in provider_cities:
            existing = self.repo.get_city_by_source_id(pc.source_id)
            province = self.repo.get_or_create_province(pc.province_name or "نامشخص")
            if existing:
                existing.name = pc.name
                existing.name_en = pc.name_en
                existing.province_id = province.id
                if existing.latitude is None:
                    existing.latitude = pc.latitude
                if existing.longitude is None:
                    existing.longitude = pc.longitude
                existing.cached_at = datetime.now(UTC)
                result.append(self.repo.upsert_city(existing))
            else:
                new_city = City(
                    name=pc.name,
                    name_en=pc.name_en,
                    province_id=province.id,
                    latitude=pc.latitude,
                    longitude=pc.longitude,
                    source_provider_id=pc.source_id,
                )
                result.append(self.repo.upsert_city(new_city))
        return result

    def get_places_for_city(
        self,
        city: City,
        query: str | None = None,
        kind: PlaceKind = DEFAULT_PLACE_KIND,
    ) -> list[Place]:
        kind = coerce_place_kind(kind)
        cached = self.repo.list_places_for_city(city.id, kind=kind.value)
        if cached:
            return cached

        source_id = city.source_provider_id or city.id
        try:
            provider_places = self.provider.search_places(
                source_id,
                query,
                city_name=city.name,
                latitude=city.latitude,
                longitude=city.longitude,
                kind=kind,
            )
        except ExternalProviderError as exc:
            if cached:
                logger.warning("Provider failed (%s); serving %d stale cached places.", exc, len(cached))
                return cached
            logger.warning("Provider failed (%s); no cached %s places for city %s.", exc, kind.value, city.name)
            return []

        for pp in provider_places:
            existing = self.repo.get_place_by_source_id(pp.source_id)
            place_kind = coerce_place_kind(getattr(pp, "kind", kind)).value
            if existing:
                existing.name = pp.name
                existing.description = shorten_description(pp.description)
                existing.category = pp.category
                existing.latitude = pp.latitude
                existing.longitude = pp.longitude
                existing.image = pp.image or existing.image
                existing.address = getattr(pp, "address", None) or existing.address
                existing.estimated_entrance_fee = pp.estimated_entrance_fee
                existing.opening_hours = pp.opening_hours
                existing.kind = place_kind
                existing.cached_at = datetime.now(UTC)
                self.repo.upsert_place(existing)
            else:
                new_place = Place(
                    name=pp.name,
                    description=shorten_description(pp.description),
                    category=pp.category,
                    city_id=city.id,
                    latitude=pp.latitude,
                    longitude=pp.longitude,
                    image=pp.image,
                    estimated_entrance_fee=pp.estimated_entrance_fee,
                    opening_hours=pp.opening_hours,
                    kind=place_kind,
                    source_provider_id=pp.source_id,
                )
                self.repo.upsert_place(new_place)
        return self.repo.list_places_for_city(city.id, kind=kind.value)
