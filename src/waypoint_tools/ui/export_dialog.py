"""Export dialog for exporting missions to RC 2 controller."""

import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from waypoint_tools.models.database import Database
from waypoint_tools.models.mission import Mission
from waypoint_tools.services.mtp_device import MTPDevice, replace_mission_on_device

logger = logging.getLogger(__name__)


class ExportToControllerDialog(QDialog):
    """Two-step wizard dialog for exporting missions to RC 2 controller."""

    def __init__(self, device: MTPDevice, parent=None) -> None:
        """
        Initialize the export dialog.

        Args:
            device: MTP device (RC 2 controller)
            parent: Parent widget
        """
        super().__init__(parent)
        self.device = device
        self.db = Database.get_instance()
        self.selected_local_mission: Mission | None = None
        self.selected_controller_uuid: str | None = None
        self.controller_missions: list[str] = []

        self.setWindowTitle("Export to RC 2")
        self.setModal(True)
        self.resize(600, 500)
        self._setup_ui()
        self._load_step1()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)

        # Stacked widget for two steps
        self.stacked = QStackedWidget()
        layout.addWidget(self.stacked)

        # Step 1: Select local mission
        self.step1_widget = self._create_step1()
        self.stacked.addWidget(self.step1_widget)

        # Step 2: Select controller mission
        self.step2_widget = self._create_step2()
        self.stacked.addWidget(self.step2_widget)

        # Button box (changes based on step)
        self.button_box = QDialogButtonBox()
        layout.addWidget(self.button_box)

        self._update_buttons_for_step(1)

    def _create_step1(self) -> QWidget:
        """Create step 1 UI: select local mission."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        self.step1_header = QLabel("Export to RC 2 - Step 1 of 2")
        self.step1_header.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(self.step1_header)

        # Instructions
        instructions = QLabel("Select a mission to export:")
        layout.addWidget(instructions)

        # Mission list
        self.local_mission_list = QListWidget()
        self.local_mission_list.setSelectionMode(
            QListWidget.SelectionMode.SingleSelection
        )
        self.local_mission_list.itemDoubleClicked.connect(self._on_step1_next)
        layout.addWidget(self.local_mission_list)

        # Info label
        self.step1_info = QLabel()
        self.step1_info.setProperty("class", "secondary")
        layout.addWidget(self.step1_info)

        return widget

    def _create_step2(self) -> QWidget:
        """Create step 2 UI: select controller mission to replace."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        self.step2_header = QLabel("Export to RC 2 - Step 2 of 2")
        self.step2_header.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(self.step2_header)

        # Instructions
        instructions = QLabel("Select which controller mission to replace:")
        layout.addWidget(instructions)

        # Controller mission list
        self.controller_mission_list = QListWidget()
        self.controller_mission_list.setSelectionMode(
            QListWidget.SelectionMode.SingleSelection
        )
        self.controller_mission_list.itemDoubleClicked.connect(self._on_export)
        layout.addWidget(self.controller_mission_list)

        # Info label
        self.step2_info = QLabel()
        self.step2_info.setProperty("class", "secondary")
        layout.addWidget(self.step2_info)

        return widget

    def _update_buttons_for_step(self, step: int) -> None:
        """Update button box based on current step."""
        self.button_box.clear()

        if step == 1:
            # Step 1: Next and Cancel
            self.next_btn = QPushButton("Next >")
            self.next_btn.clicked.connect(self._on_step1_next)
            self.button_box.addButton(
                self.next_btn, QDialogButtonBox.ButtonRole.AcceptRole
            )

            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.reject)
            self.button_box.addButton(cancel_btn, QDialogButtonBox.ButtonRole.RejectRole)

        elif step == 2:
            # Step 2: Back, Export, Cancel
            back_btn = QPushButton("< Back")
            back_btn.clicked.connect(self._on_step2_back)
            self.button_box.addButton(back_btn, QDialogButtonBox.ButtonRole.ActionRole)

            self.export_btn = QPushButton("Export")
            self.export_btn.clicked.connect(self._on_export)
            self.button_box.addButton(
                self.export_btn, QDialogButtonBox.ButtonRole.AcceptRole
            )

            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.reject)
            self.button_box.addButton(cancel_btn, QDialogButtonBox.ButtonRole.RejectRole)

    def _load_step1(self) -> None:
        """Load local missions for step 1."""
        try:
            missions = self.db.get_all_missions()

            if not missions:
                self.step1_info.setText("No missions in database to export.")
                return

            # Sort by date modified
            missions.sort(
                key=lambda m: m.date_modified or m.date_created or 0, reverse=True
            )

            for mission in missions:
                item = QListWidgetItem()

                # Format display text
                display = mission.display_name
                if mission.location:
                    display += f" | {mission.location}"
                display += f" | {mission.waypoint_count} pts"

                if mission.controller_uuid:
                    display += " | ✓ Exported"

                item.setText(display)
                item.setData(Qt.ItemDataRole.UserRole, mission.uuid)
                self.local_mission_list.addItem(item)

            self.step1_info.setText(f"{len(missions)} mission(s) available to export.")

        except Exception as e:
            logger.error(f"Failed to load local missions: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load missions:\n{e}",
            )

    def _on_step1_next(self) -> None:
        """Handle Next button on step 1."""
        current_item = self.local_mission_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a mission to export.",
            )
            return

        mission_uuid = current_item.data(Qt.ItemDataRole.UserRole)
        self.selected_local_mission = self.db.get_mission(mission_uuid)

        if not self.selected_local_mission:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to load selected mission.",
            )
            return

        # Check if mission has file_path
        if not self.selected_local_mission.file_path:
            QMessageBox.critical(
                self,
                "Error",
                "Selected mission has no file path. Cannot export.",
            )
            return

        # Load step 2
        self._load_step2()

    def _load_step2(self) -> None:
        """Load controller missions for step 2."""
        try:
            # Get controller missions
            self.controller_missions = self.device.list_missions()

            if not self.controller_missions:
                QMessageBox.critical(
                    self,
                    "No Controller Missions",
                    "No waypoint missions found on the controller.\n\n"
                    "Please create at least one mission on the controller first, "
                    "then you can replace it.",
                )
                return

            self.controller_mission_list.clear()

            for controller_uuid in self.controller_missions:
                item = QListWidgetItem()

                # Check if this controller UUID was previously replaced
                previous_mission = self.db.get_mission_by_controller_uuid(
                    controller_uuid
                )

                display = f"{controller_uuid[:16]}..."
                if previous_mission:
                    display += f" (Previously: {previous_mission.display_name})"

                item.setText(display)
                item.setData(Qt.ItemDataRole.UserRole, controller_uuid)
                self.controller_mission_list.addItem(item)

            self.step2_info.setText(
                f"{len(self.controller_missions)} controller mission(s) available."
            )

            # Switch to step 2
            self.stacked.setCurrentIndex(1)
            self._update_buttons_for_step(2)

        except Exception as e:
            logger.error(f"Failed to load controller missions: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load controller missions:\n{e}",
            )

    def _on_step2_back(self) -> None:
        """Handle Back button on step 2."""
        self.stacked.setCurrentIndex(0)
        self._update_buttons_for_step(1)

    def _on_export(self) -> None:
        """Handle Export button."""
        current_item = self.controller_mission_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a controller mission to replace.",
            )
            return

        self.selected_controller_uuid = current_item.data(Qt.ItemDataRole.UserRole)

        if not self.selected_local_mission or not self.selected_controller_uuid:
            QMessageBox.critical(
                self,
                "Error",
                "Invalid selection. Please try again.",
            )
            return

        # Show confirmation dialog
        local_name = self.selected_local_mission.display_name
        waypoint_count = self.selected_local_mission.waypoint_count
        distance = self.selected_local_mission.total_distance_m
        target_uuid = self.selected_controller_uuid

        response = QMessageBox.question(
            self,
            "Confirm Export",
            f"Replace controller mission?\n\n"
            f"Local mission: {local_name}\n"
            f"  - {waypoint_count} waypoints\n"
            f"  - {distance:.1f}m total distance\n\n"
            f"Will replace controller mission: {target_uuid[:16]}...\n\n"
            f"This will delete all files in the controller mission folder\n"
            f"and copy your KMZ file (renamed to match the controller UUID).\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if response != QMessageBox.StandardButton.Yes:
            return

        self._do_export()

    def _do_export(self) -> None:
        """Perform the actual export operation."""
        if not self.selected_local_mission or not self.selected_controller_uuid:
            return

        try:
            # Get source KMZ path
            if not self.selected_local_mission.file_path:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Mission has no file path. Cannot export.",
                )
                return
                
            mission_folder = Path(self.selected_local_mission.file_path)
            source_kmz = mission_folder / f"{self.selected_local_mission.uuid}.kmz"

            if not source_kmz.exists():
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Source KMZ file not found:\n{source_kmz}",
                )
                return

            # Perform the export
            logger.info(
                f"Exporting {self.selected_local_mission.uuid} to controller "
                f"slot {self.selected_controller_uuid}"
            )

            success = replace_mission_on_device(
                self.device, source_kmz, self.selected_controller_uuid
            )

            if success:
                # Update database with controller UUID
                self.selected_local_mission.controller_uuid = (
                    self.selected_controller_uuid
                )
                self.db.add_mission(self.selected_local_mission)

                QMessageBox.information(
                    self,
                    "Export Successful",
                    f'Mission "{self.selected_local_mission.display_name}" '
                    f"has been exported to the controller.",
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    "Failed to export mission to controller.\n"
                    "Check the log for details.",
                )

        except Exception as e:
            logger.error(f"Export failed: {e}")
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred during export:\n{e}",
            )
