from datetime import date

from app.modules.weather.advice import advise, condition_label
from app.modules.weather.interfaces import WeatherObservation


def _obs(**kwargs) -> WeatherObservation:
    defaults = dict(
        observed_date=date(2026, 8, 26),
        weather_code=1,
        temp_min_c=18,
        temp_max_c=28,
        precipitation_probability=5,
        wind_kmh=12,
        available=True,
    )
    defaults.update(kwargs)
    return WeatherObservation(**defaults)


def test_clear_mild_weather_is_good_for_walking():
    advice = advise(_obs(weather_code=0, temp_min_c=16, temp_max_c=26, precipitation_probability=0))
    assert advice.condition_label == condition_label(0)
    assert any("پیاده‌روی" in item for item in advice.suitable)
    assert any("فضای باز" in item for item in advice.suitable)


def test_storm_prefers_indoor_activities():
    advice = advise(_obs(weather_code=95, temp_min_c=18, temp_max_c=24, precipitation_probability=90))
    assert "موزه" in " ".join(advice.suitable)
    assert any("رعدوبرق" in item for item in advice.unsuitable)


def test_hot_day_warns_against_midday_sun():
    advice = advise(_obs(weather_code=1, temp_min_c=26, temp_max_c=39, precipitation_probability=0))
    assert any("آفتاب" in item for item in advice.unsuitable)
