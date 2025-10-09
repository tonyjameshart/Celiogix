#!/usr/bin/env python3
"""
Menu Manager for Celiogix Application

Handles menu bar setup, styling, and navigation management.
"""

import logging
from typing import List, Tuple, Optional, Dict, Any, Callable
from PySide6.QtWidgets import (
    QMenuBar, QMenu, QWidget, QHBoxLayout, 
    QPushButton, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QAction

# Import error handling
from utils.error_handler import handle_error, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class MenuManager:
    """Manages menu bar, navigation, and menu-related functionality"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_bar = None
        self.menu_widget = None
        
        # Menu configuration
        self.menu_items = [
            ("&Cookbook", "Ctrl+1", 0),
            ("&Pantry", "Ctrl+2", 1),
            ("&Shopping List", "Ctrl+3", 2),
            ("&Menu Planner", "Ctrl+4", 3),
            ("&Health Log", "Ctrl+5", 4),
            ("&Calendar", "Ctrl+6", 5),
            ("&Guide", "Ctrl+7", 6),
        ]
    
    def setup_menu_bar(self) -> QMenuBar:
        """
        Set up the traditional menu bar
        
        Returns:
            QMenuBar: The configured menu bar
        """
        self.menu_bar = self.main_window.menuBar()
        
        # Add panel actions
        for text, shortcut, panel_index in self.menu_items:
            action = QAction(text, self.main_window)
            action.setShortcut(QKeySequence(shortcut))
            action.setStatusTip(f'Switch to {text.replace("&", "")} panel')
            action.triggered.connect(lambda checked, idx=panel_index: self.main_window.switch_to_panel(idx))
            self.menu_bar.addAction(action)
        
        # Add Options menu
        self._setup_options_menu()
        
        return self.menu_bar
    
    def _setup_options_menu(self):
        """Set up the Options menu"""
        options_menu = self.menu_bar.addMenu('&Options')
        
        # Settings action
        settings_action = QAction('&Settings', self.main_window)
        settings_action.setShortcut(QKeySequence('Ctrl+,'))
        settings_action.setStatusTip('Open application settings')
        settings_action.triggered.connect(self.main_window.show_settings)
        options_menu.addAction(settings_action)
        
        # Separator
        options_menu.addSeparator()
        
        # About action
        about_action = QAction('&About', self.main_window)
        about_action.setStatusTip('About Celiogix')
        about_action.triggered.connect(self.main_window.show_about)
        options_menu.addAction(about_action)
        
        # Separator
        options_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('E&xit', self.main_window)
        exit_action.setShortcut(QKeySequence('Ctrl+Q'))
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.main_window.close)
        options_menu.addAction(exit_action)
    
    def create_custom_menu_widget(self) -> QWidget:
        """
        Create a custom menu widget (alternative to traditional menu bar)
        
        Returns:
            QWidget: Custom menu widget
        """
        menu_widget = QWidget()
        menu_layout = QHBoxLayout(menu_widget)
        menu_layout.setContentsMargins(10, 5, 10, 5)
        menu_layout.setSpacing(15)
        
        # Add left spacer
        left_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        menu_layout.addItem(left_spacer)
        
        # Create menu buttons
        for text, shortcut, panel_index in self.menu_items:
            btn = self._create_menu_button(text, panel_index)
            menu_layout.addWidget(btn)
        
        # Add Options button
        options_btn = self._create_options_button()
        menu_layout.addWidget(options_btn)
        
        # Add right spacer
        right_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        menu_layout.addItem(right_spacer)
        
        self.menu_widget = menu_widget
        return menu_widget
    
    def _create_menu_button(self, text: str, panel_index: int) -> QPushButton:
        """Create a menu button"""
        # Remove ampersand from display text
        display_text = text.replace("&", "")
        
        btn = QPushButton(display_text)
        btn.setStyleSheet(self._get_menu_button_style())
        btn.clicked.connect(lambda: self.main_window.switch_to_panel(panel_index))
        return btn
    
    def _create_options_button(self) -> QPushButton:
        """Create the Options button"""
        options_btn = QPushButton("Options")
        options_btn.setStyleSheet(self._get_menu_button_style())
        options_btn.clicked.connect(self.main_window.show_settings)
        return options_btn
    
    def _get_menu_button_style(self) -> str:
        """Get the CSS style for menu buttons"""
        return """
            QPushButton {
                background-color: transparent;
                color: #1b5e20;
                border: none;
                padding: 8px 12px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e8f5e8;
                color: #1b5e20;
            }
            QPushButton:pressed {
                background-color: #66bb6a;
                color: #ffffff;
            }
        """
    
    def apply_menu_bar_styling(self, menubar: QMenuBar):
        """
        Apply styling to the menu bar
        
        Args:
            menubar: Menu bar to style
        """
        try:
            # Clear any existing stylesheet first
            menubar.setStyleSheet("")
            
            # Apply comprehensive menu styling
            menu_style = self._get_menu_bar_style()
            menubar.setStyleSheet(menu_style)
            
            # Ensure menu bar is properly positioned and visible
            menubar.setVisible(True)
            menubar.setEnabled(True)
            menubar.raise_()
            menubar.activateWindow()
            
            # Force repaint and layout update
            menubar.repaint()
            menubar.update()
            menubar.adjustSize()
            
            # Ensure menu bar is at the very top
            menubar.move(0, 0)
            # QMenuBar doesn't have setZValue (that's for QGraphicsItem)
            # Raise to top of widget stack instead
            menubar.raise_()
            
        except Exception as e:
            handle_error(
                e,
                ErrorCategory.UI,
                ErrorSeverity.MEDIUM,
                "Menu Bar Styling",
                False,
                self.main_window
            )
    
    def _get_menu_bar_style(self) -> str:
        """Get the CSS style for menu bar"""
        return """
            QMenuBar {
                background-color: #f1f8e9;
                color: #1b5e20;
                border-bottom: 1px solid #c8e6c9;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                padding: 4px 20px;
                spacing: 15px;
                text-align: center;
            }
            
            QMenuBar::item {
                background-color: transparent;
                color: #1b5e20;
                padding: 8px 12px;
                border-radius: 4px;
                margin: 2px;
                border: none;
                text-align: center;
            }
            
            QMenuBar::item:selected {
                background-color: #e8f5e8;
                color: #1b5e20;
                border: 1px solid #c8e6c9;
            }
            
            QMenuBar::item:pressed {
                background-color: #66bb6a;
                color: #ffffff;
            }
            
            QMenuBar::item:disabled {
                color: #81c784;
            }
            
            QMenu {
                background-color: #ffffff;
                color: #1b5e20;
                border: 1px solid #c8e6c9;
                border-radius: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                padding: 4px;
            }
            
            QMenu::item {
                background-color: transparent;
                color: #1b5e20;
                padding: 8px 20px;
                border-radius: 4px;
                margin: 1px;
                border: none;
            }
            
            QMenu::item:selected {
                background-color: #e8f5e8;
                color: #1b5e20;
            }
            
            QMenu::item:disabled {
                color: #81c784;
            }
            
            QMenu::separator {
                height: 1px;
                background-color: #c8e6c9;
                margin: 4px 8px;
            }
            
            QMenu::indicator {
                width: 16px;
                height: 16px;
                margin-right: 8px;
            }
            
            QMenu::indicator:checked {
                background-color: #2e7d32;
                border: 1px solid #1b5e20;
                border-radius: 2px;
            }
            
            QMenu::indicator:unchecked {
                background-color: transparent;
                border: 1px solid #c8e6c9;
                border-radius: 2px;
            }
        """
    
    def ensure_menu_bar_visibility(self):
        """Ensure menu bar is visible and not overlapped"""
        if not self.menu_bar:
            return
        
        try:
            # Ensure menu bar is at the top and visible
            self.menu_bar.setVisible(True)
            self.menu_bar.setEnabled(True)
            self.menu_bar.raise_()
            
            # Ensure it's properly sized and positioned
            self.menu_bar.adjustSize()
            
            # Force repaint
            self.menu_bar.update()
            self.menu_bar.repaint()
            
            # Make sure no other widgets are overlapping
            self.menu_bar.setGeometry(self.menu_bar.geometry())
            
        except Exception as e:
            handle_error(
                e,
                ErrorCategory.UI,
                ErrorSeverity.MEDIUM,
                "Menu Bar Visibility",
                False,
                self.main_window
            )
    
    def refresh_menu_styling(self):
        """Refresh menu bar styling with delayed execution"""
        if not self.menu_bar:
            return
        
        try:
            # Apply styling directly instead of using QTimer
            # This avoids potential thread issues with QTimer
            from PySide6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
            self.apply_menu_bar_styling(self.menu_bar)
        except Exception as e:
            handle_error(
                e,
                ErrorCategory.UI,
                ErrorSeverity.MEDIUM,
                "Menu Refresh",
                False,
                self.main_window
            )
    
    def get_menu_bar(self) -> Optional[QMenuBar]:
        """Get the menu bar"""
        return self.menu_bar
    
    def get_menu_widget(self) -> Optional[QWidget]:
        """Get the custom menu widget"""
        return self.menu_widget
