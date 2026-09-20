"""Pydantic DTOs for lodging stays on a trip."""
from pydantic import BaseModel, Field

from app.modules.trip.dtos import TripStayOut

__all__ = ["StayCreate", "StayUpdate", "TripStayOut"]


class StayCreate(BaseModel):
    place_id: str
    check_in_day_number: int = Field(ge=1)
    nights: int = Field(ge=1, le=60)
    nightly_rate: float | None = Field(default=None, ge=0)
    guest_count: int = Field(default=1, ge=1, le=50)
    note: str | None = Field(default=None, max_length=500)


class StayUpdate(BaseModel):
    check_in_day_number: int | None = Field(default=None, ge=1)
    nights: int | None = Field(default=None, ge=1, le=60)
    nightly_rate: float | None = Field(default=None, ge=0)
    guest_count: int | None = Field(default=None, ge=1, le=50)
    note: str | None = Field(default=None, max_length=500)
