#!/usr/bin/env python3
"""
Unit tests for ThemeCreator service
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from services.theme_creator import ThemeCreator


class TestThemeCreator(unittest.TestCase):
    """Test cases for ThemeCreator"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.theme_creator = ThemeCreator(themes_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_theme_creator_initialization(self):
        """Test theme creator initializes correctly"""
        self.assertIsNotNone(self.theme_creator)
        self.assertEqual(self.theme_creator.themes_dir, self.temp_dir)
    
    def test_save_theme(self):
        """Test saving a theme"""
        theme_data = {
            'name': 'Test Theme',
            'description': 'A test theme',
            'colors': {
                'primary': '#ff0000',
                'background': '#ffffff'
            }
        }
        
        result = self.theme_creator.save_theme('test_theme', theme_data)
        self.assertTrue(result)
        
        # Verify file was created
        theme_file = os.path.join(self.temp_dir, 'test_theme.json')
        self.assertTrue(os.path.exists(theme_file))
    
    def test_load_theme(self):
        """Test loading a theme"""
        theme_data = {
            'name': 'Test Theme',
            'description': 'A test theme',
            'colors': {
                'primary': '#ff0000',
                'background': '#ffffff'
            }
        }
        
        # Save theme first
        self.theme_creator.save_theme('test_theme', theme_data)
        
        # Load theme
        loaded_theme = self.theme_creator.load_theme('test_theme')
        self.assertIsNotNone(loaded_theme)
        self.assertEqual(loaded_theme['name'], 'Test Theme')
        self.assertEqual(loaded_theme['colors']['primary'], '#ff0000')
    
    def test_list_themes(self):
        """Test listing themes"""
        theme_data = {
            'name': 'Test Theme',
            'description': 'A test theme',
            'colors': {
                'primary': '#ff0000',
                'background': '#ffffff'
            }
        }
        
        # Save a theme
        self.theme_creator.save_theme('test_theme', theme_data)
        
        # List themes
        themes = self.theme_creator.list_themes()
        self.assertEqual(len(themes), 1)
        self.assertEqual(themes[0]['id'], 'test_theme')
        self.assertEqual(themes[0]['name'], 'Test Theme')
    
    def test_delete_theme(self):
        """Test deleting a theme"""
        theme_data = {
            'name': 'Test Theme',
            'description': 'A test theme',
            'colors': {
                'primary': '#ff0000',
                'background': '#ffffff'
            }
        }
        
        # Save theme first
        self.theme_creator.save_theme('test_theme', theme_data)
        
        # Verify it exists
        theme_file = os.path.join(self.temp_dir, 'test_theme.json')
        self.assertTrue(os.path.exists(theme_file))
        
        # Delete theme
        result = self.theme_creator.delete_theme('test_theme')
        self.assertTrue(result)
        
        # Verify it's gone
        self.assertFalse(os.path.exists(theme_file))
    
    def test_create_default_themes(self):
        """Test creating default themes"""
        self.theme_creator.create_default_themes()
        
        themes = self.theme_creator.list_themes()
        self.assertGreater(len(themes), 0)
        
        # Check for expected default themes
        theme_ids = [theme['id'] for theme in themes]
        self.assertIn('light_modern', theme_ids)
        self.assertIn('dark_modern', theme_ids)
        self.assertIn('celiac_safe', theme_ids)
    
    def test_apply_theme(self):
        """Test applying a theme"""
        theme_data = {
            'name': 'Test Theme',
            'description': 'A test theme',
            'colors': {
                'primary': '#ff0000',
                'background': '#ffffff'
            },
            'typography': {
                'font_family': 'Arial',
                'font_size': 12
            },
            'components': {
                'border_radius': 4,
                'padding': 8,
                'spacing': 10
            }
        }
        
        # Save theme first
        self.theme_creator.save_theme('test_theme', theme_data)
        
        # Apply theme
        result = self.theme_creator.apply_theme('test_theme', self.app)
        self.assertTrue(result)
        self.assertEqual(self.theme_creator.current_theme, 'test_theme')


if __name__ == '__main__':
    unittest.main()
