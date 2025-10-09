# path: services/theme_creator.py
"""
Theme Creator Service for PySide6 Application

Provides theme creation, editing, and management functionality.
"""

import json
import os
from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QFont


class ThemeCreator:
    """Theme creation and management system"""
    
    def __init__(self, themes_dir: str = "data/themes"):
        self.themes_dir = themes_dir
        self.current_theme = None
        self.settings_file = "data/theme_settings.json"
        self.ensure_themes_directory()
        self.load_current_theme_setting()
    
    def ensure_themes_directory(self):
        """Ensure themes directory exists"""
        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir)
        if not os.path.exists("data"):
            os.makedirs("data")
    
    def save_current_theme_setting(self, theme_id: str):
        """Save current theme setting to file"""
        try:
            settings = {"current_theme": theme_id}
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            self.current_theme = theme_id
        except Exception as e:
            print(f"Error saving theme setting: {str(e)}")
    
    def load_current_theme_setting(self):
        """Load current theme setting from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get("current_theme", "celiac_safe")
            else:
                self.current_theme = "celiac_safe"  # Default theme
        except Exception as e:
            print(f"Error loading theme setting: {str(e)}")
            self.current_theme = "celiac_safe"
    
    def create_default_themes(self):
        """Create default theme collection"""
        default_themes = {
            "light_modern": {
                "name": "Light Modern",
                "description": "Clean, modern light theme",
                "colors": {
                    "primary": "#4caf50",
                    "primary_dark": "#45a049",
                    "primary_light": "#81c784",
                    "secondary": "#ff9800",
                    "background": "#fafafa",
                    "surface": "#ffffff",
                    "surface_variant": "#f5f5f5",
                    "text_primary": "#212121",
                    "text_secondary": "#616161",
                    "text_disabled": "#9e9e9e",
                    "error": "#f44336",
                    "border": "#e0e0e0",
                    "title_background": "#fafafa",
                    "tab_background": "#ffffff",
                    "tab_selected": "#e8f5e8",
                    "menubar_background": "#fafafa",
                    "menubar_text": "#212121",
                    "selection_background": "#e3f2fd",
                    "selection_text": "#1976d2",
                    "selection_border": "#1976d2"
                },
                "typography": {
                    "font_family": "Segoe UI",
                    "font_size": 9,
                    "header_size": 14,
                    "button_font_size": 10
                },
                "components": {
                    "border_radius": 4,
                    "padding": 8,
                    "spacing": 10
                }
            },
            "dark_modern": {
                "name": "Dark Modern",
                "description": "Modern dark theme with green accents",
                "colors": {
                    "primary": "#4caf50",
                    "primary_dark": "#45a049",
                    "primary_light": "#81c784",
                    "secondary": "#ff9800",
                    "background": "#121212",
                    "surface": "#1e1e1e",
                    "surface_variant": "#2d2d2d",
                    "text_primary": "#ffffff",
                    "text_secondary": "#b0b0b0",
                    "text_disabled": "#757575",
                    "error": "#f44336",
                    "border": "#424242",
                    "title_background": "#121212",
                    "tab_background": "#1e1e1e",
                    "tab_selected": "#2d2d2d",
                    "menubar_background": "#121212",
                    "menubar_text": "#ffffff",
                    "selection_background": "#1a237e",
                    "selection_text": "#ffffff",
                    "selection_border": "#3f51b5"
                },
                "typography": {
                    "font_family": "Segoe UI",
                    "font_size": 9,
                    "header_size": 14,
                    "button_font_size": 10
                },
                "components": {
                    "border_radius": 4,
                    "padding": 8,
                    "spacing": 10
                }
            },
            "celiac_safe": {
                "name": "Celiac Safe",
                "description": "Theme designed for celiac disease management",
                "colors": {
                    "primary": "#2e7d32",  # Darker green for safety
                    "primary_dark": "#1b5e20",
                    "primary_light": "#66bb6a",
                    "secondary": "#ff6f00",  # Orange for warnings
                    "background": "#f1f8e9",  # Light green tint
                    "surface": "#ffffff",
                    "surface_variant": "#e8f5e8",
                    "text_primary": "#1b5e20",
                    "text_secondary": "#388e3c",
                    "text_disabled": "#81c784",
                    "error": "#d32f2f",  # Red for gluten warnings
                    "border": "#c8e6c9",
                    "title_background": "#f1f8e9",
                    "tab_background": "#ffffff",
                    "tab_selected": "#e8f5e8",
                    "menubar_background": "#f1f8e9",
                    "menubar_text": "#1b5e20"
                },
                "typography": {
                    "font_family": "Segoe UI",
                    "font_size": 10,
                    "header_size": 16,
                    "button_font_size": 11
                },
                "components": {
                    "border_radius": 6,
                    "padding": 10,
                    "spacing": 12
                }
            },
            "celiac_org": {
                "name": "Celiac.org",
                "description": "Theme inspired by the Celiac Disease Foundation website",
                "colors": {
                    "primary": "#1976d2",  # Professional blue from celiac.org
                    "primary_dark": "#1565c0",
                    "primary_light": "#42a5f5",
                    "secondary": "#26a69a",  # Teal accent for highlights
                    "background": "#ffffff",  # Clean white background
                    "surface": "#f8f9fa",  # Light gray surface
                    "surface_variant": "#e9ecef",
                    "text_primary": "#212529",  # Dark gray text for readability
                    "text_secondary": "#6c757d",
                    "text_disabled": "#adb5bd",
                    "error": "#dc3545",  # Standard red for errors
                    "border": "#dee2e6",  # Light border
                    "header_background": "#ffffff",  # White header background
                    "border_color": "#dee2e6"
                },
                "typography": {
                    "font_family": "Segoe UI, Arial, sans-serif",
                    "font_size": 10,
                    "header_size": 16,
                    "button_font_size": 11
                },
                "components": {
                    "border_radius": 6,
                    "padding": 10,
                    "spacing": 12
                }
            },
            "high_contrast": {
                "name": "High Contrast",
                "description": "High contrast theme for accessibility",
                "colors": {
                    "primary": "#000000",
                    "primary_dark": "#000000",
                    "primary_light": "#666666",
                    "secondary": "#ff0000",
                    "background": "#ffffff",
                    "surface": "#ffffff",
                    "surface_variant": "#f0f0f0",
                    "text_primary": "#000000",
                    "text_secondary": "#333333",
                    "text_disabled": "#999999",
                    "error": "#ff0000",
                    "border": "#000000",
                    "title_background": "#ffffff",
                    "tab_background": "#ffffff",
                    "tab_selected": "#f0f0f0",
                    "menubar_background": "#ffffff",
                    "menubar_text": "#000000"
                },
                "typography": {
                    "font_family": "Arial",
                    "font_size": 12,
                    "header_size": 18,
                    "button_font_size": 14
                },
                "components": {
                    "border_radius": 2,
                    "padding": 12,
                    "spacing": 15
                }
            }
        }
        
        for theme_id, theme_data in default_themes.items():
            self.save_theme(theme_id, theme_data)
    
    def save_theme(self, theme_id: str, theme_data: Dict[str, Any]) -> bool:
        """Save theme to file"""
        try:
            theme_file = os.path.join(self.themes_dir, f"{theme_id}.json")
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving theme {theme_id}: {str(e)}")
            return False
    
    def load_theme(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """Load theme from file and convert to standard format"""
        try:
            theme_file = os.path.join(self.themes_dir, f"{theme_id}.json")
            if os.path.exists(theme_file):
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                    return self._convert_theme_to_standard_format(theme_data)
        except Exception as e:
            print(f"Error loading theme {theme_id}: {str(e)}")
        return None
    
    def _convert_theme_to_standard_format(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert old format themes to new standard format"""
        converted = theme_data.copy()
        
        # Check if this is old format (has 'bg' instead of 'background')
        colors = theme_data.get('colors', {})
        if 'bg' in colors and 'background' not in colors:
            # Convert old format to new format
            converted['colors'] = {
                'primary': colors.get('accent', '#1976d2'),
                'primary_dark': colors.get('accent', '#1565c0'),
                'primary_light': colors.get('accent_fg', '#42a5f5'),
                'secondary': colors.get('warning', '#ff9800'),
                'background': colors.get('bg', '#ffffff'),
                'surface': colors.get('surface', '#f8f9fa'),
                'surface_variant': colors.get('zebra_even', '#e9ecef'),
                'text_primary': colors.get('text', '#212529'),
                'text_secondary': colors.get('muted_text', '#6c757d'),
                'text_disabled': colors.get('low_fg', '#adb5bd'),
                'error': colors.get('danger', '#dc3545'),
                'border': colors.get('border', '#dee2e6'),
                'header_background': colors.get('bg', '#ffffff'),
                'border_color': colors.get('border', '#dee2e6')
            }
        
        # Convert old fonts format to new typography format
        if 'fonts' in theme_data and 'typography' not in theme_data:
            fonts = theme_data.get('fonts', {})
            converted['typography'] = {
                'font_family': fonts.get('base_family', 'Segoe UI'),
                'font_size': fonts.get('base_size', 10),
                'header_size': int(fonts.get('base_size', 10) * 1.6),
                'button_font_size': int(fonts.get('base_size', 10) * 1.1)
            }
        
        # Ensure typography exists
        if 'typography' not in converted:
            converted['typography'] = {
                'font_family': 'Segoe UI',
                'font_size': 10,
                'header_size': 16,
                'button_font_size': 11
            }
        
        # Ensure components exist
        if 'components' not in converted:
            converted['components'] = {
                'border_radius': 6,
                'padding': 10,
                'spacing': 12
            }
        
        return converted
    
    def list_themes(self) -> List[Dict[str, Any]]:
        """List all available themes"""
        themes = []
        try:
            for filename in os.listdir(self.themes_dir):
                if filename.endswith('.json'):
                    theme_id = filename[:-5]  # Remove .json extension
                    theme_data = self.load_theme(theme_id)
                    if theme_data:
                        themes.append({
                            'id': theme_id,
                            'name': theme_data.get('name', theme_id),
                            'description': theme_data.get('description', ''),
                            'data': theme_data
                        })
        except Exception as e:
            print(f"Error listing themes: {str(e)}")
        return themes
    
    def delete_theme(self, theme_id: str) -> bool:
        """Delete a theme"""
        try:
            theme_file = os.path.join(self.themes_dir, f"{theme_id}.json")
            if os.path.exists(theme_file):
                os.remove(theme_file)
                return True
        except Exception as e:
            print(f"Error deleting theme {theme_id}: {str(e)}")
        return False
    
    def apply_theme(self, theme_id: str, app: QApplication) -> bool:
        """Apply theme to application"""
        try:
            theme_data = self.load_theme(theme_id)
            if not theme_data:
                return False
            
            self.current_theme = theme_id
            self.save_current_theme_setting(theme_id)  # Save theme setting
            self._apply_colors(app, theme_data.get('colors', {}))
            self._apply_typography(app, theme_data.get('typography', {}))
            self._apply_stylesheet(app, theme_data)
            return True
        except Exception as e:
            print(f"Error applying theme {theme_id}: {str(e)}")
            return False
    
    def _apply_colors(self, app: QApplication, colors: Dict[str, str]):
        """Apply color palette to application"""
        palette = QPalette()
        
        # Set palette colors
        palette.setColor(QPalette.Window, QColor(colors.get('background', '#fafafa')))
        palette.setColor(QPalette.WindowText, QColor(colors.get('text_primary', '#212121')))
        palette.setColor(QPalette.Base, QColor(colors.get('surface', '#ffffff')))
        palette.setColor(QPalette.AlternateBase, QColor(colors.get('surface_variant', '#f5f5f5')))
        palette.setColor(QPalette.ToolTipBase, QColor(colors.get('surface', '#ffffff')))
        palette.setColor(QPalette.ToolTipText, QColor(colors.get('text_primary', '#212121')))
        palette.setColor(QPalette.Text, QColor(colors.get('text_primary', '#212121')))
        palette.setColor(QPalette.Button, QColor(colors.get('surface', '#ffffff')))
        palette.setColor(QPalette.ButtonText, QColor(colors.get('text_primary', '#212121')))
        palette.setColor(QPalette.BrightText, Qt.white)
        palette.setColor(QPalette.Link, QColor(colors.get('primary', '#4caf50')))
        palette.setColor(QPalette.Highlight, QColor(colors.get('primary', '#4caf50')))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        
        app.setPalette(palette)
    
    def _apply_typography(self, app: QApplication, typography: Dict[str, Any]):
        """Apply typography settings to application"""
        font_family = typography.get('font_family', 'Segoe UI')
        font_size = typography.get('font_size', 9)
        
        font = QFont(font_family, font_size)
        app.setFont(font)
    
    def _apply_stylesheet(self, app: QApplication, theme_data: Dict[str, Any]):
        """Apply stylesheet to application"""
        colors = theme_data.get('colors', {})
        typography = theme_data.get('typography', {})
        components = theme_data.get('components', {})
        
        stylesheet = self._generate_stylesheet(colors, typography, components)
        print(f"DEBUG: Applying stylesheet with background: {colors.get('background', '#fafafa')}")
        app.setStyleSheet(stylesheet)
        
        # Force a repaint of all widgets to ensure stylesheet is applied
        try:
            for widget in app.allWidgets():
                if hasattr(widget, 'update'):
                    try:
                        widget.update()
                    except TypeError:
                        # Some widgets require arguments for update()
                        pass
                if hasattr(widget, 'repaint'):
                    widget.repaint()
        except AttributeError:
            # allWidgets() method doesn't exist in this Qt version
            pass
    
    def _generate_stylesheet(self, colors: Dict[str, str], typography: Dict[str, Any], components: Dict[str, Any]) -> str:
        """Generate stylesheet from theme data"""
        border_radius = components.get('border_radius', 4)
        padding = components.get('padding', 8)
        spacing = components.get('spacing', 10)
        font_family = typography.get('font_family', 'Segoe UI')
        font_size = typography.get('font_size', 9)
        button_font_size = typography.get('button_font_size', 10)
        
        return f"""
        /* Theme Stylesheet - Clean Selection Design */
        
        /* Global overrides to disable problematic Qt defaults */
        * {{
            text-decoration: none !important;
            selection-background-color: transparent !important;
            selection-color: inherit !important;
        }}
        
        /* Disable all default selection styling */
        QAbstractItemView::item:selected {{
            background: transparent !important;
            color: inherit !important;
            border: none !important;
            outline: none !important;
            text-decoration: none !important;
        }}
        
        QMainWindow {{
            background-color: {colors.get('background', '#fafafa')};
            color: {colors.get('text_primary', '#212121')};
            font-family: '{font_family}';
            font-size: {font_size}px;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {colors.get('border', '#e0e0e0')};
            background-color: {colors.get('surface', '#ffffff')};
        }}
        
        QTabBar::tab {{
            background-color: {colors.get('tab_background', colors.get('surface', '#ffffff'))};
            color: {colors.get('text_primary', '#212121')};
            border: 1px solid {colors.get('border', '#e0e0e0')};
            padding: {padding}px {padding*2}px;
            margin-right: 2px;
            border-top-left-radius: {border_radius}px;
            border-top-right-radius: {border_radius}px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors.get('tab_selected', colors.get('surface_variant', '#f5f5f5'))};
            color: {colors.get('text_primary', '#212121')};
            border-bottom: 2px solid {colors.get('primary', '#4caf50')};
            font-weight: bold;
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors.get('surface_variant', '#f5f5f5')};
            color: {colors.get('text_primary', '#212121')};
        }}
        
        QMenuBar {{
            background-color: {colors.get('menubar_background', colors.get('background', '#fafafa'))};
            color: {colors.get('menubar_text', colors.get('text_primary', '#212121'))};
            border: none;
            spacing: 3px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 4px 8px;
            border-radius: {border_radius}px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors.get('primary', '#4caf50')};
            color: white;
        }}
        
        QMenu {{
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text_primary', '#212121')};
            border: 1px solid {colors.get('border', '#e0e0e0')};
            border-radius: {border_radius}px;
        }}
        
        QMenu::item {{
            padding: 8px 16px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors.get('primary', '#4caf50')};
            color: white;
        }}
        
        QPushButton {{
            background-color: {colors.get('primary', '#4caf50')};
            color: white;
            border: none;
            padding: {padding}px {padding*2}px;
            border-radius: {border_radius}px;
            font-weight: bold;
            font-size: {button_font_size}px;
        }}
        
        QPushButton:hover {{
            background-color: {colors.get('primary_dark', '#45a049')};
        }}
        
        QPushButton:pressed {{
            background-color: {colors.get('primary_dark', '#45a049')};
        }}
        
        QPushButton:disabled {{
            background-color: {colors.get('text_disabled', '#cccccc')};
            color: {colors.get('text_secondary', '#666666')};
        }}
        
        QLineEdit {{
            border: 1px solid {colors.get('border', '#e0e0e0')};
            border-radius: {border_radius}px;
            padding: {padding}px;
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text_primary', '#212121')};
        }}
        
        QLineEdit:focus {{
            border: 2px solid {colors.get('primary', '#4caf50')};
        }}
        
        QTextEdit {{
            border: 1px solid {colors.get('border', '#e0e0e0')};
            border-radius: {border_radius}px;
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text_primary', '#212121')};
        }}
        
        QTextEdit:focus {{
            border: 2px solid {colors.get('primary', '#4caf50')};
        }}
        
        QComboBox {{
            border: 1px solid {colors.get('border', '#e0e0e0')};
            border-radius: {border_radius}px;
            padding: {padding}px;
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text_primary', '#212121')};
        }}
        
        QComboBox:focus {{
            border: 2px solid {colors.get('primary', '#4caf50')};
        }}
        
        QSpinBox {{
            border: 1px solid {colors.get('border', '#e0e0e0')};
            border-radius: {border_radius}px;
            padding: {padding}px;
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text_primary', '#212121')};
        }}
        
        QSpinBox:focus {{
            border: 2px solid {colors.get('primary', '#4caf50')};
        }}
        
        QTableWidget {{
            border: 1px solid {colors.get('border', '#e0e0e0')};
            border-radius: {border_radius}px;
            background-color: {colors.get('surface', '#ffffff')};
            alternate-background-color: {colors.get('surface_variant', '#f5f5f5')};
            gridline-color: {colors.get('border', '#f0f0f0')};
            color: {colors.get('text_primary', '#212121')};
            selection-background-color: transparent;
            selection-color: inherit;
            show-decoration-selected: 0;
        }}
        
        QTableWidget::item {{
            padding: {padding}px;
            border: none;
            text-decoration: none;
            background: transparent;
            color: {colors.get('text_primary', '#212121')};
        }}
        
        /* Completely disable Qt's selection system */
        QTableWidget::item:selected {{
            background: transparent !important;
            color: inherit !important;
            border: none !important;
            outline: none !important;
            text-decoration: none !important;
            font-weight: normal !important;
        }}
        
        QTableWidget::item:selected:focus {{
            background: transparent !important;
            color: inherit !important;
            border: none !important;
            outline: none !important;
            text-decoration: none !important;
            font-weight: normal !important;
        }}
        
        QTableWidget::item:hover {{
            background-color: #f0f8f0;
            text-decoration: none;
        }}
        
        QTableWidget::item:selected:hover {{
            background: transparent !important;
            color: inherit !important;
            border: none !important;
            text-decoration: none !important;
            font-weight: normal !important;
        }}
        
        QHeaderView::section {{
            background-color: {colors.get('surface_variant', '#f5f5f5')};
            border: 1px solid {colors.get('border', '#e0e0e0')};
            padding: {padding}px;
            font-weight: bold;
            color: {colors.get('text_primary', '#212121')};
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {colors.get('border', '#e0e0e0')};
            border-radius: {border_radius}px;
            margin-top: {padding}px;
            padding-top: {padding}px;
            color: {colors.get('text_primary', '#212121')};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {padding}px;
            padding: 0 {padding}px 0 {padding}px;
            color: {colors.get('primary', '#4caf50')};
        }}
        
        QMessageBox {{
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text_primary', '#212121')};
        }}
        
        QListWidget {{
            border: 1px solid {colors.get('border', '#e0e0e0')};
            border-radius: {border_radius}px;
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text_primary', '#212121')};
            selection-background-color: transparent;
            selection-color: inherit;
            show-decoration-selected: 0;
        }}
        
        QListWidget::item {{
            padding: {padding}px;
            border: none;
            text-decoration: none;
            background: transparent;
            color: {colors.get('text_primary', '#212121')};
        }}
        
        /* Completely disable Qt's selection system */
        QListWidget::item:selected {{
            background: transparent !important;
            color: inherit !important;
            border: none !important;
            outline: none !important;
            text-decoration: none !important;
            font-weight: normal !important;
        }}
        
        QListWidget::item:selected:focus {{
            background: transparent !important;
            color: inherit !important;
            border: none !important;
            outline: none !important;
            text-decoration: none !important;
            font-weight: normal !important;
        }}
        
        QListWidget::item:hover {{
            background-color: #f0f8f0;
            text-decoration: none;
        }}
        
        QListWidget::item:selected:hover {{
            background: transparent !important;
            color: inherit !important;
            border: none !important;
            text-decoration: none !important;
            font-weight: normal !important;
        }}
        
        QTreeWidget {{
            border: 1px solid {colors.get('border', '#e0e0e0')};
            border-radius: {border_radius}px;
            background-color: {colors.get('surface', '#ffffff')};
            color: {colors.get('text_primary', '#212121')};
            selection-background-color: transparent;
            selection-color: inherit;
            show-decoration-selected: 0;
        }}
        
        QTreeWidget::item {{
            padding: {padding}px;
            border: none;
            text-decoration: none;
            background: transparent;
            color: {colors.get('text_primary', '#212121')};
        }}
        
        /* Completely disable Qt's selection system */
        QTreeWidget::item:selected {{
            background: transparent !important;
            color: inherit !important;
            border: none !important;
            outline: none !important;
            text-decoration: none !important;
            font-weight: normal !important;
        }}
        
        QTreeWidget::item:selected:focus {{
            background: transparent !important;
            color: inherit !important;
            border: none !important;
            outline: none !important;
            text-decoration: none !important;
            font-weight: normal !important;
        }}
        
        QTreeWidget::item:hover {{
            background-color: #f0f8f0;
            text-decoration: none;
        }}
        
        QTreeWidget::item:selected:hover {{
            background: transparent !important;
            color: inherit !important;
            border: none !important;
            text-decoration: none !important;
            font-weight: normal !important;
        }}
        
        QMenu {{
            background-color: {colors.get('surface', '#ffffff')};
            border: 1px solid {colors.get('border', '#e0e0e0')};
            border-radius: {border_radius}px;
            color: {colors.get('text_primary', '#212121')};
        }}
        
        QMenu::item {{
            padding: {padding}px {padding*2}px;
            background-color: transparent;
        }}
        
        QMenu::item:selected {{
            background-color: {colors.get('primary', '#4caf50')};
            color: white;
        }}
        """
    
    def create_custom_theme(self, theme_data: Dict[str, Any]) -> str:
        """Create a custom theme from provided data"""
        theme_id = theme_data.get('id', f"custom_{len(self.list_themes())}")
        if self.save_theme(theme_id, theme_data):
            return theme_id
        return None
    
    def export_theme(self, theme_id: str, export_path: str) -> bool:
        """Export theme to file"""
        try:
            theme_data = self.load_theme(theme_id)
            if not theme_data:
                return False
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting theme {theme_id}: {str(e)}")
            return False
    
    def import_theme(self, import_path: str) -> Optional[str]:
        """Import theme from file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            theme_id = theme_data.get('id', f"imported_{len(self.list_themes())}")
            if self.save_theme(theme_id, theme_data):
                return theme_id
        except Exception as e:
            print(f"Error importing theme: {str(e)}")
        return None


# Global theme creator instance
theme_creator = ThemeCreator()
