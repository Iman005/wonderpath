"""
Unit tests for BudgetService — TripService and BudgetRepository are mocked.
"""
from unittest.mock import MagicMock

import pytest

from app.modules.budget.service import BudgetService
from app.shared.exceptions import NotFoundError, ValidationDomainError
from app.shared.place_kind import PlaceKind


def test_two_travelers_multiply_attraction_fee():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = None
    trip.traveler_count = 1
    trip.stays = []
    place = _make_trip_place(fee=100000, party_size=2)
    place.place.kind = PlaceKind.ATTRACTION.value
    trip.days = [_make_day(1, [place])]

    result = _make_service(trip)[0].get_trip_budget("trip-1", "device-1")

    assert result.attractions_total == 200000
    assert result.estimated_total == 200000
    assert result.days[0].places[0].fee == 100000
    assert result.days[0].places[0].line_total == 200000
    assert result.days[0].places[0].traveler_multiplier == 2


def test_dining_is_per_person_lodging_is_not():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = None
    trip.traveler_count = 1
    meal = _make_trip_place(fee=200000, name="رستوران", party_size=3)
    meal.place.kind = PlaceKind.DINING.value
    trip.days = [_make_day(1, [meal])]
    stay = MagicMock()
    stay.id = "stay-1"
    stay.place_id = "hotel-1"
    stay.check_in_day_number = 1
    stay.nights = 2
    stay.nightly_rate = 1_000_000
    stay.place.name = "هتل"
    trip.stays = [stay]

    result = _make_service(trip)[0].get_trip_budget("trip-1", "device-1")

    assert result.dining_total == 600000
    assert result.lodging_total == 2_000_000
    assert result.grand_total == 2_600_000
    assert result.stays[0].total == 2_000_000


def test_unknown_stay_rate_is_flagged_not_zeroed():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = None
    trip.traveler_count = 1
    trip.days = []
    stay = MagicMock()
    stay.id = "stay-1"
    stay.place_id = "hotel-1"
    stay.check_in_day_number = 1
    stay.nights = 2
    stay.nightly_rate = None
    stay.place.name = "هتل"
    trip.stays = [stay]

    result = _make_service(trip)[0].get_trip_budget("trip-1", "device-1")

    assert result.lodging_total == 0
    assert result.stays_with_unknown_rate == 1
    assert result.stays[0].total is None


def _make_trip_place(fee=None, custom_fee=None, place_id="place-1", name="آزادی", party_size=1):
    tp = MagicMock()
    tp.id = f"tp-{place_id}"
    tp.place_id = place_id
    tp.custom_entrance_fee = custom_fee
    tp.party_size = party_size
    tp.place.estimated_entrance_fee = fee
    tp.place.name = name
    return tp


def _make_day(day_number, trip_places):
    day = MagicMock()
    day.id = f"day-{day_number}"
    day.day_number = day_number
    day.trip_places = trip_places
    return day


def _make_service(trip, expenses=None):
    trip_service = MagicMock()
    trip_service.get_trip.return_value = trip
    repo = MagicMock()
    repo.list_expenses.return_value = expenses or []
    return BudgetService(trip_service, repo), trip_service, repo


def test_uses_custom_fee_over_place_fee_when_set():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = None
    trip.days = [_make_day(1, [_make_trip_place(fee=100000, custom_fee=50000)])]

    result = _make_service(trip)[0].get_trip_budget("trip-1", "device-1")

    assert result.estimated_total == 50000
    assert result.grand_total == 50000
    assert result.places_with_unknown_fee == 0
    assert result.is_over_budget is False


def test_falls_back_to_place_fee_when_no_custom_fee():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = None
    trip.days = [_make_day(1, [_make_trip_place(fee=200000, custom_fee=None)])]

    result = _make_service(trip)[0].get_trip_budget("trip-1", "device-1")

    assert result.estimated_total == 200000


def test_counts_unknown_fee_without_breaking_total():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = None
    trip.days = [
        _make_day(1, [_make_trip_place(fee=None, custom_fee=None), _make_trip_place(fee=100000)])
    ]

    result = _make_service(trip)[0].get_trip_budget("trip-1", "device-1")

    assert result.estimated_total == 100000
    assert result.places_with_unknown_fee == 1
    assert result.days[0].places_with_unknown_fee == 1


