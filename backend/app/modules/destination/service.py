"""
DestinationService — business logic for searching cities and places.
Delegates cache-freshness decisions to PlaceCacheSync and pure data
reads to DestinationRepository; never touches the provider or the DB
session directly for anything beyond that delegation.
"""
from app.infrastructure.cache.place_cache_sync import PlaceCacheSync
from app.infrastructure.cache.route_distance_cache import RouteDistanceCache
from app.infrastructure.data.place_details import extra_image_urls
from app.infrastructure.db.models import City, Place
from app.infrastructure.providers.wikipedia_image import wikipedia_page_summary
from app.modules.destination.dtos import (
    CityOut,
    FeaturedPlaceOut,
    PlaceDetailOut,
    PlaceOut,
    to_city_out,
    to_place_detail_out,
    to_place_out,
)
from app.modules.destination.repository import DestinationRepository
from app.modules.trip.itinerary import search_origin_coords
from app.modules.trip.service import TripService
from app.shared.exceptions import NotFoundError, OwnershipError
from app.shared.geo import haversine_km
from app.shared.place_kind import DEFAULT_PLACE_KIND, PlaceKind, coerce_place_kind
from app.shared.text import SHORT_DESCRIPTION_MAX



def _prefer_demo_catalog(places: list[Place], kind: PlaceKind) -> list[Place]:
    """When a city has seeded demo lodging/dining, hide empty OSM leftovers."""
    kind = coerce_place_kind(kind)
    if kind not in (PlaceKind.LODGING, PlaceKind.DINING):
        return places
    seeded = [
        place
        for place in places
        if str(getattr(place, "source_provider_id", "") or "").startswith("seed:")
    ]
    return seeded or places


