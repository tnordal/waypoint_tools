"""Mission data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class Waypoint:
    """Individual waypoint data."""
    
    index: int
    latitude: float
    longitude: float
    altitude: float  # meters (relative to takeoff)
    speed: float  # m/s
    heading: float | None = None  # degrees
    gimbal_pitch: float | None = None  # degrees
    actions: list[str] = field(default_factory=list)


@dataclass
class Mission:
    """Waypoint mission metadata and cached information."""
    
    # Required
    uuid: str
    
    # User metadata
    friendly_name: str | None = None
    location: str | None = None
    notes: str | None = None
    tags: list[str] = field(default_factory=list)
    date_created: datetime | None = None
    date_modified: datetime | None = None
    
    # Parsed from WPML (cached)
    waypoint_count: int = 0
    total_distance_m: float = 0.0
    altitude_min: float = 0.0
    altitude_max: float = 0.0
    center_lat: float = 0.0
    center_lon: float = 0.0
    flight_speed: float = 0.0
    finish_action: str = ""
    drone_type: str = ""
    
    # Runtime information
    source: Literal["controller", "local", "both"] = "local"
    thumbnail_paths: list[str] = field(default_factory=list)
    waypoints: list[Waypoint] = field(default_factory=list)
    
    @property
    def display_name(self) -> str:
        """Get display name (friendly name or truncated UUID)."""
        if self.friendly_name:
            return self.friendly_name
        return f"{self.uuid[:8]}..."
    
    @property
    def estimated_flight_time(self) -> float:
        """
        Estimate flight time in seconds.
        
        Assumes constant speed along the path.
        """
        if self.flight_speed <= 0:
            return 0.0
        return self.total_distance_m / self.flight_speed
    
    def to_dict(self) -> dict:
        """Convert mission to dictionary for JSON serialization."""
        return {
            "friendly_name": self.friendly_name,
            "location": self.location,
            "notes": self.notes,
            "tags": self.tags,
            "date_created": (
                self.date_created.isoformat() if self.date_created else None
            ),
            "date_modified": (
                self.date_modified.isoformat() if self.date_modified else None
            ),
            "cached_info": {
                "waypoint_count": self.waypoint_count,
                "total_distance_m": self.total_distance_m,
                "altitude_min": self.altitude_min,
                "altitude_max": self.altitude_max,
                "center_lat": self.center_lat,
                "center_lon": self.center_lon,
                "flight_speed": self.flight_speed,
                "finish_action": self.finish_action,
                "drone_type": self.drone_type,
            },
        }
    
    @classmethod
    def from_dict(cls, uuid: str, data: dict) -> "Mission":
        """Create mission from dictionary loaded from JSON."""
        cached = data.get("cached_info", {})
        
        # Parse dates
        date_created = None
        if data.get("date_created"):
            try:
                date_created = datetime.fromisoformat(data["date_created"])
            except (ValueError, TypeError):
                pass
        
        date_modified = None
        if data.get("date_modified"):
            try:
                date_modified = datetime.fromisoformat(data["date_modified"])
            except (ValueError, TypeError):
                pass
        
        return cls(
            uuid=uuid,
            friendly_name=data.get("friendly_name"),
            location=data.get("location"),
            notes=data.get("notes"),
            tags=data.get("tags", []),
            date_created=date_created,
            date_modified=date_modified,
            waypoint_count=cached.get("waypoint_count", 0),
            total_distance_m=cached.get("total_distance_m", 0.0),
            altitude_min=cached.get("altitude_min", 0.0),
            altitude_max=cached.get("altitude_max", 0.0),
            center_lat=cached.get("center_lat", 0.0),
            center_lon=cached.get("center_lon", 0.0),
            flight_speed=cached.get("flight_speed", 0.0),
            finish_action=cached.get("finish_action", ""),
            drone_type=cached.get("drone_type", ""),
        )
