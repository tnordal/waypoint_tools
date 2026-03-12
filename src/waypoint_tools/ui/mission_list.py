"""Mission list widget - displays list of waypoint missions."""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from waypoint_tools.models.database import Database
from waypoint_tools.models.mission import Mission

logger = logging.getLogger(__name__)


class MissionListWidget(QWidget):
    """Widget for displaying and managing the mission list."""

    # Signals
    mission_selected = pyqtSignal(str)  # Emits mission UUID

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the mission list widget."""
        super().__init__(parent)
        self.db = Database.get_instance()
        self.current_missions: list[Mission] = []
        self._setup_ui()
        self._connect_signals()
        self.refresh()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Search bar
        search_layout = QHBoxLayout()

        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search missions...")
        search_layout.addWidget(self.search_box)

        layout.addLayout(search_layout)

        # Tag filter
        filter_layout = QHBoxLayout()

        filter_label = QLabel("Tags:")
        filter_layout.addWidget(filter_label)

        self.tag_filter = QComboBox()
        self.tag_filter.addItem("All")
        self.tag_filter.setMinimumWidth(150)
        self.tag_filter.setMaxVisibleItems(10)
        filter_layout.addWidget(self.tag_filter)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Mission list
        self.mission_list = QListWidget()
        self.mission_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.mission_list)

    def _connect_signals(self) -> None:
        """Connect internal signals to slots."""
        self.search_box.textChanged.connect(self._on_search_changed)
        self.tag_filter.currentTextChanged.connect(self._on_tag_filter_changed)
        self.mission_list.currentItemChanged.connect(self._on_selection_changed)

    def refresh(self) -> None:
        """Refresh the mission list."""
        logger.debug("Refreshing mission list")

        # Update tag filter
        self._update_tag_filter()

        # Apply filters
        self._apply_filters()

    def _update_tag_filter(self) -> None:
        """Update the tag filter dropdown."""
        current_tag = self.tag_filter.currentText()

        self.tag_filter.clear()
        self.tag_filter.addItem("All")

        tags = self.db.get_all_tags()
        for tag in tags:
            self.tag_filter.addItem(tag)

        # Restore selection
        index = self.tag_filter.findText(current_tag)
        if index >= 0:
            self.tag_filter.setCurrentIndex(index)

    def _apply_filters(self) -> None:
        """Apply search and tag filters to the mission list."""
        search_query = self.search_box.text().strip()
        selected_tag = self.tag_filter.currentText()

        # Get filtered missions
        if search_query or (selected_tag and selected_tag != "All"):
            tags = [selected_tag] if selected_tag and selected_tag != "All" else None
            query = search_query if search_query else None
            missions = self.db.search_missions(query=query, tags=tags)
        else:
            missions = self.db.get_all_missions()

        # Sort by date modified (newest first)
        missions.sort(
            key=lambda m: m.date_modified or m.date_created or 0,
            reverse=True,
        )

        self.current_missions = missions
        self._populate_list(missions)

    def _populate_list(self, missions: list[Mission]) -> None:
        """Populate the list widget with missions."""
        # Explicitly emit signal to clear preview panel
        self.mission_selected.emit("")

        # Clear selection and list
        self.mission_list.clearSelection()
        self.mission_list.setCurrentItem(None)
        self.mission_list.clear()

        for mission in missions:
            item = QListWidgetItem()

            # Format display text
            name = mission.display_name
            location = f" | {mission.location}" if mission.location else ""

            # Export indicator
            export_status = " | ✓ Exported" if mission.controller_uuid else ""

            waypoints = f" | {mission.waypoint_count} pts"

            # Format date
            date_str = ""
            if mission.date_modified:
                date_str = f" | {mission.date_modified.strftime('%Y-%m-%d')}"
            elif mission.date_created:
                date_str = f" | {mission.date_created.strftime('%Y-%m-%d')}"

            # Format tags
            tags_str = ""
            if mission.tags:
                tag_count = len(mission.tags)
                tags_str = f"\n  [{', '.join(mission.tags)}] ({tag_count} tag{'s' if tag_count > 1 else ''})"

            item_text = (
                f"{name}{location}{export_status}{waypoints}{date_str}{tags_str}"
            )
            item.setText(item_text)
            item.setData(Qt.ItemDataRole.UserRole, mission.uuid)

            self.mission_list.addItem(item)

        logger.info(f"Displayed {len(missions)} mission(s)")

    def _on_search_changed(self, text: str) -> None:
        """Handle search text change."""
        self._apply_filters()

    def _on_tag_filter_changed(self, tag: str) -> None:
        """Handle tag filter change."""
        self._apply_filters()

    def _on_selection_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        """Handle mission selection change."""
        if current:
            uuid = current.data(Qt.ItemDataRole.UserRole)
            logger.debug(f"Mission selected: {uuid}")
            self.mission_selected.emit(uuid)
        else:
            self.mission_selected.emit("")

    def get_selected_mission(self) -> Mission | None:
        """Get the currently selected mission."""
        current_item = self.mission_list.currentItem()
        if current_item:
            uuid = current_item.data(Qt.ItemDataRole.UserRole)
            return self.db.get_mission(uuid)
        return None
