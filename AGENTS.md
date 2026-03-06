# AGENTS.md - Coding Agent Guidelines

This document provides guidelines for AI coding agents working on the DJI Waypoint Manager project.

## Project Overview

- **Type**: Windows GUI desktop application
- **Language**: Python 3.11+
- **Framework**: PyQt6
- **Package Manager**: uv
- **Target Platform**: Windows 10/11

---

## Build & Run Commands

### Setup
```powershell
uv sync                              # Install all dependencies
```

### Run Application
```powershell
uv run python -m waypoint_manager    # Run from module
uv run waypoint-manager              # Run via entry point
```

### Linting & Formatting
```powershell
uv run ruff check .                  # Lint all files
uv run ruff check src/               # Lint src directory only
uv run ruff check path/to/file.py    # Lint single file
uv run ruff format .                 # Format all files
uv run ruff format path/to/file.py   # Format single file
uv run ruff check --fix .            # Auto-fix lint issues
```

### Testing
```powershell
uv run pytest                        # Run all tests
uv run pytest tests/                 # Run tests in directory
uv run pytest tests/test_parser.py   # Run single test file
uv run pytest tests/test_parser.py::test_parse_waypoints  # Run single test
uv run pytest -v                     # Verbose output
uv run pytest -x                     # Stop on first failure
uv run pytest --tb=short             # Shorter tracebacks
```

### Build EXE
```powershell
uv run pyinstaller waypoint_manager.spec
```

---

## Project Structure

```
src/waypoint_manager/
├── __main__.py          # Entry point
├── app.py               # QApplication setup
├── ui/                  # PyQt6 widgets and dialogs
├── models/              # Data models and database
├── services/            # Business logic (parsing, file ops, MTP)
└── utils/               # Helpers (constants, geo calculations)
```

---

## Code Style Guidelines

### Python Version
- Use Python 3.11+ features
- Use `|` for union types: `str | None` (not `Optional[str]`)
- Use `list[str]` not `List[str]` (lowercase generics)

### Imports
Order imports as follows, separated by blank lines:
```python
# 1. Standard library
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# 2. Third-party
from lxml import etree
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QWidget

# 3. Local imports
from waypoint_manager.models.mission import Mission
from waypoint_manager.utils.constants import APP_NAME
```

### Formatting
- **Line length**: 100 characters max
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings `"hello"`
- **Trailing commas**: Use in multi-line collections
- **Blank lines**: 2 between top-level definitions, 1 within classes

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `MissionListWidget` |
| Functions/methods | snake_case | `parse_waypoints()` |
| Variables | snake_case | `waypoint_count` |
| Constants | UPPER_SNAKE | `DEFAULT_SPEED` |
| Private | Leading underscore | `_internal_state` |
| PyQt signals | snake_case | `mission_selected` |

### Type Hints
Always use type hints for function signatures:
```python
def parse_kmz(path: Path) -> Mission:
    ...

def calculate_distance(points: list[tuple[float, float]]) -> float:
    ...

def get_mission(uuid: str) -> Mission | None:
    ...
```

### Dataclasses
Use dataclasses for data models:
```python
from dataclasses import dataclass, field

@dataclass
class Mission:
    uuid: str
    friendly_name: str | None = None
    tags: list[str] = field(default_factory=list)
```

### PyQt6 Patterns
```python
class MissionListWidget(QWidget):
    # Signals at class level
    mission_selected = pyqtSignal(str)  # emits UUID
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        ...
    
    def _connect_signals(self) -> None:
        """Connect internal signals to slots."""
        ...
```

---

## Error Handling

### Use Specific Exceptions
```python
# Good
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {e}")
    return None

# Bad - too broad
try:
    data = json.loads(content)
except Exception:
    return None
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Parsing waypoint file")
logger.info(f"Loaded {count} missions")
logger.warning(f"Missing thumbnail: {path}")
logger.error(f"Failed to connect to device: {e}")
```

### User-Facing Errors
Use QMessageBox for user-facing errors:
```python
from PyQt6.QtWidgets import QMessageBox

QMessageBox.warning(
    self,
    "Connection Error",
    "Could not connect to RC 2 controller.\nCheck USB connection."
)
```

---

## File Operations

### Always Use pathlib
```python
from pathlib import Path

# Good
config_path = Path.home() / ".waypoint_manager" / "config.json"
kmz_files = list(folder.glob("*.kmz"))

# Bad
config_path = os.path.join(os.path.expanduser("~"), ".waypoint_manager", "config.json")
```

### Safe File Writing
```python
import json
from pathlib import Path

def save_database(path: Path, data: dict) -> None:
    """Write JSON atomically to prevent corruption."""
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(data, indent=2))
    temp_path.replace(path)  # Atomic on Windows
```

---

## Testing Guidelines

### Test File Naming
- Test files: `test_<module>.py`
- Test functions: `test_<description>()`

### Test Structure
```python
import pytest
from waypoint_manager.services.wpml_parser import parse_waypoints

def test_parse_waypoints_returns_correct_count():
    """Parser should extract all waypoints from WPML."""
    result = parse_waypoints(SAMPLE_WPML)
    assert len(result.waypoints) == 12

def test_parse_waypoints_handles_empty_file():
    """Parser should return empty list for empty WPML."""
    result = parse_waypoints("")
    assert result.waypoints == []

@pytest.fixture
def sample_mission_folder(tmp_path):
    """Create a temporary mission folder for testing."""
    ...
```

---

## Windows-Specific Notes

- Use `pywin32` for MTP device access and Windows mutex
- Test MTP functionality manually (cannot be unit tested)
- Use `QSettings` with organization/app name for registry storage
- File paths may contain spaces - always use `Path` objects

---

## Common Patterns

### Singleton for Database
```python
class Database:
    _instance: "Database | None" = None
    
    @classmethod
    def get_instance(cls) -> "Database":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

### QSettings Usage
```python
from PyQt6.QtCore import QSettings

settings = QSettings("WaypointManager", "DJI Waypoint Manager")
settings.setValue("geometry", self.saveGeometry())
geometry = settings.value("geometry")
```

---

## Do NOT

- Do not use `print()` for debugging - use `logger`
- Do not catch bare `Exception` without re-raising or logging
- Do not use `os.path` - use `pathlib.Path`
- Do not hardcode paths - use constants or settings
- Do not block the UI thread - use QThread for long operations
- Do not use `Optional[X]` - use `X | None`
- Do not use `List`, `Dict`, `Tuple` from typing - use lowercase builtins
