"""Edit dialog for mission metadata."""

import logging

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from waypoint_tools.models.database import Database
from waypoint_tools.models.mission import Mission

logger = logging.getLogger(__name__)


class EditMissionDialog(QDialog):
    """Dialog for editing mission metadata."""
    
    def __init__(
        self,
        mission: Mission,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize the edit dialog.
        
        Args:
            mission: Mission to edit
            parent: Parent widget
        """
        super().__init__(parent)
        self.mission = mission
        self.db = Database.get_instance()
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle("Edit Mission")
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Form layout for fields
        form = QFormLayout()
        
        # UUID (read-only)
        uuid_label = QLabel(self.mission.uuid)
        uuid_label.setProperty("class", "secondary")
        form.addRow("UUID:", uuid_label)
        
        # Friendly name
        self.name_edit = QLineEdit()
        form.addRow("Name:", self.name_edit)
        
        # Location
        self.location_edit = QLineEdit()
        form.addRow("Location:", self.location_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        form.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form)
        
        # Tags
        tags_label = QLabel("Tags:")
        layout.addWidget(tags_label)
        
        self.tags_list = QListWidget()
        self.tags_list.setMaximumHeight(150)
        layout.addWidget(self.tags_list)
        
        # Tag management buttons
        tag_btn_layout = QVBoxLayout()
        
        add_tag_btn = QPushButton("Add Tag")
        add_tag_btn.clicked.connect(self._add_tag)
        tag_btn_layout.addWidget(add_tag_btn)
        
        remove_tag_btn = QPushButton("Remove Tag")
        remove_tag_btn.clicked.connect(self._remove_tag)
        tag_btn_layout.addWidget(remove_tag_btn)
        
        layout.addLayout(tag_btn_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_data(self) -> None:
        """Load mission data into form."""
        if self.mission.friendly_name:
            self.name_edit.setText(self.mission.friendly_name)
        
        if self.mission.location:
            self.location_edit.setText(self.mission.location)
        
        if self.mission.notes:
            self.notes_edit.setPlainText(self.mission.notes)
        
        for tag in self.mission.tags:
            self.tags_list.addItem(tag)
    
    def _add_tag(self) -> None:
        """Add a new tag to the list."""
        # Get existing tags
        all_tags = self.db.get_all_tags()
        
        # Prompt for tag
        tag, ok = QInputDialog.getItem(
            self,
            "Add Tag",
            "Select or enter a tag:",
            all_tags,
            0,
            True,  # Allow custom input
        )
        
        if ok and tag:
            # Check if already added
            items = [self.tags_list.item(i).text() for i in range(self.tags_list.count())]
            if tag not in items:
                self.tags_list.addItem(tag)
    
    def _remove_tag(self) -> None:
        """Remove selected tag from list."""
        current_row = self.tags_list.currentRow()
        if current_row >= 0:
            self.tags_list.takeItem(current_row)
    
    def _save_and_accept(self) -> None:
        """Save changes and accept dialog."""
        # Update mission
        self.mission.friendly_name = self.name_edit.text().strip() or None
        self.mission.location = self.location_edit.text().strip() or None
        self.mission.notes = self.notes_edit.toPlainText().strip() or None
        
        # Update tags
        self.mission.tags = [
            self.tags_list.item(i).text()
            for i in range(self.tags_list.count())
        ]
        
        # Save to database
        self.db.update_mission(self.mission)
        logger.info(f"Updated mission: {self.mission.uuid}")
        
        self.accept()
