# path: panels/theme_editor_panel.py
"""
Theme Editor Panel for PySide6 Application

Provides theme creation, editing, and management functionality.
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QMessageBox, QDialog,
    QColorDialog, QSpinBox, QFileDialog, QTabWidget, QScrollArea,
    QGridLayout, QCheckBox, QSlider, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPalette

from panels.base_panel import BasePanel
from services.theme_creator import theme_creator


class ThemeEditDialog(QDialog):
    """Dialog for editing themes"""
    
    def __init__(self, parent=None, theme_id=None):
        super().__init__(parent)
        self.theme_id = theme_id
        self.setWindowTitle(f"Edit Theme: {theme_id}")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        self.setup_ui()
        if theme_id:
            self.load_theme_data()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Theme info
        info_group = QGroupBox("Theme Information")
        info_layout = QGridLayout(info_group)
        
        self.theme_id_edit = QLineEdit()
        self.theme_name_edit = QLineEdit()
        self.theme_description_edit = QTextEdit()
        self.theme_description_edit.setMaximumHeight(80)
        
        info_layout.addWidget(QLabel("Theme ID:"), 0, 0)
        info_layout.addWidget(self.theme_id_edit, 0, 1)
        info_layout.addWidget(QLabel("Theme Name:"), 1, 0)
        info_layout.addWidget(self.theme_name_edit, 1, 1)
        info_layout.addWidget(QLabel("Description:"), 2, 0)
        info_layout.addWidget(self.theme_description_edit, 2, 1)
        
        scroll_layout.addWidget(info_group)
        
        # Colors
        colors_group = QGroupBox("Colors")
        colors_layout = QGridLayout(colors_group)
        
        self.color_edits = {}
        color_properties = [
            "primary", "primary_dark", "primary_light", "secondary",
            "background", "surface", "surface_variant", "text_primary",
            "text_secondary", "text_disabled", "error", "border",
            "title_background", "tab_background", "tab_selected", 
            "menubar_background", "menubar_text"
        ]
        
        for i, prop in enumerate(color_properties):
            row = i // 2
            col = (i % 2) * 3
            
            colors_layout.addWidget(QLabel(f"{prop.replace('_', ' ').title()}:"), row, col)
            
            color_edit = QLineEdit()
            color_edit.setText("#4caf50" if "primary" in prop else "#ffffff" if "surface" in prop or "background" in prop else "#212121")
            self.color_edits[prop] = color_edit
            colors_layout.addWidget(color_edit, row, col + 1)
            
            color_btn = QPushButton("...")
            color_btn.setMaximumWidth(30)
            color_btn.clicked.connect(lambda checked, p=prop: self.select_color(p))
            colors_layout.addWidget(color_btn, row, col + 2)
        
        scroll_layout.addWidget(colors_group)
        
        # Typography
        typography_group = QGroupBox("Typography")
        typography_layout = QGridLayout(typography_group)
        
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
        
        typography_layout.addWidget(QLabel("Font Family:"), 0, 0)
        typography_layout.addWidget(self.font_family_edit, 0, 1)
        typography_layout.addWidget(QLabel("Font Size:"), 1, 0)
        typography_layout.addWidget(self.font_size_spin, 1, 1)
        typography_layout.addWidget(QLabel("Header Size:"), 2, 0)
        typography_layout.addWidget(self.header_size_spin, 2, 1)
        typography_layout.addWidget(QLabel("Button Font Size:"), 3, 0)
        typography_layout.addWidget(self.button_font_size_spin, 3, 1)
        
        scroll_layout.addWidget(typography_group)
        
        # Components
        components_group = QGroupBox("Components")
        components_layout = QGridLayout(components_group)
        
        self.border_radius_spin = QSpinBox()
        self.border_radius_spin.setRange(0, 20)
        self.border_radius_spin.setValue(4)
        self.padding_spin = QSpinBox()
        self.padding_spin.setRange(0, 20)
        self.padding_spin.setValue(8)
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setRange(0, 30)
        self.spacing_spin.setValue(10)
        
        components_layout.addWidget(QLabel("Border Radius:"), 0, 0)
        components_layout.addWidget(self.border_radius_spin, 0, 1)
        components_layout.addWidget(QLabel("Padding:"), 1, 0)
        components_layout.addWidget(self.padding_spin, 1, 1)
        components_layout.addWidget(QLabel("Spacing:"), 2, 0)
        components_layout.addWidget(self.spacing_spin, 2, 1)
        
        scroll_layout.addWidget(components_group)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_theme)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def load_theme_data(self):
        """Load theme data for editing"""
        theme_data = theme_creator.load_theme(self.theme_id)
        if not theme_data:
            return
        
        # Load theme info
        self.theme_id_edit.setText(self.theme_id)
        self.theme_name_edit.setText(theme_data.get('name', ''))
        self.theme_description_edit.setPlainText(theme_data.get('description', ''))
        
        # Load colors
        colors = theme_data.get('colors', {})
        for prop, color_edit in self.color_edits.items():
            color_edit.setText(colors.get(prop, '#ffffff'))
        
        # Load typography
        typography = theme_data.get('typography', {})
        self.font_family_edit.setText(typography.get('font_family', 'Segoe UI'))
        self.font_size_spin.setValue(typography.get('font_size', 9))
        self.header_size_spin.setValue(typography.get('header_size', 14))
        self.button_font_size_spin.setValue(typography.get('button_font_size', 10))
        
        # Load components
        components = theme_data.get('components', {})
        self.border_radius_spin.setValue(components.get('border_radius', 4))
        self.padding_spin.setValue(components.get('padding', 8))
        self.spacing_spin.setValue(components.get('spacing', 10))
    
    def select_color(self, property_name):
        """Open color dialog for property"""
        color_edit = self.color_edits[property_name]
        current_color = QColor(color_edit.text())
        
        color = QColorDialog.getColor(current_color, self, f"Select {property_name.replace('_', ' ').title()} Color")
        if color.isValid():
            color_edit.setText(color.name())
    
    def save_theme(self):
        """Save theme data"""
        try:
            # Collect theme data
            theme_data = {
                'name': self.theme_name_edit.text(),
                'description': self.theme_description_edit.toPlainText(),
                'colors': {prop: edit.text() for prop, edit in self.color_edits.items()},
                'typography': {
                    'font_family': self.font_family_edit.text(),
                    'font_size': self.font_size_spin.value(),
                    'header_size': self.header_size_spin.value(),
                    'button_font_size': self.button_font_size_spin.value()
                },
                'components': {
                    'border_radius': self.border_radius_spin.value(),
                    'padding': self.padding_spin.value(),
                    'spacing': self.spacing_spin.value()
                }
            }
            
            # Save theme
            theme_id = self.theme_id_edit.text()
            if theme_creator.save_theme(theme_id, theme_data):
                QMessageBox.information(self, "Success", "Theme saved successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save theme")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save theme: {str(e)}")


class ThemeEditorPanel(BasePanel):
    """Theme editor panel for creating and managing themes"""
    
    theme_changed = Signal(str)  # Signal emitted when theme changes
    
    def __init__(self, master=None, app=None):
        super().__init__(master, app)
        self.current_theme_id = None
        self.theme_preview_data = {}
        self.setup_ui()
        # Ensure default themes exist
        theme_creator.create_default_themes()
        self.load_themes()
    
    def setup_ui(self):
        """Set up the theme editor UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Theme Editor")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Main content with tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Theme Management Tab
        self.setup_theme_management_tab()
        
        # Preview Tab
        self.setup_preview_tab()
    
    def setup_theme_management_tab(self):
        """Set up theme management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme list
        theme_group = QGroupBox("Available Themes")
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme selection
        selection_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.currentTextChanged.connect(self.on_theme_selected)
        selection_layout.addWidget(QLabel("Select Theme:"))
        selection_layout.addWidget(self.theme_combo)
        selection_layout.addStretch()
        
        self.apply_btn = QPushButton("Apply Theme")
        self.apply_btn.clicked.connect(self.apply_selected_theme)
        self.edit_btn = QPushButton("Edit Theme")
        self.edit_btn.clicked.connect(self.edit_selected_theme)
        self.delete_btn = QPushButton("Delete Theme")
        self.delete_btn.clicked.connect(self.delete_selected_theme)
        
        selection_layout.addWidget(self.apply_btn)
        selection_layout.addWidget(self.edit_btn)
        selection_layout.addWidget(self.delete_btn)
        theme_layout.addLayout(selection_layout)
        
        # Theme details
        self.theme_details = QTextEdit()
        self.theme_details.setMaximumHeight(150)
        self.theme_details.setReadOnly(True)
        theme_layout.addWidget(self.theme_details)
        
        # Theme actions
        actions_layout = QHBoxLayout()
        self.create_btn = QPushButton("Create New Theme")
        self.create_btn.clicked.connect(self.create_new_theme)
        self.import_btn = QPushButton("Import Theme")
        self.import_btn.clicked.connect(self.import_theme)
        self.export_btn = QPushButton("Export Theme")
        self.export_btn.clicked.connect(self.export_theme)
        
        actions_layout.addWidget(self.create_btn)
        actions_layout.addWidget(self.import_btn)
        actions_layout.addWidget(self.export_btn)
        actions_layout.addStretch()
        theme_layout.addLayout(actions_layout)
        
        layout.addWidget(theme_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Manage Themes")
    
    
    def setup_preview_tab(self):
        """Set up theme preview tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        preview_group = QGroupBox("Theme Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Preview controls
        preview_controls_layout = QHBoxLayout()
        self.preview_theme_combo = QComboBox()
        preview_controls_layout.addWidget(QLabel("Preview Theme:"))
        preview_controls_layout.addWidget(self.preview_theme_combo)
        
        self.apply_preview_btn = QPushButton("Apply Preview")
        self.apply_preview_btn.clicked.connect(self.apply_preview_theme)
        preview_controls_layout.addWidget(self.apply_preview_btn)
        preview_controls_layout.addStretch()
        
        preview_layout.addLayout(preview_controls_layout)
        
        # Preview widget
        self.preview_widget = QWidget()
        self.preview_widget.setMinimumHeight(300)
        self.setup_preview_widget()
        preview_layout.addWidget(self.preview_widget)
        
        layout.addWidget(preview_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Preview")
    
    def setup_preview_widget(self):
        """Set up preview widget with sample components"""
        layout = QVBoxLayout(self.preview_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Sample components
        sample_label = QLabel("Sample Components")
        sample_font = QFont()
        sample_font.setPointSize(14)
        sample_font.setBold(True)
        sample_label.setFont(sample_font)
        layout.addWidget(sample_label)
        
        # Sample buttons
        button_layout = QHBoxLayout()
        sample_btn1 = QPushButton("Primary Button")
        sample_btn2 = QPushButton("Secondary Button")
        sample_btn3 = QPushButton("Disabled Button")
        sample_btn3.setEnabled(False)
        
        button_layout.addWidget(sample_btn1)
        button_layout.addWidget(sample_btn2)
        button_layout.addWidget(sample_btn3)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Sample form
        form_group = QGroupBox("Sample Form")
        form_layout = QGridLayout(form_group)
        
        form_layout.addWidget(QLabel("Name:"), 0, 0)
        form_layout.addWidget(QLineEdit("Sample text"), 0, 1)
        form_layout.addWidget(QLabel("Category:"), 1, 0)
        form_layout.addWidget(QComboBox(), 1, 1)
        form_layout.addWidget(QLabel("Notes:"), 2, 0)
        form_layout.addWidget(QTextEdit("Sample text area"), 2, 1)
        
        layout.addWidget(form_group)
        
        # Sample table
        table_label = QLabel("Sample Table")
        layout.addWidget(table_label)
        
        sample_table = QTableWidget(3, 3)
        sample_table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
        sample_table.setItem(0, 0, QTableWidgetItem("Sample Data 1"))
        sample_table.setItem(0, 1, QTableWidgetItem("Sample Data 2"))
        sample_table.setItem(0, 2, QTableWidgetItem("Sample Data 3"))
        sample_table.setMaximumHeight(100)
        layout.addWidget(sample_table)
        
        layout.addStretch()
    
    def load_themes(self):
        """Load available themes"""
        print("DEBUG: ThemeEditorPanel.load_themes() called")
        themes = theme_creator.list_themes()
        print(f"DEBUG: Found {len(themes)} themes from theme_creator")
        
        self.theme_combo.clear()
        self.preview_theme_combo.clear()
        
        for theme in themes:
            print(f"DEBUG: Adding theme: {theme['name']} ({theme['id']})")
            self.theme_combo.addItem(theme['name'], theme['id'])
            self.preview_theme_combo.addItem(theme['name'], theme['id'])
        
        print(f"DEBUG: Combo box now has {self.theme_combo.count()} items")
        
        # Set default selection to first theme if available
        if themes:
            self.theme_combo.setCurrentIndex(0)
            self.preview_theme_combo.setCurrentIndex(0)
            # Trigger theme selection to populate details
            self.on_theme_selected(self.theme_combo.currentText())
            print(f"ThemeEditorPanel: Loaded {len(themes)} themes, selected: {self.theme_combo.currentText()}")
        else:
            print("ThemeEditorPanel: No themes found to load")
    
    def on_theme_selected(self, theme_name):
        """Handle theme selection"""
        if not theme_name:
            return
        
        theme_id = self.theme_combo.currentData()
        theme_data = theme_creator.load_theme(theme_id)
        
        if theme_data:
            details = f"Name: {theme_data.get('name', 'Unknown')}\n"
            details += f"Description: {theme_data.get('description', 'No description')}\n"
            details += f"Primary Color: {theme_data.get('colors', {}).get('primary', 'Unknown')}\n"
            details += f"Background: {theme_data.get('colors', {}).get('background', 'Unknown')}"
            
            self.theme_details.setPlainText(details)
            self.current_theme_id = theme_id
    
    def apply_selected_theme(self):
        """Apply selected theme to application"""
        if not self.current_theme_id:
            QMessageBox.warning(self, "No Selection", "Please select a theme to apply.")
            return
        
        app = self.app or QApplication.instance()
        if theme_creator.apply_theme(self.current_theme_id, app):
            QMessageBox.information(self, "Success", f"Theme '{self.current_theme_id}' applied successfully!")
            self.theme_changed.emit(self.current_theme_id)
        else:
            QMessageBox.critical(self, "Error", f"Failed to apply theme '{self.current_theme_id}'")
    
    def edit_selected_theme(self):
        """Edit selected theme"""
        if not self.current_theme_id:
            QMessageBox.warning(self, "No Selection", "Please select a theme to edit.")
            return
        
        # Create theme editing dialog
        dialog = ThemeEditDialog(self, self.current_theme_id)
        if dialog.exec() == QDialog.Accepted:
            # Theme was saved, reload themes
            self.load_themes()
    
    def delete_selected_theme(self):
        """Delete selected theme"""
        if not self.current_theme_id:
            QMessageBox.warning(self, "No Selection", "Please select a theme to delete.")
            return
        
        reply = QMessageBox.question(self, "Delete Theme", 
                                   f"Are you sure you want to delete theme '{self.current_theme_id}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if theme_creator.delete_theme(self.current_theme_id):
                QMessageBox.information(self, "Success", "Theme deleted successfully!")
                self.load_themes()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete theme")
    
    def create_new_theme(self):
        """Create new theme"""
        # Create theme editing dialog for new theme
        dialog = ThemeEditDialog(self, None)
        if dialog.exec() == QDialog.Accepted:
            # Theme was saved, reload themes
            self.load_themes()
    
    def import_theme(self):
        """Import theme from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Theme", "", "JSON Files (*.json);;All Files (*)")
        
        if file_path:
            theme_id = theme_creator.import_theme(file_path)
            if theme_id:
                QMessageBox.information(self, "Success", f"Theme imported successfully as '{theme_id}'")
                self.load_themes()
            else:
                QMessageBox.critical(self, "Error", "Failed to import theme")
    
    def export_theme(self):
        """Export selected theme to file"""
        if not self.current_theme_id:
            QMessageBox.warning(self, "No Selection", "Please select a theme to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Theme", f"{self.current_theme_id}.json", "JSON Files (*.json);;All Files (*)")
        
        if file_path:
            if theme_creator.export_theme(self.current_theme_id, file_path):
                QMessageBox.information(self, "Success", "Theme exported successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to export theme")
    
    def load_theme_for_editing(self, theme_id):
        """Load theme data for editing"""
        theme_data = theme_creator.load_theme(theme_id)
        if not theme_data:
            return
        
        pass  # Method removed - editing now handled by dialog
    
    def select_color(self, property_name):
        """Select color for property - method removed, editing now handled by dialog"""
        pass
    
    def save_theme(self):
        """Save current theme - method removed, editing now handled by dialog"""
        pass
    
    def preview_theme(self):
        """Preview current theme"""
        pass  # Method removed - editing now handled by dialog
    
    def apply_preview_theme(self):
        """Apply preview theme to application"""
        theme_id = self.preview_theme_combo.currentData()
        if theme_id and self.app:
            try:
                result = theme_creator.apply_theme(theme_id, self.app)
                if result:
                    self.theme_changed.emit(theme_id)
                else:
                    QMessageBox.warning(self, "Theme Error", "Failed to apply theme.")
            except Exception as e:
                QMessageBox.critical(self, "Theme Error", f"Failed to apply theme: {str(e)}")
    
    def reset_theme(self):
        """Reset theme to default values - method removed, editing now handled by dialog"""
        pass
    
    def apply_theme_to_widget(self, widget, theme_data):
        """Apply theme data to a widget"""
        colors = theme_data.get('colors', {})
        typography = theme_data.get('typography', {})
        components = theme_data.get('components', {})
        
        # Generate stylesheet
        stylesheet = theme_creator._generate_stylesheet(colors, typography, components)
        widget.setStyleSheet(stylesheet)
    
    def refresh(self):
        """Refresh panel data"""
        self.load_themes()
