"""FastAPI dependency wiring for the notebook module."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.notebook.repository import NotebookRepository
from app.modules.notebook.service import NotebookService
from app.modules.trip.dependencies import get_trip_service
from app.modules.trip.service import TripService


def get_notebook_service(
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> NotebookService:
    return NotebookService(trip_service, NotebookRepository(db))
