"""Weather API schemas."""
from datetime import date

from pydantic import BaseModel, Field


class DayWeatherOut(BaseModel):
    date: date
    city_label: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    available: bool = True
    condition_code: int | None = None
    condition_label: str
    temp_min_c: float | None = None
    temp_max_c: float | None = None
    precipitation_probability: int | None = None
    wind_kmh: float | None = None
    suitable: list[str] = Field(default_factory=list)
    unsuitable: list[str] = Field(default_factory=list)
    hint: str = ""
