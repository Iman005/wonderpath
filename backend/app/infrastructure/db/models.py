"""
SQLAlchemy ORM models.

This is the ONLY place entity/table structure is defined. Modules import
these models through their repositories — never directly in services or
controllers, to keep persistence details out of business logic.
"""
import uuid
from datetime import datetime, UTC

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.place_kind import DEFAULT_PLACE_KIND


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    google_sub: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Province(Base):
    __tablename__ = "provinces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(120), nullable=True)

    cities: Mapped[list["City"]] = relationship(back_populates="province", cascade="all, delete-orphan")


class City(Base):
    __tablename__ = "cities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(120), nullable=True)
    province_id: Mapped[str] = mapped_column(ForeignKey("provinces.id"), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Cache bookkeeping
    source_provider_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cached_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    province: Mapped["Province"] = relationship(back_populates="cities")
    places: Mapped[list["Place"]] = relationship(back_populates="city", cascade="all, delete-orphan")


class Place(Base):
    __tablename__ = "places"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    city_id: Mapped[str] = mapped_column(ForeignKey("cities.id"), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    address: Mapped[str | None] = mapped_column(String(400), nullable=True)

    # attraction | lodging | dining — see app/shared/place_kind.py. Decides
    # what estimated_entrance_fee means and whether it scales per traveler.
    kind: Mapped[str] = mapped_column(
        String(20), nullable=False, default=DEFAULT_PLACE_KIND.value, index=True
    )

    # Nullable by design — if the provider has no value, the user edits it manually.
    estimated_entrance_fee: Mapped[float | None] = mapped_column(Float, nullable=True)
    opening_hours: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # JSON blob for demo catalogs (rooms, menu, amenities). Real providers can
    # reuse the same shape later without another schema change.
    details_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Tracks which external provider/record this was cached from, for refresh/reconciliation.
    source_provider_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cached_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    city: Mapped["City"] = relationship(back_populates="places")


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_device_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    origin_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    origin_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    origin_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Total trip spend cap in Toman. Soft limit: overage warns rather than
    # blocking itinerary edits.
    budget_cap: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Scales per-person costs (attraction tickets, meals). Lodging is priced
    # per night for the whole group and is never multiplied by this.
    traveler_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # Public read-only snapshot. None means sharing is off.
    share_token: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    days: Mapped[list["TripDay"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan", order_by="TripDay.day_number"
    )
    expenses: Mapped[list["TripExpense"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan", order_by="TripExpense.created_at"
    )
    stays: Mapped[list["TripStay"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="TripStay.check_in_day_number",
    )


class TripDay(Base):
    __tablename__ = "trip_days"
    __table_args__ = (UniqueConstraint("trip_id", "day_number", name="uq_trip_day_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id"), nullable=False)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    trip: Mapped["Trip"] = relationship(back_populates="days")
    trip_places: Mapped[list["TripPlace"]] = relationship(
        back_populates="trip_day", cascade="all, delete-orphan", order_by="TripPlace.order_index"
    )


class TripPlace(Base):
    """Join entity: a Place attached to a specific TripDay, with ordering."""

    __tablename__ = "trip_places"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    trip_day_id: Mapped[str] = mapped_column(ForeignKey("trip_days.id"), nullable=False)
    place_id: Mapped[str] = mapped_column(ForeignKey("places.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Snapshot override — lets a user manually set/edit a fee even if the
    # provider had none, without mutating the shared cached Place row.
    # For attraction/dining this is the per-person unit fee; line_total uses party_size.
    custom_entrance_fee: Mapped[float | None] = mapped_column(Float, nullable=True)
    party_size: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    trip_day: Mapped["TripDay"] = relationship(back_populates="trip_places")
    place: Mapped["Place"] = relationship()


class TripStay(Base):
    """
    A lodging booking on a trip: one place, held for `nights` nights from
    `check_in_day_number`.

    Deliberately not a TripPlace: a hotel is not a stop in a day's ordered
    route, it spans days, and its cost is per night rather than per visit.
    """

    __tablename__ = "trip_stays"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    trip_id: Mapped[str] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    place_id: Mapped[str] = mapped_column(ForeignKey("places.id"), nullable=False)
    check_in_day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    nights: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Nightly price for the whole room/unit. Nullable — providers rarely
    # publish rates, so the traveler fills it in like an unknown entrance fee.
    nightly_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    guest_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Position among that day's mixed itinerary (places + this stay).
    sort_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    trip: Mapped["Trip"] = relationship(back_populates="stays")
    place: Mapped["Place"] = relationship()


class TripExpense(Base):
    """Trip-wide miscellaneous cost (food, transport) — not a place entrance fee."""

    __tablename__ = "trip_expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    trip: Mapped["Trip"] = relationship(back_populates="expenses")


class TripNote(Base):
    """A free-text note on a trip, optionally scoped to one day."""

    __tablename__ = "trip_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    trip_day_id: Mapped[str | None] = mapped_column(
        ForeignKey("trip_days.id", ondelete="CASCADE"), nullable=True, index=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    attachments: Mapped[list["NoteAttachment"]] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
        order_by="NoteAttachment.created_at",
    )


class NoteAttachment(Base):
    """Image (or other file) attached to a trip note — stored on disk, not in SQLite."""

    __tablename__ = "note_attachments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    note_id: Mapped[str] = mapped_column(
        ForeignKey("trip_notes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    note: Mapped["TripNote"] = relationship(back_populates="attachments")


class PackingList(Base):
    """A packing/gear checklist, optionally scoped to one day."""

    __tablename__ = "packing_lists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    trip_day_id: Mapped[str | None] = mapped_column(
        ForeignKey("trip_days.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    items: Mapped[list["PackingItem"]] = relationship(
        back_populates="packing_list",
        cascade="all, delete-orphan",
        order_by="PackingItem.order_index",
    )


class PackingItem(Base):
    __tablename__ = "packing_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    packing_list_id: Mapped[str] = mapped_column(
        ForeignKey("packing_lists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    is_checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    packing_list: Mapped["PackingList"] = relationship(back_populates="items")
