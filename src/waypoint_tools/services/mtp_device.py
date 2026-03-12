"""MTP device detection and file access for RC 2 controller."""

import logging
from pathlib import Path

import win32com.client

logger = logging.getLogger(__name__)

# Expected path on RC 2 controller
RC2_WAYPOINT_PATH = "Internal shared storage/Android/data/dji.go.v5/files/waypoint"


class MTPDevice:
    """Represents an MTP device (RC 2 controller)."""

    def __init__(self, name: str, shell_folder) -> None:
        """
        Initialize MTP device.

        Args:
            name: Device name
            shell_folder: Windows Shell folder object
        """
        self.name = name
        self.shell_folder = shell_folder
        self._waypoint_folder = None

    def find_waypoint_folder(self) -> bool:
        """
        Navigate to the waypoint folder on the device.

        Returns:
            True if waypoint folder found, False otherwise
        """
        try:
            # Navigate: Internal shared storage -> Android -> data -> dji.go.v5 -> files -> FlightRoute
            path_parts = RC2_WAYPOINT_PATH.split("/")

            current_folder = self.shell_folder

            for part in path_parts:
                found = False
                try:
                    items = current_folder.Items()
                    # List available folders at this level for debugging
                    available_folders = []
                    for item in items:
                        if item.IsFolder:
                            available_folders.append(item.Name)
                            if item.Name == part:
                                current_folder = item.GetFolder
                                found = True
                                break

                    if not found:
                        logger.warning(
                            f"Path component not found: {part}. "
                            f"Available folders: {', '.join(available_folders)}"
                        )
                        return False

                except Exception as e:
                    logger.error(f"Failed to enumerate folder items: {e}")
                    return False

            self._waypoint_folder = current_folder
            logger.info(f"Found waypoint folder on {self.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to find waypoint folder: {e}")
            return False

    def get_waypoint_folder(self):
        """
        Get the waypoint folder object.

        Returns:
            Shell folder object for waypoints, or None
        """
        return self._waypoint_folder

    def list_missions(self) -> list[str]:
        """
        List mission UUIDs on the device.

        Returns:
            List of mission UUID folder names
        """
        if not self._waypoint_folder:
            if not self.find_waypoint_folder():
                return []

        missions = []
        try:
            items = self._waypoint_folder.Items()
            for item in items:
                if item.IsFolder:
                    folder_name = item.Name
                    # Check if it looks like a UUID
                    if len(folder_name) == 36 and folder_name.count("-") == 4:
                        missions.append(folder_name)
        except Exception as e:
            logger.error(f"Failed to list missions: {e}")

        return missions


def detect_rc2_controller() -> MTPDevice | None:
    """
    Detect connected RC 2 controller via MTP.

    Returns:
        MTPDevice object if found, None otherwise
    """
    try:
        shell = win32com.client.Dispatch("Shell.Application")

        # Get "This PC" namespace (17 = Computer)
        computer = shell.NameSpace(17)

        if not computer:
            logger.warning("Could not access Computer namespace")
            return None

        # Iterate through devices
        items = computer.Items()
        for item in items:
            device_name = item.Name
            logger.debug(f"Checking device: {device_name}")

            # Look for RC 2 controller (may show as "DJI RC 2" or similar)
            if "RC" in device_name.upper() or "DJI" in device_name.upper():
                logger.info(f"Found potential RC 2 device: {device_name}")

                # Get the folder for this device
                device_folder = item.GetFolder
                if device_folder:
                    device = MTPDevice(device_name, device_folder)

                    # Verify it has the waypoint folder structure
                    if device.find_waypoint_folder():
                        logger.info(f"RC 2 controller detected: {device_name}")
                        return device
                    else:
                        logger.info(
                            f"Device {device_name} does not have waypoint folder"
                        )

        logger.debug("No RC 2 controller found")
        return None

    except ImportError:
        logger.error("pywin32 not installed - MTP access unavailable")
        return None
    except Exception as e:
        logger.error(f"Error detecting RC 2 controller: {e}")
        return None


def copy_from_device(device: MTPDevice, mission_uuid: str, dest_folder: Path) -> bool:
    """
    Copy a mission folder from device to local folder.

    Args:
        device: MTP device
        mission_uuid: Mission UUID to copy
        dest_folder: Destination folder on PC

    Returns:
        True if successful, False otherwise
    """
    try:
        waypoint_folder = device.get_waypoint_folder()
        if not waypoint_folder:
            logger.error("Waypoint folder not accessible")
            return False

        # Find the mission folder
        mission_folder = None
        items = waypoint_folder.Items()
        for item in items:
            if item.Name == mission_uuid and item.IsFolder:
                mission_folder = item.GetFolder
                break

        if not mission_folder:
            logger.error(f"Mission folder not found: {mission_uuid}")
            return False

        # Create destination folder
        dest_mission = dest_folder / mission_uuid
        dest_mission.mkdir(parents=True, exist_ok=True)

        # Copy files using Shell
        shell = win32com.client.Dispatch("Shell.Application")
        dest_shell = shell.NameSpace(str(dest_mission))

        # Copy all items from mission folder
        mission_items = mission_folder.Items()
        for item in mission_items:
            dest_shell.CopyHere(item, 16)  # 16 = no UI

        logger.info(f"Copied mission {mission_uuid} from device to {dest_mission}")
        return True

    except Exception as e:
        logger.error(f"Failed to copy mission from device: {e}")
        return False


