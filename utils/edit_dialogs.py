# path: utils/edit_dialogs.py
"""
Edit Dialog Utilities for PySide6 Application

Provides reusable edit dialogs for different data types.
"""

from typing import Dict, Any, Optional, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QSpinBox, QDateEdit, QPushButton, QFormLayout,
    QGroupBox, QMessageBox, QCheckBox, QTableWidget, QTableWidgetItem, QSplitter, QWidget
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QPixmap


class BaseEditDialog(QDialog):
    """Base class for edit dialogs"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.data = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI - to be overridden by subclasses"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(self.windowTitle())
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Content will be added by subclasses
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def set_data(self, data: Dict[str, Any]):
        """Set the data to be edited"""
        self.data = data.copy()
        self.populate_fields()
    
    def get_data(self) -> Dict[str, Any]:
        """Get the edited data"""
        return self.data.copy()
    
    def populate_fields(self):
        """Populate fields with data - to be overridden by subclasses"""
        pass


class PantryItemEditDialog(BaseEditDialog):
    """Dialog for editing pantry items"""
    
    def __init__(self, parent=None):
        super().__init__("Edit Pantry Item", parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Form layout
        form_group = QGroupBox("Item Details")
        form_layout = QFormLayout(form_group)
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter item name...")
        form_layout.addRow("Name:", self.name_edit)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Grains & Flours", "Proteins", "Dairy & Eggs", "Vegetables", 
            "Fruits", "Pantry Staples", "Spices & Herbs", "Beverages", "Other"
        ])
        form_layout.addRow("Category:", self.category_combo)
        
        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(9999)
        form_layout.addRow("Quantity:", self.quantity_spin)
        
        # Unit
        self.unit_combo = QComboBox()
        self.unit_combo.addItems([
            "pieces", "lbs", "oz", "kg", "g", "cups", "tbsp", "tsp", 
            "ml", "l", "cans", "boxes", "bags"
        ])
        form_layout.addRow("Unit:", self.unit_combo)
        
        # Expiration Date
        self.exp_date = QDateEdit()
        self.exp_date.setDate(QDate.currentDate().addDays(30))
        self.exp_date.setCalendarPopup(True)
        form_layout.addRow("Expiration:", self.exp_date)
        
        # Gluten-Free Status
        self.gf_combo = QComboBox()
        self.gf_combo.addItems(["Yes", "No", "Unknown"])
        form_layout.addRow("Gluten-Free:", self.gf_combo)
        
        # UPC Code
        self.upc_edit = QLineEdit()
        self.upc_edit.setPlaceholderText("Enter UPC code...")
        form_layout.addRow("UPC Code:", self.upc_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Additional notes...")
        form_layout.addRow("Notes:", self.notes_edit)
        
        self.content_layout.addWidget(form_group)
    
    def populate_fields(self):
        """Populate fields with existing data"""
        self.name_edit.setText(self.data.get('name', ''))
        
        category = self.data.get('category', 'Other')
        index = self.category_combo.findText(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        self.quantity_spin.setValue(self.data.get('quantity', 1))
        
        unit = self.data.get('unit', 'pieces')
        index = self.unit_combo.findText(unit)
        if index >= 0:
            self.unit_combo.setCurrentIndex(index)
        
        exp_date = self.data.get('expiration_date')
        if exp_date:
            self.exp_date.setDate(QDate.fromString(exp_date, "yyyy-MM-dd"))
        
        gf_status = self.data.get('gluten_free', 'Unknown')
        index = self.gf_combo.findText(gf_status)
        if index >= 0:
            self.gf_combo.setCurrentIndex(index)
        
        self.upc_edit.setText(self.data.get('upc_code', ''))
        self.notes_edit.setPlainText(self.data.get('notes', ''))
    
    def get_data(self) -> Dict[str, Any]:
        """Get the edited data"""
        return {
            'name': self.name_edit.text().strip(),
            'category': self.category_combo.currentText(),
            'quantity': self.quantity_spin.value(),
            'unit': self.unit_combo.currentText(),
            'expiration_date': self.exp_date.date().toString("yyyy-MM-dd"),
            'gluten_free': self.gf_combo.currentText(),
            'upc_code': self.upc_edit.text().strip(),
            'notes': self.notes_edit.toPlainText().strip()
        }


class HealthEntryEditDialog(BaseEditDialog):
    """Dialog for editing health log entries"""
    
    def __init__(self, parent=None):
        super().__init__("Edit Health Entry", parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Form layout
        form_group = QGroupBox("Health Entry Details")
        form_layout = QFormLayout(form_group)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)
        
        # Symptoms
        self.symptoms_edit = QTextEdit()
        self.symptoms_edit.setMaximumHeight(80)
        self.symptoms_edit.setPlaceholderText("Describe any symptoms...")
        form_layout.addRow("Symptoms:", self.symptoms_edit)
        
        # Bristol Stool Scale
        self.bristol_combo = QComboBox()
        self.bristol_combo.addItems([
            "Type 1", "Type 2", "Type 3", "Type 4", "Type 5", "Type 6", "Type 7", "Not recorded"
        ])
        form_layout.addRow("Bristol Scale:", self.bristol_combo)
        
        # Hydration
        self.hydration_spin = QSpinBox()
        self.hydration_spin.setSuffix(" liters")
        self.hydration_spin.setMinimum(0)
        self.hydration_spin.setMaximum(10)
        self.hydration_spin.setValue(2)
        form_layout.addRow("Hydration:", self.hydration_spin)
        
        # Fiber
        self.fiber_spin = QSpinBox()
        self.fiber_spin.setSuffix(" grams")
        self.fiber_spin.setMinimum(0)
        self.fiber_spin.setMaximum(100)
        form_layout.addRow("Fiber:", self.fiber_spin)
        
        # Mood
        self.mood_combo = QComboBox()
        self.mood_combo.addItems([
            "Excellent", "Good", "Fair", "Poor", "Very Poor"
        ])
        form_layout.addRow("Mood:", self.mood_combo)
        
        # Energy Level
        self.energy_spin = QSpinBox()
        self.energy_spin.setMinimum(1)
        self.energy_spin.setMaximum(10)
        self.energy_spin.setValue(5)
        form_layout.addRow("Energy Level (1-10):", self.energy_spin)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Additional notes...")
        form_layout.addRow("Notes:", self.notes_edit)
        
        self.content_layout.addWidget(form_group)
    
    def populate_fields(self):
        """Populate fields with existing data"""
        date = self.data.get('date')
        if date:
            self.date_edit.setDate(QDate.fromString(date, "yyyy-MM-dd"))
        
        self.symptoms_edit.setPlainText(self.data.get('symptoms', ''))
        
        bristol = self.data.get('bristol_scale', 'Not recorded')
        index = self.bristol_combo.findText(bristol)
        if index >= 0:
            self.bristol_combo.setCurrentIndex(index)
        
        self.hydration_spin.setValue(self.data.get('hydration_liters', 2))
        self.fiber_spin.setValue(self.data.get('fiber_grams', 0))
        
        mood = self.data.get('mood', 'Good')
        index = self.mood_combo.findText(mood)
        if index >= 0:
            self.mood_combo.setCurrentIndex(index)
        
        self.energy_spin.setValue(self.data.get('energy_level', 5))
        self.notes_edit.setPlainText(self.data.get('notes', ''))
    
    def get_data(self) -> Dict[str, Any]:
        """Get the edited data"""
        return {
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'symptoms': self.symptoms_edit.toPlainText().strip(),
            'bristol_scale': self.bristol_combo.currentText(),
            'hydration_liters': self.hydration_spin.value(),
            'fiber_grams': self.fiber_spin.value(),
            'mood': self.mood_combo.currentText(),
            'energy_level': self.energy_spin.value(),
            'notes': self.notes_edit.toPlainText().strip()
        }


class RecipeEditDialog(BaseEditDialog):
    """Dialog for editing recipes"""
    
    def __init__(self, parent=None):
        super().__init__("Edit Recipe", parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Create main splitter for left-right layout
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Recipe Details
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Form layout
        form_group = QGroupBox("Recipe Details")
        form_layout = QFormLayout(form_group)
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter recipe name...")
        form_layout.addRow("Name:", self.name_edit)
        
        # Category
        self.category_combo = QComboBox()
        self.load_categories()
        form_layout.addRow("Category:", self.category_combo)
        
        # Prep Time
        self.prep_time_edit = QLineEdit()
        self.prep_time_edit.setPlaceholderText("e.g., 15 min")
        form_layout.addRow("Prep Time:", self.prep_time_edit)
        
        # Cook Time
        self.cook_time_edit = QLineEdit()
        self.cook_time_edit.setPlaceholderText("e.g., 30 min")
        form_layout.addRow("Cook Time:", self.cook_time_edit)
        
        # Servings
        self.servings_spin = QSpinBox()
        self.servings_spin.setMinimum(1)
        self.servings_spin.setMaximum(50)
        self.servings_spin.setValue(4)
        form_layout.addRow("Servings:", self.servings_spin)
        
        # Difficulty
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        form_layout.addRow("Difficulty:", self.difficulty_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Recipe description...")
        form_layout.addRow("Description:", self.description_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Additional notes...")
        form_layout.addRow("Notes:", self.notes_edit)
        
        left_layout.addWidget(form_group)
        
        # Recipe Image
        image_group = QGroupBox("Recipe Image")
        image_layout = QVBoxLayout(image_group)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 150)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f9f9f9;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("No Image\nClick 'Select Image' to add")
        self.image_label.setWordWrap(True)
        image_layout.addWidget(self.image_label)
        
        # Image buttons
        image_btn_layout = QHBoxLayout()
        self.select_image_btn = QPushButton("Select Image")
        self.select_image_btn.clicked.connect(self.select_recipe_image)
        self.remove_image_btn = QPushButton("Remove Image")
        self.remove_image_btn.clicked.connect(self.remove_recipe_image)
        self.remove_image_btn.setEnabled(False)
        
        image_btn_layout.addWidget(self.select_image_btn)
        image_btn_layout.addWidget(self.remove_image_btn)
        image_btn_layout.addStretch()
        image_layout.addLayout(image_btn_layout)
        
        left_layout.addWidget(image_group)
        left_layout.addStretch()
        
        # Right side - Ingredients and Instructions
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Ingredients
        ingredients_group = QGroupBox("Ingredients")
        ingredients_layout = QVBoxLayout(ingredients_group)
        
        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(2)
        self.ingredients_table.setHorizontalHeaderLabels(["Ingredient", "Amount"])
        self.ingredients_table.horizontalHeader().setStretchLastSection(True)
        self.ingredients_table.setMinimumHeight(200)
        self.ingredients_table.setMaximumHeight(300)
        
        # Apply custom stylesheet to fix selection styling issues
        self.ingredients_table.setStyleSheet("""
            QTableWidget {
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
                gridline-color: #e0e0e0;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                background: transparent;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                border: none;
                outline: none;
            }
            QTableWidget::item:selected:focus {
                background-color: #e3f2fd;
                color: #1976d2;
                border: none;
                outline: none;
            }
            QTableWidget::item:hover {
                background-color: #f0f8f0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                padding: 8px;
                font-weight: bold;
            }
        """)
        
        ingredients_layout.addWidget(self.ingredients_table)
        
        ingredients_btn_layout = QHBoxLayout()
        add_ingredient_btn = QPushButton("Add Ingredient")
        add_ingredient_btn.clicked.connect(self.add_ingredient)
        remove_ingredient_btn = QPushButton("Remove Ingredient")
        remove_ingredient_btn.clicked.connect(self.remove_ingredient)
        
        ingredients_btn_layout.addWidget(add_ingredient_btn)
        ingredients_btn_layout.addWidget(remove_ingredient_btn)
        ingredients_btn_layout.addStretch()
        ingredients_layout.addLayout(ingredients_btn_layout)
        
        # Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        self.instructions_edit = QTextEdit()
        self.instructions_edit.setMinimumHeight(200)
        self.instructions_edit.setMaximumHeight(300)
        self.instructions_edit.setPlaceholderText("Enter cooking instructions...")
        instructions_layout.addWidget(self.instructions_edit)
        
        right_layout.addWidget(ingredients_group)
        right_layout.addWidget(instructions_group)
        
        # Add widgets to splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([400, 500])  # Set initial sizes
        
        self.content_layout.addWidget(main_splitter)
    
    def add_ingredient(self):
        """Add a new ingredient row"""
        row = self.ingredients_table.rowCount()
        self.ingredients_table.insertRow(row)
        self.ingredients_table.setItem(row, 0, QTableWidgetItem(""))
        self.ingredients_table.setItem(row, 1, QTableWidgetItem(""))
    
    def remove_ingredient(self):
        """Remove selected ingredient row"""
        current_row = self.ingredients_table.currentRow()
        if current_row >= 0:
            self.ingredients_table.removeRow(current_row)
    
    def populate_fields(self):
        """Populate fields with existing data"""
        self.name_edit.setText(self.data.get('name', ''))
        
        category = self.data.get('category', 'Other')
        index = self.category_combo.findText(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        self.prep_time_edit.setText(self.data.get('prep_time', ''))
        self.cook_time_edit.setText(self.data.get('cook_time', ''))
        self.servings_spin.setValue(self.data.get('servings', 4))
        
        difficulty = self.data.get('difficulty', 'Medium')
        index = self.difficulty_combo.findText(difficulty)
        if index >= 0:
            self.difficulty_combo.setCurrentIndex(index)
        
        self.description_edit.setPlainText(self.data.get('description', ''))
        self.notes_edit.setPlainText(self.data.get('notes', ''))
        self.instructions_edit.setPlainText(self.data.get('instructions', ''))
        
        # Populate ingredients
        ingredients = self.data.get('ingredients', [])
        self.ingredients_table.setRowCount(len(ingredients))
        for i, ingredient in enumerate(ingredients):
            if isinstance(ingredient, dict):
                self.ingredients_table.setItem(i, 0, QTableWidgetItem(ingredient.get('name', '')))
                self.ingredients_table.setItem(i, 1, QTableWidgetItem(ingredient.get('amount', '')))
            else:
                self.ingredients_table.setItem(i, 0, QTableWidgetItem(str(ingredient)))
    
    def get_data(self) -> Dict[str, Any]:
        """Get the edited data"""
        ingredients = []
        for row in range(self.ingredients_table.rowCount()):
            name_item = self.ingredients_table.item(row, 0)
            amount_item = self.ingredients_table.item(row, 1)
            if name_item and name_item.text().strip():
                ingredients.append({
                    'name': name_item.text().strip(),
                    'amount': amount_item.text().strip() if amount_item else ''
                })
        
        return {
            'name': self.name_edit.text().strip(),
            'category': self.category_combo.currentText(),
            'category_id': self.category_combo.currentData(),
            'prep_time': self.prep_time_edit.text().strip(),
            'cook_time': self.cook_time_edit.text().strip(),
            'servings': self.servings_spin.value(),
            'difficulty': self.difficulty_combo.currentText(),
            'description': self.description_edit.toPlainText().strip(),
            'ingredients': ingredients,
            'instructions': self.instructions_edit.toPlainText().strip(),
            'notes': self.notes_edit.toPlainText().strip(),
            'image_path': getattr(self, 'current_image_path', '')
        }
    
    def load_categories(self):
        """Load categories from database and populate dropdown"""
        try:
            from utils.db import get_connection
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Get all categories ordered by parent_id, then sort_order
            cursor.execute("""
                SELECT id, name, parent_id, icon, color 
                FROM categories 
                ORDER BY 
                    CASE WHEN parent_id IS NULL THEN 0 ELSE 1 END,
                    parent_id,
                    sort_order,
                    name
            """)
            categories = cursor.fetchall()
            conn.close()
            
            # Clear existing items
            self.category_combo.clear()
            
            # Add categories with proper indentation for subcategories
            for cat_id, name, parent_id, icon, color in categories:
                if parent_id is None:
                    # Primary category
                    display_text = f"{icon} {name}"
                    self.category_combo.addItem(display_text, cat_id)
                else:
                    # Subcategory - find parent name for indentation
                    parent_name = self._get_category_name(parent_id)
                    display_text = f"  └ {icon} {name}"
                    self.category_combo.addItem(display_text, cat_id)
            
        except Exception as e:
            print(f"Error loading categories: {e}")
            # Fallback to basic categories
            self.category_combo.addItems([
                "Breakfast", "Lunch", "Dinner", "Dessert", "Snack", "Beverage", "Other"
            ])
    
    def _get_category_name(self, category_id):
        """Get category name by ID"""
        try:
            from utils.db import get_connection
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "Unknown"
        except Exception:
            return "Unknown"
    
    def select_recipe_image(self):
        """Select and display recipe image"""
        try:
            from services.image_service import recipe_image_service
            
            # Select image file
            image_path = recipe_image_service.select_image(self)
            if image_path:
                # Display the selected image
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Scale image to fit label while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        self.image_label.size(), 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    self.image_label.setText("")
                    
                    # Store the image path for later processing
                    self.current_image_path = image_path
                    self.remove_image_btn.setEnabled(True)
                else:
                    QMessageBox.warning(self, "Invalid Image", "The selected file is not a valid image.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to select image: {str(e)}")
    
    def remove_recipe_image(self):
        """Remove the selected recipe image"""
        try:
            # Clear the image display
            self.image_label.clear()
            self.image_label.setText("No Image\nClick 'Select Image' to add")
            
            # Clear the stored image path
            self.current_image_path = ""
            self.remove_image_btn.setEnabled(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove image: {str(e)}")
    
    def load_recipe_image(self, recipe_id):
        """Load and display existing recipe image"""
        try:
            from services.image_service import recipe_image_service
            
            if recipe_id:
                # Try to load existing image
                pixmap = recipe_image_service.load_image_pixmap(recipe_id, (200, 150))
                if pixmap and not pixmap.isNull():
                    self.image_label.setPixmap(pixmap)
                    self.image_label.setText("")
                    self.remove_image_btn.setEnabled(True)
                    # Store the recipe ID for image processing
                    self.current_recipe_id = recipe_id
                else:
                    # No existing image
                    self.image_label.clear()
                    self.image_label.setText("No Image\nClick 'Select Image' to add")
                    self.remove_image_btn.setEnabled(False)
            
        except Exception as e:
            print(f"Error loading recipe image: {e}")
            self.image_label.clear()
            self.image_label.setText("No Image\nClick 'Select Image' to add")
            self.remove_image_btn.setEnabled(False)


class ShoppingItemEditDialog(BaseEditDialog):
    """Dialog for editing shopping list items"""
    
    def __init__(self, parent=None):
        super().__init__("Edit Shopping Item", parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Form layout
        form_group = QGroupBox("Item Details")
        form_layout = QFormLayout(form_group)
        
        # Store
        self.store_combo = QComboBox()
        self.store_combo.addItems([
            "Grocery Store",
            "Health Food Store", 
            "Farmers Market",
            "Bulk Store",
            "Online Order",
            "Specialty Store",
            "Other"
        ])
        form_layout.addRow("Store:", self.store_combo)
        
        # Item name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter item name...")
        form_layout.addRow("Item:", self.name_edit)
        
        # Quantity
        self.quantity_edit = QLineEdit()
        self.quantity_edit.setPlaceholderText("e.g., 2 lbs, 1 bunch")
        form_layout.addRow("Quantity:", self.quantity_edit)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Produce", "Meat & Seafood", "Dairy & Eggs", "Pantry", 
            "Frozen", "Bakery (GF)", "Beverages", "Health & Beauty", "Other"
        ])
        form_layout.addRow("Category:", self.category_combo)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        form_layout.addRow("Priority:", self.priority_combo)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Additional notes...")
        form_layout.addRow("Notes:", self.notes_edit)
        
        self.content_layout.addWidget(form_group)
    
    def populate_fields(self):
        """Populate fields with existing data"""
        store = self.data.get('store', 'Grocery Store')
        index = self.store_combo.findText(store)
        if index >= 0:
            self.store_combo.setCurrentIndex(index)
        
        self.name_edit.setText(self.data.get('item', ''))
        self.quantity_edit.setText(self.data.get('quantity', ''))
        
        category = self.data.get('category', 'Other')
        index = self.category_combo.findText(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        priority = self.data.get('priority', 'Medium')
        index = self.priority_combo.findText(priority)
        if index >= 0:
            self.priority_combo.setCurrentIndex(index)
        
        self.notes_edit.setPlainText(self.data.get('notes', ''))
    
    def get_data(self) -> Dict[str, Any]:
        """Get the edited data"""
        return {
            'store': self.store_combo.currentText(),
            'item': self.name_edit.text().strip(),
            'quantity': self.quantity_edit.text().strip(),
            'category': self.category_combo.currentText(),
            'priority': self.priority_combo.currentText(),
            'notes': self.notes_edit.toPlainText().strip()
        }


class MenuItemEditDialog(BaseEditDialog):
    """Dialog for editing menu items"""
    
    def __init__(self, parent=None):
        super().__init__("Edit Menu Item", parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Form layout
        form_group = QGroupBox("Meal Details")
        form_layout = QFormLayout(form_group)
        
        # Day
        self.day_combo = QComboBox()
        self.day_combo.addItems([
            "Monday", "Tuesday", "Wednesday", "Thursday", 
            "Friday", "Saturday", "Sunday"
        ])
        form_layout.addRow("Day:", self.day_combo)
        
        # Meal Type
        self.meal_type_combo = QComboBox()
        self.meal_type_combo.addItems([
            "Breakfast", "Lunch", "Dinner", "Snack"
        ])
        form_layout.addRow("Meal Type:", self.meal_type_combo)
        
        # Recipe
        self.recipe_edit = QLineEdit()
        self.recipe_edit.setPlaceholderText("Enter recipe name...")
        form_layout.addRow("Recipe:", self.recipe_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Additional notes...")
        form_layout.addRow("Notes:", self.notes_edit)
        
        self.content_layout.addWidget(form_group)
    
    def populate_fields(self):
        """Populate fields with existing data"""
        day = self.data.get('day', 'Monday')
        index = self.day_combo.findText(day)
        if index >= 0:
            self.day_combo.setCurrentIndex(index)
        
        meal_type = self.data.get('meal_type', 'Breakfast')
        index = self.meal_type_combo.findText(meal_type)
        if index >= 0:
            self.meal_type_combo.setCurrentIndex(index)
        
        self.recipe_edit.setText(self.data.get('recipe', ''))
        self.notes_edit.setPlainText(self.data.get('notes', ''))
    
    def get_data(self) -> Dict[str, Any]:
        """Get the edited data"""
        return {
            'day': self.day_combo.currentText(),
            'meal_type': self.meal_type_combo.currentText(),
            'recipe': self.recipe_edit.text().strip(),
            'notes': self.notes_edit.toPlainText().strip()
        }


class CalendarEventEditDialog(BaseEditDialog):
    """Dialog for editing calendar events"""
    
    def __init__(self, parent=None):
        super().__init__("Edit Calendar Event", parent)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Form layout
        form_group = QGroupBox("Event Details")
        form_layout = QFormLayout(form_group)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)
        
        # Event name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter event name...")
        form_layout.addRow("Event:", self.name_edit)
        
        # Event type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Health", "Social", "Work", "Education", "Personal", "Other"
        ])
        form_layout.addRow("Type:", self.type_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Event description...")
        form_layout.addRow("Description:", self.description_edit)
        
        self.content_layout.addWidget(form_group)
    
    def populate_fields(self):
        """Populate fields with existing data"""
        date = self.data.get('date')
        if date:
            self.date_edit.setDate(QDate.fromString(date, "yyyy-MM-dd"))
        
        self.name_edit.setText(self.data.get('event', ''))
        
        event_type = self.data.get('type', 'Personal')
        index = self.type_combo.findText(event_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        self.description_edit.setPlainText(self.data.get('description', ''))
    
    def get_data(self) -> Dict[str, Any]:
        """Get the edited data"""
        return {
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'event': self.name_edit.text().strip(),
            'type': self.type_combo.currentText(),
            'description': self.description_edit.toPlainText().strip()
        }
