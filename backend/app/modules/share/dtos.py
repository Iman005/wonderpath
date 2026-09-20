"""Read-only public trip snapshot schemas."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.budget.dtos import TripBudgetOut
from app.modules.map.dtos import MapViewConfigOut
from app.modules.notebook.dtos import NoteOut, PackingListOut
from app.modules.summary.dtos import TripSummaryOut
from app.modules.weather.dtos import DayWeatherOut


class ShareLinkOut(BaseModel):
    token: str
    path: str


class SharedTripOut(BaseModel):
    trip_name: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    origin_label: str | None = None
    traveler_count: int = 1
    summary: TripSummaryOut
    budget: TripBudgetOut
    map: MapViewConfigOut | None = None
    notes: list[NoteOut] = Field(default_factory=list)
    packing_lists: list[PackingListOut] = Field(default_factory=list)
    weather: list[DayWeatherOut] = Field(default_factory=list)
    total_distance_km: float | None = None
    total_duration_minutes: float | None = None
