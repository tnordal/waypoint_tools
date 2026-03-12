"""WPML waypoint file parser."""

import logging
import zipfile
from pathlib import Path

from lxml import etree

from waypoint_tools.models.mission import Mission, Waypoint
from waypoint_tools.utils.constants import DRONE_TYPES, FINISH_ACTIONS
from waypoint_tools.utils.geo import (
    calculate_center_point,
    calculate_path_distance,
)

logger = logging.getLogger(__name__)

# XML namespaces
NAMESPACES = {
    "kml": "http://www.opengis.net/kml/2.2",
    "wpml": "http://www.uav.com/wpmz/1.0.2",
}

# Alternative namespace used by waypointmap.com
NAMESPACES_DJI = {
    "kml": "http://www.opengis.net/kml/2.2",
    "wpml": "http://www.dji.com/wpmz/1.0.2",
}


def parse_kmz(kmz_path: Path, uuid: str) -> Mission | None:
    """
    Parse a KMZ waypoint file and extract mission data.
    
    Args:
        kmz_path: Path to the .kmz file
        uuid: Mission UUID
    
    Returns:
        Mission object with parsed data, or None if parsing fails
    """
    try:
        with zipfile.ZipFile(kmz_path, "r") as kmz:
            # Read waylines.wpml (try both locations)
            wpml_data = None
            try:
                wpml_data = kmz.read("wpmz/waylines.wpml")
            except KeyError:
                try:
                    wpml_data = kmz.read("waylines.wpml")
                except KeyError:
                    logger.error(f"waylines.wpml not found in {kmz_path}")
                    return None
            
            # Parse XML
            mission = parse_wpml(wpml_data, uuid)
            return mission
            
    except zipfile.BadZipFile:
        logger.error(f"Invalid KMZ file: {kmz_path}")
        return None
    except Exception as e:
        logger.error(f"Failed to parse KMZ {kmz_path}: {e}")
        return None


def parse_wpml(wpml_data: bytes | str, uuid: str) -> Mission | None:
    """
    Parse WPML XML data and extract mission information.
    
    Args:
        wpml_data: WPML XML content as bytes or string
        uuid: Mission UUID
    
    Returns:
        Mission object with parsed data, or None if parsing fails
    """
    try:
        # Parse XML
        if isinstance(wpml_data, str):
            root = etree.fromstring(wpml_data.encode("utf-8"))
        else:
            root = etree.fromstring(wpml_data)
        
        # Detect which namespace is used
        namespaces = NAMESPACES
        if root.nsmap.get("wpml") == "http://www.dji.com/wpmz/1.0.2":
            namespaces = NAMESPACES_DJI
            logger.debug(f"Using DJI namespace for {uuid}")
        else:
            logger.debug(f"Using UAV namespace for {uuid}")
        
        # Extract mission configuration
        mission_config = root.find(".//wpml:missionConfig", namespaces=namespaces)
        if mission_config is None:
            logger.warning(f"No mission config found in WPML for {uuid}")
            mission_config = etree.Element("missionConfig")
        
        finish_action = _get_text(
            mission_config, ".//wpml:finishAction", namespaces, "goHome"
        )
        drone_enum = _get_text(
            mission_config,
            ".//wpml:droneInfo/wpml:droneEnumValue",
            namespaces,
            "68",
        )
        
        # Get friendly finish action and drone type
        finish_action_display = FINISH_ACTIONS.get(finish_action, finish_action)
        drone_type_display = DRONE_TYPES.get(drone_enum, f"Unknown ({drone_enum})")
        
        # Extract flight speed (Folder is in kml namespace)
        folder = root.find(".//kml:Folder", namespaces=namespaces)
        if folder is None:
            # Try without namespace
            folder = root.find(".//Folder")
        if folder is None:
            logger.error(f"No waypoint folder found in WPML for {uuid}")
            return None
        
        flight_speed = float(
            _get_text(folder, ".//wpml:autoFlightSpeed", namespaces, "2.5")
        )
        
        # Parse waypoints (Placemark is also in kml namespace)
        waypoints = []
        placemarks = folder.findall(".//kml:Placemark", namespaces=namespaces)
        if not placemarks:
            # Try without namespace
            placemarks = folder.findall(".//Placemark")
        
        for placemark in placemarks:
            waypoint = _parse_waypoint(placemark, namespaces)
            if waypoint:
                waypoints.append(waypoint)
        
        # Sort by index
        waypoints.sort(key=lambda w: w.index)
        
        # Calculate statistics
        coordinates = [(w.latitude, w.longitude) for w in waypoints]
        altitudes = [w.altitude for w in waypoints]
        
        total_distance = calculate_path_distance(coordinates)
        center_lat, center_lon = calculate_center_point(coordinates)
        altitude_min = min(altitudes) if altitudes else 0.0
        altitude_max = max(altitudes) if altitudes else 0.0
        
        # Create mission
        mission = Mission(
            uuid=uuid,
            waypoint_count=len(waypoints),
            total_distance_m=total_distance,
            altitude_min=altitude_min,
            altitude_max=altitude_max,
            center_lat=center_lat,
            center_lon=center_lon,
            flight_speed=flight_speed,
            finish_action=finish_action_display,
            drone_type=drone_type_display,
            waypoints=waypoints,
        )
        
        logger.info(f"Parsed mission {uuid}: {len(waypoints)} waypoints")
        return mission
        
    except etree.XMLSyntaxError as e:
        logger.error(f"XML syntax error in WPML for {uuid}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to parse WPML for {uuid}: {e}")
        return None


