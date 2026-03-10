"""Geographic calculations for waypoint analysis."""

import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Uses the Haversine formula to compute distance in meters.
    
    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees
    
    Returns:
        Distance in meters
    """
    # Earth's radius in meters
    R = 6371000
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def calculate_path_distance(coordinates: list[tuple[float, float]]) -> float:
    """
    Calculate total distance along a path of waypoints.
    
    Args:
        coordinates: List of (latitude, longitude) tuples
    
    Returns:
        Total distance in meters
    """
    if len(coordinates) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(len(coordinates) - 1):
        lat1, lon1 = coordinates[i]
        lat2, lon2 = coordinates[i + 1]
        total_distance += haversine_distance(lat1, lon1, lat2, lon2)
    
    return total_distance


def calculate_center_point(coordinates: list[tuple[float, float]]) -> tuple[float, float]:
    """
    Calculate the geographic center point of a list of coordinates.
    
    Uses simple averaging (suitable for small areas).
    
    Args:
        coordinates: List of (latitude, longitude) tuples
    
    Returns:
        Tuple of (center_latitude, center_longitude)
    """
    if not coordinates:
        return (0.0, 0.0)
    
    lat_sum = sum(lat for lat, _ in coordinates)
    lon_sum = sum(lon for _, lon in coordinates)
    count = len(coordinates)
    
    return (lat_sum / count, lon_sum / count)


def format_coordinates(lat: float, lon: float) -> str:
    """
    Format coordinates as human-readable string.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
    
    Returns:
        Formatted string like "17.34N 104.59E"
    """
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"
    
    return f"{abs(lat):.2f}{lat_dir} {abs(lon):.2f}{lon_dir}"
