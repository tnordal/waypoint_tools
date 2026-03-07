# DJI Waypoint Tools - Project Plan

## Overview

A Windows GUI application for managing DJI Mini 5 Pro waypoint files from the RC 2 controller. Users generate KML files via [waypointmap.com](https://www.waypointmap.com/) and need a way to organize, backup, and transfer these missions since the RC 2 uses unreadable UUID folder names.

## Problem Statement

- RC 2 waypoint folders have UUID names like `2B12AF14-F77B-4772-8EE7-B0D4DD9B7E83`
- Cannot rename folders or files on the controller
- No way to identify missions without opening each one
- No backup/organization system

## Solution

Desktop app that:
- Provides friendly naming via local metadata database
- Previews mission details (waypoints, distance, altitude, thumbnails)
- Transfers missions between PC and RC 2 via USB
- Backs up missions with organized folder structure

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12+ |
| GUI Framework | PyQt6 |
| Package Manager | uv |
| Distribution | PyInstaller (standalone EXE) |
| XML Parsing | lxml |
| Windows API | pywin32 (MTP access, mutex) |

---

## DJI Waypoint File Structure

Based on analysis of actual RC 2 waypoint folder:

```
{UUID}/
├── {UUID}.kmz                    # Main waypoint file (ZIP archive)
│   └── wpmz/
│       ├── template.kml          # Mission config (drone type, finish action, etc.)
│       └── waylines.wpml         # Waypoint data (coordinates, altitude, speed, actions)
└── image/
    ├── ShotSnap.json             # Shot metadata (usually empty {})
    └── WP_*.jpg                  # Waypoint thumbnails (180x135 JPEG)
```

### Key Data Fields (from waylines.wpml)

| Field | Location | Example |
|-------|----------|---------|
| Coordinates | `Placemark/Point/coordinates` | `104.591298,17.344573` |
| Altitude | `Placemark/wpml:executeHeight` | `11.1` (meters) |
| Speed | `Placemark/wpml:waypointSpeed` | `2.5` (m/s) |
| Heading | `wpml:waypointHeadingAngle` | `155` (degrees) |
| Gimbal Pitch | `wpml:gimbalPitchRotateAngle` | `-20.5` (degrees) |
| Finish Action | `wpml:finishAction` | `goHome` |
| Drone Type | `wpml:droneEnumValue` | `68` (Mini 5 Pro) |

---

## Architecture

```
waypoint_tools/
├── src/
│   └── waypoint_tools/
│       ├── __init__.py
│       ├── __main__.py              # Entry point
│       ├── app.py                   # QApplication + single-instance
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py       # Main window (remembers size/position)
│       │   ├── mission_list.py      # Mission list widget
│       │   ├── preview_panel.py     # Mission preview + thumbnails
│       │   ├── thumbnail_viewer.py  # Grid popup for thumbnails
│       │   ├── edit_dialog.py       # Edit mission metadata
│       │   ├── transfer_dialog.py   # Import/Export progress
│       │   ├── settings_dialog.py   # App settings
│       │   └── styles.py            # Light/Dark theme QSS
│       ├── models/
│       │   ├── __init__.py
│       │   ├── mission.py           # Mission dataclass
│       │   └── database.py          # JSON database CRUD
│       ├── services/
│       │   ├── __init__.py
│       │   ├── device_manager.py    # MTP device detection (RC 2)
│       │   ├── file_manager.py      # Copy, backup, restore
│       │   └── wpml_parser.py       # Parse waylines.wpml
│       └── utils/
│           ├── __init__.py
│           ├── constants.py         # Paths, enums, config
│           ├── single_instance.py   # Windows mutex
│           └── geo.py               # Haversine distance calc
├── data/
│   └── missions.json                # User metadata database
├── resources/
│   ├── icon.ico                     # App icon (Windows)
│   ├── icon.png                     # App icon (PNG)
│   └── icons/                       # UI icons
├── pyproject.toml                   # uv project config
├── uv.lock                          # Locked dependencies
├── build.py                         # Build script
├── waypoint_tools.spec            # PyInstaller spec
├── PLANNING.md                      # This file
└── README.md                        # User documentation
```

---

## Features

### 1. Single Instance Application
- Windows named mutex prevents multiple instances
- Second launch brings existing window to foreground

### 2. Window State Persistence
- Remember window size and position
- Remember splitter positions
- Store in QSettings (Windows registry)

### 3. Mission List View
| Column | Source |
|--------|--------|
| Friendly Name | User metadata |
| UUID | Folder name (truncated) |
| Location | User metadata |
| Waypoints | Parsed from WPML |
| Date | File modified or user metadata |
| Tags | User metadata |
| Source | Controller / Local / Both |

### 4. Preview Panel
- Mission summary (waypoints, distance, altitude range, speed, finish action)
- Center point coordinates
- Waypoint table with details
- Thumbnail strip (horizontal scrollable)
- Click thumbnail strip to open grid viewer

### 5. Thumbnail Viewer
- Modal dialog with grid of all waypoint thumbnails
- Click to view full size
- Keyboard navigation

### 6. Theme Support
- Light theme (default)
- Dark theme
- Toggle in settings, persisted

### 7. Transfer Operations
- **Scan Controller**: Auto-detect RC 2 via MTP
- **Import**: Copy from RC 2 to local backup
- **Export**: Copy from local to RC 2
- Progress dialog with cancel option

### 8. Backup System
```
{backup_folder}/
└── {friendly_name}_{uuid_short}/
    ├── {UUID}.kmz
    ├── image/
    │   └── *.jpg
    └── metadata.json
```

### 9. Search & Filter
- Search by name, location, notes
- Filter by tags
- Sort by date, name, waypoint count

---

## Data Model

### missions.json
```json
{
  "version": "1.0",
  "settings": {
    "backup_folder": "D:\\DroneBackups",
    "theme": "light"
  },
  "tags": ["survey", "inspection", "video", "mapping"],
  "missions": {
    "2B12AF14-F77B-4772-8EE7-B0D4DD9B7E83": {
      "friendly_name": "Temple Survey",
      "location": "Wat Phu, Laos",
      "notes": "Morning flight around the temple",
      "tags": ["survey", "temple"],
      "date_created": "2026-03-01T10:30:00",
      "date_modified": "2026-03-02T14:20:00",
      "cached_info": {
        "waypoint_count": 12,
        "total_distance_m": 245.3,
        "altitude_min": 3.8,
        "altitude_max": 19.5,
        "center_lat": 17.3443,
        "center_lon": 104.5914
      }
    }
  }
}
```

### Mission Dataclass
```python
@dataclass
class Mission:
    uuid: str
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
    
    # Runtime
    source: Literal["controller", "local", "both"] = "local"
    thumbnail_paths: list[str] = field(default_factory=list)
```

---

## Dependencies

### pyproject.toml
```toml
[project]
name = "waypoint-tools"
version = "1.0.0"
description = "DJI Mini 5 Pro Waypoint File Manager"
requires-python = ">=3.12"
dependencies = [
    "PyQt6>=6.6.0",
    "pywin32>=306",
    "lxml>=5.1.0",
]

[project.scripts]
waypoint-tools = "waypoint_tools.__main__:main"

[project.gui-scripts]
waypoint-tools-gui = "waypoint_tools.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pyinstaller>=6.3.0",
    "pytest>=8.0.0",
    "ruff>=0.2.0",
]
```

---

## Build & Distribution

### Development
```bash
# Install uv (Windows PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create and sync project
uv sync

# Run app
uv run python -m waypoint_tools

# Run tests
uv run pytest
```

### Build EXE
```bash
uv run pyinstaller waypoint_tools.spec
# Output: dist/WaypointTools.exe
```

### PyInstaller Spec Highlights
```python
exe = EXE(
    ...
    name='WaypointTools',
    icon='resources/icon.ico',
    console=False,      # GUI app, no console
    onefile=True,       # Single EXE file
)
```

---

## UI Design

### Main Window Layout
```
+------------------------------------------------------------------------------+
|  DJI Waypoint Tools                                             [_] [O] [X]  |
+------------------------------------------------------------------------------+
|  [Controller] [Local Backup]          RC 2 Connected            [Settings]   |
+------------------------------------------------------------------------------+
|  Search: [_______________]  Tags: [All v]    [Import] [Export] [Backup All]  |
+----------------------------------------------+-------------------------------+
|  MISSIONS                                    |  PREVIEW                      |
| +------------------------------------------+ | +---------------------------+ |
| | [x] Temple Survey                        | | | Temple Survey             | |
| |     Wat Phu, Laos | 12 pts | 2026-03-01  | | | UUID: 2B12AF14-F77B...   | |
| |     [survey] [temple]                    | | |                           | |
| +------------------------------------------+ | | Waypoints:     12         | |
| | [ ] City Mapping                         | | | Distance:      245.3 m    | |
| |     Vientiane | 24 pts | 2026-02-28      | | | Est. Time:     ~1m 38s    | |
| |     [mapping]                            | | | Altitude:      3.8-19.5m  | |
| +------------------------------------------+ | | Speed:         2.5 m/s    | |
| | [ ] 8A3F2E91-BC44-...                    | | | Finish:        Go Home    | |
| |     (no name) | 8 pts | 2026-02-25       | | | Center: 17.34N 104.59E    | |
| +------------------------------------------+ | +---------------------------+ |
|                                              | | Waypoints:                | |
|                                              | |  0: 17.34N 104.59E @11.1m | |
|                                              | |  1: 17.34N 104.59E @11.8m | |
|                                              | +---------------------------+ |
|                                              | | [img][img][img][img]  [>] | |
|                                              | +---------------------------+ |
+----------------------------------------------+-------------------------------+
|  3 missions | 1 selected | Backup: D:\DroneBackups                          |
+------------------------------------------------------------------------------+
```

### Color Scheme

#### Light Theme
- Background: #FFFFFF
- Surface: #F5F5F5
- Primary: #1976D2 (blue)
- Text: #212121
- Secondary Text: #757575

#### Dark Theme
- Background: #121212
- Surface: #1E1E1E
- Primary: #90CAF9 (light blue)
- Text: #FFFFFF
- Secondary Text: #B0B0B0

---

## MTP Device Access

Using Windows Shell COM via pywin32:

```python
from win32com.shell import shell, shellcon

def find_mtp_devices():
    """Find portable devices in Windows shell namespace"""
    # Access "This PC" > Portable Devices
    # Look for "DJI" or "RC" in device name
    # Return path to device
    
def get_waypoint_folder(device):
    """Navigate to waypoint folder on device"""
    # Path: Internal Shared Storage/Android/data/dji.go.v5/files/waypoint
    return waypoint_folder_path
```

---

## Development Phases

| Phase | Description | Est. Time |
|-------|-------------|-----------|
| 1 | Project setup (uv, folders, constants) | 1.0 hr |
| 2 | Single-instance mutex | 0.5 hr |
| 3 | WPML parser + distance calculation | 1.5 hr |
| 4 | JSON database model + CRUD | 1.0 hr |
| 5 | Main window + window state persistence | 2.0 hr |
| 6 | Mission list widget + search/filter | 2.0 hr |
| 7 | Preview panel + waypoint table | 2.0 hr |
| 8 | Thumbnail strip + grid viewer | 1.5 hr |
| 9 | Light/Dark theme system | 1.0 hr |
| 10 | Edit dialog | 1.0 hr |
| 11 | MTP device detection | 2.0 hr |
| 12 | Import/Export/Backup operations | 2.5 hr |
| 13 | Settings dialog | 1.0 hr |
| 14 | App icon creation | 0.5 hr |
| 15 | PyInstaller packaging + testing | 2.0 hr |

**Total Estimate: ~21.5 hours**

---

## Testing Strategy

### Manual Testing
- Connect RC 2, verify detection
- Import mission from controller
- Edit metadata, verify persistence
- Export mission back to controller
- Verify mission works on drone

### Automated Tests
- WPML parser unit tests
- Database CRUD tests
- Distance calculation tests
- Mission model tests

---

## Future Enhancements (Out of Scope v1.0)

- [ ] Map view with flight path visualization
- [ ] Edit waypoint parameters (altitude, speed)
- [ ] Batch operations (multi-select)
- [ ] Export to other formats (GPX, CSV)
- [ ] Mission comparison
- [ ] Cloud backup integration
- [ ] Localization (multi-language)

---

## References

- [WaypointMap.com](https://www.waypointmap.com/) - KML generator
- [DJI Mini 5 Pro](https://www.dji.com/mini-5-pro) - Drone specs
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
