#!/usr/bin/env python3
"""
Accessible widget implementations with built-in accessibility features
"""

from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QComboBox, QTextEdit,
    QTableWidget, QTreeWidget, QListWidget, QLabel, QGroupBox,
    QVBoxLayout, QHBoxLayout, QFormLayout, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPalette
from .accessibility import AccessibleWidget, announce_for_screen_reader


class AccessiblePushButton(QPushButton):
    """Accessible push button with enhanced accessibility features"""
    
    def __init__(self, text: str = "", parent=None, description: str = ""):
        super().__init__(text, parent)
        self.setup_accessibility(description or text)
        self.setup_button_accessibility()
    
    def setup_accessibility(self, description: str):
        """Set up accessibility features"""
        self.setAccessibleName(description)
        self.setAccessibleDescription(f"Button: {description}")
        self.setFocusPolicy(Qt.StrongFocus)
    
    def setup_button_accessibility(self):
        """Set up button-specific accessibility"""
        # Connect click signal to announce action
        self.clicked.connect(self._announce_click)
        
        # Set up keyboard shortcuts
        if hasattr(self, 'keyboard_navigation'):
            self.keyboard_navigation.add_widget_to_navigation(self, self.accessibleName())
    
    def _announce_click(self):
        """Announce button click"""
        announce_for_screen_reader(f"Button clicked: {self.text()}")
    
    def setText(self, text: str):
        """Set button text with accessibility announcement"""
        super().setText(text)
        self.setAccessibleName(text)
        announce_for_screen_reader(f"Button text updated: {text}")


class AccessibleLineEdit(QLineEdit):
    """Accessible line edit with enhanced accessibility features"""
    
    def __init__(self, placeholder_text: str = "", parent=None, description: str = ""):
        super().__init__(parent)
        self.setPlaceholderText(placeholder_text)
        self.setup_accessibility(description or placeholder_text)
        self.setup_edit_accessibility()
    
    def setup_accessibility(self, description: str):
        """Set up accessibility features"""
        self.setAccessibleName(description)
        self.setAccessibleDescription(f"Text input field: {description}")
        self.setFocusPolicy(Qt.StrongFocus)
    
    def setup_edit_accessibility(self):
        """Set up edit-specific accessibility"""
        # Connect text change signal
        self.textChanged.connect(self._announce_text_change)
        self.textEdited.connect(self._announce_text_edit)
        
        # Set up keyboard shortcuts
        if hasattr(self, 'keyboard_navigation'):
            self.keyboard_navigation.add_widget_to_navigation(self, self.accessibleName())
    
    def _announce_text_change(self, text: str):
        """Announce text change"""
        if text:
            announce_for_screen_reader(f"Text changed: {text}")
    
    def _announce_text_edit(self, text: str):
        """Announce text edit"""
        announce_for_screen_reader(f"Text edited: {text}")
    
    def setText(self, text: str):
        """Set text with accessibility announcement"""
        super().setText(text)
        announce_for_screen_reader(f"Text field updated: {text}")
    
    def focusInEvent(self, event):
        """Handle focus in event"""
        announce_for_screen_reader(f"Text field focused: {self.accessibleName()}")
        super().focusInEvent(event)


class AccessibleComboBox(QComboBox):
    """Accessible combo box with enhanced accessibility features"""
    
    def __init__(self, parent=None, description: str = ""):
        super().__init__(parent)
        self.setup_accessibility(description)
        self.setup_combo_accessibility()
    
    def setup_accessibility(self, description: str):
        """Set up accessibility features"""
        self.setAccessibleName(description)
        self.setAccessibleDescription(f"Dropdown selection: {description}")
        self.setFocusPolicy(Qt.StrongFocus)
    
    def setup_combo_accessibility(self):
        """Set up combo box-specific accessibility"""
        # Connect signals
        self.currentTextChanged.connect(self._announce_selection_change)
        self.activated.connect(self._announce_activation)
        
        # Set up keyboard shortcuts
        if hasattr(self, 'keyboard_navigation'):
            self.keyboard_navigation.add_widget_to_navigation(self, self.accessibleName())
    
    def _announce_selection_change(self, text: str):
        """Announce selection change"""
        announce_for_screen_reader(f"Selection changed to: {text}")
    
    def _announce_activation(self, index: int):
        """Announce activation"""
        text = self.itemText(index)
        announce_for_screen_reader(f"Selected: {text}")
    
    def addItem(self, text: str, userData=None):
        """Add item with accessibility announcement"""
        super().addItem(text, userData)
        announce_for_screen_reader(f"Added option: {text}")
    
    def setCurrentText(self, text: str):
        """Set current text with accessibility announcement"""
        super().setCurrentText(text)
        announce_for_screen_reader(f"Selection set to: {text}")
    
    def focusInEvent(self, event):
        """Handle focus in event"""
        announce_for_screen_reader(f"Dropdown focused: {self.accessibleName()}")
        super().focusInEvent(event)


