"""
IMapProvider — abstraction over map *rendering* only (pins, routes,
viewport config). Deliberately separate from IPlaceDataProvider because
the data source (Neshan, Balad, ...) and the map renderer may change
independently of each other.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MapPin:
    place_id: str
    name: str
    latitude: float
    longitude: float
    sequence_index: int = 0


@dataclass(frozen=True)
class RouteSegment:
    sequence_index: int
    origin_label: str
    destination_label: str
    encoded_polyline: str
    distance_meters: float
    duration_seconds: float
    is_current_leg: bool


@dataclass(frozen=True)
class MapViewConfig:
    """Everything the frontend map widget needs to render a view: which
    tile/style config to use, the initial viewport, and the pins to draw.
    The frontend never talks to the map vendor's SDK/API key directly for
    anything beyond rendering tiles — vendor specifics stay server-side
    wherever this config crosses the network."""

    provider: str
    center_latitude: float
    center_longitude: float
    zoom: int
    pins: list[MapPin]
    route_segments: list[RouteSegment] = field(default_factory=list)
    style_url: str = "https://static.neshan.org/sdk/maplibre/styles/light.json"


class IMapProvider(ABC):
    @abstractmethod
    def build_view_config(
        self,
        pins: list[MapPin],
        center_latitude: float | None = None,
        center_longitude: float | None = None,
        route_segments: list[RouteSegment] | None = None,
    ) -> MapViewConfig:
        """Build a renderable map view for the given pins."""
        raise NotImplementedError

    @abstractmethod
    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        *,
        allow_straight_fallback: bool = True,
    ) -> RouteSegment | None:
        """Fetch a single origin→destination driving route.

        Returns None when the provider cannot produce a route for this
        pair (missing key, network error, empty result) so callers can
        skip the leg without failing the whole map view.

        allow_straight_fallback: when True (map drawing), a great-circle
        polyline may be returned so pins stay connected. Distance/ETA
        displays must pass False so air-line km is never treated as road.
        """
        raise NotImplementedError
