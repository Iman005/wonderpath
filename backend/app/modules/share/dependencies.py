"""FastAPI DI wiring for public trip sharing."""
from fastapi import Depends

from app.modules.budget.dependencies import get_budget_service
from app.modules.budget.service import BudgetService
from app.modules.map.dependencies import get_map_service
from app.modules.map.service import MapService
from app.modules.notebook.dependencies import get_notebook_service
from app.modules.notebook.service import NotebookService
from app.modules.share.service import ShareService
from app.modules.summary.dependencies import get_summary_service
from app.modules.summary.service import SummaryService
from app.modules.trip.dependencies import get_trip_service
from app.modules.trip.service import TripService
from app.modules.weather.dependencies import get_weather_service
from app.modules.weather.service import WeatherService


def get_share_service(
    trip_service: TripService = Depends(get_trip_service),
    summary_service: SummaryService = Depends(get_summary_service),
    budget_service: BudgetService = Depends(get_budget_service),
    notebook_service: NotebookService = Depends(get_notebook_service),
    map_service: MapService = Depends(get_map_service),
    weather_service: WeatherService = Depends(get_weather_service),
) -> ShareService:
    return ShareService(
        trip_service,
        summary_service,
        budget_service,
        notebook_service,
        map_service,
        weather_service,
    )