class AccessibleTextEdit(QTextEdit):
    """Accessible text edit with enhanced accessibility features"""
    
    def __init__(self, placeholder_text: str = "", parent=None, description: str = ""):
        super().__init__(parent)
        self.setPlaceholderText(placeholder_text)
        self.setup_accessibility(description or placeholder_text)
        self.setup_text_edit_accessibility()
    
    def setup_accessibility(self, description: str):
        """Set up accessibility features"""
        self.setAccessibleName(description)
        self.setAccessibleDescription(f"Multi-line text editor: {description}")
        self.setFocusPolicy(Qt.StrongFocus)
    
    def setup_text_edit_accessibility(self):
        """Set up text edit-specific accessibility"""
        # Connect signals
        self.textChanged.connect(self._announce_text_change)
        
        # Set up keyboard shortcuts
        if hasattr(self, 'keyboard_navigation'):
            self.keyboard_navigation.add_widget_to_navigation(self, self.accessibleName())
    
    def _announce_text_change(self):
        """Announce text change"""
        text = self.toPlainText()
        if text:
            # Only announce if text is not empty and not just whitespace
            if text.strip():
                announce_for_screen_reader("Text content modified")
    
    def setPlainText(self, text: str):
        """Set plain text with accessibility announcement"""
        super().setPlainText(text)
        announce_for_screen_reader(f"Text editor updated: {len(text)} characters")
    
    def focusInEvent(self, event):
        """Handle focus in event"""
        announce_for_screen_reader(f"Text editor focused: {self.accessibleName()}")
        super().focusInEvent(event)


class AccessibleLabel(QLabel):
    """Accessible label with enhanced accessibility features"""
    
    def __init__(self, text: str = "", parent=None, description: str = ""):
        super().__init__(text, parent)
        self.setup_accessibility(description or text)
        self.setup_label_accessibility()
    
    def setup_accessibility(self, description: str):
        """Set up accessibility features"""
        self.setAccessibleName(description)
        self.setAccessibleDescription(f"Label: {description}")
        # Labels typically don't receive focus
        self.setFocusPolicy(Qt.NoFocus)
    
    def setup_label_accessibility(self):
        """Set up label-specific accessibility"""
        # Labels are usually read-only, so no special setup needed
        pass
    
    def setText(self, text: str):
        """Set label text with accessibility announcement"""
        super().setText(text)
        announce_for_screen_reader(f"Label updated: {text}")


class AccessibleGroupBox(QGroupBox):
    """Accessible group box with enhanced accessibility features"""
    
    def __init__(self, title: str = "", parent=None, description: str = ""):
        super().__init__(title, parent)
        self.setup_accessibility(description or title)
        self.setup_group_box_accessibility()
    
    def setup_accessibility(self, description: str):
        """Set up accessibility features"""
        self.setAccessibleName(description)
        self.setAccessibleDescription(f"Group box: {description}")
        self.setFocusPolicy(Qt.StrongFocus)
    
    def setup_group_box_accessibility(self):
        """Set up group box-specific accessibility"""
        # Group boxes can contain other widgets
        # Set up keyboard navigation for contained widgets
        if hasattr(self, 'keyboard_navigation'):
            self.keyboard_navigation.add_widget_to_navigation(self, self.accessibleName())
    
    def setTitle(self, title: str):
        """Set group box title with accessibility announcement"""
        super().setTitle(title)
        self.setAccessibleName(title)
        announce_for_screen_reader(f"Group box title updated: {title}")
    
    def focusInEvent(self, event):
        """Handle focus in event"""
        announce_for_screen_reader(f"Group box focused: {self.accessibleName()}")
        super().focusInEvent(event)


