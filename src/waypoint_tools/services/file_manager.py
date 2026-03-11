"""File manager for mission import/export operations."""

import json
import logging
import shutil
import uuid
from pathlib import Path

from waypoint_tools.models.database import Database
from waypoint_tools.models.mission import Mission
from waypoint_tools.services.wpml_parser import parse_kmz
from waypoint_tools.utils.constants import DATA_DIR

logger = logging.getLogger(__name__)


def _is_mission_folder(folder: Path) -> bool:
    """
    Check if a folder is a mission folder (contains UUID.kmz file).

    Args:
        folder: Path to check

    Returns:
        True if folder is a mission folder
    """
    folder_name = folder.name
    if len(folder_name) != 36 or folder_name.count("-") != 4:
        return False

    kmz_file = folder / f"{folder_name}.kmz"
    return kmz_file.exists()


def _parse_mission_folder(mission_folder: Path) -> Mission | None:
    """
    Parse a single mission folder.

    Args:
        mission_folder: Path to mission folder

    Returns:
        Parsed mission or None if parsing failed
    """
    folder_name = mission_folder.name
    kmz_file = mission_folder / f"{folder_name}.kmz"

    if not kmz_file.exists():
        logger.warning(f"No KMZ file found for mission: {folder_name}")
        return None

    # Parse the mission
    mission = parse_kmz(kmz_file, folder_name)
    if mission:
        # Set the file path to the mission folder
        mission.file_path = str(mission_folder)

        # Check for thumbnails
        image_folder = mission_folder / "image"
        if image_folder.exists():
            thumbnails = list(image_folder.glob("WP_*.jpg"))
            mission.thumbnail_paths = [str(t) for t in thumbnails]

        logger.info(f"Found mission: {folder_name}")

    return mission


def scan_folder_for_missions(folder: Path) -> list[Mission]:
    """
    Scan a folder for DJI waypoint missions.

    Handles two cases:
    1. Folder contains UUID-named mission folders (normal case)
    2. Folder itself is a mission folder (user selected mission folder directly)

    Args:
        folder: Path to scan

    Returns:
        List of parsed missions
    """
    missions: list[Mission] = []

    if not folder.exists() or not folder.is_dir():
        logger.warning(f"Folder does not exist: {folder}")
        return missions

    # Case 1: Check if the selected folder itself is a mission folder
    if _is_mission_folder(folder):
        logger.info(f"Selected folder is a mission folder: {folder.name}")
        mission = _parse_mission_folder(folder)
        if mission:
            missions.append(mission)
        return missions

    # Case 2: Look for mission folders inside the selected folder
    for mission_folder in folder.iterdir():
        if not mission_folder.is_dir():
            continue

        if not _is_mission_folder(mission_folder):
            continue

        mission = _parse_mission_folder(mission_folder)
        if mission:
            missions.append(mission)

    return missions


def import_missions_from_folder(folder: Path) -> tuple[int, int]:
    """
    Import missions from a folder into the database.

    Args:
        folder: Path to folder containing mission folders

    Returns:
        Tuple of (new_count, updated_count)
    """
    db = Database.get_instance()
    missions = scan_folder_for_missions(folder)

    new_count = 0
    updated_count = 0

    for mission in missions:
        # Check if mission already exists
        existing = db.get_mission(mission.uuid)
        if existing:
            # Update cached info and file path but preserve user metadata
            mission.friendly_name = existing.friendly_name
            mission.location = existing.location
            mission.notes = existing.notes
            mission.tags = existing.tags
            mission.date_created = existing.date_created
            # Keep the new file_path (mission may have been moved)
            db.add_mission(mission)
            updated_count += 1
            logger.debug(f"Updated existing mission: {mission.uuid}")
        else:
            db.add_mission(mission)
            new_count += 1
            logger.debug(f"Imported new mission: {mission.uuid}")

    logger.info(
        f"Imported {new_count} new mission(s), updated {updated_count} existing"
    )
    return new_count, updated_count


