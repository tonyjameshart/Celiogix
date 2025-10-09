# path: panels/cookbook/cookbook_panel.py
"""
Main Cookbook Panel for PySide6 Application
"""

from typing import Optional
from PySide6.QtCore import QMarginsF, Qt
from PySide6.QtGui import QFont, QPageLayout, QPageSize, QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrintPreviewDialog, QPrinter
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QProgressBar, QPushButton, QRadioButton, QScrollArea,
    QSlider, QSpinBox, QSplitter, QTableWidget, QTableWidgetItem,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)

from panels.base_panel import BasePanel
from panels.context_menu_mixin import CookbookContextMenuMixin
from utils.custom_widgets import NoSelectionTableWidget
from .recipe_manager import RecipeManager
from .recipe_ui_components import RecipeUIComponents
from .recipe_dialogs import RecipeDialogs
from .recipe_export import RecipeExport


class CookbookPanel(CookbookContextMenuMixin, BasePanel):
    """Cookbook panel for PySide6"""
    
    def __init__(self, master=None, app=None):
        super().__init__(master, app)
        self.recipe_manager = RecipeManager()
        self.ui_components = RecipeUIComponents()
        self.dialogs = RecipeDialogs()
        self.export_handler = RecipeExport()
        
        # UI state
        self.current_recipe_id = None
        self.recipe_cards = []
        self.recipe_data_storage = {}
    
    def setup_ui(self):
        """Set up the cookbook panel UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Navigation and search
        self.setup_cookbook_navigation(main_layout)
        
        # Recipe display area
        self.setup_recipe_display_area(main_layout)
        
        # Action buttons
        self.setup_action_buttons(main_layout)
        
        # Load initial data
        self.load_recipes()
    
    def setup_cookbook_navigation(self, parent_layout):
        """Set up navigation and search components"""
        nav_widget = self.ui_components.create_navigation_widget()
        parent_layout.addWidget(nav_widget)
    
    def setup_recipe_display_area(self, parent_layout):
        """Set up recipe display area"""
        display_widget = self.ui_components.create_recipe_display_area()
        parent_layout.addWidget(display_widget)
    
    def setup_action_buttons(self, parent_layout):
        """Set up action buttons"""
        button_widget = self.ui_components.create_action_buttons()
        parent_layout.addWidget(button_widget)
    
    def refresh(self):
        """Refresh panel data"""
        self.load_recipes()
    
    def load_recipes(self):
        """Load recipes from database"""
        self.recipe_manager.load_recipes()
        self.refresh_recipe_display()
    
    def refresh_recipe_display(self):
        """Refresh the recipe display"""
        recipes = self.get_filtered_recipes()
        if self.get_view_mode() == "grid":
            self.display_grid_view(recipes)
        else:
            self.display_list_view(recipes)
    
    def get_filtered_recipes(self):
        """Get filtered recipes based on current filters"""
        return self.recipe_manager.get_filtered_recipes()
    
    def get_view_mode(self):
        """Get current view mode"""
        return getattr(self, 'view_mode', 'grid')
    
    def set_view_mode(self, mode):
        """Set view mode"""
        self.view_mode = mode
        self.refresh_recipe_display()
    
    def display_grid_view(self, recipes):
        """Display recipes in grid view"""
        # Implementation moved to UI components
        self.ui_components.display_grid_view(recipes)
    
    def display_list_view(self, recipes):
        """Display recipes in list view"""
        # Implementation moved to UI components
        self.ui_components.display_list_view(recipes)
    
    def add_recipe(self):
        """Add a new recipe"""
        recipe_data = self.dialogs.show_add_recipe_dialog()
        if recipe_data:
            recipe_id = self.recipe_manager.save_recipe(recipe_data)
            self.refresh()
            return recipe_id
        return None
    
    def edit_recipe(self):
        """Edit selected recipe"""
        if not self.current_recipe_id:
            return
        
        recipe_data = self.recipe_manager.get_recipe(self.current_recipe_id)
        if recipe_data:
            updated_data = self.dialogs.show_edit_recipe_dialog(recipe_data)
            if updated_data:
                self.recipe_manager.update_recipe(self.current_recipe_id, updated_data)
                self.refresh()
    
    def delete_recipe(self):
        """Delete selected recipe"""
        if not self.current_recipe_id:
            return
        
        if self.dialogs.confirm_delete_recipe():
            self.recipe_manager.delete_recipe(self.current_recipe_id)
            self.current_recipe_id = None
            self.refresh()
    
    def view_recipe(self):
        """View recipe details"""
        if not self.current_recipe_id:
            return
        
        recipe_data = self.recipe_manager.get_recipe(self.current_recipe_id)
        if recipe_data:
            self.dialogs.show_recipe_view_dialog(recipe_data)
    
    def export_recipes(self):
        """Export recipes"""
        recipes = self.get_filtered_recipes()
        self.export_handler.export_recipes(recipes)
    
    def import_from_web(self):
        """Import recipe from web"""
        url = self.dialogs.get_web_url()
        if url:
            recipe_data = self.recipe_manager.scrape_recipe_from_web(url)
            if recipe_data:
                self.recipe_manager.save_recipe(recipe_data)
                self.refresh()
    
    def filter_recipes(self):
        """Filter recipes based on search criteria"""
        self.refresh_recipe_display()
    
    def sort_recipes(self):
        """Sort recipes based on selected criteria"""
        self.refresh_recipe_display()
    
    def on_selection_changed(self):
        """Handle selection changes"""
        # Implementation for selection handling
        pass
