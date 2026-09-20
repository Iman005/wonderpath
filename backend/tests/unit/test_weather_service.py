from datetime import date
from unittest.mock import MagicMock

from app.modules.weather.interfaces import WeatherObservation
from app.modules.weather.service import WeatherService


def test_get_day_maps_provider_payload_to_advice():
    cache = MagicMock()
    cache.get_daily.return_value = WeatherObservation(
        observed_date=date(2026, 8, 26),
        weather_code=0,
        temp_min_c=17,
        temp_max_c=27,
        precipitation_probability=10,
        wind_kmh=8,
        available=True,
    )
    service = WeatherService(cache)
    result = service.get_day(29.6, 52.5, date(2026, 8, 26), city_label="شیراز")
    assert result.available is True
    assert result.city_label == "شیراز"
    assert result.condition_label == "آسمان صاف"
    assert result.suitable


def test_unavailable_observation_returns_fallback_copy():
    cache = MagicMock()
    cache.get_daily.return_value = WeatherObservation(
        observed_date=date(2027, 1, 1),
        weather_code=0,
        temp_min_c=0,
        temp_max_c=0,
        available=False,
    )
    service = WeatherService(cache)
    result = service.get_day(35.7, 51.4, date(2027, 1, 1))
    assert result.available is False
    assert "در دسترس نیست" in result.condition_label
