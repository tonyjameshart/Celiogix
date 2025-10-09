# path: panels/context_menu_mixin.py
"""
Context Menu Mixin for PySide6 Panels

Provides right-click context menu functionality to panels.
"""

from typing import Dict, Callable
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QContextMenuEvent

from utils.context_menu import context_menu_manager


class ContextMenuMixin:
    """Mixin class to add context menu functionality to panels"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context_menu = None
        self.action_callbacks = {}
        self.setup_context_menu()
    
    def setup_context_menu(self):
        """Set up the context menu for this panel"""
        # Enable context menu events
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Get panel name from class name
        panel_name = self.__class__.__name__.lower().replace('panelpyside6', '').replace('panel', '')
        
        # Set up action callbacks
        self.setup_action_callbacks()
        
        # Create context menu
        self.context_menu = context_menu_manager.create_context_menu(
            panel_name, self, self.action_callbacks
        )
    
    def setup_action_callbacks(self):
        """Set up action callbacks - to be overridden by subclasses"""
        # Default callbacks that can be overridden
        self.action_callbacks = {
            'refresh': self.safe_refresh,
            'export': self.export_data,
            'print': self.print_data,
            'help': self.show_help
        }
    
    def show_context_menu(self, position):
        """Show the context menu at the specified position"""
        if self.context_menu:
            # Update action states before showing menu
            self.update_context_menu_states()
            
            # Show menu at cursor position
            global_pos = self.mapToGlobal(position)
            self.context_menu.exec(global_pos)
    
    def update_context_menu_states(self):
        """Update the enabled/disabled state of context menu actions"""
        # Override in subclasses to enable/disable actions based on current state
        pass
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        """Handle context menu event"""
        self.show_context_menu(event.pos())
        event.accept()
    
    # Default action implementations - can be overridden by subclasses
    def refresh(self):
        """Refresh panel data"""
        if hasattr(self, 'refresh') and callable(getattr(self, 'refresh')):
            self.refresh()
    
    def export_data(self):
        """Export panel data"""
        print(f"Export data for {self.__class__.__name__}")
        # Override in subclasses for specific export functionality
    
    def print_data(self):
        """Print panel data"""
        print(f"Print data for {self.__class__.__name__}")
        # Override in subclasses for specific print functionality
    
    def show_help(self):
        """Show help for this panel"""
        print(f"Show help for {self.__class__.__name__}")
        # Override in subclasses for specific help functionality
    
    def safe_refresh(self):
        """Safe refresh method that prevents recursion"""
        try:
            # Check if we're already refreshing to prevent recursion
            if hasattr(self, '_refreshing') and self._refreshing:
                return
            
            self._refreshing = True
            self.refresh()
        except Exception as e:
            print(f"Error refreshing panel: {str(e)}")
        finally:
            self._refreshing = False


class PantryContextMenuMixin(ContextMenuMixin):
    """Context menu mixin for pantry panel"""
    
    def setup_action_callbacks(self):
        """Set up pantry-specific action callbacks"""
        super().setup_action_callbacks()
        self.action_callbacks.update({
            'add_item': self.add_new_item,
            'delete_selected': self.delete_selected_item,
            'edit_item': self.edit_selected_item,
            'search': self.focus_search
        })
    
    def add_new_item(self):
        """Add new pantry item"""
        if hasattr(self, 'add_item') and callable(getattr(self, 'add_item')):
            self.add_item()
    
    def delete_selected_item(self):
        """Delete selected pantry item"""
        if hasattr(self, 'delete_item') and callable(getattr(self, 'delete_item')):
            self.delete_item()
    
    def edit_selected_item(self):
        """Edit selected pantry item"""
        if hasattr(self, 'edit_item') and callable(getattr(self, 'edit_item')):
            self.edit_item()
    
    def focus_search(self):
        """Focus on search field"""
        if hasattr(self, 'search_edit'):
            self.search_edit.setFocus()


class HealthLogContextMenuMixin(ContextMenuMixin):
    """Context menu mixin for health log panel"""
    
    def setup_action_callbacks(self):
        """Set up health log-specific action callbacks"""
        super().setup_action_callbacks()
        self.action_callbacks.update({
            'add_entry': self.add_health_entry,
            'analyze_patterns': self.analyze_symptom_patterns,
            'export_report': self.export_health_report,
            'view_calendar': self.view_health_calendar
        })
    
    def add_health_entry(self):
        """Add new health log entry"""
        if hasattr(self, 'add_entry') and callable(getattr(self, 'add_entry')):
            self.add_entry()
    
    def analyze_symptom_patterns(self):
        """Analyze symptom patterns"""
        if hasattr(self, 'analyze_patterns') and callable(getattr(self, 'analyze_patterns')):
            self.analyze_patterns()
    
    def export_health_report(self):
        """Export health report"""
        print("Export health report")
    
    def view_health_calendar(self):
        """View health calendar"""
        print("View health calendar")


class CookbookContextMenuMixin(ContextMenuMixin):
    """Context menu mixin for cookbook panel"""
    
    def setup_action_callbacks(self):
        """Set up cookbook-specific action callbacks"""
        super().setup_action_callbacks()
        self.action_callbacks.update({
            'add_recipe': self.add_new_recipe,
            'edit_recipe': self.edit_selected_recipe,
            'delete_recipe': self.delete_selected_recipe,
            'add_to_menu': self.add_recipe_to_menu,
            'add_to_shopping': self.add_recipe_to_shopping,
            'export_txt': self.export_recipe_txt,
            'export_html': self.export_recipe_html
        })
    
    def add_new_recipe(self):
        """Add new recipe"""
        if hasattr(self, 'add_recipe') and callable(getattr(self, 'add_recipe')):
            self.add_recipe()
    
    def edit_selected_recipe(self):
        """Edit selected recipe"""
        if hasattr(self, 'edit_recipe') and callable(getattr(self, 'edit_recipe')):
            self.edit_recipe()
    
    def delete_selected_recipe(self):
        """Delete selected recipe"""
        if hasattr(self, 'delete_recipe') and callable(getattr(self, 'delete_recipe')):
            self.delete_recipe()
    
    def add_recipe_to_menu(self):
        """Add recipe to menu plan"""
        print("Add recipe to menu plan")
    
    def add_recipe_to_shopping(self):
        """Add recipe to shopping list"""
        print("Add recipe to shopping list")
    
    def export_recipe_txt(self):
        """Export recipe as text"""
        if hasattr(self, '_export_recipe_txt') and callable(getattr(self, '_export_recipe_txt')):
            self._export_recipe_txt()
    
    def export_recipe_html(self):
        """Export recipe as HTML"""
        if hasattr(self, '_export_recipe_html') and callable(getattr(self, '_export_recipe_html')):
            self._export_recipe_html()


class ShoppingListContextMenuMixin(ContextMenuMixin):
    """Context menu mixin for shopping list panel"""
    
    def setup_action_callbacks(self):
        """Set up shopping list-specific action callbacks"""
        super().setup_action_callbacks()
        self.action_callbacks.update({
            'add_item': self.add_shopping_item,
            'mark_purchased': self.mark_items_purchased,
            'clear_purchased': self.clear_purchased_items,
            'generate_from_recipes': self.generate_from_recipes
        })
    
    def add_shopping_item(self):
        """Add shopping item"""
        if hasattr(self, 'add_item') and callable(getattr(self, 'add_item')):
            self.add_item()
    
    def mark_items_purchased(self):
        """Mark items as purchased"""
        if hasattr(self, 'mark_purchased') and callable(getattr(self, 'mark_purchased')):
            self.mark_purchased()
    
    def clear_purchased_items(self):
        """Clear purchased items"""
        if hasattr(self, 'clear_purchased') and callable(getattr(self, 'clear_purchased')):
            self.clear_purchased()
    
    def generate_from_recipes(self):
        """Generate shopping list from recipes"""
        print("Generate shopping list from recipes")


class MenuContextMenuMixin(ContextMenuMixin):
    """Context menu mixin for menu panel"""
    
    def setup_action_callbacks(self):
        """Set up menu-specific action callbacks"""
        super().setup_action_callbacks()
        self.action_callbacks.update({
            'plan_week': self.plan_this_week,
            'add_meal': self.add_meal,
            'generate_shopping': self.generate_shopping_list,
            'nutritional_analysis': self.nutritional_analysis
        })
    
    def plan_this_week(self):
        """Plan this week's meals"""
        print("Plan this week's meals")
    
    def add_meal(self):
        """Add meal to plan"""
        print("Add meal to plan")
    
    def generate_shopping_list(self):
        """Generate shopping list from menu"""
        print("Generate shopping list from menu")
    
    def nutritional_analysis(self):
        """Perform nutritional analysis"""
        print("Perform nutritional analysis")


