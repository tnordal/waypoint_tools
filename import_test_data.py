"""Test script to import test data."""

from pathlib import Path

from waypoint_tools.services.file_manager import import_missions_from_folder

if __name__ == "__main__":
    test_data_folder = Path(__file__).parent / "test_data"
    print(f"Importing missions from: {test_data_folder}")
    
    new_count, updated_count = import_missions_from_folder(test_data_folder)
    print(f"Imported {new_count} new mission(s), updated {updated_count} existing")
