"""Bluetooth synchronization service for mobile companion app."""

import json
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
import bluetooth
from PySide6.QtCore import QObject, pyqtSignal


@dataclass
class SyncData:
    """Data structure for sync operations."""
    panel: str
    action: str  # 'push' or 'pull'
    data: Dict[str, Any]


class BluetoothSyncService(QObject):
    """Handles Bluetooth communication with mobile app."""
    
    data_received = pyqtSignal(str, dict)  # panel, data
    sync_complete = pyqtSignal(str)  # panel
    
    def __init__(self):
        super().__init__()
        self.server_socket = None
        self.client_socket = None
        self.is_connected = False
        
    def start_server(self) -> bool:
        """Start Bluetooth server for mobile connections."""
        try:
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_socket.bind(("", bluetooth.PORT_ANY))
            self.server_socket.listen(1)
            return True
        except Exception:
            return False
    
    async def handle_sync_request(self, sync_data: SyncData) -> Dict[str, Any]:
        """Process sync request from mobile app."""
        if sync_data.panel == 'settings':
            return {'status': 'blocked', 'message': 'Settings sync disabled'}
            
        if sync_data.action == 'push':
            return await self._handle_push(sync_data.panel, sync_data.data)
        elif sync_data.action == 'pull':
            return await self._handle_pull(sync_data.panel)
            
    async def _handle_push(self, panel: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data push from mobile to desktop."""
        self.data_received.emit(panel, data)
        return {'status': 'success', 'panel': panel}
        
    async def _handle_pull(self, panel: str) -> Dict[str, Any]:
        """Handle data pull request from mobile."""
        # Request data from panel
        panel_data = self._get_panel_data(panel)
        return {'status': 'success', 'panel': panel, 'data': panel_data}
        
    def _get_panel_data(self, panel: str) -> Dict[str, Any]:
        """Get current data from specified panel."""
        # This would integrate with actual panel data
        return {'panel': panel, 'timestamp': asyncio.get_event_loop().time()}
        
    def send_to_mobile(self, panel: str, data: Dict[str, Any]) -> bool:
        """Send data to mobile app."""
        if not self.is_connected:
            return False
            
        try:
            message = json.dumps({'panel': panel, 'data': data})
            self.client_socket.send(message.encode())
            return True
        except Exception:
            return False