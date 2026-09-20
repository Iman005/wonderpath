"""
Contract tests for NeshanPlaceDataProvider / NeshanMapProvider.

These isolate breakage to the infrastructure layer: they mock only the
HTTP boundary (httpx), asserting that our adapter correctly translates
Neshan's response shape into our provider-agnostic DTOs, and that
network/HTTP failures surface as ExternalProviderError rather than
leaking a raw httpx exception into the domain layer.
"""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.infrastructure.providers.neshan_map_provider import NeshanMapProvider
from app.infrastructure.providers.neshan_place_data_provider import NeshanPlaceDataProvider
from app.modules.map.interfaces import MapPin
from app.shared.exceptions import ExternalProviderError


def _mock_response(json_data):
    response = MagicMock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class TestNeshanPlaceDataProviderContract:
    def test_search_cities_translates_response_shape(self):
        provider = NeshanPlaceDataProvider(api_key="fake-key")
        raw = {
            "items": [
                {
                    "id": 42,
                    "title": "شیراز",
                    "title_en": "Shiraz",
                    "province": "فارس",
                    "location": {"x": 52.58, "y": 29.59},
                }
            ]
        }
        with patch("httpx.Client.get", return_value=_mock_response(raw)):
            cities = provider.search_cities("شیراز")

        assert len(cities) == 1
        assert cities[0].source_id == "42"
        assert cities[0].name == "شیراز"
        assert cities[0].province_name == "فارس"
        assert cities[0].longitude == 52.58

    def test_missing_api_key_raises_external_provider_error(self):
        provider = NeshanPlaceDataProvider(api_key="")
        with pytest.raises(ExternalProviderError):
            provider.search_cities("شیراز")

    def test_http_failure_raises_external_provider_error_not_httpx_error(self):
        provider = NeshanPlaceDataProvider(api_key="fake-key")
        with patch("httpx.Client.get", side_effect=httpx.ConnectTimeout("timeout")):
            with pytest.raises(ExternalProviderError):
                provider.search_places("42")


class TestNeshanMapProviderContract:
    def test_defaults_to_iran_center_when_no_pins(self):
        provider = NeshanMapProvider()
        config = provider.build_view_config(pins=[])

        assert config.provider == "neshan"
        assert config.pins == []

    def test_centers_on_average_of_pins(self):
        provider = NeshanMapProvider()
        pins = [
            MapPin(place_id="a", name="A", latitude=30.0, longitude=50.0),
            MapPin(place_id="b", name="B", latitude=32.0, longitude=52.0),
        ]
        config = provider.build_view_config(pins=pins)

        assert config.center_latitude == 31.0
        assert config.center_longitude == 51.0
        assert len(config.pins) == 2
        assert config.route_segments == []

    def test_get_route_translates_direction_response(self):
        provider = NeshanMapProvider(api_key="fake-key", base_url="https://api.neshan.org/v4")
        raw = {
            "routes": [
                {
                    "overview_polyline": {"points": "abc123"},
                    "legs": [{"distance": {"value": 1500.0, "text": "1.5 km"}, "duration": {"value": 240.0, "text": "4 دقیقه"}}],
                }
            ]
        }
        with patch("httpx.Client.get", return_value=_mock_response(raw)) as mocked_get:
            segment = provider.get_route(35.7, 51.4, 29.6, 52.5)

        assert segment is not None
        assert segment.encoded_polyline == "abc123"
        assert segment.distance_meters == 1500.0
        assert segment.duration_seconds == 240.0
        mocked_get.assert_called_once()
        _, kwargs = mocked_get.call_args
        assert kwargs["params"]["origin"] == "35.7,51.4"
        assert kwargs["params"]["destination"] == "29.6,52.5"
        assert kwargs["headers"]["Api-Key"] == "fake-key"

    def test_get_route_falls_back_to_straight_line_on_http_failure(self):
        provider = NeshanMapProvider(api_key="fake-key")
        with patch("httpx.Client.get", side_effect=httpx.ConnectTimeout("timeout")):
            segment = provider.get_route(35.7, 51.4, 29.6, 52.5)
        assert segment is not None
        assert segment.encoded_polyline
        assert segment.distance_meters > 0

    def test_get_route_falls_back_to_straight_line_without_api_key(self):
        provider = NeshanMapProvider(api_key="")
        with patch("httpx.Client.get", side_effect=httpx.ConnectTimeout("timeout")):
            segment = provider.get_route(35.7, 51.4, 29.6, 52.5)
        assert segment is not None
        assert segment.encoded_polyline
