"""
Haversine distance calculation.
Returns the great-circle distance between two points on Earth in kilometres.
"""
import math
from app.core.config import settings


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    All inputs in decimal degrees.
    Returns distance in kilometres (rounded to 3 decimal places).
    """
    R = settings.EARTH_RADIUS_KM
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 3)
