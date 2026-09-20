"""
Map controller — HTTP layer only.

Note: this endpoint is an addition beyond the spec's minimal API
contract table, needed to fulfil the Map Module's stated responsibility
("map visualization only, via IMapProvider"). It returns render config
only — never the vendor API key — so the frontend's map widget still
needs its own public Neshan Maps SDK key for tile rendering.
"""
from fastapi import APIRouter, Depends, Query

from app.modules.identity.dependencies import get_current_device_id
from app.modules.map.dependencies import get_map_service
from app.modules.map.dtos import MapViewConfigOut
from app.modules.map.service import MapService

router = APIRouter(prefix="/trips", tags=["Map"])


@router.get("/{trip_id}/map", response_model=MapViewConfigOut)
def get_trip_map(
    trip_id: str,
    device_id: str = Depends(get_current_device_id),
    service: MapService = Depends(get_map_service),
    day_number: int | None = Query(default=None, ge=1),
):
    return service.get_trip_map_view(trip_id, device_id, day_number=day_number)
