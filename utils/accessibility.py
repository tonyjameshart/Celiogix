#!/usr/bin/env python3
"""
Accessibility utilities for keyboard navigation and screen reader support
"""

from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QComboBox, QTextEdit,
    QTableWidget, QTreeWidget, QListWidget, QTabWidget,
    QLabel, QGroupBox, QDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeySequence, QShortcut, QAction


class AccessibilityManager:
    """Manages accessibility features for the application"""
    
    def __init__(self):
        self.announcements = []
        self.announcement_timer = QTimer()
        self.announcement_timer.timeout.connect(self._process_announcements)
        self.announcement_timer.start(100)  # Check every 100ms
    
    def announce(self, message: str, priority: str = "normal"):
        """
        Announce a message for screen readers
        
        Args:
            message: Message to announce
            priority: Priority level (low, normal, high)
        """
        self.announcements.append({
            'message': message,
            'priority': priority,
            'timestamp': self._get_timestamp()
        })
    
    def _process_announcements(self):
        """Process pending announcements"""
        if self.announcements:
            # Process high priority announcements first
            high_priority = [a for a in self.announcements if a['priority'] == 'high']
            if high_priority:
                announcement = high_priority[0]
                self.announcements.remove(announcement)
                self._send_announcement(announcement['message'])
            else:
                announcement = self.announcements.pop(0)
                self._send_announcement(announcement['message'])
    
    def _send_announcement(self, message: str):
        """Send announcement to screen reader"""
        # This would integrate with screen reader APIs
        # For now, we'll use Qt's accessibility features
        print(f"ANNOUNCE: {message}")  # Debug output
    
    def _get_timestamp(self) -> float:
        """Get current timestamp"""
        import time
        return time.time()