def copy_to_device(device: MTPDevice, source_folder: Path, mission_uuid: str) -> bool:
    """
    Copy a mission folder from local folder to device.

    Args:
        device: MTP device
        source_folder: Source folder on PC containing mission
        mission_uuid: Mission UUID to copy

    Returns:
        True if successful, False otherwise
    """
    try:
        waypoint_folder = device.get_waypoint_folder()
        if not waypoint_folder:
            logger.error("Waypoint folder not accessible")
            return False

        source_mission = source_folder / mission_uuid
        if not source_mission.exists():
            logger.error(f"Source mission folder not found: {source_mission}")
            return False

        # Copy folder to device using Shell
        shell = win32com.client.Dispatch("Shell.Application")

        # Get the parent folder namespace and the mission folder item
        parent_namespace = shell.NameSpace(str(source_folder))

        # Find the mission folder item
        mission_folder_item = None
        for item in parent_namespace.Items():
            if item.Name == mission_uuid:
                mission_folder_item = item
                break

        if not mission_folder_item:
            logger.error(f"Could not find mission folder item: {mission_uuid}")
            return False

        # Copy the folder to device (16 = no UI, 4 = no confirmation)
        waypoint_folder.CopyHere(mission_folder_item, 20)  # 16 + 4 = 20

        logger.info(f"Copied mission {mission_uuid} to device")
        return True

    except Exception as e:
        logger.error(f"Failed to copy mission to device: {e}")
        return False


def replace_mission_on_device(
    device: MTPDevice, source_kmz_path: Path, target_controller_uuid: str
) -> bool:
    """
    Replace a mission on the controller.

    This function:
    1. Finds the target UUID folder on the controller
    2. Deletes all files in that folder
    3. Copies the source KMZ file, renamed to match target UUID

    Args:
        device: MTP device (RC 2 controller)
        source_kmz_path: Path to local KMZ file to copy
        target_controller_uuid: UUID of controller folder to replace

    Returns:
        True if successful, False otherwise
    """
    try:
        waypoint_folder = device.get_waypoint_folder()
        if not waypoint_folder:
            logger.error("Waypoint folder not accessible")
            return False

        if not source_kmz_path.exists():
            logger.error(f"Source KMZ file not found: {source_kmz_path}")
            return False

        # Find the target mission folder on controller
        target_folder = None
        items = waypoint_folder.Items()
        for item in items:
            if item.Name == target_controller_uuid and item.IsFolder:
                target_folder = item.GetFolder
                break

        if not target_folder:
            logger.error(
                f"Target mission folder not found on controller: {target_controller_uuid}"
            )
            return False

        # Delete all files in the target folder
        logger.info(f"Deleting files in controller folder: {target_controller_uuid}")
        try:
            folder_items = target_folder.Items()
            # Convert to list to avoid modifying collection during iteration
            items_to_delete = [item for item in folder_items]
            for item in items_to_delete:
                try:
                    # Invoke delete verb directly on the item
                    item.InvokeVerb("delete")
                    logger.debug(f"Deleted {item.Name}")
                except Exception as e:
                    logger.warning(f"Failed to delete item {item.Name}: {e}")
                    # Continue even if some files fail to delete
        except Exception as e:
            logger.error(f"Failed to delete folder contents: {e}")
            return False

        # Copy the KMZ file with renamed filename
        logger.info(
            f"Copying {source_kmz_path.name} to controller as {target_controller_uuid}.kmz"
        )

        # Create a temporary copy with the target UUID name
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            renamed_kmz = temp_path / f"{target_controller_uuid}.kmz"
            shutil.copy2(source_kmz_path, renamed_kmz)
            logger.debug(f"Created temp renamed file: {renamed_kmz}")

            # Verify the file exists
            if not renamed_kmz.exists():
                logger.error(f"Renamed KMZ file not created: {renamed_kmz}")
                return False

            # Copy renamed file to device using Shell
            shell = win32com.client.Dispatch("Shell.Application")
            temp_namespace = shell.NameSpace(str(temp_path))

            if not temp_namespace:
                logger.error(f"Failed to get namespace for temp folder: {temp_path}")
                return False

            # Find the renamed KMZ file in temp folder
            kmz_item = None
            temp_items = temp_namespace.Items()
            logger.debug(f"Temp folder has {temp_items.Count} items")

            for item in temp_items:
                logger.debug(f"Found temp item: {item.Name}")
                if item.Name == f"{target_controller_uuid}.kmz":
                    kmz_item = item
                    break

            if not kmz_item:
                logger.error(
                    f"Failed to find renamed KMZ file in temp folder. Looking for: {target_controller_uuid}.kmz"
                )
                return False

            # Copy to controller folder (16 = no UI, 4 = no confirmation)
            logger.debug(f"Copying {kmz_item.Name} to controller folder")
            target_folder.CopyHere(kmz_item, 20)  # 16 + 4 = 20

            # Give Windows time to complete the copy operation
            import time

            time.sleep(1)

        logger.info(
            f"Successfully replaced mission {target_controller_uuid} on controller"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to replace mission on device: {e}")
        return False
