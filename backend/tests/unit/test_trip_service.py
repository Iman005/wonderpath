"""
Service layer tests for TripService, with repositories mocked — per the
spec's testing strategy ("Service layer tests — with mocked
repositories and mocked providers").
"""
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.modules.trip.service import TripService
from app.shared.exceptions import NotFoundError, OwnershipError, ValidationDomainError


def _make_service():
    repo = MagicMock()
    destination_repo = MagicMock()
    return TripService(repo, destination_repo), repo, destination_repo


def test_get_trip_raises_not_found_when_missing():
    service, repo, _ = _make_service()
    repo.get_trip.return_value = None

    with pytest.raises(NotFoundError):
        service.get_trip("missing-id", "device-1")


def test_get_trip_raises_ownership_error_for_wrong_device():
    service, repo, _ = _make_service()
    trip = MagicMock(owner_device_id="device-owner")
    repo.get_trip.return_value = trip

    with pytest.raises(OwnershipError):
        service.get_trip("trip-1", "device-intruder")


def test_get_trip_succeeds_for_owning_device():
    service, repo, _ = _make_service()
    trip = MagicMock(owner_device_id="device-1")
    repo.get_trip.return_value = trip

    result = service.get_trip("trip-1", "device-1")

    assert result is trip


def test_add_day_rejects_duplicate_day_number():
    service, repo, _ = _make_service()
    existing_day = MagicMock(day_number=1)
    trip = MagicMock(owner_device_id="device-1", days=[existing_day])
    repo.get_trip.return_value = trip

    with pytest.raises(ValidationDomainError):
        service.add_day("trip-1", "device-1", day_number=1)


def test_add_place_to_day_raises_not_found_for_missing_place():
    service, repo, destination_repo = _make_service()
    trip = MagicMock(owner_device_id="device-1")
    trip_day = MagicMock(id="day-1", trip_id="trip-1")
    repo.get_trip.return_value = trip
    repo.get_trip_day.return_value = trip_day
    destination_repo.get_place.return_value = None

    with pytest.raises(NotFoundError):
        service.add_place_to_day("day-1", "device-1", place_id="ghost-place")


def test_add_place_to_day_rejects_lodging():
    service, repo, destination_repo = _make_service()
    trip = MagicMock(owner_device_id="device-1", stays=[])
    trip_day = MagicMock(id="day-1", trip_id="trip-1", day_number=1)
    repo.get_trip.return_value = trip
    repo.get_trip_day.return_value = trip_day
    destination_repo.get_place.return_value = MagicMock(id="hotel-1", kind="lodging")

    with pytest.raises(ValidationDomainError):
        service.add_place_to_day("day-1", "device-1", place_id="hotel-1")
    repo.create_trip_place.assert_not_called()


def test_add_place_to_day_rejects_duplicate_without_flag():
    service, repo, destination_repo = _make_service()
    trip = MagicMock(owner_device_id="device-1", stays=[])
    trip_day = MagicMock(id="day-1", trip_id="trip-1", day_number=1)
    repo.get_trip.return_value = trip
    repo.get_trip_day.return_value = trip_day
    repo.list_trip_places_for_day.return_value = [MagicMock(place_id="p-1", order_index=0)]
    destination_repo.get_place.return_value = MagicMock(id="p-1", kind="attraction")

    with pytest.raises(ValidationDomainError, match="already"):
        service.add_place_to_day("day-1", "device-1", place_id="p-1")
    repo.create_trip_place.assert_not_called()


def test_add_place_to_day_allows_duplicate_when_flagged():
    service, repo, destination_repo = _make_service()
    trip = MagicMock(owner_device_id="device-1", stays=[])
    trip_day = MagicMock(id="day-1", trip_id="trip-1", day_number=1)
    repo.get_trip.return_value = trip
    repo.get_trip_day.return_value = trip_day
    repo.list_trip_places_for_day.return_value = [MagicMock(place_id="p-1", order_index=0)]
    destination_repo.get_place.return_value = MagicMock(id="p-1", kind="dining")
    created = MagicMock()
    repo.create_trip_place.return_value = created

    result = service.add_place_to_day("day-1", "device-1", place_id="p-1", allow_duplicate=True)

    assert result is created
    saved = repo.create_trip_place.call_args[0][0]
    assert saved.order_index == 1