def test_sums_across_multiple_days():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = None
    trip.days = [
        _make_day(1, [_make_trip_place(fee=100000)]),
        _make_day(2, [_make_trip_place(fee=250000), _make_trip_place(fee=50000)]),
    ]

    result = _make_service(trip)[0].get_trip_budget("trip-1", "device-1")

    assert result.estimated_total == 400000
    assert len(result.days) == 2
    assert result.days[1].estimated_total == 300000


def test_grand_total_is_places_plus_expenses():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = 7_000_000
    trip.days = [_make_day(1, [_make_trip_place(fee=1_500_000)])]
    food = MagicMock(id="exp-1", label="غذا", amount=5_000_000)

    result = _make_service(trip, [food])[0].get_trip_budget("trip-1", "device-1")

    assert result.estimated_total == 1_500_000
    assert result.expenses_total == 5_000_000
    assert result.grand_total == 6_500_000
    assert result.is_over_budget is False
    assert result.over_budget_amount == 0


def test_is_over_budget_false_when_equal_to_cap():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = 6_500_000
    trip.days = [_make_day(1, [_make_trip_place(fee=1_500_000)])]
    food = MagicMock(id="exp-1", label="غذا", amount=5_000_000)

    result = _make_service(trip, [food])[0].get_trip_budget("trip-1", "device-1")

    assert result.grand_total == 6_500_000
    assert result.is_over_budget is False
    assert result.over_budget_amount == 0


def test_is_over_budget_true_when_grand_total_exceeds_cap():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = 7_000_000
    trip.days = [_make_day(1, [_make_trip_place(fee=2_500_000)])]
    food = MagicMock(id="exp-1", label="غذا", amount=5_000_000)

    result = _make_service(trip, [food])[0].get_trip_budget("trip-1", "device-1")

    assert result.grand_total == 7_500_000
    assert result.is_over_budget is True
    assert result.over_budget_amount == 500_000


def test_is_over_budget_false_when_cap_is_unset():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = None
    trip.days = [_make_day(1, [_make_trip_place(fee=2_500_000)])]
    food = MagicMock(id="exp-1", label="غذا", amount=5_000_000)

    result = _make_service(trip, [food])[0].get_trip_budget("trip-1", "device-1")

    assert result.grand_total == 7_500_000
    assert result.is_over_budget is False
    assert result.over_budget_amount == 0


def test_over_budget_amount_is_zero_when_under_cap():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = 10_000_000
    trip.days = [_make_day(1, [_make_trip_place(fee=1_000_000)])]

    result = _make_service(trip)[0].get_trip_budget("trip-1", "device-1")

    assert result.is_over_budget is False
    assert result.over_budget_amount == 0


def test_add_expense_rejects_non_positive_amount():
    trip = MagicMock(id="trip-1")
    service, _, repo = _make_service(trip)

    with pytest.raises(ValidationDomainError):
        service.add_expense("trip-1", "device-1", "غذا", 0)
    with pytest.raises(ValidationDomainError):
        service.add_expense("trip-1", "device-1", "غذا", -1)
    repo.create_expense.assert_not_called()


def test_add_expense_rejects_blank_label():
    trip = MagicMock(id="trip-1")
    service, _, repo = _make_service(trip)

    with pytest.raises(ValidationDomainError):
        service.add_expense("trip-1", "device-1", "   ", 1000)
    repo.create_expense.assert_not_called()


def test_remove_expense_raises_not_found_for_other_trip():
    trip = MagicMock(id="trip-1")
    service, _, repo = _make_service(trip)
    repo.get_expense.return_value = MagicMock(id="exp-1", trip_id="trip-other")

    with pytest.raises(NotFoundError):
        service.remove_expense("trip-1", "device-1", "exp-1")
    repo.delete_expense.assert_not_called()


def test_day_budget_includes_place_line_items():
    trip = MagicMock()
    trip.id = "trip-1"
    trip.budget_cap = None
    trip.days = [_make_day(1, [_make_trip_place(fee=100000, name="حافظیه")])]

    result = _make_service(trip)[0].get_trip_budget("trip-1", "device-1")

    assert len(result.days[0].places) == 1
    assert result.days[0].places[0].name == "حافظیه"
    assert result.days[0].places[0].fee == 100000
