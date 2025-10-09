# path: services/theme_engine_pyside6.py
"""
Modern Theme Engine for PySide6 Application

Provides a clean, modern theme with proper color schemes and styling.
"""

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFont


def apply_modern_theme(app_or_widget):
    """Apply modern theme to application or widget"""
    
    # Create modern color palette
    palette = QPalette()
    
    # Define colors
    # Primary colors
    primary_color = QColor(76, 175, 80)  # Green for celiac-safe
    primary_dark = QColor(56, 142, 60)
    primary_light = QColor(129, 199, 132)
    
    # Secondary colors
    secondary_color = QColor(255, 152, 0)  # Orange for warnings
    secondary_dark = QColor(230, 81, 0)
    secondary_light = QColor(255, 183, 77)
    
    # Background colors
    background_color = QColor(250, 250, 250)  # Light gray
    surface_color = QColor(255, 255, 255)  # White
    surface_variant = QColor(245, 245, 245)  # Light gray
    
    # Text colors
    text_primary = QColor(33, 33, 33)  # Dark gray
    text_secondary = QColor(97, 97, 97)  # Medium gray
    text_disabled = QColor(158, 158, 158)  # Light gray
    
    # Error color
    error_color = QColor(244, 67, 54)  # Red
    
    # Set palette colors
    palette.setColor(QPalette.Window, background_color)
    palette.setColor(QPalette.WindowText, text_primary)
    palette.setColor(QPalette.Base, surface_color)
    palette.setColor(QPalette.AlternateBase, surface_variant)
    palette.setColor(QPalette.ToolTipBase, surface_color)
    palette.setColor(QPalette.ToolTipText, text_primary)
    palette.setColor(QPalette.Text, text_primary)
    palette.setColor(QPalette.Button, surface_color)
    palette.setColor(QPalette.ButtonText, text_primary)
    palette.setColor(QPalette.BrightText, Qt.white)
    palette.setColor(QPalette.Link, primary_color)
    palette.setColor(QPalette.Highlight, primary_color)
    palette.setColor(QPalette.HighlightedText, Qt.white)
    
    # Apply palette
    if isinstance(app_or_widget, QApplication):
        app_or_widget.setPalette(palette)
    else:
        app_or_widget.setPalette(palette)
    
    # Set application font
    font = QFont("Segoe UI", 9)
    if isinstance(app_or_widget, QApplication):
        app_or_widget.setFont(font)
    else:
        app_or_widget.setFont(font)


def get_modern_stylesheet():
    """Get modern stylesheet for widgets"""
    return """
    /* Modern stylesheet for PySide6 widgets */
    
    QMainWindow {
        background-color: #fafafa;
        color: #212121;
    }
    
    QTabWidget::pane {
        border: 1px solid #e0e0e0;
        background-color: white;
    }
    
    QTabBar::tab {
        background-color: #424242;
        color: white;
        border: 1px solid #616161;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: white;
        color: #212121;
        border-bottom: 2px solid #4caf50;
        font-weight: bold;
    }
    
    QTabBar::tab:hover {
        background-color: #616161;
        color: white;
    }
    
    QPushButton {
        background-color: #4caf50;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #45a049;
    }
    
    QPushButton:pressed {
        background-color: #3d8b40;
    }
    
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    
    QLineEdit {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 8px;
        background-color: white;
    }
    
    QLineEdit:focus {
        border: 2px solid #4caf50;
    }
    
    QTextEdit {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        background-color: white;
    }
    
    QTextEdit:focus {
        border: 2px solid #4caf50;
    }
    
    QComboBox {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 8px;
        background-color: white;
    }
    
    QComboBox:focus {
        border: 2px solid #4caf50;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #666666;
        margin-right: 5px;
    }
    
    QSpinBox {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 8px;
        background-color: white;
    }
    
    QSpinBox:focus {
        border: 2px solid #4caf50;
    }
    
    QCheckBox {
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #e0e0e0;
        border-radius: 3px;
        background-color: white;
    }
    
    QCheckBox::indicator:checked {
        background-color: #4caf50;
        border: 1px solid #4caf50;
    }
    
    QCheckBox::indicator:checked:hover {
        background-color: #45a049;
    }
    
    QRadioButton {
        spacing: 8px;
    }
    
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #e0e0e0;
        border-radius: 9px;
        background-color: white;
    }
    
    QRadioButton::indicator:checked {
        background-color: #4caf50;
        border: 1px solid #4caf50;
    }
    
    QRadioButton::indicator:checked:hover {
        background-color: #45a049;
    }
    
    QListWidget {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        background-color: white;
        alternate-background-color: #f5f5f5;
    }
    
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #f0f0f0;
    }
    
    QListWidget::item:selected {
        background-color: #4caf50;
        color: white;
    }
    
    QListWidget::item:hover {
        background-color: #e8f5e8;
    }
    
    QTreeWidget {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        background-color: white;
        alternate-background-color: #f5f5f5;
    }
    
    QTreeWidget::item {
        padding: 4px;
    }
    
    QTreeWidget::item:selected {
        background-color: #4caf50;
        color: white;
    }
    
    QTreeWidget::item:hover {
        background-color: #e8f5e8;
    }
    
    QTableWidget {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        background-color: white;
        alternate-background-color: #f5f5f5;
        gridline-color: #f0f0f0;
    }
    
    QTableWidget::item {
        padding: 8px;
        border: none;
        text-decoration: none;
    }
    
    QTableWidget::item:selected {
        background-color: #4caf50;
        color: white;
        text-decoration: none;
    }
    
    QTableWidget::item:hover {
        background-color: #e8f5e8;
    }
    
    QHeaderView::section {
        background-color: #f5f5f5;
        border: 1px solid #e0e0e0;
        padding: 8px;
        font-weight: bold;
    }
    
    QScrollBar:vertical {
        background-color: #f5f5f5;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #cccccc;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #999999;
    }
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        background-color: #f5f5f5;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #cccccc;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #999999;
    }
    
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    QStatusBar {
        background-color: #f5f5f5;
        border-top: 1px solid #e0e0e0;
        color: #666666;
    }
    
    QMenuBar {
        background-color: #f5f5f5;
        border-bottom: 1px solid #e0e0e0;
        color: #212121;
    }
    
    QMenuBar::item {
        padding: 8px 16px;
        background-color: transparent;
    }
    
    QMenuBar::item:selected {
        background-color: #e8f5e8;
        color: #4caf50;
    }
    
    QMenu {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
    }
    
    QMenu::item {
        padding: 8px 16px;
        background-color: transparent;
    }
    
    QMenu::item:selected {
        background-color: #4caf50;
        color: white;
    }
    
    QMessageBox {
        background-color: white;
    }
    
    QProgressBar {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        text-align: center;
        background-color: #f5f5f5;
    }
    
    QProgressBar::chunk {
        background-color: #4caf50;
        border-radius: 3px;
    }
    
    QSlider::groove:horizontal {
        height: 6px;
        background-color: #e0e0e0;
        border-radius: 3px;
    }
    
    QSlider::handle:horizontal {
        background-color: #4caf50;
        border: none;
        width: 18px;
        height: 18px;
        border-radius: 9px;
        margin: -6px 0;
    }
    
    QSlider::handle:horizontal:hover {
        background-color: #45a049;
    }
    
    QGroupBox {
        font-weight: bold;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 8px;
        padding: 0 8px 0 8px;
        color: #4caf50;
    }
    """
