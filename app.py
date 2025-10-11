# path: app_pyside6_working.py - Working PySide6 application
from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QStatusBar, QMenuBar, QMenu, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QAction

# Import existing PySide6 panels
from panels.pantry_panel import PantryPanel
from panels.health_log_panel import HealthLogPanel
from panels.cookbook_panel import CookbookPanel
from panels.shopping_list_panel import ShoppingListPanel
from panels.menu_panel import MenuPanel
from panels.calendar_panel import CalendarPanel
from panels.guide_panel import GuidePanel
from panels.settings_panel import SettingsPanel

# Import sync manager
from core.sync_manager import SyncManager

# Import theme engine
try:
    from services.theme_engine_pyside6 import apply_modern_theme
except ImportError:
    def apply_modern_theme(app):
        """Fallback theme if theme engine is not available"""
        app.setStyle('Fusion')


class MainWindow(QMainWindow):
    """Main window for PySide6 application"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize status variable early
        self.status_var = "Initializing..."
        
        # Set window properties
        self.setWindowTitle("CeliacShield")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Initialize database
        self.init_database()
        
        # Initialize Bluetooth sync
        self.sync_manager = SyncManager()
        self.sync_manager.sync_status_changed.connect(self._handle_sync_update)
        self.sync_manager.start_bluetooth_sync()
        
        # Set up UI with centered title and navigation menu
        self.setup_ui()
        self.setup_status_bar()
        self.setup_panels()
        
        # Apply saved theme or default theme
        self.apply_saved_theme()

    def apply_saved_theme(self):
        """Apply the saved theme or default theme"""
        try:
            from services.theme_creator import theme_creator
            app = QApplication.instance()
            if app:
                # Get the saved theme ID, default to celiac_safe if none saved
                saved_theme = theme_creator.current_theme or "celiac_safe"
                result = theme_creator.apply_theme(saved_theme, app)
                if result:
                    self.status_var = f"Applied theme: {saved_theme}"
                    # Apply menu bar styling at application level to override theme
                    self.apply_application_level_menu_styling()
                    # Update navigation widget to match theme
                    self.update_navigation_theme()
                else:
                    # Fallback to celiac safe theme if saved theme fails
                    result = theme_creator.apply_theme("celiac_safe", app)
                    if result:
                        self.status_var = "Applied fallback Celiac Safe theme"
                        self.apply_application_level_menu_styling()
                        self.update_navigation_theme()
        except Exception as e:
            print(f"Error applying saved theme: {e}")
            # Fallback to celiac safe theme
            try:
                from services.theme_creator import theme_creator
                app = QApplication.instance()
                if app:
                    result = theme_creator.apply_theme("celiac_safe", app)
                    if result:
                        self.status_var = "Applied fallback Celiac Safe theme"
                        self.apply_application_level_menu_styling()
                        self.update_navigation_theme()
            except Exception as e2:
                print(f"Error applying fallback theme: {e2}")
    
    def apply_default_theme(self):
        """Apply the default Celiac Safe theme"""
        try:
            from services.theme_creator import theme_creator
            app = QApplication.instance()
            if app:
                # Apply celiac safe theme as default
                result = theme_creator.apply_theme("celiac_safe", app)
                if result:
                    self.status_var = "Celiac Safe theme applied"
                    # Apply menu bar styling at application level to override theme
                    self.apply_application_level_menu_styling()
                    # Update navigation widget to match theme
                    self.update_navigation_theme()
                else:
                    # Fallback to modern theme if celiac safe fails
                    apply_modern_theme(app)
                    self.status_var = "Fallback theme applied"
        except Exception as e:
            print(f"Error applying default theme: {e}")
            # Fallback to modern theme
            try:
                apply_modern_theme(QApplication.instance())
                self.status_var = "Fallback theme applied"
            except:
                self.status_var = "Theme error"

    def finalize_menu_styling(self):
        """Finalize menu bar styling to fix theme artifacts"""
        try:
            # Apply styling multiple times with different delays to ensure it sticks
            from PySide6.QtCore import QTimer
            
            # Immediate styling
            self._apply_final_menu_styling()
            
            # Delayed styling (100ms)
            timer1 = QTimer()
            timer1.timeout.connect(self._apply_final_menu_styling)
            timer1.setSingleShot(True)
            timer1.start(100)
            
            # Additional delayed styling (500ms)
            timer2 = QTimer()
            timer2.timeout.connect(self._apply_final_menu_styling)
            timer2.setSingleShot(True)
            timer2.start(500)
            
        except Exception as e:
            print(f"Error setting up final menu styling: {e}")

    def apply_application_level_menu_styling(self):
        """Apply menu styling at application level to override theme"""
        try:
            # Don't apply application-level styling as it may cause overlay issues
            # Instead, focus on direct menu bar styling
            pass
                
        except Exception as e:
            print(f"Error applying application-level menu styling: {e}")

    def force_window_refresh(self):
        """Force a window refresh to fix menu artifacts (simulates opening Settings)"""
        try:
            from PySide6.QtCore import QTimer
            
            # Use QTimer to delay the refresh
            timer = QTimer()
            timer.timeout.connect(self._perform_window_refresh)
            timer.setSingleShot(True)
            timer.start(200)  # 200ms delay
            
        except Exception as e:
            print(f"Error setting up window refresh: {e}")

    def _perform_window_refresh(self):
        """Actually perform the window refresh"""
        try:
            # Create and immediately close a temporary dialog to trigger refresh
            # This simulates what happens when Settings is opened
            from PySide6.QtWidgets import QDialog
            temp_dialog = QDialog(self)
            temp_dialog.setWindowTitle("Temp")
            temp_dialog.setModal(False)
            temp_dialog.setVisible(False)  # Don't show it, just create it
            temp_dialog.close()
            temp_dialog.deleteLater()
            
            # Ensure menu bar is properly positioned and not overlapped
            self.ensure_menu_bar_visibility()
                
            # Force the main window to refresh its layout
            self.update()
            self.repaint()
                
            # Force status bar refresh
            status_bar = self.statusBar()
            if status_bar:
                status_bar.update()
                status_bar.repaint()
                
            # Force the entire window to redraw
            self.show()
            
        except Exception as e:
            print(f"Error performing window refresh: {e}")

    def ensure_menu_bar_visibility(self):
        """Ensure menu bar is visible and not overlapped by other elements"""
        try:
            menubar = self.menuBar()
            if menubar:
                # Ensure menu bar is at the top and visible
                menubar.setVisible(True)
                menubar.setEnabled(True)
                menubar.raise_()  # Bring to front
                
                # Ensure it's properly sized and positioned
                menubar.adjustSize()
                
                # Force repaint
                menubar.update()
                menubar.repaint()
                
                # Make sure no other widgets are overlapping
                menubar.setGeometry(menubar.geometry())
                
        except Exception as e:
            print(f"Error ensuring menu bar visibility: {e}")

    def _apply_final_menu_styling(self):
        """Apply final menu styling with force"""
        try:
            menubar = self.menuBar()
            if menubar:
                # Clear any existing stylesheet first
                menubar.setStyleSheet("")
                # Force a repaint
                menubar.repaint()
                # Apply our styling
                self.style_menu_bar(menubar)
                # Force another repaint
                menubar.update()
                
            status_bar = self.statusBar()
            if status_bar:
                self.style_status_bar(status_bar)
        except Exception as e:
            print(f"Error applying final menu styling: {e}")

    def refresh_menu_styling(self):
        """Refresh menu bar styling to fix theme artifacts"""
        try:
            # Use QTimer to delay styling refresh slightly
            from PySide6.QtCore import QTimer
            timer = QTimer()
            timer.timeout.connect(self._apply_menu_styling_refresh)
            timer.setSingleShot(True)
            timer.start(100)  # 100ms delay
        except Exception as e:
            print(f"Error setting up menu refresh: {e}")

    def _apply_menu_styling_refresh(self):
        """Actually apply the menu styling refresh"""
        try:
            menubar = self.menuBar()
            if menubar:
                self.style_menu_bar(menubar)
            status_bar = self.statusBar()
            if status_bar:
                self.style_status_bar(status_bar)
        except Exception as e:
            print(f"Error applying menu styling refresh: {e}")

    def init_database(self):
        """Initialize database connection"""
        try:
            from utils.db import get_connection
            from utils.migrations import ensure_schema
            from utils.settings import ensure_settings_table
            
            self.db = get_connection()
            ensure_schema(self.db)
            ensure_settings_table(self.db)
            if self.status_var == "Database initialized":
                self.status_var = "Database initialized"
            else:
                # Keep the theme status if it was set
                pass
        except Exception as e:
            print(f"Database initialization error: {e}")
            self.db = None
            if "Database error" not in self.status_var:
                self.status_var = "Database error"

    def setup_ui(self):
        """Set up the main UI"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Centered title with improved styling
        title_label = QLabel("CeliacShield Management")
        from core.ui_polish import UIPolish
        title_label.setFont(UIPolish.get_title_font())
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #1b5e20;
                margin: 20px;
                padding: 16px;
                background-color: rgba(241, 248, 233, 0.8);
                border-radius: 8px;
            }
        """)
        self.title_label = title_label
        main_layout.addWidget(title_label)
        
        # Create centered navigation menu below title
        self.create_centered_navigation_menu(main_layout)
        
        # Tab widget with improved styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c8e6c9;
                border-radius: 8px;
                background-color: #fafafa;
                margin-top: 4px;
            }
            QTabBar::tab {
                background-color: #e8f5e8;
                color: #2e7d32;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #4caf50;
            }
            QTabBar::tab:hover:!selected {
                background-color: #f1f8e9;
            }
        """)
        main_layout.addWidget(self.tab_widget)

    def create_centered_navigation_menu(self, main_layout):
        """Create a centered navigation menu below the title"""
        try:
            from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
            
            # Create navigation widget
            nav_widget = QWidget()
            nav_layout = QHBoxLayout(nav_widget)
            nav_layout.setContentsMargins(20, 10, 20, 10)
            nav_layout.setSpacing(10)
            
            # Add left spacer
            left_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            nav_layout.addItem(left_spacer)
            
            # Create navigation buttons
            nav_buttons = [
                ("Cookbook", lambda: self.switch_to_panel(0)),
                ("Pantry", lambda: self.switch_to_panel(1)),
                ("Shopping List", lambda: self.switch_to_panel(2)),
                ("Menu Planner", lambda: self.switch_to_panel(3)),
                ("Health Log", lambda: self.switch_to_panel(4)),
                ("Calendar", lambda: self.switch_to_panel(5)),
                ("Guide", lambda: self.switch_to_panel(6)),
            ]
            
            for text, callback in nav_buttons:
                btn = QPushButton(text)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        color: #2e7d32;
                        border: 2px solid #c8e6c9;
                        padding: 10px 18px;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 11px;
                        font-weight: 500;
                        border-radius: 6px;
                        min-width: 90px;
                        min-height: 36px;
                    }
                    QPushButton:hover {
                        background-color: #e8f5e8;
                        border-color: #4caf50;
                        transform: translateY(-1px);
                    }
                    QPushButton:pressed {
                        background-color: #2e7d32;
                        color: #ffffff;
                        border-color: #1b5e20;
                    }
                """)
                btn.clicked.connect(callback)
                nav_layout.addWidget(btn)
            
            # Add Options button with distinct styling
            options_btn = QPushButton("⚙ Options")
            options_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f5f5f5;
                    color: #424242;
                    border: 2px solid #bdbdbd;
                    padding: 10px 18px;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 11px;
                    font-weight: 500;
                    border-radius: 6px;
                    min-width: 90px;
                    min-height: 36px;
                }
                QPushButton:hover {
                    background-color: #eeeeee;
                    border-color: #757575;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                    border-color: #424242;
                }
            """)
            options_btn.clicked.connect(self.show_settings)
            nav_layout.addWidget(options_btn)
            
            # Add right spacer
            right_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            nav_layout.addItem(right_spacer)
            
            # Don't apply hardcoded styling - let theme handle it
            # nav_widget.setStyleSheet("""
            #     QWidget {
            #         background-color: #f1f8e9;
            #         border-bottom: 1px solid #c8e6c9;
            #     }
            # """)
            
            # Apply polished navigation styling
            nav_widget.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8fdf8, stop:1 #f1f8e9);
                    border-bottom: 2px solid #c8e6c9;
                    border-top: 1px solid #e8f5e8;
                }
            """)
            
            self.nav_widget = nav_widget
            main_layout.addWidget(nav_widget)
            
        except Exception as e:
            print(f"Error creating centered navigation menu: {e}")

    def update_navigation_theme(self):
        """Update navigation widget to match current theme"""
        try:
            if hasattr(self, 'nav_widget') and self.nav_widget:
                # Get the current theme colors
                from services.theme_creator import theme_creator
                
                # Get current theme ID and load theme data
                current_theme_id = theme_creator.current_theme
                if current_theme_id:
                    theme_data = theme_creator.load_theme(current_theme_id)
                    if theme_data:
                        # Extract colors from theme
                        colors = theme_data.get('colors', {})
                        
                        # Use the main theme background color for title
                        header_bg = colors.get('background', '#fafafa')
                        print(f"DEBUG: Theme {current_theme_id} - background: {header_bg}, primary: {colors.get('primary', 'N/A')}")
                        
                        # Try different possible color keys for border
                        border_color = (colors.get('border_color') or 
                                      colors.get('border') or 
                                      colors.get('surface_variant') or 
                                      '#c8e6c9')
                        
                        # Get additional theme colors
                        background_color = colors.get('background', '#fafafa')
                        text_color = colors.get('text_primary', '#212121')
                        
                        # Update title label styling
                        if hasattr(self, 'title_label') and self.title_label:
                            title_style = f"""
                                QLabel {{
                                    color: {text_color} !important; 
                                    margin: 15px; 
                                    padding: 15px; 
                                    background-color: {header_bg} !important;
                                    border-bottom: 2px solid {border_color};
                                    border: none;
                                }}
                            """
                            self.title_label.setStyleSheet(title_style)
                            print(f"Updated title background to: {header_bg}")
                        
                        # Apply theme colors to navigation widget
                        self.nav_widget.setStyleSheet(f"""
                            QWidget {{
                                background-color: {header_bg};
                                border-bottom: 1px solid {border_color};
                            }}
                        """)
                        
                        print(f"Updated navigation theme with background: {header_bg}")
                    else:
                        print("Failed to load theme data for navigation update")
                else:
                    print("No current theme ID found for navigation update")
        except Exception as e:
            print(f"Error updating navigation theme: {e}")

    def style_menu_bar(self, menubar):
        """Apply Celiac Safe theme styling to menu bar"""
        try:
            # Clear any existing stylesheet first to prevent conflicts
            menubar.setStyleSheet("")
            
            # Simple, direct styling to avoid overlay issues
            menu_style = """
                QMenuBar {
                    background-color: #f1f8e9;
                    color: #1b5e20;
                    border-bottom: 1px solid #c8e6c9;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 11px;
                    padding: 4px 20px;
                    spacing: 15px;
                    text-align: center;
                }
                
                QMenuBar::item {
                    background-color: transparent;
                    color: #1b5e20;
                    padding: 8px 12px;
                    border-radius: 4px;
                    margin: 2px;
                    border: none;
                    text-align: center;
                }
                
                QMenuBar::item:selected {
                    background-color: #e8f5e8;
                    color: #1b5e20;
                    border: 1px solid #c8e6c9;
                }
                
                QMenuBar::item:pressed {
                    background-color: #66bb6a;
                    color: #ffffff;
                }
                
                QMenuBar::item:disabled {
                    color: #81c784;
                }
                
                QMenu {
                    background-color: #ffffff;
                    color: #1b5e20;
                    border: 1px solid #c8e6c9;
                    border-radius: 6px;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 11px;
                    padding: 4px;
                }
                
                QMenu::item {
                    background-color: transparent;
                    color: #1b5e20;
                    padding: 8px 20px;
                    border-radius: 4px;
                    margin: 1px;
                    border: none;
                }
                
                QMenu::item:selected {
                    background-color: #e8f5e8;
                    color: #1b5e20;
                }
                
                QMenu::item:disabled {
                    color: #81c784;
                }
                
                QMenu::separator {
                    height: 1px;
                    background-color: #c8e6c9;
                    margin: 4px 8px;
                }
                
                QMenu::indicator {
                    width: 16px;
                    height: 16px;
                    margin-right: 8px;
                }
                
                QMenu::indicator:checked {
                    background-color: #2e7d32;
                    border: 1px solid #1b5e20;
                    border-radius: 2px;
                }
                
                QMenu::indicator:unchecked {
                    background-color: transparent;
                    border: 1px solid #c8e6c9;
                    border-radius: 2px;
                }
            """
            
            # Don't apply hardcoded styling - let theme handle it
            # menubar.setStyleSheet(menu_style)
            
            # Ensure menu bar is properly positioned and visible
            menubar.setVisible(True)
            menubar.setEnabled(True)
            menubar.raise_()  # Bring to front
            menubar.activateWindow()  # Ensure it's active
            
            # Force repaint and layout update
            menubar.repaint()
            menubar.update()
            menubar.adjustSize()
            
            # Ensure menu bar is at the very top and properly layered
            menubar.move(0, 0)
            menubar.setZValue(1000)  # Ensure it's on top
            
        except Exception as e:
            print(f"Error styling menu bar: {e}")

    def create_centered_menu_bar(self):
        """Create a custom centered menu bar layout"""
        try:
            from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
            
            # Get the original menubar
            menubar = self.menuBar()
            
            # Create a custom widget to replace the menu bar
            menu_widget = QWidget()
            menu_layout = QHBoxLayout(menu_widget)
            menu_layout.setContentsMargins(10, 5, 10, 5)
            menu_layout.setSpacing(15)
            
            # Add left spacer
            left_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            menu_layout.addItem(left_spacer)
            
            # Create centered menu buttons
            menu_buttons = [
                ("Cookbook", lambda: self.switch_to_panel(0)),
                ("Pantry", lambda: self.switch_to_panel(1)),
                ("Shopping List", lambda: self.switch_to_panel(2)),
                ("Menu Planner", lambda: self.switch_to_panel(3)),
                ("Health Log", lambda: self.switch_to_panel(4)),
                ("Calendar", lambda: self.switch_to_panel(5)),
                ("Guide", lambda: self.switch_to_panel(6)),
            ]
            
            for text, callback in menu_buttons:
                btn = QPushButton(text)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #1b5e20;
                        border: none;
                        padding: 8px 12px;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 11px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #e8f5e8;
                        color: #1b5e20;
                    }
                    QPushButton:pressed {
                        background-color: #66bb6a;
                        color: #ffffff;
                    }
                """)
                btn.clicked.connect(callback)
                menu_layout.addWidget(btn)
            
            # Add Options button
            options_btn = QPushButton("Options")
            options_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #1b5e20;
                    border: none;
                    padding: 8px 12px;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 11px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #e8f5e8;
                    color: #1b5e20;
                }
                QPushButton:pressed {
                    background-color: #66bb6a;
                    color: #ffffff;
                }
            """)
            options_btn.clicked.connect(self.show_settings)
            menu_layout.addWidget(options_btn)
            
            # Add right spacer
            right_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            menu_layout.addItem(right_spacer)
            
            # Set the menu widget as the central widget's top layout
            # We need to add this to the main layout
            self.menu_widget = menu_widget
            
            # Apply the same styling as the original menu bar
            menu_widget.setStyleSheet("""
                QWidget {
                    background-color: #f1f8e9;
                    border-bottom: 1px solid #c8e6c9;
                }
            """)
            
        except Exception as e:
            print(f"Error creating centered menu bar: {e}")

    def center_menu_bar_items(self, menubar):
        """Center the menu bar items across the menu bar"""
        try:
            # Store the original actions
            original_actions = menubar.actions().copy()
            
            # Clear the menu bar
            menubar.clear()
            
            # Add invisible spacer at the beginning
            spacer_left = QAction('', self)
            spacer_left.setVisible(False)
            menubar.addAction(spacer_left)
            
            # Re-add all original actions
            for action in original_actions:
                menubar.addAction(action)
            
            # Add invisible spacer at the end
            spacer_right = QAction('', self)
            spacer_right.setVisible(False)
            menubar.addAction(spacer_right)
            
            # Apply CSS to center items by making spacers take equal space
            menubar.setStyleSheet(menubar.styleSheet() + """
                QMenuBar::item:first-child,
                QMenuBar::item:last-child {
                    background: transparent;
                    border: none;
                    min-width: 200px;
                    max-width: 200px;
                }
            """)
            
        except Exception as e:
            print(f"Error centering menu bar items: {e}")

    def setup_menu_bar(self):
        """Set up the menu bar"""
        menubar = self.menuBar()
        
        # Cookbook panel action
        cookbook_action = QAction('&Cookbook', self)
        cookbook_action.setShortcut('Ctrl+1')
        cookbook_action.setStatusTip('Switch to Cookbook panel')
        cookbook_action.triggered.connect(lambda: self.switch_to_panel(0))
        menubar.addAction(cookbook_action)
        
        # Pantry panel action
        pantry_action = QAction('&Pantry', self)
        pantry_action.setShortcut('Ctrl+2')
        pantry_action.setStatusTip('Switch to Pantry panel')
        pantry_action.triggered.connect(lambda: self.switch_to_panel(1))
        menubar.addAction(pantry_action)
        
        # Shopping List panel action
        shopping_action = QAction('&Shopping List', self)
        shopping_action.setShortcut('Ctrl+3')
        shopping_action.setStatusTip('Switch to Shopping List panel')
        shopping_action.triggered.connect(lambda: self.switch_to_panel(2))
        menubar.addAction(shopping_action)
        
        # Menu Planning panel action
        menu_action = QAction('&Menu Planner', self)
        menu_action.setShortcut('Ctrl+4')
        menu_action.setStatusTip('Switch to Menu Planning panel')
        menu_action.triggered.connect(lambda: self.switch_to_panel(3))
        menubar.addAction(menu_action)
        
        # Health Log panel action
        health_action = QAction('&Health Log', self)
        health_action.setShortcut('Ctrl+5')
        health_action.setStatusTip('Switch to Health Log panel')
        health_action.triggered.connect(lambda: self.switch_to_panel(4))
        menubar.addAction(health_action)
        
        # Calendar panel action
        calendar_action = QAction('&Calendar', self)
        calendar_action.setShortcut('Ctrl+6')
        calendar_action.setStatusTip('Switch to Calendar panel')
        calendar_action.triggered.connect(lambda: self.switch_to_panel(5))
        menubar.addAction(calendar_action)
        
        # Guide panel action
        guide_action = QAction('&Guide', self)
        guide_action.setShortcut('Ctrl+7')
        guide_action.setStatusTip('Switch to Guide panel')
        guide_action.triggered.connect(lambda: self.switch_to_panel(6))
        menubar.addAction(guide_action)
        
        # Options menu
        options_menu = menubar.addMenu('&Options')
        
        # Settings action
        settings_action = QAction('&Settings', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.setStatusTip('Open application settings')
        settings_action.triggered.connect(self.show_settings)
        options_menu.addAction(settings_action)
        
        # Separator
        options_menu.addSeparator()
        
        # About action
        about_action = QAction('&About', self)
        about_action.setStatusTip('About CeliacShield')
        about_action.triggered.connect(self.show_about)
        options_menu.addAction(about_action)
        
        # Separator
        options_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        options_menu.addAction(exit_action)
        
        # Apply styling to the menu bar
        self.style_menu_bar(menubar)

    def style_status_bar(self, status_bar):
        """Apply Celiac Safe theme styling to status bar"""
        try:
            # Celiac Safe theme colors for status bar
            status_style = """
                QStatusBar {
                    background-color: #e8f5e8;
                    color: #1b5e20;
                    border-top: 1px solid #c8e6c9;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 10px;
                    padding: 4px;
                }
                
                QStatusBar::item {
                    border: none;
                }
                
                QStatusBar QLabel {
                    color: #1b5e20;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 10px;
                }
            """
            # Don't apply hardcoded styling - let theme handle it
            # status_bar.setStyleSheet(status_style)
        except Exception as e:
            print(f"Error styling status bar: {e}")

    def setup_status_bar(self):
        """Set up the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Apply Celiac Safe theme styling to status bar
        self.style_status_bar(self.status_bar)
        
        self.status_bar.showMessage(self.status_var or "Ready")

    def setup_panels(self):
        """Set up all panels"""
        try:
            # Cookbook Panel (index 0)
            self.cookbook_panel = CookbookPanel(self, self)
            self.tab_widget.addTab(self.cookbook_panel, "Cookbook")
            
            # Pantry Panel (index 1)
            self.pantry_panel = PantryPanel(self, self)
            self.tab_widget.addTab(self.pantry_panel, "Pantry")
            
            # Shopping List Panel (index 2)
            self.shopping_list_panel = ShoppingListPanel(self, self)
            self.tab_widget.addTab(self.shopping_list_panel, "Shopping List")
            
            # Menu Panel (index 3)
            self.menu_panel = MenuPanel(self, self)
            self.tab_widget.addTab(self.menu_panel, "Menu Planner")
            
            # Health Log Panel (index 4)
            self.health_log_panel = HealthLogPanel(self, self)
            self.tab_widget.addTab(self.health_log_panel, "Health Log")
            
            # Calendar Panel (index 5)
            self.calendar_panel = CalendarPanel(self, self)
            self.tab_widget.addTab(self.calendar_panel, "Calendar")
            
            # Guide Panel (index 6)
            self.guide_panel = GuidePanel(self, self)
            self.tab_widget.addTab(self.guide_panel, "Guide")
            
            # Settings Panel will be created fresh each time it's opened
            
            # Connect tab change signal
            self.tab_widget.currentChanged.connect(self.on_tab_changed)
            
        except Exception as e:
            print(f"Error setting up panels: {e}")
            # Add error panel
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel(f"Error loading panels: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 14px;")
            error_layout.addWidget(error_label)
            self.tab_widget.addTab(error_widget, "Error")

    def switch_to_panel(self, index):
        """Switch to a specific panel by index"""
        try:
            if 0 <= index < self.tab_widget.count():
                self.tab_widget.setCurrentIndex(index)
                # Trigger the tab changed event to refresh the panel
                self.on_tab_changed(index)
        except Exception as e:
            print(f"Error switching to panel {index}: {e}")

    def on_tab_changed(self, index: int):
        """Handle tab change events"""
        tab_text = self.tab_widget.tabText(index)
        self.status_bar.showMessage(f"Switched to {tab_text}")
        
        # Refresh the panel if it has a refresh method
        current_panel = self.tab_widget.currentWidget()
        if hasattr(current_panel, 'refresh'):
            try:
                current_panel.refresh()
            except Exception as e:
                print(f"Error refreshing panel: {e}")
    
    def _handle_sync_update(self, panel: str, success: bool):
        """Handle sync updates from mobile app."""
        if success and panel != 'settings':
            # Find and refresh the corresponding panel
            panel_map = {
                'pantry': 1, 'cookbook': 0, 'shopping_list': 2,
                'menu': 3, 'health_log': 4, 'calendar': 5
            }
            if panel in panel_map:
                widget = self.tab_widget.widget(panel_map[panel])
                if hasattr(widget, 'refresh'):
                    widget.refresh()
                self.status_bar.showMessage(f"Synced {panel} from mobile")

    def on_theme_changed(self, theme_id):
        """Handle theme change from theme editor"""
        try:
            print(f"DEBUG: on_theme_changed called with theme_id: {theme_id}")
            from services.theme_creator import theme_creator
            # Apply the new theme to the entire application
            app = QApplication.instance()
            if app and theme_creator.apply_theme(theme_id, app):
                print(f"DEBUG: Theme {theme_id} applied successfully in main app")
                
                # Force a complete refresh of the main window
                self.refresh_main_window_styling()
                
                # Apply menu styling at application level after theme change
                self.apply_application_level_menu_styling()
                # Update navigation theme to match new theme
                self.update_navigation_theme()
                self.status_bar.showMessage(f"Theme changed to: {theme_id}")
                print(f"DEBUG: Theme change complete for {theme_id}")
            else:
                print(f"DEBUG: Failed to apply theme {theme_id} in main app")
                QMessageBox.warning(self, "Theme Error", "Failed to apply theme. Please check theme configuration.")
        except Exception as e:
            print(f"DEBUG: Error in on_theme_changed: {e}")
            QMessageBox.critical(self, "Theme Error", f"Failed to change theme: {str(e)}")
    
    def refresh_main_window_styling(self):
        """Force refresh of main window styling"""
        try:
            # Force repaint of main window
            self.update()
            self.repaint()
            
            # Force repaint of central widget
            central_widget = self.centralWidget()
            if central_widget:
                central_widget.update()
                central_widget.repaint()
            
            # Force repaint of tab widget
            if hasattr(self, 'tab_widget') and self.tab_widget:
                self.tab_widget.update()
                self.tab_widget.repaint()
            
            # Force repaint of navigation widget
            if hasattr(self, 'nav_widget') and self.nav_widget:
                self.nav_widget.update()
                self.nav_widget.repaint()
            
            # Force repaint of title label
            if hasattr(self, 'title_label') and self.title_label:
                self.title_label.update()
                self.title_label.repaint()
            
            print("DEBUG: Main window styling refreshed")
            
        except Exception as e:
            print(f"DEBUG: Error refreshing main window styling: {e}")

    def show_settings(self):
        """Show settings dialog"""
        try:
            # Create a dialog to contain the settings panel
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
            from panels.settings_panel import SettingsPanel
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Settings")
            dialog.setModal(True)
            dialog.setMinimumSize(800, 600)
            
            # Layout for the dialog
            layout = QVBoxLayout(dialog)
            
            # Create a new settings panel for this dialog
            settings_panel = SettingsPanel(self, self)
            
            # Connect theme change signal to main app
            settings_panel.theme_changed.connect(self.on_theme_changed)
            
            # Add the settings panel to the dialog
            layout.addWidget(settings_panel)
            
            # Add OK/Cancel buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            # Show the dialog
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Settings Error", f"Failed to open settings: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About CeliacShield", 
                         "CeliacShield - Celiac Disease Management Application\n\n"
                         "Built with PySide6\n"
                         "Version 1.0\n\n"
                         "Features:\n"
                         "• Pantry Management\n"
                         "• Health Logging\n"
                         "• Recipe Management\n"
                         "• Shopping Lists\n"
                         "• Menu Planning\n"
                         "• Calendar Integration\n"
                         "• Data Import/Export")

    def closeEvent(self, event):
        """Handle application close event"""
        reply = QMessageBox.question(self, 'Exit Application', 
                                   'Are you sure you want to exit?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Clean up Bluetooth connection
            if hasattr(self, 'sync_manager'):
                self.sync_manager.bluetooth_service.server_socket = None
            event.accept()
        else:
            event.ignore()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("CeliacShield")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("CeliacShield")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
