# path: utils/custom_delegates.py
"""
Custom QStyledItemDelegate implementations for Celiogix application
"""

from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QApplication, QStyle
from PySide6.QtGui import QFont, QPalette
from PySide6.QtCore import Qt


class CleanSelectionDelegate(QStyledItemDelegate):
    """
    Paints items without the default focus/selection border.
    Selected items get a filled background and bold text.
    Drop-in: table.setItemDelegate(CleanSelectionDelegate())
    """
    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        selected = bool(opt.state & QStyle.State_Selected)

        # Remove focus state so style doesn't draw a dashed/focused border
        opt.state &= ~QStyle.State_HasFocus

        # Make font bold when selected
        font = QFont(opt.font)
        font.setBold(selected)
        opt.font = font

        if selected:
            # Fill background using palette highlight (keeps theme consistency)
            painter.fillRect(opt.rect, opt.palette.highlight())

            # Ensure text color uses highlightedText for readability
            opt.palette.setColor(opt.palette.ColorRole.Text, opt.palette.highlightedText().color())

        # Let the style draw the item content (text, icon, etc.) without drawing focus rect.
        style = QApplication.style() or QStyle()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter)


class NoBorderDelegate(QStyledItemDelegate):
    """Custom delegate that suppresses selection borders and focus indicators"""
    
    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        # Remove focus state so style doesn't draw a dashed/focused border
        opt.state &= ~QStyle.State_HasFocus

        # Let the style draw the item content without focus rect
        style = QApplication.style() or QStyle()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter)


class TableWidgetCustomDelegate(QStyledItemDelegate):
    """Enhanced custom delegate for table widgets with better control over styling"""
    
    def __init__(self, parent=None, suppress_borders=True, suppress_focus=True):
        super().__init__(parent)
        self.suppress_borders = suppress_borders
        self.suppress_focus = suppress_focus
    
    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        # Remove focus rectangle
        if self.suppress_focus:
            opt.state &= ~QStyle.State_HasFocus

        # Let the style draw the item content
        style = QApplication.style() or QStyle()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter)
    
    def drawFocus(self, painter, option, rect):
        # Override to prevent focus rectangle drawing
        if self.suppress_focus:
            return
        super().drawFocus(painter, option, rect)


class MenuTableDelegate(QStyledItemDelegate):
    """Specialized delegate for menu table with custom selection styling"""
    
    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        selected = bool(opt.state & QStyle.State_Selected)

        # Remove focus state so style doesn't draw a dashed/focused border
        opt.state &= ~QStyle.State_HasFocus

        # Make font bold when selected
        font = QFont(opt.font)
        font.setBold(selected)
        opt.font = font

        if selected:
            # Fill background using palette highlight (keeps theme consistency)
            painter.fillRect(opt.rect, opt.palette.highlight())

            # Ensure text color uses highlightedText for readability
            opt.palette.setColor(opt.palette.ColorRole.Text, opt.palette.highlightedText().color())

        # Let the style draw the item content (text, icon, etc.) without drawing focus rect.
        style = QApplication.style() or QStyle()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter)
    
    def drawFocus(self, painter, option, rect):
        # Completely suppress focus rectangle
        pass