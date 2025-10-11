# path: panels/cookbook/recipe_dialogs.py
"""
Dialog boxes for recipe operations
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QSpinBox, QPushButton, QMessageBox, QGroupBox,
    QFormLayout, QScrollArea, QWidget
)
from PySide6.QtCore import Qt


class RecipeDialogs:
    """Dialog boxes for recipe operations"""
    
    def __init__(self, cookbook_panel_instance=None):
        self.cookbook_panel = cookbook_panel_instance
    
    def show_add_recipe_dialog(self) -> Optional[Dict[str, Any]]:
        """Show dialog to add a new recipe"""
        dialog = QDialog()
        dialog.setWindowTitle("Add New Recipe")
        dialog.setModal(True)
        dialog.resize(600, 700)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_widget = self.create_recipe_form()
        layout.addWidget(form_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Recipe")
        save_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        if dialog.exec() == QDialog.Accepted:
            return self.extract_form_data(form_widget)
        
        return None
    
    def show_edit_recipe_dialog(self, recipe_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Show dialog to edit an existing recipe"""
        dialog = QDialog()
        dialog.setWindowTitle(f"Edit Recipe: {recipe_data.get('name', '')}")
        dialog.setModal(True)
        dialog.resize(600, 700)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_widget = self.create_recipe_form(recipe_data)
        layout.addWidget(form_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        if dialog.exec() == QDialog.Accepted:
            return self.extract_form_data(form_widget)
        
        return None
    
    def show_recipe_view_dialog(self, recipe_data: Dict[str, Any]):
        """Show dialog to view recipe details"""
        dialog = QDialog()
        dialog.setWindowTitle(f"Recipe: {recipe_data.get('name', '')}")
        dialog.setModal(True)
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Recipe display
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Recipe header
        header_layout = QVBoxLayout()
        
        name_label = QLabel(recipe_data.get('name', ''))
        name_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(name_label)
        
        if recipe_data.get('description'):
            desc_label = QLabel(recipe_data.get('description', ''))
            desc_label.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 10px;")
            desc_label.setWordWrap(True)
            header_layout.addWidget(desc_label)
        
        # Recipe details
        details_layout = QHBoxLayout()
        
        prep_time = recipe_data.get('prep_time', 0)
        cook_time = recipe_data.get('cook_time', 0)
        servings = recipe_data.get('servings', 1)
        difficulty = recipe_data.get('difficulty', 'Easy')
        
        details_text = f"⏱️ Prep: {prep_time} min | 🍳 Cook: {cook_time} min | 👥 Serves: {servings} | 📊 Difficulty: {difficulty}"
        details_label = QLabel(details_text)
        details_label.setStyleSheet("font-size: 12px; color: #95a5a6;")
        details_layout.addWidget(details_label)
        details_layout.addStretch()
        
        header_layout.addLayout(details_layout)
        scroll_layout.addLayout(header_layout)
        
        # Ingredients section
        ingredients_group = QGroupBox("Ingredients")
        ingredients_layout = QVBoxLayout(ingredients_group)
        
        ingredients_text = QTextEdit()
        ingredients_text.setPlainText(recipe_data.get('ingredients', ''))
        ingredients_text.setReadOnly(True)
        ingredients_text.setMaximumHeight(200)
        ingredients_layout.addWidget(ingredients_text)
        
        scroll_layout.addWidget(ingredients_group)
        
        # Instructions section
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        instructions_text = QTextEdit()
        instructions_text.setPlainText(recipe_data.get('instructions', ''))
        instructions_text.setReadOnly(True)
        instructions_text.setMaximumHeight(300)
        instructions_layout.addWidget(instructions_text)
        
        scroll_layout.addWidget(instructions_group)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        convert_btn = QPushButton("Convert to GF")
        convert_btn.clicked.connect(lambda: self.handle_gf_conversion(recipe_data, dialog))
        button_layout.addWidget(convert_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()

    def handle_gf_conversion(self, recipe_data, parent_dialog):
        if self.cookbook_panel:
            self.cookbook_panel.handle_gf_conversion_request(recipe_data)
            parent_dialog.accept() # Close the view dialog after conversion
    
    def confirm_delete_recipe(self) -> bool:
        """Show confirmation dialog for recipe deletion"""
        reply = QMessageBox.question(
            None,
            "Delete Recipe",
            "Are you sure you want to delete this recipe? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def get_web_url(self) -> Optional[str]:
        """Get web URL for recipe import"""
        dialog = QDialog()
        dialog.setWindowTitle("Import Recipe from Web")
        dialog.setModal(True)
        dialog.resize(400, 150)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Enter the URL of the recipe to import:"))
        
        url_edit = QLineEdit()
        url_edit.setPlaceholderText("https://example.com/recipe")
        layout.addWidget(url_edit)
        
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(import_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        if dialog.exec() == QDialog.Accepted:
            return url_edit.text().strip()
        
        return None
    
    def create_recipe_form(self, recipe_data: Optional[Dict[str, Any]] = None) -> QWidget:
        """Create recipe form widget"""
        form_widget = QWidget()
        layout = QVBoxLayout(form_widget)
        
        # Basic information group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        name_edit = QLineEdit()
        name_edit.setText(recipe_data.get('name', '') if recipe_data else '')
        basic_layout.addRow("Recipe Name:", name_edit)
        
        # Use new category selector
        from utils.category_selector import CategorySelector
        category_selector = CategorySelector(title="")
        category_selector.set_categories([
            ("Breakfast", "breakfast"),
            ("Lunch", "lunch"),
            ("Dinner", "dinner"),
            ("Snack", "snack"),
            ("Dessert", "dessert"),
            ("Beverage", "beverage"),
            ("Other", "other")
        ])
        if recipe_data and recipe_data.get('category_name'):
            # Map category name to category ID
            category_name = recipe_data.get('category_name', '').lower()
            category_selector.set_selected_category(category_name)
        basic_layout.addRow("Category:", category_selector)
        
        description_edit = QTextEdit()
        description_edit.setMaximumHeight(80)
        description_edit.setPlainText(recipe_data.get('description', '') if recipe_data else '')
        basic_layout.addRow("Description:", description_edit)
        
        layout.addWidget(basic_group)
        
        # Timing and servings group
        timing_group = QGroupBox("Timing & Servings")
        timing_layout = QFormLayout(timing_group)
        
        prep_spin = QSpinBox()
        prep_spin.setRange(0, 999)
        prep_spin.setValue(recipe_data.get('prep_time', 0) if recipe_data else 0)
        timing_layout.addRow("Prep Time (minutes):", prep_spin)
        
        cook_spin = QSpinBox()
        cook_spin.setRange(0, 999)
        cook_spin.setValue(recipe_data.get('cook_time', 0) if recipe_data else 0)
        timing_layout.addRow("Cook Time (minutes):", cook_spin)
        
        servings_spin = QSpinBox()
        servings_spin.setRange(1, 50)
        servings_spin.setValue(recipe_data.get('servings', 1) if recipe_data else 1)
        timing_layout.addRow("Servings:", servings_spin)
        
        difficulty_combo = QComboBox()
        difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        if recipe_data:
            difficulty_combo.setCurrentText(recipe_data.get('difficulty', 'Easy'))
        timing_layout.addRow("Difficulty:", difficulty_combo)
        
        layout.addWidget(timing_group)
        
        # Ingredients group
        ingredients_group = QGroupBox("Ingredients")
        ingredients_layout = QVBoxLayout(ingredients_group)
        
        ingredients_edit = QTextEdit()
        ingredients_edit.setMaximumHeight(120)
        ingredients_edit.setPlainText(recipe_data.get('ingredients', '') if recipe_data else '')
        ingredients_edit.setPlaceholderText("List ingredients, one per line...")
        ingredients_layout.addWidget(ingredients_edit)
        
        layout.addWidget(ingredients_group)
        
        # Instructions group
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        instructions_edit = QTextEdit()
        instructions_edit.setMaximumHeight(150)
        instructions_edit.setPlainText(recipe_data.get('instructions', '') if recipe_data else '')
        instructions_edit.setPlaceholderText("Enter cooking instructions...")
        instructions_layout.addWidget(instructions_edit)
        
        layout.addWidget(instructions_group)
        
        # Store references to form fields for data extraction
        form_widget.name_edit = name_edit
        form_widget.category_selector = category_selector
        form_widget.description_edit = description_edit
        form_widget.prep_spin = prep_spin
        form_widget.cook_spin = cook_spin
        form_widget.servings_spin = servings_spin
        form_widget.difficulty_combo = difficulty_combo
        form_widget.ingredients_edit = ingredients_edit
        form_widget.instructions_edit = instructions_edit
        
        return form_widget
    
    def extract_form_data(self, form_widget: QWidget) -> Dict[str, Any]:
        """Extract data from form widget"""
        category_id, category_name = form_widget.category_selector.get_selected_category()
        return {
            'name': form_widget.name_edit.text(),
            'category_name': category_name,
            'description': form_widget.description_edit.toPlainText(),
            'prep_time': form_widget.prep_spin.value(),
            'cook_time': form_widget.cook_spin.value(),
            'servings': form_widget.servings_spin.value(),
            'difficulty': form_widget.difficulty_combo.currentText(),
            'ingredients': form_widget.ingredients_edit.toPlainText(),
            'instructions': form_widget.instructions_edit.toPlainText()
        }
