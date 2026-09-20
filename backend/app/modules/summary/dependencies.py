"""FastAPI dependency wiring for the Summary module."""
from fastapi import Depends

from app.modules.summary.service import SummaryService
from app.modules.trip.dependencies import get_trip_service
from app.modules.trip.service import TripService


def get_summary_service(trip_service: TripService = Depends(get_trip_service)) -> SummaryService:
    return SummaryService(trip_service)
