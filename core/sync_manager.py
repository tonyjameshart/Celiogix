"""Manages synchronization between desktop and mobile app."""

from typing import Dict, Any
from PySide6.QtCore import QObject, pyqtSignal
from services.bluetooth_sync import BluetoothSyncService


class SyncManager(QObject):
    """Coordinates data sync across all panels."""
    
    sync_status_changed = pyqtSignal(str, bool)  # panel, success
    
    def __init__(self):
        super().__init__()
        self.bluetooth_service = BluetoothSyncService()
        self.panels = ['pantry', 'cookbook', 'shopping_list', 'health_log', 'menu', 'calendar']
        self._setup_connections()
        
    def _setup_connections(self):
        """Connect Bluetooth service signals."""
        self.bluetooth_service.data_received.connect(self._handle_mobile_data)
        self.bluetooth_service.sync_complete.connect(self._on_sync_complete)
        
    def start_bluetooth_sync(self) -> bool:
        """Initialize Bluetooth sync service."""
        return self.bluetooth_service.start_server()
        
    def sync_panel_to_mobile(self, panel: str, data: Dict[str, Any]) -> bool:
        """Send panel data to mobile app."""
        if panel == 'settings':
            return False
        return self.bluetooth_service.send_to_mobile(panel, data)
        
    def _handle_mobile_data(self, panel: str, data: Dict[str, Any]):
        """Process data received from mobile app."""
        if panel in self.panels:
            # Emit signal for specific panel to update
            self.sync_status_changed.emit(panel, True)
            
    def _on_sync_complete(self, panel: str):
        """Handle sync completion."""
        self.sync_status_changed.emit(panel, True)