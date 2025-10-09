#!/usr/bin/env python3
"""
Responsive design utilities for adapting layouts to different screen sizes
"""

from typing import Dict, List, Optional, Tuple, Any
from PySide6.QtWidgets import (
    QWidget, QLayout, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSplitter, QScrollArea, QStackedWidget, QTabWidget
)
from PySide6.QtCore import Qt, QSize, Signal, QTimer
from PySide6.QtGui import QScreen
from enum import Enum


class ScreenSize(Enum):
    """Screen size categories"""
    MOBILE = "mobile"          # < 768px width
    TABLET = "tablet"          # 768px - 1024px width
    DESKTOP = "desktop"        # > 1024px width
    LARGE_DESKTOP = "large"    # > 1440px width


class Breakpoint(Enum):
    """Breakpoint values"""
    MOBILE_MAX = 767
    TABLET_MAX = 1023
    DESKTOP_MAX = 1439


class ResponsiveManager:
    """Manages responsive design for the application"""
    
    def __init__(self):
        self.current_screen_size = ScreenSize.DESKTOP
        self.breakpoints = {
            ScreenSize.MOBILE: Breakpoint.MOBILE_MAX,
            ScreenSize.TABLET: Breakpoint.TABLET_MAX,
            ScreenSize.DESKTOP: Breakpoint.DESKTOP_MAX
        }
        self.responsive_widgets = []
        self.layout_adapters = {}
    
    def register_widget(self, widget: QWidget, adapter: 'ResponsiveAdapter'):
        """Register a widget for responsive behavior"""
        self.responsive_widgets.append({
            'widget': widget,
            'adapter': adapter
        })
    
    def unregister_widget(self, widget: QWidget):
        """Unregister a widget"""
        self.responsive_widgets = [
            item for item in self.responsive_widgets
            if item['widget'] != widget
        ]
    
    def update_screen_size(self, width: int):
        """Update current screen size based on width"""
        if width <= Breakpoint.MOBILE_MAX.value:
            new_size = ScreenSize.MOBILE
        elif width <= Breakpoint.TABLET_MAX.value:
            new_size = ScreenSize.TABLET
        elif width <= Breakpoint.DESKTOP_MAX.value:
            new_size = ScreenSize.DESKTOP
        else:
            new_size = ScreenSize.LARGE_DESKTOP
        
        if new_size != self.current_screen_size:
            self.current_screen_size = new_size
            self._notify_widgets()
    
    def _notify_widgets(self):
        """Notify all registered widgets of screen size change"""
        for item in self.responsive_widgets:
            item['adapter'].adapt_to_screen_size(self.current_screen_size)
    
    def get_current_screen_size(self) -> ScreenSize:
        """Get current screen size"""
        return self.current_screen_size
    
    def is_mobile(self) -> bool:
        """Check if current screen size is mobile"""
        return self.current_screen_size == ScreenSize.MOBILE
    
    def is_tablet(self) -> bool:
        """Check if current screen size is tablet"""
        return self.current_screen_size == ScreenSize.TABLET
    
    def is_desktop(self) -> bool:
        """Check if current screen size is desktop"""
        return self.current_screen_size in [ScreenSize.DESKTOP, ScreenSize.LARGE_DESKTOP]


class ResponsiveAdapter:
    """Base class for responsive adapters"""
    
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.original_layout = None
        self.mobile_layout = None
        self.tablet_layout = None
        self.desktop_layout = None
    
    def adapt_to_screen_size(self, screen_size: ScreenSize):
        """Adapt widget to screen size"""
        if screen_size == ScreenSize.MOBILE:
            self._adapt_to_mobile()
        elif screen_size == ScreenSize.TABLET:
            self._adapt_to_tablet()
        else:
            self._adapt_to_desktop()
    
    def _adapt_to_mobile(self):
        """Adapt to mobile layout"""
        pass
    
    def _adapt_to_tablet(self):
        """Adapt to tablet layout"""
        pass
    
    def _adapt_to_desktop(self):
        """Adapt to desktop layout"""
        pass


