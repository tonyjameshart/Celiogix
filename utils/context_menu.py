# path: utils/context_menu.py
"""
Context Menu System for PySide6 Application

Provides right-click context menus with panel-specific actions.
"""

from typing import Dict, List, Callable, Optional
from PySide6.QtWidgets import QMenu, QWidget
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


class ContextMenuManager:
    """Manages context menus for different panels"""
    
    def __init__(self):
        self.menu_actions = {}
        self.setup_default_actions()
    
    def setup_default_actions(self):
        """Set up default context menu actions for all panels"""
        # Common actions for all panels
        self.common_actions = {
            'refresh': {
                'text': 'Refresh',
                'shortcut': 'F5',
                'icon': None,
                'enabled': True
            },
            'export': {
                'text': 'Export Data',
                'shortcut': 'Ctrl+E',
                'icon': None,
                'enabled': True
            },
            'print': {
                'text': 'Print',
                'shortcut': 'Ctrl+P',
                'icon': None,
                'enabled': True
            },
            'help': {
                'text': 'Help',
                'shortcut': 'F1',
                'icon': None,
                'enabled': True
            }
        }
        
        # Panel-specific actions
        self.panel_actions = {
            'pantry': {
                'add_item': {
                    'text': 'Add New Item',
                    'shortcut': 'Ctrl+N',
                    'icon': None,
                    'enabled': True
                },
                'delete_selected': {
                    'text': 'Delete Selected',
                    'shortcut': 'Delete',
                    'icon': None,
                    'enabled': True
                },
                'edit_item': {
                    'text': 'Edit Item',
                    'shortcut': 'F2',
                    'icon': None,
                    'enabled': True
                },
                'search': {
                    'text': 'Search Items',
                    'shortcut': 'Ctrl+F',
                    'icon': None,
                    'enabled': True
                }
            },
            'health_log': {
                'add_entry': {
                    'text': 'Add Health Entry',
                    'shortcut': 'Ctrl+N',
                    'icon': None,
                    'enabled': True
                },
                'analyze_patterns': {
                    'text': 'Analyze Patterns',
                    'shortcut': 'Ctrl+A',
                    'icon': None,
                    'enabled': True
                },
                'export_report': {
                    'text': 'Export Health Report',
                    'shortcut': 'Ctrl+R',
                    'icon': None,
                    'enabled': True
                },
                'view_calendar': {
                    'text': 'View Calendar',
                    'shortcut': 'Ctrl+C',
                    'icon': None,
                    'enabled': True
                }
            },
            'cookbook': {
                'add_recipe': {
                    'text': 'Add New Recipe',
                    'shortcut': 'Ctrl+N',
                    'icon': None,
                    'enabled': True
                },
                'edit_recipe': {
                    'text': 'Edit Recipe',
                    'shortcut': 'F2',
                    'icon': None,
                    'enabled': True
                },
                'delete_recipe': {
                    'text': 'Delete Recipe',
                    'shortcut': 'Delete',
                    'icon': None,
                    'enabled': True
                },
                'add_to_menu': {
                    'text': 'Add to Menu Plan',
                    'shortcut': 'Ctrl+M',
                    'icon': None,
                    'enabled': True
                },
                'add_to_shopping': {
                    'text': 'Add to Shopping List',
                    'shortcut': 'Ctrl+S',
                    'icon': None,
                    'enabled': True
                },
                'export_txt': {
                    'text': 'Export as Text',
                    'shortcut': 'Ctrl+E',
                    'icon': None,
                    'enabled': True
                },
                'export_html': {
                    'text': 'Export as HTML',
                    'shortcut': 'Ctrl+H',
                    'icon': None,
                    'enabled': True
                }
            },
            'shopping_list': {
                'add_item': {
                    'text': 'Add Item',
                    'shortcut': 'Ctrl+N',
                    'icon': None,
                    'enabled': True
                },
                'mark_purchased': {
                    'text': 'Mark as Purchased',
                    'shortcut': 'Ctrl+M',
                    'icon': None,
                    'enabled': True
                },
                'clear_purchased': {
                    'text': 'Clear Purchased Items',
                    'shortcut': 'Ctrl+L',
                    'icon': None,
                    'enabled': True
                },
                'generate_from_recipes': {
                    'text': 'Generate from Recipes',
                    'shortcut': 'Ctrl+G',
                    'icon': None,
                    'enabled': True
                }
            },
            'menu': {
                'plan_week': {
                    'text': 'Plan This Week',
                    'shortcut': 'Ctrl+W',
                    'icon': None,
                    'enabled': True
                },
                'add_meal': {
                    'text': 'Add Meal',
                    'shortcut': 'Ctrl+N',
                    'icon': None,
                    'enabled': True
                },
                'generate_shopping': {
                    'text': 'Generate Shopping List',
                    'shortcut': 'Ctrl+G',
                    'icon': None,
                    'enabled': True
                },
                'nutritional_analysis': {
                    'text': 'Nutritional Analysis',
                    'shortcut': 'Ctrl+N',
                    'icon': None,
                    'enabled': True
                }
            },
            'calendar': {
                'go_to_today': {
                    'text': 'Go to Today',
                    'shortcut': 'Ctrl+T',
                    'icon': None,
                    'enabled': True
                },
                'add_appointment': {
                    'text': 'Add Appointment',
                    'shortcut': 'Ctrl+N',
                    'icon': None,
                    'enabled': True
                },
                'view_health_summary': {
                    'text': 'View Health Summary',
                    'shortcut': 'Ctrl+H',
                    'icon': None,
                    'enabled': True
                },
                'export_calendar': {
                    'text': 'Export Calendar',
                    'shortcut': 'Ctrl+E',
                    'icon': None,
                    'enabled': True
                }
            },
            'csv_import': {
                'browse_file': {
                    'text': 'Browse for File',
                    'shortcut': 'Ctrl+O',
                    'icon': None,
                    'enabled': True
                },
                'validate_file': {
                    'text': 'Validate File',
                    'shortcut': 'Ctrl+V',
                    'icon': None,
                    'enabled': True
                },
                'import_data': {
                    'text': 'Import Data',
                    'shortcut': 'Ctrl+I',
                    'icon': None,
                    'enabled': True
                },
                'clear_results': {
                    'text': 'Clear Results',
                    'shortcut': 'Ctrl+L',
                    'icon': None,
                    'enabled': True
                }
            },
            'settings': {
                'backup_data': {
                    'text': 'Backup Data',
                    'shortcut': 'Ctrl+B',
                    'icon': None,
                    'enabled': True
                },
                'restore_data': {
                    'text': 'Restore Data',
                    'shortcut': 'Ctrl+R',
                    'icon': None,
                    'enabled': True
                },
                'reset_settings': {
                    'text': 'Reset Settings',
                    'shortcut': 'Ctrl+Shift+R',
                    'icon': None,
                    'enabled': True
                },
                'database_info': {
                    'text': 'Database Information',
                    'shortcut': 'Ctrl+D',
                    'icon': None,
                    'enabled': True
                }
            }
        }
    
    def create_context_menu(self, panel_name: str, parent_widget: QWidget, 
                          action_callbacks: Dict[str, Callable]) -> QMenu:
        """Create a context menu for a specific panel"""
        menu = QMenu(parent_widget)
        
        # Apply styling to fix black box issue
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px;
                color: #333333;
                font-size: 12px;
            }
            QMenu::item {
                padding: 6px 12px;
                margin: 1px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 4px 8px;
            }
        """)
        
        # Add common actions
        for action_key, action_info in self.common_actions.items():
            if action_key in action_callbacks:
                action = QAction(action_info['text'], parent_widget)
                action.setShortcut(action_info['shortcut'])
                action.setEnabled(action_info['enabled'])
                action.triggered.connect(action_callbacks[action_key])
                menu.addAction(action)
        
        # Add separator if we have both common and panel-specific actions
        if panel_name in self.panel_actions and any(
            key in action_callbacks for key in self.panel_actions[panel_name]
        ):
            menu.addSeparator()
        
        # Add panel-specific actions
        if panel_name in self.panel_actions:
            for action_key, action_info in self.panel_actions[panel_name].items():
                if action_key in action_callbacks:
                    action = QAction(action_info['text'], parent_widget)
                    action.setShortcut(action_info['shortcut'])
                    action.setEnabled(action_info['enabled'])
                    action.triggered.connect(action_callbacks[action_key])
                    menu.addAction(action)
        
        return menu
    
    def get_available_actions(self, panel_name: str) -> List[str]:
        """Get list of available actions for a panel"""
        actions = list(self.common_actions.keys())
        if panel_name in self.panel_actions:
            actions.extend(self.panel_actions[panel_name].keys())
        return actions


# Global context menu manager instance
context_menu_manager = ContextMenuManager()
