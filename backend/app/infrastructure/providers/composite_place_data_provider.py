"""Try Neshan first, then OSM, without leaking provider choice into services."""
from app.modules.destination.interfaces import IPlaceDataProvider, ProviderCity, ProviderPlace
from app.shared.exceptions import ExternalProviderError
from app.shared.place_kind import DEFAULT_PLACE_KIND, PlaceKind


class CompositePlaceDataProvider(IPlaceDataProvider):
    def __init__(self, primary: IPlaceDataProvider, fallback: IPlaceDataProvider) -> None:
        self.primary = primary
        self.fallback = fallback

    def search_cities(self, query: str) -> list[ProviderCity]:
        try:
            results = self.primary.search_cities(query)
            if results:
                return results
        except ExternalProviderError:
            pass
        return self.fallback.search_cities(query)

    def search_places(
        self,
        city_source_id: str,
        query: str | None = None,
        city_name: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        kind: PlaceKind = DEFAULT_PLACE_KIND,
    ) -> list[ProviderPlace]:
        try:
            results = self.primary.search_places(
                city_source_id,
                query,
                city_name=city_name,
                latitude=latitude,
                longitude=longitude,
                kind=kind,
            )
            if results:
                return results
        except ExternalProviderError:
            pass
        return self.fallback.search_places(
            city_source_id,
            query,
            city_name=city_name,
            latitude=latitude,
            longitude=longitude,
            kind=kind,
        )

    def get_place_details(self, place_source_id: str) -> ProviderPlace | None:
        try:
            details = self.primary.get_place_details(place_source_id)
            if details:
                return details
        except ExternalProviderError:
            pass
        return self.fallback.get_place_details(place_source_id)
