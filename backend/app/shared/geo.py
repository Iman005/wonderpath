"""Geographic helpers shared across modules."""
from app.infrastructure.geo.haversine import haversine_meters


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in kilometers."""
    return haversine_meters(lat1, lng1, lat2, lng2) / 1000.0
