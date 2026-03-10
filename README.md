# DJI Waypoint Tools

A Windows desktop application for managing DJI Mini 5 Pro waypoint mission files from the RC 2 controller.

## Features

- **Mission Management**: Import, organize, and preview waypoint missions
- **Friendly Naming**: Assign custom names, locations, notes, and tags to missions
- **Mission Preview**: View waypoint details, statistics, and thumbnails
- **Search & Filter**: Quickly find missions by name, tags, or metadata
- **RC 2 Integration**: Import/export missions directly from/to your RC 2 controller
- **Backup System**: Create organized backups with friendly folder names
- **Dark/Light Theme**: Choose your preferred visual style

## Requirements

- Windows 10/11
- DJI RC 2 controller (for import/export features)
- DJI Mini 5 Pro drone

## Installation

### Option 1: Download Executable (Recommended)

1. Download `DJI Waypoint Tools.exe` from the releases page
2. Run the executable - no installation required!

### Option 2: Run from Source

```powershell
# Install uv (if not already installed)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Clone the repository
git clone https://github.com/tnordal/waypoint_tools.git
cd waypoint_tools

# Install dependencies
uv sync

# Run the application
uv run waypoint-tools
```

## Usage

### Importing Missions

**From Folder:**
1. Click "Import Folder"
2. Select a folder containing mission folders (UUID-named folders with .kmz files)
3. Missions will be imported into the database

**From RC 2 Controller:**
1. Connect your RC 2 to your PC via USB
2. Wait for "RC 2: Connected" status in the toolbar
3. Click "Import from RC 2"
4. Select missions to import
5. Click OK to transfer

### Editing Mission Metadata

1. Select a mission from the list
2. Click "Edit" in the preview panel
3. Add friendly name, location, notes, and tags
4. Click OK to save

### Exporting to RC 2

1. Connect your RC 2 to your PC via USB
2. Click "Export to RC 2"
3. Select missions to export
4. Click OK to transfer

### Settings

Click "Settings" to configure:
- **Theme**: Light or Dark mode
- **Backup Folder**: Custom location for mission backups

## File Locations

- **Database**: `%USERPROFILE%\.waypoint_tools\data\missions.json`
- **Default Backups**: `%USERPROFILE%\Documents\DJI Waypoint Tools\Backups`

## Mission Folder Structure

DJI waypoint missions are stored in UUID-named folders:

```
2B12AF14-F77B-4772-8EE7-B0D4DD9B7E83/
├── 2B12AF14-F77B-4772-8EE7-B0D4DD9B7E83.kmz  # Waypoint data
└── image/
    ├── WP_001.jpg                              # Waypoint thumbnails
    ├── WP_002.jpg
    └── ...
```

The `.kmz` file is a ZIP archive containing:
- `wpmz/waylines.wpml` - Waypoint coordinates, altitude, speed, actions
- `wpmz/template.kml` - Mission configuration

## Development

### Setup Development Environment

```powershell
# Install dependencies including dev tools
uv sync

# Run the application
uv run python -m waypoint_tools

# Run tests
uv run pytest

# Lint code
uv run ruff check .

# Format code
uv run ruff format .
```

### Building Executable

```powershell
# Build with PyInstaller
uv run pyinstaller waypoint_tools.spec --clean

# Executable will be in dist/ folder
```

### Project Structure

```
src/waypoint_tools/
├── __main__.py              # Entry point
├── app.py                   # QApplication setup
├── ui/                      # PyQt6 widgets
│   ├── main_window.py       # Main window
│   ├── mission_list.py      # Mission list with search/filter
│   ├── preview_panel.py     # Mission preview
│   ├── edit_dialog.py       # Edit mission metadata
│   ├── settings_dialog.py   # Settings
│   ├── import_dialog.py     # Import from RC 2
│   ├── export_dialog.py     # Export to RC 2
│   ├── thumbnail_viewer.py  # Thumbnail grid viewer
│   └── styles.py            # Theme stylesheets
├── models/                  # Data models
│   ├── mission.py           # Mission dataclass
│   └── database.py          # JSON database
├── services/                # Business logic
│   ├── wpml_parser.py       # KMZ/WPML parser
│   ├── file_manager.py      # Import/export operations
│   └── mtp_device.py        # RC 2 MTP detection
└── utils/                   # Utilities
    ├── constants.py         # App configuration
    ├── geo.py               # Geographic calculations
    └── single_instance.py   # Single instance mutex
```

## Code Style

This project follows strict Python code style guidelines:

- **Type hints**: All functions have type annotations
- **Line length**: 100 characters maximum
- **Imports**: Grouped by stdlib, third-party, local
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Tools**: ruff for linting and formatting

See `AGENTS.md` for detailed coding guidelines.

## Troubleshooting

### RC 2 Not Detected

- Ensure USB connection is secure
- Try a different USB cable or port
- Check Windows Device Manager for MTP device
- Restart the application

### Import Shows "No missions found"

- Make sure you selected the correct folder
- The folder should contain UUID-named subfolders
- Each subfolder should have a `.kmz` file with matching UUID name

### Application Won't Start

- Check Windows Application Control settings
- Run as Administrator if needed
- Check antivirus hasn't quarantined the executable

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with PyQt6 for the GUI framework
- Uses pywin32 for Windows MTP/COM access
- Uses lxml for XML parsing
- Packaged with PyInstaller

## Support

For issues and feature requests, please open an issue on GitHub.
