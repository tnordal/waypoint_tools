"""Application constants and configuration."""

from pathlib import Path

# Application metadata
APP_NAME = "DJI Waypoint Tools"
APP_VERSION = "1.0.0"
ORGANIZATION_NAME = "WaypointManager"

# File paths
APP_DIR = Path.home() / ".waypoint_tools"
DATA_DIR = APP_DIR / "data"
DATABASE_PATH = DATA_DIR / "missions.json"

# Default settings
DEFAULT_BACKUP_FOLDER = Path.home() / "Documents" / "DroneBackups"
DEFAULT_THEME = "light"

# DJI waypoint constants
DJI_WAYPOINT_FOLDER = "Internal Shared Storage/Android/data/dji.go.v5/files/waypoint"
SUPPORTED_EXTENSIONS = [".kmz"]

# UI constants
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700
PREVIEW_THUMBNAIL_HEIGHT = 100
GRID_THUMBNAIL_SIZE = 200

# Drone types (from WPML spec)
DRONE_TYPES = {
    "67": "DJI Mini 4 Pro",
    "68": "DJI Mini 5 Pro",
    "77": "DJI Air 3",
    "60": "DJI Mavic 3",
}

# Finish actions (from WPML spec)
FINISH_ACTIONS = {
    "goHome": "Go Home",
    "autoLand": "Auto Land",
    "hover": "Hover",
    "gotoFirstWaypoint": "Go to First Waypoint",
}

# MTP device detection
MTP_DEVICE_KEYWORDS = ["DJI", "RC"]

# Database schema version
DATABASE_VERSION = "1.0"
