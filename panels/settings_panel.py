#!/usr/bin/env python3
"""
Comprehensive Settings Panel for CeliacShield Application
Includes: Theme customization, Database settings, Import/Export, Recipe Search, Communication
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, QLabel, 
    QPushButton, QComboBox, QLineEdit, QTextEdit, QSpinBox, QCheckBox,
    QFileDialog, QMessageBox, QColorDialog, QScrollArea, QGridLayout,
    QSlider, QFormLayout, QListWidget, QListWidgetItem, QSplitter,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QDialogButtonBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter

from utils.db import get_connection
from utils.settings import get_setting, set_setting
from services.theme_creator import theme_creator


class ColorPickerWidget(QWidget):
    """Custom color picker widget with preview"""
    
    color_changed = Signal(str)  # Emits hex color code
    
    def __init__(self, initial_color="#ffffff", parent=None):
        super().__init__(parent)
        self.current_color = initial_color
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """Set up the color picker UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Color preview
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(40, 25)
        self.color_preview.setFrameStyle(QFrame.Box)
        self.color_preview.setStyleSheet("border: 1px solid #ccc;")
        
        # Color hex input
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("#ffffff")
        self.color_input.setMaximumWidth(80)
        self.color_input.textChanged.connect(self.on_text_changed)
        
        # Pick color button
        self.pick_button = QPushButton("Pick")
        self.pick_button.setMaximumWidth(50)
        self.pick_button.clicked.connect(self.pick_color)
        
        layout.addWidget(self.color_preview)
        layout.addWidget(self.color_input)
        layout.addWidget(self.pick_button)
        layout.addStretch()
    
    def pick_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor(QColor(self.current_color), self, "Pick Color")
        if color.isValid():
            self.set_color(color.name())
    
    def set_color(self, color_hex: str):
        """Set the current color"""
        self.current_color = color_hex
        self.color_input.setText(color_hex)
        self.update_display()
        self.color_changed.emit(color_hex)
    
    def on_text_changed(self, text: str):
        """Handle text input changes"""
        if QColor.isValidColor(text):
            self.current_color = text
            self.update_display()
            self.color_changed.emit(text)
    
    def update_display(self):
        """Update the color preview"""
        self.color_preview.setStyleSheet(f"""
            border: 1px solid #ccc;
            background-color: {self.current_color};
        """)
        self.color_input.setText(self.current_color)