class AccessibleFormWidget(QWidget):
    """Accessible form widget with automatic accessibility setup"""
    
    def __init__(self, parent=None, form_title: str = ""):
        super().__init__(parent)
        self.form_title = form_title
        self.form_layout = QFormLayout(self)
        self.setup_accessibility()
    
    def setup_accessibility(self):
        """Set up form accessibility"""
        self.setAccessibleName(self.form_title or "Form")
        self.setAccessibleDescription(f"Form: {self.form_title}")
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Set up keyboard navigation
        from .accessibility import KeyboardNavigation
        self.keyboard_navigation = KeyboardNavigation(self)
    
    def add_field(self, label_text: str, widget: QWidget, description: str = ""):
        """
        Add a field to the form with automatic accessibility setup
        
        Args:
            label_text: Label text for the field
            widget: Input widget
            description: Accessibility description
        """
        # Create accessible label
        label = AccessibleLabel(label_text)
        
        # Set up widget accessibility
        if hasattr(widget, 'setup_accessibility'):
            widget.setup_accessibility(description or label_text)
        else:
            widget.setAccessibleName(description or label_text)
            widget.setFocusPolicy(Qt.StrongFocus)
        
        # Add to form layout
        self.form_layout.addRow(label, widget)
        
        # Add to keyboard navigation
        if hasattr(self, 'keyboard_navigation'):
            self.keyboard_navigation.add_widget_to_navigation(widget, description or label_text)
    
    def add_button(self, text: str, description: str = ""):
        """
        Add an accessible button to the form
        
        Args:
            text: Button text
            description: Accessibility description
            
        Returns:
            The created button
        """
        button = AccessiblePushButton(text, description=description or text)
        self.form_layout.addRow(button)
        
        # Add to keyboard navigation
        if hasattr(self, 'keyboard_navigation'):
            self.keyboard_navigation.add_widget_to_navigation(button, description or text)
        
        return button
    
    def add_text_field(self, label_text: str, placeholder: str = "", description: str = ""):
        """
        Add an accessible text field to the form
        
        Args:
            label_text: Label text
            placeholder: Placeholder text
            description: Accessibility description
            
        Returns:
            The created text field
        """
        text_field = AccessibleLineEdit(placeholder, description=description or label_text)
        self.add_field(label_text, text_field, description or label_text)
        return text_field
    
    def add_dropdown(self, label_text: str, options: List[str], description: str = ""):
        """
        Add an accessible dropdown to the form
        
        Args:
            label_text: Label text
            options: List of options
            description: Accessibility description
            
        Returns:
            The created dropdown
        """
        dropdown = AccessibleComboBox(description=description or label_text)
        for option in options:
            dropdown.addItem(option)
        
        self.add_field(label_text, dropdown, description or label_text)
        return dropdown
    
    def add_text_area(self, label_text: str, placeholder: str = "", description: str = ""):
        """
        Add an accessible text area to the form
        
        Args:
            label_text: Label text
            placeholder: Placeholder text
            description: Accessibility description
            
        Returns:
            The created text area
        """
        text_area = AccessibleTextEdit(placeholder, description=description or label_text)
        self.add_field(label_text, text_area, description or label_text)
        return text_area


def create_accessible_form(parent=None, title: str = "") -> AccessibleFormWidget:
    """
    Create an accessible form widget
    
    Args:
        parent: Parent widget
        title: Form title
        
    Returns:
        Accessible form widget
    """
    return AccessibleFormWidget(parent, title)


def setup_widget_accessibility(widget: QWidget, name: str, description: str = ""):
    """
    Set up accessibility for any widget
    
    Args:
        widget: Widget to set up
        name: Accessible name
        description: Accessible description
    """
    widget.setAccessibleName(name)
    widget.setAccessibleDescription(description or f"Widget: {name}")
    widget.setFocusPolicy(Qt.StrongFocus)
    
    # Set up keyboard navigation if not already set up
    if not hasattr(widget, 'keyboard_navigation'):
        from .accessibility import KeyboardNavigation
        widget.keyboard_navigation = KeyboardNavigation(widget)
        widget.keyboard_navigation.add_widget_to_navigation(widget, name)
