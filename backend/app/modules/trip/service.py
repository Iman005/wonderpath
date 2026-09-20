"""
TripService — business logic for trip/day/place management.

Ownership enforcement lives here, applied uniformly before any
mutation or read of a specific trip: the requesting device's
owner_device_id must match Trip.owner_device_id, or an OwnershipError
(-> HTTP 403) is raised.
"""
import secrets
from datetime import datetime, timedelta, timezone

from app.infrastructure.db.models import Trip, TripDay, TripPlace
from app.modules.destination.repository import DestinationRepository
from app.modules.trip.repository import TripRepository
from app.shared.exceptions import NotFoundError, OwnershipError, ValidationDomainError
from app.shared.place_kind import PlaceKind, coerce_place_kind


class TripService:
    def __init__(self, repo: TripRepository, destination_repo: DestinationRepository) -> None:
        self.repo = repo
        self.destination_repo = destination_repo

    def _get_owned_trip(self, trip_id: str, owner_device_id: str) -> Trip:
        trip = self.repo.get_trip(trip_id)
        if not trip:
            raise NotFoundError(f"Trip '{trip_id}' not found.")
        if trip.owner_device_id != owner_device_id:
            raise OwnershipError("This trip does not belong to the requesting device.")
        return trip

    def _ensure_unique_trip_name(
        self,
        owner_device_id: str,
        name: str,
        *,
        exclude_trip_id: str | None = None,
    ) -> str:
        trimmed = name.strip()
        if not trimmed:
            raise ValidationDomainError("Trip name is required.")
        existing = self.repo.find_trip_by_owner_and_name(
            owner_device_id,
            trimmed,
            exclude_trip_id=exclude_trip_id,
        )
        if existing is not None:
            raise ValidationDomainError(
                "A trip with this name already exists. Choose a name that differs at least slightly."
            )
        return trimmed

    @staticmethod
    def _as_datetime(value: datetime) -> datetime:
        if isinstance(value, datetime):
            return datetime(value.year, value.month, value.day)
        return datetime(value.year, value.month, value.day)

    @staticmethod
    def _inclusive_day_count(start_date: datetime, end_date: datetime) -> int:
        start_day = start_date.date() if isinstance(start_date, datetime) else start_date
        end_day = end_date.date() if isinstance(end_date, datetime) else end_date
        return (end_day - start_day).days + 1

    @staticmethod
    def _ensure_start_date_not_in_past(start_date: datetime | None) -> None:
        if start_date is None:
            return
        start_day = start_date.date() if isinstance(start_date, datetime) else start_date
        today = datetime.now(timezone.utc).date()
        if start_day < today:
            raise ValidationDomainError("Trip start date cannot be before today.")

    def _validate_date_range(self, start_date: datetime, end_date: datetime) -> tuple[datetime, datetime]:
        start = self._as_datetime(start_date)
        end = self._as_datetime(end_date)
        self._ensure_start_date_not_in_past(start)
        count = self._inclusive_day_count(start, end)
        if count < 1:
            raise ValidationDomainError("Trip end date cannot be before the start date.")
        if count > 30:
            raise ValidationDomainError("A trip can have at most 30 days.")
        return start, end

    def planned_day_count(self, trip: Trip) -> int:
        if trip.start_date and trip.end_date:
            return max(self._inclusive_day_count(trip.start_date, trip.end_date), 1)
        return 1

    def _set_end_from_days(self, trip: Trip) -> None:
        if trip.start_date is None or not trip.days:
            return
        last_number = max(day.day_number for day in trip.days)
        trip.end_date = self._as_datetime(trip.start_date) + timedelta(days=last_number - 1)

    def set_date_range(self, trip_id: str, owner_device_id: str, start_date: datetime, end_date: datetime) -> Trip:
        trip = self._get_owned_trip(trip_id, owner_device_id)
        start, end = self._validate_date_range(start_date, end_date)
        wanted = self._inclusive_day_count(start, end)
        trip.start_date = start
        trip.end_date = end
        existing = sorted(trip.days, key=lambda day: day.day_number)
        if existing:
            while len(existing) > wanted:
                last = existing.pop()
                self.repo.delete_trip_day(last)
            start_number = max((day.day_number for day in existing), default=0) + 1
            for offset in range(wanted - len(existing)):
                day_number = start_number + offset
                date = self._resolve_day_date(trip, day_number, None)
                created = self.repo.create_trip_day(TripDay(trip_id=trip.id, day_number=day_number, date=date))
                existing.append(created)
            for day in existing:
                day.date = self._resolve_day_date(trip, day.day_number, None)
        self.repo.db.flush()
        return trip

    # --- Trip ---
    def create_trip(
        self,
        name: str,
        owner_device_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        origin_latitude: float | None = None,
        origin_longitude: float | None = None,
        origin_label: str | None = None,
        budget_cap: float | None = None,
        traveler_count: int = 1,
    ) -> Trip:
        unique_name = self._ensure_unique_trip_name(owner_device_id, name)
        resolved_end = end_date
        if start_date is not None:
            resolved_end = end_date or start_date
            start_date, resolved_end = self._validate_date_range(start_date, resolved_end)
        if traveler_count < 1:
            raise ValidationDomainError("Traveler count must be at least 1.")
        trip = Trip(
            name=unique_name,
            owner_device_id=owner_device_id,
            start_date=start_date,
            end_date=resolved_end,
            origin_latitude=origin_latitude,
            origin_longitude=origin_longitude,
            origin_label=origin_label,
            budget_cap=budget_cap,
            traveler_count=traveler_count,
        )
        return self.repo.create_trip(trip)

    def get_trip(self, trip_id: str, owner_device_id: str) -> Trip:
        return self._get_owned_trip(trip_id, owner_device_id)

    def update_trip(self, trip_id: str, owner_device_id: str, fields: dict) -> Trip:
        trip = self._get_owned_trip(trip_id, owner_device_id)
        if "name" in fields and fields["name"] is not None:
            trip.name = self._ensure_unique_trip_name(
                owner_device_id,
                fields["name"],
                exclude_trip_id=trip.id,
            )
        if "start_date" in fields or "end_date" in fields:
            next_start = fields.get("start_date", trip.start_date)
            next_end = fields.get("end_date", trip.end_date or next_start)
            if next_start is not None and next_end is not None:
                return self.set_date_range(trip_id, owner_device_id, next_start, next_end)
        for key in ("origin_latitude", "origin_longitude", "origin_label", "budget_cap", "traveler_count"):
            if key in fields:
                if key == "traveler_count" and fields[key] is not None and fields[key] < 1:
                    raise ValidationDomainError("Traveler count must be at least 1.")
                setattr(trip, key, fields[key])
        self.repo.db.flush()
        return trip

    def delete_trip(self, trip_id: str, owner_device_id: str) -> None:
        trip = self._get_owned_trip(trip_id, owner_device_id)
        self.repo.delete_trip(trip)

    # --- Trip Day ---
    def add_day(self, trip_id: str, owner_device_id: str, day_number: int, date=None) -> TripDay:
        trip = self._get_owned_trip(trip_id, owner_device_id)
        if any(d.day_number == day_number for d in trip.days):
            raise ValidationDomainError(f"Day {day_number} already exists on this trip.")
        resolved_date = self._resolve_day_date(trip, day_number, date)
        trip_day = TripDay(trip_id=trip.id, day_number=day_number, date=resolved_date)
        created = self.repo.create_trip_day(trip_day)
        if trip.start_date is not None:
            trip.end_date = self._as_datetime(trip.start_date) + timedelta(days=day_number - 1)
        return created

    def add_days_bulk(self, trip_id: str, owner_device_id: str, count: int) -> list[TripDay]:
        trip = self._get_owned_trip(trip_id, owner_device_id)
        if count < 1:
            raise ValidationDomainError("Day count must be at least 1.")
        start_number = max((d.day_number for d in trip.days), default=0) + 1
        created: list[TripDay] = []
        for offset in range(count):
            day_number = start_number + offset
            date = self._resolve_day_date(trip, day_number, None)
            trip_day = TripDay(trip_id=trip.id, day_number=day_number, date=date)
            created.append(self.repo.create_trip_day(trip_day))
        if trip.start_date is not None:
            last_number = start_number + count - 1
            trip.end_date = self._as_datetime(trip.start_date) + timedelta(days=last_number - 1)
        return created

    def remove_day(self, trip_id: str, owner_device_id: str, trip_day_id: str) -> None:
        """Delete one day and shift later days (and their plans) one slot earlier."""
        trip = self._get_owned_trip(trip_id, owner_device_id)
        target = next((day for day in trip.days if day.id == trip_day_id), None)
        if not target:
            raise NotFoundError(f"Trip day '{trip_day_id}' not found.")
        if len(trip.days) <= 1:
            raise ValidationDomainError("A trip must keep at least one day.")

        deleted_number = target.day_number
        later_days = sorted(
            [day for day in trip.days if day.day_number > deleted_number],
            key=lambda day: day.day_number,
        )
        self.repo.delete_trip_day(target)
        for offset, day in enumerate(later_days):
            day.day_number = 10_000 + offset
        self.repo.db.flush()
        for offset, day in enumerate(later_days):
            day.day_number = deleted_number + offset
            day.date = self._resolve_day_date(trip, day.day_number, None)
        self._shift_stays_after_removed_day(trip, deleted_number)
        remaining = [day for day in trip.days if day.id != trip_day_id]
        if trip.start_date is not None and remaining:
            last_number = max(day.day_number for day in remaining)
            trip.end_date = self._as_datetime(trip.start_date) + timedelta(days=last_number - 1)
        elif trip.start_date is not None:
            trip.end_date = self._as_datetime(trip.start_date)

    def remove_last_day(self, trip_id: str, owner_device_id: str) -> None:
        """Drops the highest-numbered day, so day numbering stays contiguous."""
        trip = self._get_owned_trip(trip_id, owner_device_id)
        if not trip.days:
            raise ValidationDomainError("This trip has no days to remove.")
        last_day = max(trip.days, key=lambda day: day.day_number)
        if len(trip.days) == 1:
            self.repo.delete_trip_day(last_day)
            if trip.start_date is not None:
                trip.end_date = self._as_datetime(trip.start_date)
            return
        self.remove_day(trip_id, owner_device_id, last_day.id)

    def _shift_stays_after_removed_day(self, trip: Trip, deleted_number: int) -> None:
        for stay in list(trip.stays or []):
            start = stay.check_in_day_number
            nights = stay.nights or 1
            end = start + nights
            if end <= deleted_number:
                continue
            if start > deleted_number:
                stay.check_in_day_number = start - 1
                continue
            nights -= 1
            if nights < 1:
                self.repo.db.delete(stay)
            else:
                stay.nights = nights

    @staticmethod
    def _resolve_day_date(trip: Trip, day_number: int, date: datetime | None) -> datetime | None:
        if date is not None:
            return date
        if trip.start_date is None:
            return None
        return trip.start_date + timedelta(days=day_number - 1)

    # --- Trip Place (add / reorder / remove) ---
    def add_place_to_day(
        self,
        trip_day_id: str,
        owner_device_id: str,
        place_id: str,
        note: str | None = None,
        custom_entrance_fee: float | None = None,
        allow_duplicate: bool = False,
        party_size: int = 1,
    ) -> TripPlace:
        trip_day = self._get_owned_trip_day(trip_day_id, owner_device_id)

        place = self.destination_repo.get_place(place_id)
        if not place:
            raise NotFoundError(f"Place '{place_id}' not found.")
        if coerce_place_kind(place.kind) is PlaceKind.LODGING:
            raise ValidationDomainError("Lodging must be added as a stay, not a day stop.")

        existing = self.repo.list_trip_places_for_day(trip_day.id)
        if not allow_duplicate and any(tp.place_id == place_id for tp in existing):
            raise ValidationDomainError("This place is already on this day.")
        trip = self._get_owned_trip(trip_day.trip_id, owner_device_id)
        next_order = _next_itinerary_index(trip, trip_day.day_number, existing)
        size = max(1, int(party_size or 1))

        trip_place = TripPlace(
            trip_day_id=trip_day.id,
            place_id=place_id,
            order_index=next_order,
            note=note,
            custom_entrance_fee=custom_entrance_fee,
            party_size=size,
        )
        return self.repo.create_trip_place(trip_place)

    def reorder_day_itinerary(
        self,
        trip_day_id: str,
        owner_device_id: str,
        items: list[tuple[str, str]],
    ) -> None:
        trip_day = self._get_owned_trip_day(trip_day_id, owner_device_id)
        trip = self._get_owned_trip(trip_day.trip_id, owner_device_id)
        places = {tp.id: tp for tp in trip_day.trip_places}
        stays = {
            stay.id: stay
            for stay in (trip.stays or [])
            if _stay_covers_day(stay, trip_day.day_number)
        }
        expected = {("place", place_id) for place_id in places} | {("stay", stay_id) for stay_id in stays}
        incoming = set(items)
        if incoming != expected:
            raise ValidationDomainError("Itinerary must include exactly this day's stops and lodging.")
        for index, (kind, item_id) in enumerate(items):
            if kind == "place":
                places[item_id].order_index = index
            else:
                stays[item_id].sort_index = index

    def reorder_places(self, trip_day_id: str, owner_device_id: str, ordered_trip_place_ids: list[str]) -> list[TripPlace]:
        trip_day = self._get_owned_trip_day(trip_day_id, owner_device_id)
        existing = self.repo.list_trip_places_for_day(trip_day.id)
        existing_ids = {tp.id for tp in existing}
        incoming_ids = set(ordered_trip_place_ids)

        if existing_ids != incoming_ids:
            raise ValidationDomainError("Reorder list must contain exactly the current trip places for this day.")

        by_id = {tp.id: tp for tp in existing}
        for index, tp_id in enumerate(ordered_trip_place_ids):
            by_id[tp_id].order_index = index

        return self.repo.list_trip_places_for_day(trip_day.id)

    def remove_place(self, trip_day_id: str, place_id: str, owner_device_id: str) -> None:
        trip_day = self._get_owned_trip_day(trip_day_id, owner_device_id)
        trip_places = [tp for tp in self.repo.list_trip_places_for_day(trip_day.id) if tp.place_id == place_id]
        if not trip_places:
            raise NotFoundError(f"Place '{place_id}' is not on this trip day.")
        for tp in trip_places:
            self.repo.delete_trip_place(tp)

    def remove_trip_place(self, trip_day_id: str, trip_place_id: str, owner_device_id: str) -> None:
        trip_day = self._get_owned_trip_day(trip_day_id, owner_device_id)
        trip_place = self.repo.get_trip_place(trip_place_id)
        if not trip_place or trip_place.trip_day_id != trip_day.id:
            raise NotFoundError(f"Stop '{trip_place_id}' is not on this trip day.")
        self.repo.delete_trip_place(trip_place)

    def update_place_fee(
        self,
        trip_day_id: str,
        place_id: str,
        owner_device_id: str,
        custom_entrance_fee: float | None,
        party_size: int | None = None,
    ) -> TripPlace:
        trip_day = self._get_owned_trip_day(trip_day_id, owner_device_id)
        trip_places = [tp for tp in self.repo.list_trip_places_for_day(trip_day.id) if tp.place_id == place_id]
        if not trip_places:
            raise NotFoundError(f"Place '{place_id}' is not on this trip day.")
        trip_place = trip_places[0]
        trip_place.custom_entrance_fee = custom_entrance_fee
        if party_size is not None:
            trip_place.party_size = max(1, int(party_size))
        self.repo.db.flush()
        return trip_place

    def enable_share(self, trip_id: str, owner_device_id: str) -> str:
        trip = self._get_owned_trip(trip_id, owner_device_id)
        if not trip.share_token:
            trip.share_token = secrets.token_urlsafe(24)
        self.repo.db.flush()
        return trip.share_token

    def get_trip_by_share_token(self, token: str) -> Trip:
        trip = self.repo.get_trip_by_share_token(token)
        if not trip:
            raise NotFoundError("Shared trip was not found.")
        return trip

    def _get_owned_trip_day(self, trip_day_id: str, owner_device_id: str) -> TripDay:
        trip_day = self.repo.get_trip_day(trip_day_id)
        if not trip_day:
            raise NotFoundError(f"Trip day '{trip_day_id}' not found.")
        # Ownership is transitively enforced through the parent trip.
        self._get_owned_trip(trip_day.trip_id, owner_device_id)
        return trip_day


def _stay_covers_day(stay, day_number: int) -> bool:
    check_in = getattr(stay, "check_in_day_number", None)
    nights = getattr(stay, "nights", 1) or 1
    if check_in is None:
        return False
    return check_in <= day_number < check_in + nights


def _next_itinerary_index(trip, day_number: int, places) -> int:
    indices = [tp.order_index for tp in places]
    for stay in getattr(trip, "stays", None) or []:
        if _stay_covers_day(stay, day_number):
            indices.append(getattr(stay, "sort_index", 0) or 0)
    return max(indices, default=-1) + 1
