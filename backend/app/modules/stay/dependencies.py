"""FastAPI dependency wiring for the Stay module."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.destination.repository import DestinationRepository
from app.modules.stay.repository import StayRepository
from app.modules.stay.service import StayService
from app.modules.trip.dependencies import get_trip_service
from app.modules.trip.service import TripService


def get_stay_service(
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> StayService:
    return StayService(trip_service, StayRepository(db), DestinationRepository(db))
