"""FastAPI dependency wiring for the Map module."""
from fastapi import Depends

from app.infrastructure.providers.neshan_map_provider import NeshanMapProvider
from app.modules.map.service import MapService
from app.modules.trip.dependencies import get_trip_service
from app.modules.trip.service import TripService


def get_map_service(trip_service: TripService = Depends(get_trip_service)) -> MapService:
    return MapService(NeshanMapProvider(), trip_service)
