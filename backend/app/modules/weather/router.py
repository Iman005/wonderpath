"""Weather controller — HTTP layer only."""
from datetime import date

from fastapi import APIRouter, Depends, Query

from app.modules.identity.dependencies import get_current_device_id
from app.modules.weather.dependencies import get_weather_service
from app.modules.weather.dtos import DayWeatherOut
from app.modules.weather.service import WeatherService

router = APIRouter(tags=["Weather"])


@router.get("/weather", response_model=DayWeatherOut)
def get_day_weather(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    date: date = Query(...),
    label: str | None = Query(default=None),
    service: WeatherService = Depends(get_weather_service),
):
    return service.get_day(lat, lng, date, city_label=label)


@router.get("/trips/{trip_id}/weather", response_model=list[DayWeatherOut])
def get_trip_weather(
    trip_id: str,
    device_id: str = Depends(get_current_device_id),
    service: WeatherService = Depends(get_weather_service),
):
    return service.get_trip_weather(trip_id, device_id)
