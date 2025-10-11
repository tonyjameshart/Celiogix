#!/usr/bin/env python3
"""
UI Manager for CeliacShield Application

Handles UI setup, styling, and component management for the main window.
"""

import logging
from typing import List, Tuple, Optional, Dict, Any, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, 
    QPushButton, QSpacerItem, QSizePolicy, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Import error handling
from utils.error_handler import handle_error, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class UIManager:
    """Manages UI components and styling for the main window"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.nav_widget = None
        self.title_label = None
        self.tab_widget = None
        self.status_bar = None
        
        # Navigation button configuration
        self.nav_buttons = [
            ("Cookbook", 0),
            ("Pantry", 1),
            ("Shopping List", 2),
            ("Menu Planner", 3),
            ("Health Log", 4),
            ("Calendar", 5),
            ("Guide", 6),
        ]
        
        # Track active navigation button
        self.active_nav_button = None
        self.nav_button_widgets = {}
    
    def setup_main_ui(self) -> QWidget:
        """
        Set up the main UI layout
        
        Returns:
            QWidget: The central widget
        """
        # Create central widget
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Set up title
        self.title_label = self._create_title_label()
        main_layout.addWidget(self.title_label)
        
        # Set up navigation
        self.nav_widget = self._create_navigation_widget()
        main_layout.addWidget(self.nav_widget)
        
        # Set up tab widget
        self.tab_widget = self._create_tab_widget()
        main_layout.addWidget(self.tab_widget)
        
        return central_widget
    
    def _create_title_label(self) -> QLabel:
        """Create and configure the title label"""
        title_label = QLabel("Celiac Shield")
        
        # Configure font
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        return title_label
    
    def _create_navigation_widget(self) -> QWidget:
        """Create the navigation widget with buttons"""
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(20, 10, 20, 10)
        nav_layout.setSpacing(10)
        
        # Add left spacer
        left_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        nav_layout.addItem(left_spacer)
        
        # Create navigation buttons
        for text, panel_index in self.nav_buttons:
            btn = self._create_nav_button(text, panel_index)
            nav_layout.addWidget(btn)
            self.nav_button_widgets[panel_index] = btn
        
        # Add Options button
        options_btn = self._create_options_button()
        nav_layout.addWidget(options_btn)
        
        # Add right spacer
        right_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        nav_layout.addItem(right_spacer)
        
        return nav_widget
    
    def _create_nav_button(self, text: str, panel_index: int) -> QPushButton:
        """Create a navigation button"""
        btn = QPushButton(text)
        btn.setStyleSheet(self._get_nav_button_style())
        btn.clicked.connect(lambda: self.main_window.switch_to_panel(panel_index))
        return btn
    
    def _create_options_button(self) -> QPushButton:
        """Create the Options button"""
        options_btn = QPushButton("Options")
        options_btn.setStyleSheet(self._get_nav_button_style())
        options_btn.clicked.connect(self.main_window.show_settings)
        return options_btn
    
    def _get_nav_button_style(self, theme_colors: Optional[Dict[str, str]] = None) -> str:
        """Get the CSS style for navigation buttons with theme support"""
        if theme_colors:
            # Use theme colors
            primary = theme_colors.get('primary', '#1b5e20')
            primary_light = theme_colors.get('primary_light', '#e8f5e8')
            primary_dark = theme_colors.get('primary_dark', '#2e7d32')
            border_color = theme_colors.get('border_color', theme_colors.get('border', '#c8e6c9'))
            text_primary = theme_colors.get('text_primary', '#212121')
            text_on_primary = theme_colors.get('text_on_primary', '#ffffff')
        else:
            # Fallback to default green theme
            primary = '#1b5e20'
            primary_light = '#e8f5e8'
            primary_dark = '#2e7d32'
            border_color = '#c8e6c9'
            text_primary = '#1b5e20'
            text_on_primary = '#ffffff'
        
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {text_primary};
                border: 1px solid {border_color};
                padding: 8px 15px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                border-radius: 4px;
                min-width: 80px;
                font-weight: normal;
            }}
            QPushButton:hover {{
                background-color: {primary_light};
                color: {text_primary};
                border-color: {primary};
            }}
            QPushButton:pressed {{
                background-color: {primary};
                color: {text_on_primary};
                border-color: {primary_dark};
            }}
            QPushButton[active="true"] {{
                background-color: {primary};
                color: {text_on_primary};
                border-color: {primary_dark};
                font-weight: bold;
            }}
        """
    
    def _create_tab_widget(self) -> QTabWidget:
        """Create and configure the tab widget"""
        tab_widget = QTabWidget()
        tab_widget.setTabPosition(QTabWidget.North)
        tab_widget.setMovable(False)  # Disable tab movement
        
        # Hide tab bar - we only want to show the active panel content
        tab_widget.tabBar().hide()
        
        return tab_widget
    
    def setup_status_bar(self) -> QStatusBar:
        """Set up the status bar"""
        status_bar = QStatusBar()
        self.main_window.setStatusBar(status_bar)
        self.status_bar = status_bar
        return status_bar
    
    def add_panel_to_tabs(self, panel: QWidget, title: str) -> int:
        """
        Add a panel to the tab widget
        
        Args:
            panel: Panel widget to add
            title: Tab title
            
        Returns:
            int: Tab index
        """
        if self.tab_widget:
            return self.tab_widget.addTab(panel, title)
        return -1
    
    def switch_to_tab(self, index: int):
        """Switch to a specific tab"""
        if self.tab_widget and 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
            self.set_active_nav_button(index)
    
    def get_current_tab_index(self) -> int:
        """Get the current tab index"""
        return self.tab_widget.currentIndex() if self.tab_widget else -1
    
    def get_tab_widget(self) -> QTabWidget:
        """Get the tab widget"""
        return self.tab_widget
    
    def update_status_message(self, message: str):
        """Update the status bar message"""
        if self.status_bar:
            self.status_bar.showMessage(message)
    
    def update_navigation_theme(self, theme_colors: Dict[str, str]):
        """
        Update navigation widget styling based on theme colors
        
        Args:
            theme_colors: Dictionary of theme color values
        """
        if not self.nav_widget:
            return
        
        try:
            header_bg = theme_colors.get('background', '#fafafa')
            border_color = (theme_colors.get('border_color') or 
                           theme_colors.get('border') or 
                           theme_colors.get('surface_variant') or 
                           '#c8e6c9')
            
            nav_style = f"""
                QWidget {{
                    background-color: {header_bg};
                    border-bottom: 1px solid {border_color};
                }}
            """
            self.nav_widget.setStyleSheet(nav_style)
            
            # Update all navigation button styles with theme colors
            button_style = self._get_nav_button_style(theme_colors)
            for btn in self.nav_button_widgets.values():
                btn.setStyleSheet(button_style)
                # Re-apply active state if needed
                if btn.property("active"):
                    btn.style().unpolish(btn)
                    btn.style().polish(btn)
                    
        except Exception as e:
            handle_error(
                e,
                ErrorCategory.UI,
                ErrorSeverity.MEDIUM,
                "Navigation Theme Update",
                False,
                self.main_window
            )
    
    def update_title_theme(self, theme_colors: Dict[str, str]):
        """
        Update title label styling based on theme colors
        
        Args:
            theme_colors: Dictionary of theme color values
        """
        if not self.title_label:
            return
        
        try:
            header_bg = theme_colors.get('background', '#fafafa')
            border_color = (theme_colors.get('border_color') or 
                           theme_colors.get('border') or 
                           theme_colors.get('surface_variant') or 
                           '#c8e6c9')
            text_color = theme_colors.get('text_primary', '#212121')
            
            title_style = f"""
                QLabel {{
                    color: {text_color} !important; 
                    margin: 15px; 
                    padding: 15px; 
                    background-color: {header_bg} !important;
                    border-bottom: 2px solid {border_color};
                    border: none;
                }}
            """
            self.title_label.setStyleSheet(title_style)
        except Exception as e:
            handle_error(
                e,
                ErrorCategory.UI,
                ErrorSeverity.MEDIUM,
                "Title Theme Update",
                False,
                self.main_window
            )
    
    def get_navigation_widget(self) -> Optional[QWidget]:
        """Get the navigation widget"""
        return self.nav_widget
    
    def get_title_label(self) -> Optional[QLabel]:
        """Get the title label"""
        return self.title_label
    
    def get_tab_widget(self) -> Optional[QTabWidget]:
        """Get the tab widget"""
        return self.tab_widget
    
    def get_status_bar(self) -> Optional[QStatusBar]:
        """Get the status bar"""
        return self.status_bar
    
    def set_active_nav_button(self, panel_index: int):
        """
        Set the active navigation button
        
        Args:
            panel_index: Index of the panel to make active
        """
        # Remove active state from current button
        if self.active_nav_button is not None and self.active_nav_button in self.nav_button_widgets:
            current_btn = self.nav_button_widgets[self.active_nav_button]
            current_btn.setProperty("active", False)
            current_btn.style().unpolish(current_btn)
            current_btn.style().polish(current_btn)
        
        # Set new active button
        if panel_index in self.nav_button_widgets:
            active_btn = self.nav_button_widgets[panel_index]
            active_btn.setProperty("active", True)
            active_btn.style().unpolish(active_btn)
            active_btn.style().polish(active_btn)
            self.active_nav_button = panel_index
    
    def get_active_nav_button(self) -> Optional[int]:
        """Get the currently active navigation button index"""
        return self.active_nav_button