class ResponsiveGridAdapter(ResponsiveAdapter):
    """Adapter for responsive grid layouts"""
    
    def __init__(self, widget: QWidget, grid_layout: QGridLayout):
        super().__init__(widget)
        self.grid_layout = grid_layout
        self.original_columns = 3
        self.mobile_columns = 1
        self.tablet_columns = 2
        self.desktop_columns = 3
        self.large_desktop_columns = 4
    
    def set_column_counts(self, mobile: int = 1, tablet: int = 2, 
                         desktop: int = 3, large: int = 4):
        """Set column counts for different screen sizes"""
        self.mobile_columns = mobile
        self.tablet_columns = tablet
        self.desktop_columns = desktop
        self.large_desktop_columns = large
    
    def _adapt_to_mobile(self):
        """Adapt grid to mobile layout"""
        self._rearrange_grid(self.mobile_columns)
    
    def _adapt_to_tablet(self):
        """Adapt grid to tablet layout"""
        self._rearrange_grid(self.tablet_columns)
    
    def _adapt_to_desktop(self):
        """Adapt grid to desktop layout"""
        self._rearrange_grid(self.desktop_columns)
    
    def _rearrange_grid(self, columns: int):
        """Rearrange grid items"""
        # Get all items from the grid
        items = []
        for row in range(self.grid_layout.rowCount()):
            for col in range(self.grid_layout.columnCount()):
                item = self.grid_layout.itemAtPosition(row, col)
                if item and item.widget():
                    items.append(item.widget())
        
        # Clear the grid
        for item in items:
            self.grid_layout.removeWidget(item)
        
        # Re-add items in new arrangement
        for i, widget in enumerate(items):
            row = i // columns
            col = i % columns
            self.grid_layout.addWidget(widget, row, col)


class ResponsiveSplitterAdapter(ResponsiveAdapter):
    """Adapter for responsive splitter layouts"""
    
    def __init__(self, widget: QWidget, splitter: QSplitter):
        super().__init__(widget)
        self.splitter = splitter
        self.original_orientation = splitter.orientation()
        self.original_sizes = splitter.sizes()
    
    def _adapt_to_mobile(self):
        """Adapt splitter to mobile layout"""
        # Stack vertically on mobile
        self.splitter.setOrientation(Qt.Vertical)
        # Make all sections equal size
        count = self.splitter.count()
        if count > 0:
            self.splitter.setSizes([1] * count)
    
    def _adapt_to_tablet(self):
        """Adapt splitter to tablet layout"""
        # Use original orientation
        self.splitter.setOrientation(self.original_orientation)
        # Adjust sizes for tablet
        count = self.splitter.count()
        if count > 0:
            if self.original_orientation == Qt.Horizontal:
                # Make left panel smaller on tablet
                sizes = [200, 400] if count == 2 else [1] * count
            else:
                # Make top panel smaller on tablet
                sizes = [150, 300] if count == 2 else [1] * count
            self.splitter.setSizes(sizes)
    
    def _adapt_to_desktop(self):
        """Adapt splitter to desktop layout"""
        # Use original orientation and sizes
        self.splitter.setOrientation(self.original_orientation)
        self.splitter.setSizes(self.original_sizes)


class ResponsiveTabAdapter(ResponsiveAdapter):
    """Adapter for responsive tab widgets"""
    
    def __init__(self, widget: QWidget, tab_widget: QTabWidget):
        super().__init__(widget)
        self.tab_widget = tab_widget
        self.original_tab_position = tab_widget.tabPosition()
        self.mobile_tab_position = QTabWidget.North
        self.desktop_tab_position = self.original_tab_position
    
    def _adapt_to_mobile(self):
        """Adapt tabs to mobile layout"""
        # Use top tabs on mobile
        self.tab_widget.setTabPosition(self.mobile_tab_position)
        # Make tabs more touch-friendly
        self.tab_widget.setTabBarAutoHide(False)
    
    def _adapt_to_tablet(self):
        """Adapt tabs to tablet layout"""
        # Use top tabs on tablet
        self.tab_widget.setTabPosition(self.mobile_tab_position)
        self.tab_widget.setTabBarAutoHide(False)
    
    def _adapt_to_desktop(self):
        """Adapt tabs to desktop layout"""
        # Use original tab position
        self.tab_widget.setTabPosition(self.desktop_tab_position)
        # Enable auto-hide for desktop
        self.tab_widget.setTabBarAutoHide(True)


class ResponsiveStackAdapter(ResponsiveAdapter):
    """Adapter for responsive stacked widgets"""
    
    def __init__(self, widget: QWidget, stacked_widget: QStackedWidget):
        super().__init__(widget)
        self.stacked_widget = stacked_widget
        self.mobile_page = 0
        self.tablet_page = 0
        self.desktop_page = 0
    
    def set_pages(self, mobile: int = 0, tablet: int = 0, desktop: int = 0):
        """Set which page to show for each screen size"""
        self.mobile_page = mobile
        self.tablet_page = tablet
        self.desktop_page = desktop
    
    def _adapt_to_mobile(self):
        """Adapt to mobile page"""
        if 0 <= self.mobile_page < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(self.mobile_page)
    
    def _adapt_to_tablet(self):
        """Adapt to tablet page"""
        if 0 <= self.tablet_page < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(self.tablet_page)
    
    def _adapt_to_desktop(self):
        """Adapt to desktop page"""
        if 0 <= self.desktop_page < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(self.desktop_page)


