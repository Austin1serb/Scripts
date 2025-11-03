"""Geographic and geospatial utilities."""

from math import radians, sin, cos, asin, sqrt
from typing import Optional, Tuple, List
from ..config import CITIES

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError

    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False

# Cache for reverse geocoding to avoid repeated API calls
_geocode_cache = {}


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


def get_city_from_gps(gps: Tuple[float, float]) -> Optional[str]:
    """Get actual city name from GPS coordinates using reverse geocoding.

    Args:
        gps: GPS coordinates (lat, lon)

    Returns:
        City name or None if geocoding fails
    """
    if not GEOPY_AVAILABLE:
        return None

    # Check cache first
    cache_key = f"{gps[0]:.4f},{gps[1]:.4f}"
    if cache_key in _geocode_cache:
        return _geocode_cache[cache_key]

    try:
        geolocator = Nominatim(user_agent="photo_organizer")
        location = geolocator.reverse(
            f"{gps[0]}, {gps[1]}", exactly_one=True, timeout=5
        )

        if location and location.raw.get("address"):
            address = location.raw["address"]
            # Try to get city from various fields (different countries use different keys)
            city = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("municipality")
                or address.get("county")
            )

            if city:
                # Cache the result
                _geocode_cache[cache_key] = city
                return city
    except (GeocoderTimedOut, GeocoderServiceError, Exception) as e:
        print(f"⚠️  Geocoding failed: {e}")
        return None

    return None


def nearest_city(gps: Optional[Tuple[float, float]], fallback_cycle, idx: int) -> str:
    """Determine city name from GPS coordinates or use fallback.

    If GPS exists:
    1. Try reverse geocoding to get actual city name
    2. If that fails, fall back to nearest city from CITIES dict

    If no GPS:
    - Use rotation or static fallback

    Args:
        gps: GPS coordinates (lat, lon) or None
        fallback_cycle: List of city names to cycle through, or dict of cities
        idx: Index for cycling through fallback cities (used only with list)

    Returns:
        City name
    """
    if gps:
        # Try to get actual city name from GPS
        actual_city = get_city_from_gps(gps)
        if actual_city:
            print(f"📍 City from GPS: {actual_city}")
            return actual_city

        # Fallback: Find nearest city from predefined list
        lat, lon = gps
        best = None
        best_city = None
        for c, (clat, clon) in CITIES.items():
            d = haversine(lat, lon, clat, clon)
            if best is None or d < best:
                best, best_city = d, c
        if best_city:
            print(
                f"📍 Nearest city from GPS: {best_city} (reverse geocoding unavailable)"
            )
            return best_city

    # Handle both list (for rotation) and dict (for static fallback)
    if isinstance(fallback_cycle, dict):
        # Use first city from dict when not rotating
        fallback = list(fallback_cycle.keys())[0]
    else:
        # Cycle through list
        fallback = fallback_cycle[idx % len(fallback_cycle)]

    print(f"📍 Using fallback city: {fallback}")
    return fallback
