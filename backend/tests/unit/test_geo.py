"""Tests for shared geographic helpers."""
from app.shared.geo import haversine_km


def test_haversine_km_tehran_to_shiraz_approx():
    # Straight-line Tehran → Shiraz is roughly 680–720 km.
    distance = haversine_km(35.6892, 51.3890, 29.5918, 52.5837)
    assert 650 <= distance <= 750
