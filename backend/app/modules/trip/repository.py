"""TripRepository — data access only. No business rules, no ownership checks."""
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.db.models import Place, Trip, TripDay, TripPlace, TripStay


class TripRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _trip_with_relations_stmt(self):
        return select(Trip).options(
            selectinload(Trip.days)
            .selectinload(TripDay.trip_places)
            .selectinload(TripPlace.place)
            .selectinload(Place.city),
            selectinload(Trip.stays).selectinload(TripStay.place).selectinload(Place.city),
        )

    def create_trip(self, trip: Trip) -> Trip:
        self.db.add(trip)
        self.db.flush()
        return trip

    def get_trip(self, trip_id: str) -> Trip | None:
        stmt = self._trip_with_relations_stmt().where(Trip.id == trip_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_trip_by_share_token(self, token: str) -> Trip | None:
        if not token or not token.strip():
            return None
        stmt = self._trip_with_relations_stmt().where(Trip.share_token == token.strip())
        return self.db.execute(stmt).scalar_one_or_none()

    def list_trips_for_device(self, owner_device_id: str) -> list[Trip]:
        stmt = self._trip_with_relations_stmt().where(Trip.owner_device_id == owner_device_id)
        return list(self.db.execute(stmt).scalars().all())

    def find_trip_by_owner_and_name(
        self,
        owner_device_id: str,
        name: str,
        *,
        exclude_trip_id: str | None = None,
    ) -> Trip | None:
        """Case-insensitive exact name match for this owner (trimmed)."""
        needle = name.strip().casefold()
        if not needle:
            return None
        for trip in self.list_trips_for_device(owner_device_id):
            if exclude_trip_id and trip.id == exclude_trip_id:
                continue
            if (trip.name or "").strip().casefold() == needle:
                return trip
        return None

    def delete_trip(self, trip: Trip) -> None:
        self.db.delete(trip)

    def create_trip_day(self, trip_day: TripDay) -> TripDay:
        self.db.add(trip_day)
        self.db.flush()
        return trip_day

    def get_trip_day(self, trip_day_id: str) -> TripDay | None:
        return self.db.get(TripDay, trip_day_id)

    def delete_trip_day(self, trip_day: TripDay) -> None:
        self.db.delete(trip_day)
        self.db.flush()

    def create_trip_place(self, trip_place: TripPlace) -> TripPlace:
        self.db.add(trip_place)
        self.db.flush()
        return trip_place

    def get_trip_place(self, trip_place_id: str) -> TripPlace | None:
        return self.db.get(TripPlace, trip_place_id)

    def delete_trip_place(self, trip_place: TripPlace) -> None:
        self.db.delete(trip_place)

    def list_trip_places_for_day(self, trip_day_id: str) -> list[TripPlace]:
        stmt = select(TripPlace).where(TripPlace.trip_day_id == trip_day_id).order_by(TripPlace.order_index)
        return list(self.db.execute(stmt).scalars().all())
