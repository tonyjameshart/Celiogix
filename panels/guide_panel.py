#!/usr/bin/env python3
"""
Guide Panel for Celiogix Application
Provides documentation and links for celiac disease management
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QPushButton, QGroupBox, QFrame, QTextEdit, QSplitter,
    QTreeWidget, QTreeWidgetItem, QHeaderView
)
from utils.custom_widgets import NoSelectionTreeWidget
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QPixmap, QPalette, QDesktopServices

from panels.base_panel import BasePanel
from panels.context_menu_mixin import GuideContextMenuMixin


class GuidePanel(GuideContextMenuMixin, BasePanel):
    """Guide panel providing documentation and celiac resources"""
    
    def __init__(self, master=None, app=None):
        super().__init__(master, app)
        # Clear the default layout from BasePanel
        if self.layout():
            QWidget().setLayout(self.layout())
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the guide panel UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Celiogix User Guide & Celiac Resources")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #1b5e20; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left side - App Documentation
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # App Documentation Section
        app_doc_group = QGroupBox("📱 App Documentation")
        app_doc_layout = QVBoxLayout(app_doc_group)
        
        # App features documentation
        app_features_text = QTextEdit()
        app_features_text.setReadOnly(True)
        app_features_text.setMaximumHeight(200)
        app_features_text.setHtml("""
        <h3>Getting Started with Celiogix</h3>
        <p><b>Cookbook Panel:</b> Manage your gluten-free recipes, import from web, scale ingredients, and track nutrition.</p>
        <p><b>Pantry Panel:</b> Track your gluten-free inventory, scan UPC codes for gluten safety, and monitor expiration dates.</p>
        <p><b>Shopping List:</b> Create organized shopping lists by store and category, with gluten-free item tracking.</p>
        <p><b>Menu Planner:</b> Plan your weekly meals with automatic shopping list generation and nutrition tracking.</p>
        <p><b>Health Log:</b> Track symptoms, Bristol Stool Scale, hydration, and identify gluten exposure patterns.</p>
        <p><b>Calendar:</b> Schedule appointments, track medication, and manage your celiac care routine.</p>
        """)
        app_doc_layout.addWidget(app_features_text)
        
        # Quick tips
        tips_text = QTextEdit()
        tips_text.setReadOnly(True)
        tips_text.setMaximumHeight(150)
        tips_text.setHtml("""
        <h4>💡 Quick Tips</h4>
        <ul>
        <li>Use Ctrl+1-7 to quickly switch between panels</li>
        <li>Right-click on any panel for context-specific actions</li>
        <li>Scan UPC codes in Pantry to check gluten safety</li>
        <li>Export your data regularly for backup</li>
        <li>Use the Health Log to track patterns and symptoms</li>
        </ul>
        """)
        app_doc_layout.addWidget(tips_text)
        
        left_layout.addWidget(app_doc_group)
        
        # Right side - Expandable Celiac Resources Tree
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create expandable tree widget
        self.resources_tree = NoSelectionTreeWidget()
        self.resources_tree.setHeaderLabel("Celiac Resources")
        self.resources_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #c8e6c9;
                border-radius: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
                text-decoration: none;
            }
            QTreeWidget::item:selected {
                background-color: #e8f5e8;
                color: #1b5e20;
                text-decoration: none;
            }
            QTreeWidget::item:hover {
                background-color: #f1f8e9;
            }
            QTreeWidget::branch {
                background-color: transparent;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuNSA2TDcuNSA2IiBzdHJva2U9IiMxYjVlMjAiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTYgNC41TDYgNy41IiBzdHJva2U9IiMxYjVlMjAiIHN0cm9rZS13aWR0aD0i1.5IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPHBhdGggZD0iTTQuNSA2TDcuNSA2IiBzdHJva2U9IiMxYjVlMjAiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
        """)
        
        # Create expandable sections
        self.setup_expandable_sections()
        
        right_layout.addWidget(self.resources_tree)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])  # Equal sizes
        
        # Footer
        footer_label = QLabel("💚 Celiogix - Your Celiac Disease Management Companion")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #2e7d32; font-style: italic; margin: 10px;")
        main_layout.addWidget(footer_label)
    
    def setup_expandable_sections(self):
        """Set up the expandable sections in the tree widget"""
        # Celiac 101 Section (TOP)
        celiac101_item = QTreeWidgetItem(self.resources_tree)
        celiac101_item.setText(0, "🧠 Celiac 101")
        celiac101_item.setExpanded(True)
        
        celiac101_links = [
            ("Understanding Celiac", "https://www.celiac.org/about-celiac-disease/what-is-celiac-disease/"),
            ("Celiac Insights", "https://www.beyondceliac.org/what-is-celiac-disease/"),
            ("Celiac Wellness", "https://www.healthline.com/health/celiac-disease"),
            ("Gluten-Free Wisdom", "https://gluten.org/learn/gluten-free/")
        ]
        
        for title, url in celiac101_links:
            link_item = QTreeWidgetItem(celiac101_item)
            link_item.setText(0, title)
            link_item.setData(0, Qt.UserRole, url)
            link_item.setFlags(link_item.flags() | Qt.ItemIsUserCheckable)
        
        # Managing Celiac Section (MIDDLE)
        managing_item = QTreeWidgetItem(self.resources_tree)
        managing_item.setText(0, "🔍 Managing Celiac")
        managing_item.setExpanded(True)
        
        managing_links = [
            ("Living with Celiac", "https://celiac.org/living-gluten-free/living-with-celiac-disease/"),
            ("Celiac Life Guide", "https://www.beyondceliac.org/living-with-celiac-disease/"),
            ("Celiac Support Hub", "https://www.celiac.org/"),
            ("Thriving Gluten-Free", "https://gluten.org/")
        ]
        
        for title, url in managing_links:
            link_item = QTreeWidgetItem(managing_item)
            link_item.setText(0, title)
            link_item.setData(0, Qt.UserRole, url)
            link_item.setFlags(link_item.flags() | Qt.ItemIsUserCheckable)
        
        # Celiac Survival Guide Section (BOTTOM)
        survival_item = QTreeWidgetItem(self.resources_tree)
        survival_item.setText(0, "🧭 Celiac Survival Guide")
        survival_item.setExpanded(True)
        
        survival_links = [
            ("Your Celiac Toolkit", "https://www.celiac.org/living-gluten-free/glutenfreediet/"),
            ("Mastering Celiac", "https://www.beyondceliac.org/living-with-celiac-disease/diet/"),
            ("Navigate Celiac", "https://celiac.org/living-gluten-free/glutenfreediet/"),
            ("Empower Your Gut", "https://www.healthline.com/health/celiac-disease")
        ]
        
        for title, url in survival_links:
            link_item = QTreeWidgetItem(survival_item)
            link_item.setText(0, title)
            link_item.setData(0, Qt.UserRole, url)
            link_item.setFlags(link_item.flags() | Qt.ItemIsUserCheckable)
        
        # Connect item click to open links
        self.resources_tree.itemDoubleClicked.connect(self.on_tree_item_clicked)
    
    def on_tree_item_clicked(self, item, column):
        """Handle tree item clicks to open links"""
        url = item.data(0, Qt.UserRole)
        if url:
            self.open_link(url)
    
    def open_link(self, url):
        """Open a URL in the default web browser"""
        try:
            QDesktopServices.openUrl(QUrl(url))
        except Exception as e:
            print(f"Error opening URL {url}: {e}")
    
    def refresh(self):
        """Refresh the guide panel"""
        # No specific refresh needed for guide panel
        pass
