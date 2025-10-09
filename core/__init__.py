#!/usr/bin/env python3
"""
Core package for Celiogix Application

This package contains the core management classes that handle different
aspects of the application functionality.
"""

from .theme_manager import ThemeManager, get_theme_manager
from .ui_manager import UIManager
from .menu_manager import MenuManager
from .database_manager import DatabaseManager, get_database_manager
from .status_manager import StatusManager, get_status_manager
from .refactored_main_window import RefactoredMainWindow

__all__ = [
    'ThemeManager',
    'get_theme_manager',
    'UIManager',
    'MenuManager',
    'DatabaseManager',
    'get_database_manager',
    'StatusManager',
    'get_status_manager',
    'RefactoredMainWindow'
]
