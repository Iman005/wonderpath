"""StayService domain rules — TripService and repositories mocked."""
from unittest.mock import MagicMock

import pytest

from app.modules.stay.service import StayService
from app.shared.exceptions import NotFoundError, ValidationDomainError
from app.shared.place_kind import PlaceKind


def _service(trip, place=None):
    trip_service = MagicMock()
    trip_service.get_trip.return_value = trip
    repo = MagicMock()
    destination_repo = MagicMock()
    destination_repo.get_place.return_value = place
    return StayService(trip_service, repo, destination_repo), repo, destination_repo


def _trip(days=(1, 2, 3)):
    trip = MagicMock()
    trip.id = "trip-1"
    trip.stays = []
    trip.days = [MagicMock(day_number=n, trip_places=[]) for n in days]
    return trip


def test_add_stay_rejects_missing_place():
    service, repo, _ = _service(_trip(), place=None)
    with pytest.raises(NotFoundError):
        service.add_stay("trip-1", "device-1", "ghost", 1, 2)
    repo.create_stay.assert_not_called()


def test_add_stay_rejects_non_lodging_place():
    place = MagicMock(id="p1", kind=PlaceKind.ATTRACTION.value)
    service, repo, _ = _service(_trip(), place=place)
    with pytest.raises(ValidationDomainError):
        service.add_stay("trip-1", "device-1", "p1", 1, 2)
    repo.create_stay.assert_not_called()


def test_add_stay_rejects_check_in_outside_trip_days():
    place = MagicMock(id="p1", kind=PlaceKind.LODGING.value)
    service, repo, _ = _service(_trip(days=(1, 2)), place=place)
    with pytest.raises(ValidationDomainError):
        service.add_stay("trip-1", "device-1", "p1", 5, 1)
    repo.create_stay.assert_not_called()


def test_add_stay_persists_valid_lodging():
    place = MagicMock(id="p1", kind=PlaceKind.LODGING.value)
    service, repo, _ = _service(_trip(), place=place)
    created = MagicMock()
    repo.create_stay.return_value = created
    repo.get_stay.return_value = created

    result = service.add_stay("trip-1", "device-1", "p1", 2, 2, nightly_rate=2_000_000)

    assert result is created
    stay = repo.create_stay.call_args[0][0]
    assert stay.place_id == "p1"
    assert stay.check_in_day_number == 2
    assert stay.nights == 2
    assert stay.nightly_rate == 2_000_000


def test_add_stay_rejects_nights_past_trip_end():
    place = MagicMock(id="p1", kind=PlaceKind.LODGING.value)
    service, repo, _ = _service(_trip(days=(1, 2)), place=place)
    with pytest.raises(ValidationDomainError, match="within this trip"):
        service.add_stay("trip-1", "device-1", "p1", 1, 3)
    repo.create_stay.assert_not_called()


def test_add_stay_rejects_second_lodging_on_same_day():
    trip = _trip()
    existing = MagicMock(id="s-old", check_in_day_number=2, nights=2)
    trip.stays = [existing]
    place = MagicMock(id="p1", kind=PlaceKind.LODGING.value)
    service, repo, _ = _service(trip, place=place)
    with pytest.raises(ValidationDomainError, match="already has lodging"):
        service.add_stay("trip-1", "device-1", "p1", 3, 1)
    repo.create_stay.assert_not_called()


def test_remove_stay_not_found_on_other_trip():
    trip = _trip()
    service, repo, _ = _service(trip)
    repo.get_stay.return_value = MagicMock(id="s1", trip_id="other")
    with pytest.raises(NotFoundError):
        service.remove_stay("trip-1", "device-1", "s1")
    repo.delete_stay.assert_not_called()
