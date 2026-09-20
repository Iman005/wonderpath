"""Summary controller — HTTP layer only. Read-only by design (GET only)."""
from fastapi import APIRouter, Depends

from app.modules.identity.dependencies import get_current_device_id
from app.modules.summary.dependencies import get_summary_service
from app.modules.summary.dtos import TripSummaryOut
from app.modules.summary.service import SummaryService

router = APIRouter(prefix="/trips", tags=["Summary"])


@router.get("/{trip_id}/summary", response_model=TripSummaryOut)
def get_trip_summary(
    trip_id: str,
    device_id: str = Depends(get_current_device_id),
    service: SummaryService = Depends(get_summary_service),
):
    return service.get_trip_summary(trip_id, device_id)
