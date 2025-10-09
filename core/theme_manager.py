#!/usr/bin/env python3
"""
Theme Manager for Celiogix Application

Handles all theme-related operations including application, navigation updates,
and fallback mechanisms.
"""

import logging
from typing import Optional, Dict, Any, Callable
from PySide6.QtWidgets import QApplication, QWidget, QMenuBar, QStatusBar
from PySide6.QtCore import QObject, Signal, QTimer

# Import error handling
from utils.error_handler import handle_error, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class ThemeManager(QObject):
    """Centralized theme management for the application"""
    
    # Signals
    theme_applied = Signal(str)  # theme_id
    theme_error = Signal(str)  # error_message
    fallback_applied = Signal(str)  # fallback_theme_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._theme_creator = None
        self._fallback_theme = "celiac_safe"
        self._current_theme = None
        self._setup_theme_creator()
    
    def _setup_theme_creator(self):
        """Initialize theme creator service"""
        try:
            from services.theme_creator import theme_creator
            self._theme_creator = theme_creator
        except ImportError as e:
            logger.warning(f"Could not import theme creator: {e}")
            self._theme_creator = None
    
    def apply_theme(self, theme_id: str, app: Optional[QApplication] = None) -> bool:
        """
        Apply a theme to the application
        
        Args:
            theme_id: ID of the theme to apply
            app: QApplication instance (if None, uses current instance)
            
        Returns:
            bool: True if theme was applied successfully
        """
        if not app:
            app = QApplication.instance()
        
        if not app:
            logger.error("No QApplication instance available")
            self.theme_error.emit("No QApplication instance available")
            return False
        
        try:
            if self._theme_creator:
                result = self._theme_creator.apply_theme(theme_id, app)
                if result:
                    self._current_theme = theme_id
                    self.theme_applied.emit(theme_id)
                    logger.info(f"Successfully applied theme: {theme_id}")
                    return True
                else:
                    logger.warning(f"Failed to apply theme {theme_id}, trying fallback")
                    return self._apply_fallback_theme(app)
            else:
                logger.warning("Theme creator not available, applying fallback")
                return self._apply_fallback_theme(app)
                
        except Exception as e:
            handle_error(
                e,
                ErrorCategory.THEME,
                ErrorSeverity.HIGH,
                f"Theme Application: {theme_id}",
                False,
                None
            )
            self.theme_error.emit(str(e))
            return self._apply_fallback_theme(app)
    
    def _apply_fallback_theme(self, app: QApplication) -> bool:
        """Apply fallback theme when primary theme fails"""
        try:
            if self._theme_creator:
                result = self._theme_creator.apply_theme(self._fallback_theme, app)
                if result:
                    self._current_theme = self._fallback_theme
                    self.fallback_applied.emit(self._fallback_theme)
                    logger.info(f"Applied fallback theme: {self._fallback_theme}")
                    return True
            
            # Ultimate fallback to basic styling
            app.setStyle('Fusion')
            self.fallback_applied.emit("fusion")
            logger.info("Applied ultimate fallback: Fusion style")
            return True
            
        except Exception as e:
            handle_error(
                e,
                ErrorCategory.THEME,
                ErrorSeverity.CRITICAL,
                "Fallback Theme Application",
                True,  # Show to user since this is critical
                None
            )
            self.theme_error.emit(f"Fallback theme failed: {e}")
            return False
    
    def apply_saved_theme(self, app: Optional[QApplication] = None) -> bool:
        """
        Apply the saved theme or default theme
        
        Returns:
            bool: True if theme was applied successfully
        """
        if not self._theme_creator:
            return self._apply_fallback_theme(app or QApplication.instance())
        
        try:
            saved_theme = self._theme_creator.current_theme or self._fallback_theme
            return self.apply_theme(saved_theme, app)
        except Exception as e:
            logger.error(f"Error applying saved theme: {e}")
            return self._apply_fallback_theme(app or QApplication.instance())
    
    def update_navigation_theme(self, nav_widget: QWidget, title_label: Optional[QWidget] = None) -> bool:
        """
        Update navigation widget and title label to match current theme
        
        Args:
            nav_widget: Navigation widget to update
            title_label: Optional title label to update
            
        Returns:
            bool: True if update was successful
        """
        if not self._theme_creator or not self._current_theme:
            logger.warning("No theme creator or current theme available")
            return False
        
        try:
            theme_data = self._theme_creator.load_theme(self._current_theme)
            if not theme_data:
                logger.warning(f"Could not load theme data for {self._current_theme}")
                return False
            
            colors = theme_data.get('colors', {})
            header_bg = colors.get('background', '#fafafa')
            border_color = (colors.get('border_color') or 
                          colors.get('border') or 
                          colors.get('surface_variant') or 
                          '#c8e6c9')
            text_color = colors.get('text_primary', '#212121')
            
            # Update navigation widget
            nav_style = f"""
                QWidget {{
                    background-color: {header_bg};
                    border-bottom: 1px solid {border_color};
                }}
            """
            nav_widget.setStyleSheet(nav_style)
            
            # Update title label if provided
            if title_label:
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
                title_label.setStyleSheet(title_style)
            
            logger.debug(f"Updated navigation theme with background: {header_bg}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating navigation theme: {e}")
            return False
    
    def get_current_theme(self) -> Optional[str]:
        """Get the currently applied theme ID"""
        return self._current_theme
    
    def get_theme_colors(self, theme_id: Optional[str] = None) -> Dict[str, str]:
        """
        Get color palette for a theme
        
        Args:
            theme_id: Theme ID (if None, uses current theme)
            
        Returns:
            Dict of color values
        """
        if not theme_id:
            theme_id = self._current_theme
        
        if not theme_id or not self._theme_creator:
            return {}
        
        try:
            theme_data = self._theme_creator.load_theme(theme_id)
            return theme_data.get('colors', {}) if theme_data else {}
        except Exception as e:
            logger.error(f"Error getting theme colors for {theme_id}: {e}")
            return {}
    
    def set_fallback_theme(self, theme_id: str):
        """Set the fallback theme ID"""
        self._fallback_theme = theme_id
    
    def get_fallback_theme(self) -> str:
        """Get the current fallback theme ID"""
        return self._fallback_theme


# Global theme manager instance
_theme_manager = None


def get_theme_manager() -> ThemeManager:
    """Get global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
