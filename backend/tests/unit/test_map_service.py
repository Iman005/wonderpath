"""Service-layer tests for MapService with mocked trip + map providers."""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from app.modules.map.interfaces import MapViewConfig, RouteSegment
from app.modules.map.service import ORIGIN_PIN_ID, MapService


def _place(place_id, name, lat, lng):
    place = MagicMock()
    place.id = place_id
    place.name = name
    place.latitude = lat
    place.longitude = lng
    return place


def _trip_place(order_index, place):
    tp = MagicMock()
    tp.order_index = order_index
    tp.place = place
    return tp


def _day(day_number, trip_places, date=None):
    day = MagicMock()
    day.day_number = day_number
    day.trip_places = trip_places
    day.date = date
    return day


def test_builds_origin_then_visit_order_and_marks_first_leg_current():
    trip_service = MagicMock()
    trip = MagicMock()
    trip.origin_latitude = 35.7
    trip.origin_longitude = 51.4
    trip.origin_label = "تهران، منزل"
    trip.start_date = None
    trip.stays = []
    trip.days = [
        _day(2, [_trip_place(0, _place("p-b", "باغ ارم", 29.63, 52.52))]),
        _day(1, [_trip_place(0, _place("p-a", "تخت جمشید", 29.93, 52.89))]),
    ]
    trip_service.get_trip.return_value = trip

    map_provider = MagicMock()
    map_provider.get_route.side_effect = [
        RouteSegment(0, "", "", "poly-1", 1000, 120, False),
        RouteSegment(0, "", "", "poly-2", 2000, 240, False),
    ]
    map_provider.build_view_config.side_effect = lambda pins, **kwargs: MapViewConfig(
        provider="neshan",
        center_latitude=30.0,
        center_longitude=52.0,
        zoom=12,
        pins=pins,
        route_segments=kwargs.get("route_segments") or [],
    )

    result = MapService(map_provider, trip_service).get_trip_map_view("trip-1", "device-1")

    assert [pin.place_id for pin in result.pins] == [ORIGIN_PIN_ID, "p-a", "p-b"]
    assert [pin.sequence_index for pin in result.pins] == [0, 1, 2]
    assert len(result.route_segments) == 2
    assert result.route_segments[0].is_current_leg is True
    assert result.route_segments[0].origin_label == "تهران، منزل"
    assert result.route_segments[0].destination_label == "تخت جمشید"
    assert result.route_segments[1].is_current_leg is False
    assert map_provider.get_route.call_count == 2


def test_skips_failed_leg_and_still_returns_pins():
    trip_service = MagicMock()
    trip = MagicMock()
    trip.origin_latitude = None
    trip.origin_longitude = None
    trip.origin_label = None
    trip.start_date = None
    trip.stays = []
    trip.days = [
        _day(
            1,
            [
                _trip_place(0, _place("p-a", "A", 30.0, 50.0)),
                _trip_place(1, _place("p-b", "B", 31.0, 51.0)),
                _trip_place(2, _place("p-c", "C", 32.0, 52.0)),
            ],
        )
    ]
    trip_service.get_trip.return_value = trip

    map_provider = MagicMock()
    map_provider.get_route.side_effect = [
        None,
        RouteSegment(0, "", "", "poly-ok", 500, 60, False),
    ]
    map_provider.build_view_config.side_effect = lambda pins, **kwargs: MapViewConfig(
        provider="neshan",
        center_latitude=31.0,
        center_longitude=51.0,
        zoom=12,
        pins=pins,
        route_segments=kwargs.get("route_segments") or [],
    )

    result = MapService(map_provider, trip_service).get_trip_map_view("trip-1", "device-1")

    assert [pin.place_id for pin in result.pins] == ["p-a", "p-b", "p-c"]
    assert len(result.route_segments) == 1
    assert result.route_segments[0].encoded_polyline == "poly-ok"
    assert result.route_segments[0].is_current_leg is False


