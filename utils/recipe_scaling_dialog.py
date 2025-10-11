#!/usr/bin/env python3
"""
Recipe Scaling Dialog

Provides a user-friendly interface for scaling recipes with conversion options.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QGridLayout, QMessageBox, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from services.recipe_scaling_service import recipe_scaling_service


class RecipeScalingDialog(QDialog):
    """Dialog for scaling recipes with conversion options"""
    
    recipe_scaled = Signal(list)  # Emitted when recipe is scaled
    
    def __init__(self, ingredients, parent=None):
        super().__init__(parent)
        self.original_ingredients = ingredients
        self.scaled_ingredients = ingredients.copy()
        self.setup_ui()
        self.setup_connections()
        self.load_ingredients()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Scale Recipe")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Recipe Scaling")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Scale factor selection
        scale_group = QGroupBox("Scale Factor")
        scale_layout = QHBoxLayout(scale_group)
        
        scale_layout.addWidget(QLabel("Scale to:"))
        
        self.scale_combo = QComboBox()
        self.scale_combo.setMinimumWidth(200)
        for factor, description in recipe_scaling_service.get_common_scales():
            self.scale_combo.addItem(description, factor)
        self.scale_combo.setCurrentText("1x (Original)")
        scale_layout.addWidget(self.scale_combo)
        
        scale_layout.addWidget(QLabel("or custom:"))
        
        self.custom_scale_spin = QDoubleSpinBox()
        self.custom_scale_spin.setRange(0.1, 10.0)
        self.custom_scale_spin.setSingleStep(0.1)
        self.custom_scale_spin.setValue(1.0)
        self.custom_scale_spin.setDecimals(2)
        scale_layout.addWidget(self.custom_scale_spin)
        
        scale_layout.addStretch()
        layout.addWidget(scale_group)
        
        # Conversion options
        conversion_group = QGroupBox("Unit Conversion")
        conversion_layout = QGridLayout(conversion_group)
        
        conversion_layout.addWidget(QLabel("Convert to:"), 0, 0)
        self.conversion_combo = QComboBox()
        self.conversion_combo.addItems([
            "Keep original units",
            "Metric (ml, g)",
            "Imperial (cups, oz)",
            "Mixed (best fit)"
        ])
        conversion_layout.addWidget(self.conversion_combo, 0, 1)
        
        layout.addWidget(conversion_group)
        
        # Ingredients table
        ingredients_group = QGroupBox("Ingredients")
        ingredients_layout = QVBoxLayout(ingredients_group)
        
        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(4)
        self.ingredients_table.setHorizontalHeaderLabels([
            "Ingredient", "Original Amount", "Scaled Amount", "Unit"
        ])
        
        # Set table properties
        header = self.ingredients_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.ingredients_table.setAlternatingRowColors(True)
        self.ingredients_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        ingredients_layout.addWidget(self.ingredients_table)
        layout.addWidget(ingredients_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("Preview Changes")
        self.apply_button = QPushButton("Apply Scaling")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(self.preview_button)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.scale_combo.currentIndexChanged.connect(self.on_scale_changed)
        self.custom_scale_spin.valueChanged.connect(self.on_custom_scale_changed)
        self.conversion_combo.currentIndexChanged.connect(self.on_conversion_changed)
        self.preview_button.clicked.connect(self.preview_scaling)
        self.apply_button.clicked.connect(self.apply_scaling)
        self.cancel_button.clicked.connect(self.reject)
    
    def load_ingredients(self):
        """Load ingredients into the table"""
        self.ingredients_table.setRowCount(len(self.original_ingredients))
        
        for row, ingredient in enumerate(self.original_ingredients):
            # Ingredient name
            name_item = QTableWidgetItem(ingredient.get('name', ''))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.ingredients_table.setItem(row, 0, name_item)
            
            # Original amount
            original_amount = ingredient.get('amount', '')
            original_item = QTableWidgetItem(original_amount)
            original_item.setFlags(original_item.flags() & ~Qt.ItemIsEditable)
            self.ingredients_table.setItem(row, 1, original_item)
            
            # Scaled amount (initially same as original)
            scaled_item = QTableWidgetItem(original_amount)
            scaled_item.setFlags(scaled_item.flags() & ~Qt.ItemIsEditable)
            self.ingredients_table.setItem(row, 2, scaled_item)
            
            # Unit
            unit = ingredient.get('unit', '')
            unit_item = QTableWidgetItem(unit)
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)
            self.ingredients_table.setItem(row, 3, unit_item)
    
    def get_scale_factor(self):
        """Get the current scale factor"""
        if self.scale_combo.currentText().startswith("custom"):
            return self.custom_scale_spin.value()
        return self.scale_combo.currentData()
    
    def get_conversion_mode(self):
        """Get the current conversion mode"""
        return self.conversion_combo.currentText()
    
    def on_scale_changed(self):
        """Handle scale factor change"""
        self.preview_scaling()
    
    def on_custom_scale_changed(self):
        """Handle custom scale factor change"""
        self.scale_combo.setCurrentText("Custom")
        self.preview_scaling()
    
    def on_conversion_changed(self):
        """Handle conversion mode change"""
        self.preview_scaling()
    
    def preview_scaling(self):
        """Preview the scaling changes"""
        scale_factor = self.get_scale_factor()
        conversion_mode = self.get_conversion_mode()
        
        # Determine target units based on conversion mode
        target_units = None
        if conversion_mode == "Metric (ml, g)":
            target_units = {
                "liquid": "ml",
                "flour": "g",
                "sugar": "g",
                "butter": "g",
                "oil": "ml"
            }
        elif conversion_mode == "Imperial (cups, oz)":
            target_units = {
                "liquid": "cup",
                "flour": "cup",
                "sugar": "cup",
                "butter": "oz",
                "oil": "cup"
            }
        
        # Scale ingredients
        self.scaled_ingredients = recipe_scaling_service.scale_recipe(
            self.original_ingredients, scale_factor, target_units
        )
        
        # Update table
        for row, ingredient in enumerate(self.scaled_ingredients):
            scaled_amount = ingredient.get('amount', '')
            unit = ingredient.get('unit', '')
            
            self.ingredients_table.setItem(row, 2, QTableWidgetItem(scaled_amount))
            self.ingredients_table.setItem(row, 3, QTableWidgetItem(unit))
    
    def apply_scaling(self):
        """Apply the scaling and close dialog"""
        self.recipe_scaled.emit(self.scaled_ingredients)
        self.accept()
    
    def get_scaled_ingredients(self):
        """Get the scaled ingredients"""
        return self.scaled_ingredients