class KeyboardNavigation:
    """Handles keyboard navigation for widgets"""
    
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.navigation_order = []
        self.current_focus_index = 0
        self.setup_keyboard_shortcuts()
    
    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for navigation"""
        # Tab navigation
        tab_shortcut = QShortcut(QKeySequence("Tab"), self.widget)
        tab_shortcut.activated.connect(self.next_widget)
        
        # Shift+Tab navigation
        shift_tab_shortcut = QShortcut(QKeySequence("Shift+Tab"), self.widget)
        shift_tab_shortcut.activated.connect(self.previous_widget)
        
        # Enter key activation
        enter_shortcut = QShortcut(QKeySequence("Return"), self.widget)
        enter_shortcut.activated.connect(self.activate_current_widget)
        
        # Escape key
        escape_shortcut = QShortcut(QKeySequence("Escape"), self.widget)
        escape_shortcut.activated.connect(self.cancel_current_action)
        
        # Arrow key navigation for lists and tables
        up_shortcut = QShortcut(QKeySequence("Up"), self.widget)
        up_shortcut.activated.connect(self.navigate_up)
        
        down_shortcut = QShortcut(QKeySequence("Down"), self.widget)
        down_shortcut.activated.connect(self.navigate_down)
        
        left_shortcut = QShortcut(QKeySequence("Left"), self.widget)
        left_shortcut.activated.connect(self.navigate_left)
        
        right_shortcut = QShortcut(QKeySequence("Right"), self.widget)
        right_shortcut.activated.connect(self.navigate_right)
    
    def add_widget_to_navigation(self, widget: QWidget, description: str = ""):
        """
        Add widget to keyboard navigation order
        
        Args:
            widget: Widget to add to navigation
            description: Description for screen readers
        """
        self.navigation_order.append({
            'widget': widget,
            'description': description
        })
        
        # Set accessibility properties
        widget.setAccessibleName(description)
        widget.setAccessibleDescription(f"Keyboard navigable: {description}")
    
    def next_widget(self):
        """Move focus to next widget in navigation order"""
        if not self.navigation_order:
            return
        
        self.current_focus_index = (self.current_focus_index + 1) % len(self.navigation_order)
        self._focus_current_widget()
    
    def previous_widget(self):
        """Move focus to previous widget in navigation order"""
        if not self.navigation_order:
            return
        
        self.current_focus_index = (self.current_focus_index - 1) % len(self.navigation_order)
        self._focus_current_widget()
    
    def _focus_current_widget(self):
        """Focus the current widget in navigation order"""
        if self.current_focus_index < len(self.navigation_order):
            widget_info = self.navigation_order[self.current_focus_index]
            widget_info['widget'].setFocus()
            
            # Announce the focused widget
            if widget_info['description']:
                accessibility_manager.announce(f"Focused: {widget_info['description']}")
    
    def activate_current_widget(self):
        """Activate the currently focused widget"""
        if self.current_focus_index < len(self.navigation_order):
            widget_info = self.navigation_order[self.current_focus_index]
            widget = widget_info['widget']
            
            if isinstance(widget, QPushButton):
                widget.click()
            elif isinstance(widget, QLineEdit):
                widget.selectAll()
            elif isinstance(widget, QComboBox):
                widget.showPopup()
            elif hasattr(widget, 'clicked'):
                widget.clicked.emit()
    
    def cancel_current_action(self):
        """Cancel current action (Escape key)"""
        # Find and close any open dialogs
        if hasattr(self.widget, 'close'):
            self.widget.close()
    
    def navigate_up(self):
        """Navigate up in lists/tables"""
        current_widget = self._get_current_widget()
        if isinstance(current_widget, (QTableWidget, QListWidget, QTreeWidget)):
            current_widget.keyPressEvent(self._create_key_event(Qt.Key_Up))
    
    def navigate_down(self):
        """Navigate down in lists/tables"""
        current_widget = self._get_current_widget()
        if isinstance(current_widget, (QTableWidget, QListWidget, QTreeWidget)):
            current_widget.keyPressEvent(self._create_key_event(Qt.Key_Down))
    
    def navigate_left(self):
        """Navigate left in tables"""
        current_widget = self._get_current_widget()
        if isinstance(current_widget, QTableWidget):
            current_widget.keyPressEvent(self._create_key_event(Qt.Key_Left))
    
    def navigate_right(self):
        """Navigate right in tables"""
        current_widget = self._get_current_widget()
        if isinstance(current_widget, QTableWidget):
            current_widget.keyPressEvent(self._create_key_event(Qt.Key_Right))
    
    def _get_current_widget(self) -> Optional[QWidget]:
        """Get currently focused widget"""
        if self.current_focus_index < len(self.navigation_order):
            return self.navigation_order[self.current_focus_index]['widget']
        return None
    
    def _create_key_event(self, key: int):
        """Create a key event for programmatic navigation"""
        from PySide6.QtGui import QKeyEvent
        return QKeyEvent(QKeyEvent.KeyPress, key, Qt.NoModifier)


class AccessibleWidget:
    """Mixin class to add accessibility features to widgets"""
    
    def __init__(self):
        self.accessibility_manager = None
        self.keyboard_navigation = None
    
    def setup_accessibility(self, description: str = ""):
        """
        Set up accessibility features for the widget
        
        Args:
            description: Description for screen readers
        """
        global accessibility_manager
        
        # Set accessible properties
        self.setAccessibleName(description)
        self.setAccessibleDescription(f"Accessible widget: {description}")
        
        # Set up keyboard navigation
        self.keyboard_navigation = KeyboardNavigation(self)
        
        # Enable focus
        self.setFocusPolicy(Qt.StrongFocus)
    
    def announce_change(self, message: str, priority: str = "normal"):
        """
        Announce a change for screen readers
        
        Args:
            message: Message to announce
            priority: Priority level
        """
        global accessibility_manager
        accessibility_manager.announce(message, priority)
    
    def add_to_navigation(self, widget: QWidget, description: str = ""):
        """
        Add widget to keyboard navigation
        
        Args:
            widget: Widget to add
            description: Description for screen readers
        """
        if self.keyboard_navigation:
            self.keyboard_navigation.add_widget_to_navigation(widget, description)


class AccessibleTableWidget(QTableWidget):
    """Accessible table widget with keyboard navigation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_accessibility()
        self.setup_table_accessibility()
    
    def setup_accessibility(self):
        """Set up accessibility features"""
        self.setAccessibleName("Data table")
        self.setAccessibleDescription("Interactive data table with keyboard navigation")
        self.setFocusPolicy(Qt.StrongFocus)
    
    def setup_table_accessibility(self):
        """Set up table-specific accessibility"""
        # Enable keyboard navigation
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setAlternatingRowColors(True)
        
        # Set up keyboard shortcuts
        self.keyboard_navigation = KeyboardNavigation(self)
    
    def keyPressEvent(self, event):
        """Handle key press events with accessibility announcements"""
        super().keyPressEvent(event)
        
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down:
            current_row = self.currentRow()
            current_col = self.currentColumn()
            
            if current_row >= 0 and current_col >= 0:
                item = self.item(current_row, current_col)
                if item:
                    # Announce current cell content
                    content = item.text()
                    if content:
                        accessibility_manager.announce(f"Row {current_row + 1}, Column {current_col + 1}: {content}")


