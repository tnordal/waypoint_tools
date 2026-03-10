"""Application styling and themes."""

# Light theme stylesheet
LIGHT_THEME = """
QMainWindow, QWidget {
    background-color: #FFFFFF;
    color: #212121;
}

QListWidget, QTableWidget, QTextEdit {
    background-color: #F5F5F5;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
}

QPushButton {
    background-color: #1976D2;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1565C0;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #BDBDBD;
    color: #757575;
}

QLineEdit, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #BDBDBD;
    border-radius: 4px;
    padding: 4px 8px;
}

QLineEdit:focus, QComboBox:focus {
    border: 2px solid #1976D2;
}

QLabel {
    color: #212121;
}

QLabel[class="secondary"] {
    color: #757575;
}

QStatusBar {
    background-color: #F5F5F5;
    color: #757575;
}

QMenuBar {
    background-color: #FFFFFF;
    color: #212121;
}

QMenuBar::item:selected {
    background-color: #E3F2FD;
}

QMenu {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
}

QMenu::item:selected {
    background-color: #E3F2FD;
}

QSplitter::handle {
    background-color: #E0E0E0;
}

QScrollBar:vertical, QScrollBar:horizontal {
    background-color: #F5F5F5;
    border: none;
}

QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background-color: #BDBDBD;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background-color: #9E9E9E;
}
"""

# Dark theme stylesheet
DARK_THEME = """
QMainWindow, QWidget {
    background-color: #121212;
    color: #FFFFFF;
}

QListWidget, QTableWidget, QTextEdit {
    background-color: #1E1E1E;
    border: 1px solid #2C2C2C;
    border-radius: 4px;
    color: #FFFFFF;
}

QPushButton {
    background-color: #90CAF9;
    color: #000000;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #64B5F6;
}

QPushButton:pressed {
    background-color: #42A5F5;
}

QPushButton:disabled {
    background-color: #424242;
    color: #757575;
}

QLineEdit, QComboBox {
    background-color: #1E1E1E;
    border: 1px solid #424242;
    border-radius: 4px;
    padding: 4px 8px;
    color: #FFFFFF;
}

QLineEdit:focus, QComboBox:focus {
    border: 2px solid #90CAF9;
}

QLabel {
    color: #FFFFFF;
}

QLabel[class="secondary"] {
    color: #B0B0B0;
}

QStatusBar {
    background-color: #1E1E1E;
    color: #B0B0B0;
}

QMenuBar {
    background-color: #121212;
    color: #FFFFFF;
}

QMenuBar::item:selected {
    background-color: #1E1E1E;
}

QMenu {
    background-color: #1E1E1E;
    border: 1px solid #2C2C2C;
    color: #FFFFFF;
}

QMenu::item:selected {
    background-color: #2C2C2C;
}

QSplitter::handle {
    background-color: #2C2C2C;
}

QScrollBar:vertical, QScrollBar:horizontal {
    background-color: #1E1E1E;
    border: none;
}

QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background-color: #424242;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background-color: #616161;
}
"""


def get_theme_stylesheet(theme: str) -> str:
    """
    Get stylesheet for the specified theme.
    
    Args:
        theme: Theme name ("light" or "dark")
    
    Returns:
        QSS stylesheet string
    """
    if theme == "dark":
        return DARK_THEME
    return LIGHT_THEME
