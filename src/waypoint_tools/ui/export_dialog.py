"""Export dialog for exporting missions to RC 2 controller."""

import logging
from pathlib import Path

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
from waypoint_tools.services.mtp_device import MTPDevice, copy_to_device
from waypoint_tools.utils.constants import DATA_DIR

logger = logging.getLogger(__name__)


class ExportToControllerDialog(QDialog):
    """Dialog for exporting missions to RC 2 controller."""
    
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
        self.setWindowTitle("Export to RC 2")
        self.setModal(True)
        self.resize(500, 400)
        self._setup_ui()
        self._load_missions()
    
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"Select missions to export to {self.device.name}:")
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
        button_box.accepted.connect(self._do_export)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_missions(self) -> None:
        """Load missions from the database."""
        try:
            missions = self.db.get_all_missions()
            
            if not missions:
                self.info_label.setText("No missions in database to export.")
                return
            
            # Get controller missions for comparison
            controller_missions = set(self.device.list_missions())
            
            for mission in missions:
                item = QListWidgetItem()
                
                display_name = mission.display_name
                if mission.uuid in controller_missions:
                    item.setText(f"{display_name} (already on controller)")
                else:
                    item.setText(f"{display_name}")
                
                item.setData(Qt.ItemDataRole.UserRole, mission.uuid)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.mission_list.addItem(item)
            
            self.info_label.setText(f"{len(missions)} mission(s) available to export.")
            
        except Exception as e:
            logger.error(f"Failed to load missions: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load missions:\n{e}",
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
    
    def _do_export(self) -> None:
        """Export selected missions to controller."""
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
                "Please select at least one mission to export.",
            )
            return
        
        # Confirm export
        response = QMessageBox.question(
            self,
            "Confirm Export",
            f"Export {len(selected)} mission(s) to RC 2 controller?\n\n"
            "Note: Existing missions on the controller will be overwritten.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        
        if response != QMessageBox.StandardButton.Yes:
            return
        
        # Progress dialog
        progress = QProgressDialog(
            "Exporting missions...",
            "Cancel",
            0,
            len(selected),
            self,
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        
        exported_count = 0
        failed = []
        
        try:
            for i, mission_uuid in enumerate(selected):
                if progress.wasCanceled():
                    break
                
                mission = self.db.get_mission(mission_uuid)
                if not mission:
                    failed.append(mission_uuid)
                    continue
                
                # Check if mission has a file_path
                if not mission.file_path:
                    logger.warning(f"Mission {mission_uuid} has no file_path stored")
                    failed.append(mission_uuid)
                    continue
                
                progress.setValue(i)
                progress.setLabelText(f"Exporting {mission.display_name}...")
                
                # Get the parent folder from the file_path
                mission_folder = Path(mission.file_path)
                source_folder = mission_folder.parent
                
                # Copy to device
                if copy_to_device(self.device, source_folder, mission_uuid):
                    exported_count += 1
                else:
                    failed.append(mission_uuid)
            
            progress.setValue(len(selected))
            
            # Show results
            if exported_count > 0:
                message = f"Successfully exported {exported_count} mission(s) to controller."
                
                if failed:
                    message += f"\n\nFailed to export {len(failed)} mission(s)."
                
                QMessageBox.information(self, "Export Complete", message)
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Export Failed",
                    "No missions were exported successfully.",
                )
        
        except Exception as e:
            logger.error(f"Export failed: {e}")
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred during export:\n{e}",
            )
