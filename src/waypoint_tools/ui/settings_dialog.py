"""Settings dialog for application configuration."""

import logging
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from waypoint_tools.models.database import Database

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Dialog for editing application settings."""
    
    theme_changed = pyqtSignal(str)  # Emits "light" or "dark"
    
    def __init__(self, parent=None) -> None:
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.db = Database.get_instance()
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 300)
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Form layout for settings
        form = QFormLayout()
        form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        
        # Theme selector
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        form.addRow("Theme:", self.theme_combo)
        
        # Backup folder selector
        backup_layout = QHBoxLayout()
        self.backup_path_edit = QLineEdit()
        self.backup_path_edit.setReadOnly(True)
        backup_layout.addWidget(self.backup_path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_backup_folder)
        backup_layout.addWidget(browse_btn)
        
        form.addRow("Backup Folder:", backup_layout)
        
        # Info label
        info_label = QLabel(
            "The backup folder is where mission backups will be stored.\n"
            "If not set, backups will be saved to Documents/DJI Waypoint Tools/Backups."
        )
        info_label.setWordWrap(True)
        info_label.setProperty("class", "secondary")
        form.addRow("", info_label)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_settings(self) -> None:
        """Load current settings from database."""
        settings = self.db.get_settings()
        
        # Load theme
        theme = settings.get("theme", "light")
        if theme == "dark":
            self.theme_combo.setCurrentText("Dark")
        else:
            self.theme_combo.setCurrentText("Light")
        
        # Load backup folder
        backup_folder = settings.get("backup_folder", "")
        if backup_folder:
            self.backup_path_edit.setText(backup_folder)
        else:
            # Show default path
            default_path = Path.home() / "Documents" / "DJI Waypoint Tools" / "Backups"
            self.backup_path_edit.setPlaceholderText(str(default_path))
    
    def _on_theme_changed(self, theme_text: str) -> None:
        """Handle theme selection change."""
        theme = theme_text.lower()
        self.theme_changed.emit(theme)
    
    def _browse_backup_folder(self) -> None:
        """Open folder browser for backup location."""
        current_path = self.backup_path_edit.text()
        if not current_path:
            current_path = str(
                Path.home() / "Documents" / "DJI Waypoint Tools" / "Backups"
            )
        
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Folder",
            current_path,
            QFileDialog.Option.ShowDirsOnly,
        )
        
        if folder:
            self.backup_path_edit.setText(folder)
            logger.info(f"Backup folder selected: {folder}")
    
    def accept(self) -> None:
        """Save settings when dialog is accepted."""
        settings = self.db.get_settings()
        
        # Save theme
        theme = self.theme_combo.currentText().lower()
        settings["theme"] = theme
        
        # Save backup folder
        backup_folder = self.backup_path_edit.text()
        if backup_folder:
            settings["backup_folder"] = backup_folder
        else:
            # Remove custom backup folder (use default)
            settings.pop("backup_folder", None)
        
        self.db.update_settings(settings)
        logger.info(f"Settings saved: theme={theme}, backup_folder={backup_folder}")
        
        super().accept()
