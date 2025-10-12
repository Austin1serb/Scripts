"""Geographic and geospatial utilities."""

from math import radians, sin, cos, asin, sqrt
from typing import Optional, Tuple, List
from ..config import CITIES


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points on Earth.

    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates

    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    return 2 * R * asin(sqrt(a))


def meters_between(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Calculate distance between two GPS coordinates in meters.

    Args:
        a: First point (lat, lon)
        b: Second point (lat, lon)

    Returns:
        Distance in meters
    """
    return haversine(a[0], a[1], b[0], b[1]) * 1000.0


def nearest_city(gps: Optional[Tuple[float, float]], fallback_cycle, idx: int) -> str:
    """Determine nearest city from GPS coordinates or use fallback.

    Args:
        gps: GPS coordinates (lat, lon) or None
        fallback_cycle: List of city names to cycle through, or dict of cities
        idx: Index for cycling through fallback cities (used only with list)

    Returns:
        City name
    """
    if gps:
        lat, lon = gps
        best = None
        best_city = None
        for c, (clat, clon) in CITIES.items():
            d = haversine(lat, lon, clat, clon)
            if best is None or d < best:
                best, best_city = d, c
        if best_city:
            print(f"Best city from GPS: {best_city}")
            return best_city

    # Handle both list (for rotation) and dict (for static fallback)
    if isinstance(fallback_cycle, dict):
        # Use first city from dict when not rotating
        fallback = list(fallback_cycle.keys())[0]
    else:
        # Cycle through list
        fallback = fallback_cycle[idx % len(fallback_cycle)]

    print(f"Using fallback city: {fallback}")
    return fallback
