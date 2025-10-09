#!/usr/bin/env python3
"""
Lazy loading utilities for large datasets
"""

import time
from typing import Any, Dict, List, Optional, Callable, Iterator, Tuple
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtWidgets import QWidget, QTableWidget, QListWidget, QTreeWidget


class LazyLoadingMixin:
    """Mixin class for lazy loading functionality"""
    
    def __init__(self):
        self._lazy_data = {}
        self._loading_states = {}
        self._page_size = 50
        self._current_page = 0
        self._total_items = 0
        self._is_loading = False
    
    def set_page_size(self, page_size: int):
        """Set page size for lazy loading"""
        self._page_size = page_size
    
    def get_page_size(self) -> int:
        """Get current page size"""
        return self._page_size
    
    def set_total_items(self, total: int):
        """Set total number of items"""
        self._total_items = total
    
    def get_total_items(self) -> int:
        """Get total number of items"""
        return self._total_items
    
    def is_loading(self) -> bool:
        """Check if currently loading"""
        return self._is_loading
    
    def set_loading(self, loading: bool):
        """Set loading state"""
        self._is_loading = loading
    
    def get_current_page(self) -> int:
        """Get current page number"""
        return self._current_page
    
    def set_current_page(self, page: int):
        """Set current page number"""
        self._current_page = page
    
    def can_load_more(self) -> bool:
        """Check if more data can be loaded"""
        return (self._current_page + 1) * self._page_size < self._total_items


class LazyTableWidget(QTableWidget, LazyLoadingMixin):
    """Table widget with lazy loading support"""
    
    # Signals
    load_more_requested = Signal(int, int)  # page, page_size
    data_loaded = Signal(list)
    loading_state_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        LazyLoadingMixin.__init__(self)
        self.setup_lazy_loading()
    
    def setup_lazy_loading(self):
        """Set up lazy loading functionality"""
        # Connect scroll events
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)
        
        # Set up loading indicator
        self._loading_row = None
    
    def _on_scroll(self, value):
        """Handle scroll events for lazy loading"""
        if self.is_loading():
            return
        
        # Check if scrolled near bottom
        scrollbar = self.verticalScrollBar()
        if value >= scrollbar.maximum() - 100:  # 100px from bottom
            self._load_next_page()
    
    def _load_next_page(self):
        """Load next page of data"""
        if not self.can_load_more() or self.is_loading():
            return
        
        self.set_loading(True)
        self.loading_state_changed.emit(True)
        
        # Add loading indicator
        self._add_loading_row()
        
        # Emit signal to load more data
        self.load_more_requested.emit(self._current_page + 1, self._page_size)
    
    def _add_loading_row(self):
        """Add loading indicator row"""
        if self._loading_row is None:
            self._loading_row = self.rowCount()
            self.insertRow(self._loading_row)
            
            loading_item = QTableWidgetItem("Loading...")
            loading_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
            self.setItem(self._loading_row, 0, loading_item)
    
    def _remove_loading_row(self):
        """Remove loading indicator row"""
        if self._loading_row is not None:
            self.removeRow(self._loading_row)
            self._loading_row = None
    
    def load_data(self, data: List[Dict[str, Any]]):
        """
        Load data into table
        
        Args:
            data: List of data dictionaries
        """
        self._remove_loading_row()
        
        # Add new rows
        start_row = self.rowCount()
        for i, item in enumerate(data):
            row = start_row + i
            self.insertRow(row)
            
            # Populate columns
            for col, (key, value) in enumerate(item.items()):
                if col < self.columnCount():
                    item_widget = QTableWidgetItem(str(value))
                    self.setItem(row, col, item_widget)
        
        self.set_loading(False)
        self.loading_state_changed.emit(False)
        self.data_loaded.emit(data)
    
    def reset_data(self):
        """Reset table data"""
        self.setRowCount(0)
        self.set_current_page(0)
        self._loading_row = None