def test_marks_first_untraveled_leg_using_trip_dates():
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=1)
    trip_service = MagicMock()
    trip = MagicMock()
    trip.origin_latitude = 35.7
    trip.origin_longitude = 51.4
    trip.origin_label = "تهران"
    trip.start_date = start
    trip.stays = []
    trip.days = [
        _day(1, [_trip_place(0, _place("p-a", "A", 30.0, 50.0))], date=start),
        _day(2, [_trip_place(0, _place("p-b", "B", 31.0, 51.0))], date=start + timedelta(days=1)),
    ]
    trip_service.get_trip.return_value = trip

    map_provider = MagicMock()
    map_provider.get_route.side_effect = [
        RouteSegment(0, "", "", "poly-1", 1000, 120, False),
        RouteSegment(0, "", "", "poly-2", 2000, 240, False),
    ]
    map_provider.build_view_config.side_effect = lambda pins, **kwargs: MapViewConfig(
        provider="neshan",
        center_latitude=31.0,
        center_longitude=51.0,
        zoom=12,
        pins=pins,
        route_segments=kwargs.get("route_segments") or [],
    )

    result = MapService(map_provider, trip_service).get_trip_map_view("trip-1", "device-1")

    assert [segment.is_current_leg for segment in result.route_segments] == [False, True]


def test_day_filter_keeps_origin_on_day_one_and_skips_other_days():
    trip_service = MagicMock()
    trip = MagicMock()
    trip.origin_latitude = 35.7
    trip.origin_longitude = 51.4
    trip.origin_label = "تهران"
    trip.start_date = None
    stay = MagicMock()
    stay.check_in_day_number = 1
    stay.nights = 1
    stay.sort_index = 1
    stay.place = _place("hotel-1", "هتل عباسی", 32.65, 51.67)
    trip.stays = [stay]
    day1_place = _trip_place(0, _place("p-a", "نقش جهان", 32.65, 51.67))
    trip.days = [
        _day(1, [day1_place]),
        _day(2, [_trip_place(0, _place("p-b", "سی‌وسه‌پل", 32.64, 51.66))]),
    ]
    trip_service.get_trip.return_value = trip

    map_provider = MagicMock()
    map_provider.get_route.side_effect = [
        RouteSegment(0, "", "", "poly-1", 4000, 600, False),
        RouteSegment(0, "", "", "poly-2", 2500, 400, False),
    ]
    map_provider.build_view_config.side_effect = lambda pins, **kwargs: MapViewConfig(
        provider="neshan",
        center_latitude=32.6,
        center_longitude=51.6,
        zoom=12,
        pins=pins,
        route_segments=kwargs.get("route_segments") or [],
    )

    result = MapService(map_provider, trip_service).get_trip_map_view(
        "trip-1", "device-1", day_number=1
    )

    assert [pin.place_id for pin in result.pins] == [ORIGIN_PIN_ID, "p-a", "hotel-1"]
    assert len(result.route_segments) == 2
    assert result.route_segments[0].destination_label == "نقش جهان"
    assert result.route_segments[1].destination_label == "هتل عباسی"
    assert map_provider.get_route.call_count == 2


def test_later_day_map_starts_from_previous_day_last_place():
    trip_service = MagicMock()
    trip = MagicMock()
    trip.origin_latitude = 35.7
    trip.origin_longitude = 51.4
    trip.origin_label = "تهران"
    trip.start_date = None
    trip.stays = []
    trip.days = [
        _day(1, [_trip_place(0, _place("p-a", "A", 30.0, 50.0))]),
        _day(
            2,
            [
                _trip_place(0, _place("p-b", "B", 31.0, 51.0)),
                _trip_place(1, _place("p-c", "C", 32.0, 52.0)),
            ],
        ),
    ]
    trip_service.get_trip.return_value = trip

    map_provider = MagicMock()
    map_provider.get_route.return_value = RouteSegment(0, "", "", "poly-2", 8000, 900, False)
    map_provider.build_view_config.side_effect = lambda pins, **kwargs: MapViewConfig(
        provider="neshan",
        center_latitude=31.5,
        center_longitude=51.5,
        zoom=12,
        pins=pins,
        route_segments=kwargs.get("route_segments") or [],
    )

    result = MapService(map_provider, trip_service).get_trip_map_view(
        "trip-1", "device-1", day_number=2
    )

    assert [pin.place_id for pin in result.pins] == ["carry-p-a", "p-b", "p-c"]
    assert len(result.route_segments) == 2
    assert result.route_segments[0].origin_label == "A"
    assert result.route_segments[0].destination_label == "B"
