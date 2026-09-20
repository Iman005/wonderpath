"""
RouteDistanceCache — caches *real* driving distance/duration.

Uses IMapProvider.get_route(..., allow_straight_fallback=False) so a failed
router never silently reports air-line distance as road distance. When no
road route is available, falls back to haversine km with duration=None so
the UI can label it as approximate.
"""
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import get_settings
from app.modules.map.interfaces import IMapProvider
from app.shared.geo import haversine_km

logger = logging.getLogger("wanderpath.cache.route_distance")
settings = get_settings()

# Process-wide cache so listing many places does not re-hit OSRM every request.
_GLOBAL_ENTRIES: dict[tuple[float, float, float, float], tuple[float, float | None, bool, datetime]] = {}


class RouteDistanceCache:
    def __init__(self, map_provider: IMapProvider, ttl_seconds: int | None = None) -> None:
        self._map_provider = map_provider
        self._ttl = timedelta(seconds=ttl_seconds or settings.ROUTE_CACHE_TTL_SECONDS)
        self._entries = _GLOBAL_ENTRIES

    @staticmethod
    def _cache_key(
        origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float
    ) -> tuple[float, float, float, float]:
        return (round(origin_lat, 3), round(origin_lng, 3), round(dest_lat, 3), round(dest_lng, 3))

    def driving_metrics(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        *,
        allow_fetch: bool = True,
    ) -> tuple[float | None, float | None, bool]:
        """Return (distance_km, duration_minutes, is_driving).

        is_driving=True when values came from a real router; False when only
        a great-circle estimate is available (duration_minutes will be None).

        When allow_fetch=False, only a warm cache entry is used; otherwise
        haversine is returned without blocking on Neshan/OSRM. Place catalogs
        pass False so listing dozens of venues stays responsive in Iran.
        """
        key = self._cache_key(origin_lat, origin_lng, dest_lat, dest_lng)
        cached = self._entries.get(key)
        if cached is not None:
            distance_km, duration_minutes, is_driving, cached_at = cached
            cached_at_aware = cached_at if cached_at.tzinfo else cached_at.replace(tzinfo=UTC)
            if datetime.now(UTC) - cached_at_aware <= self._ttl:
                return distance_km, duration_minutes, is_driving

        if not allow_fetch:
            return haversine_km(origin_lat, origin_lng, dest_lat, dest_lng), None, False

        segment = self._fetch_driving_segment(origin_lat, origin_lng, dest_lat, dest_lng)
        if segment is not None:
            distance_km = segment.distance_meters / 1000.0
            duration_minutes = segment.duration_seconds / 60.0
            self._entries[key] = (distance_km, duration_minutes, True, datetime.now(UTC))
            return distance_km, duration_minutes, True

        # Honest fallback: air-line only, no fake driving duration.
        approx_km = haversine_km(origin_lat, origin_lng, dest_lat, dest_lng)
        self._entries[key] = (approx_km, None, False, datetime.now(UTC))
        return approx_km, None, False

    def _fetch_driving_segment(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> Any:
        try:
            return self._map_provider.get_route(
                origin_lat,
                origin_lng,
                dest_lat,
                dest_lng,
                allow_straight_fallback=False,
            )
        except TypeError:
            # Older/mock providers without the keyword — call and treat result
            # as driving only if present (tests/mocks).
            try:
                return self._map_provider.get_route(origin_lat, origin_lng, dest_lat, dest_lng)
            except Exception as exc:
                logger.warning("Route lookup failed for %s: %s", (origin_lat, dest_lat), exc)
                return None
        except Exception as exc:
            logger.warning("Route lookup failed for %s: %s", (origin_lat, dest_lat), exc)
            return None
