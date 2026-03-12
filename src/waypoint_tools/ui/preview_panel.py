"""Preview panel for displaying mission details."""

import logging
from pathlib import Path

from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from waypoint_tools.models.database import Database
from waypoint_tools.models.mission import Mission
from waypoint_tools.services.wpml_parser import parse_kmz
from waypoint_tools.ui.edit_dialog import EditMissionDialog
from waypoint_tools.ui.thumbnail_viewer import ThumbnailViewer
from waypoint_tools.utils.geo import format_coordinates

logger = logging.getLogger(__name__)


class PreviewPanel(QWidget):
    """Widget for displaying mission preview and details."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the preview panel."""
        super().__init__(parent)
        self.db = Database.get_instance()
        self.current_mission: Mission | None = None
        self.scroll_area: QScrollArea | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        # Make the panel scrollable
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll_area.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll_area)

        # Empty state
        self.empty_label = QLabel("Select a mission to view details")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setProperty("class", "secondary")
        self.content_layout.addWidget(self.empty_label)
        self.content_layout.addStretch()

    def set_mission(self, mission_uuid: str | None) -> None:
        """
        Set the mission to preview.

        Args:
            mission_uuid: UUID of mission to display, or None to clear
        """
        if not mission_uuid:
            self._clear_preview()
            return

        mission = self.db.get_mission(mission_uuid)
        if not mission:
            logger.warning(f"Mission not found: {mission_uuid}")
            self._clear_preview()
            return

        # Load waypoints and thumbnails from file system if file_path is available
        if mission.file_path:
            self._load_mission_details(mission)

        self.current_mission = mission
        self._display_mission(mission)

    def _load_mission_details(self, mission: Mission) -> None:
        """
        Load waypoints and thumbnails from file system.

        Args:
            mission: Mission object to populate with details
        """
        if not mission.file_path:
            return

        try:
            mission_folder = Path(mission.file_path)
            if not mission_folder.exists():
                logger.warning(f"Mission folder not found: {mission_folder}")
                return

            # Load waypoints from KMZ file
            kmz_file = mission_folder / f"{mission.uuid}.kmz"
            if kmz_file.exists():
                parsed_mission = parse_kmz(kmz_file, mission.uuid)
                if parsed_mission:
                    mission.waypoints = parsed_mission.waypoints

            # Load thumbnails
            image_folder = mission_folder / "image"
            if image_folder.exists():
                thumbnails = sorted(image_folder.glob("WP_*.jpg"))
                mission.thumbnail_paths = [str(t) for t in thumbnails]

        except Exception as e:
            logger.error(f"Failed to load mission details: {e}")

    def _clear_preview(self) -> None:
        """Clear the preview panel."""
        self.current_mission = None

        # Create a completely new content widget to ensure clean state
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(10, 10, 10, 10)

        # Add empty state
        self.empty_label = QLabel("Select a mission to view details")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setProperty("class", "secondary")
        self.content_layout.addWidget(self.empty_label)
        self.content_layout.addStretch()

        # Replace the scroll area's widget
        if self.scroll_area:
            old_widget = self.scroll_area.takeWidget()
            if old_widget:
                old_widget.deleteLater()
            self.scroll_area.setWidget(content)

    def _display_mission(self, mission: Mission) -> None:
        """Display mission details."""
        # Clear existing content
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
            elif item.spacerItem():
                # Remove spacer items as well
                pass
        
        # Process pending delete events to ensure widgets are actually removed
        QCoreApplication.processEvents()

        # Header with Edit button
        header_layout = QHBoxLayout()

        header = QLabel(mission.display_name)
        header.setStyleSheet("font-size: 16pt; font-weight: bold;")
        header_layout.addWidget(header)

        header_layout.addStretch()

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self._edit_mission(mission))
        header_layout.addWidget(edit_btn)

        self.content_layout.addLayout(header_layout)

        if mission.location:
            location = QLabel(mission.location)
            location.setProperty("class", "secondary")
            self.content_layout.addWidget(location)

        # UUID
        uuid_label = QLabel(f"UUID: {mission.uuid[:16]}...")
        uuid_label.setProperty("class", "secondary")
        self.content_layout.addWidget(uuid_label)

        # Tags
        if mission.tags:
            tags_label = QLabel(f"Tags: {', '.join(mission.tags)}")
            self.content_layout.addWidget(tags_label)

        # Notes
        if mission.notes:
            notes_group = QGroupBox("Notes")
            notes_layout = QVBoxLayout()
            notes_text = QLabel(mission.notes)
            notes_text.setWordWrap(True)
            notes_layout.addWidget(notes_text)
            notes_group.setLayout(notes_layout)
            self.content_layout.addWidget(notes_group)

        # Mission summary
        summary_group = QGroupBox("Mission Summary")
        summary_layout = QFormLayout()

        summary_layout.addRow("Waypoints:", QLabel(str(mission.waypoint_count)))
        summary_layout.addRow(
            "Distance:",
            QLabel(f"{mission.total_distance_m:.1f} m"),
        )

        if mission.estimated_flight_time > 0:
            minutes = int(mission.estimated_flight_time // 60)
            seconds = int(mission.estimated_flight_time % 60)
            summary_layout.addRow(
                "Est. Time:",
                QLabel(f"~{minutes}m {seconds}s"),
            )

        if mission.altitude_min or mission.altitude_max:
            summary_layout.addRow(
                "Altitude:",
                QLabel(f"{mission.altitude_min:.1f} - {mission.altitude_max:.1f} m"),
            )

        if mission.flight_speed:
            summary_layout.addRow("Speed:", QLabel(f"{mission.flight_speed} m/s"))

        if mission.finish_action:
            summary_layout.addRow("Finish:", QLabel(mission.finish_action))

        if mission.drone_type:
            summary_layout.addRow("Drone:", QLabel(mission.drone_type))

        if mission.center_lat and mission.center_lon:
            coords = format_coordinates(mission.center_lat, mission.center_lon)
            summary_layout.addRow("Center:", QLabel(coords))

        summary_group.setLayout(summary_layout)
        self.content_layout.addWidget(summary_group)

        # Waypoints table
        if mission.waypoints:
            waypoints_group = QGroupBox("Waypoints")
            waypoints_layout = QVBoxLayout()

            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(
                [
                    "#",
                    "Latitude",
                    "Longitude",
                    "Altitude (m)",
                    "Speed (m/s)",
                ]
            )
            table.setRowCount(len(mission.waypoints))

            for i, wp in enumerate(mission.waypoints):
                table.setItem(i, 0, QTableWidgetItem(str(wp.index)))
                table.setItem(i, 1, QTableWidgetItem(f"{wp.latitude:.6f}"))
                table.setItem(i, 2, QTableWidgetItem(f"{wp.longitude:.6f}"))
                table.setItem(i, 3, QTableWidgetItem(f"{wp.altitude:.1f}"))
                table.setItem(i, 4, QTableWidgetItem(f"{wp.speed:.1f}"))

            table.resizeColumnsToContents()
            table.setMaximumHeight(300)
            waypoints_layout.addWidget(table)

            waypoints_group.setLayout(waypoints_layout)
            self.content_layout.addWidget(waypoints_group)

        # Thumbnails
        if mission.thumbnail_paths:
            thumbnails_group = QGroupBox("Thumbnails")
            thumbnails_layout = QVBoxLayout()

            # Horizontal scroll area for thumbnail strip
            scroll = QScrollArea()
            scroll.setMaximumHeight(150)
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            strip_widget = QWidget()
            strip_layout = QHBoxLayout(strip_widget)

            # Show first 5 thumbnails
            for thumb_path in mission.thumbnail_paths[:5]:
                thumb_label = QLabel()

                path = Path(thumb_path)
                if path.exists():
                    pixmap = QPixmap(str(path))
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(
                            100,
                            100,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                        thumb_label.setPixmap(pixmap)
                    else:
                        thumb_label.setText("Invalid")
                else:
                    thumb_label.setText("Not found")

                thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                thumb_label.setStyleSheet("border: 1px solid #ccc; padding: 2px;")
                strip_layout.addWidget(thumb_label)

            strip_layout.addStretch()
            scroll.setWidget(strip_widget)
            thumbnails_layout.addWidget(scroll)

            # View all button
            view_all_btn = QPushButton(
                f"View All ({len(mission.thumbnail_paths)} thumbnails)"
            )
            view_all_btn.clicked.connect(
                lambda: self._open_thumbnail_viewer(mission.thumbnail_paths)
            )
            thumbnails_layout.addWidget(view_all_btn)

            thumbnails_group.setLayout(thumbnails_layout)
            self.content_layout.addWidget(thumbnails_group)

        self.content_layout.addStretch()

    def _edit_mission(self, mission: Mission) -> None:
        """Open the edit mission dialog."""
        dialog = EditMissionDialog(mission, self)
        if dialog.exec():
            # Dialog accepted - refresh the preview with updated data
            self.set_mission(mission.uuid)

    def _open_thumbnail_viewer(self, thumbnails: list[str]) -> None:
        """Open the thumbnail grid viewer dialog."""
        viewer = ThumbnailViewer(thumbnails, self)
        viewer.exec()
