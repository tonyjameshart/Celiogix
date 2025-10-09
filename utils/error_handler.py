#!/usr/bin/env python3
"""
Error handling utilities for Celiogix application

Provides centralized error handling, logging, and user notification.
"""

import logging
import traceback
from typing import Optional, Dict, Any, Callable
from enum import Enum
from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    UI = "ui"
    DATABASE = "database"
    THEME = "theme"
    NETWORK = "network"
    VALIDATION = "validation"
    FILE_IO = "file_io"
    GENERAL = "general"


class ErrorHandler(QObject):
    """Centralized error handler for the application"""
    
    # Signals
    error_occurred = Signal(str, str, str)  # category, severity, message
    error_resolved = Signal(str)  # error_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_history = []
        self.max_history = 100
    
    def handle_error(self, 
                    error: Exception, 
                    category: ErrorCategory = ErrorCategory.GENERAL,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    context: str = "",
                    show_to_user: bool = True,
                    parent_widget: Optional[QWidget] = None) -> str:
        """
        Handle an error with centralized logging and user notification
        
        Args:
            error: The exception that occurred
            category: Category of the error
            severity: Severity level of the error
            context: Additional context information
            show_to_user: Whether to show error to user
            parent_widget: Parent widget for message boxes
            
        Returns:
            str: Error ID for tracking
        """
        error_id = f"{category.value}_{len(self.error_history)}"
        error_message = str(error)
        full_context = f"{context}: {error_message}" if context else error_message
        
        # Log the error
        self._log_error(error, category, severity, full_context)
        
        # Add to history
        error_info = {
            'id': error_id,
            'category': category.value,
            'severity': severity.value,
            'message': error_message,
            'context': context,
            'traceback': traceback.format_exc()
        }
        self.error_history.append(error_info)
        
        # Trim history if too long
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # Emit signal
        self.error_occurred.emit(category.value, severity.value, error_message)
        
        # Show to user if requested
        if show_to_user:
            self._show_error_to_user(error_message, context, severity, parent_widget)
        
        return error_id
    
    def _log_error(self, error: Exception, category: ErrorCategory, 
                   severity: ErrorSeverity, context: str):
        """Log error with appropriate level"""
        log_message = f"[{category.value.upper()}] {context}"
        
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=True)
        elif severity == ErrorSeverity.HIGH:
            logger.error(log_message, exc_info=True)
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:  # LOW
            logger.info(log_message)
    
    def _show_error_to_user(self, error_message: str, context: str, 
                           severity: ErrorSeverity, parent_widget: Optional[QWidget]):
        """Show error to user with appropriate message box"""
        if not parent_widget:
            return
        
        title = "Error"
        if severity == ErrorSeverity.CRITICAL:
            title = "Critical Error"
            icon = QMessageBox.Critical
        elif severity == ErrorSeverity.HIGH:
            title = "Error"
            icon = QMessageBox.Warning
        elif severity == ErrorSeverity.MEDIUM:
            title = "Warning"
            icon = QMessageBox.Warning
        else:  # LOW
            title = "Information"
            icon = QMessageBox.Information
        
        full_message = f"{context}: {error_message}" if context else error_message
        
        msg_box = QMessageBox(parent_widget)
        msg_box.setWindowTitle(title)
        msg_box.setText(full_message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def get_error_history(self, category: Optional[ErrorCategory] = None, 
                         severity: Optional[ErrorSeverity] = None) -> list:
        """Get filtered error history"""
        filtered_history = self.error_history.copy()
        
        if category:
            filtered_history = [e for e in filtered_history if e['category'] == category.value]
        
        if severity:
            filtered_history = [e for e in filtered_history if e['severity'] == severity.value]
        
        return filtered_history
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        if not self.error_history:
            return {'total': 0, 'by_category': {}, 'by_severity': {}}
        
        stats = {
            'total': len(self.error_history),
            'by_category': {},
            'by_severity': {}
        }
        
        for error in self.error_history:
            category = error['category']
            severity = error['severity']
            
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
        
        return stats


# Global error handler instance
_error_handler = None


def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_error(error: Exception, 
                category: ErrorCategory = ErrorCategory.GENERAL,
                severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                context: str = "",
                show_to_user: bool = True,
                parent_widget: Optional[QWidget] = None) -> str:
    """
    Convenience function to handle errors using global error handler
    
    Returns:
        str: Error ID for tracking
    """
    return get_error_handler().handle_error(
        error, category, severity, context, show_to_user, parent_widget
    )


def safe_execute(func: Callable, 
                category: ErrorCategory = ErrorCategory.GENERAL,
                severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                context: str = "",
                show_to_user: bool = False,
                parent_widget: Optional[QWidget] = None,
                default_return=None):
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        category: Error category if function fails
        severity: Error severity if function fails
        context: Context for error messages
        show_to_user: Whether to show errors to user
        parent_widget: Parent widget for error dialogs
        default_return: Value to return if function fails
        
    Returns:
        Result of function or default_return if error occurred
    """
    try:
        return func()
    except Exception as e:
        handle_error(e, category, severity, context, show_to_user, parent_widget)
        return default_return
