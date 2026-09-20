from unittest.mock import MagicMock

from app.modules.trip.itinerary import search_origin_coords


def _place(lat, lng):
    place = MagicMock()
    place.latitude = lat
    place.longitude = lng
    return place


def _trip_place(order_index, place):
    tp = MagicMock()
    tp.order_index = order_index
    tp.place = place
    return tp


def _day(day_number, trip_places):
    day = MagicMock()
    day.day_number = day_number
    day.trip_places = trip_places
    return day


def test_search_origin_falls_back_to_trip_home():
    trip = MagicMock()
    trip.origin_latitude = 35.7
    trip.origin_longitude = 51.4
    trip.days = [_day(1, [])]
    trip.stays = []
    assert search_origin_coords(trip, 1) == (35.7, 51.4)


def test_search_origin_uses_last_stop_on_current_day():
    first = _place(29.6, 52.5)
    last = _place(29.63, 52.52)
    trip = MagicMock()
    trip.origin_latitude = 35.7
    trip.origin_longitude = 51.4
    trip.days = [_day(1, [_trip_place(0, first), _trip_place(1, last)])]
    trip.stays = []
    assert search_origin_coords(trip, 1) == (29.63, 52.52)


def test_search_origin_on_empty_day_uses_previous_day():
    previous = _place(29.62, 52.54)
    trip = MagicMock()
    trip.origin_latitude = 35.7
    trip.origin_longitude = 51.4
    trip.days = [_day(1, [_trip_place(0, previous)]), _day(2, [])]
    trip.stays = []
    assert search_origin_coords(trip, 2) == (29.62, 52.54)
