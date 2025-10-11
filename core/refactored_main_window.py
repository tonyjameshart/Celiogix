#!/usr/bin/env python3
"""
Refactored Main Window for CeliacShield Application

This is a simplified version of the main window that delegates responsibilities
to specialized manager classes.
"""

import logging
from typing import Optional
from PySide6.QtWidgets import QMainWindow, QWidget, QMessageBox
from PySide6.QtCore import Qt

# Import manager classes
from .theme_manager import get_theme_manager
from .ui_manager import UIManager
from .menu_manager import MenuManager
from .database_manager import get_database_manager
from .status_manager import get_status_manager

# Import error handling
from utils.error_handler import get_error_handler, ErrorCategory, ErrorSeverity

# Import panels
from panels.pantry_panel import PantryPanel
from panels.health_log_panel import HealthLogPanel
from panels.cookbook_panel import CookbookPanel
from panels.shopping_list_panel import ShoppingListPanel
from panels.menu_panel import MenuPanel
from panels.calendar_panel import CalendarPanel
from panels.guide_panel import GuidePanel
from panels.settings_panel import SettingsPanel

logger = logging.getLogger(__name__)


class RefactoredMainWindow(QMainWindow):
    """Refactored main window with delegated responsibilities"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.theme_manager = get_theme_manager()
        self.database_manager = get_database_manager()
        self.status_manager = get_status_manager()
        self.error_handler = get_error_handler()
        
        # Initialize UI and menu managers
        self.ui_manager = UIManager(self)
        self.menu_manager = MenuManager(self)
        
        # Set up the window
        self._setup_window_properties()
        self._initialize_application()
        self._setup_ui()
        self._setup_theme_connections()
        self._apply_initial_theme()
    
    def _setup_window_properties(self):
        """Set up basic window properties"""
        self.setWindowTitle("Celiac Shield")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
    
    def _initialize_application(self):
        """Initialize application components"""
        # Initialize database
        db_success = self.database_manager.initialize()
        if db_success:
            self.status_manager.update_status_with_database(True)
        else:
            self.status_manager.update_status_with_database(False)
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Set up main UI
        central_widget = self.ui_manager.setup_main_ui()
        
        # Set up status bar
        status_bar = self.ui_manager.setup_status_bar()
        self.status_manager.set_status_bar(status_bar)
        
        # Note: Menu bar removed as per user request
        
        # Set up panels
        self._setup_panels()
        
        # Note: Tab change signal removed since tabs are not used for navigation
    
    def _setup_panels(self):
        """Set up all application panels"""
        try:
            # Cookbook Panel (index 0)
            cookbook_panel = CookbookPanel(self, self)
            self.ui_manager.add_panel_to_tabs(cookbook_panel, "Cookbook")
            
            # Pantry Panel (index 1)
            pantry_panel = PantryPanel(self, self)
            self.ui_manager.add_panel_to_tabs(pantry_panel, "Pantry")
            
            # Shopping List Panel (index 2)
            shopping_panel = ShoppingListPanel(self, self)
            self.ui_manager.add_panel_to_tabs(shopping_panel, "Shopping List")
            
            # Menu Panel (index 3)
            menu_panel = MenuPanel(self, self)
            self.ui_manager.add_panel_to_tabs(menu_panel, "Menu Planner")
            
            # Health Log Panel (index 4)
            health_panel = HealthLogPanel(self, self)
            self.ui_manager.add_panel_to_tabs(health_panel, "Health Log")
            
            # Calendar Panel (index 5)
            calendar_panel = CalendarPanel(self, self)
            self.ui_manager.add_panel_to_tabs(calendar_panel, "Calendar")
            
            # Guide Panel (index 6)
            guide_panel = GuidePanel(self, self)
            self.ui_manager.add_panel_to_tabs(guide_panel, "Guide")
            
            # Set initial active navigation button (Cookbook - index 0)
            self.ui_manager.set_active_nav_button(0)
            
            self.status_manager.update_status("Panels initialized successfully")
            
        except Exception as e:
            self.error_handler.handle_error(
                e, 
                ErrorCategory.UI, 
                ErrorSeverity.HIGH, 
                "Panel Setup", 
                True, 
                self
            )
    
    def _setup_theme_connections(self):
        """Set up theme manager signal connections"""
        self.theme_manager.theme_applied.connect(self._on_theme_applied)
        self.theme_manager.theme_error.connect(self._on_theme_error)
        self.theme_manager.fallback_applied.connect(self._on_fallback_applied)
    
    def _apply_initial_theme(self):
        """Apply the initial theme"""
        success = self.theme_manager.apply_saved_theme()
        if not success:
            logger.warning("Failed to apply initial theme")
    
    def _on_theme_applied(self, theme_id: str):
        """Handle theme application success"""
        self.status_manager.update_status_with_theme(theme_id, True)
        self._update_ui_theme()
    
    def _on_theme_error(self, error_message: str):
        """Handle theme application error"""
        self.status_manager.set_error_status(error_message, "Theme Application")
    
    def _on_fallback_applied(self, fallback_theme_id: str):
        """Handle fallback theme application"""
        self.status_manager.update_status(f"Applied fallback theme: {fallback_theme_id}", "warning")
        self._update_ui_theme()
    
    def _update_ui_theme(self):
        """Update UI components to match current theme"""
        try:
            # Get current theme colors
            theme_colors = self.theme_manager.get_theme_colors()
            
            # Update navigation theme
            nav_widget = self.ui_manager.get_navigation_widget()
            if nav_widget:
                self.ui_manager.update_navigation_theme(theme_colors)
            
            # Update title theme
            title_label = self.ui_manager.get_title_label()
            if title_label:
                self.ui_manager.update_title_theme(theme_colors)
            
            # Update menu bar styling
            menu_bar = self.menu_manager.get_menu_bar()
            if menu_bar:
                self.menu_manager.apply_menu_bar_styling(menu_bar)
            
        except Exception as e:
            logger.error(f"Error updating UI theme: {e}")
    
    def switch_to_panel(self, index: int):
        """Switch to a specific panel by index"""
        try:
            self.ui_manager.switch_to_tab(index)
            tab_widget = self.ui_manager.get_tab_widget()
            if tab_widget and 0 <= index < tab_widget.count():
                tab_text = tab_widget.tabText(index)
                self.status_manager.update_status_with_panel(tab_text)
                
                # Update menu button active state
                if hasattr(self.menu_manager, 'set_active_button'):
                    self.menu_manager.set_active_button(index)
                
                # Refresh the panel if it has a refresh method
                current_panel = tab_widget.currentWidget()
                if hasattr(current_panel, 'refresh'):
                    current_panel.refresh()
        except Exception as e:
            self.error_handler.handle_error(
                e,
                ErrorCategory.UI,
                ErrorSeverity.MEDIUM,
                f"Panel Switch: {index}",
                False,
                self
            )
    
    def show_settings(self):
        """Show settings dialog"""
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Settings")
            dialog.setModal(True)
            dialog.setMinimumSize(800, 600)
            
            # Layout for the dialog
            layout = QVBoxLayout(dialog)
            
            # Create a new settings panel for this dialog
            settings_panel = SettingsPanel(self, self)
            
            # Connect theme change signal to main app
            settings_panel.theme_changed.connect(self._on_theme_changed)
            
            # Add the settings panel to the dialog
            layout.addWidget(settings_panel)
            
            # Add OK/Cancel buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            # Show the dialog
            dialog.exec()
            
        except Exception as e:
            self.error_handler.handle_error(
                e,
                ErrorCategory.UI,
                ErrorSeverity.HIGH,
                "Settings Dialog",
                True,
                self
            )
    
    def _on_theme_changed(self, theme_id: str):
        """Handle theme change from settings"""
        try:
            logger.info(f"Theme change requested: {theme_id}")
            success = self.theme_manager.apply_theme(theme_id)
            
            if success:
                self.status_manager.update_status_with_theme(theme_id, True)
                self._update_ui_theme()
            else:
                self.status_manager.update_status_with_theme(theme_id, False)
                QMessageBox.warning(self, "Theme Error", "Failed to apply theme. Please check theme configuration.")
                
        except Exception as e:
            self.error_handler.handle_error(
                e,
                ErrorCategory.THEME,
                ErrorSeverity.HIGH,
                f"Theme Change: {theme_id}",
                True,
                self
            )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About CeliacShield", 
                         "CeliacShield - Celiac Disease Management Application\n\n"
                         "Built with PySide6\n"
                         "Version 1.0\n\n"
                         "Features:\n"
                         "• Pantry Management\n"
                         "• Health Logging\n"
                         "• Recipe Management\n"
                         "• Shopping Lists\n"
                         "• Menu Planning\n"
                         "• Calendar Integration\n"
                         "• Data Import/Export")
    
    def closeEvent(self, event):
        """Handle application close event"""
        reply = QMessageBox.question(self, 'Exit Application', 
                                   'Are you sure you want to exit?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Clean up resources
            self.database_manager.close_connection()
            event.accept()
        else:
            event.ignore()
    
    # Properties for backward compatibility
    @property
    def db(self):
        """Get database connection for backward compatibility"""
        return self.database_manager.get_connection_ref()
    
    @property
    def status_var(self):
        """Get current status for backward compatibility"""
        return self.status_manager.get_current_status()
    
    @status_var.setter
    def status_var(self, value: str):
        """Set status for backward compatibility"""
        self.status_manager.update_status(value)
