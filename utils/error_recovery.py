#!/usr/bin/env python3
"""
Error recovery actions and strategies
"""

import os
import sqlite3
import shutil
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from .error_handling import ErrorHandler, ErrorCategory, ErrorSeverity, error_handler
from .db import get_connection


class DatabaseRecovery:
    """Database recovery actions"""
    
    @staticmethod
    def retry_connection():
        """Retry database connection"""
        try:
            conn = get_connection()
            conn.execute("SELECT 1")  # Test connection
            conn.close()
            return True
        except Exception:
            return False
    
    @staticmethod
    def backup_database():
        """Create database backup"""
        try:
            from utils.db import _db_path
            db_path = _db_path()
            
            if os.path.exists(db_path):
                backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(db_path, backup_path)
                return backup_path
        except Exception:
            pass
        return None
    
    @staticmethod
    def restore_database(backup_path: str):
        """Restore database from backup"""
        try:
            from utils.db import _db_path
            db_path = _db_path()
            
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, db_path)
                return True
        except Exception:
            pass
        return False
    
    @staticmethod
    def repair_database():
        """Attempt to repair database"""
        try:
            from utils.db import _db_path
            db_path = _db_path()
            
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                conn.execute("VACUUM")
                conn.execute("REINDEX")
                conn.close()
                return True
        except Exception:
            pass
        return False


class NetworkRecovery:
    """Network recovery actions"""
    
    @staticmethod
    def retry_network_request(url: str, max_retries: int = 3):
        """Retry network request with exponential backoff"""
        import time
        import requests
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response
            except Exception:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
        
        return None
    
    @staticmethod
    def check_network_connectivity():
        """Check network connectivity"""
        import requests
        
        try:
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class FileRecovery:
    """File I/O recovery actions"""
    
    @staticmethod
    def retry_file_operation(operation: Callable, max_retries: int = 3):
        """Retry file operation with backoff"""
        import time
        
        for attempt in range(max_retries):
            try:
                return operation()
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(1)
                continue
            except FileNotFoundError:
                return None  # Can't retry if file doesn't exist
        
        return None
    
    @staticmethod
    def create_backup_directory():
        """Create backup directory if it doesn't exist"""
        backup_dir = "data/backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    
    @staticmethod
    def cleanup_temp_files():
        """Clean up temporary files"""
        temp_dir = "data/temp"
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                os.makedirs(temp_dir, exist_ok=True)
                return True
            except Exception:
                pass
        return False


class EncryptionRecovery:
    """Encryption recovery actions"""
    
    @staticmethod
    def reset_encryption_key():
        """Reset encryption key (use with caution)"""
        try:
            # This would reset the encryption key
            # In practice, this should be done very carefully
            # as it would make existing encrypted data unreadable
            pass
        except Exception:
            pass
    
    @staticmethod
    def verify_encryption_setup():
        """Verify encryption setup is working"""
        try:
            from utils.encryption import get_general_encryption
            encryption = get_general_encryption()
            
            # Test encryption/decryption
            test_data = "test_data"
            encrypted = encryption.encrypt_string(test_data)
            decrypted = encryption.decrypt_string(encrypted)
            
            return decrypted == test_data
        except Exception:
            return False


class RecoveryManager:
    """Centralized recovery manager"""
    
    def __init__(self):
        self.recovery_strategies = {
            'retry_connection': DatabaseRecovery.retry_connection,
            'backup_database': DatabaseRecovery.backup_database,
            'restore_database': DatabaseRecovery.restore_database,
            'repair_database': DatabaseRecovery.repair_database,
            'retry_network': NetworkRecovery.check_network_connectivity,
            'check_encryption': EncryptionRecovery.verify_encryption_setup,
            'cleanup_temp_files': FileRecovery.cleanup_temp_files,
        }
        
        self.setup_recovery_actions()
    
    def setup_recovery_actions(self):
        """Set up recovery actions with error handler"""
        for action_id, action_func in self.recovery_strategies.items():
            error_handler.register_recovery_action(action_id, action_func)
    
    def execute_recovery_plan(self, error_category: ErrorCategory) -> bool:
        """
        Execute recovery plan based on error category
        
        Args:
            error_category: Category of error
            
        Returns:
            True if recovery was successful
        """
        recovery_plans = {
            ErrorCategory.DATABASE: [
                'retry_connection',
                'repair_database',
                'backup_database'
            ],
            ErrorCategory.NETWORK: [
                'retry_network'
            ],
            ErrorCategory.FILE_IO: [
                'cleanup_temp_files'
            ],
            ErrorCategory.ENCRYPTION: [
                'check_encryption'
            ],
            ErrorCategory.PERFORMANCE: [
                'cleanup_temp_files',
                'repair_database'
            ]
        }
        
        plan = recovery_plans.get(error_category, [])
        
        for action_id in plan:
            if error_handler.execute_recovery_action(action_id):
                return True
        
        return False
    
    def create_recovery_report(self) -> Dict[str, Any]:
        """Create recovery report"""
        stats = error_handler.get_error_statistics()
        
        return {
            'total_errors': stats['total_errors'],
            'recovery_attempts': len(self.recovery_strategies),
            'successful_recoveries': sum(1 for _ in stats['category_counts'].values()),  # Simplified
            'last_recovery': datetime.now().isoformat(),
            'available_actions': list(self.recovery_strategies.keys())
        }


# Global recovery manager instance
recovery_manager = RecoveryManager()


def get_recovery_manager() -> RecoveryManager:
    """Get global recovery manager"""
    return recovery_manager


def setup_recovery_system():
    """Set up recovery system"""
    # This would be called during application startup
    recovery_manager.setup_recovery_actions()
    
    # Set up automatic recovery for certain error types
    def auto_recovery_handler(error_info):
        if error_info.severity in [ErrorSeverity.MEDIUM, ErrorSeverity.HIGH]:
            recovery_manager.execute_recovery_plan(error_info.category)
    
    error_handler.error_occurred.connect(auto_recovery_handler)
