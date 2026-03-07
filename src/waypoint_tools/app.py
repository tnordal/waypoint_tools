"""QApplication setup and initialization."""

import logging
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from waypoint_tools.models.database import Database
from waypoint_tools.ui.main_window import MainWindow
from waypoint_tools.utils.constants import APP_NAME, ORGANIZATION_NAME
from waypoint_tools.utils.single_instance import SingleInstance

logger = logging.getLogger(__name__)


def run_app() -> int:
    """
    Initialize and run the application.
    
    Returns:
        Application exit code
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Check single instance
    with SingleInstance(f"Global\\{ORGANIZATION_NAME}_{APP_NAME}") as instance:
        if not instance.try_acquire():
            # Another instance is already running
            logger.info("Another instance is already running")
            
            # Show message to user
            temp_app = QApplication(sys.argv)
            QMessageBox.information(
                None,
                "Already Running",
                f"{APP_NAME} is already running.\n\n"
                "Only one instance can run at a time.",
            )
            return 0
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setOrganizationName(ORGANIZATION_NAME)
        
        # Initialize database
        db = Database.get_instance()
        logger.info(f"Database initialized with {len(db.get_all_missions())} missions")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Run event loop
        return app.exec()
