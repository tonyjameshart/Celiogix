#!/usr/bin/env python3
"""
Launcher script for the CeliacShield PySide6 application.

This entry point wires up the refactored main window that delegates
responsibilities to the specialized manager classes.
"""

import sys
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Ensure the project root is on sys.path so package imports work reliably
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.refactored_main_window import RefactoredMainWindow  # noqa: E402


def _setup_logging() -> None:
    """Configure basic application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(PROJECT_ROOT / "logs" / "app.log", mode="a", encoding="utf-8"),
        ],
    )


def main() -> int:
    """Application entry point."""
    _setup_logging()
    logger = logging.getLogger(__name__)

    try:
        app = QApplication(sys.argv)
        app.setApplicationName("CeliacShield")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("CeliacShield")

        logger.info("Launching CeliacShield PySide6 Application (refactored window)...")

        window = RefactoredMainWindow()
        window.show()

        return app.exec()

    except Exception as exc:  # pragma: no cover - fatal startup path
        logger.critical("Failed to launch CeliacShield application: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
