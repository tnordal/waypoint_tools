"""JSON database for mission metadata."""

import json
import logging
from datetime import datetime
from pathlib import Path

from waypoint_tools.models.mission import Mission
from waypoint_tools.utils.constants import (
    DATABASE_PATH,
    DATABASE_VERSION,
    DATA_DIR,
    DEFAULT_BACKUP_FOLDER,
    DEFAULT_THEME,
)

logger = logging.getLogger(__name__)


class Database:
    """Singleton database for mission metadata management."""
    
    _instance: "Database | None" = None
    
    def __init__(self) -> None:
        """Initialize database."""
        self.db_path = DATABASE_PATH
        self.data: dict = {}
        self._ensure_data_dir()
        self.load()
    
    @classmethod
    def get_instance(cls) -> "Database":
        """Get singleton database instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _ensure_data_dir(self) -> None:
        """Ensure data directory exists."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> None:
        """Load database from disk."""
        if not self.db_path.exists():
            logger.info("Database file not found, creating new database")
            self.data = self._create_default_db()
            self.save()
            return
        
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            logger.info(f"Loaded database with {len(self.data.get('missions', {}))} missions")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse database JSON: {e}")
            self.data = self._create_default_db()
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            self.data = self._create_default_db()
    
    def save(self) -> None:
        """Save database to disk atomically."""
        try:
            # Write to temp file first
            temp_path = self.db_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            # Atomic replace
            temp_path.replace(self.db_path)
            logger.debug("Database saved successfully")
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
    
    def _create_default_db(self) -> dict:
        """Create default database structure."""
        return {
            "version": DATABASE_VERSION,
            "settings": {
                "backup_folder": str(DEFAULT_BACKUP_FOLDER),
                "theme": DEFAULT_THEME,
            },
            "tags": [],
            "missions": {},
        }
    
    # Settings methods
    
    def get_setting(self, key: str, default: str | None = None) -> str | None:
        """Get a setting value."""
        return self.data.get("settings", {}).get(key, default)
    
    def set_setting(self, key: str, value: str) -> None:
        """Set a setting value."""
        if "settings" not in self.data:
            self.data["settings"] = {}
        self.data["settings"][key] = value
        self.save()
    
    def get_backup_folder(self) -> Path:
        """Get backup folder path."""
        folder_str = self.get_setting("backup_folder", str(DEFAULT_BACKUP_FOLDER))
        return Path(folder_str) if folder_str else DEFAULT_BACKUP_FOLDER
    
    def set_backup_folder(self, folder: Path) -> None:
        """Set backup folder path."""
        self.set_setting("backup_folder", str(folder))
    
    def get_theme(self) -> str:
        """Get current theme."""
        return self.get_setting("theme", DEFAULT_THEME) or DEFAULT_THEME
    
    def set_theme(self, theme: str) -> None:
        """Set current theme."""
        self.set_setting("theme", theme)
    
    # Tags methods
    
    def get_all_tags(self) -> list[str]:
        """Get all available tags."""
        return self.data.get("tags", [])
    
    def add_tag(self, tag: str) -> None:
        """Add a new tag to the global tag list."""
        if "tags" not in self.data:
            self.data["tags"] = []
        if tag not in self.data["tags"]:
            self.data["tags"].append(tag)
            self.data["tags"].sort()
            self.save()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the global tag list."""
        if "tags" in self.data and tag in self.data["tags"]:
            self.data["tags"].remove(tag)
            self.save()
    
    # Mission CRUD methods
    
    def get_mission(self, uuid: str) -> Mission | None:
        """Get mission by UUID."""
        missions_data = self.data.get("missions", {})
        if uuid not in missions_data:
            return None
        
        return Mission.from_dict(uuid, missions_data[uuid])
    
    def get_all_missions(self) -> list[Mission]:
        """Get all missions."""
        missions_data = self.data.get("missions", {})
        return [
            Mission.from_dict(uuid, data)
            for uuid, data in missions_data.items()
        ]
    
    def add_mission(self, mission: Mission) -> None:
        """Add or update a mission."""
        if "missions" not in self.data:
            self.data["missions"] = {}
        
        # Set modified date
        mission.date_modified = datetime.now()
        
        # Set created date if new
        if mission.uuid not in self.data["missions"]:
            mission.date_created = datetime.now()
        
        self.data["missions"][mission.uuid] = mission.to_dict()
        
        # Add any new tags to global tag list
        for tag in mission.tags:
            self.add_tag(tag)
        
        self.save()
        logger.info(f"Saved mission {mission.uuid}")
    
    def update_mission(self, mission: Mission) -> None:
        """Update an existing mission (alias for add_mission)."""
        self.add_mission(mission)
    
    def delete_mission(self, uuid: str) -> bool:
        """
        Delete a mission from the database.
        
        Returns:
            True if deleted, False if not found
        """
        if "missions" not in self.data:
            return False
        
        if uuid in self.data["missions"]:
            del self.data["missions"][uuid]
            self.save()
            logger.info(f"Deleted mission {uuid}")
            return True
        
        return False
    
    def mission_exists(self, uuid: str) -> bool:
        """Check if a mission exists in the database."""
        return uuid in self.data.get("missions", {})
    
    def search_missions(
        self,
        query: str | None = None,
        tags: list[str] | None = None,
    ) -> list[Mission]:
        """
        Search missions by query string and/or tags.
        
        Args:
            query: Search string to match against name, location, notes
            tags: List of tags that missions must have (any match)
        
        Returns:
            List of matching missions
        """
        missions = self.get_all_missions()
        
        if query:
            query_lower = query.lower()
            missions = [
                m for m in missions
                if (
                    (m.friendly_name and query_lower in m.friendly_name.lower())
                    or (m.location and query_lower in m.location.lower())
                    or (m.notes and query_lower in m.notes.lower())
                    or query_lower in m.uuid.lower()
                )
            ]
        
        if tags:
            missions = [
                m for m in missions
                if any(tag in m.tags for tag in tags)
            ]
        
        return missions