class LazyListWidget(QListWidget, LazyLoadingMixin):
    """List widget with lazy loading support"""
    
    # Signals
    load_more_requested = Signal(int, int)  # page, page_size
    data_loaded = Signal(list)
    loading_state_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        LazyLoadingMixin.__init__(self)
        self.setup_lazy_loading()
    
    def setup_lazy_loading(self):
        """Set up lazy loading functionality"""
        # Connect scroll events
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)
    
    def _on_scroll(self, value):
        """Handle scroll events for lazy loading"""
        if self.is_loading():
            return
        
        # Check if scrolled near bottom
        scrollbar = self.verticalScrollBar()
        if value >= scrollbar.maximum() - 100:  # 100px from bottom
            self._load_next_page()
    
    def _load_next_page(self):
        """Load next page of data"""
        if not self.can_load_more() or self.is_loading():
            return
        
        self.set_loading(True)
        self.loading_state_changed.emit(True)
        
        # Add loading indicator
        loading_item = QListWidgetItem("Loading...")
        loading_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
        self.addItem(loading_item)
        
        # Emit signal to load more data
        self.load_more_requested.emit(self._current_page + 1, self._page_size)
    
    def load_data(self, data: List[str]):
        """
        Load data into list
        
        Args:
            data: List of strings
        """
        # Remove loading indicator
        if self.count() > 0:
            last_item = self.item(self.count() - 1)
            if last_item and last_item.text() == "Loading...":
                self.takeItem(self.count() - 1)
        
        # Add new items
        for item_text in data:
            self.addItem(item_text)
        
        self.set_loading(False)
        self.loading_state_changed.emit(False)
        self.data_loaded.emit(data)
    
    def reset_data(self):
        """Reset list data"""
        self.clear()
        self.set_current_page(0)


class LazyTreeWidget(QTreeWidget, LazyLoadingMixin):
    """Tree widget with lazy loading support"""
    
    # Signals
    load_more_requested = Signal(str, int, int)  # parent_path, page, page_size
    data_loaded = Signal(str, list)  # parent_path, data
    loading_state_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        LazyLoadingMixin.__init__(self)
        self.setup_lazy_loading()
        self._loading_items = {}  # Track loading items by parent path
    
    def setup_lazy_loading(self):
        """Set up lazy loading functionality"""
        # Connect item expansion events
        self.itemExpanded.connect(self._on_item_expanded)
    
    def _on_item_expanded(self, item):
        """Handle item expansion for lazy loading"""
        if self.is_loading():
            return
        
        # Check if item has children that need loading
        if item.childCount() == 0 or (item.childCount() == 1 and item.child(0).text(0) == "Loading..."):
            self._load_children(item)
    
    def _load_children(self, parent_item):
        """Load children for parent item"""
        parent_path = self._get_item_path(parent_item)
        
        if parent_path in self._loading_items:
            return  # Already loading
        
        self.set_loading(True)
        self.loading_state_changed.emit(True)
        
        # Add loading indicator
        loading_item = QTreeWidgetItem(parent_item)
        loading_item.setText(0, "Loading...")
        loading_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
        self._loading_items[parent_path] = loading_item
        
        # Emit signal to load children
        self.load_more_requested.emit(parent_path, 0, self._page_size)
    
    def _get_item_path(self, item) -> str:
        """Get path string for item"""
        path_parts = []
        current = item
        
        while current:
            path_parts.insert(0, current.text(0))
            current = current.parent()
        
        return "/".join(path_parts)
    
    def load_children_data(self, parent_path: str, data: List[Dict[str, Any]]):
        """
        Load children data for parent
        
        Args:
            parent_path: Path to parent item
            data: List of child data dictionaries
        """
        # Remove loading indicator
        if parent_path in self._loading_items:
            loading_item = self._loading_items[parent_path]
            parent = loading_item.parent()
            if parent:
                parent.removeChild(loading_item)
            del self._loading_items[parent_path]
        
        # Add new items
        parent_item = self._find_item_by_path(parent_path)
        if parent_item:
            for item_data in data:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, item_data.get('text', ''))
                
                # Set additional data
                for key, value in item_data.items():
                    if key != 'text':
                        child_item.setData(0, Qt.UserRole, {key: value})
        
        self.set_loading(False)
        self.loading_state_changed.emit(False)
        self.data_loaded.emit(parent_path, data)
    
    def _find_item_by_path(self, path: str) -> Optional[QTreeWidgetItem]:
        """Find item by path string"""
        path_parts = path.split("/")
        
        # Start from root
        current_items = []
        for i in range(self.topLevelItemCount()):
            current_items.append(self.topLevelItem(i))
        
        # Navigate through path parts
        for part in path_parts:
            found = False
            for item in current_items:
                if item.text(0) == part:
                    current_items = []
                    for i in range(item.childCount()):
                        current_items.append(item.child(i))
                    found = True
                    break
            
            if not found:
                return None
        
        # Return the last matching item
        if current_items and len(path_parts) > 0:
            for item in current_items:
                if item.text(0) == path_parts[-1]:
                    return item
        
        return None
    
    def reset_data(self):
        """Reset tree data"""
        self.clear()
        self.set_current_page(0)
        self._loading_items.clear()