class CalendarContextMenuMixin(ContextMenuMixin):
    """Context menu mixin for calendar panel"""
    
    def setup_action_callbacks(self):
        """Set up calendar-specific action callbacks"""
        super().setup_action_callbacks()
        self.action_callbacks.update({
            'go_to_today': self.go_to_today,
            'add_appointment': self.add_appointment,
            'view_health_summary': self.view_health_summary,
            'export_calendar': self.export_calendar
        })
    
    def go_to_today(self):
        """Go to today's date"""
        if hasattr(self, 'go_to_today') and callable(getattr(self, 'go_to_today')):
            self.go_to_today()
    
    def add_appointment(self):
        """Add appointment"""
        if hasattr(self, 'add_appointment') and callable(getattr(self, 'add_appointment')):
            self.add_appointment()
    
    def view_health_summary(self):
        """View health summary"""
        print("View health summary")
    
    def export_calendar(self):
        """Export calendar"""
        print("Export calendar")


class CSVImportContextMenuMixin(ContextMenuMixin):
    """Context menu mixin for CSV import panel"""
    
    def setup_action_callbacks(self):
        """Set up CSV import-specific action callbacks"""
        super().setup_action_callbacks()
        self.action_callbacks.update({
            'browse_file': self.browse_for_file,
            'validate_file': self.validate_file,
            'import_data': self.import_csv,
            'clear_results': self.clear_form
        })
    
    def browse_for_file(self):
        """Browse for CSV file"""
        if hasattr(self, 'browse_file') and callable(getattr(self, 'browse_file')):
            self.browse_file()
    
    def validate_file(self):
        """Validate CSV file"""
        if hasattr(self, 'validate_file') and callable(getattr(self, 'validate_file')):
            self.validate_file()
    
    def import_csv(self):
        """Import CSV data"""
        if hasattr(self, 'import_csv') and callable(getattr(self, 'import_csv')):
            self.import_csv()
    
    def clear_form(self):
        """Clear form"""
        if hasattr(self, 'clear_form') and callable(getattr(self, 'clear_form')):
            self.clear_form()


