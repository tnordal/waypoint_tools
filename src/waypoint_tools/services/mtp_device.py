"""MTP device detection and file access for RC 2 controller."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Expected path on RC 2 controller
RC2_WAYPOINT_PATH = "Internal shared storage/Android/data/dji.go.v5/files/FlightRoute"


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
                for item in current_folder:
                    if item.Name == part and item.IsFolder:
                        current_folder = item.GetFolder
                        found = True
                        break
                
                if not found:
                    logger.warning(f"Path component not found: {part}")
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
            for item in self._waypoint_folder:
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
        import win32com.client
        
        shell = win32com.client.Dispatch("Shell.Application")
        
        # Get "This PC" namespace (17 = Computer)
        computer = shell.NameSpace(17)
        
        if not computer:
            logger.warning("Could not access Computer namespace")
            return None
        
        # Iterate through devices
        for item in computer.Items():
            device_name = item.Name
            
            # Look for RC 2 controller (may show as "RC 2" or similar)
            if "RC" in device_name or "DJI" in device_name:
                logger.info(f"Found potential RC 2 device: {device_name}")
                
                # Get the folder for this device
                device_folder = item.GetFolder
                if device_folder:
                    device = MTPDevice(device_name, device_folder)
                    
                    # Verify it has the waypoint folder structure
                    if device.find_waypoint_folder():
                        logger.info(f"RC 2 controller detected: {device_name}")
                        return device
        
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
        for item in waypoint_folder:
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
        import win32com.client
        shell = win32com.client.Dispatch("Shell.Application")
        dest_shell = shell.NameSpace(str(dest_mission))
        
        # Copy all items from mission folder
        for item in mission_folder:
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
        import win32com.client
        shell = win32com.client.Dispatch("Shell.Application")
        source_shell = shell.NameSpace(str(source_mission))
        
        # Copy to device
        waypoint_folder.CopyHere(source_shell, 16)  # 16 = no UI
        
        logger.info(f"Copied mission {mission_uuid} to device")
        return True
        
    except Exception as e:
        logger.error(f"Failed to copy mission to device: {e}")
        return False
