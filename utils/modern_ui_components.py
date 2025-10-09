#!/usr/bin/env python3
"""
Modern UI components with card-based layouts and enhanced visual design
"""

from typing import Any, Dict, List, Optional, Callable, Union
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QSpacerItem, QApplication
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, Signal, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap, QIcon


class ModernCard(QFrame):
    """Modern card component with hover effects and animations"""
    
    # Signals
    clicked = Signal()
    hover_entered = Signal()
    hover_left = Signal()
    
    def __init__(self, parent=None, title: str = "", content: str = ""):
        super().__init__(parent)
        self.title = title
        self.content = content
        self.is_hovered = False
        self.is_selected = False
        
        self.setup_ui()
        self.setup_animations()
        self.setup_styling()
    
    def setup_ui(self):
        """Set up card UI"""
        self.setFrameStyle(QFrame.Box)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        if self.title:
            self.title_label = QLabel(self.title)
            self.title_label.setObjectName("cardTitle")
            self.title_label.setWordWrap(True)
            layout.addWidget(self.title_label)
        
        # Content
        if self.content:
            self.content_label = QLabel(self.content)
            self.content_label.setObjectName("cardContent")
            self.content_label.setWordWrap(True)
            self.content_label.setAlignment(Qt.AlignTop)
            layout.addWidget(self.content_label)
        
        # Actions area (can be customized)
        self.actions_layout = QHBoxLayout()
        self.actions_layout.addStretch()
        layout.addLayout(self.actions_layout)
    
    def setup_animations(self):
        """Set up hover animations"""
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(150)
        self.scale_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def setup_styling(self):
        """Set up card styling"""
        self.setStyleSheet("""
            ModernCard {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 12px;
                padding: 16px;
            }
            
            ModernCard:hover {
                border-color: #3498db;
                box-shadow: 0 4px 12px rgba(52, 152, 219, 0.15);
            }
            
            ModernCard[selected="true"] {
                border-color: #3498db;
                background-color: #f8f9fa;
                box-shadow: 0 2px 8px rgba(52, 152, 219, 0.1);
            }
            
            QLabel#cardTitle {
                font-size: 16px;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 8px;
            }
            
            QLabel#cardContent {
                font-size: 14px;
                color: #7f8c8d;
                line-height: 1.4;
            }
        """)
    
    def add_action_button(self, text: str, callback: Optional[Callable] = None) -> QPushButton:
        """Add action button to card"""
        button = QPushButton(text)
        button.setObjectName("cardActionButton")
        button.setStyleSheet("""
            QPushButton#cardActionButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
            }
            
            QPushButton#cardActionButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton#cardActionButton:pressed {
                background-color: #21618c;
            }
        """)
        
        if callback:
            button.clicked.connect(callback)
        
        self.actions_layout.addWidget(button)
        return button
    
    def set_selected(self, selected: bool):
        """Set card selection state"""
        self.is_selected = selected
        self.setProperty("selected", "true" if selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter"""
        self.is_hovered = True
        self.hover_entered.emit()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        self.is_hovered = False
        self.hover_left.emit()
        super().leaveEvent(event)


class CardGrid(QWidget):
    """Grid layout for cards with responsive design"""
    
    # Signals
    card_selected = Signal(ModernCard)
    card_clicked = Signal(ModernCard)
    
    def __init__(self, parent=None, cards_per_row: int = 3):
        super().__init__(parent)
        self.cards_per_row = cards_per_row
        self.cards = []
        self.selected_card = None
        
        self.setup_ui()
        self.setup_responsive_design()
    
    def setup_ui(self):
        """Set up grid UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(16)
        
        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(16)
        
        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area)
    
    def setup_responsive_design(self):
        """Set up responsive design"""
        # This would handle window resize events to adjust cards per row
        pass
    
    def add_card(self, card: ModernCard):
        """Add card to grid"""
        self.cards.append(card)
        
        # Connect signals
        card.clicked.connect(lambda: self._on_card_clicked(card))
        
        # Add to grid layout
        row = (len(self.cards) - 1) // self.cards_per_row
        col = (len(self.cards) - 1) % self.cards_per_row
        
        self.grid_layout.addWidget(card, row, col)
    
    def remove_card(self, card: ModernCard):
        """Remove card from grid"""
        if card in self.cards:
            self.cards.remove(card)
            self.grid_layout.removeWidget(card)
            card.deleteLater()
    
    def clear_cards(self):
        """Clear all cards"""
        for card in self.cards:
            self.grid_layout.removeWidget(card)
            card.deleteLater()
        self.cards.clear()
        self.selected_card = None
    
    def _on_card_clicked(self, card: ModernCard):
        """Handle card click"""
        # Update selection
        if self.selected_card:
            self.selected_card.set_selected(False)
        
        self.selected_card = card
        card.set_selected(True)
        
        # Emit signals
        self.card_selected.emit(card)
        self.card_clicked.emit(card)
    
    def set_cards_per_row(self, count: int):
        """Set number of cards per row"""
        self.cards_per_row = count
        self._rearrange_cards()
    
    def _rearrange_cards(self):
        """Rearrange cards in grid"""
        # Remove all cards from layout
        for card in self.cards:
            self.grid_layout.removeWidget(card)
        
        # Re-add cards in new arrangement
        for i, card in enumerate(self.cards):
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            self.grid_layout.addWidget(card, row, col)


