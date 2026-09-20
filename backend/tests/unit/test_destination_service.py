"""
Service layer tests for DestinationService, with repositories and
Wikipedia lookups mocked.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.modules.destination.service import DestinationService
from app.shared.exceptions import NotFoundError


def _make_service():
    repo = MagicMock()
    cache_sync = MagicMock()
    trip_service = MagicMock()
    route_cache = MagicMock()
    return DestinationService(repo, cache_sync, trip_service=trip_service, route_cache=route_cache), repo, cache_sync, route_cache


def test_list_places_passes_kind_to_cache():
    service, repo, cache_sync, _ = _make_service()
    city = MagicMock()
    repo.get_city.return_value = city
    cache_sync.get_places_for_city.return_value = []

    from app.shared.place_kind import PlaceKind

    service.list_places_for_city("city-1", kind=PlaceKind.LODGING)
    cache_sync.get_places_for_city.assert_called_once()
    assert cache_sync.get_places_for_city.call_args.kwargs["kind"] == PlaceKind.LODGING


def test_list_places_raises_not_found_for_missing_city():
    service, repo, _, _ = _make_service()
    repo.get_city.return_value = None

    with pytest.raises(NotFoundError):
        service.list_places_for_city("missing-city")


def test_search_cities_adds_driving_distance_when_origin_known():
    service, repo, cache_sync, route_cache = _make_service()
    city = MagicMock()
    city.id = "city-1"
    city.name = "شیراز"
    city.name_en = "Shiraz"
    city.province_id = "prov-1"
    city.latitude = 29.5918
    city.longitude = 52.5837
    city.province = MagicMock(name="فارس")
    city.province.name = "فارس"
    cache_sync.search_cities.return_value = [city]

    trip_service = MagicMock()
    trip = MagicMock()
    trip.origin_latitude = 35.6892
    trip.origin_longitude = 51.3890
    trip.days = []
    trip.stays = []
    trip_service.get_trip.return_value = trip
    service.trip_service = trip_service
    route_cache.driving_metrics.return_value = (920.4, 560.0, True)

    results = service.search_cities("شیراز", trip_id="trip-1", owner_device_id="user-1")
    assert len(results) == 1
    assert results[0].distance_from_origin_km == 920.4
    assert results[0].duration_from_origin_minutes == 560.0
    assert results[0].distance_is_driving is True
    route_cache.driving_metrics.assert_called_once()
    assert route_cache.driving_metrics.call_args.kwargs.get("allow_fetch") is True


def test_search_cities_ranks_exact_name_before_substring():
    service, _repo, cache_sync, route_cache = _make_service()
    rashtkhar = MagicMock()
    rashtkhar.id = "c-rosh"
    rashtkhar.name = "رشتخوار"
    rashtkhar.name_en = "Roshtkhar"
    rashtkhar.province_id = "p-1"
    rashtkhar.latitude = 34.97
    rashtkhar.longitude = 59.62
    rashtkhar.province = MagicMock()
    rashtkhar.province.name = "خراسان رضوی"
    rasht = MagicMock()
    rasht.id = "c-rasht"
    rasht.name = "رشت"
    rasht.name_en = "Rasht"
    rasht.province_id = "p-2"
    rasht.latitude = 37.28
    rasht.longitude = 49.58
    rasht.province = MagicMock()
    rasht.province.name = "گیلان"
    cache_sync.search_cities.return_value = [rashtkhar, rasht]
    route_cache.driving_metrics.return_value = (1.0, None, False)

    results = service.search_cities("رشت")
    assert [item.name for item in results] == ["رشت", "رشتخوار"]


def test_search_cities_uses_previous_day_last_stop_as_origin():
    service, _repo, cache_sync, route_cache = _make_service()
    city = MagicMock()
    city.id = "city-1"
    city.name = "رشت"
    city.name_en = "Rasht"
    city.province_id = "prov-1"
    city.latitude = 37.28
    city.longitude = 49.58
    city.province = MagicMock()
    city.province.name = "گیلان"
    cache_sync.search_cities.return_value = [city]

    last_stop = MagicMock()
    last_stop.latitude = 29.62
    last_stop.longitude = 52.54
    last_stop.name = "حافظیه"
    tp = MagicMock()
    tp.order_index = 0
    tp.place = last_stop
    day1 = MagicMock()
    day1.day_number = 1
    day1.trip_places = [tp]
    day2 = MagicMock()
    day2.day_number = 2
    day2.trip_places = []

    trip = MagicMock()
    trip.origin_latitude = 35.6892
    trip.origin_longitude = 51.3890
    trip.days = [day1, day2]
    trip.stays = []
    trip_service = MagicMock()
    trip_service.get_trip.return_value = trip
    service.trip_service = trip_service
    route_cache.driving_metrics.return_value = (430.0, 300.0, True)

    results = service.search_cities("رشت", trip_id="trip-1", owner_device_id="user-1", day_number=2)
    assert results[0].distance_from_origin_km == 430.0
    args = route_cache.driving_metrics.call_args.args
    assert args[0] == 29.62
    assert args[1] == 52.54
    assert args[2] == 37.28
    assert args[3] == 49.58


def test_get_place_details_raises_not_found():
    service, repo, _, _ = _make_service()
    repo.get_place.return_value = None

    with pytest.raises(NotFoundError):
        service.get_place_details("missing-place")


def test_get_place_details_returns_curated_gallery_without_wikipedia():
    service, repo, _, _ = _make_service()
    city = MagicMock(name="تهران")
    city.name = "تهران"
    city.province = MagicMock()
    city.province.name = "تهران"
    place = MagicMock()
    place.id = "place-1"
    place.name = "برج آزادی"
    place.description = "نماد مدرن تهران در ورودی غربی شهر. " * 8
    place.category = "دیدنی شهری"
    place.city_id = "city-1"
    place.latitude = 35.7
    place.longitude = 51.3
    place.image = "https://example.com/azadi.jpg"
    place.address = "میدان آزادی"
    place.estimated_entrance_fee = 200000
    place.opening_hours = "۹:۰۰ تا ۱۹:۰۰"
    place.kind = "attraction"
    place.details_json = None
    place.city = city
    repo.get_place.return_value = place

    with patch("app.modules.destination.service.wikipedia_page_summary") as wiki:
        details = service.get_place_details("place-1")
        wiki.assert_not_called()

    assert details.name == "برج آزادی"
    assert details.city_name == "تهران"
    assert details.visit_tip
    assert details.extra_images
    assert details.historical_era
    assert details.identity
    assert details.notable_events


def test_get_place_details_falls_back_to_wikipedia_when_thin():
    service, repo, _, _ = _make_service()
    place = MagicMock()
    place.id = "place-2"
    place.name = "جایی ناشناخته"
    place.description = "کوتاه"
    place.category = None
    place.city_id = "city-1"
    place.latitude = 1.0
    place.longitude = 2.0
    place.image = None
    place.address = None
    place.estimated_entrance_fee = None
    place.opening_hours = None
    place.kind = "attraction"
    place.details_json = None
    place.city = None
    repo.get_place.return_value = place

    wiki = MagicMock()
    wiki.extract = "توضیح بلند ویکی‌پدیا درباره این مکان گردشگری."
    wiki.original_image = "https://example.com/original.jpg"
    wiki.thumbnail = "https://example.com/thumb.jpg"

    with patch("app.modules.destination.service.wikipedia_page_summary", return_value=wiki):
        details = service.get_place_details("place-2")

    assert details.description == wiki.extract
    assert "https://example.com/original.jpg" in details.extra_images


def test_get_place_details_skips_wikipedia_for_demo_lodging():
    service, repo, _, _ = _make_service()
    place = MagicMock()
    place.id = "hotel-1"
    place.name = "هتل عباسی"
    place.description = "هتل دمو"
    place.category = "هتل"
    place.city_id = "city-1"
    place.latitude = 32.6
    place.longitude = 51.6
    place.image = None
    place.address = "اصفهان"
    place.estimated_entrance_fee = 14_800_000
    place.opening_hours = "شبانه‌روزی"
    place.kind = "lodging"
    place.details_json = '{"is_demo": true, "stars": 5, "amenities": ["وای‌فای"], "rooms": [{"name": "دو تخته", "price": 14800000}], "menu": []}'
    place.city = None
    repo.get_place.return_value = place

    with patch("app.modules.destination.service.wikipedia_page_summary") as wiki:
        details = service.get_place_details("hotel-1")
        wiki.assert_not_called()

    assert details.catalog is not None
    assert details.catalog.is_demo is True
    assert details.catalog.stars == 5
    assert details.catalog.rooms[0].price == 14_800_000


def test_list_lodging_prefers_seeded_catalog_over_osm():
    service, repo, cache_sync, _ = _make_service()
    repo.get_city.return_value = MagicMock()

    osm = MagicMock()
    osm.id = "osm-1"
    osm.name = "Hotel OSM"
    osm.description = None
    osm.category = "hotel"
    osm.city_id = "city-1"
    osm.latitude = 32.6
    osm.longitude = 51.6
    osm.image = None
    osm.address = None
    osm.estimated_entrance_fee = None
    osm.opening_hours = None
    osm.kind = "lodging"
    osm.details_json = None
    osm.source_provider_id = "osm:123"

    seed = MagicMock()
    seed.id = "seed-1"
    seed.name = "هتل عباسی"
    seed.description = "هتل دمو"
    seed.category = "هتل"
    seed.city_id = "city-1"
    seed.latitude = 32.65
    seed.longitude = 51.67
    seed.image = None
    seed.address = "خیابان آمادگاه"
    seed.estimated_entrance_fee = 14_800_000
    seed.opening_hours = "شبانه‌روزی"
    seed.kind = "lodging"
    seed.details_json = '{"is_demo": true, "stars": 5, "amenities": [], "rooms": [], "menu": []}'
    seed.source_provider_id = "seed:lodging:هتل عباسی"

    cache_sync.get_places_for_city.return_value = [osm, seed]

    from app.shared.place_kind import PlaceKind

    results = service.list_places_for_city("city-1", kind=PlaceKind.LODGING)
    assert [item.id for item in results] == ["seed-1"]
    assert results[0].catalog is not None
    assert results[0].catalog.is_demo is True


def test_list_places_uses_city_driving_distance_not_air_line():
    service, repo, cache_sync, route_cache = _make_service()
    city = MagicMock()
    city.latitude = 37.2808
    city.longitude = 49.5832
    repo.get_city.return_value = city

    place = MagicMock()
    place.id = "p-1"
    place.name = "میدان شهرداری رشت"
    place.description = "میدان"
    place.category = "دیدنی شهری"
    place.city_id = "city-1"
    place.latitude = 37.2783
    place.longitude = 49.5892
    place.image = None
    place.address = None
    place.estimated_entrance_fee = None
    place.opening_hours = None
    place.kind = "attraction"
    place.details_json = None
    cache_sync.get_places_for_city.return_value = [place]

    trip = MagicMock()
    trip.origin_latitude = 35.6892
    trip.origin_longitude = 51.3890
    trip.days = []
    trip.stays = []
    service.trip_service.get_trip.return_value = trip

    def metrics(_olat, _olng, _dlat, _dlng, allow_fetch=False):
        if allow_fetch:
            return (330.0, 240.0, True)
        return (240.0, None, False)

    route_cache.driving_metrics.side_effect = metrics

    from app.shared.place_kind import PlaceKind

    results = service.list_places_for_city(
        "city-1",
        trip_id="trip-1",
        owner_device_id="user-1",
        kind=PlaceKind.ATTRACTION,
    )
    assert len(results) == 1
    assert results[0].distance_is_driving is True
    assert results[0].distance_from_origin_km >= 330.0
    assert results[0].duration_from_origin_minutes == 240.0
    fetched = [
        call
        for call in route_cache.driving_metrics.call_args_list
        if call.kwargs.get("allow_fetch") is True
    ]
    assert len(fetched) == 1


def test_every_curated_place_has_historical_context():
    from app.infrastructure.data.place_details import PLACE_DETAILS
    from app.infrastructure.data.place_history import PLACE_HISTORY

    missing = sorted(set(PLACE_DETAILS) - set(PLACE_HISTORY))
    assert missing == []