class SettingsContextMenuMixin(ContextMenuMixin):
    """Context menu mixin for settings panel"""
    
    def setup_action_callbacks(self):
        """Set up settings-specific action callbacks"""
        super().setup_action_callbacks()
        self.action_callbacks.update({
            'backup_data': self.backup_database,
            'restore_data': self.restore_database,
            'reset_settings': self.reset_settings,
            'database_info': self.show_database_info
        })
    
    def backup_database(self):
        """Backup database"""
        print("Backup database")
    
    def restore_database(self):
        """Restore database"""
        print("Restore database")
    
    def reset_settings(self):
        """Reset settings"""
        print("Reset settings")
    
    def show_database_info(self):
        """Show database information"""
        print("Show database information")


class GuideContextMenuMixin(ContextMenuMixin):
    """Context menu mixin for Guide panel"""
    
    def setup_action_callbacks(self):
        """Set up action callbacks for Guide panel"""
        self.action_callbacks = {
            'refresh': self.refresh_guide,
            'export_docs': self.export_documentation,
            'print_guide': self.print_guide,
            'copy_links': self.copy_resource_links
        }
    
    def refresh_guide(self):
        """Refresh the guide content"""
        print("Refreshing guide content")
        self.refresh()
    
    def export_documentation(self):
        """Export documentation to file"""
        print("Exporting documentation")
    
    def print_guide(self):
        """Print the guide"""
        print("Printing guide")
    
    def copy_resource_links(self):
        """Copy resource links to clipboard"""
        print("Copying resource links to clipboard")
