"""FastAPI dependency wiring for the Destination module (DI composition root)."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.cache.place_cache_sync import PlaceCacheSync
from app.infrastructure.cache.route_distance_cache import RouteDistanceCache
from app.infrastructure.providers.composite_place_data_provider import CompositePlaceDataProvider
from app.infrastructure.providers.neshan_map_provider import NeshanMapProvider
from app.infrastructure.providers.neshan_place_data_provider import NeshanPlaceDataProvider
from app.infrastructure.providers.osm_place_data_provider import OsmPlaceDataProvider
from app.modules.destination.repository import DestinationRepository
from app.modules.destination.service import DestinationService
from app.modules.trip.dependencies import get_trip_service
from app.modules.trip.service import TripService


def get_destination_service(
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> DestinationService:
    repo = DestinationRepository(db)
    provider = CompositePlaceDataProvider(NeshanPlaceDataProvider(), OsmPlaceDataProvider())
    cache_sync = PlaceCacheSync(repo, provider)
    route_cache = RouteDistanceCache(NeshanMapProvider())
    return DestinationService(repo, cache_sync, trip_service=trip_service, route_cache=route_cache)