class ResponsiveWidget(QWidget):
    """Base class for responsive widgets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.responsive_manager = get_responsive_manager()
        self.adapter = None
        self.setup_responsive_behavior()
    
    def setup_responsive_behavior(self):
        """Set up responsive behavior"""
        # Override in subclasses
        pass
    
    def set_responsive_adapter(self, adapter: ResponsiveAdapter):
        """Set responsive adapter"""
        self.adapter = adapter
        self.responsive_manager.register_widget(self, adapter)
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        width = event.size().width()
        self.responsive_manager.update_screen_size(width)
    
    def closeEvent(self, event):
        """Handle close events"""
        if self.adapter:
            self.responsive_manager.unregister_widget(self)
        super().closeEvent(event)


class ResponsiveGridWidget(ResponsiveWidget):
    """Responsive grid widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self.setup_responsive_behavior()
    
    def setup_responsive_behavior(self):
        """Set up responsive grid behavior"""
        adapter = ResponsiveGridAdapter(self, self.grid_layout)
        self.set_responsive_adapter(adapter)
    
    def add_widget(self, widget: QWidget):
        """Add widget to grid"""
        self.grid_layout.addWidget(widget)
    
    def set_column_counts(self, mobile: int = 1, tablet: int = 2, 
                         desktop: int = 3, large: int = 4):
        """Set column counts for different screen sizes"""
        if self.adapter:
            self.adapter.set_column_counts(mobile, tablet, desktop, large)


class ResponsiveSplitterWidget(ResponsiveWidget):
    """Responsive splitter widget"""
    
    def __init__(self, orientation: Qt.Orientation = Qt.Horizontal, parent=None):
        super().__init__(parent)
        self.splitter = QSplitter(orientation, self)
        self.setup_responsive_behavior()
    
    def setup_responsive_behavior(self):
        """Set up responsive splitter behavior"""
        adapter = ResponsiveSplitterAdapter(self, self.splitter)
        self.set_responsive_adapter(adapter)
    
    def add_widget(self, widget: QWidget):
        """Add widget to splitter"""
        self.splitter.addWidget(widget)
    
    def set_sizes(self, sizes: List[int]):
        """Set splitter sizes"""
        self.splitter.setSizes(sizes)


class ResponsiveTabWidget(ResponsiveWidget):
    """Responsive tab widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab_widget = QTabWidget(self)
        self.setup_responsive_behavior()
    
    def setup_responsive_behavior(self):
        """Set up responsive tab behavior"""
        adapter = ResponsiveTabAdapter(self, self.tab_widget)
        self.set_responsive_adapter(adapter)
    
    def add_tab(self, widget: QWidget, title: str):
        """Add tab to widget"""
        self.tab_widget.addTab(widget, title)
    
    def set_tab_position(self, position: QTabWidget.TabPosition):
        """Set tab position"""
        self.tab_widget.setTabPosition(position)


class ResponsiveStackWidget(ResponsiveWidget):
    """Responsive stacked widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stacked_widget = QStackedWidget(self)
        self.setup_responsive_behavior()
    
    def setup_responsive_behavior(self):
        """Set up responsive stack behavior"""
        adapter = ResponsiveStackAdapter(self, self.stacked_widget)
        self.set_responsive_adapter(adapter)
    
    def add_page(self, widget: QWidget):
        """Add page to stack"""
        self.stacked_widget.addWidget(widget)
    
    def set_pages(self, mobile: int = 0, tablet: int = 0, desktop: int = 0):
        """Set which page to show for each screen size"""
        if self.adapter:
            self.adapter.set_pages(mobile, tablet, desktop)


def get_responsive_manager() -> ResponsiveManager:
    """Get global responsive manager"""
    global _responsive_manager
    if _responsive_manager is None:
        _responsive_manager = ResponsiveManager()
    return _responsive_manager


def create_responsive_grid(parent=None) -> ResponsiveGridWidget:
    """Create responsive grid widget"""
    return ResponsiveGridWidget(parent)


def create_responsive_splitter(orientation: Qt.Orientation = Qt.Horizontal, 
                             parent=None) -> ResponsiveSplitterWidget:
    """Create responsive splitter widget"""
    return ResponsiveSplitterWidget(orientation, parent)


def create_responsive_tabs(parent=None) -> ResponsiveTabWidget:
    """Create responsive tab widget"""
    return ResponsiveTabWidget(parent)


def create_responsive_stack(parent=None) -> ResponsiveStackWidget:
    """Create responsive stacked widget"""
    return ResponsiveStackWidget(parent)


# Global responsive manager instance
_responsive_manager = None