def test_add_place_uses_shared_itinerary_index_with_stay():
    service, repo, destination_repo = _make_service()
    stay = MagicMock(id="stay-1", check_in_day_number=1, nights=1, sort_index=0)
    trip = MagicMock(owner_device_id="device-1", stays=[stay])
    trip_day = MagicMock(id="day-1", trip_id="trip-1", day_number=1)
    repo.get_trip.return_value = trip
    repo.get_trip_day.return_value = trip_day
    repo.list_trip_places_for_day.return_value = []
    destination_repo.get_place.return_value = MagicMock(id="p-1", kind="attraction")
    repo.create_trip_place.return_value = MagicMock()

    service.add_place_to_day("day-1", "device-1", place_id="p-1")

    saved = repo.create_trip_place.call_args[0][0]
    assert saved.order_index == 1


def test_remove_trip_place_deletes_one_stop():
    service, repo, _ = _make_service()
    trip = MagicMock(owner_device_id="device-1", stays=[])
    trip_day = MagicMock(id="day-1", trip_id="trip-1", day_number=1)
    trip_place = MagicMock(id="tp-1", trip_day_id="day-1")
    repo.get_trip.return_value = trip
    repo.get_trip_day.return_value = trip_day
    repo.get_trip_place.return_value = trip_place

    service.remove_trip_place("day-1", "tp-1", "device-1")

    repo.delete_trip_place.assert_called_once_with(trip_place)


def test_reorder_day_itinerary_assigns_shared_indices():
    service, repo, _ = _make_service()
    trip_day = MagicMock(id="day-1", trip_id="trip-1", day_number=1)
    tp = MagicMock(id="tp-1", order_index=0)
    stay = MagicMock(id="stay-1", check_in_day_number=1, nights=1, sort_index=1)
    trip_day.trip_places = [tp]
    trip = MagicMock(owner_device_id="device-1", stays=[stay], days=[trip_day])
    repo.get_trip.return_value = trip
    repo.get_trip_day.return_value = trip_day

    service.reorder_day_itinerary("day-1", "device-1", [("stay", "stay-1"), ("place", "tp-1")])

    assert stay.sort_index == 0
    assert tp.order_index == 1


def test_reorder_rejects_mismatched_id_set():
    service, repo, _ = _make_service()
    trip = MagicMock(owner_device_id="device-1")
    trip_day = MagicMock(id="day-1", trip_id="trip-1")
    repo.get_trip.return_value = trip
    repo.get_trip_day.return_value = trip_day
    tp1, tp2 = MagicMock(id="tp-1"), MagicMock(id="tp-2")
    repo.list_trip_places_for_day.return_value = [tp1, tp2]

    with pytest.raises(ValidationDomainError):
        service.reorder_places("day-1", "device-1", ordered_trip_place_ids=["tp-1"])  # missing tp-2


def test_create_trip_stores_end_date_range():
    service, repo, _ = _make_service()
    created = MagicMock()
    repo.create_trip.return_value = created
    repo.find_trip_by_owner_and_name.return_value = None
    start = datetime(2099, 8, 20)
    end = datetime(2099, 8, 23)

    service.create_trip("سفر شیراز", "device-1", start_date=start, end_date=end)

    saved = repo.create_trip.call_args[0][0]
    assert saved.start_date == start
    assert saved.end_date == end


def test_create_trip_rejects_end_before_start():
    service, repo, _ = _make_service()
    repo.find_trip_by_owner_and_name.return_value = None
    with pytest.raises(ValidationDomainError, match="end date"):
        service.create_trip(
            "سفر کوتاه",
            "device-1",
            start_date=datetime(2099, 8, 20),
            end_date=datetime(2099, 8, 19),
        )


def test_create_trip_stores_start_date_and_origin():
    service, repo, _ = _make_service()
    created = MagicMock()
    repo.create_trip.return_value = created
    repo.find_trip_by_owner_and_name.return_value = None
    start = datetime(2099, 8, 20)

    result = service.create_trip(
        "سفر شیراز",
        "device-1",
        start_date=start,
        origin_latitude=35.7,
        origin_longitude=51.4,
        origin_label="تهران، منزل",
        budget_cap=7_000_000,
    )

    saved = repo.create_trip.call_args[0][0]
    assert saved.name == "سفر شیراز"
    assert saved.start_date == start
    assert saved.origin_label == "تهران، منزل"
    assert saved.origin_latitude == 35.7
    assert saved.budget_cap == 7_000_000
    assert saved.traveler_count == 1
    assert result is created


