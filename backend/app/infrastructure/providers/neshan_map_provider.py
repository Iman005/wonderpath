"""
NeshanMapProvider — concrete IMapProvider.

Viewport config is assembled locally. Driving routes prefer Neshan
Direction API v4, then public OSRM, then a straight-line polyline so
pins are always connected on the summary map.
"""
import logging
import time

import httpx

from app.core.config import get_settings
from app.infrastructure.geo.haversine import haversine_meters
from app.modules.map.interfaces import IMapProvider, MapPin, MapViewConfig, RouteSegment
from app.shared.polyline import encode_polyline

logger = logging.getLogger("wanderpath.providers.neshan_map")
settings = get_settings()

_DEFAULT_CENTER_LAT = 32.4279
_DEFAULT_CENTER_LNG = 53.6880
_DEFAULT_ZOOM = 5
_PIN_ZOOM = 12
_MAX_RETRIES = 2
_TIMEOUT_SECONDS = 5.0
_OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
_OSRM_TIMEOUT_SECONDS = 4.0
_AVG_SPEED_MPS = 16.7  # ~60 km/h for straight-line duration estimate

# Neshan custom client errors that mean "this key will not work for Direction".
# Retrying every leg of a trip map would stall the summary page for minutes.
_NESHAN_FATAL_STATUS = frozenset({480, 483, 484, 485})
_NESHAN_COOLDOWN_SECONDS = 60 * 60
_neshan_disabled_until = 0.0


class NeshanMapProvider(IMapProvider):
    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self._api_key = api_key if api_key is not None else settings.NESHAN_API_KEY
        self._base_url = (base_url or settings.NESHAN_MAP_BASE_URL).rstrip("/")

    def build_view_config(
        self,
        pins: list[MapPin],
        center_latitude: float | None = None,
        center_longitude: float | None = None,
        route_segments: list[RouteSegment] | None = None,
    ) -> MapViewConfig:
        if center_latitude is not None and center_longitude is not None:
            center_lat, center_lng, zoom = center_latitude, center_longitude, _PIN_ZOOM
        elif pins:
            center_lat = sum(p.latitude for p in pins) / len(pins)
            center_lng = sum(p.longitude for p in pins) / len(pins)
            zoom = _PIN_ZOOM
        else:
            center_lat, center_lng, zoom = _DEFAULT_CENTER_LAT, _DEFAULT_CENTER_LNG, _DEFAULT_ZOOM

        return MapViewConfig(
            provider="neshan",
            center_latitude=center_lat,
            center_longitude=center_lng,
            zoom=zoom,
            pins=pins,
            route_segments=list(route_segments or []),
            style_url=settings.NESHAN_MAP_STYLE_URL,
        )

    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        *,
        allow_straight_fallback: bool = True,
    ) -> RouteSegment | None:
        """Fetch a driving route. Map drawing may fall back to a straight line;
        distance displays must pass allow_straight_fallback=False so air-line
        distances are never shown as road distance.
        """
        if self._api_key:
            neshan = self._neshan_route(origin_lat, origin_lng, dest_lat, dest_lng)
            if neshan is not None:
                return neshan
        osrm = self._osrm_route(origin_lat, origin_lng, dest_lat, dest_lng)
        if osrm is not None:
            return osrm
        if allow_straight_fallback:
            return self._straight_line(origin_lat, origin_lng, dest_lat, dest_lng)
        return None

    def _neshan_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> RouteSegment | None:
        global _neshan_disabled_until
        if time.monotonic() < _neshan_disabled_until:
            return None

        last_error: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                with httpx.Client(timeout=_TIMEOUT_SECONDS) as client:
                    response = client.get(
                        f"{self._base_url}/direction",
                        params={
                            "type": "car",
                            "origin": f"{origin_lat},{origin_lng}",
                            "destination": f"{dest_lat},{dest_lng}",
                            "alternative": "false",
                        },
                        headers={"Api-Key": self._api_key},
                    )
                    if response.status_code in _NESHAN_FATAL_STATUS:
                        _neshan_disabled_until = time.monotonic() + _NESHAN_COOLDOWN_SECONDS
                        logger.warning(
                            "Neshan direction disabled for %ss (HTTP %s — key lacks this service): %s",
                            _NESHAN_COOLDOWN_SECONDS,
                            response.status_code,
                            response.text[:200],
                        )
                        return None
                    response.raise_for_status()
                    data = response.json()
                return self._to_route_segment(data)
            except httpx.HTTPStatusError as exc:
                last_error = exc
                # Other 4xx will not succeed on retry.
                if exc.response is not None and 400 <= exc.response.status_code < 500:
                    logger.warning("Neshan direction client error: %s", exc)
                    return None
                logger.warning("Neshan direction API attempt %s/%s failed: %s", attempt, _MAX_RETRIES, exc)
            except (httpx.HTTPError, ValueError, KeyError, TypeError, IndexError) as exc:
                last_error = exc
                logger.warning("Neshan direction API attempt %s/%s failed: %s", attempt, _MAX_RETRIES, exc)
        logger.warning("Neshan direction unavailable: %s", last_error)
        return None

    def _osrm_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> RouteSegment | None:
        url = f"{_OSRM_URL}/{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        try:
            with httpx.Client(timeout=_OSRM_TIMEOUT_SECONDS) as client:
                response = client.get(url, params={"overview": "full", "geometries": "polyline"})
                response.raise_for_status()
                data = response.json()
            routes = data.get("routes") or []
            if not routes:
                return None
            route = routes[0]
            geometry = route.get("geometry")
            if not geometry:
                return None
            return RouteSegment(
                sequence_index=0,
                origin_label="",
                destination_label="",
                encoded_polyline=geometry,
                distance_meters=float(route.get("distance") or 0),
                duration_seconds=float(route.get("duration") or 0),
                is_current_leg=False,
            )
        except (httpx.HTTPError, ValueError, KeyError, TypeError, IndexError) as exc:
            logger.warning("OSRM fallback failed: %s", exc)
            return None

    @staticmethod
    def _straight_line(
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> RouteSegment:
        distance = haversine_meters(origin_lat, origin_lng, dest_lat, dest_lng)
        return RouteSegment(
            sequence_index=0,
            origin_label="",
            destination_label="",
            encoded_polyline=encode_polyline([(origin_lat, origin_lng), (dest_lat, dest_lng)]),
            distance_meters=distance,
            duration_seconds=distance / _AVG_SPEED_MPS if distance else 0,
            is_current_leg=False,
        )

    @staticmethod
    def _to_route_segment(data: dict) -> RouteSegment | None:
        routes = data.get("routes") or []
        if not routes:
            return None
        route = routes[0]
        points = (route.get("overview_polyline") or {}).get("points")
        if not points:
            return None
        legs = route.get("legs") or []
        distance = 0.0
        duration = 0.0
        if legs:
            distance = float((legs[0].get("distance") or {}).get("value") or 0)
            duration = float((legs[0].get("duration") or {}).get("value") or 0)
        return RouteSegment(
            sequence_index=0,
            origin_label="",
            destination_label="",
            encoded_polyline=points,
            distance_meters=distance,
            duration_seconds=duration,
            is_current_leg=False,
        )
