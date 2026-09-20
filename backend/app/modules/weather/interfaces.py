"""IWeatherProvider — forecast/archive lookup by coordinates and date."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class WeatherObservation:
    """Raw provider payload. Persian copy and activity advice live in the service."""

    observed_date: date
    weather_code: int
    temp_min_c: float
    temp_max_c: float
    precipitation_probability: int | None = None
    wind_kmh: float | None = None
    available: bool = True


class IWeatherProvider(ABC):
    @abstractmethod
    def get_daily(
        self,
        latitude: float,
        longitude: float,
        day: date,
    ) -> WeatherObservation | None:
        """Return one day's conditions, or None when the provider has no data."""
        raise NotImplementedError