def _parse_waypoint(placemark: etree.Element, namespaces: dict) -> Waypoint | None:
    """Parse a single waypoint from a Placemark element."""
    try:
        # Get index
        index_str = _get_text(placemark, ".//wpml:index", namespaces)
        if not index_str:
            return None
        index = int(index_str)
        
        # Get coordinates (format: "longitude,latitude") - Point is in kml namespace
        coords_str = _get_text(placemark, ".//kml:Point/kml:coordinates", namespaces)
        if not coords_str:
            # Try without namespace
            coords_str = _get_text(placemark, ".//Point/coordinates", namespaces)
        if not coords_str:
            logger.warning(f"No coordinates for waypoint {index}")
            return None
        
        coords_parts = coords_str.strip().split(",")
        if len(coords_parts) < 2:
            logger.warning(f"Invalid coordinates for waypoint {index}: {coords_str}")
            return None
        
        longitude = float(coords_parts[0])
        latitude = float(coords_parts[1])
        
        # Get altitude (executeHeight)
        altitude = float(
            _get_text(placemark, ".//wpml:executeHeight", namespaces, "0")
        )
        
        # Get speed
        speed = float(
            _get_text(placemark, ".//wpml:waypointSpeed", namespaces, "2.5")
        )
        
        # Get heading (optional)
        heading_str = _get_text(
            placemark,
            ".//wpml:waypointHeadingParam/wpml:waypointHeadingAngle",
            namespaces,
        )
        heading = float(heading_str) if heading_str else None
        
        # Get gimbal pitch (optional, from first action if available)
        gimbal_pitch_str = _get_text(
            placemark,
            ".//wpml:actionActuatorFuncParam/wpml:gimbalPitchRotateAngle",
            namespaces,
        )
        gimbal_pitch = float(gimbal_pitch_str) if gimbal_pitch_str else None
        
        # Get action types
        actions = []
        action_funcs = placemark.findall(
            ".//wpml:actionActuatorFunc", namespaces=namespaces
        )
        for func in action_funcs:
            if func.text:
                actions.append(func.text)
        
        return Waypoint(
            index=index,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            speed=speed,
            heading=heading,
            gimbal_pitch=gimbal_pitch,
            actions=actions,
        )
        
    except (ValueError, AttributeError) as e:
        logger.warning(f"Failed to parse waypoint: {e}")
        return None


def _get_text(
    element: etree.Element,
    xpath: str,
    namespaces: dict[str, str],
    default: str = "",
) -> str:
    """
    Safely extract text from an XML element using XPath.
    
    Args:
        element: Parent element
        xpath: XPath expression
        namespaces: XML namespaces
        default: Default value if element not found
    
    Returns:
        Text content or default value
    """
    found = element.find(xpath, namespaces=namespaces)
    if found is not None and found.text:
        return found.text.strip()
    return default
