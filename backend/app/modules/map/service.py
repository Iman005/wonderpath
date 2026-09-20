"""
MapService — assembles a renderable map view for a trip's places, via
IMapProvider. Contains no rendering/vendor logic itself (that's the
provider's job) — only the business rule of which pins and route legs
belong on this trip's map.
"""
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta, timezone

from app.modules.map.interfaces import IMapProvider, MapPin, MapViewConfig, RouteSegment
from app.modules.trip.itinerary import day_places_in_itinerary_order, last_place_before
from app.modules.trip.service import TripService
from app.shared.exceptions import NotFoundError

ORIGIN_PIN_ID = "origin"


@dataclass(frozen=True)
class _RoutePoint:
    place_id: str
    label: str
    latitude: float
    longitude: float
    sequence_index: int
    day_number: int
    day_date: date | None


class MapService:
    def __init__(self, map_provider: IMapProvider, trip_service: TripService) -> None:
        self.map_provider = map_provider
        self.trip_service = trip_service

    def get_trip_map_view(
        self,
        trip_id: str,
        owner_device_id: str,
        *,
        day_number: int | None = None,
    ) -> MapViewConfig:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        return self.build_view_for_trip(trip, day_number=day_number)

    def build_view_for_trip(self, trip, *, day_number: int | None = None) -> MapViewConfig:
        if day_number is not None:
            if not any(day.day_number == day_number for day in trip.days):
                raise NotFoundError(f"Day {day_number} was not found on this trip.")
            route_points = self._ordered_points(trip, day_number=day_number)
            pins = [_to_pin(point) for point in route_points]
            current_leg = 0 if len(route_points) >= 2 else None
            segments = self._route_segments(route_points, current_leg)
            return self.map_provider.build_view_config(pins, route_segments=segments)

        points = self._ordered_points(trip)
        pins = [_to_pin(point) for point in points]
        current_leg = self._first_untraveled_leg_index(points, trip)
        segments = self._route_segments(points, current_leg)
        return self.map_provider.build_view_config(pins, route_segments=segments)

    def _ordered_points(self, trip, *, day_number: int | None = None) -> list[_RoutePoint]:
        points: list[_RoutePoint] = []
        start_date = _as_date(getattr(trip, "start_date", None))
        has_origin = trip.origin_latitude is not None and trip.origin_longitude is not None
        include_trip_origin = has_origin and (day_number is None or day_number == 1)
        days = sorted(trip.days, key=lambda d: d.day_number)
        if day_number is not None:
            days = [day for day in days if day.day_number == day_number]
        carry_origin = None
        if day_number is not None and day_number > 1:
            carry_origin = last_place_before(trip, day_number)
            first_places = day_places_in_itinerary_order(trip, days[0]) if days else []
            if carry_origin is not None and first_places and first_places[0].id == carry_origin.id:
                carry_origin = None
        if include_trip_origin:
            points.append(
                _RoutePoint(
                    place_id=ORIGIN_PIN_ID,
                    label=trip.origin_label or ORIGIN_PIN_ID,
                    latitude=trip.origin_latitude,
                    longitude=trip.origin_longitude,
                    sequence_index=0,
                    day_number=0,
                    day_date=start_date,
                )
            )
        elif carry_origin is not None:
            points.append(
                _RoutePoint(
                    place_id=f"carry-{carry_origin.id}",
                    label=carry_origin.name,
                    latitude=carry_origin.latitude,
                    longitude=carry_origin.longitude,
                    sequence_index=0,
                    day_number=day_number - 1,
                    day_date=None,
                )
            )
        elif has_origin:
            points.append(
                _RoutePoint(
                    place_id=ORIGIN_PIN_ID,
                    label=trip.origin_label or ORIGIN_PIN_ID,
                    latitude=trip.origin_latitude,
                    longitude=trip.origin_longitude,
                    sequence_index=0,
                    day_number=0,
                    day_date=start_date,
                )
            )

        visit_index = 1
        for day in days:
            day_date = _as_date(getattr(day, "date", None))
            if day_date is None and start_date is not None:
                day_date = start_date + timedelta(days=day.day_number - 1)
            for place in day_places_in_itinerary_order(trip, day):
                points.append(
                    _RoutePoint(
                        place_id=place.id,
                        label=place.name,
                        latitude=place.latitude,
                        longitude=place.longitude,
                        sequence_index=visit_index,
                        day_number=day.day_number,
                        day_date=day_date,
                    )
                )
                visit_index += 1
        return points

    def _route_segments(
        self,
        points: list[_RoutePoint],
        current_leg: int | None,
    ) -> list[RouteSegment]:
        segments: list[RouteSegment] = []
        for index in range(len(points) - 1):
            origin = points[index]
            destination = points[index + 1]
            segment = self.map_provider.get_route(
                origin.latitude,
                origin.longitude,
                destination.latitude,
                destination.longitude,
            )
            if segment is None:
                continue
            segments.append(
                replace(
                    segment,
                    sequence_index=index,
                    origin_label=origin.label,
                    destination_label=destination.label,
                    is_current_leg=current_leg is not None and index == current_leg,
                )
            )
        return segments

    @staticmethod
    def _first_untraveled_leg_index(points: list[_RoutePoint], trip) -> int | None:
        """First remaining origin→destination hop by trip calendar.

        Origin is day 0 / start_date. Places belong to their trip day.
        The current leg is the inbound route to the first stop whose date
        is today or later. If every stop is in the past, nothing is
        highlighted.
        """
        if len(points) < 2:
            return None
        today = datetime.now(timezone.utc).date()
        start_date = _as_date(getattr(trip, "start_date", None))
        if start_date is None and all(point.day_date is None for point in points):
            return 0

        for index, point in enumerate(points):
            if point.place_id == ORIGIN_PIN_ID:
                continue
            point_date = point.day_date
            if point_date is None and start_date is not None:
                point_date = start_date + timedelta(days=max(point.day_number, 1) - 1)
            if point_date is None or point_date >= today:
                return max(index - 1, 0)
        return None


def _to_pin(point: _RoutePoint) -> MapPin:
    return MapPin(
        place_id=point.place_id,
        name=point.label,
        latitude=point.latitude,
        longitude=point.longitude,
        sequence_index=point.sequence_index,
    )


def _as_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None