class ModernListWidget(QWidget):
    """Modern list widget with card-based items"""
    
    # Signals
    item_selected = Signal(int, object)  # index, item_data
    item_clicked = Signal(int, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        self.selected_index = -1
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up list UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_layout.setSpacing(8)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
    
    def add_item(self, data: Dict[str, Any]):
        """Add item to list"""
        item_widget = self._create_item_widget(data)
        self.items.append({'data': data, 'widget': item_widget})
        
        self.content_layout.addWidget(item_widget)
    
    def _create_item_widget(self, data: Dict[str, Any]) -> QWidget:
        """Create item widget"""
        item_widget = QFrame()
        item_widget.setFrameStyle(QFrame.Box)
        item_widget.setObjectName("listItem")
        item_widget.setStyleSheet("""
            QFrame#listItem {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                padding: 12px;
            }
            
            QFrame#listItem:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
            
            QFrame#listItem[selected="true"] {
                border-color: #3498db;
                background-color: #e3f2fd;
            }
        """)
        
        # Layout
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Content
        content_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(data.get('title', ''))
        title_label.setObjectName("itemTitle")
        title_label.setStyleSheet("""
            QLabel#itemTitle {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
            }
        """)
        content_layout.addWidget(title_label)
        
        # Description
        if data.get('description'):
            desc_label = QLabel(data.get('description', ''))
            desc_label.setObjectName("itemDescription")
            desc_label.setStyleSheet("""
                QLabel#itemDescription {
                    font-size: 12px;
                    color: #7f8c8d;
                    margin-top: 4px;
                }
            """)
            desc_label.setWordWrap(True)
            content_layout.addWidget(desc_label)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        # Connect click event
        item_widget.mousePressEvent = lambda event: self._on_item_clicked(item_widget)
        
        return item_widget
    
    def _on_item_clicked(self, item_widget: QWidget):
        """Handle item click"""
        # Find item index
        for i, item in enumerate(self.items):
            if item['widget'] == item_widget:
                self._select_item(i)
                self.item_clicked.emit(i, item['data'])
                break
    
    def _select_item(self, index: int):
        """Select item by index"""
        if self.selected_index >= 0:
            self.items[self.selected_index]['widget'].setProperty("selected", "false")
            self.items[self.selected_index]['widget'].style().unpolish(self.items[self.selected_index]['widget'])
            self.items[self.selected_index]['widget'].style().polish(self.items[self.selected_index]['widget'])
        
        self.selected_index = index
        
        if index >= 0 and index < len(self.items):
            self.items[index]['widget'].setProperty("selected", "true")
            self.items[index]['widget'].style().unpolish(self.items[index]['widget'])
            self.items[index]['widget'].style().polish(self.items[index]['widget'])
            
            self.item_selected.emit(index, self.items[index]['data'])
    
    def clear_items(self):
        """Clear all items"""
        for item in self.items:
            self.content_layout.removeWidget(item['widget'])
            item['widget'].deleteLater()
        self.items.clear()
        self.selected_index = -1


class AnimatedButton(QPushButton):
    """Button with smooth animations"""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setup_animations()
        self.setup_styling()
    
    def setup_animations(self):
        """Set up button animations"""
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(150)
        self.scale_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def setup_styling(self):
        """Set up button styling"""
        self.setStyleSheet("""
            AnimatedButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }
            
            AnimatedButton:hover {
                background-color: #2980b9;
            }
            
            AnimatedButton:pressed {
                background-color: #21618c;
            }
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press with animation"""
        if event.button() == Qt.LeftButton:
            # Scale down animation
            self.scale_animation.setStartValue(self.geometry())
            scaled_rect = QRect(
                self.x() + 2, self.y() + 2,
                self.width() - 4, self.height() - 4
            )
            self.scale_animation.setEndValue(scaled_rect)
            self.scale_animation.start()
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release with animation"""
        if event.button() == Qt.LeftButton:
            # Scale back up animation
            self.scale_animation.setStartValue(self.geometry())
            self.scale_animation.setEndValue(QRect(
                self.x() - 2, self.y() - 2,
                self.width() + 4, self.height() + 4
            ))
            self.scale_animation.start()
        
        super().mouseReleaseEvent(event)


class ModernSearchBar(QWidget):
    """Modern search bar with animations"""
    
    # Signals
    text_changed = Signal(str)
    search_requested = Signal(str)
    
    def __init__(self, placeholder: str = "Search...", parent=None):
        super().__init__(parent)
        self.placeholder = placeholder
        
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Set up search bar UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.placeholder)
        self.search_input.setObjectName("searchInput")
        
        # Search button
        self.search_button = QPushButton("🔍")
        self.search_button.setObjectName("searchButton")
        
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_button)
        
        # Connect signals
        self.search_input.textChanged.connect(self.text_changed.emit)
        self.search_button.clicked.connect(self._on_search)
        self.search_input.returnPressed.connect(self._on_search)
    
    def setup_animations(self):
        """Set up search bar animations"""
        self.focus_animation = QPropertyAnimation(self.search_input, b"geometry")
        self.focus_animation.setDuration(200)
        self.focus_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def _on_search(self):
        """Handle search request"""
        text = self.search_input.text()
        self.search_requested.emit(text)
    
    def setStyleSheet(self, style):
        """Set custom stylesheet"""
        super().setStyleSheet(style)
        self.search_input.setStyleSheet("""
            QLineEdit#searchInput {
                background-color: white;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
            }
            
            QLineEdit#searchInput:focus {
                border-color: #3498db;
                outline: none;
            }
        """)
        
        self.search_button.setStyleSheet("""
            QPushButton#searchButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
            }
            
            QPushButton#searchButton:hover {
                background-color: #2980b9;
            }
        """)


def create_modern_card(title: str = "", content: str = "", parent=None) -> ModernCard:
    """Create a modern card widget"""
    return ModernCard(parent, title, content)


def create_card_grid(cards_per_row: int = 3, parent=None) -> CardGrid:
    """Create a card grid widget"""
    return CardGrid(parent, cards_per_row)


def create_modern_list(parent=None) -> ModernListWidget:
    """Create a modern list widget"""
    return ModernListWidget(parent)


def create_animated_button(text: str = "", parent=None) -> AnimatedButton:
    """Create an animated button"""
    return AnimatedButton(text, parent)


def create_modern_search_bar(placeholder: str = "Search...", parent=None) -> ModernSearchBar:
    """Create a modern search bar"""
    return ModernSearchBar(placeholder, parent)
