"""
StayService — lodging bookings that span nights, not ordered day stops.

A stay is a Place of kind lodging, held from check_in_day_number for
`nights` nights. The nightly rate is for the whole group and is never
multiplied by traveler_count.
"""
from app.infrastructure.db.models import TripStay
from app.modules.destination.repository import DestinationRepository
from app.modules.stay.repository import StayRepository
from app.modules.trip.service import TripService
from app.shared.exceptions import NotFoundError, ValidationDomainError
from app.shared.place_kind import PlaceKind, coerce_place_kind


class StayService:
    def __init__(
        self,
        trip_service: TripService,
        repo: StayRepository,
        destination_repo: DestinationRepository,
    ) -> None:
        self.trip_service = trip_service
        self.repo = repo
        self.destination_repo = destination_repo

    def list_stays(self, trip_id: str, owner_device_id: str) -> list[TripStay]:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        return self.repo.list_stays(trip.id)

    def add_stay(
        self,
        trip_id: str,
        owner_device_id: str,
        place_id: str,
        check_in_day_number: int,
        nights: int,
        nightly_rate: float | None = None,
        note: str | None = None,
        guest_count: int = 1,
    ) -> TripStay:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        place = self.destination_repo.get_place(place_id)
        if not place:
            raise NotFoundError(f"Place '{place_id}' not found.")
        if coerce_place_kind(place.kind) is not PlaceKind.LODGING:
            raise ValidationDomainError("Only lodging places can be added as a stay.")
        self._validate_window(trip, check_in_day_number, nights)
        self._ensure_one_stay_per_day(trip, check_in_day_number, nights)
        sort_index = _next_sort_index(trip, check_in_day_number)
        stay = TripStay(
            trip_id=trip.id,
            place_id=place.id,
            check_in_day_number=check_in_day_number,
            nights=nights,
            nightly_rate=nightly_rate,
            guest_count=max(1, int(guest_count or 1)),
            note=note.strip() if note else None,
            sort_index=sort_index,
        )
        created = self.repo.create_stay(stay)
        return self.repo.get_stay(created.id) or created

    def update_stay(
        self,
        trip_id: str,
        owner_device_id: str,
        stay_id: str,
        fields: dict,
    ) -> TripStay:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        stay = self._owned_stay(trip.id, stay_id)
        check_in = fields.get("check_in_day_number", stay.check_in_day_number)
        nights = fields.get("nights", stay.nights)
        self._validate_window(trip, check_in, nights)
        self._ensure_one_stay_per_day(trip, check_in, nights, exclude_stay_id=stay.id)
        stay.check_in_day_number = check_in
        stay.nights = nights
        if "nightly_rate" in fields:
            stay.nightly_rate = fields["nightly_rate"]
        if "guest_count" in fields and fields["guest_count"] is not None:
            stay.guest_count = max(1, int(fields["guest_count"]))
        if "note" in fields:
            note = fields["note"]
            stay.note = note.strip() if isinstance(note, str) and note.strip() else note
        return self.repo.get_stay(stay.id) or stay

    def remove_stay(self, trip_id: str, owner_device_id: str, stay_id: str) -> None:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        stay = self._owned_stay(trip.id, stay_id)
        self.repo.delete_stay(stay)

    def _owned_stay(self, trip_id: str, stay_id: str) -> TripStay:
        stay = self.repo.get_stay(stay_id)
        if not stay or stay.trip_id != trip_id:
            raise NotFoundError(f"Stay '{stay_id}' not found.")
        return stay

    @staticmethod
    def _validate_window(trip, check_in_day_number: int, nights: int) -> None:
        if nights < 1:
            raise ValidationDomainError("Nights must be at least 1.")
        day_numbers = {day.day_number for day in trip.days}
        if not day_numbers:
            raise ValidationDomainError("Add trip days before booking lodging.")
        if check_in_day_number not in day_numbers:
            raise ValidationDomainError("Check-in day must be one of this trip's days.")
        covered = set(range(check_in_day_number, check_in_day_number + nights))
        missing = covered - day_numbers
        if missing:
            raise ValidationDomainError(
                "Stay nights must fall within this trip's days. Shorten nights or add more days."
            )

    @staticmethod
    def _ensure_one_stay_per_day(trip, check_in_day_number: int, nights: int, exclude_stay_id: str | None = None) -> None:
        new_days = set(range(check_in_day_number, check_in_day_number + nights))
        for stay in getattr(trip, "stays", None) or []:
            if exclude_stay_id and stay.id == exclude_stay_id:
                continue
            existing_days = set(range(stay.check_in_day_number, stay.check_in_day_number + (stay.nights or 1)))
            if new_days & existing_days:
                raise ValidationDomainError("This day already has lodging.")


def _stay_covers_day(stay, day_number: int) -> bool:
    return stay.check_in_day_number <= day_number < stay.check_in_day_number + (stay.nights or 1)


def _next_sort_index(trip, check_in_day_number: int) -> int:
    indices: list[int] = []
    for day in getattr(trip, "days", None) or []:
        if day.day_number != check_in_day_number:
            continue
        for tp in getattr(day, "trip_places", None) or []:
            indices.append(tp.order_index)
    for stay in getattr(trip, "stays", None) or []:
        if _stay_covers_day(stay, check_in_day_number):
            indices.append(getattr(stay, "sort_index", 0) or 0)
    return max(indices, default=-1) + 1
