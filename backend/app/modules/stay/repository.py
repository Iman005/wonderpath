"""StayRepository — persistence for trip lodging bookings."""
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.infrastructure.db.models import Place, TripStay


class StayRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_stays(self, trip_id: str) -> list[TripStay]:
        stmt = (
            select(TripStay)
            .options(selectinload(TripStay.place).selectinload(Place.city))
            .where(TripStay.trip_id == trip_id)
            .order_by(TripStay.check_in_day_number, TripStay.created_at)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_stay(self, stay_id: str) -> TripStay | None:
        stmt = (
            select(TripStay)
            .options(selectinload(TripStay.place).selectinload(Place.city))
            .where(TripStay.id == stay_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create_stay(self, stay: TripStay) -> TripStay:
        self.db.add(stay)
        self.db.flush()
        return stay

    def delete_stay(self, stay: TripStay) -> None:
        self.db.delete(stay)
        self.db.flush()