class LazyDataLoader(QObject):
    """Background data loader for lazy loading widgets"""
    
    # Signals
    data_loaded = Signal(list)
    loading_finished = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, loader_func: Callable, parent=None):
        super().__init__(parent)
        self.loader_func = loader_func
        self._is_loading = False
    
    def load_data(self, *args, **kwargs):
        """Load data in background"""
        if self._is_loading:
            return
        
        self._is_loading = True
        
        try:
            # Execute loader function
            data = self.loader_func(*args, **kwargs)
            self.data_loaded.emit(data)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self._is_loading = False
            self.loading_finished.emit()
    
    def is_loading(self) -> bool:
        """Check if currently loading"""
        return self._is_loading


class VirtualScrollWidget(QWidget):
    """Widget that implements virtual scrolling for large datasets"""
    
    def __init__(self, item_height: int = 30, parent=None):
        super().__init__(parent)
        self.item_height = item_height
        self.visible_items = []
        self.total_items = 0
        self.scroll_offset = 0
        self.viewport_height = 0
        
        # Set up scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self._on_scroll)
        
        # Content widget
        self.content_widget = QWidget()
        self.scroll_area.setWidget(self.content_widget)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
    
    def set_total_items(self, total: int):
        """Set total number of items"""
        self.total_items = total
        self._update_content_size()
    
    def set_item_renderer(self, renderer_func: Callable):
        """Set function to render individual items"""
        self.renderer_func = renderer_func
    
    def _update_content_size(self):
        """Update content widget size"""
        total_height = self.total_items * self.item_height
        self.content_widget.setFixedHeight(total_height)
    
    def _on_scroll(self, value):
        """Handle scroll events"""
        self.scroll_offset = value
        self._update_visible_items()
    
    def _update_visible_items(self):
        """Update visible items based on scroll position"""
        if not hasattr(self, 'renderer_func'):
            return
        
        # Calculate visible range
        start_index = self.scroll_offset // self.item_height
        end_index = min(
            start_index + (self.viewport_height // self.item_height) + 2,
            self.total_items
        )
        
        # Render visible items
        for i in range(start_index, end_index):
            if i not in self.visible_items:
                item_widget = self.renderer_func(i)
                item_widget.setParent(self.content_widget)
                item_widget.move(0, i * self.item_height)
                self.visible_items.append(i)
        
        # Remove off-screen items
        self.visible_items = [i for i in self.visible_items if start_index <= i < end_index]
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        self.viewport_height = self.scroll_area.height()
        self._update_visible_items()


def create_lazy_table(parent=None) -> LazyTableWidget:
    """Create a lazy loading table widget"""
    return LazyTableWidget(parent)


def create_lazy_list(parent=None) -> LazyListWidget:
    """Create a lazy loading list widget"""
    return LazyListWidget(parent)


def create_lazy_tree(parent=None) -> LazyTreeWidget:
    """Create a lazy loading tree widget"""
    return LazyTreeWidget(parent)


def create_virtual_scroll_widget(item_height: int = 30, parent=None) -> VirtualScrollWidget:
    """Create a virtual scrolling widget"""
    return VirtualScrollWidget(item_height, parent)
