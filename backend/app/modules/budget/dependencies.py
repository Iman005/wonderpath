"""FastAPI dependency wiring for the Budget module."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.budget.repository import BudgetRepository
from app.modules.budget.service import BudgetService
from app.modules.trip.dependencies import get_trip_service
from app.modules.trip.service import TripService


def get_budget_service(
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> BudgetService:
    return BudgetService(trip_service, BudgetRepository(db))