class DestinationService:
    def __init__(
        self,
        repo: DestinationRepository,
        cache_sync: PlaceCacheSync,
        trip_service: TripService | None = None,
        route_cache: RouteDistanceCache | None = None,
    ) -> None:
        self.repo = repo
        self.cache_sync = cache_sync
        self.trip_service = trip_service
        self.route_cache = route_cache

    def search_cities(
        self,
        query: str,
        *,
        trip_id: str | None = None,
        owner_device_id: str | None = None,
        day_number: int | None = None,
    ) -> list[CityOut]:
        if not query or not query.strip():
            return []
        cities = self.cache_sync.search_cities(query.strip())
        origin = self._trip_origin(trip_id, owner_device_id, day_number)
        ranked = sorted(cities, key=lambda city: self._city_search_rank(query.strip(), city))
        return [self._city_with_distance(city, origin, allow_fetch=True) for city in ranked]

    def list_places_for_city(
        self,
        city_id: str,
        *,
        trip_id: str | None = None,
        owner_device_id: str | None = None,
        kind: PlaceKind = DEFAULT_PLACE_KIND,
        day_number: int | None = None,
    ) -> list[PlaceOut]:
        city = self.repo.get_city(city_id)
        if not city:
            raise NotFoundError(f"City '{city_id}' not found.")
        places = self.cache_sync.get_places_for_city(city, kind=coerce_place_kind(kind))
        origin = self._trip_origin(trip_id, owner_device_id, day_number)
        city_leg = self._city_driving_leg(city, origin)
        return [
            self._place_with_distance(place, origin, city=city, city_leg=city_leg)
            for place in _prefer_demo_catalog(places, kind)
        ]

    def get_place(self, place_id: str) -> Place:
        place = self.repo.get_place(place_id)
        if not place:
            raise NotFoundError(f"Place '{place_id}' not found.")
        return place

    def get_city_out(self, city_id: str) -> CityOut:
        city = self.repo.get_city(city_id)
        if not city:
            raise NotFoundError(f"City '{city_id}' not found.")
        return to_city_out(city)

    def list_featured_places(self, limit: int = 12) -> list[FeaturedPlaceOut]:
        places = self.repo.list_featured_attractions(limit=limit)
        rows: list[FeaturedPlaceOut] = []
        for place in places:
            city = getattr(place, "city", None)
            province = getattr(city, "province", None) if city is not None else None
            rows.append(
                FeaturedPlaceOut(
                    id=place.id,
                    name=place.name,
                    description=place.description,
                    category=place.category,
                    image=place.image,
                    city_id=place.city_id,
                    city_name=getattr(city, "name", None) or "",
                    province_name=getattr(province, "name", None) if province is not None else None,
                )
            )
        return rows

    def get_place_details(self, place_id: str) -> PlaceDetailOut:
        place = self.get_place(place_id)
        description = place.description
        gallery = extra_image_urls(place.name, place.image)
        kind = coerce_place_kind(place.kind)
        needs_wiki = kind is PlaceKind.ATTRACTION and (
            (not description or len(description) < SHORT_DESCRIPTION_MAX) or len(gallery) == 0
        )
        if needs_wiki:
            wiki = wikipedia_page_summary(place.name)
            if wiki:
                if wiki.extract and (not description or len(wiki.extract) > len(description or "")):
                    description = wiki.extract
                for url in (wiki.original_image, wiki.thumbnail):
                    if url and url not in gallery and url != place.image:
                        gallery.append(url)
        return to_place_detail_out(place, description=description, extra_images=gallery)

    def _trip_origin(
        self,
        trip_id: str | None,
        owner_device_id: str | None,
        day_number: int | None = None,
    ) -> tuple[float, float] | None:
        if not trip_id or not owner_device_id or self.trip_service is None:
            return None
        try:
            trip = self.trip_service.get_trip(trip_id, owner_device_id)
        except (NotFoundError, OwnershipError):
            # Distance enrichment is optional — never fail the catalog for it.
            return None
        return search_origin_coords(trip, day_number)

    @staticmethod
    def _city_search_rank(query: str, city: City) -> tuple:
        q = query.strip()
        q_fold = q.casefold()
        name = (city.name or "").strip()
        name_en = (city.name_en or "").strip()
        if name == q or name_en.casefold() == q_fold:
            return (0, name)
        if name.startswith(q) or name_en.casefold().startswith(q_fold):
            return (1, name)
        return (2, name)

    def _city_with_distance(
        self,
        city: City,
        origin: tuple[float, float] | None,
        *,
        allow_fetch: bool = False,
    ) -> CityOut:
        distance_km: float | None = None
        duration_minutes: float | None = None
        is_driving = False
        if origin is not None and city.latitude is not None and city.longitude is not None:
            if self.route_cache is not None:
                distance_km, duration_minutes, is_driving = self.route_cache.driving_metrics(
                    origin[0],
                    origin[1],
                    city.latitude,
                    city.longitude,
                    allow_fetch=allow_fetch,
                )
            else:
                distance_km = haversine_km(origin[0], origin[1], city.latitude, city.longitude)
            if distance_km is not None:
                distance_km = round(distance_km, 1)
            if duration_minutes is not None:
                duration_minutes = round(duration_minutes, 0)
        return to_city_out(
            city,
            distance_from_origin_km=distance_km,
            duration_from_origin_minutes=duration_minutes,
            distance_is_driving=is_driving,
        )

    def _city_driving_leg(
        self,
        city: City,
        origin: tuple[float, float] | None,
    ) -> tuple[float | None, float | None, bool] | None:
        if origin is None or city.latitude is None or city.longitude is None or self.route_cache is None:
            return None
        return self.route_cache.driving_metrics(
            origin[0],
            origin[1],
            city.latitude,
            city.longitude,
            allow_fetch=True,
        )

    def _place_with_distance(
        self,
        place: Place,
        origin: tuple[float, float] | None,
        *,
        city: City | None = None,
        city_leg: tuple[float | None, float | None, bool] | None = None,
    ) -> PlaceOut:
        distance_km: float | None = None
        duration_minutes: float | None = None
        is_driving = False
        if origin is not None and place.latitude is not None and place.longitude is not None:
            if self.route_cache is not None:
                distance_km, duration_minutes, is_driving = self.route_cache.driving_metrics(
                    origin[0],
                    origin[1],
                    place.latitude,
                    place.longitude,
                    allow_fetch=False,
                )
            if not is_driving and city_leg is not None and city_leg[2] and city_leg[0] is not None:
                extra = 0.0
                if city is not None and city.latitude is not None and city.longitude is not None:
                    extra = haversine_km(city.latitude, city.longitude, place.latitude, place.longitude)
                distance_km = city_leg[0] + extra
                duration_minutes = city_leg[1]
                is_driving = True
            elif self.route_cache is None:
                distance_km = haversine_km(origin[0], origin[1], place.latitude, place.longitude)
            if distance_km is not None:
                distance_km = round(distance_km, 1)
            if duration_minutes is not None:
                duration_minutes = round(duration_minutes, 0)
        return to_place_out(
            place,
            distance_from_origin_km=distance_km,
            duration_from_origin_minutes=duration_minutes,
            distance_is_driving=is_driving,
        )
