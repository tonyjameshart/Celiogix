#!/usr/bin/env python3
"""
Custom Widgets for CeliacShield Application
Provides widgets without problematic Qt selection styling
"""

from PySide6.QtWidgets import QTableWidget, QListWidget, QTreeWidget
from PySide6.QtCore import Qt


class NoSelectionTableWidget(QTableWidget):
    """Table widget with selection completely disabled"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        
    def mousePressEvent(self, event):
        # Override to prevent any selection behavior
        pass
        
    def mouseReleaseEvent(self, event):
        # Override to prevent any selection behavior
        pass


class NoSelectionListWidget(QListWidget):
    """List widget with selection completely disabled"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QListWidget.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        
    def mousePressEvent(self, event):
        # Override to prevent any selection behavior
        pass
        
    def mouseReleaseEvent(self, event):
        # Override to prevent any selection behavior
        pass


class NoSelectionTreeWidget(QTreeWidget):
    """Tree widget with selection completely disabled"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QTreeWidget.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        
    def mousePressEvent(self, event):
        # Override to prevent any selection behavior
        pass
        
    def mouseReleaseEvent(self, event):
        # Override to prevent any selection behavior
        pass
