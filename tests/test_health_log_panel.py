#!/usr/bin/env python3
"""
Unit tests for HealthLogPanel
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QDate
from panels.health_log_panel import HealthLogPanel


class TestHealthLogPanel(unittest.TestCase):
    """Test cases for HealthLogPanel"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up each test"""
        self.panel = HealthLogPanel()
    
    def tearDown(self):
        """Clean up after each test"""
        self.panel.close()
    
    def test_panel_initialization(self):
        """Test panel initializes correctly"""
        self.assertIsNotNone(self.panel)
        self.assertIsInstance(self.panel, HealthLogPanel)
    
    def test_setup_ui(self):
        """Test UI setup"""
        # Should not raise any exceptions
        self.panel.setup_ui()
        
        # Check that key UI elements exist
        self.assertTrue(hasattr(self.panel, 'date_edit'))
        self.assertTrue(hasattr(self.panel, 'symptoms_edit'))
        self.assertTrue(hasattr(self.panel, 'bristol_combo'))
        self.assertTrue(hasattr(self.panel, 'meal_combo'))
    
    def test_save_entry_method(self):
        """Test save entry method exists and is callable"""
        # Should not raise any exceptions
        self.panel.save_entry()
    
    def test_clear_form_method(self):
        """Test clear form method exists and is callable"""
        # Should not raise any exceptions
        self.panel.clear_form()
    
    def test_analyze_patterns_method(self):
        """Test analyze patterns method exists and is callable"""
        # Should not raise any exceptions
        self.panel.analyze_patterns()
    
    def test_export_health_data_method(self):
        """Test export health data method exists and is callable"""
        # Should not raise any exceptions
        self.panel.export_health_data()
    
    def test_refresh_method(self):
        """Test refresh method exists and is callable"""
        # Should not raise any exceptions
        self.panel.refresh()
    
    @patch('utils.db.get_connection')
    def test_save_entry_to_database(self, mock_get_connection):
        """Test saving entry to database"""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        
        # Set up form data
        self.panel.date_edit.setDate(QDate.currentDate())
        self.panel.symptoms_edit.setPlainText("Test symptoms")
        self.panel.bristol_combo.setCurrentText("4")
        self.panel.meal_combo.setCurrentText("Breakfast")
        
        # Test the method
        result = self.panel._save_entry_to_database()
        
        # Verify database operations were called
        mock_conn.execute.assert_called()
        mock_conn.commit.assert_called()


if __name__ == '__main__':
    unittest.main()
