"""Budget controller — HTTP layer only."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.budget.dependencies import get_budget_service
from app.modules.budget.dtos import ExpenseCreate, ExpenseOut, TripBudgetOut
from app.modules.budget.service import BudgetService
from app.modules.identity.dependencies import get_current_device_id

router = APIRouter(prefix="/trips", tags=["Budget"])


@router.get("/{trip_id}/budget", response_model=TripBudgetOut)
def get_trip_budget(
    trip_id: str,
    device_id: str = Depends(get_current_device_id),
    service: BudgetService = Depends(get_budget_service),
):
    return service.get_trip_budget(trip_id, device_id)


@router.post(
    "/{trip_id}/budget/expenses",
    response_model=ExpenseOut,
    status_code=status.HTTP_201_CREATED,
)
def add_expense(
    trip_id: str,
    payload: ExpenseCreate,
    device_id: str = Depends(get_current_device_id),
    service: BudgetService = Depends(get_budget_service),
    db: Session = Depends(get_db),
):
    expense = service.add_expense(trip_id, device_id, payload.label, payload.amount)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{trip_id}/budget/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_expense(
    trip_id: str,
    expense_id: str,
    device_id: str = Depends(get_current_device_id),
    service: BudgetService = Depends(get_budget_service),
    db: Session = Depends(get_db),
):
    service.remove_expense(trip_id, device_id, expense_id)
    db.commit()
