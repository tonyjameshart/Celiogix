"""
Pytest configuration and fixtures
"""

import pytest
import sys
import os
import tempfile
import sqlite3
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qt_app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        app = QApplication([])
        yield app
        app.quit()
    else:
        yield QApplication.instance()


@pytest.fixture
def temp_database():
    """Create temporary database for testing"""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    with patch('utils.db._db_path') as mock_path:
        mock_path.return_value = temp_db.name
        conn = sqlite3.connect(temp_db.name)
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        yield conn
        conn.close()
        os.unlink(temp_db.name)


@pytest.fixture
def temp_themes_dir():
    """Create temporary themes directory for testing"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_app():
    """Create mock application for testing"""
    app = Mock()
    app.allWidgets = Mock(return_value=[])
    return app
