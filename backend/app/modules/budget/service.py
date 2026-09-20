"""
BudgetService — computes estimated daily and total trip costs, and
manages miscellaneous (non-place) expenses.

A TripPlace's unit cost is its custom_entrance_fee if the user set one,
otherwise the cached Place.estimated_entrance_fee. The meaning of that
unit depends on Place.kind:

    attraction / dining -> per person, multiplied by TripPlace.party_size
    lodging             -> not used here; lodging lives on TripStay

If neither fee is known, that place contributes 0 but is counted in
places_with_unknown_fee so the UI can flag the estimate as incomplete.

Lodging: nightly_rate * nights, for the whole group (never multiplied).
Unknown nightly_rate is counted in stays_with_unknown_rate.

grand_total = attractions + dining + lodging + expenses.
budget_cap is a soft cap: exceeding it is reported (is_over_budget) so
the traveler can raise the cap or change the plan. It never blocks edits.
"""
from app.infrastructure.db.models import Trip, TripExpense
from app.modules.budget.dtos import (
    DayBudgetOut,
    ExpenseOut,
    PlaceBudgetOut,
    StayBudgetOut,
    TripBudgetOut,
)
from app.modules.budget.repository import BudgetRepository
from app.modules.trip.service import TripService
from app.shared.exceptions import NotFoundError, ValidationDomainError
from app.shared.place_kind import PlaceKind, coerce_place_kind, is_per_person


def _place_fee(trip_place) -> float | None:
    fee = trip_place.custom_entrance_fee
    if fee is not None:
        return fee
    place = getattr(trip_place, "place", None)
    if place is None:
        return None
    return place.estimated_entrance_fee


def _party_size(trip_place) -> int:
    raw = getattr(trip_place, "party_size", 1)
    try:
        return max(1, int(raw))
    except (TypeError, ValueError):
        return 1


def _traveler_count(trip) -> int:
    raw = getattr(trip, "traveler_count", 1)
    try:
        return max(1, int(raw))
    except (TypeError, ValueError):
        return 1


def _iter_stays(trip) -> list:
    stays = getattr(trip, "stays", None)
    if isinstance(stays, (list, tuple)):
        return list(stays)
    return []


class BudgetService:
    def __init__(self, trip_service: TripService, repo: BudgetRepository) -> None:
        self.trip_service = trip_service
        self.repo = repo

    def get_trip_budget(self, trip_id: str, owner_device_id: str) -> TripBudgetOut:
        trip: Trip = self.trip_service.get_trip(trip_id, owner_device_id)
        return self._to_budget(trip)

    def budget_for_trip(self, trip: Trip) -> TripBudgetOut:
        return self._to_budget(trip)

    def add_expense(self, trip_id: str, owner_device_id: str, label: str, amount: float) -> TripExpense:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        if amount <= 0:
            raise ValidationDomainError("Expense amount must be greater than zero.")
        trimmed = label.strip()
        if not trimmed:
            raise ValidationDomainError("Expense label is required.")
        return self.repo.create_expense(TripExpense(trip_id=trip.id, label=trimmed, amount=amount))

    def remove_expense(self, trip_id: str, owner_device_id: str, expense_id: str) -> None:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        expense = self.repo.get_expense(expense_id)
        if not expense or expense.trip_id != trip.id:
            raise NotFoundError(f"Expense '{expense_id}' not found.")
        self.repo.delete_expense(expense)

    def _to_budget(self, trip: Trip) -> TripBudgetOut:
        day_budgets: list[DayBudgetOut] = []
        attractions_total = 0.0
        dining_total = 0.0
        total_unknown = 0
        travelers = _traveler_count(trip)

        for day in trip.days:
            day_attractions = 0.0
            day_dining = 0.0
            day_unknown = 0
            place_rows: list[PlaceBudgetOut] = []
            for tp in day.trip_places:
                place = getattr(tp, "place", None)
                kind = coerce_place_kind(getattr(place, "kind", None) if place is not None else None)
                fee = _place_fee(tp)
                multiplier = _party_size(tp) if is_per_person(kind) else 1
                line_total = None if fee is None else fee * multiplier
                if line_total is None:
                    day_unknown += 1
                elif kind is PlaceKind.DINING:
                    day_dining += line_total
                else:
                    day_attractions += line_total
                place_rows.append(
                    PlaceBudgetOut(
                        trip_place_id=tp.id,
                        place_id=tp.place_id,
                        name=getattr(place, "name", None) or "",
                        fee=fee,
                        line_total=line_total,
                        kind=kind.value,
                        traveler_multiplier=multiplier,
                    )
                )

            day_total = day_attractions + day_dining
            day_budgets.append(
                DayBudgetOut(
                    trip_day_id=day.id,
                    day_number=day.day_number,
                    estimated_total=day_total,
                    attractions_total=day_attractions,
                    dining_total=day_dining,
                    places_with_unknown_fee=day_unknown,
                    places=place_rows,
                )
            )
            attractions_total += day_attractions
            dining_total += day_dining
            total_unknown += day_unknown

        stay_rows: list[StayBudgetOut] = []
        lodging_total = 0.0
        unknown_stays = 0
        for stay in _iter_stays(trip):
            place = getattr(stay, "place", None)
            rate = stay.nightly_rate
            nights = stay.nights or 0
            total = None if rate is None else rate * nights
            if total is None:
                unknown_stays += 1
            else:
                lodging_total += total
            stay_rows.append(
                StayBudgetOut(
                    stay_id=stay.id,
                    place_id=stay.place_id,
                    name=getattr(place, "name", None) or "",
                    check_in_day_number=stay.check_in_day_number,
                    nights=nights,
                    nightly_rate=rate,
                    total=total,
                )
            )

        expenses = self.repo.list_expenses(trip.id)
        expenses_total = sum(item.amount for item in expenses)
        estimated_total = attractions_total + dining_total
        grand_total = estimated_total + lodging_total + expenses_total
        cap = trip.budget_cap

        is_over_budget = False
        over_budget_amount = 0.0
        if cap is not None and grand_total > cap:
            is_over_budget = True
            over_budget_amount = grand_total - cap

        return TripBudgetOut(
            trip_id=trip.id,
            traveler_count=travelers,
            estimated_total=estimated_total,
            attractions_total=attractions_total,
            dining_total=dining_total,
            lodging_total=lodging_total,
            expenses_total=expenses_total,
            grand_total=grand_total,
            budget_cap=cap,
            is_over_budget=is_over_budget,
            over_budget_amount=over_budget_amount,
            days=day_budgets,
            stays=stay_rows,
            expenses=[
                ExpenseOut(id=item.id, label=item.label, amount=item.amount) for item in expenses
            ],
            places_with_unknown_fee=total_unknown,
            stays_with_unknown_rate=unknown_stays,
        )
