"""BudgetRepository — persistence for trip-wide miscellaneous expenses."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.models import TripExpense


class BudgetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_expenses(self, trip_id: str) -> list[TripExpense]:
        stmt = (
            select(TripExpense)
            .where(TripExpense.trip_id == trip_id)
            .order_by(TripExpense.created_at)
        )
        return list(self.db.execute(stmt).scalars().all())

    def create_expense(self, expense: TripExpense) -> TripExpense:
        self.db.add(expense)
        self.db.flush()
        return expense

    def get_expense(self, expense_id: str) -> TripExpense | None:
        return self.db.get(TripExpense, expense_id)

    def delete_expense(self, expense: TripExpense) -> None:
        self.db.delete(expense)
        self.db.flush()
