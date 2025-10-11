#!/usr/bin/env python3
"""
Status Manager for CeliacShield Application

Handles status messages, logging, and application state management.
"""

import logging
from typing import Optional, Dict, Any
from PySide6.QtWidgets import QStatusBar
from PySide6.QtCore import QObject, Signal

# Import error handling
from utils.error_handler import handle_error, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class StatusManager(QObject):
    """Manages application status messages and state"""
    
    # Signals
    status_changed = Signal(str)  # status_message
    error_occurred = Signal(str)  # error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_status = "Ready"
        self._status_bar = None
        self._status_history = []
        self._max_history = 100
    
    def set_status_bar(self, status_bar: QStatusBar):
        """
        Set the status bar widget
        
        Args:
            status_bar: QStatusBar widget to update
        """
        self._status_bar = status_bar
    
    def update_status(self, message: str, log_level: str = "info"):
        """
        Update the status message
        
        Args:
            message: Status message
            log_level: Log level (info, warning, error, debug)
        """
        self._current_status = message
        self.status_changed.emit(message)
        
        # Add to history
        self._status_history.append(message)
        if len(self._status_history) > self._max_history:
            self._status_history.pop(0)
        
        # Log the message
        log_method = getattr(logger, log_level, logger.info)
        log_method(f"Status: {message}")
        
        # Update status bar if available
        if self._status_bar:
            self._status_bar.showMessage(message)
    
    def update_status_with_theme(self, theme_id: str, success: bool = True):
        """
        Update status with theme application result
        
        Args:
            theme_id: Theme ID that was applied
            success: Whether theme application was successful
        """
        if success:
            self.update_status(f"Applied theme: {theme_id}")
        else:
            self.update_status(f"Failed to apply theme: {theme_id}", "error")
            self.error_occurred.emit(f"Failed to apply theme: {theme_id}")
    
    def update_status_with_database(self, success: bool = True):
        """
        Update status with database operation result
        
        Args:
            success: Whether database operation was successful
        """
        if success:
            self.update_status("Database initialized")
        else:
            self.update_status("Database error", "error")
            self.error_occurred.emit("Database initialization failed")
    
    def update_status_with_panel(self, panel_name: str):
        """
        Update status when switching panels
        
        Args:
            panel_name: Name of the panel being switched to
        """
        self.update_status(f"Switched to {panel_name}")
    
    def set_error_status(self, error_message: str, context: str = ""):
        """
        Set error status message
        
        Args:
            error_message: Error message
            context: Additional context information
        """
        full_message = f"{context}: {error_message}" if context else error_message
        self.update_status(f"Error: {full_message}", "error")
        self.error_occurred.emit(full_message)
    
    def clear_status(self):
        """Clear the current status message"""
        self.update_status("Ready")
    
    def get_current_status(self) -> str:
        """Get the current status message"""
        return self._current_status
    
    def get_status_history(self) -> list:
        """Get the status message history"""
        return self._status_history.copy()
    
    def get_status_bar(self) -> Optional[QStatusBar]:
        """Get the status bar widget"""
        return self._status_bar


# Global status manager instance
_status_manager = None


def get_status_manager() -> StatusManager:
    """Get global status manager instance"""
    global _status_manager
    if _status_manager is None:
        _status_manager = StatusManager()
    return _status_manager
