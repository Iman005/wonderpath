"""
IPlaceDataProvider — abstraction over fetching city/place data (search,
details, entrance fees where available) from an external source.

Deliberately separate from IMapProvider (see app/modules/map/interfaces.py)
because the data source and the map renderer may change independently.

Implementations live in app/infrastructure/providers/ — API key handling,
rate limiting, retries, and network error handling all live there, never
in this interface or in the domain services that consume it.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.shared.place_kind import DEFAULT_PLACE_KIND, PlaceKind


@dataclass(frozen=True)
class ProviderCity:
    source_id: str
    name: str
    name_en: str | None
    province_name: str
    latitude: float | None
    longitude: float | None


@dataclass(frozen=True)
class ProviderPlace:
    source_id: str
    name: str
    description: str | None
    category: str | None
    latitude: float
    longitude: float
    image: str | None
    estimated_entrance_fee: float | None
    opening_hours: str | None
    # What this record is (attraction / lodging / dining). Providers that only
    # know about sightseeing can leave the default.
    kind: PlaceKind = field(default=DEFAULT_PLACE_KIND)


class IPlaceDataProvider(ABC):
    @abstractmethod
    def search_cities(self, query: str) -> list[ProviderCity]:
        raise NotImplementedError

    @abstractmethod
    def search_places(
        self,
        city_source_id: str,
        query: str | None = None,
        city_name: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        kind: PlaceKind = DEFAULT_PLACE_KIND,
    ) -> list[ProviderPlace]:
        raise NotImplementedError

    @abstractmethod
    def get_place_details(self, place_source_id: str) -> ProviderPlace | None:
        raise NotImplementedError