class AccessibleDialog(QDialog):
    """Accessible dialog with keyboard navigation"""
    
    def __init__(self, parent=None, title: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setup_accessibility()
    
    def setup_accessibility(self):
        """Set up dialog accessibility"""
        self.setAccessibleName(self.windowTitle())
        self.setAccessibleDescription(f"Dialog: {self.windowTitle()}")
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Set up keyboard navigation
        self.keyboard_navigation = KeyboardNavigation(self)
        
        # Announce dialog opening
        accessibility_manager.announce(f"Dialog opened: {self.windowTitle()}", "high")
    
    def closeEvent(self, event):
        """Handle dialog closing with accessibility announcement"""
        accessibility_manager.announce(f"Dialog closed: {self.windowTitle()}")
        super().closeEvent(event)


class AccessibleMessageBox(QMessageBox):
    """Accessible message box"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_accessibility()
    
    def setup_accessibility(self):
        """Set up message box accessibility"""
        self.setAccessibleName("Message dialog")
        self.setAccessibleDescription("System message dialog")
        
        # Announce message box opening
        accessibility_manager.announce(f"Message: {self.text()}", "high")
    
    def closeEvent(self, event):
        """Handle message box closing"""
        accessibility_manager.announce("Message dialog closed")
        super().closeEvent(event)


def setup_panel_accessibility(panel: QWidget, panel_name: str):
    """
    Set up accessibility for a panel
    
    Args:
        panel: Panel widget
        panel_name: Name of the panel for accessibility
    """
    panel.setAccessibleName(f"{panel_name} panel")
    panel.setAccessibleDescription(f"Main panel for {panel_name} functionality")
    
    # Set up keyboard navigation
    keyboard_nav = KeyboardNavigation(panel)
    
    # Find and add all focusable widgets to navigation
    for widget in panel.findChildren(QWidget):
        if widget.focusPolicy() != Qt.NoFocus:
            widget_type = type(widget).__name__
            description = f"{widget_type} in {panel_name}"
            
            if hasattr(widget, 'accessibleName') and widget.accessibleName():
                description = widget.accessibleName()
            
            keyboard_nav.add_widget_to_navigation(widget, description)
    
    # Announce panel focus
    panel.focusInEvent = lambda event: accessibility_manager.announce(f"Focused {panel_name} panel", "normal") or super(type(panel), panel).focusInEvent(event)


# Global accessibility manager instance
accessibility_manager = AccessibilityManager()


def get_accessibility_manager() -> AccessibilityManager:
    """Get global accessibility manager"""
    return accessibility_manager


def announce_for_screen_reader(message: str, priority: str = "normal"):
    """Convenience function to announce messages"""
    accessibility_manager.announce(message, priority)
