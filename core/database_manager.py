#!/usr/bin/env python3
"""
Database Manager for Celiogix Application

Handles database initialization, connections, and schema management.
"""

import logging
from typing import Optional
from contextlib import contextmanager

# Import error handling
from utils.error_handler import handle_error, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and initialization"""
    
    def __init__(self):
        self._connection = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize database connection and schema
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            from utils.db import get_connection
            from utils.migrations import ensure_schema
            from utils.settings import ensure_settings_table
            
            # Get database connection
            self._connection = get_connection()
            
            # Ensure schema is up to date
            ensure_schema(self._connection)
            
            # Ensure settings table exists
            ensure_settings_table(self._connection)
            
            self._initialized = True
            logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            handle_error(
                e,
                ErrorCategory.DATABASE,
                ErrorSeverity.CRITICAL,
                "Database Initialization",
                True,  # Show to user since this is critical
                None
            )
            self._connection = None
            self._initialized = False
            return False
    
    @contextmanager
    def get_connection(self):
        """
        Get database connection as context manager
        
        Yields:
            Database connection
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        try:
            yield self._connection
        except Exception as e:
            handle_error(
                e,
                ErrorCategory.DATABASE,
                ErrorSeverity.HIGH,
                "Database Operation",
                False,
                None
            )
            raise
    
    def get_connection_ref(self) -> Optional[object]:
        """
        Get direct reference to database connection
        
        Returns:
            Database connection or None if not initialized
        """
        return self._connection if self._initialized else None
    
    def is_initialized(self) -> bool:
        """
        Check if database is initialized
        
        Returns:
            bool: True if database is initialized
        """
        return self._initialized
    
    def close_connection(self):
        """Close database connection"""
        if self._connection:
            try:
                self._connection.close()
                logger.info("Database connection closed")
            except Exception as e:
                handle_error(
                    e,
                    ErrorCategory.DATABASE,
                    ErrorSeverity.MEDIUM,
                    "Database Connection Close",
                    False,
                    None
                )
            finally:
                self._connection = None
                self._initialized = False
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close_connection()


# Global database manager instance
_db_manager = None


def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
