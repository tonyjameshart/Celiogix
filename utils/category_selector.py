#!/usr/bin/env python3
"""
Enhanced Category Selector Widget for Recipe Categories
"""

from typing import List, Dict, Any, Optional, Callable
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
    QButtonGroup, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette


class CategoryButton(QPushButton):
    """Custom category button with enhanced styling"""
    
    def __init__(self, text: str, category_id = None, parent=None):
        # Ensure parent is None or a QWidget
        if parent is not None and not isinstance(parent, QWidget):
            parent = None
        super().__init__(text, parent)
        self.category_id = str(category_id) if category_id is not None else text.lower()
        self.setup_styling()
    
    def setup_styling(self):
        """Set up button styling"""
        self.setCheckable(True)
        self.setMinimumHeight(35)
        self.setMaximumHeight(35)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # Enhanced styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 8px 16px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: 500;
                text-align: center;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
                color: #212529;
            }
            QPushButton:checked {
                background-color: #4caf50;
                color: white;
                border-color: #2e7d32;
                font-weight: 600;
            }
            QPushButton:checked:hover {
                background-color: #66bb6a;
                border-color: #388e3c;
            }
        """)


class CategorySelector(QWidget):
    """Enhanced category selector with button-based selection"""
    
    # Signals
    category_changed = Signal(str, str)  # category_id, category_name
    
    def __init__(self, parent=None, title: str = "Category"):
        super().__init__(parent)
        self.title = title
        self.button_group = QButtonGroup()
        self.buttons = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the category selector UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #495057; margin-bottom: 4px;")
        layout.addWidget(title_label)
        
        # Scroll area for buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(50)
        scroll_area.setMinimumHeight(50)
        
        # Button container
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        button_layout.addStretch()
        
        scroll_area.setWidget(button_widget)
        layout.addWidget(scroll_area)
        
        self.button_widget = button_widget
        self.button_layout = button_layout
        
        # Set default categories
        self.set_categories([
            ("All", "all"),
            ("Breakfast", "breakfast"),
            ("Lunch", "lunch"),
            ("Dinner", "dinner"),
            ("Snack", "snack"),
            ("Dessert", "dessert"),
            ("Beverage", "beverage"),
            ("Other", "other")
        ])
    
    def set_categories(self, categories: List[tuple]):
        """
        Set the available categories
        
        Args:
            categories: List of (name, id) tuples
        """
        # Clear existing buttons
        for button in self.buttons.values():
            button.deleteLater()
        self.buttons.clear()
        
        # Add new buttons
        for name, category_id in categories:
            # Ensure name is a string and category_id is converted to string
            button = CategoryButton(str(name), str(category_id))
            button.clicked.connect(lambda checked, cid=str(category_id), cname=str(name): 
                                 self._on_category_selected(cid, cname))
            
            self.button_group.addButton(button)
            self.button_layout.insertWidget(self.button_layout.count() - 1, button)
            self.buttons[str(category_id)] = button
        
        # Select "All" by default
        if "all" in self.buttons:
            self.buttons["all"].setChecked(True)
    
    def _on_category_selected(self, category_id: str, category_name: str):
        """Handle category selection"""
        self.category_changed.emit(category_id, category_name)
    
    def get_selected_category(self) -> tuple:
        """Get the currently selected category"""
        checked_button = self.button_group.checkedButton()
        if checked_button:
            return checked_button.category_id, checked_button.text()
        return "all", "All"
    
    def set_selected_category(self, category_id):
        """Set the selected category by ID"""
        category_id = str(category_id)
        if category_id in self.buttons:
            self.buttons[category_id].setChecked(True)
    
    def add_custom_category(self, name: str, category_id: str = None):
        """Add a custom category"""
        if category_id is None:
            category_id = name.lower().replace(" ", "_")
        
        button = CategoryButton(name, category_id)
        button.clicked.connect(lambda checked, cid=category_id, cname=name: 
                             self._on_category_selected(cid, cname))
        
        self.button_group.addButton(button)
        self.button_layout.insertWidget(self.button_layout.count() - 1, button)
        self.buttons[category_id] = button


