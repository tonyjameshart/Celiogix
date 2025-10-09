# path: panels/base_panel_pyside6.py
"""
Base Panel for PySide6 Application

Provides common functionality for all panels in the PySide6 application.
"""

from typing import Optional, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class BasePanel(QWidget):
    """Base class for all PySide6 panels"""
    
    def __init__(self, master=None, app=None):
        super().__init__(master)
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface - to be overridden by subclasses"""
        # Default layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Placeholder label
        label = QLabel(f"{self.__class__.__name__} - PySide6 Version")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    
    def refresh(self):
        """Refresh the panel data - to be overridden by subclasses"""
        pass
    
    def save_data(self):
        """Save panel data - to be overridden by subclasses"""
        pass
    
    def load_data(self):
        """Load panel data - to be overridden by subclasses"""
        pass
