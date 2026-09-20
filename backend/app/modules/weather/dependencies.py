"""FastAPI DI wiring for weather."""
from fastapi import Depends

from app.infrastructure.cache.weather_cache import WeatherCache
from app.infrastructure.providers.open_meteo_weather_provider import OpenMeteoWeatherProvider
from app.modules.trip.dependencies import get_trip_service
from app.modules.trip.service import TripService
from app.modules.weather.service import WeatherService


def get_weather_service(trip_service: TripService = Depends(get_trip_service)) -> WeatherService:
    return WeatherService(WeatherCache(OpenMeteoWeatherProvider()), trip_service=trip_service)
