"""Unit tests for the Haversine distance utility."""
import math
import pytest
from app.utils.haversine import haversine


class TestHaversine:
    def test_same_point_is_zero(self):
        assert haversine(12.9716, 77.5946, 12.9716, 77.5946) == 0.0

    def test_known_distance_bengaluru_to_mysuru(self):
        # Bengaluru → Mysuru ≈ 143 km by straight line
        dist = haversine(12.9716, 77.5946, 12.2958, 76.6394)
        assert 115 < dist < 150

    def test_electronic_city_to_koramangala(self):
        # ~11–12 km apart
        dist = haversine(12.8399, 77.6770, 12.9352, 77.6245)
        assert 10 < dist < 14

    def test_symmetry(self):
        d1 = haversine(12.839, 77.677, 12.935, 77.624)
        d2 = haversine(12.935, 77.624, 12.839, 77.677)
        assert math.isclose(d1, d2, rel_tol=1e-6)

    def test_returns_float(self):
        result = haversine(0.0, 0.0, 1.0, 1.0)
        assert isinstance(result, float)

    def test_equator_crossing(self):
        dist = haversine(0, 0, 0, 1)
        # 1 degree of longitude at equator ≈ 111.19 km
        assert math.isclose(dist, 111.195, rel_tol=0.01)

    def test_antipodal_points(self):
        # Max possible distance ≈ half Earth circumference ≈ 20,015 km
        dist = haversine(0, 0, 0, 180)
        assert 20_000 < dist < 20_100
