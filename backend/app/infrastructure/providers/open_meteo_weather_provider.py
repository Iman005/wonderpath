"""
Open-Meteo weather provider — no API key, reachable from Iran more often
than commercial weather APIs.

Forecast covers roughly the next 16 days. Past dates use the archive API.
"""
import logging
from datetime import date

import httpx

from app.modules.weather.interfaces import IWeatherProvider, WeatherObservation
from app.shared.exceptions import ExternalProviderError

logger = logging.getLogger("wanderpath.providers.open_meteo")

_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
_TIMEOUT = 6.0
_FORECAST_HORIZON_DAYS = 16


class OpenMeteoWeatherProvider(IWeatherProvider):
    def get_daily(self, latitude: float, longitude: float, day: date) -> WeatherObservation | None:
        today = date.today()
        iso = day.isoformat()
        if day < today:
            payload = self._fetch(_ARCHIVE_URL, latitude, longitude, iso, archive=True)
        elif (day - today).days <= _FORECAST_HORIZON_DAYS:
            payload = self._fetch(_FORECAST_URL, latitude, longitude, iso, archive=False)
        else:
            return WeatherObservation(
                observed_date=day,
                weather_code=0,
                temp_min_c=0,
                temp_max_c=0,
                available=False,
            )
        if payload is None:
            return None
        return self._parse(payload, day)

    def _fetch(
        self,
        url: str,
        latitude: float,
        longitude: float,
        iso: str,
        *,
        archive: bool,
    ) -> dict | None:
        daily = "weather_code,temperature_2m_max,temperature_2m_min,wind_speed_10m_max"
        if not archive:
            daily += ",precipitation_probability_max"
        else:
            daily += ",precipitation_sum"
        params = {
            "latitude": round(latitude, 4),
            "longitude": round(longitude, 4),
            "daily": daily,
            "timezone": "Asia/Tehran",
            "start_date": iso,
            "end_date": iso,
        }
        try:
            with httpx.Client(timeout=_TIMEOUT) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.warning("Open-Meteo request failed: %s", exc)
            raise ExternalProviderError("Weather data is temporarily unavailable.") from exc

    @staticmethod
    def _parse(payload: dict, day: date) -> WeatherObservation | None:
        daily = payload.get("daily") or {}
        times = daily.get("time") or []
        if day.isoformat() not in times:
            return None
        index = times.index(day.isoformat())

        def _at(key: str) -> float | None:
            values = daily.get(key) or []
            if index >= len(values) or values[index] is None:
                return None
            try:
                return float(values[index])
            except (TypeError, ValueError):
                return None

        tmax = _at("temperature_2m_max")
        tmin = _at("temperature_2m_min")
        if tmax is None or tmin is None:
            return None
        precip = _at("precipitation_probability_max")
        if precip is None:
            rain = _at("precipitation_sum")
            if rain is not None:
                precip = 80 if rain >= 2 else (40 if rain >= 0.2 else 0)
        wind = _at("wind_speed_10m_max")
        code = _at("weather_code")
        return WeatherObservation(
            observed_date=day,
            weather_code=int(code) if code is not None else 0,
            temp_min_c=tmin,
            temp_max_c=tmax,
            precipitation_probability=int(precip) if precip is not None else None,
            wind_kmh=wind,
            available=True,
        )
