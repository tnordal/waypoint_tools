"""Thumbnail viewer dialog for displaying mission waypoint thumbnails."""

import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class ThumbnailViewer(QDialog):
    """Dialog for viewing mission thumbnails in a grid."""
    
    def __init__(
        self,
        thumbnails: list[str],
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize the thumbnail viewer.
        
        Args:
            thumbnails: List of thumbnail image paths
            parent: Parent widget
        """
        super().__init__(parent)
        self.thumbnails = thumbnails
        self._setup_ui()
        self._load_thumbnails()
    
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle("Mission Thumbnails")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Scroll area for grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Container for grid
        container = QWidget()
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(10)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def _load_thumbnails(self) -> None:
        """Load and display thumbnails in grid."""
        if not self.thumbnails:
            no_thumbs = QLabel("No thumbnails available")
            no_thumbs.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(no_thumbs, 0, 0)
            return
        
        cols = 3  # 3 thumbnails per row
        for i, thumb_path in enumerate(self.thumbnails):
            row = i // cols
            col = i % cols
            
            thumb_widget = self._create_thumbnail_widget(thumb_path, i)
            self.grid_layout.addWidget(thumb_widget, row, col)
    
    def _create_thumbnail_widget(self, path: str, index: int) -> QWidget:
        """Create a widget for a single thumbnail."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Thumbnail label
        label = QLabel()
        
        thumb_path = Path(path)
        if thumb_path.exists():
            pixmap = QPixmap(str(thumb_path))
            if not pixmap.isNull():
                # Scale to reasonable size
                pixmap = pixmap.scaled(
                    200,
                    200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                label.setPixmap(pixmap)
            else:
                label.setText(f"WP {index}\n(Invalid image)")
        else:
            label.setText(f"WP {index}\n(Not found)")
        
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        layout.addWidget(label)
        
        # Filename
        filename = QLabel(thumb_path.name)
        filename.setAlignment(Qt.AlignmentFlag.AlignCenter)
        filename.setProperty("class", "secondary")
        layout.addWidget(filename)
        
        return widget
