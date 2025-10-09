#!/usr/bin/env python3
"""
Unit tests for BasePanel class
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from panels.base_panel import BasePanel


class TestBasePanel(unittest.TestCase):
    """Test cases for BasePanel"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up each test"""
        self.panel = BasePanel()
    
    def tearDown(self):
        """Clean up after each test"""
        self.panel.close()
    
    def test_panel_initialization(self):
        """Test panel initializes correctly"""
        self.assertIsNotNone(self.panel)
        self.assertIsInstance(self.panel, BasePanel)
    
    def test_setup_ui(self):
        """Test UI setup"""
        # Should not raise any exceptions
        self.panel.setup_ui()
        self.assertTrue(hasattr(self.panel, 'layout'))
    
    def test_refresh_method(self):
        """Test refresh method exists and is callable"""
        # Should not raise any exceptions
        self.panel.refresh()
    
    def test_save_data_method(self):
        """Test save_data method exists and is callable"""
        # Should not raise any exceptions
        self.panel.save_data()
    
    def test_load_data_method(self):
        """Test load_data method exists and is callable"""
        # Should not raise any exceptions
        self.panel.load_data()
    
    def test_app_property(self):
        """Test app property can be set"""
        mock_app = Mock()
        panel_with_app = BasePanel(app=mock_app)
        self.assertEqual(panel_with_app.app, mock_app)


if __name__ == '__main__':
    unittest.main()
