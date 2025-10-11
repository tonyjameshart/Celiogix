#!/usr/bin/env python3
"""
Centralized error handling system
"""

import sys
import traceback
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import QObject, Signal, QTimer


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    DATABASE = "database"
    NETWORK = "network"
    UI = "ui"
    VALIDATION = "validation"
    SECURITY = "security"
    PERFORMANCE = "performance"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    FILE_IO = "file_io"
    ENCRYPTION = "encryption"


@dataclass
class ErrorInfo:
    """Error information container"""
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    timestamp: datetime
    traceback: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    user_message: Optional[str] = None
    recovery_action: Optional[str] = None


class ErrorHandler(QObject):
    """Centralized error handler"""
    
    # Signals
    error_occurred = Signal(ErrorInfo)
    error_resolved = Signal(ErrorInfo)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_log: List[ErrorInfo] = []
        self.error_handlers: Dict[ErrorCategory, Callable] = {}
        self.recovery_actions: Dict[str, Callable] = {}
        self.setup_logging()
        self.setup_default_handlers()
    
    def setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/error.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('CeliacShield')
    
    def setup_default_handlers(self):
        """Set up default error handlers"""
        self.error_handlers = {
            ErrorCategory.DATABASE: self._handle_database_error,
            ErrorCategory.NETWORK: self._handle_network_error,
            ErrorCategory.UI: self._handle_ui_error,
            ErrorCategory.VALIDATION: self._handle_validation_error,
            ErrorCategory.SECURITY: self._handle_security_error,
            ErrorCategory.PERFORMANCE: self._handle_performance_error,
            ErrorCategory.SYSTEM: self._handle_system_error,
            ErrorCategory.USER_INPUT: self._handle_user_input_error,
            ErrorCategory.FILE_IO: self._handle_file_io_error,
            ErrorCategory.ENCRYPTION: self._handle_encryption_error,
        }
    
    def handle_error(self, 
                    error: Union[Exception, str],
                    category: ErrorCategory,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    context: Optional[Dict[str, Any]] = None,
                    user_message: Optional[str] = None,
                    recovery_action: Optional[str] = None) -> ErrorInfo:
        """
        Handle an error
        
        Args:
            error: Exception or error message
            category: Error category
            severity: Error severity
            context: Additional context information
            user_message: User-friendly message
            recovery_action: Recovery action identifier
            
        Returns:
            ErrorInfo object
        """
        # Extract error information
        if isinstance(error, Exception):
            message = str(error)
            tb = traceback.format_exc()
        else:
            message = error
            tb = None
        
        # Create error info
        error_info = ErrorInfo(
            message=message,
            severity=severity,
            category=category,
            timestamp=datetime.now(),
            traceback=tb,
            context=context or {},
            user_message=user_message,
            recovery_action=recovery_action
        )
        
        # Log error
        self._log_error(error_info)
        
        # Store error
        self.error_log.append(error_info)
        
        # Handle based on category
        if category in self.error_handlers:
            self.error_handlers[category](error_info)
        
        # Emit signal
        self.error_occurred.emit(error_info)
        
        # Show user notification if needed
        self._notify_user(error_info)
        
        return error_info
    
    def _log_error(self, error_info: ErrorInfo):
        """Log error to file and console"""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error_info.severity, logging.ERROR)
        
        self.logger.log(
            log_level,
            f"[{error_info.category.value}] {error_info.message}",
            extra={'context': error_info.context, 'traceback': error_info.traceback}
        )
    
    def _notify_user(self, error_info: ErrorInfo):
        """Notify user of error"""
        if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self._show_error_dialog(error_info)
        elif error_info.user_message:
            # Show less intrusive notification
            self._show_notification(error_info.user_message)
    
    def _show_error_dialog(self, error_info: ErrorInfo):
        """Show error dialog to user"""
        message = error_info.user_message or error_info.message
        
        # Add recovery action if available
        if error_info.recovery_action:
            message += f"\n\nRecovery action: {error_info.recovery_action}"
        
        # Show appropriate message box
        if error_info.severity == ErrorSeverity.CRITICAL:
            QMessageBox.critical(None, "Critical Error", message)
        else:
            QMessageBox.warning(None, "Error", message)
    
    def _show_notification(self, message: str):
        """Show notification to user"""
        # This could be implemented with a toast notification
        print(f"NOTIFICATION: {message}")
    
    # Category-specific error handlers
    def _handle_database_error(self, error_info: ErrorInfo):
        """Handle database errors"""
        # Try to reconnect or show database error message
        if "connection" in error_info.message.lower():
            error_info.user_message = "Database connection lost. Please check your connection and try again."
            error_info.recovery_action = "retry_connection"
        elif "constraint" in error_info.message.lower():
            error_info.user_message = "Data validation error. Please check your input and try again."
        else:
            error_info.user_message = "Database error occurred. Please try again."
    
    def _handle_network_error(self, error_info: ErrorInfo):
        """Handle network errors"""
        error_info.user_message = "Network error occurred. Please check your internet connection."
        error_info.recovery_action = "retry_network"
    
    def _handle_ui_error(self, error_info: ErrorInfo):
        """Handle UI errors"""
        error_info.user_message = "Interface error occurred. Please restart the application."
        error_info.recovery_action = "restart_ui"
    
    def _handle_validation_error(self, error_info: ErrorInfo):
        """Handle validation errors"""
        error_info.user_message = "Please check your input and try again."
    
    def _handle_security_error(self, error_info: ErrorInfo):
        """Handle security errors"""
        error_info.user_message = "Security error occurred. Please contact support."
        error_info.recovery_action = "contact_support"
    
    def _handle_performance_error(self, error_info: ErrorInfo):
        """Handle performance errors"""
        error_info.user_message = "Performance issue detected. The application may be slow."
    
    def _handle_system_error(self, error_info: ErrorInfo):
        """Handle system errors"""
        error_info.user_message = "System error occurred. Please restart the application."
        error_info.recovery_action = "restart_application"
    
    def _handle_user_input_error(self, error_info: ErrorInfo):
        """Handle user input errors"""
        error_info.user_message = "Invalid input. Please check your data and try again."
    
    def _handle_file_io_error(self, error_info: ErrorInfo):
        """Handle file I/O errors"""
        if "permission" in error_info.message.lower():
            error_info.user_message = "Permission denied. Please check file permissions."
        elif "not found" in error_info.message.lower():
            error_info.user_message = "File not found. Please check the file path."
        else:
            error_info.user_message = "File operation failed. Please try again."
    
    def _handle_encryption_error(self, error_info: ErrorInfo):
        """Handle encryption errors"""
        error_info.user_message = "Encryption error occurred. Please check your security settings."
        error_info.recovery_action = "check_encryption"
    
    def register_recovery_action(self, action_id: str, action_func: Callable):
        """Register a recovery action"""
        self.recovery_actions[action_id] = action_func
    
    def execute_recovery_action(self, action_id: str) -> bool:
        """Execute a recovery action"""
        if action_id in self.recovery_actions:
            try:
                self.recovery_actions[action_id]()
                return True
            except Exception as e:
                self.handle_error(
                    f"Recovery action failed: {str(e)}",
                    ErrorCategory.SYSTEM,
                    ErrorSeverity.HIGH
                )
                return False
        return False
    
    def get_error_history(self, limit: Optional[int] = None) -> List[ErrorInfo]:
        """Get error history"""
        if limit:
            return self.error_log[-limit:]
        return self.error_log.copy()
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_log.clear()
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_errors = len(self.error_log)
        
        severity_counts = {}
        category_counts = {}
        
        for error in self.error_log:
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
        
        return {
            'total_errors': total_errors,
            'severity_counts': severity_counts,
            'category_counts': category_counts,
            'last_error': self.error_log[-1] if self.error_log else None
        }


