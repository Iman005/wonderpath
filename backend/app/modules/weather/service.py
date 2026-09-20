"""WeatherService — one-day and trip-range forecasts with activity advice."""
from datetime import date, datetime, timedelta

from app.infrastructure.cache.weather_cache import WeatherCache
from app.modules.weather.advice import advise
from app.modules.weather.dtos import DayWeatherOut
from app.modules.trip.service import TripService
from app.shared.exceptions import ExternalProviderError, ValidationDomainError


class WeatherService:
    def __init__(self, cache: WeatherCache, trip_service: TripService | None = None) -> None:
        self.cache = cache
        self.trip_service = trip_service

    def get_day(
        self,
        latitude: float,
        longitude: float,
        day: date,
        *,
        city_label: str | None = None,
    ) -> DayWeatherOut:
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValidationDomainError("Coordinates are out of range.")
        try:
            observation = self.cache.get_daily(latitude, longitude, day)
        except ExternalProviderError:
            observation = None
        if observation is None or not observation.available:
            return DayWeatherOut(
                date=day,
                city_label=city_label,
                latitude=latitude,
                longitude=longitude,
                available=False,
                condition_label="پیش‌بینی برای این تاریخ در دسترس نیست",
                hint="برای تاریخ‌های دورتر، چند روز مانده به سفر دوباره سر بزن.",
            )
        advice = advise(observation)
        return DayWeatherOut(
            date=day,
            city_label=city_label,
            latitude=latitude,
            longitude=longitude,
            available=True,
            condition_code=observation.weather_code,
            condition_label=advice.condition_label,
            temp_min_c=round(observation.temp_min_c, 1),
            temp_max_c=round(observation.temp_max_c, 1),
            precipitation_probability=observation.precipitation_probability,
            wind_kmh=None if observation.wind_kmh is None else round(observation.wind_kmh, 1),
            suitable=list(advice.suitable),
            unsuitable=list(advice.unsuitable),
            hint=advice.hint,
        )

    def get_trip_weather(self, trip_id: str, owner_device_id: str) -> list[DayWeatherOut]:
        if self.trip_service is None:
            raise ValidationDomainError("Trip weather is not configured.")
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        return self.weather_for_trip(trip)

    def weather_for_trip(self, trip) -> list[DayWeatherOut]:
        rows: list[DayWeatherOut] = []
        for day in sorted(getattr(trip, "days", None) or [], key=lambda item: item.day_number):
            day_date = _day_date(trip, day)
            if day_date is None:
                continue
            lat, lng, label = _day_location(trip, day)
            if lat is None or lng is None:
                rows.append(
                    DayWeatherOut(
                        date=day_date,
                        city_label=label,
                        available=False,
                        condition_label="مختصات این روز مشخص نیست",
                        hint="با انتخاب شهر یا مبدأ، هوای همان روز اینجا می‌آید.",
                    )
                )
                continue
            rows.append(self.get_day(lat, lng, day_date, city_label=label))
        return rows


def _as_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def _day_date(trip, day) -> date | None:
    explicit = _as_date(getattr(day, "date", None))
    if explicit is not None:
        return explicit
    start = _as_date(getattr(trip, "start_date", None))
    if start is None:
        return None
    return start + timedelta(days=max(int(day.day_number), 1) - 1)


def _day_location(trip, day) -> tuple[float | None, float | None, str | None]:
    for tp in getattr(day, "trip_places", None) or []:
        place = getattr(tp, "place", None)
        if place is None:
            continue
        city = getattr(place, "city", None)
        label = getattr(city, "name", None) or getattr(place, "name", None)
        lat = getattr(city, "latitude", None) or getattr(place, "latitude", None)
        lng = getattr(city, "longitude", None) or getattr(place, "longitude", None)
        if lat is not None and lng is not None:
            return float(lat), float(lng), label
    day_number = getattr(day, "day_number", None)
    for stay in getattr(trip, "stays", None) or []:
        check_in = getattr(stay, "check_in_day_number", None)
        nights = getattr(stay, "nights", 1) or 1
        if check_in is None or day_number is None:
            continue
        if not (check_in <= day_number < check_in + nights):
            continue
        place = getattr(stay, "place", None)
        if place is None:
            continue
        city = getattr(place, "city", None)
        label = getattr(city, "name", None) or getattr(place, "name", None)
        lat = getattr(city, "latitude", None) or getattr(place, "latitude", None)
        lng = getattr(city, "longitude", None) or getattr(place, "longitude", None)
        if lat is not None and lng is not None:
            return float(lat), float(lng), label
    origin_lat = getattr(trip, "origin_latitude", None)
    origin_lng = getattr(trip, "origin_longitude", None)
    if origin_lat is not None and origin_lng is not None:
        return float(origin_lat), float(origin_lng), getattr(trip, "origin_label", None)
    return None, None, None
