"""Stay controller — HTTP layer only."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.identity.dependencies import get_current_device_id
from app.modules.stay.dependencies import get_stay_service
from app.modules.stay.dtos import StayCreate, StayUpdate
from app.modules.stay.service import StayService
from app.modules.trip.dtos import TripStayOut

router = APIRouter(prefix="/trips", tags=["Stay"])


@router.post("/{trip_id}/stays", response_model=TripStayOut, status_code=status.HTTP_201_CREATED)
def add_stay(
    trip_id: str,
    payload: StayCreate,
    device_id: str = Depends(get_current_device_id),
    service: StayService = Depends(get_stay_service),
    db: Session = Depends(get_db),
):
    stay = service.add_stay(
        trip_id,
        device_id,
        payload.place_id,
        payload.check_in_day_number,
        payload.nights,
        nightly_rate=payload.nightly_rate,
        note=payload.note,
        guest_count=payload.guest_count,
    )
    db.commit()
    return stay


@router.put("/{trip_id}/stays/{stay_id}", response_model=TripStayOut)
def update_stay(
    trip_id: str,
    stay_id: str,
    payload: StayUpdate,
    device_id: str = Depends(get_current_device_id),
    service: StayService = Depends(get_stay_service),
    db: Session = Depends(get_db),
):
    stay = service.update_stay(trip_id, device_id, stay_id, payload.model_dump(exclude_unset=True))
    db.commit()
    return stay


@router.delete("/{trip_id}/stays/{stay_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_stay(
    trip_id: str,
    stay_id: str,
    device_id: str = Depends(get_current_device_id),
    service: StayService = Depends(get_stay_service),
    db: Session = Depends(get_db),
):
    service.remove_stay(trip_id, device_id, stay_id)
    db.commit()
