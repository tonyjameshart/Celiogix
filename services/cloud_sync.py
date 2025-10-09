#!/usr/bin/env python3
"""
Cloud synchronization service for data backup and multi-device access
"""

import json
import hashlib
import requests
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtWidgets import QMessageBox

from utils.encryption import get_general_encryption
from utils.error_handling import handle_error, ErrorCategory, ErrorSeverity


class SyncStatus(Enum):
    """Sync status enumeration"""
    IDLE = "idle"
    SYNCING = "syncing"
    SUCCESS = "success"
    ERROR = "error"
    CONFLICT = "conflict"


@dataclass
class SyncItem:
    """Sync item data structure"""
    id: str
    type: str  # 'recipe', 'health_log', 'pantry', etc.
    data: Dict[str, Any]
    timestamp: datetime
    checksum: str
    device_id: str
    version: int = 1


@dataclass
class SyncConflict:
    """Sync conflict data structure"""
    item_id: str
    local_item: SyncItem
    remote_item: SyncItem
    conflict_type: str  # 'data', 'version', 'timestamp'


class CloudSyncService(QObject):
    """Cloud synchronization service"""
    
    # Signals
    sync_started = Signal()
    sync_progress = Signal(int)  # Progress percentage
    sync_finished = Signal(SyncStatus)
    sync_error = Signal(str)
    conflict_detected = Signal(SyncConflict)
    
    def __init__(self, api_base_url: str = "https://api.celiogix.com", parent=None):
        super().__init__(parent)
        self.api_base_url = api_base_url
        self.api_key = None
        self.device_id = self._generate_device_id()
        self.sync_status = SyncStatus.IDLE
        self.encryption = get_general_encryption()
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.auto_sync)
        self.auto_sync_enabled = False
        self.auto_sync_interval = 300  # 5 minutes
        
        # Sync settings
        self.sync_enabled = False
        self.sync_recipes = True
        self.sync_health_logs = True
        self.sync_pantry = True
        self.sync_calendar = True
        
        # Local sync data
        self.local_sync_data = {}
        self.remote_sync_data = {}
        self.pending_conflicts = []
    
    def _generate_device_id(self) -> str:
        """Generate unique device ID"""
        import platform
        import uuid
        
        system_info = f"{platform.node()}{platform.system()}{platform.machine()}"
        return hashlib.sha256(system_info.encode()).hexdigest()[:16]
    
    def set_api_key(self, api_key: str):
        """Set API key for authentication"""
        self.api_key = api_key
        self.sync_enabled = True
    
    def enable_auto_sync(self, interval_minutes: int = 5):
        """Enable automatic synchronization"""
        self.auto_sync_enabled = True
        self.auto_sync_interval = interval_minutes * 60 * 1000  # Convert to milliseconds
        self.sync_timer.start(self.auto_sync_interval)
    
    def disable_auto_sync(self):
        """Disable automatic synchronization"""
        self.auto_sync_enabled = False
        self.sync_timer.stop()
    
    def set_sync_settings(self, recipes: bool = True, health_logs: bool = True, 
                         pantry: bool = True, calendar: bool = True):
        """Set what data to sync"""
        self.sync_recipes = recipes
        self.sync_health_logs = health_logs
        self.sync_pantry = pantry
        self.sync_calendar = calendar
    
    def sync_data(self, force: bool = False) -> bool:
        """
        Synchronize data with cloud
        
        Args:
            force: Force sync even if no changes detected
            
        Returns:
            True if sync started successfully
        """
        if not self.sync_enabled or not self.api_key:
            self.sync_error.emit("Sync not enabled or API key not set")
            return False
        
        if self.sync_status == SyncStatus.SYNCING:
            self.sync_error.emit("Sync already in progress")
            return False
        
        # Start sync in background thread
        self.sync_worker = SyncWorker(self)
        self.sync_worker.sync_started.connect(self.sync_started.emit)
        self.sync_worker.sync_progress.connect(self.sync_progress.emit)
        self.sync_worker.sync_finished.connect(self._on_sync_finished)
        self.sync_worker.sync_error.connect(self.sync_error.emit)
        self.sync_worker.conflict_detected.connect(self.conflict_detected.emit)
        
        self.sync_worker.start()
        return True
    
    def _on_sync_finished(self, status: SyncStatus):
        """Handle sync finished"""
        self.sync_status = status
        self.sync_finished.emit(status)
    
    def auto_sync(self):
        """Automatic sync trigger"""
        if self.sync_enabled and self.sync_status == SyncStatus.IDLE:
            self.sync_data()
    
    def upload_data(self, data_type: str, data: Dict[str, Any]) -> bool:
        """
        Upload data to cloud
        
        Args:
            data_type: Type of data ('recipe', 'health_log', etc.)
            data: Data to upload
            
        Returns:
            True if upload successful
        """
        try:
            # Create sync item
            sync_item = self._create_sync_item(data_type, data)
            
            # Encrypt sensitive data
            if data_type in ['health_log', 'pantry']:
                sync_item.data = self.encryption.encrypt_dict(sync_item.data)
            
            # Upload to cloud
            response = self._make_api_request('POST', '/sync/upload', {
                'item': sync_item.__dict__
            })
            
            if response and response.get('success'):
                # Update local sync data
                self.local_sync_data[sync_item.id] = sync_item
                return True
            
        except Exception as e:
            handle_error(
                e, ErrorCategory.NETWORK, ErrorSeverity.MEDIUM,
                context={'operation': 'upload_data', 'data_type': data_type}
            )
        
        return False
    
    def download_data(self, data_type: str, since: Optional[datetime] = None) -> List[SyncItem]:
        """
        Download data from cloud
        
        Args:
            data_type: Type of data to download
            since: Download changes since this timestamp
            
        Returns:
            List of sync items
        """
        try:
            params = {'type': data_type}
            if since:
                params['since'] = since.isoformat()
            
            response = self._make_api_request('GET', '/sync/download', params)
            
            if response and response.get('success'):
                items = []
                for item_data in response.get('items', []):
                    sync_item = SyncItem(**item_data)
                    
                    # Decrypt sensitive data
                    if data_type in ['health_log', 'pantry']:
                        sync_item.data = self.encryption.decrypt_dict(sync_item.data)
                    
                    items.append(sync_item)
                
                return items
            
        except Exception as e:
            handle_error(
                e, ErrorCategory.NETWORK, ErrorSeverity.MEDIUM,
                context={'operation': 'download_data', 'data_type': data_type}
            )
        
        return []
    
    def resolve_conflict(self, conflict: SyncConflict, resolution: str) -> bool:
        """
        Resolve sync conflict
        
        Args:
            conflict: Conflict to resolve
            resolution: Resolution choice ('local', 'remote', 'merge')
            
        Returns:
            True if resolution successful
        """
        try:
            if resolution == 'local':
                # Use local version
                sync_item = conflict.local_item
            elif resolution == 'remote':
                # Use remote version
                sync_item = conflict.remote_item
            elif resolution == 'merge':
                # Merge versions (implement merge logic)
                sync_item = self._merge_items(conflict.local_item, conflict.remote_item)
            else:
                return False
            
            # Upload resolved item
            response = self._make_api_request('POST', '/sync/resolve', {
                'item': sync_item.__dict__,
                'conflict_id': conflict.item_id
            })
            
            if response and response.get('success'):
                # Remove from pending conflicts
                self.pending_conflicts = [
                    c for c in self.pending_conflicts if c.item_id != conflict.item_id
                ]
                return True
            
        except Exception as e:
            handle_error(
                e, ErrorCategory.NETWORK, ErrorSeverity.MEDIUM,
                context={'operation': 'resolve_conflict', 'conflict_id': conflict.item_id}
            )
        
        return False
    
    def _create_sync_item(self, data_type: str, data: Dict[str, Any]) -> SyncItem:
        """Create sync item from data"""
        item_id = hashlib.sha256(
            f"{data_type}{json.dumps(data, sort_keys=True)}".encode()
        ).hexdigest()
        
        checksum = hashlib.md5(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
        
        return SyncItem(
            id=item_id,
            type=data_type,
            data=data,
            timestamp=datetime.now(),
            checksum=checksum,
            device_id=self.device_id
        )
    
    def _merge_items(self, local_item: SyncItem, remote_item: SyncItem) -> SyncItem:
        """Merge two sync items"""
        # Simple merge strategy - use newer timestamp
        if local_item.timestamp > remote_item.timestamp:
            merged_item = local_item
        else:
            merged_item = remote_item
        
        # Increment version
        merged_item.version = max(local_item.version, remote_item.version) + 1
        merged_item.timestamp = datetime.now()
        
        return merged_item
    
    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request to cloud service"""
        try:
            url = f"{self.api_base_url}{endpoint}"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-Device-ID': self.device_id
            }
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=data, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            handle_error(
                e, ErrorCategory.NETWORK, ErrorSeverity.MEDIUM,
                context={'operation': 'api_request', 'method': method, 'endpoint': endpoint}
            )
            return None
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get sync status information"""
        return {
            'status': self.sync_status.value,
            'auto_sync_enabled': self.auto_sync_enabled,
            'sync_enabled': self.sync_enabled,
            'device_id': self.device_id,
            'pending_conflicts': len(self.pending_conflicts),
            'last_sync': getattr(self, 'last_sync_time', None)
        }
    
    def backup_data(self) -> bool:
        """Create backup of all data"""
        try:
            backup_data = {
                'recipes': self._get_local_data('recipes'),
                'health_logs': self._get_local_data('health_logs'),
                'pantry': self._get_local_data('pantry'),
                'calendar': self._get_local_data('calendar'),
                'backup_timestamp': datetime.now().isoformat(),
                'device_id': self.device_id
            }
            
            # Encrypt backup
            encrypted_backup = self.encryption.encrypt_string(json.dumps(backup_data))
            
            # Upload backup
            response = self._make_api_request('POST', '/backup/create', {
                'backup_data': encrypted_backup
            })
            
            return response and response.get('success')
            
        except Exception as e:
            handle_error(
                e, ErrorCategory.NETWORK, ErrorSeverity.MEDIUM,
                context={'operation': 'backup_data'}
            )
            return False
    
    def restore_data(self, backup_id: str) -> bool:
        """Restore data from backup"""
        try:
            response = self._make_api_request('GET', f'/backup/{backup_id}')
            
            if response and response.get('success'):
                backup_data = json.loads(
                    self.encryption.decrypt_string(response['backup_data'])
                )
                
                # Restore data to local database
                self._restore_local_data(backup_data)
                return True
            
        except Exception as e:
            handle_error(
                e, ErrorCategory.NETWORK, ErrorSeverity.MEDIUM,
                context={'operation': 'restore_data', 'backup_id': backup_id}
            )
        
        return False
    
    def _get_local_data(self, data_type: str) -> List[Dict[str, Any]]:
        """Get local data for sync"""
        # This would integrate with the database to get actual data
        # For now, return empty list
        return []
    
    def _restore_local_data(self, backup_data: Dict[str, Any]):
        """Restore data to local database"""
        # This would integrate with the database to restore data
        pass


class SyncWorker(QThread):
    """Background worker for sync operations"""
    
    # Signals
    sync_started = Signal()
    sync_progress = Signal(int)
    sync_finished = Signal(SyncStatus)
    sync_error = Signal(str)
    conflict_detected = Signal(SyncConflict)
    
    def __init__(self, sync_service: CloudSyncService):
        super().__init__()
        self.sync_service = sync_service
    
    def run(self):
        """Run sync operation"""
        try:
            self.sync_started.emit()
            self.sync_progress.emit(0)
            
            # Check for conflicts
            conflicts = self._check_conflicts()
            if conflicts:
                for conflict in conflicts:
                    self.conflict_detected.emit(conflict)
                self.sync_finished.emit(SyncStatus.CONFLICT)
                return
            
            # Upload local changes
            self.sync_progress.emit(25)
            self._upload_changes()
            
            # Download remote changes
            self.sync_progress.emit(50)
            self._download_changes()
            
            # Apply changes
            self.sync_progress.emit(75)
            self._apply_changes()
            
            self.sync_progress.emit(100)
            self.sync_finished.emit(SyncStatus.SUCCESS)
            
        except Exception as e:
            self.sync_error.emit(str(e))
            self.sync_finished.emit(SyncStatus.ERROR)
    
    def _check_conflicts(self) -> List[SyncConflict]:
        """Check for sync conflicts"""
        conflicts = []
        
        # Check each data type for conflicts
        for data_type in ['recipes', 'health_logs', 'pantry', 'calendar']:
            if getattr(self.sync_service, f'sync_{data_type}', False):
                # Get local and remote items
                local_items = self.sync_service._get_local_data(data_type)
                remote_items = self.sync_service.download_data(data_type)
                
                # Check for conflicts
                for local_item in local_items:
                    for remote_item in remote_items:
                        if local_item['id'] == remote_item.id:
                            if local_item['checksum'] != remote_item.checksum:
                                conflict = SyncConflict(
                                    item_id=local_item['id'],
                                    local_item=local_item,
                                    remote_item=remote_item,
                                    conflict_type='data'
                                )
                                conflicts.append(conflict)
        
        return conflicts
    
    def _upload_changes(self):
        """Upload local changes to cloud"""
        for data_type in ['recipes', 'health_logs', 'pantry', 'calendar']:
            if getattr(self.sync_service, f'sync_{data_type}', False):
                local_data = self.sync_service._get_local_data(data_type)
                for item in local_data:
                    self.sync_service.upload_data(data_type, item)
    
    def _download_changes(self):
        """Download remote changes from cloud"""
        for data_type in ['recipes', 'health_logs', 'pantry', 'calendar']:
            if getattr(self.sync_service, f'sync_{data_type}', False):
                remote_items = self.sync_service.download_data(data_type)
                self.sync_service.remote_sync_data[data_type] = remote_items
    
    def _apply_changes(self):
        """Apply downloaded changes to local database"""
        # This would integrate with the database to apply changes
        pass


# Global cloud sync service instance
_cloud_sync_service = None


def get_cloud_sync_service() -> CloudSyncService:
    """Get global cloud sync service"""
    global _cloud_sync_service
    if _cloud_sync_service is None:
        _cloud_sync_service = CloudSyncService()
    return _cloud_sync_service


def setup_cloud_sync(api_key: str, enable_auto_sync: bool = True):
    """Set up cloud sync service"""
    service = get_cloud_sync_service()
    service.set_api_key(api_key)
    
    if enable_auto_sync:
        service.enable_auto_sync()
    
    return service