class ThemeEditorDialog(QDialog):
    """Advanced theme editor dialog"""
    
    def __init__(self, parent=None, theme_data=None, theme_id=None):
        super().__init__(parent)
        self.theme_data = theme_data or {}
        self.theme_id = theme_id
        self.color_widgets = {}
        
        self.setWindowTitle(f"Edit Theme: {theme_id}" if theme_id else "Create New Theme")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
        self.load_theme_data()
    
    def setup_ui(self):
        """Set up the theme editor UI"""
        layout = QVBoxLayout(self)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Theme Information
        info_group = QGroupBox("Theme Information")
        info_layout = QFormLayout(info_group)
        
        self.theme_id_edit = QLineEdit()
        self.theme_name_edit = QLineEdit()
        self.theme_description_edit = QTextEdit()
        self.theme_description_edit.setMaximumHeight(80)
        
        info_layout.addRow("Theme ID:", self.theme_id_edit)
        info_layout.addRow("Theme Name:", self.theme_name_edit)
        info_layout.addRow("Description:", self.theme_description_edit)
        
        scroll_layout.addWidget(info_group)
        
        # Colors Section
        colors_group = QGroupBox("Color Palette")
        colors_layout = QGridLayout(colors_group)
        
        # Define all possible color properties
        color_properties = [
            # Primary colors
            ("primary", "Primary Color", "#4caf50"),
            ("primary_dark", "Primary Dark", "#45a049"),
            ("primary_light", "Primary Light", "#81c784"),
            ("secondary", "Secondary Color", "#ff9800"),
            
            # Background colors
            ("background", "Main Background", "#fafafa"),
            ("surface", "Surface Color", "#ffffff"),
            ("surface_variant", "Surface Variant", "#f5f5f5"),
            
            # Text colors
            ("text_primary", "Primary Text", "#212121"),
            ("text_secondary", "Secondary Text", "#757575"),
            ("text_disabled", "Disabled Text", "#bdbdbd"),
            
            # Status colors
            ("error", "Error Color", "#f44336"),
            ("warning", "Warning Color", "#ff9800"),
            ("success", "Success Color", "#4caf50"),
            ("info", "Info Color", "#2196f3"),
            
            # Border colors
            ("border", "Border Color", "#e0e0e0"),
            ("border_light", "Light Border", "#f0f0f0"),
            ("border_dark", "Dark Border", "#bdbdbd"),
            
            # Component specific colors
            ("title_background", "Title Background", "#fafafa"),
            ("tab_background", "Tab Background", "#ffffff"),
            ("tab_selected", "Selected Tab", "#f5f5f5"),
            ("menubar_background", "Menu Bar Background", "#fafafa"),
            ("menubar_text", "Menu Bar Text", "#212121"),
            ("button_background", "Button Background", "#4caf50"),
            ("button_text", "Button Text", "#ffffff"),
            ("button_hover", "Button Hover", "#45a049"),
            ("input_background", "Input Background", "#ffffff"),
            ("input_border", "Input Border", "#e0e0e0"),
            ("input_focus", "Input Focus", "#4caf50"),
            
            # Special colors
            ("accent", "Accent Color", "#ff5722"),
            ("highlight", "Highlight Color", "#ffeb3b"),
            ("shadow", "Shadow Color", "#000000"),
        ]
        
        # Create color picker widgets
        for i, (prop, label, default) in enumerate(color_properties):
            row = i // 2
            col = (i % 2) * 2
            
            # Label
            label_widget = QLabel(label)
            colors_layout.addWidget(label_widget, row, col)
            
            # Color picker
            color_widget = ColorPickerWidget(default)
            color_widget.color_changed.connect(lambda color, p=prop: self.update_color_preview(p, color))
            self.color_widgets[prop] = color_widget
            colors_layout.addWidget(color_widget, row, col + 1)
        
        scroll_layout.addWidget(colors_group)
        
        # Typography Section
        typography_group = QGroupBox("Typography")
        typography_layout = QFormLayout(typography_group)
        
        self.font_family_edit = QLineEdit("Segoe UI")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 20)
        self.font_size_spin.setValue(9)
        
        self.header_size_spin = QSpinBox()
        self.header_size_spin.setRange(10, 24)
        self.header_size_spin.setValue(14)
        
        self.button_font_size_spin = QSpinBox()
        self.button_font_size_spin.setRange(6, 16)
        self.button_font_size_spin.setValue(10)
        
        self.line_height_spin = QSpinBox()
        self.line_height_spin.setRange(100, 200)
        self.line_height_spin.setValue(120)
        
        typography_layout.addRow("Font Family:", self.font_family_edit)
        typography_layout.addRow("Font Size:", self.font_size_spin)
        typography_layout.addRow("Header Size:", self.header_size_spin)
        typography_layout.addRow("Button Font Size:", self.button_font_size_spin)
        typography_layout.addRow("Line Height (%):", self.line_height_spin)
        
        scroll_layout.addWidget(typography_group)
        
        # Components Section
        components_group = QGroupBox("Components")
        components_layout = QFormLayout(components_group)
        
        self.border_radius_spin = QSpinBox()
        self.border_radius_spin.setRange(0, 20)
        self.border_radius_spin.setValue(4)
        
        self.padding_spin = QSpinBox()
        self.padding_spin.setRange(0, 20)
        self.padding_spin.setValue(8)
        
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setRange(0, 30)
        self.spacing_spin.setValue(10)
        
        self.shadow_opacity_spin = QSpinBox()
        self.shadow_opacity_spin.setRange(0, 100)
        self.shadow_opacity_spin.setValue(20)
        
        components_layout.addRow("Border Radius:", self.border_radius_spin)
        components_layout.addRow("Padding:", self.padding_spin)
        components_layout.addRow("Spacing:", self.spacing_spin)
        components_layout.addRow("Shadow Opacity (%):", self.shadow_opacity_spin)
        
        scroll_layout.addWidget(components_group)
        
        # Preview Section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_widget = QWidget()
        self.preview_widget.setMinimumHeight(150)
        self.preview_widget.setStyleSheet("border: 1px solid #ccc; background-color: #fafafa;")
        
        preview_layout.addWidget(self.preview_widget)
        
        # Preview controls
        preview_controls = QHBoxLayout()
        self.refresh_preview_btn = QPushButton("Refresh Preview")
        self.refresh_preview_btn.clicked.connect(self.update_preview)
        preview_controls.addWidget(self.refresh_preview_btn)
        preview_controls.addStretch()
        
        preview_layout.addLayout(preview_controls)
        scroll_layout.addWidget(preview_group)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals for live preview
        for widget in self.color_widgets.values():
            widget.color_changed.connect(self.update_preview)
    
    def load_theme_data(self):
        """Load existing theme data"""
        if self.theme_data:
            # Load theme info
            self.theme_id_edit.setText(self.theme_data.get('id', ''))
            self.theme_name_edit.setText(self.theme_data.get('name', ''))
            self.theme_description_edit.setPlainText(self.theme_data.get('description', ''))
            
            # Load colors
            colors = self.theme_data.get('colors', {})
            for prop, widget in self.color_widgets.items():
                if prop in colors:
                    widget.set_color(colors[prop])
            
            # Load typography
            typography = self.theme_data.get('typography', {})
            self.font_family_edit.setText(typography.get('font_family', 'Segoe UI'))
            self.font_size_spin.setValue(typography.get('font_size', 9))
            self.header_size_spin.setValue(typography.get('header_size', 14))
            self.button_font_size_spin.setValue(typography.get('button_font_size', 10))
            self.line_height_spin.setValue(typography.get('line_height', 120))
            
            # Load components
            components = self.theme_data.get('components', {})
            self.border_radius_spin.setValue(components.get('border_radius', 4))
            self.padding_spin.setValue(components.get('padding', 8))
            self.spacing_spin.setValue(components.get('spacing', 10))
            self.shadow_opacity_spin.setValue(components.get('shadow_opacity', 20))
        else:
            # Set defaults for new theme
            self.theme_id_edit.setText(f"custom_{len(theme_creator.list_themes())}")
            self.theme_name_edit.setText("New Custom Theme")
            self.theme_description_edit.setPlainText("Custom theme created by user")
    
    def update_color_preview(self, property_name: str, color: str):
        """Update color preview when colors change"""
        self.update_preview()
    
    def update_preview(self):
        """Update the preview widget"""
        try:
            colors = {}
            for prop, widget in self.color_widgets.items():
                colors[prop] = widget.current_color
            
            # Apply colors to preview
            bg_color = colors.get('background', '#fafafa')
            surface_color = colors.get('surface', '#ffffff')
            primary_color = colors.get('primary', '#4caf50')
            text_color = colors.get('text_primary', '#212121')
            border_color = colors.get('border', '#e0e0e0')
            
            self.preview_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                }}
            """)
            
        except Exception as e:
            print(f"Error updating preview: {e}")
    
    def get_theme_data(self) -> Dict[str, Any]:
        """Get the complete theme data"""
        colors = {}
        for prop, widget in self.color_widgets.items():
            colors[prop] = widget.current_color
        
        return {
            'id': self.theme_id_edit.text() or 'custom_theme',
            'name': self.theme_name_edit.text() or 'Custom Theme',
            'description': self.theme_description_edit.toPlainText(),
            'colors': colors,
            'typography': {
                'font_family': self.font_family_edit.text(),
                'font_size': self.font_size_spin.value(),
                'header_size': self.header_size_spin.value(),
                'button_font_size': self.button_font_size_spin.value(),
                'line_height': self.line_height_spin.value()
            },
            'components': {
                'border_radius': self.border_radius_spin.value(),
                'padding': self.padding_spin.value(),
                'spacing': self.spacing_spin.value(),
                'shadow_opacity': self.shadow_opacity_spin.value()
            }
        }


class DatabaseBackupThread(QThread):
    """Thread for database backup operations"""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, source_path: str, backup_path: str):
        super().__init__()
        self.source_path = source_path
        self.backup_path = backup_path
    
    def run(self):
        """Perform database backup"""
        try:
            self.status_updated.emit("Starting backup...")
            self.progress_updated.emit(10)
            
            # Create backup directory if it doesn't exist
            os.makedirs(os.path.dirname(self.backup_path), exist_ok=True)
            
            self.status_updated.emit("Copying database file...")
            self.progress_updated.emit(50)
            
            shutil.copy2(self.source_path, self.backup_path)
            
            self.status_updated.emit("Backup completed successfully!")
            self.progress_updated.emit(100)
            
            self.finished.emit(True, f"Database backed up to: {self.backup_path}")
            
        except Exception as e:
            self.finished.emit(False, f"Backup failed: {str(e)}")


class SettingsPanel(QWidget):
    """Comprehensive Settings Panel"""
    
    theme_changed = Signal(str)  # Emits theme_id when theme changes
    
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app  # Store reference to main app for theme application
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Set up the settings panel UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.setup_theme_tab()
        self.setup_database_tab()
        self.setup_import_export_tab()
        self.setup_recipe_search_tab()
        self.setup_communication_tab()
        
        layout.addWidget(self.tab_widget)
    
    def setup_theme_tab(self):
        """Set up the theme customization tab"""
        # Create scroll area for theme tab
        theme_scroll = QScrollArea()
        theme_widget = QWidget()
        layout = QVBoxLayout(theme_widget)
        
        # Current Theme Section
        current_group = QGroupBox("Current Theme")
        current_layout = QHBoxLayout(current_group)
        
        current_layout.addWidget(QLabel("Active Theme:"))
        self.current_theme_combo = QComboBox()
        self.current_theme_combo.currentTextChanged.connect(self.on_theme_selection_changed)
        current_layout.addWidget(self.current_theme_combo)
        
        self.apply_theme_btn = QPushButton("Apply Theme")
        self.apply_theme_btn.clicked.connect(self.apply_selected_theme)
        current_layout.addWidget(self.apply_theme_btn)
        
        current_layout.addStretch()
        layout.addWidget(current_group)
        
        # Theme Management Section
        management_group = QGroupBox("Theme Management")
        management_layout = QHBoxLayout(management_group)
        
        self.create_theme_btn = QPushButton("Create New")
        self.create_theme_btn.clicked.connect(self.create_new_theme)
        management_layout.addWidget(self.create_theme_btn)
        
        self.edit_theme_btn = QPushButton("Edit Selected")
        self.edit_theme_btn.clicked.connect(self.edit_selected_theme)
        management_layout.addWidget(self.edit_theme_btn)
        
        self.duplicate_theme_btn = QPushButton("Duplicate")
        self.duplicate_theme_btn.clicked.connect(self.duplicate_selected_theme)
        management_layout.addWidget(self.duplicate_theme_btn)
        
        self.delete_theme_btn = QPushButton("Delete")
        self.delete_theme_btn.clicked.connect(self.delete_selected_theme)
        management_layout.addWidget(self.delete_theme_btn)
        
        management_layout.addStretch()
        layout.addWidget(management_group)
        
        # Theme Preview Section
        preview_group = QGroupBox("Theme Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.theme_preview_widget = QWidget()
        self.theme_preview_widget.setMinimumHeight(200)
        self.theme_preview_widget.setStyleSheet("border: 1px solid #ccc; background-color: #fafafa;")
        
        preview_layout.addWidget(self.theme_preview_widget)
        layout.addWidget(preview_group)
        
        layout.addStretch()
        
        # Set up scroll area
        theme_scroll.setWidget(theme_widget)
        theme_scroll.setWidgetResizable(True)
        theme_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        theme_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.tab_widget.addTab(theme_scroll, "Themes")
    
    def setup_database_tab(self):
        """Set up the database settings tab"""
        db_widget = QWidget()
        layout = QVBoxLayout(db_widget)
        
        # Database Path Section
        path_group = QGroupBox("Database Location")
        path_layout = QFormLayout(path_group)
        
        self.db_path_edit = QLineEdit("data/celiogix.db")
        self.db_path_edit.setReadOnly(True)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_database)
        
        path_row = QHBoxLayout()
        path_row.addWidget(self.db_path_edit)
        path_row.addWidget(browse_btn)
        
        path_layout.addRow("Database Path:", path_row)
        layout.addWidget(path_group)
        
        # Backup Section
        backup_group = QGroupBox("Database Backup")
        backup_layout = QVBoxLayout(backup_group)
        
        backup_controls = QHBoxLayout()
        self.backup_path_edit = QLineEdit()
        self.backup_path_edit.setPlaceholderText("Select backup location...")
        backup_controls.addWidget(self.backup_path_edit)
        
        browse_backup_btn = QPushButton("Browse")
        browse_backup_btn.clicked.connect(self.browse_backup_location)
        backup_controls.addWidget(browse_backup_btn)
        
        backup_controls.addStretch()
        backup_layout.addLayout(backup_controls)
        
        # Backup progress
        self.backup_progress = QProgressBar()
        self.backup_progress.setVisible(False)
        backup_layout.addWidget(self.backup_progress)
        
        self.backup_status = QLabel()
        self.backup_status.setVisible(False)
        backup_layout.addWidget(self.backup_status)
        
        # Backup buttons
        backup_buttons = QHBoxLayout()
        self.backup_now_btn = QPushButton("Backup Now")
        self.backup_now_btn.clicked.connect(self.backup_database)
        backup_buttons.addWidget(self.backup_now_btn)
        
        self.restore_btn = QPushButton("Restore from Backup")
        self.restore_btn.clicked.connect(self.restore_database)
        backup_buttons.addWidget(self.restore_btn)
        
        backup_buttons.addStretch()
        backup_layout.addLayout(backup_buttons)
        
        layout.addWidget(backup_group)
        
        # Database Statistics
        stats_group = QGroupBox("Database Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.db_size_label = QLabel("Calculating...")
        self.db_records_label = QLabel("Calculating...")
        self.last_backup_label = QLabel("Never")
        
        stats_layout.addRow("Database Size:", self.db_size_label)
        stats_layout.addRow("Total Records:", self.db_records_label)
        stats_layout.addRow("Last Backup:", self.last_backup_label)
        
        layout.addWidget(stats_group)
        layout.addStretch()
        
        self.tab_widget.addTab(db_widget, "Database")
    
    def setup_import_export_tab(self):
        """Set up the import/export settings tab"""
        ie_widget = QWidget()
        layout = QVBoxLayout(ie_widget)
        
        # Import Section
        import_group = QGroupBox("Bulk Import")
        import_layout = QVBoxLayout(import_group)
        
        # Import options for each panel
        panels = ["Cookbook", "Pantry", "Calendar", "Menu Planner", "Health Log"]
        
        for panel in panels:
            panel_layout = QHBoxLayout()
            panel_layout.addWidget(QLabel(f"{panel}:"))
            
            import_btn = QPushButton(f"Import {panel}")
            import_btn.clicked.connect(lambda checked, p=panel: self.import_panel_data(p))
            panel_layout.addWidget(import_btn)
            
            export_btn = QPushButton(f"Export {panel}")
            export_btn.clicked.connect(lambda checked, p=panel: self.export_panel_data(p))
            panel_layout.addWidget(export_btn)
            
            panel_layout.addStretch()
            import_layout.addLayout(panel_layout)
        
        # Bulk import button for recipes
        bulk_import_layout = QHBoxLayout()
        bulk_import_btn = QPushButton("Bulk Import Recipes")
        bulk_import_btn.clicked.connect(self.bulk_import_recipes)
        bulk_import_layout.addWidget(bulk_import_btn)
        bulk_import_layout.addStretch()
        import_layout.addLayout(bulk_import_layout)
        
        layout.addWidget(import_group)
        
        # Export Section
        export_group = QGroupBox("Bulk Export")
        export_layout = QVBoxLayout(export_group)
        
        # Export all button
        export_all_btn = QPushButton("Export All Data")
        export_all_btn.clicked.connect(self.export_all_data)
        export_layout.addWidget(export_all_btn)
        
        # Export favorites button
        export_favorites_btn = QPushButton("📤 Export Favorite Recipes")
        export_favorites_btn.clicked.connect(self.export_favorite_recipes)
        export_layout.addWidget(export_favorites_btn)
        
        # Export format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export Format:"))
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["CSV", "JSON", "Excel", "PDF"])
        format_layout.addWidget(self.export_format_combo)
        format_layout.addStretch()
        export_layout.addLayout(format_layout)
        
        layout.addWidget(export_group)
        
        # Import/Export Settings
        settings_group = QGroupBox("Import/Export Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.auto_backup_checkbox = QCheckBox("Create backup before import")
        self.auto_backup_checkbox.setChecked(True)
        settings_layout.addRow("Auto Backup:", self.auto_backup_checkbox)
        
        self.overwrite_checkbox = QCheckBox("Overwrite existing data")
        settings_layout.addRow("Overwrite Mode:", self.overwrite_checkbox)
        
        self.include_metadata_checkbox = QCheckBox("Include metadata in export")
        self.include_metadata_checkbox.setChecked(True)
        settings_layout.addRow("Include Metadata:", self.include_metadata_checkbox)
        
        layout.addWidget(settings_group)
        layout.addStretch()
        
        self.tab_widget.addTab(ie_widget, "Import/Export")
    
    def setup_recipe_search_tab(self):
        """Set up the recipe search settings tab"""
        search_widget = QWidget()
        layout = QVBoxLayout(search_widget)
        
        # Search Sources Section
        sources_group = QGroupBox("Recipe Search Sources")
        sources_layout = QVBoxLayout(sources_group)
        
        # URL list
        sources_layout.addWidget(QLabel("Recipe Website URLs:"))
        self.recipe_urls_list = QListWidget()
        self.recipe_urls_list.setMaximumHeight(150)
        sources_layout.addWidget(self.recipe_urls_list)
        
        # URL management
        url_controls = QHBoxLayout()
        self.add_url_btn = QPushButton("Add URL")
        self.add_url_btn.clicked.connect(self.add_recipe_url)
        url_controls.addWidget(self.add_url_btn)
        
        self.remove_url_btn = QPushButton("Remove URL")
        self.remove_url_btn.clicked.connect(self.remove_recipe_url)
        url_controls.addWidget(self.remove_url_btn)
        
        url_controls.addStretch()
        sources_layout.addLayout(url_controls)
        
        layout.addWidget(sources_group)
        
        # Google Search Section
        google_group = QGroupBox("Google Search Settings")
        google_layout = QFormLayout(google_group)
        
        self.enable_google_search = QCheckBox("Enable Google search")
        self.enable_google_search.setChecked(True)
        google_layout.addRow("Google Search:", self.enable_google_search)
        
        self.google_results_spin = QSpinBox()
        self.google_results_spin.setRange(10, 100)
        self.google_results_spin.setValue(20)
        self.google_results_spin.setSuffix(" results")
        google_layout.addRow("Max Results:", self.google_results_spin)
        
        self.auto_gluten_free = QCheckBox("Automatically add 'gluten free' to searches")
        self.auto_gluten_free.setChecked(True)
        google_layout.addRow("Auto GF:", self.auto_gluten_free)
        
        layout.addWidget(google_group)
        
        # Search Settings
        search_settings_group = QGroupBox("Search Settings")
        search_settings_layout = QFormLayout(search_settings_group)
        
        self.search_timeout_spin = QSpinBox()
        self.search_timeout_spin.setRange(5, 60)
        self.search_timeout_spin.setValue(30)
        self.search_timeout_spin.setSuffix(" seconds")
        search_settings_layout.addRow("Search Timeout:", self.search_timeout_spin)
        
        self.parallel_searches_spin = QSpinBox()
        self.parallel_searches_spin.setRange(1, 10)
        self.parallel_searches_spin.setValue(3)
        search_settings_layout.addRow("Parallel Searches:", self.parallel_searches_spin)
        
        layout.addWidget(search_settings_group)
        
        # Test Search Section
        test_group = QGroupBox("Test Search")
        test_layout = QVBoxLayout(test_group)
        
        test_input_layout = QHBoxLayout()
        test_input_layout.addWidget(QLabel("Test Query:"))
        self.test_search_edit = QLineEdit()
        self.test_search_edit.setPlaceholderText("Enter search terms to test...")
        test_input_layout.addWidget(self.test_search_edit)
        
        self.test_search_btn = QPushButton("Test Search")
        self.test_search_btn.clicked.connect(self.test_recipe_search)
        test_input_layout.addWidget(self.test_search_btn)
        
        test_layout.addLayout(test_input_layout)
        
        # Test results
        self.test_results_list = QListWidget()
        self.test_results_list.setMaximumHeight(100)
        test_layout.addWidget(self.test_results_list)
        
        layout.addWidget(test_group)
        layout.addStretch()
        
        self.tab_widget.addTab(search_widget, "Recipe Search")
    
    def setup_communication_tab(self):
        """Set up the communication settings tab"""
        # Create scroll area for communication tab
        comm_scroll = QScrollArea()
        comm_widget = QWidget()
        layout = QVBoxLayout(comm_widget)
        
        # Email Settings
        email_group = QGroupBox("Email Settings")
        email_layout = QFormLayout(email_group)
        
        self.email_enabled = QCheckBox("Enable email notifications")
        email_layout.addRow("Email Enabled:", self.email_enabled)
        
        self.smtp_server_edit = QLineEdit()
        self.smtp_server_edit.setPlaceholderText("smtp.gmail.com")
        email_layout.addRow("SMTP Server:", self.smtp_server_edit)
        
        self.smtp_port_spin = QSpinBox()
        self.smtp_port_spin.setRange(1, 65535)
        self.smtp_port_spin.setValue(587)
        email_layout.addRow("SMTP Port:", self.smtp_port_spin)
        
        self.email_address_edit = QLineEdit()
        self.email_address_edit.setPlaceholderText("your.email@example.com")
        email_layout.addRow("Email Address:", self.email_address_edit)
        
        self.email_password_edit = QLineEdit()
        self.email_password_edit.setEchoMode(QLineEdit.Password)
        email_layout.addRow("Password:", self.email_password_edit)
        
        layout.addWidget(email_group)
        
        # Text/SMS Settings
        text_group = QGroupBox("Text/SMS Settings")
        text_layout = QFormLayout(text_group)
        
        self.sms_enabled = QCheckBox("Enable SMS notifications")
        text_layout.addRow("SMS Enabled:", self.sms_enabled)
        
        self.phone_number_edit = QLineEdit()
        self.phone_number_edit.setPlaceholderText("+1234567890")
        text_layout.addRow("Phone Number:", self.phone_number_edit)
        
        self.sms_provider_combo = QComboBox()
        self.sms_provider_combo.addItems(["Twilio", "AWS SNS", "Google Cloud", "Custom"])
        text_layout.addRow("SMS Provider:", self.sms_provider_combo)
        
        layout.addWidget(text_group)
        
        # Bluetooth Settings
        bluetooth_group = QGroupBox("Bluetooth Settings")
        bluetooth_layout = QFormLayout(bluetooth_group)
        
        self.bluetooth_enabled = QCheckBox("Enable Bluetooth connectivity")
        bluetooth_layout.addRow("Bluetooth Enabled:", self.bluetooth_enabled)
        
        self.device_name_edit = QLineEdit()
        self.device_name_edit.setPlaceholderText("CeliacShield Device")
        bluetooth_layout.addRow("Device Name:", self.device_name_edit)
        
        self.auto_pair_checkbox = QCheckBox("Auto-pair with known devices")
        bluetooth_layout.addRow("Auto Pair:", self.auto_pair_checkbox)
        
        layout.addWidget(bluetooth_group)
        
        # Mobile Connection Settings
        mobile_group = QGroupBox("Mobile Connection")
        mobile_layout = QFormLayout(mobile_group)
        
        self.mobile_sync_enabled = QCheckBox("Enable mobile app sync")
        mobile_layout.addRow("Mobile Sync:", self.mobile_sync_enabled)
        
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setRange(1, 1440)
        self.sync_interval_spin.setValue(15)
        self.sync_interval_spin.setSuffix(" minutes")
        mobile_layout.addRow("Sync Interval:", self.sync_interval_spin)
        
        self.offline_mode_checkbox = QCheckBox("Enable offline mode")
        mobile_layout.addRow("Offline Mode:", self.offline_mode_checkbox)
        
        layout.addWidget(mobile_group)
        
        # Test Connections
        test_group = QGroupBox("Test Connections")
        test_layout = QHBoxLayout(test_group)
        
        self.test_email_btn = QPushButton("Test Email")
        self.test_email_btn.clicked.connect(self.test_email_connection)
        test_layout.addWidget(self.test_email_btn)
        
        self.test_sms_btn = QPushButton("Test SMS")
        self.test_sms_btn.clicked.connect(self.test_sms_connection)
        test_layout.addWidget(self.test_sms_btn)
        
        self.test_bluetooth_btn = QPushButton("Test Bluetooth")
        self.test_bluetooth_btn.clicked.connect(self.test_bluetooth_connection)
        test_layout.addWidget(self.test_bluetooth_btn)
        
        test_layout.addStretch()
        layout.addWidget(test_group)
        
        layout.addStretch()
        
        # Set up scroll area
        comm_scroll.setWidget(comm_widget)
        comm_scroll.setWidgetResizable(True)
        comm_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        comm_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.tab_widget.addTab(comm_scroll, "Communication")
    
    def load_settings(self):
        """Load all settings from database and files"""
        try:
            # Load themes
            self.load_available_themes()
            
            # Load database settings
            self.load_database_settings()
            
            # Load import/export settings
            self.load_import_export_settings()
            
            # Load recipe search settings
            self.load_recipe_search_settings()
            
            # Load communication settings
            self.load_communication_settings()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings: {e}")
    
    def load_available_themes(self):
        """Load available themes into the combo box"""
        try:
            self.current_theme_combo.clear()
            themes = theme_creator.list_themes()
            
            for theme in themes:
                self.current_theme_combo.addItem(theme['name'], theme['id'])
            
            # Select current theme
            current_theme = theme_creator.current_theme
            if current_theme:
                index = self.current_theme_combo.findData(current_theme)
                if index >= 0:
                    self.current_theme_combo.setCurrentIndex(index)
            
            self.update_theme_preview()
            
        except Exception as e:
            print(f"Error loading themes: {e}")
    
    def load_database_settings(self):
        """Load database-related settings"""
        try:
            # Update database statistics
            self.update_database_statistics()
            
            # Load backup settings
            db = get_connection()
            backup_path = get_setting(db, "backup_path", "")
            self.backup_path_edit.setText(backup_path)
            
            last_backup = get_setting(db, "last_backup", "Never")
            self.last_backup_label.setText(last_backup)
            
        except Exception as e:
            print(f"Error loading database settings: {e}")
    
    def load_import_export_settings(self):
        """Load import/export settings"""
        try:
            db = get_connection()
            
            auto_backup = get_setting(db, "auto_backup", True)
            self.auto_backup_checkbox.setChecked(auto_backup)
            
            overwrite_mode = get_setting(db, "overwrite_mode", False)
            self.overwrite_checkbox.setChecked(overwrite_mode)
            
            include_metadata = get_setting(db, "include_metadata", True)
            self.include_metadata_checkbox.setChecked(include_metadata)
            
            export_format = get_setting(db, "export_format", "CSV")
            index = self.export_format_combo.findText(export_format)
            if index >= 0:
                self.export_format_combo.setCurrentIndex(index)
                
        except Exception as e:
            print(f"Error loading import/export settings: {e}")
    
    def load_recipe_search_settings(self):
        """Load recipe search settings"""
        try:
            db = get_connection()
            
            # Load URLs
            urls_json = get_setting(db, "recipe_urls", "[]")
            urls = json.loads(urls_json)
            self.recipe_urls_list.clear()
            for url in urls:
                self.recipe_urls_list.addItem(url)
            
            # Load Google search settings
            enable_google = get_setting(db, "enable_google_search", True)
            self.enable_google_search.setChecked(enable_google)
            
            max_results = get_setting(db, "google_max_results", 20)
            self.google_results_spin.setValue(max_results)
            
            auto_gf = get_setting(db, "auto_gluten_free", True)
            self.auto_gluten_free.setChecked(auto_gf)
            
            # Load search settings
            timeout = get_setting(db, "search_timeout", 30)
            self.search_timeout_spin.setValue(timeout)
            
            parallel = get_setting(db, "parallel_searches", 3)
            self.parallel_searches_spin.setValue(parallel)
            
        except Exception as e:
            print(f"Error loading recipe search settings: {e}")
    
    def load_communication_settings(self):
        """Load communication settings"""
        try:
            db = get_connection()
            
            # Email settings
            email_enabled = get_setting(db, "email_enabled", False)
            self.email_enabled.setChecked(email_enabled)
            
            smtp_server = get_setting(db, "smtp_server", "")
            self.smtp_server_edit.setText(smtp_server)
            
            smtp_port = get_setting(db, "smtp_port", 587)
            self.smtp_port_spin.setValue(smtp_port)
            
            email_address = get_setting(db, "email_address", "")
            self.email_address_edit.setText(email_address)
            
            # SMS settings
            sms_enabled = get_setting(db, "sms_enabled", False)
            self.sms_enabled.setChecked(sms_enabled)
            
            phone_number = get_setting(db, "phone_number", "")
            self.phone_number_edit.setText(phone_number)
            
            sms_provider = get_setting(db, "sms_provider", "Twilio")
            index = self.sms_provider_combo.findText(sms_provider)
            if index >= 0:
                self.sms_provider_combo.setCurrentIndex(index)
            
            # Bluetooth settings
            bluetooth_enabled = get_setting(db, "bluetooth_enabled", False)
            self.bluetooth_enabled.setChecked(bluetooth_enabled)
            
            device_name = get_setting(db, "bluetooth_device_name", "CeliacShield Device")
            self.device_name_edit.setText(device_name)
            
            auto_pair = get_setting(db, "bluetooth_auto_pair", False)
            self.auto_pair_checkbox.setChecked(auto_pair)
            
            # Mobile settings
            mobile_sync = get_setting(db, "mobile_sync_enabled", False)
            self.mobile_sync_enabled.setChecked(mobile_sync)
            
            sync_interval = get_setting(db, "sync_interval", 15)
            self.sync_interval_spin.setValue(sync_interval)
            
            offline_mode = get_setting(db, "offline_mode", False)
            self.offline_mode_checkbox.setChecked(offline_mode)
            
        except Exception as e:
            print(f"Error loading communication settings: {e}")
    
    def update_database_statistics(self):
        """Update database statistics display"""
        try:
            db_path = self.db_path_edit.text()
            if os.path.exists(db_path):
                # Get file size
                size_bytes = os.path.getsize(db_path)
                size_mb = size_bytes / (1024 * 1024)
                self.db_size_label.setText(f"{size_mb:.2f} MB")
                
                # Get record count
                db = get_connection()
                cursor = db.cursor()
                
                tables = ['recipes', 'pantry_items', 'health_log', 'calendar_events', 'menu_plans']
                total_records = 0
                
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        total_records += count
                    except:
                        pass
                
                self.db_records_label.setText(str(total_records))
                
            else:
                self.db_size_label.setText("Database not found")
                self.db_records_label.setText("0")
                
        except Exception as e:
            self.db_size_label.setText("Error")
            self.db_records_label.setText("Error")
    
    def on_theme_selection_changed(self, theme_name):
        """Handle theme selection change"""
        self.update_theme_preview()
    
    def update_theme_preview(self):
        """Update the theme preview widget"""
        try:
            current_data = self.current_theme_combo.currentData()
            if current_data:
                theme_data = theme_creator.load_theme(current_data)
                if theme_data:
                    colors = theme_data.get('colors', {})
                    
                    # Apply theme colors to preview
                    bg_color = colors.get('background', '#fafafa')
                    surface_color = colors.get('surface', '#ffffff')
                    primary_color = colors.get('primary', '#4caf50')
                    text_color = colors.get('text_primary', '#212121')
                    
                    self.theme_preview_widget.setStyleSheet(f"""
                        QWidget {{
                            background-color: {bg_color};
                            color: {text_color};
                            border: 1px solid #ccc;
                        }}
                    """)
                    
        except Exception as e:
            print(f"Error updating theme preview: {e}")
    
    def apply_selected_theme(self):
        """Apply the currently selected theme"""
        try:
            theme_id = self.current_theme_combo.currentData()
            if not theme_id:
                QMessageBox.warning(self, "No Selection", "Please select a theme to apply.")
                return

            print(f"DEBUG: Apply Theme clicked - selected theme: '{theme_id}'")
            
            # Apply the theme
            from PySide6.QtWidgets import QApplication
            app = self.app or QApplication.instance()
            if app and theme_creator.apply_theme(theme_id, app):
                print(f"DEBUG: Theme {theme_id} applied successfully")
                QMessageBox.information(self, "Theme Changed", f"Theme applied successfully!")
                self.theme_changed.emit(theme_id)
                # Update the preview to reflect the applied theme
                self.update_theme_preview()
            else:
                print(f"DEBUG: Failed to apply theme {theme_id}")
                QMessageBox.warning(self, "Theme Error", "Failed to apply theme.")
                
        except Exception as e:
            print(f"DEBUG: Error applying theme: {e}")
            QMessageBox.critical(self, "Theme Error", f"Failed to apply theme: {e}")
    
    def create_new_theme(self):
        """Create a new theme"""
        try:
            dialog = ThemeEditorDialog(self)
            if dialog.exec() == QDialog.Accepted:
                theme_data = dialog.get_theme_data()
                
                # Save the new theme
                if theme_creator.save_theme(theme_data['id'], theme_data):
                    QMessageBox.information(self, "Success", "New theme created successfully!")
                    self.load_available_themes()
                else:
                    QMessageBox.warning(self, "Error", "Failed to save new theme.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create theme: {e}")
    
    def edit_selected_theme(self):
        """Edit the selected theme"""
        try:
            theme_id = self.current_theme_combo.currentData()
            if not theme_id:
                QMessageBox.warning(self, "No Selection", "Please select a theme to edit.")
                return

            theme_data = theme_creator.load_theme(theme_id)
            if not theme_data:
                QMessageBox.warning(self, "Error", "Failed to load theme data.")
                return
            
            dialog = ThemeEditorDialog(self, theme_data, theme_id)
            if dialog.exec() == QDialog.Accepted:
                new_theme_data = dialog.get_theme_data()
                
                # Save the updated theme
                if theme_creator.save_theme(theme_id, new_theme_data):
                    QMessageBox.information(self, "Success", "Theme updated successfully!")
                    self.load_available_themes()
                else:
                    QMessageBox.warning(self, "Error", "Failed to save theme changes.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit theme: {e}")
    
    def duplicate_selected_theme(self):
        """Duplicate the selected theme"""
        try:
            theme_id = self.current_theme_combo.currentData()
            if not theme_id:
                QMessageBox.warning(self, "No Selection", "Please select a theme to duplicate.")
                return
            
            theme_data = theme_creator.load_theme(theme_id)
            if not theme_data:
                QMessageBox.warning(self, "Error", "Failed to load theme data.")
                return

            # Create new theme ID and name
            new_id = f"{theme_id}_copy"
            theme_data['id'] = new_id
            theme_data['name'] = f"{theme_data.get('name', 'Theme')} (Copy)"
            
            dialog = ThemeEditorDialog(self, theme_data, new_id)
            if dialog.exec() == QDialog.Accepted:
                new_theme_data = dialog.get_theme_data()
                
                if theme_creator.save_theme(new_id, new_theme_data):
                    QMessageBox.information(self, "Success", "Theme duplicated successfully!")
                    self.load_available_themes()
                else:
                    QMessageBox.warning(self, "Error", "Failed to save duplicated theme.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to duplicate theme: {e}")
    
    def delete_selected_theme(self):
        """Delete the selected theme"""
        try:
            theme_id = self.current_theme_combo.currentData()
            if not theme_id:
                QMessageBox.warning(self, "No Selection", "Please select a theme to delete.")
                return

            # Confirm deletion
            reply = QMessageBox.question(
                self, "Confirm Delete", 
                f"Are you sure you want to delete the theme '{self.current_theme_combo.currentText()}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if theme_creator.delete_theme(theme_id):
                    QMessageBox.information(self, "Success", "Theme deleted successfully!")
                    self.load_available_themes()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete theme.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete theme: {e}")
    
    def browse_database(self):
        """Browse for database file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Database File", "", "SQLite Database (*.db *.sqlite *.sqlite3)"
        )
        if file_path:
            self.db_path_edit.setText(file_path)
    
    def browse_backup_location(self):
        """Browse for backup location"""
        directory = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if directory:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(directory, f"celiogix_backup_{timestamp}.db")
            self.backup_path_edit.setText(backup_path)
    
    def backup_database(self):
        """Backup the database"""
        try:
            source_path = self.db_path_edit.text()
            backup_path = self.backup_path_edit.text()
            
            if not source_path or not backup_path:
                QMessageBox.warning(self, "Missing Information", "Please specify both source and backup paths.")
                return
            
            if not os.path.exists(source_path):
                QMessageBox.warning(self, "Source Not Found", "Source database file not found.")
                return

            # Show progress
            self.backup_progress.setVisible(True)
            self.backup_status.setVisible(True)
            self.backup_now_btn.setEnabled(False)
            
            # Start backup thread
            self.backup_thread = DatabaseBackupThread(source_path, backup_path)
            self.backup_thread.progress_updated.connect(self.backup_progress.setValue)
            self.backup_thread.status_updated.connect(self.backup_status.setText)
            self.backup_thread.finished.connect(self.on_backup_finished)
            self.backup_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to start backup: {e}")
    
    def on_backup_finished(self, success, message):
        """Handle backup completion"""
        self.backup_progress.setVisible(False)
        self.backup_status.setVisible(False)
        self.backup_now_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Backup Complete", message)
            # Save backup path setting
            try:
                db = get_connection()
                set_setting(db, "backup_path", os.path.dirname(self.backup_path_edit.text()))
                set_setting(db, "last_backup", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                self.last_backup_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            except:
                pass
        else:
            QMessageBox.critical(self, "Backup Failed", message)
    
    def restore_database(self):
        """Restore database from backup"""
        try:
            backup_path, _ = QFileDialog.getOpenFileName(
                self, "Select Backup File", "", "Database Files (*.db *.sqlite *.sqlite3)"
            )
            
            if backup_path:
                # Confirm restoration
                reply = QMessageBox.question(
                    self, "Confirm Restore", 
                    "This will replace your current database with the backup. Continue?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    source_path = self.db_path_edit.text()
                    
                    # Create backup of current database first
                    if os.path.exists(source_path):
                        backup_current = f"{source_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        shutil.copy2(source_path, backup_current)
                    
                    # Restore from backup
                    shutil.copy2(backup_path, source_path)
                    
                    QMessageBox.information(self, "Restore Complete", "Database restored successfully!")
                    self.update_database_statistics()
                    
        except Exception as e:
            QMessageBox.critical(self, "Restore Error", f"Failed to restore database: {e}")
    
    def import_panel_data(self, panel_name):
        """Import data for a specific panel"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, f"Import {panel_name} Data", "", 
                "CSV Files (*.csv);;JSON Files (*.json);;Excel Files (*.xlsx)"
            )
            
            if file_path:
                from services.import_export_service import ImportExportService
                ie_service = ImportExportService()
                
                # Get overwrite mode setting
                overwrite_mode = self.overwrite_checkbox.isChecked()
                
                success, message = ie_service.import_panel_data(panel_name.lower().replace(' ', '_'), file_path, overwrite_mode)
                
                if success:
                    QMessageBox.information(self, "Import Success", f"Successfully imported {panel_name} data:\n{message}")
                else:
                    QMessageBox.warning(self, "Import Failed", f"Failed to import {panel_name} data:\n{message}")
                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import {panel_name} data: {e}")
    
    def export_panel_data(self, panel_name):
        """Export data for a specific panel"""
        try:
            # Get export format
            format_type = self.export_format_combo.currentText().lower()
            file_extension = format_type if format_type != 'excel' else 'xlsx'
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, f"Export {panel_name} Data", f"{panel_name.lower().replace(' ', '_')}_export.{file_extension}",
                f"{format_type.upper()} Files (*.{file_extension})"
            )
            
            if file_path:
                from services.import_export_service import ImportExportService
                ie_service = ImportExportService()
                
                # Get metadata setting
                include_metadata = self.include_metadata_checkbox.isChecked()
                
                success = ie_service.export_panel_data(
                    panel_name.lower().replace(' ', '_'), 
                    file_path, 
                    format_type, 
                    include_metadata
                )
                
                if success:
                    QMessageBox.information(self, "Export Success", f"Successfully exported {panel_name} data to:\n{file_path}")
                else:
                    QMessageBox.warning(self, "Export Failed", f"Failed to export {panel_name} data")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export {panel_name} data: {e}")
    
    def export_all_data(self):
        """Export all application data"""
        try:
            directory = QFileDialog.getExistingDirectory(self, "Select Export Directory")
            if directory:
                from services.import_export_service import ImportExportService
                ie_service = ImportExportService()
                
                # Get export format and metadata setting
                format_type = self.export_format_combo.currentText().lower()
                include_metadata = self.include_metadata_checkbox.isChecked()
                
                success = ie_service.export_all_data(directory, format_type, include_metadata)
                
                if success:
                    QMessageBox.information(self, "Export All Success", f"Successfully exported all data to:\n{directory}")
                else:
                    QMessageBox.warning(self, "Export All Failed", "Failed to export all data")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export all data: {e}")
    
    def export_favorite_recipes(self):
        """Export all favorite recipes"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes WHERE is_favorite = 1 ORDER BY title")
            favorites = cursor.fetchall()
            conn.close()
            
            if not favorites:
                QMessageBox.information(self, "No Favorites", "You haven't marked any recipes as favorites yet.")
                return
            
            # Show export options dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Export Favorites")
            dialog.setModal(True)
            dialog.resize(300, 200)
            
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel(f"Export {len(favorites)} favorite recipes as:"))
            
            # Format selection
            format_combo = QComboBox()
            format_combo.addItems(["HTML", "TXT", "JSON", "CSV"])
            layout.addWidget(format_combo)
            
            # Options
            include_metadata_cb = QCheckBox("Include metadata")
            include_metadata_cb.setChecked(True)
            layout.addWidget(include_metadata_cb)
            
            # Buttons
            button_layout = QHBoxLayout()
            export_btn = QPushButton("Export")
            cancel_btn = QPushButton("Cancel")
            
            def export_selected():
                format_type = format_combo.currentText().lower()
                include_meta = include_metadata_cb.isChecked()
                dialog.accept()
                self._perform_favorites_export(favorites, format_type, include_meta)
            
            export_btn.clicked.connect(export_selected)
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(export_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export favorites: {str(e)}")
    
    def _perform_favorites_export(self, favorites, format_type, include_metadata):
        """Perform the actual export of favorite recipes"""
        try:
            import os
            from datetime import datetime
            
            # Create Export folder if it doesn't exist
            export_folder = "Export"
            if not os.path.exists(export_folder):
                os.makedirs(export_folder)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Favorite_Recipes_{timestamp}.{format_type}"
            file_path = os.path.join(export_folder, filename)
            
            if format_type == 'html':
                self._export_favorites_html(favorites, file_path, include_metadata)
            elif format_type == 'txt':
                self._export_favorites_txt(favorites, file_path, include_metadata)
            elif format_type == 'json':
                self._export_favorites_json(favorites, file_path, include_metadata)
            elif format_type == 'csv':
                self._export_favorites_csv(favorites, file_path, include_metadata)
            
            # Open the exported file
            try:
                import platform
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':  # macOS
                    import subprocess
                    subprocess.run(['open', file_path])
                else:  # Linux
                    import subprocess
                    subprocess.run(['xdg-open', file_path])
                
                QMessageBox.information(self, "Export Complete", 
                                      f"Favorite recipes exported and opened:\n{file_path}")
            except Exception as e:
                QMessageBox.information(self, "Export Complete", 
                                      f"Favorite recipes exported to:\n{file_path}\n\nCould not open file automatically: {str(e)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export favorites: {str(e)}")
    
    def _export_favorites_html(self, favorites, file_path, include_metadata):
        """Export favorites as HTML"""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Favorite Recipes</title>
    <style>
        body { font-family: Georgia, serif; line-height: 1.6; margin: 40px; background: #f9f9f9; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }
        .recipe { margin: 30px 0; padding: 20px; border-left: 4px solid #f39c12; background: #f8f9fa; }
        .recipe h2 { color: #e74c3c; margin-top: 0; }
        .recipe-meta { color: #666; font-size: 0.9em; margin-bottom: 15px; }
        .ingredients, .instructions { margin: 15px 0; }
        .ingredients h3, .instructions h3 { color: #2c3e50; margin-bottom: 10px; }
        ul, ol { padding-left: 25px; }
        li { margin-bottom: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⭐ My Favorite Recipes</h1>
"""
        
        for recipe in favorites:
            html_content += f"""
        <div class="recipe">
            <h2>{recipe[1]}</h2>
            <div class="recipe-meta">
                Category: {recipe[9] or 'N/A'} | 
                Prep Time: {recipe[4] or 'N/A'} | 
                Cook Time: {recipe[5] or 'N/A'} | 
                Servings: {recipe[6] or 'N/A'} | 
                Difficulty: {recipe[10] or 'N/A'}
            </div>
            <div class="ingredients">
                <h3>Ingredients:</h3>
                <ul>
                    {self._format_ingredients_for_html(recipe[2] or '')}
                </ul>
            </div>
            <div class="instructions">
                <h3>Instructions:</h3>
                <ol>
                    {self._format_instructions_for_html(recipe[3] or '')}
                </ol>
            </div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _export_favorites_txt(self, favorites, file_path, include_metadata):
        """Export favorites as TXT"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("⭐ MY FAVORITE RECIPES\n")
            f.write("=" * 50 + "\n\n")
            
            for i, recipe in enumerate(favorites, 1):
                f.write(f"{i}. {recipe[1]}\n")
                f.write("-" * 30 + "\n")
                f.write(f"Category: {recipe[9] or 'N/A'}\n")
                f.write(f"Prep Time: {recipe[4] or 'N/A'}\n")
                f.write(f"Cook Time: {recipe[5] or 'N/A'}\n")
                f.write(f"Servings: {recipe[6] or 'N/A'}\n")
                f.write(f"Difficulty: {recipe[10] or 'N/A'}\n\n")
                
                f.write("INGREDIENTS:\n")
                f.write(recipe[2] or 'No ingredients listed\n')
                f.write("\n\nINSTRUCTIONS:\n")
                f.write(recipe[3] or 'No instructions listed\n')
                f.write("\n" + "=" * 50 + "\n\n")
    
    def _export_favorites_json(self, favorites, file_path, include_metadata):
        """Export favorites as JSON"""
        import json
        
        favorites_data = []
        for recipe in favorites:
            recipe_data = {
                'id': recipe[0],
                'title': recipe[1],
                'ingredients': recipe[2],
                'instructions': recipe[3],
                'prep_time': recipe[4],
                'cook_time': recipe[5],
                'servings': recipe[6],
                'category': recipe[9],
                'difficulty': recipe[10],
                'is_favorite': True
            }
            favorites_data.append(recipe_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(favorites_data, f, indent=2, ensure_ascii=False)
    
    def _export_favorites_csv(self, favorites, file_path, include_metadata):
        """Export favorites as CSV"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Title', 'Category', 'Prep Time', 'Cook Time', 'Servings', 'Difficulty', 'Ingredients', 'Instructions'])
            
            for recipe in favorites:
                writer.writerow([
                    recipe[1],  # title
                    recipe[9],  # category
                    recipe[4],  # prep_time
                    recipe[5],  # cook_time
                    recipe[6],  # servings
                    recipe[10], # difficulty
                    recipe[2],  # ingredients
                    recipe[3]   # instructions
                ])
    
    def _format_ingredients_for_html(self, ingredients_text):
        """Format ingredients text for HTML display"""
        if not ingredients_text:
            return "<li>No ingredients listed</li>"
        
        # Split by newlines and create list items
        ingredients = [ing.strip() for ing in ingredients_text.split('\n') if ing.strip()]
        return '\n                    '.join([f"<li>{ing}</li>" for ing in ingredients])
    
    def _format_instructions_for_html(self, instructions_text):
        """Format instructions text for HTML display"""
        if not instructions_text:
            return "<li>No instructions listed</li>"
        
        # Split by newlines or periods and create list items
        instructions = []
        for line in instructions_text.split('\n'):
            if line.strip():
                # Split by periods if it's a long line
                if '. ' in line and len(line) > 100:
                    steps = line.split('. ')
                    for step in steps:
                        if step.strip():
                            instructions.append(step.strip() + '.')
                else:
                    instructions.append(line.strip())
        
        return '\n                    '.join([f"<li>{inst}</li>" for inst in instructions])
    
    def add_recipe_url(self):
        """Add a new recipe URL"""
        from PySide6.QtWidgets import QInputDialog
        url, ok = QInputDialog.getText(self, "Add Recipe URL", "Enter the URL:")
        if ok and url.strip():
            self.recipe_urls_list.addItem(url.strip())
            self.save_recipe_search_settings()
    
    def remove_recipe_url(self):
        """Remove selected recipe URL"""
        current_row = self.recipe_urls_list.currentRow()
        if current_row >= 0:
            self.recipe_urls_list.takeItem(current_row)
            self.save_recipe_search_settings()
    
    def test_recipe_search(self):
        """Test recipe search functionality"""
        query = self.test_search_edit.text().strip()
        if not query:
            QMessageBox.warning(self, "No Query", "Please enter a search query.")
            return
        
        # TODO: Implement recipe search test
        self.test_results_list.clear()
        self.test_results_list.addItem(f"Testing search for: {query}")
        self.test_results_list.addItem("(Search functionality not yet implemented)")
    
    def test_email_connection(self):
        """Test email connection"""
        # TODO: Implement email connection test
        QMessageBox.information(self, "Test Email", "Email connection test not yet implemented.")
    
    def test_sms_connection(self):
        """Test SMS connection"""
        # TODO: Implement SMS connection test
        QMessageBox.information(self, "Test SMS", "SMS connection test not yet implemented.")
    
    def test_bluetooth_connection(self):
        """Test Bluetooth connection"""
        # TODO: Implement Bluetooth connection test
        QMessageBox.information(self, "Test Bluetooth", "Bluetooth connection test not yet implemented.")
    
    def save_recipe_search_settings(self):
        """Save recipe search settings"""
        try:
            db = get_connection()
            
            # Save URLs
            urls = []
            for i in range(self.recipe_urls_list.count()):
                urls.append(self.recipe_urls_list.item(i).text())
            
            set_setting(db, "recipe_urls", json.dumps(urls))
            set_setting(db, "enable_google_search", self.enable_google_search.isChecked())
            set_setting(db, "google_max_results", self.google_results_spin.value())
            set_setting(db, "auto_gluten_free", self.auto_gluten_free.isChecked())
            set_setting(db, "search_timeout", self.search_timeout_spin.value())
            set_setting(db, "parallel_searches", self.parallel_searches_spin.value())
            
        except Exception as e:
            print(f"Error saving recipe search settings: {e}")
    
    def save_communication_settings(self):
        """Save communication settings"""
        try:
            db = get_connection()
            
            # Email settings
            set_setting(db, "email_enabled", self.email_enabled.isChecked())
            set_setting(db, "smtp_server", self.smtp_server_edit.text())
            set_setting(db, "smtp_port", self.smtp_port_spin.value())
            set_setting(db, "email_address", self.email_address_edit.text())
            
            # SMS settings
            set_setting(db, "sms_enabled", self.sms_enabled.isChecked())
            set_setting(db, "phone_number", self.phone_number_edit.text())
            set_setting(db, "sms_provider", self.sms_provider_combo.currentText())
            
            # Bluetooth settings
            set_setting(db, "bluetooth_enabled", self.bluetooth_enabled.isChecked())
            set_setting(db, "bluetooth_device_name", self.device_name_edit.text())
            set_setting(db, "bluetooth_auto_pair", self.auto_pair_checkbox.isChecked())
            
            # Mobile settings
            set_setting(db, "mobile_sync_enabled", self.mobile_sync_enabled.isChecked())
            set_setting(db, "sync_interval", self.sync_interval_spin.value())
            set_setting(db, "offline_mode", self.offline_mode_checkbox.isChecked())
            
        except Exception as e:
            print(f"Error saving communication settings: {e}")
    
    def save_import_export_settings(self):
        """Save import/export settings"""
        try:
            db = get_connection()
            
            set_setting(db, "auto_backup", self.auto_backup_checkbox.isChecked())
            set_setting(db, "overwrite_mode", self.overwrite_checkbox.isChecked())
            set_setting(db, "include_metadata", self.include_metadata_checkbox.isChecked())
            set_setting(db, "export_format", self.export_format_combo.currentText())
            
        except Exception as e:
            print(f"Error saving import/export settings: {e}")
    
    def bulk_import_recipes(self):
        """Bulk import recipes from files"""
        try:
            # Show file selection dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Recipes", "", 
                "All Supported Files (*.csv *.json *.xlsx *.xls);;CSV Files (*.csv);;JSON Files (*.json);;Excel Files (*.xlsx *.xls)"
            )
            
            if file_path:
                # Show import options dialog
                dialog = QDialog(self)
                dialog.setWindowTitle("Import Options")
                dialog.setModal(True)
                dialog.resize(300, 200)
                
                layout = QVBoxLayout(dialog)
                layout.addWidget(QLabel("Select import options:"))
                
                # Options
                update_existing_cb = QCheckBox("Update existing recipes")
                update_existing_cb.setChecked(True)
                layout.addWidget(update_existing_cb)
                
                skip_duplicates_cb = QCheckBox("Skip duplicate recipes")
                skip_duplicates_cb.setChecked(True)
                layout.addWidget(skip_duplicates_cb)
                
                validate_ingredients_cb = QCheckBox("Validate ingredients")
                validate_ingredients_cb.setChecked(True)
                layout.addWidget(validate_ingredients_cb)
                
                # Buttons
                button_layout = QHBoxLayout()
                import_btn = QPushButton("Import")
                cancel_btn = QPushButton("Cancel")
                
                import_btn.clicked.connect(dialog.accept)
                cancel_btn.clicked.connect(dialog.reject)
                
                button_layout.addWidget(import_btn)
                button_layout.addWidget(cancel_btn)
                layout.addLayout(button_layout)
                
                if dialog.exec() == QDialog.Accepted:
                    self._perform_bulk_import(
                        file_path, 
                        update_existing_cb.isChecked(),
                        skip_duplicates_cb.isChecked(),
                        validate_ingredients_cb.isChecked()
                    )
                    
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import recipes: {str(e)}")
    
    def _perform_bulk_import(self, file_path, update_existing, skip_duplicates, validate_ingredients):
        """Perform the actual bulk import"""
        try:
            import os
            import json
            import pandas as pd
            
            file_ext = os.path.splitext(file_path)[1].lower()
            imported_count = 0
            skipped_count = 0
            
            if file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    recipes_data = json.load(f)
                    
                if isinstance(recipes_data, list):
                    recipes = recipes_data
                else:
                    recipes = [recipes_data]
                    
            elif file_ext in ['.csv']:
                df = pd.read_csv(file_path)
                recipes = df.to_dict('records')
                
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                recipes = df.to_dict('records')
                
            else:
                QMessageBox.warning(self, "Unsupported Format", f"File format {file_ext} is not supported.")
                return
            
            # Process each recipe
            for recipe_data in recipes:
                # Normalize recipe data
                normalized_recipe = self._normalize_recipe_data(recipe_data)
                
                # Check for duplicates
                if skip_duplicates and self._is_duplicate_recipe(normalized_recipe['name']):
                    skipped_count += 1
                    continue
                
                # Validate ingredients if requested
                if validate_ingredients and not self._validate_recipe_ingredients(normalized_recipe):
                    skipped_count += 1
                    continue
                
                # Import the recipe
                if self._import_single_recipe(normalized_recipe, update_existing):
                    imported_count += 1
            
            # Show results
            QMessageBox.information(
                self, "Import Complete", 
                f"Import completed!\n\nImported: {imported_count} recipes\nSkipped: {skipped_count} recipes"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to perform bulk import: {str(e)}")
    
    def _normalize_recipe_data(self, recipe_data):
        """Normalize recipe data to standard format"""
        normalized = {
            'name': recipe_data.get('name', recipe_data.get('title', 'Untitled Recipe')),
            'category': recipe_data.get('category', recipe_data.get('type', 'General')),
            'prep_time': recipe_data.get('prep_time', recipe_data.get('prepTime', 0)),
            'cook_time': recipe_data.get('cook_time', recipe_data.get('cookTime', 0)),
            'servings': recipe_data.get('servings', recipe_data.get('yield', 1)),
            'difficulty': recipe_data.get('difficulty', recipe_data.get('level', 'Easy')),
            'ingredients': recipe_data.get('ingredients', recipe_data.get('ingredientList', [])),
            'instructions': recipe_data.get('instructions', recipe_data.get('instructionList', '')),
            'notes': recipe_data.get('notes', recipe_data.get('description', ''))
        }
        
        # Convert ingredients to string if it's a list
        if isinstance(normalized['ingredients'], list):
            normalized['ingredients'] = '\n'.join(normalized['ingredients'])
        
        # Convert instructions to string if it's a list
        if isinstance(normalized['instructions'], list):
            normalized['instructions'] = '\n'.join(normalized['instructions'])
        
        return normalized
    
    def _is_duplicate_recipe(self, recipe_name):
        """Check if a recipe with the same name already exists"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE name = ?", (recipe_name,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception:
            return False
    
    def _validate_recipe_ingredients(self, recipe_data):
        """Validate recipe ingredients"""
        ingredients = recipe_data.get('ingredients', '')
        if not ingredients or not ingredients.strip():
            return False
        return True
    
    def _import_single_recipe(self, recipe_data, update_existing):
        """Import a single recipe to the database"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if update_existing:
                # Update existing recipe
                cursor.execute("""
                    UPDATE recipes SET 
                        category = ?, prep_time = ?, cook_time = ?, servings = ?, 
                        difficulty = ?, ingredients = ?, instructions = ?, notes = ?
                    WHERE name = ?
                """, (
                    recipe_data['category'], recipe_data['prep_time'], recipe_data['cook_time'],
                    recipe_data['servings'], recipe_data['difficulty'], recipe_data['ingredients'],
                    recipe_data['instructions'], recipe_data['notes'], recipe_data['name']
                ))
            else:
                # Insert new recipe
                cursor.execute("""
                    INSERT INTO recipes (name, category, prep_time, cook_time, servings, 
                                       difficulty, ingredients, instructions, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    recipe_data['name'], recipe_data['category'], recipe_data['prep_time'],
                    recipe_data['cook_time'], recipe_data['servings'], recipe_data['difficulty'],
                    recipe_data['ingredients'], recipe_data['instructions'], recipe_data['notes']
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error importing recipe {recipe_data['name']}: {e}")
            return False
    
    def closeEvent(self, event):
        """Save settings when closing"""
        try:
            self.save_recipe_search_settings()
            self.save_communication_settings()
            self.save_import_export_settings()
        except Exception as e:
            print(f"Error saving settings on close: {e}")

        event.accept()