def copy_mission_folder(
    source_folder: Path,
    destination_folder: Path,
    uuid: str,
) -> bool:
    """
    Copy a mission folder from source to destination.

    Args:
        source_folder: Source directory containing mission folders
        destination_folder: Destination directory
        uuid: Mission UUID

    Returns:
        True if successful, False otherwise
    """
    source_mission = source_folder / uuid
    dest_mission = destination_folder / uuid

    if not source_mission.exists():
        logger.error(f"Source mission not found: {source_mission}")
        return False

    try:
        # Create destination if needed
        destination_folder.mkdir(parents=True, exist_ok=True)

        # Copy entire folder
        if dest_mission.exists():
            shutil.rmtree(dest_mission)

        shutil.copytree(source_mission, dest_mission)
        logger.info(f"Copied mission {uuid} to {destination_folder}")
        return True

    except Exception as e:
        logger.error(f"Failed to copy mission {uuid}: {e}")
        return False


def create_backup(
    mission: Mission,
    source_folder: Path,
    backup_folder: Path,
) -> bool:
    """
    Create a backup of a mission with friendly folder name.

    Args:
        mission: Mission to backup
        source_folder: Source directory containing mission folders
        backup_folder: Backup directory

    Returns:
        True if successful, False otherwise
    """
    # Create backup folder name
    friendly_name = mission.friendly_name or "unnamed"
    # Sanitize filename
    friendly_name = "".join(
        c for c in friendly_name if c.isalnum() or c in (" ", "-", "_")
    ).strip()
    uuid_short = mission.uuid[:8]
    backup_name = f"{friendly_name}_{uuid_short}"

    source_mission = source_folder / mission.uuid
    dest_mission = backup_folder / backup_name

    if not source_mission.exists():
        logger.error(f"Source mission not found: {source_mission}")
        return False

    try:
        # Create backup folder
        backup_folder.mkdir(parents=True, exist_ok=True)

        # Copy mission folder
        if dest_mission.exists():
            shutil.rmtree(dest_mission)

        shutil.copytree(source_mission, dest_mission)

        # Save metadata
        metadata_file = dest_mission / "metadata.json"

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(mission.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Backed up mission to {dest_mission}")
        return True

    except Exception as e:
        logger.error(f"Failed to backup mission {mission.uuid}: {e}")
        return False


def import_kmz_file(kmz_path: Path) -> Mission | None:
    """
    Import a single KMZ file (e.g., from waypointmap.com).

    Creates a mission folder with generated UUID, copies the KMZ file,
    and imports it into the database.

    Args:
        kmz_path: Path to the KMZ file to import

    Returns:
        Imported Mission object, or None if import failed
    """
    if not kmz_path.exists() or not kmz_path.is_file():
        logger.error(f"KMZ file not found: {kmz_path}")
        return None

    if kmz_path.suffix.lower() != ".kmz":
        logger.error(f"Not a KMZ file: {kmz_path}")
        return None

    mission_folder = None
    try:
        # Generate a new UUID for this mission
        mission_uuid = str(uuid.uuid4()).upper()
        logger.info(f"Importing KMZ file as mission {mission_uuid}")

        # Create mission folder in data directory
        missions_folder = DATA_DIR / "missions"
        missions_folder.mkdir(parents=True, exist_ok=True)

        mission_folder = missions_folder / mission_uuid
        mission_folder.mkdir(parents=True, exist_ok=True)

        # Copy KMZ file with UUID name
        dest_kmz = mission_folder / f"{mission_uuid}.kmz"
        shutil.copy2(kmz_path, dest_kmz)
        logger.info(f"Copied KMZ to {dest_kmz}")

        # Parse the mission
        mission = parse_kmz(dest_kmz, mission_uuid)
        if not mission:
            raise ValueError(f"Failed to parse KMZ file: {dest_kmz}")

        # Set file path
        mission.file_path = str(mission_folder)

        # Add to database
        db = Database.get_instance()
        db.add_mission(mission)
        logger.info(f"Successfully imported mission {mission_uuid}")

        return mission

    except Exception as e:
        logger.error(f"Failed to import KMZ file {kmz_path}: {e}")
        # Clean up on error
        if mission_folder and mission_folder.exists():
            shutil.rmtree(mission_folder, ignore_errors=True)
        return None
