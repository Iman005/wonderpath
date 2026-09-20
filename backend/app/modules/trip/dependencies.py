"""FastAPI dependency wiring for the Trip module."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.destination.repository import DestinationRepository
from app.modules.trip.repository import TripRepository
from app.modules.trip.service import TripService


def get_trip_service(db: Session = Depends(get_db)) -> TripService:
    repo = TripRepository(db)
    destination_repo = DestinationRepository(db)
    return TripService(repo, destination_repo)
