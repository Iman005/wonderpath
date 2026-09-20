"""In-process TTL cache for daily weather lookups."""
from datetime import UTC, date, datetime, timedelta

from app.modules.weather.interfaces import IWeatherProvider, WeatherObservation

_TTL = timedelta(hours=3)
_ENTRIES: dict[tuple[float, float, str], tuple[WeatherObservation | None, datetime]] = {}


class WeatherCache:
    def __init__(self, provider: IWeatherProvider, ttl: timedelta | None = None) -> None:
        self._provider = provider
        self._ttl = ttl or _TTL
        self._entries = _ENTRIES

    def get_daily(self, latitude: float, longitude: float, day: date) -> WeatherObservation | None:
        key = (round(latitude, 2), round(longitude, 2), day.isoformat())
        cached = self._entries.get(key)
        if cached is not None:
            value, stored_at = cached
            stored = stored_at if stored_at.tzinfo else stored_at.replace(tzinfo=UTC)
            if datetime.now(UTC) - stored <= self._ttl:
                return value
        value = self._provider.get_daily(latitude, longitude, day)
        self._entries[key] = (value, datetime.now(UTC))
        return value
