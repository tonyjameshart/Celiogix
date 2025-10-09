# path: panels/cookbook/recipe_ui_components.py
"""
UI components for recipe display and interaction
"""

from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTreeWidget, QTreeWidgetItem, QScrollArea,
    QTableWidget, QTableWidgetItem, QSplitter
)
from PySide6.QtCore import Qt


class RecipeUIComponents:
    """UI components for recipe display"""
    
    def __init__(self):
        self.navigation_tree = None
        self.search_edit = None
        self.category_filter_combo = None
        self.view_mode_buttons = None
        self.recipe_cards_container = None
    
    def create_navigation_widget(self) -> QWidget:
        """Create navigation and search widget"""
        nav_widget = QWidget()
        layout = QVBoxLayout(nav_widget)
        
        # Category navigation tree
        self.navigation_tree = QTreeWidget()
        self.navigation_tree.setHeaderHidden(True)
        self.navigation_tree.setMaximumHeight(200)
        layout.addWidget(self.navigation_tree)
        
        # Search and filter bar
        search_filter_widget = self.create_search_filter_bar()
        layout.addWidget(search_filter_widget)
        
        return nav_widget
    
    def create_search_filter_bar(self) -> QWidget:
        """Create search and filter bar"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Search box
        layout.addWidget(QLabel("🔍"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search recipes...")
        layout.addWidget(self.search_edit)
        
        # Category filter
        layout.addWidget(QLabel("Category:"))
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItem("All Categories")
        layout.addWidget(self.category_filter_combo)
        
        # View mode buttons
        self.view_mode_buttons = self.create_view_mode_buttons()
        layout.addWidget(self.view_mode_buttons)
        
        layout.addStretch()
        return widget
    
    def create_view_mode_buttons(self) -> QWidget:
        """Create view mode toggle buttons"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        grid_btn = QPushButton("Grid")
        grid_btn.setCheckable(True)
        grid_btn.setChecked(True)
        
        list_btn = QPushButton("List")
        list_btn.setCheckable(True)
        
        layout.addWidget(QLabel("View:"))
        layout.addWidget(grid_btn)
        layout.addWidget(list_btn)
        
        return widget
    
    def create_recipe_display_area(self) -> QWidget:
        """Create recipe display area"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Recipe cards container
        self.recipe_cards_container = QScrollArea()
        self.recipe_cards_container.setWidgetResizable(True)
        self.recipe_cards_container.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.recipe_cards_container.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layout.addWidget(self.recipe_cards_container)
        
        return widget
    
    def create_action_buttons(self) -> QWidget:
        """Create action buttons widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        add_btn = QPushButton("Add Recipe")
        edit_btn = QPushButton("Edit Recipe")
        delete_btn = QPushButton("Delete Recipe")
        view_btn = QPushButton("View Recipe")
        export_btn = QPushButton("Export")
        import_btn = QPushButton("Import from Web")
        
        layout.addWidget(add_btn)
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addWidget(view_btn)
        layout.addWidget(export_btn)
        layout.addWidget(import_btn)
        layout.addStretch()
        
        return widget
    
    def display_grid_view(self, recipes: List[Dict[str, Any]]):
        """Display recipes in grid view"""
        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)
        
        # Create recipe cards in grid
        cards_per_row = 3
        current_row_layout = None
        
        for i, recipe in enumerate(recipes):
            if i % cards_per_row == 0:
                current_row_layout = QHBoxLayout()
                layout.addLayout(current_row_layout)
            
            card = self.create_recipe_card(recipe)
            current_row_layout.addWidget(card)
        
        # Add stretch to last row if needed
        if current_row_layout:
            current_row_layout.addStretch()
        
        layout.addStretch()
        
        self.recipe_cards_container.setWidget(container_widget)
    
    def display_list_view(self, recipes: List[Dict[str, Any]]):
        """Display recipes in list view"""
        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)
        
        for recipe in recipes:
            list_item = self.create_recipe_list_item(recipe)
            layout.addWidget(list_item)
        
        layout.addStretch()
        
        self.recipe_cards_container.setWidget(container_widget)
    
    def create_recipe_card(self, recipe: Dict[str, Any]) -> QWidget:
        """Create a recipe card widget"""
        card = QWidget()
        card.setFixedSize(300, 200)
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                margin: 5px;
            }
            QWidget:hover {
                border-color: #3498db;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Recipe image placeholder
        image_label = QLabel()
        image_label.setFixedHeight(120)
        image_label.setStyleSheet("background-color: #f0f0f0; border-radius: 8px;")
        image_label.setText("📷")
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)
        
        # Recipe name
        name_label = QLabel(recipe.get('name', 'Untitled Recipe'))
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Recipe details
        details_label = QLabel(f"⏱️ {recipe.get('prep_time', 0)} min | 👥 {recipe.get('servings', 1)} servings")
        details_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(details_label)
        
        # Favorite indicator
        if recipe.get('is_favorite'):
            fav_label = QLabel("⭐")
            fav_label.setAlignment(Qt.AlignRight)
            layout.addWidget(fav_label)
        
        return card
    
    def create_recipe_list_item(self, recipe: Dict[str, Any]) -> QWidget:
        """Create a recipe list item widget"""
        item = QWidget()
        item.setFixedHeight(80)
        item.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                margin: 2px;
            }
            QWidget:hover {
                background-color: #f8f9fa;
                border-color: #3498db;
            }
        """)
        
        layout = QHBoxLayout(item)
        
        # Recipe image
        image_label = QLabel()
        image_label.setFixedSize(60, 60)
        image_label.setStyleSheet("background-color: #f0f0f0; border-radius: 4px;")
        image_label.setText("📷")
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)
        
        # Recipe details
        details_layout = QVBoxLayout()
        
        name_label = QLabel(recipe.get('name', 'Untitled Recipe'))
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        details_layout.addWidget(name_label)
        
        desc_label = QLabel(recipe.get('description', '')[:100] + '...' if len(recipe.get('description', '')) > 100 else recipe.get('description', ''))
        desc_label.setStyleSheet("color: #666; font-size: 12px;")
        details_layout.addWidget(desc_label)
        
        layout.addLayout(details_layout)
        layout.addStretch()
        
        # Favorite indicator
        if recipe.get('is_favorite'):
            fav_label = QLabel("⭐")
            fav_label.setStyleSheet("font-size: 16px;")
            layout.addWidget(fav_label)
        
        return item
    
    def load_category_navigation(self, categories: List[Dict[str, Any]]):
        """Load categories into navigation tree"""
        if not self.navigation_tree:
            return
        
        self.navigation_tree.clear()
        
        # Add "All Recipes" item
        all_item = QTreeWidgetItem(self.navigation_tree)
        all_item.setText(0, "📚 All Recipes")
        all_item.setData(0, Qt.UserRole, None)
        
        # Add categories
        for category in categories:
            item = QTreeWidgetItem(self.navigation_tree)
            item.setText(0, f"{category.get('icon', '📁')} {category.get('name', '')}")
            item.setData(0, Qt.UserRole, category.get('id'))
        
        self.navigation_tree.expandAll()
    
    def populate_category_filter(self, categories: List[Dict[str, Any]]):
        """Populate category filter combo box"""
        if not self.category_filter_combo:
            return
        
        self.category_filter_combo.clear()
        self.category_filter_combo.addItem("All Categories")
        
        for category in categories:
            self.category_filter_combo.addItem(
                f"{category.get('icon', '📁')} {category.get('name', '')}",
                category.get('id')
            )
