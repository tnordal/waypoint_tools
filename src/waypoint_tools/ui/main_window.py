"""Main application window."""

import logging
from pathlib import Path

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from waypoint_tools.models.database import Database
from waypoint_tools.services.file_manager import import_missions_from_folder
from waypoint_tools.ui.mission_list import MissionListWidget
from waypoint_tools.ui.preview_panel import PreviewPanel
from waypoint_tools.ui.settings_dialog import SettingsDialog
from waypoint_tools.ui.styles import get_theme_stylesheet
from waypoint_tools.utils.constants import (
    APP_NAME,
    ORGANIZATION_NAME,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with mission management interface."""
    
    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        
        self.db = Database.get_instance()
        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)
        
        self._setup_ui()
        self._apply_theme()
        self._restore_window_state()
        self._connect_signals()
        
        logger.info("Main window initialized")
    
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Mission list (left)
        self.mission_list = MissionListWidget()
        splitter.addWidget(self.mission_list)
        
        # Preview panel (right)
        self.preview_panel = PreviewPanel()
        splitter.addWidget(self.preview_panel)
        
        # Set initial splitter sizes (40% list, 60% preview)
        splitter.setSizes([400, 600])
        self.splitter = splitter
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()
    
    def _create_toolbar(self) -> QWidget:
        """Create the toolbar with action buttons."""
        toolbar = QWidget()
        toolbar.setFixedHeight(50)
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Controller status
        self.controller_status = QLabel("RC 2: Not Connected")
        self.controller_status.setProperty("class", "secondary")
        layout.addWidget(self.controller_status)
        
        layout.addStretch()
        
        # Action buttons
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._on_refresh)
        layout.addWidget(refresh_btn)
        
        import_folder_btn = QPushButton("Import Folder")
        import_folder_btn.clicked.connect(self._on_import_folder)
        layout.addWidget(import_folder_btn)
        
        import_btn = QPushButton("Import")
        import_btn.setEnabled(False)
        layout.addWidget(import_btn)
        
        export_btn = QPushButton("Export")
        export_btn.setEnabled(False)
        layout.addWidget(export_btn)
        
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self._on_settings)
        layout.addWidget(settings_btn)
        
        return toolbar
    
    def _connect_signals(self) -> None:
        """Connect internal signals to slots."""
        self.mission_list.mission_selected.connect(self.preview_panel.set_mission)
    
    def _apply_theme(self) -> None:
        """Apply the current theme to the application."""
        theme = self.db.get_theme()
        stylesheet = get_theme_stylesheet(theme)
        self.setStyleSheet(stylesheet)
        logger.debug(f"Applied theme: {theme}")
    
    def _restore_window_state(self) -> None:
        """Restore window geometry and state from settings."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        splitter_state = self.settings.value("splitter_state")
        if splitter_state:
            self.splitter.restoreState(splitter_state)
    
    def _save_window_state(self) -> None:
        """Save window geometry and state to settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitter_state", self.splitter.saveState())
    
    def _update_status_bar(self) -> None:
        """Update status bar with mission count and backup location."""
        mission_count = len(self.db.get_all_missions())
        backup_folder = self.db.get_backup_folder()
        
        status_text = (
            f"{mission_count} mission(s) | "
            f"Backup: {backup_folder}"
        )
        self.status_bar.showMessage(status_text)
    
    def _on_refresh(self) -> None:
        """Handle refresh button click."""
        logger.info("Refresh requested")
        self.mission_list.refresh()
        self._update_status_bar()
    
    def _on_import_folder(self) -> None:
        """Handle import folder button click."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder Containing Mission Folders",
            str(Path.cwd()),
        )
        
        if not folder:
            return
        
        logger.info(f"Importing missions from {folder}")
        
        try:
            new_count, updated_count = import_missions_from_folder(Path(folder))
            
            # Build message
            if new_count == 0 and updated_count == 0:
                message = "No missions found in the selected folder."
            elif new_count > 0 and updated_count > 0:
                message = (
                    f"Imported {new_count} new mission(s) and "
                    f"updated {updated_count} existing mission(s)."
                )
            elif new_count > 0:
                message = f"Imported {new_count} new mission(s)."
            else:
                message = f"Updated {updated_count} existing mission(s)."
            
            QMessageBox.information(
                self,
                "Import Complete",
                message,
            )
            
            # Refresh UI
            self._on_refresh()
            
        except Exception as e:
            logger.error(f"Failed to import missions: {e}")
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import missions:\n{e}",
            )
    
    def _on_settings(self) -> None:
        """Handle settings button click."""
        logger.info("Settings dialog requested")
        
        dialog = SettingsDialog(self)
        
        # Connect theme change signal for live preview
        dialog.theme_changed.connect(self._apply_theme_from_name)
        
        if dialog.exec():
            # Settings saved - apply theme and update UI
            self._apply_theme()
            self._update_status_bar()
            logger.info("Settings applied")
        else:
            # Settings cancelled - revert theme to saved
            self._apply_theme()
            logger.info("Settings cancelled")
    
    def _apply_theme_from_name(self, theme: str) -> None:
        """Apply a theme by name (for live preview)."""
        stylesheet = get_theme_stylesheet(theme)
        self.setStyleSheet(stylesheet)
        logger.debug(f"Applied theme: {theme}")
    
    def closeEvent(self, event) -> None:
        """Handle window close event."""
        self._save_window_state()
        logger.info("Main window closed")
        super().closeEvent(event)
