"""Pydantic DTOs for the Budget module."""
from pydantic import BaseModel, ConfigDict


class PlaceBudgetOut(BaseModel):
    trip_place_id: str
    place_id: str
    name: str
    fee: float | None = None
    line_total: float | None = None
    kind: str = "attraction"
    traveler_multiplier: int = 1


class DayBudgetOut(BaseModel):
    trip_day_id: str
    day_number: int
    estimated_total: float
    attractions_total: float = 0
    dining_total: float = 0
    places_with_unknown_fee: int
    places: list[PlaceBudgetOut] = []


class StayBudgetOut(BaseModel):
    stay_id: str
    place_id: str
    name: str
    check_in_day_number: int
    nights: int
    nightly_rate: float | None = None
    total: float | None = None


class ExpenseCreate(BaseModel):
    label: str
    amount: float


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    label: str
    amount: float


class TripBudgetOut(BaseModel):
    trip_id: str
    currency: str = "IRT"  # Iranian Toman
    traveler_count: int = 1
    estimated_total: float
    attractions_total: float = 0
    dining_total: float = 0
    lodging_total: float = 0
    expenses_total: float
    grand_total: float
    budget_cap: float | None = None
    is_over_budget: bool = False
    over_budget_amount: float = 0
    days: list[DayBudgetOut]
    stays: list[StayBudgetOut] = []
    expenses: list[ExpenseOut] = []
    places_with_unknown_fee: int
    stays_with_unknown_rate: int = 0
