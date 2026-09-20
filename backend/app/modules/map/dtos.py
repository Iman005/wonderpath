"""Pydantic DTOs for the Map module."""
from pydantic import BaseModel, ConfigDict


class MapPinOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    place_id: str
    name: str
    latitude: float
    longitude: float
    sequence_index: int = 0


class RouteSegmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sequence_index: int
    origin_label: str
    destination_label: str
    encoded_polyline: str
    distance_meters: float
    duration_seconds: float
    is_current_leg: bool


class MapViewConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    provider: str
    center_latitude: float
    center_longitude: float
    zoom: int
    pins: list[MapPinOut]
    route_segments: list[RouteSegmentOut] = []
    style_url: str | None = None
