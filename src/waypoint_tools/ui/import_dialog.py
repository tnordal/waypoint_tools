"""Import dialog for importing missions from RC 2 controller."""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressDialog,
    QVBoxLayout,
)

from waypoint_tools.models.database import Database
from waypoint_tools.services.file_manager import import_missions_from_folder
from waypoint_tools.services.mtp_device import MTPDevice, copy_from_device
from waypoint_tools.utils.constants import DATA_DIR

logger = logging.getLogger(__name__)


class ImportFromControllerDialog(QDialog):
    """Dialog for importing missions from RC 2 controller."""
    
    def __init__(self, device: MTPDevice, parent=None) -> None:
        """
        Initialize the import dialog.
        
        Args:
            device: MTP device (RC 2 controller)
            parent: Parent widget
        """
        super().__init__(parent)
        self.device = device
        self.db = Database.get_instance()
        self.setWindowTitle("Import from RC 2")
        self.setModal(True)
        self.resize(500, 400)
        self._setup_ui()
        self._load_missions()
    
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"Select missions to import from {self.device.name}:")
        layout.addWidget(header)
        
        # Mission list with checkboxes
        self.mission_list = QListWidget()
        layout.addWidget(self.mission_list)
        
        # Select all checkbox
        self.select_all_cb = QCheckBox("Select All")
        self.select_all_cb.stateChanged.connect(self._on_select_all)
        layout.addWidget(self.select_all_cb)
        
        # Info label
        self.info_label = QLabel()
        self.info_label.setProperty("class", "secondary")
        layout.addWidget(self.info_label)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._do_import)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_missions(self) -> None:
        """Load missions from the device."""
        try:
            missions = self.device.list_missions()
            
            if not missions:
                self.info_label.setText("No missions found on controller.")
                return
            
            for mission_uuid in missions:
                # Check if already in database
                existing = self.db.get_mission(mission_uuid)
                
                item = QListWidgetItem()
                if existing:
                    display_name = existing.display_name
                    item.setText(f"{display_name} (already imported)")
                else:
                    item.setText(f"{mission_uuid[:16]}... (new)")
                
                item.setData(Qt.ItemDataRole.UserRole, mission_uuid)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.mission_list.addItem(item)
            
            self.info_label.setText(f"Found {len(missions)} mission(s) on controller.")
            
        except Exception as e:
            logger.error(f"Failed to load missions from device: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load missions from controller:\n{e}",
            )
    
    def _on_select_all(self, state: int) -> None:
        """Handle select all checkbox."""
        check_state = (
            Qt.CheckState.Checked if state == Qt.CheckState.Checked.value
            else Qt.CheckState.Unchecked
        )
        for i in range(self.mission_list.count()):
            item = self.mission_list.item(i)
            if item:
                item.setCheckState(check_state)
    
    def _do_import(self) -> None:
        """Import selected missions from controller."""
        # Get selected missions
        selected = []
        for i in range(self.mission_list.count()):
            item = self.mission_list.item(i)
            if item and item.checkState() == Qt.CheckState.Checked:
                mission_uuid = item.data(Qt.ItemDataRole.UserRole)
                selected.append(mission_uuid)
        
        if not selected:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select at least one mission to import.",
            )
            return
        
        # Create missions folder for permanent storage
        missions_folder = DATA_DIR / "missions"
        missions_folder.mkdir(parents=True, exist_ok=True)
        
        # Progress dialog
        progress = QProgressDialog(
            "Importing missions...",
            "Cancel",
            0,
            len(selected),
            self,
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        
        imported_count = 0
        failed = []
        
        try:
            for i, mission_uuid in enumerate(selected):
                if progress.wasCanceled():
                    break
                
                progress.setValue(i)
                progress.setLabelText(f"Importing {mission_uuid[:16]}...")
                
                # Copy from device to missions folder
                if copy_from_device(self.device, mission_uuid, missions_folder):
                    imported_count += 1
                else:
                    failed.append(mission_uuid)
            
            progress.setValue(len(selected))
            
            # Import from missions folder to database
            if imported_count > 0:
                new_count, updated_count = import_missions_from_folder(missions_folder)
                
                message = (
                    f"Successfully imported {imported_count} mission(s) from controller.\n"
                    f"New: {new_count}, Updated: {updated_count}"
                )
                
                if failed:
                    message += f"\n\nFailed to import {len(failed)} mission(s)."
                
                QMessageBox.information(self, "Import Complete", message)
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Import Failed",
                    "No missions were imported successfully.",
                )
        
        except Exception as e:
            logger.error(f"Import failed: {e}")
            QMessageBox.critical(
                self,
                "Import Error",
                f"An error occurred during import:\n{e}",
            )
