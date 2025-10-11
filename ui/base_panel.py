"""Base panel class for consistent UI across all panels."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from core.ui_polish import UIPolish


class BasePanel(QWidget):
    """Base class for all application panels with consistent styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_base_ui()
    
    def setup_base_ui(self):
        """Setup base UI structure."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(UIPolish.SPACING_MEDIUM)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Apply base panel styling
        self.setStyleSheet("""
            QWidget {
                background-color: #fafafa;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
    
    def add_section_header(self, title: str):
        """Add a consistent section header."""
        header = QLabel(title)
        header.setFont(UIPolish.get_header_font())
        header.setStyleSheet("""
            QLabel {
                color: #2e7d32;
                padding: 8px 0px;
                border-bottom: 2px solid #c8e6c9;
                margin-bottom: 12px;
            }
        """)
        self.main_layout.addWidget(header)
        return header
    
    def add_separator(self):
        """Add a visual separator."""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("""
            QFrame {
                color: #e0e0e0;
                background-color: #e0e0e0;
                border: none;
                height: 1px;
                margin: 16px 0px;
            }
        """)
        self.main_layout.addWidget(line)
        return line
    
    def create_card_widget(self):
        """Create a card-style widget."""
        card = QWidget()
        UIPolish.apply_card_style(card)
        return card