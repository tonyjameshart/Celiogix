"""UI polish and cohesiveness improvements."""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, pyqtSignal
from PySide6.QtGui import QFont


class UIPolish:
    """Centralized UI polish and consistency manager."""
    
    # Standard spacing and sizing
    SPACING_SMALL = 8
    SPACING_MEDIUM = 16
    SPACING_LARGE = 24
    
    BUTTON_HEIGHT = 32
    INPUT_HEIGHT = 28
    
    # Standard fonts
    @staticmethod
    def get_title_font():
        font = QFont("Segoe UI", 16, QFont.Bold)
        return font
    
    @staticmethod
    def get_header_font():
        font = QFont("Segoe UI", 12, QFont.DemiBold)
        return font
    
    @staticmethod
    def get_body_font():
        font = QFont("Segoe UI", 10)
        return font
    
    @staticmethod
    def apply_card_style(widget: QWidget):
        """Apply consistent card styling."""
        widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
    
    @staticmethod
    def apply_button_style(button):
        """Apply consistent button styling."""
        button.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:pressed {
                background-color: #1b5e20;
            }
            QPushButton:disabled {
                background-color: #c8e6c9;
                color: #81c784;
            }
        """)
    
    @staticmethod
    def create_fade_animation(widget: QWidget, duration=300):
        """Create smooth fade animation."""
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        return animation