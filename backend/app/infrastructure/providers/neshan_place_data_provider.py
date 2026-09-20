"""
NeshanPlaceDataProvider — concrete IPlaceDataProvider backed by the Neshan
API.

All Neshan-specific concerns (API key header, base URL, retries, timeout,
translating Neshan's response shape into our provider-agnostic DTOs, and
turning network/HTTP failures into ExternalProviderError) live in this
one file. Nothing above this layer (services, routers) knows Neshan
exists.
"""
import logging

import httpx

from app.core.config import get_settings
from app.modules.destination.interfaces import IPlaceDataProvider, ProviderCity, ProviderPlace
from app.shared.exceptions import ExternalProviderError
from app.shared.place_kind import DEFAULT_PLACE_KIND, PlaceKind

logger = logging.getLogger("wanderpath.providers.neshan_place")

settings = get_settings()

_MAX_RETRIES = 2
_TIMEOUT_SECONDS = 5.0

# Neshan's search endpoint has no kind facet, so the kind is expressed as a
# Persian search term when the traveler did not type one.
_DEFAULT_TERM_BY_KIND = {
    PlaceKind.LODGING: "هتل",
    PlaceKind.DINING: "رستوران",
}


class NeshanPlaceDataProvider(IPlaceDataProvider):
    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self._api_key = api_key if api_key is not None else settings.NESHAN_API_KEY
        self._base_url = base_url or settings.NESHAN_PLACE_BASE_URL

    def _headers(self) -> dict:
        return {"Api-Key": self._api_key}

    def _get(self, path: str, params: dict) -> dict:
        if not self._api_key:
            raise ExternalProviderError("Neshan API key is not configured.")

        last_error: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                with httpx.Client(timeout=_TIMEOUT_SECONDS) as client:
                    response = client.get(f"{self._base_url}{path}", params=params, headers=self._headers())
                    response.raise_for_status()
                    return response.json()
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                logger.warning("Neshan place API attempt %s/%s failed: %s", attempt, _MAX_RETRIES, exc)

        raise ExternalProviderError(f"Neshan place API unavailable: {last_error}")

    def search_cities(self, query: str) -> list[ProviderCity]:
        data = self._get("/search", {"term": query, "type": "city"})
        items = data.get("items", [])
        return [
            ProviderCity(
                source_id=str(item.get("id")),
                name=item.get("title", ""),
                name_en=item.get("title_en"),
                province_name=item.get("province", ""),
                latitude=item.get("location", {}).get("y"),
                longitude=item.get("location", {}).get("x"),
            )
            for item in items
        ]

    def search_places(
        self,
        city_source_id: str,
        query: str | None = None,
        city_name: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        kind: PlaceKind = DEFAULT_PLACE_KIND,
    ) -> list[ProviderPlace]:
        term = query or _DEFAULT_TERM_BY_KIND.get(kind, "")
        data = self._get("/search", {"city_id": city_source_id, "term": term})
        items = data.get("items", [])
        return [self._to_provider_place(item, kind) for item in items]

    def get_place_details(self, place_source_id: str) -> ProviderPlace | None:
        data = self._get(f"/places/{place_source_id}", {})
        if not data:
            return None
        return self._to_provider_place(data)

    @staticmethod
    def _to_provider_place(item: dict, kind: PlaceKind = DEFAULT_PLACE_KIND) -> ProviderPlace:
        return ProviderPlace(
            source_id=str(item.get("id")),
            name=item.get("title", ""),
            description=item.get("description"),
            category=item.get("category"),
            latitude=item.get("location", {}).get("y", 0.0),
            longitude=item.get("location", {}).get("x", 0.0),
            image=item.get("image"),
            estimated_entrance_fee=item.get("entrance_fee"),
            opening_hours=item.get("opening_hours"),
            kind=kind,
        )