class ErrorContext:
    """Context manager for error handling"""
    
    def __init__(self, 
                 category: ErrorCategory,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 context: Optional[Dict[str, Any]] = None):
        self.category = category
        self.severity = severity
        self.context = context or {}
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_handler.handle_error(
                exc_val,
                self.category,
                self.severity,
                self.context
            )
            return True  # Suppress exception


def handle_error(error: Union[Exception, str],
                category: ErrorCategory,
                severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                context: Optional[Dict[str, Any]] = None,
                user_message: Optional[str] = None,
                recovery_action: Optional[str] = None) -> ErrorInfo:
    """
    Convenience function to handle errors
    
    Args:
        error: Exception or error message
        category: Error category
        severity: Error severity
        context: Additional context
        user_message: User-friendly message
        recovery_action: Recovery action
        
    Returns:
        ErrorInfo object
    """
    return error_handler.handle_error(
        error, category, severity, context, user_message, recovery_action
    )


def error_context(category: ErrorCategory,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 context: Optional[Dict[str, Any]] = None):
    """
    Decorator for error context
    
    Args:
        category: Error category
        severity: Error severity
        context: Additional context
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with ErrorContext(category, severity, context):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Global error handler instance
error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get global error handler"""
    return error_handler


def setup_error_handling():
    """Set up error handling for the application"""
    # Set up global exception handler
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_handler.handle_error(
            exc_value,
            ErrorCategory.SYSTEM,
            ErrorSeverity.CRITICAL,
            {'exception_type': exc_type.__name__}
        )
    
    sys.excepthook = global_exception_handler
    
    # Set up Qt exception handler
    def qt_exception_handler(exc_type, exc_value, exc_traceback):
        error_handler.handle_error(
            exc_value,
            ErrorCategory.UI,
            ErrorSeverity.HIGH,
            {'exception_type': exc_type.__name__, 'source': 'qt'}
        )
    
    # Note: Qt exception handling would need to be set up differently
    # depending on the specific Qt version and setup
