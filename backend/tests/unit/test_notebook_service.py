"""NotebookService domain rules — TripService and repository mocked."""
from unittest.mock import MagicMock

import pytest

from app.modules.notebook.service import NotebookService
from app.shared.exceptions import NotFoundError, ValidationDomainError


def _service(trip=None):
    trip_service = MagicMock()
    trip = trip or MagicMock(id="trip-1", days=[MagicMock(id="day-1", day_number=1)])
    trip_service.get_trip.return_value = trip
    repo = MagicMock()
    return NotebookService(trip_service, repo), repo, trip


def test_create_note_rejects_empty_body():
    service, repo, _ = _service()
    with pytest.raises(ValidationDomainError):
        service.create_note("trip-1", "device-1", "   ")
    repo.create_note.assert_not_called()


def test_create_note_rejects_unknown_day():
    service, repo, _ = _service()
    with pytest.raises(NotFoundError):
        service.create_note("trip-1", "device-1", "خرید بلیط", trip_day_id="missing")
    repo.create_note.assert_not_called()


def test_list_notes_for_day_passes_day_filter():
    service, repo, _ = _service()
    repo.list_notes.return_value = []
    service.list_notes("trip-1", "device-1", trip_day_id="day-1")
    repo.list_notes.assert_called_once_with("trip-1", "day-1")