def test_update_trip_persists_budget_cap():
    service, repo, _ = _make_service()
    trip = MagicMock(owner_device_id="device-1", budget_cap=None)
    repo.get_trip.return_value = trip

    result = service.update_trip("trip-1", "device-1", {"budget_cap": 7_000_000})

    assert result.budget_cap == 7_000_000
    repo.db.flush.assert_called()


def test_add_day_auto_dates_from_trip_start_date():
    service, repo, _ = _make_service()
    start = datetime(2026, 8, 20)
    trip = MagicMock(id="trip-1", owner_device_id="device-1", days=[], start_date=start)
    repo.get_trip.return_value = trip
    repo.create_trip_day.side_effect = lambda day: day

    day = service.add_day("trip-1", "device-1", day_number=3)

    assert day.date == datetime(2026, 8, 22)
    assert day.day_number == 3


def test_add_day_keeps_explicit_date_override():
    service, repo, _ = _make_service()
    trip = MagicMock(id="trip-1", owner_device_id="device-1", days=[], start_date=datetime(2026, 8, 20))
    repo.get_trip.return_value = trip
    repo.create_trip_day.side_effect = lambda day: day
    override = datetime(2026, 9, 1)

    day = service.add_day("trip-1", "device-1", day_number=1, date=override)

    assert day.date == override


def test_add_days_bulk_appends_after_existing_max():
    service, repo, _ = _make_service()
    existing = MagicMock(day_number=2)
    trip = MagicMock(
        id="trip-1",
        owner_device_id="device-1",
        days=[existing],
        start_date=datetime(2026, 8, 20),
    )
    repo.get_trip.return_value = trip
    repo.create_trip_day.side_effect = lambda day: day

    days = service.add_days_bulk("trip-1", "device-1", count=2)

    assert [d.day_number for d in days] == [3, 4]
    assert days[0].date == datetime(2026, 8, 22)
    assert days[1].date == datetime(2026, 8, 23)
    assert repo.create_trip_day.call_count == 2


def test_update_place_fee_sets_custom_entrance_fee():
    service, repo, _ = _make_service()
    trip = MagicMock(owner_device_id="device-1")
    trip_day = MagicMock(id="day-1", trip_id="trip-1")
    repo.get_trip.return_value = trip
    repo.get_trip_day.return_value = trip_day
    trip_place = MagicMock(id="tp-1", place_id="place-1", custom_entrance_fee=None)
    repo.list_trip_places_for_day.return_value = [trip_place]

    result = service.update_place_fee("day-1", "place-1", "device-1", 250000)

    assert result.custom_entrance_fee == 250000
    repo.db.flush.assert_called()


def test_create_trip_rejects_duplicate_name_for_same_owner():
    service, repo, _ = _make_service()
    repo.find_trip_by_owner_and_name.return_value = MagicMock(id="existing")

    with pytest.raises(ValidationDomainError, match="name"):
        service.create_trip("سفر شمال", "user-1", start_date=datetime(2099, 1, 1))

    repo.create_trip.assert_not_called()


def test_create_trip_rejects_past_start_date():
    service, repo, _ = _make_service()
    repo.find_trip_by_owner_and_name.return_value = None

    with pytest.raises(ValidationDomainError, match="start date"):
        service.create_trip("سفر تازه", "user-1", start_date=datetime(2020, 1, 1))

    repo.create_trip.assert_not_called()


def test_update_trip_rejects_duplicate_name():
    service, repo, _ = _make_service()
    trip = MagicMock(id="trip-1", owner_device_id="user-1", name="قدیمی")
    repo.get_trip.return_value = trip
    repo.find_trip_by_owner_and_name.return_value = MagicMock(id="trip-2")

    with pytest.raises(ValidationDomainError, match="name"):
        service.update_trip("trip-1", "user-1", {"name": "سفر تکراری"})
