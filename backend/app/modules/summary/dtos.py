"""Pydantic DTOs for the read-only Summary module."""
from datetime import datetime

from pydantic import BaseModel


class SummaryPlaceOut(BaseModel):
    place_id: str
    name: str
    category: str | None = None
    city_name: str
    estimated_entrance_fee: float | None = None
    note: str | None = None
    order_index: int
    kind: str = "attraction"


class SummaryStayOut(BaseModel):
    stay_id: str
    place_id: str
    name: str
    city_name: str | None = None
    check_in_day_number: int
    nights: int
    nightly_rate: float | None = None
    total: float | None = None


class SummaryDayOut(BaseModel):
    trip_day_id: str
    day_number: int
    date: datetime | None = None
    places: list[SummaryPlaceOut]
    estimated_day_total: float


class TripSummaryOut(BaseModel):
    trip_id: str
    trip_name: str
    traveler_count: int = 1
    days: list[SummaryDayOut]
    stays: list[SummaryStayOut] = []
    estimated_trip_total: float
    lodging_total: float = 0
