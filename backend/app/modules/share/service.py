"""ShareService — owner enables a token; anyone with the token sees a read-only snapshot."""
from app.modules.budget.service import BudgetService
from app.modules.map.service import MapService
from app.modules.notebook.service import NotebookService
from app.modules.share.dtos import SharedTripOut, ShareLinkOut
from app.modules.summary.service import SummaryService
from app.modules.trip.service import TripService
from app.modules.weather.service import WeatherService
from app.shared.exceptions import ExternalProviderError


class ShareService:
    def __init__(
        self,
        trip_service: TripService,
        summary_service: SummaryService,
        budget_service: BudgetService,
        notebook_service: NotebookService,
        map_service: MapService,
        weather_service: WeatherService,
    ) -> None:
        self.trip_service = trip_service
        self.summary_service = summary_service
        self.budget_service = budget_service
        self.notebook_service = notebook_service
        self.map_service = map_service
        self.weather_service = weather_service

    def enable_share(self, trip_id: str, owner_device_id: str) -> ShareLinkOut:
        token = self.trip_service.enable_share(trip_id, owner_device_id)
        return ShareLinkOut(token=token, path=f"/share/{token}")

    def get_shared_trip(self, token: str) -> SharedTripOut:
        trip = self.trip_service.get_trip_by_share_token(token)
        summary = self.summary_service.build_from_trip(trip)
        budget = self.budget_service.budget_for_trip(trip)
        notes, packing_lists = self.notebook_service.public_snapshot(trip)
        map_config = None
        try:
            map_config = self.map_service.build_view_for_trip(trip)
        except ExternalProviderError:
            map_config = None
        try:
            weather = self.weather_service.weather_for_trip(trip)
        except ExternalProviderError:
            weather = []
        total_km = None
        total_min = None
        if map_config is not None and map_config.route_segments:
            meters = sum(segment.distance_meters for segment in map_config.route_segments)
            seconds = sum(segment.duration_seconds for segment in map_config.route_segments)
            total_km = round(meters / 1000, 1)
            total_min = round(seconds / 60)
        return SharedTripOut(
            trip_name=trip.name,
            start_date=trip.start_date,
            end_date=trip.end_date,
            origin_label=trip.origin_label,
            traveler_count=getattr(trip, "traveler_count", 1) or 1,
            summary=summary,
            budget=budget,
            map=map_config,
            notes=notes,
            packing_lists=packing_lists,
            weather=weather,
            total_distance_km=total_km,
            total_duration_minutes=total_min,
        )
