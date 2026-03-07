"""Main entry point for the Waypoint Tools application."""

import sys

from waypoint_tools.app import run_app


def main() -> None:
    """Application entry point."""
    sys.exit(run_app())


if __name__ == "__main__":
    main()
