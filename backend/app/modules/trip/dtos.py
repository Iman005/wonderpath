"""Pydantic DTOs for the Trip module's API surface."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.shared.place_kind import coerce_place_kind


# --- Requests ---

class TripCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    start_date: datetime
    end_date: datetime | None = None
    origin_latitude: float | None = None
    origin_longitude: float | None = None
    origin_label: str | None = Field(default=None, max_length=200)
    budget_cap: float | None = Field(default=None, ge=0)
    traveler_count: int = Field(default=1, ge=1, le=30)


class TripUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    start_date: datetime | None = None
    end_date: datetime | None = None
    origin_latitude: float | None = None
    origin_longitude: float | None = None
    origin_label: str | None = Field(default=None, max_length=200)
    budget_cap: float | None = Field(default=None, ge=0)
    traveler_count: int | None = Field(default=None, ge=1, le=30)


class TripDayCreate(BaseModel):
    day_number: int = Field(ge=1)
    date: datetime | None = None


class TripDaysBulkCreate(BaseModel):
    count: int = Field(ge=1, le=30)


class TripPlaceCreate(BaseModel):
    place_id: str
    note: str | None = None
    custom_entrance_fee: float | None = None
    party_size: int = Field(default=1, ge=1, le=50)
    allow_duplicate: bool = False


class TripPlaceReorder(BaseModel):
    ordered_trip_place_ids: list[str]


class ItineraryItemIn(BaseModel):
    kind: str = Field(pattern="^(place|stay)$")
    id: str


class DayItineraryReorder(BaseModel):
    items: list[ItineraryItemIn]


class TripPlaceUpdate(BaseModel):
    custom_entrance_fee: float | None = Field(default=None, ge=0)
    party_size: int | None = Field(default=None, ge=1, le=50)


# --- Responses ---

class TripPlaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    place_id: str
    order_index: int
    custom_entrance_fee: float | None = None
    party_size: int = 1
    note: str | None = None
    place_kind: str | None = None
    place_name: str | None = None
    city_id: str | None = None

    @model_validator(mode="wrap")
    @classmethod
    def _attach_place_fields(cls, value, handler):
        if hasattr(value, "place_id") and hasattr(value, "order_index"):
            place = getattr(value, "place", None)
            return handler(
                {
                    "id": value.id,
                    "place_id": value.place_id,
                    "order_index": value.order_index,
                    "custom_entrance_fee": value.custom_entrance_fee,
                    "party_size": getattr(value, "party_size", 1) or 1,
                    "note": value.note,
                    "place_kind": coerce_place_kind(getattr(place, "kind", None)).value if place is not None else None,
                    "place_name": getattr(place, "name", None) if place is not None else None,
                    "city_id": getattr(place, "city_id", None) if place is not None else None,
                }
            )
        return handler(value)


class TripStayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    place_id: str
    check_in_day_number: int
    nights: int
    nightly_rate: float | None = None
    guest_count: int = 1
    note: str | None = None
    place_name: str | None = None
    city_name: str | None = None
    city_id: str | None = None
    sort_index: int = 0

    @model_validator(mode="wrap")
    @classmethod
    def _attach_place_fields(cls, value, handler):
        if hasattr(value, "place_id") and hasattr(value, "check_in_day_number"):
            place = getattr(value, "place", None)
            city = getattr(place, "city", None) if place is not None else None
            return handler(
                {
                    "id": value.id,
                    "place_id": value.place_id,
                    "check_in_day_number": value.check_in_day_number,
                    "nights": value.nights,
                    "nightly_rate": value.nightly_rate,
                    "guest_count": getattr(value, "guest_count", 1) or 1,
                    "note": value.note,
                    "place_name": getattr(place, "name", None) if place is not None else None,
                    "city_name": getattr(city, "name", None) if city is not None else None,
                    "city_id": getattr(place, "city_id", None) if place is not None else None,
                    "sort_index": getattr(value, "sort_index", 0) or 0,
                }
            )
        return handler(value)


class TripDayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    day_number: int
    date: datetime | None = None
    trip_places: list[TripPlaceOut] = []


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    owner_device_id: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    origin_latitude: float | None = None
    origin_longitude: float | None = None
    origin_label: str | None = None
    budget_cap: float | None = None
    traveler_count: int = 1
    created_at: datetime
    updated_at: datetime
    days: list[TripDayOut] = []
    stays: list[TripStayOut] = []
