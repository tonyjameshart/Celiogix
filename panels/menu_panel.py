# path: panels/menu_panel_pyside6.py
"""
Menu Panel for PySide6 Application
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QMessageBox,
    QDialog, QCheckBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from panels.base_panel import BasePanel
from panels.context_menu_mixin import MenuContextMenuMixin


class MenuPanel(MenuContextMenuMixin, BasePanel):
    """Menu panel for PySide6"""
    
    def __init__(self, master=None, app=None):
        super().__init__(master, app)
    
    def setup_ui(self):
        """Set up the menu panel UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Week selection
        week_layout = QHBoxLayout()
        week_layout.addWidget(QLabel("Week:"))
        self.week_combo = QComboBox()
        self.week_combo.addItems(["This Week", "Next Week", "Week 3", "Week 4"])
        self.week_combo.currentTextChanged.connect(self.load_week_menu)
        week_layout.addWidget(self.week_combo)
        week_layout.addStretch()
        
        generate_btn = QPushButton("Generate Menu")
        generate_btn.clicked.connect(self.generate_menu)
        week_layout.addWidget(generate_btn)
        
        main_layout.addLayout(week_layout)
        
        # Menu table
        self.menu_table = QTableWidget()
        self.menu_table.setColumnCount(4)
        self.menu_table.setHorizontalHeaderLabels(["Day", "Breakfast", "Lunch", "Dinner"])
        
        # Set up auto-sizing columns with equal minimum width
        header = self.menu_table.horizontalHeader()
        header.setStretchLastSection(False)  # Disable stretch last section
        for col in range(4):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
            header.setMinimumSectionSize(int(self.menu_table.width() * 0.25) if self.menu_table.width() > 0 else 100)
        
        self.menu_table.setAlternatingRowColors(True)
        self.menu_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.menu_table.itemDoubleClicked.connect(self.edit_meal)
        
        # Configure selection behavior to minimize default Qt styling
        self.menu_table.setSelectionMode(QTableWidget.SingleSelection)  # Single selection mode
        self.menu_table.setShowGrid(True)  # Show grid for better visual separation
        self.menu_table.setGridStyle(Qt.SolidLine)  # Solid grid lines
        
        # Apply custom delegate to suppress selection borders
        from utils.custom_delegates import MenuTableDelegate
        self.menu_table.setItemDelegate(MenuTableDelegate())
        
        # Minimal custom styling - delegate handles selection
        self.menu_table.setStyleSheet("""
            QTableWidget::item {
                padding: 6px;
                border: none;          /* no cell border */
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;    /* visible selected background */
                color: #1976d2;               /* selected text color */
                /* no border here */
            }
        """)
        
        # Set up resize event handler for dynamic minimum width
        self.menu_table.resizeEvent = self.on_table_resize
        
        main_layout.addWidget(self.menu_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.edit_meal_btn = QPushButton("Edit Meal")
        self.edit_meal_btn.clicked.connect(self.edit_meal)
        self.edit_meal_btn.setEnabled(False)
        
        self.add_meal_btn = QPushButton("Add Meal")
        self.add_meal_btn.clicked.connect(self.add_meal)
        
        self.shopping_btn = QPushButton("Generate Shopping List")
        self.shopping_btn.clicked.connect(self.generate_shopping_list)
        
        self.export_btn = QPushButton("Export Menu")
        self.export_btn.clicked.connect(self.export_menu)
        
        self.import_btn = QPushButton("Import Menu")
        self.import_btn.clicked.connect(self.import_menu)
        
        self.push_to_mobile_btn = QPushButton("📱 Push Recipes to Mobile")
        self.push_to_mobile_btn.clicked.connect(self.push_recipes_to_mobile)
        self.push_to_mobile_btn.setToolTip("Send selected recipes to mobile app for offline viewing")
        
        button_layout.addWidget(self.edit_meal_btn)
        button_layout.addWidget(self.add_meal_btn)
        button_layout.addWidget(self.shopping_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.push_to_mobile_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Connect selection changes
        self.menu_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # Load initial data
        self.load_week_menu()

    def refresh(self):
        """Refresh panel data"""
        self.load_week_menu()
    
    def apply_custom_table_styling(self):
        """Apply custom table styling after theme changes"""
        if hasattr(self, 'menu_table'):
            # Re-apply the minimal selection styling
            self.menu_table.setStyleSheet("""
                QTableWidget::item {
                    padding: 6px;
                    border: none;          /* no cell border */
                }
                QTableWidget::item:selected {
                    background-color: #e3f2fd;    /* visible selected background */
                    color: #1976d2;               /* selected text color */
                    /* no border here */
                }
            """)
    
    def load_week_menu(self):
        """Load menu for selected week"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        sample_meals = [
            ("GF Pancakes", "Quinoa Salad", "Baked Salmon"),
            ("Oatmeal", "GF Sandwich", "Chicken Stir-fry"),
            ("Smoothie Bowl", "Lentil Soup", "Turkey Meatballs"),
            ("GF Toast", "Caesar Salad", "Fish Tacos"),
            ("Yogurt Parfait", "Wrap", "Pasta"),
            ("Waffles", "Leftovers", "BBQ"),
            ("Brunch", "Snacks", "Family Dinner")
        ]
        
        self.menu_table.setRowCount(len(days))
        for row, day in enumerate(days):
            self.menu_table.setItem(row, 0, QTableWidgetItem(day))
            if row < len(sample_meals):
                breakfast, lunch, dinner = sample_meals[row]
                self.menu_table.setItem(row, 1, QTableWidgetItem(breakfast))
                self.menu_table.setItem(row, 2, QTableWidgetItem(lunch))
                self.menu_table.setItem(row, 3, QTableWidgetItem(dinner))
            else:
                self.menu_table.setItem(row, 1, QTableWidgetItem(""))
                self.menu_table.setItem(row, 2, QTableWidgetItem(""))
                self.menu_table.setItem(row, 3, QTableWidgetItem(""))
    
    def on_selection_changed(self):
        """Handle table selection changes"""
        has_selection = len(self.menu_table.selectedItems()) > 0
        self.edit_meal_btn.setEnabled(has_selection)
    
    def on_table_resize(self, event):
        """Handle table resize to update minimum column widths"""
        header = self.menu_table.horizontalHeader()
        min_width = int(self.menu_table.width() * 0.25) if self.menu_table.width() > 0 else 100
        header.setMinimumSectionSize(min_width)
        QTableWidget.resizeEvent(self.menu_table, event)
    
    def edit_meal(self):
        """Edit selected meal"""
        current_row = self.menu_table.currentRow()
        current_col = self.menu_table.currentColumn()
        
        if current_row >= 0 and current_col >= 1:
            day = self.menu_table.item(current_row, 0).text()
            meal_type = ["", "Breakfast", "Lunch", "Dinner"][current_col]
            current_meal = self.menu_table.item(current_row, current_col).text()
            
            # Create edit dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit {meal_type} for {day}")
            dialog.setModal(True)
            dialog.resize(500, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Header
            header_label = QLabel(f"Edit {meal_type} for {day}")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(header_label)
            
            # Current meal display
            current_label = QLabel(f"Current: {current_meal}")
            layout.addWidget(current_label)
            
            # Recipe selection
            recipe_layout = QHBoxLayout()
            recipe_layout.addWidget(QLabel("Recipe:"))
            recipe_combo = QComboBox()
            recipe_combo.setEditable(True)
            recipe_combo.addItems([
                "Gluten-Free Pasta with Marinara",
                "Quinoa Salad Bowl",
                "Grilled Chicken with Vegetables",
                "Rice and Beans",
                "Gluten-Free Pizza",
                "Stir-Fried Vegetables",
                "Baked Salmon",
                "Vegetable Soup",
                "Tacos with Corn Tortillas",
                "Stuffed Bell Peppers"
            ])
            recipe_combo.setCurrentText(current_meal)
            recipe_layout.addWidget(recipe_combo)
            layout.addLayout(recipe_layout)
            
            # Meal notes
            notes_layout = QVBoxLayout()
            notes_layout.addWidget(QLabel("Notes:"))
            notes_edit = QTextEdit()
            notes_edit.setMaximumHeight(100)
            notes_edit.setPlaceholderText("Add any special notes or modifications...")
            notes_layout.addWidget(notes_edit)
            layout.addLayout(notes_layout)
            
            # Meal time
            time_layout = QHBoxLayout()
            time_layout.addWidget(QLabel("Time:"))
            time_combo = QComboBox()
            time_combo.addItems([
                "6:00 AM", "7:00 AM", "8:00 AM",  # Breakfast
                "12:00 PM", "1:00 PM", "2:00 PM",  # Lunch
                "6:00 PM", "7:00 PM", "8:00 PM"   # Dinner
            ])
            # Set default time based on meal type
            if meal_type == "Breakfast":
                time_combo.setCurrentText("8:00 AM")
            elif meal_type == "Lunch":
                time_combo.setCurrentText("12:00 PM")
            elif meal_type == "Dinner":
                time_combo.setCurrentText("7:00 PM")
            time_layout.addWidget(time_combo)
            layout.addLayout(time_layout)
            
            # Portion size
            portion_layout = QHBoxLayout()
            portion_layout.addWidget(QLabel("Portion Size:"))
            portion_combo = QComboBox()
            portion_combo.addItems(["Small", "Medium", "Large", "Extra Large"])
            portion_combo.setCurrentText("Medium")
            portion_layout.addWidget(portion_combo)
            layout.addLayout(portion_layout)
            
            # Buttons
            button_layout = QHBoxLayout()
            save_btn = QPushButton("Save")
            cancel_btn = QPushButton("Cancel")
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            # Connect signals
            save_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            if dialog.exec() == QDialog.Accepted:
                # Update the meal in the table
                new_meal = recipe_combo.currentText()
                notes = notes_edit.toPlainText()
                time = time_combo.currentText()
                portion = portion_combo.currentText()
                
                # Create display text with additional info
                display_text = new_meal
                if portion != "Medium":
                    display_text += f" ({portion})"
                if notes:
                    display_text += f" - {notes[:30]}..."
                
                # Update table
                self.menu_table.setItem(current_row, current_col, QTableWidgetItem(display_text))
                
                # Save to database
                self._save_meal_to_database(day, meal_type, new_meal, notes, time, portion)
                
                QMessageBox.information(self, "Success", f"{meal_type} updated successfully!")
    
    def _save_meal_to_database(self, day: str, meal_type: str, recipe: str, notes: str, time: str, portion: str):
        """Save meal to database"""
        try:
            from utils.db import get_connection
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Insert or update meal (table already exists from migrations)
            cursor.execute("""
                INSERT OR REPLACE INTO menu_plan (date, meal, title, notes, time)
                VALUES (?, ?, ?, ?, ?)
            """, (day, meal_type, recipe, notes, time))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving meal to database: {str(e)}")
            # Don't show error to user as this is a background operation
    
    def add_meal(self):
        """Add a new meal"""
        # Create add meal dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Meal")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel("Add New Meal")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Day selection
        day_layout = QHBoxLayout()
        day_layout.addWidget(QLabel("Day:"))
        day_combo = QComboBox()
        day_combo.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        day_layout.addWidget(day_combo)
        layout.addLayout(day_layout)
        
        # Meal type
        meal_type_layout = QHBoxLayout()
        meal_type_layout.addWidget(QLabel("Meal Type:"))
        meal_type_combo = QComboBox()
        meal_type_combo.addItems(["Breakfast", "Lunch", "Dinner", "Snack"])
        meal_type_layout.addWidget(meal_type_combo)
        layout.addLayout(meal_type_layout)
        
        # Recipe selection
        recipe_layout = QHBoxLayout()
        recipe_layout.addWidget(QLabel("Recipe:"))
        recipe_combo = QComboBox()
        recipe_combo.setEditable(True)
        recipe_combo.addItems([
            "Gluten-Free Pancakes with Berries",
            "Quinoa Power Bowl",
            "Grilled Chicken with Vegetables",
            "Rice and Beans Bowl",
            "Gluten-Free Pizza",
            "Stir-Fried Vegetables",
            "Baked Salmon with Herbs",
            "Vegetable Soup",
            "Tacos with Corn Tortillas",
            "Stuffed Bell Peppers",
            "GF Pasta with Marinara",
            "Caesar Salad (GF)",
            "Turkey Meatballs",
            "Fish Tacos",
            "BBQ Chicken",
            "Lentil Curry",
            "Chicken Stir-fry",
            "Baked Sweet Potato",
            "GF Waffles",
            "Smoothie Bowl"
        ])
        recipe_layout.addWidget(recipe_combo)
        layout.addLayout(recipe_layout)
        
        # Meal time
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Time:"))
        time_combo = QComboBox()
        time_combo.addItems([
            "6:00 AM", "6:30 AM", "7:00 AM", "7:30 AM", "8:00 AM", "8:30 AM",  # Breakfast
            "11:30 AM", "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM",  # Lunch
            "5:30 PM", "6:00 PM", "6:30 PM", "7:00 PM", "7:30 PM", "8:00 PM"   # Dinner
        ])
        # Set default time based on meal type
        if meal_type_combo.currentText() == "Breakfast":
            time_combo.setCurrentText("8:00 AM")
        elif meal_type_combo.currentText() == "Lunch":
            time_combo.setCurrentText("12:00 PM")
        elif meal_type_combo.currentText() == "Dinner":
            time_combo.setCurrentText("7:00 PM")
        time_layout.addWidget(time_combo)
        layout.addLayout(time_layout)
        
        # Portion size
        portion_layout = QHBoxLayout()
        portion_layout.addWidget(QLabel("Portion Size:"))
        portion_combo = QComboBox()
        portion_combo.addItems(["Small", "Medium", "Large", "Extra Large"])
        portion_combo.setCurrentText("Medium")
        portion_layout.addWidget(portion_combo)
        layout.addLayout(portion_layout)
        
        # Meal notes
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        notes_edit = QTextEdit()
        notes_edit.setMaximumHeight(100)
        notes_edit.setPlaceholderText("Add any special notes, modifications, or dietary considerations...")
        notes_layout.addWidget(notes_edit)
        layout.addLayout(notes_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Add Meal")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Update time when meal type changes
        def update_time_default():
            if meal_type_combo.currentText() == "Breakfast":
                time_combo.setCurrentText("8:00 AM")
            elif meal_type_combo.currentText() == "Lunch":
                time_combo.setCurrentText("12:00 PM")
            elif meal_type_combo.currentText() == "Dinner":
                time_combo.setCurrentText("7:00 PM")
        
        meal_type_combo.currentTextChanged.connect(update_time_default)
        
        if dialog.exec() == QDialog.Accepted:
            # Get selected values
            day = day_combo.currentText()
            meal_type = meal_type_combo.currentText()
            recipe = recipe_combo.currentText()
            time = time_combo.currentText()
            portion = portion_combo.currentText()
            notes = notes_edit.toPlainText()
            
            # Find the row for the selected day
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            try:
                day_row = days.index(day)
            except ValueError:
                day_row = 0
            
            # Determine column based on meal type
            meal_columns = {"Breakfast": 1, "Lunch": 2, "Dinner": 3}
            meal_col = meal_columns.get(meal_type, 1)
            
            # Create display text
            display_text = recipe
            if portion != "Medium":
                display_text += f" ({portion})"
            if notes:
                display_text += f" - {notes[:30]}..."
            
            # Update table
            self.menu_table.setItem(day_row, meal_col, QTableWidgetItem(display_text))
            
            # Save to database
            self._save_meal_to_database(day, meal_type, recipe, notes, time, portion)
            
            QMessageBox.information(self, "Success", f"{meal_type} added successfully for {day}!")
    
    def generate_menu(self):
        """Generate automatic menu"""
        # Create menu generation dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate Menu")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel("Generate Gluten-Free Menu")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Menu preferences
        preferences_group = QGroupBox("Menu Preferences")
        preferences_layout = QVBoxLayout(preferences_group)
        
        # Dietary preferences
        diet_layout = QHBoxLayout()
        diet_layout.addWidget(QLabel("Dietary Focus:"))
        diet_combo = QComboBox()
        diet_combo.addItems(["Balanced", "High Protein", "Vegetarian", "Quick & Easy", "Family Friendly", "Budget Friendly"])
        diet_layout.addWidget(diet_combo)
        preferences_layout.addLayout(diet_layout)
        
        # Meal variety
        variety_layout = QHBoxLayout()
        variety_layout.addWidget(QLabel("Variety Level:"))
        variety_combo = QComboBox()
        variety_combo.addItems(["High Variety", "Medium Variety", "Simple & Consistent"])
        variety_layout.addWidget(variety_combo)
        preferences_layout.addLayout(variety_layout)
        
        # Cooking time
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Max Cooking Time:"))
        time_combo = QComboBox()
        time_combo.addItems(["15 minutes", "30 minutes", "45 minutes", "60+ minutes"])
        time_combo.setCurrentText("30 minutes")
        time_layout.addWidget(time_combo)
        preferences_layout.addLayout(time_layout)
        
        layout.addWidget(preferences_group)
        
        # Include options
        options_group = QGroupBox("Include Options")
        options_layout = QVBoxLayout(options_group)
        
        include_breakfast = QCheckBox("Include Breakfast")
        include_breakfast.setChecked(True)
        options_layout.addWidget(include_breakfast)
        
        include_lunch = QCheckBox("Include Lunch")
        include_lunch.setChecked(True)
        options_layout.addWidget(include_lunch)
        
        include_dinner = QCheckBox("Include Dinner")
        include_dinner.setChecked(True)
        options_layout.addWidget(include_dinner)
        
        include_snacks = QCheckBox("Include Snacks")
        options_layout.addWidget(include_snacks)
        
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        generate_btn = QPushButton("Generate Menu")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(generate_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        generate_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.Accepted:
            # Get preferences
            dietary_focus = diet_combo.currentText()
            variety_level = variety_combo.currentText()
            max_time = time_combo.currentText()
            include_bfast = include_breakfast.isChecked()
            include_lun = include_lunch.isChecked()
            include_din = include_dinner.isChecked()
            include_sna = include_snacks.isChecked()
            
            # Generate menu based on preferences
            self._generate_menu_with_preferences(dietary_focus, variety_level, max_time, 
                                               include_bfast, include_lun, include_din, include_sna)
            
            QMessageBox.information(self, "Success", "Menu generated successfully!")
    
    def _generate_menu_with_preferences(self, dietary_focus, variety_level, max_time, 
                                      include_breakfast, include_lunch, include_dinner, include_snacks):
        """Generate menu based on user preferences"""
        
        # Define meal options based on dietary focus
        meal_options = {
            "Balanced": {
                "breakfast": [
                    "GF Pancakes with Berries", "Oatmeal with Nuts", "GF Toast with Avocado",
                    "Smoothie Bowl", "GF Waffles", "Yogurt Parfait"
                ],
                "lunch": [
                    "Quinoa Power Bowl", "Caesar Salad (GF)", "Rice and Beans Bowl",
                    "Turkey Wrap (GF)", "Lentil Soup", "Chicken Salad"
                ],
                "dinner": [
                    "Baked Salmon with Herbs", "Grilled Chicken with Vegetables", "Turkey Meatballs",
                    "Fish Tacos", "Stuffed Bell Peppers", "Chicken Stir-fry"
                ]
            },
            "High Protein": {
                "breakfast": [
                    "Protein Smoothie Bowl", "GF Pancakes with Greek Yogurt", "Egg Scramble",
                    "Protein Oatmeal", "GF Waffles with Nut Butter", "Greek Yogurt Bowl"
                ],
                "lunch": [
                    "Quinoa Power Bowl", "Grilled Chicken Salad", "Turkey Meatballs",
                    "Lentil Curry", "Chicken Stir-fry", "Protein Wrap (GF)"
                ],
                "dinner": [
                    "Baked Salmon with Herbs", "Grilled Chicken with Vegetables", "Turkey Meatballs",
                    "BBQ Chicken", "Fish Tacos", "Chicken Stir-fry"
                ]
            },
            "Vegetarian": {
                "breakfast": [
                    "GF Pancakes with Berries", "Oatmeal with Nuts", "Smoothie Bowl",
                    "GF Waffles", "Yogurt Parfait", "GF Toast with Nut Butter"
                ],
                "lunch": [
                    "Quinoa Power Bowl", "Lentil Soup", "Caesar Salad (GF)",
                    "Rice and Beans Bowl", "Vegetable Stir-fry", "GF Pasta with Marinara"
                ],
                "dinner": [
                    "Stuffed Bell Peppers", "Vegetable Soup", "Lentil Curry",
                    "GF Pasta with Marinara", "Stir-Fried Vegetables", "Baked Sweet Potato"
                ]
            },
            "Quick & Easy": {
                "breakfast": [
                    "GF Toast with Avocado", "Yogurt Parfait", "Smoothie Bowl",
                    "GF Pancakes (mix)", "Oatmeal", "GF Waffles (frozen)"
                ],
                "lunch": [
                    "Turkey Wrap (GF)", "Caesar Salad (GF)", "Rice and Beans Bowl",
                    "Lentil Soup", "Chicken Salad", "GF Pasta with Marinara"
                ],
                "dinner": [
                    "Baked Salmon with Herbs", "Grilled Chicken", "Fish Tacos",
                    "Chicken Stir-fry", "Turkey Meatballs", "BBQ Chicken"
                ]
            },
            "Family Friendly": {
                "breakfast": [
                    "GF Pancakes with Berries", "GF Waffles", "Smoothie Bowl",
                    "Yogurt Parfait", "Oatmeal", "GF Toast with Nut Butter"
                ],
                "lunch": [
                    "Turkey Wrap (GF)", "Caesar Salad (GF)", "Rice and Beans Bowl",
                    "Chicken Salad", "Lentil Soup", "GF Pasta with Marinara"
                ],
                "dinner": [
                    "Baked Salmon with Herbs", "Grilled Chicken with Vegetables", "Turkey Meatballs",
                    "Fish Tacos", "BBQ Chicken", "Stuffed Bell Peppers"
                ]
            },
            "Budget Friendly": {
                "breakfast": [
                    "Oatmeal with Nuts", "GF Toast with Avocado", "Yogurt Parfait",
                    "GF Pancakes", "Smoothie Bowl", "GF Waffles"
                ],
                "lunch": [
                    "Rice and Beans Bowl", "Lentil Soup", "Caesar Salad (GF)",
                    "GF Pasta with Marinara", "Vegetable Soup", "Turkey Wrap (GF)"
                ],
                "dinner": [
                    "Turkey Meatballs", "Lentil Curry", "Stuffed Bell Peppers",
                    "Vegetable Soup", "Rice and Beans Bowl", "Chicken Stir-fry"
                ]
            }
        }
        
        # Get meal options for selected dietary focus
        options = meal_options.get(dietary_focus, meal_options["Balanced"])
        
        # Days of the week
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Generate meals for each day
        import random
        
        for day_idx, day in enumerate(days):
            # Breakfast
            if include_breakfast and variety_level in ["High Variety", "Medium Variety"]:
                breakfast = random.choice(options["breakfast"])
                self.menu_table.setItem(day_idx, 1, QTableWidgetItem(breakfast))
                self._save_meal_to_database(day, "Breakfast", breakfast, "Generated menu", "8:00 AM", "Medium")
            
            # Lunch
            if include_lunch and variety_level in ["High Variety", "Medium Variety"]:
                lunch = random.choice(options["lunch"])
                self.menu_table.setItem(day_idx, 2, QTableWidgetItem(lunch))
                self._save_meal_to_database(day, "Lunch", lunch, "Generated menu", "12:00 PM", "Medium")
            
            # Dinner
            if include_dinner:
                dinner = random.choice(options["dinner"])
                self.menu_table.setItem(day_idx, 3, QTableWidgetItem(dinner))
                self._save_meal_to_database(day, "Dinner", dinner, "Generated menu", "7:00 PM", "Medium")
        
        # For simple & consistent, use fewer meal variations
        if variety_level == "Simple & Consistent":
            consistent_meals = {
                "breakfast": options["breakfast"][0] if options["breakfast"] else "",
                "lunch": options["lunch"][0] if options["lunch"] else "",
                "dinner": options["dinner"][0] if options["dinner"] else ""
            }
            
            for day_idx, day in enumerate(days):
                if include_breakfast and consistent_meals["breakfast"]:
                    self.menu_table.setItem(day_idx, 1, QTableWidgetItem(consistent_meals["breakfast"]))
                    self._save_meal_to_database(day, "Breakfast", consistent_meals["breakfast"], "Generated menu", "8:00 AM", "Medium")
                
                if include_lunch and consistent_meals["lunch"]:
                    self.menu_table.setItem(day_idx, 2, QTableWidgetItem(consistent_meals["lunch"]))
                    self._save_meal_to_database(day, "Lunch", consistent_meals["lunch"], "Generated menu", "12:00 PM", "Medium")
                
                if include_dinner and consistent_meals["dinner"]:
                    self.menu_table.setItem(day_idx, 3, QTableWidgetItem(consistent_meals["dinner"]))
                    self._save_meal_to_database(day, "Dinner", consistent_meals["dinner"], "Generated menu", "7:00 PM", "Medium")
    
    def generate_shopping_list(self):
        """Generate shopping list from menu"""
        # Collect all meals from the menu table
        meals = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for row in range(self.menu_table.rowCount()):
            day = days[row] if row < len(days) else f"Day {row + 1}"
            
            # Get breakfast, lunch, dinner
            for col in range(1, 4):  # Columns 1, 2, 3
                meal_item = self.menu_table.item(row, col)
                if meal_item and meal_item.text().strip():
                    meal_type = ["Breakfast", "Lunch", "Dinner"][col - 1]
                    meals.append({
                        'day': day,
                        'type': meal_type,
                        'recipe': meal_item.text().strip()
                    })
        
        if not meals:
            QMessageBox.warning(self, "No Meals", "No meals found in the menu. Please add some meals first.")
            return
        
        # Create shopping list dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate Shopping List")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel("Generate Shopping List from Menu")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Show meals that will be included
        meals_group = QGroupBox("Meals to Include")
        meals_layout = QVBoxLayout(meals_group)
        
        meals_text = QTextEdit()
        meals_text.setMaximumHeight(150)
        meals_text.setReadOnly(True)
        
        meals_summary = []
        for meal in meals:
            meals_summary.append(f"{meal['day']} {meal['type']}: {meal['recipe']}")
        
        meals_text.setPlainText("\n".join(meals_summary))
        meals_layout.addWidget(meals_text)
        layout.addWidget(meals_group)
        
        # Shopping list options
        options_group = QGroupBox("Shopping List Options")
        options_layout = QVBoxLayout(options_group)
        
        # Include pantry staples
        include_staples = QCheckBox("Include pantry staples (salt, pepper, oil, etc.)")
        include_staples.setChecked(True)
        options_layout.addWidget(include_staples)
        
        # Group by category
        group_by_category = QCheckBox("Group items by category")
        group_by_category.setChecked(True)
        options_layout.addWidget(group_by_category)
        
        # Include quantities
        include_quantities = QCheckBox("Include estimated quantities")
        include_quantities.setChecked(True)
        options_layout.addWidget(include_quantities)
        
        # Add to existing shopping list
        add_to_existing = QCheckBox("Add to existing shopping list")
        options_layout.addWidget(add_to_existing)
        
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        generate_btn = QPushButton("Generate Shopping List")
        preview_btn = QPushButton("Preview List")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(generate_btn)
        button_layout.addWidget(preview_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        generate_btn.clicked.connect(dialog.accept)
        preview_btn.clicked.connect(lambda: self._preview_shopping_list(meals, 
                                                                        include_staples.isChecked(),
                                                                        group_by_category.isChecked(),
                                                                        include_quantities.isChecked()))
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.Accepted:
            # Generate the shopping list
            shopping_list = self._generate_shopping_list_from_meals(meals, 
                                                                   include_staples.isChecked(),
                                                                   group_by_category.isChecked(),
                                                                   include_quantities.isChecked())
            
            # Add to shopping list panel or show results
            self._add_shopping_list_to_panel(shopping_list, add_to_existing.isChecked())
            
            QMessageBox.information(self, "Success", f"Shopping list generated with {len(shopping_list)} items!")
    
    def _generate_shopping_list_from_meals(self, meals, include_staples, group_by_category, include_quantities):
        """Generate shopping list items from menu meals"""
        
        # Recipe to ingredients mapping
        recipe_ingredients = {
            # Breakfast recipes
            "GF Pancakes with Berries": [
                ("GF Pancake Mix", "1 box"),
                ("Eggs", "2"),
                ("Milk (GF)", "1 cup"),
                ("Berries", "1 pint"),
                ("Maple Syrup", "1 bottle")
            ],
            "Oatmeal with Nuts": [
                ("Rolled Oats (GF)", "1 container"),
                ("Almonds", "1 bag"),
                ("Walnuts", "1 bag"),
                ("Honey", "1 bottle"),
                ("Milk (GF)", "1 gallon")
            ],
            "GF Toast with Avocado": [
                ("GF Bread", "1 loaf"),
                ("Avocados", "4"),
                ("Lemon", "2"),
                ("Salt", "1 container"),
                ("Pepper", "1 container")
            ],
            "Smoothie Bowl": [
                ("Frozen Berries", "2 bags"),
                ("Bananas", "1 bunch"),
                ("Greek Yogurt (GF)", "1 container"),
                ("Granola (GF)", "1 bag"),
                ("Honey", "1 bottle")
            ],
            "GF Waffles": [
                ("GF Waffle Mix", "1 box"),
                ("Eggs", "2"),
                ("Milk (GF)", "1 cup"),
                ("Butter (GF)", "1 stick"),
                ("Maple Syrup", "1 bottle")
            ],
            "Yogurt Parfait": [
                ("Greek Yogurt (GF)", "2 containers"),
                ("Granola (GF)", "1 bag"),
                ("Mixed Berries", "2 containers"),
                ("Honey", "1 bottle")
            ],
            
            # Lunch recipes
            "Quinoa Power Bowl": [
                ("Quinoa (GF)", "1 bag"),
                ("Chickpeas", "2 cans"),
                ("Cucumber", "2"),
                ("Cherry Tomatoes", "1 container"),
                ("Feta Cheese (GF)", "1 container"),
                ("Olive Oil", "1 bottle")
            ],
            "Caesar Salad (GF)": [
                ("Romaine Lettuce", "2 heads"),
                ("GF Croutons", "1 bag"),
                ("Parmesan Cheese (GF)", "1 container"),
                ("Caesar Dressing (GF)", "1 bottle"),
                ("Lemon", "2")
            ],
            "Rice and Beans Bowl": [
                ("Brown Rice (GF)", "1 bag"),
                ("Black Beans", "2 cans"),
                ("Corn", "1 can"),
                ("Bell Peppers", "3"),
                ("Onion", "1"),
                ("Cilantro", "1 bunch")
            ],
            "Turkey Wrap (GF)": [
                ("GF Tortillas", "1 package"),
                ("Turkey Breast", "1 lb"),
                ("Lettuce", "1 head"),
                ("Tomatoes", "2"),
                ("Cheese (GF)", "1 package"),
                ("Mayo (GF)", "1 jar")
            ],
            "Lentil Soup": [
                ("Red Lentils", "1 bag"),
                ("Carrots", "1 bag"),
                ("Celery", "1 bunch"),
                ("Onion", "2"),
                ("Vegetable Broth (GF)", "2 boxes"),
                ("Garlic", "1 bulb")
            ],
            "Chicken Salad": [
                ("Chicken Breast", "2 lbs"),
                ("Lettuce", "1 head"),
                ("Cherry Tomatoes", "1 container"),
                ("Cucumber", "1"),
                ("GF Croutons", "1 bag"),
                ("Ranch Dressing (GF)", "1 bottle")
            ],
            
            # Dinner recipes
            "Baked Salmon with Herbs": [
                ("Salmon Fillets", "4 pieces"),
                ("Fresh Dill", "1 bunch"),
                ("Lemon", "3"),
                ("Olive Oil", "1 bottle"),
                ("Asparagus", "2 bunches"),
                ("Salt", "1 container")
            ],
            "Grilled Chicken with Vegetables": [
                ("Chicken Breast", "3 lbs"),
                ("Bell Peppers", "4"),
                ("Zucchini", "3"),
                ("Onion", "2"),
                ("Olive Oil", "1 bottle"),
                ("Italian Seasoning", "1 container")
            ],
            "Turkey Meatballs": [
                ("Ground Turkey", "2 lbs"),
                ("GF Breadcrumbs", "1 bag"),
                ("Eggs", "2"),
                ("Parmesan Cheese (GF)", "1 container"),
                ("GF Pasta", "1 box"),
                ("Marinara Sauce (GF)", "1 jar")
            ],
            "Fish Tacos": [
                ("White Fish", "2 lbs"),
                ("GF Tortillas", "1 package"),
                ("Cabbage", "1 head"),
                ("Lime", "3"),
                ("Sour Cream (GF)", "1 container"),
                ("Avocado", "3")
            ],
            "Stuffed Bell Peppers": [
                ("Bell Peppers", "6"),
                ("Ground Beef", "1 lb"),
                ("Rice (GF)", "1 bag"),
                ("Tomatoes", "3"),
                ("Onion", "1"),
                ("Cheese (GF)", "1 package")
            ],
            "Chicken Stir-fry": [
                ("Chicken Breast", "2 lbs"),
                ("Broccoli", "2 heads"),
                ("Carrots", "1 bag"),
                ("Snow Peas", "1 bag"),
                ("Soy Sauce (GF)", "1 bottle"),
                ("Ginger", "1 piece")
            ]
        }
        
        # Pantry staples
        pantry_staples = [
            ("Salt", "1 container"),
            ("Black Pepper", "1 container"),
            ("Olive Oil", "1 bottle"),
            ("Vegetable Oil", "1 bottle"),
            ("Garlic", "1 bulb"),
            ("Onion", "1 bag"),
            ("Butter (GF)", "1 package"),
            ("Flour (GF)", "1 bag"),
            ("Sugar", "1 bag"),
            ("Baking Powder (GF)", "1 container")
        ]
        
        # Collect all ingredients
        all_ingredients = {}
        
        for meal in meals:
            recipe = meal['recipe']
            # Remove portion and notes info for matching
            base_recipe = recipe.split(' (')[0].split(' - ')[0]
            
            if base_recipe in recipe_ingredients:
                for ingredient, quantity in recipe_ingredients[base_recipe]:
                    if ingredient in all_ingredients:
                        # Combine quantities (simple approach)
                        all_ingredients[ingredient] = f"{all_ingredients[ingredient]} + {quantity}"
                    else:
                        all_ingredients[ingredient] = quantity
        
        # Add pantry staples if requested
        if include_staples:
            for ingredient, quantity in pantry_staples:
                if ingredient not in all_ingredients:
                    all_ingredients[ingredient] = quantity
        
        # Convert to shopping list format
        shopping_list = []
        for ingredient, quantity in all_ingredients.items():
            shopping_list.append({
                'item': ingredient,
                'quantity': quantity if include_quantities else "",
                'category': self._get_ingredient_category(ingredient),
                'notes': "From menu planning"
            })
        
        return shopping_list
    
    def _get_ingredient_category(self, ingredient):
        """Get category for ingredient"""
        ingredient_lower = ingredient.lower()
        
        if any(word in ingredient_lower for word in ['chicken', 'turkey', 'beef', 'pork', 'salmon', 'fish']):
            return "Meat & Seafood"
        elif any(word in ingredient_lower for word in ['milk', 'cheese', 'yogurt', 'butter', 'cream']):
            return "Dairy"
        elif any(word in ingredient_lower for word in ['lettuce', 'tomato', 'carrot', 'pepper', 'onion', 'celery', 'broccoli', 'asparagus']):
            return "Vegetables"
        elif any(word in ingredient_lower for word in ['berry', 'banana', 'apple', 'lemon', 'lime', 'avocado']):
            return "Fruits"
        elif any(word in ingredient_lower for word in ['bread', 'pasta', 'rice', 'quinoa', 'oats', 'tortilla', 'waffle', 'pancake']):
            return "Grains & Bread"
        elif any(word in ingredient_lower for word in ['bean', 'lentil', 'chickpea', 'corn']):
            return "Canned & Pantry"
        elif any(word in ingredient_lower for word in ['oil', 'vinegar', 'sauce', 'dressing', 'syrup', 'honey']):
            return "Condiments & Oils"
        elif any(word in ingredient_lower for word in ['salt', 'pepper', 'garlic', 'ginger', 'seasoning']):
            return "Spices & Herbs"
        else:
            return "Other"
    
    def _preview_shopping_list(self, meals, include_staples, group_by_category, include_quantities):
        """Preview the shopping list before generating"""
        shopping_list = self._generate_shopping_list_from_meals(meals, include_staples, group_by_category, include_quantities)
        
        # Create preview dialog
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("Shopping List Preview")
        preview_dialog.setModal(True)
        preview_dialog.resize(500, 400)
        
        layout = QVBoxLayout(preview_dialog)
        
        # Header
        header_label = QLabel("Shopping List Preview")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Shopping list text
        list_text = QTextEdit()
        list_text.setReadOnly(True)
        
        if group_by_category:
            # Group by category
            categories = {}
            for item in shopping_list:
                category = item['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(item)
            
            preview_text = []
            for category, items in sorted(categories.items()):
                preview_text.append(f"\n{category}:")
                preview_text.append("-" * len(category))
                for item in items:
                    if include_quantities and item['quantity']:
                        preview_text.append(f"  • {item['item']} - {item['quantity']}")
                    else:
                        preview_text.append(f"  • {item['item']}")
        else:
            # Simple list
            preview_text = []
            for item in shopping_list:
                if include_quantities and item['quantity']:
                    preview_text.append(f"• {item['item']} - {item['quantity']}")
                else:
                    preview_text.append(f"• {item['item']}")
        
        list_text.setPlainText("\n".join(preview_text))
        layout.addWidget(list_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(preview_dialog.accept)
        layout.addWidget(close_btn)
        
        preview_dialog.exec()
    
    def _add_shopping_list_to_panel(self, shopping_list, add_to_existing):
        """Add shopping list items to the shopping list panel"""
        try:
            # Try to get the shopping list panel from the main app
            if hasattr(self.app, 'shopping_list_panel'):
                shopping_panel = self.app.shopping_list_panel
                
                if add_to_existing:
                    # Add to existing items
                    for item in shopping_list:
                        shopping_panel._add_shopping_item(item['item'], item['quantity'], item['category'])
                else:
                    # Clear existing and add new items
                    shopping_panel.clear_all()
                    for item in shopping_list:
                        shopping_panel._add_shopping_item(item['item'], item['quantity'], item['category'])
                
                # Switch to shopping list tab
                if hasattr(self.app, 'tab_widget'):
                    for i in range(self.app.tab_widget.count()):
                        if "Shopping" in self.app.tab_widget.tabText(i):
                            self.app.tab_widget.setCurrentIndex(i)
                            break
            else:
                QMessageBox.information(self, "Shopping List Generated", 
                                      f"Shopping list with {len(shopping_list)} items has been generated.\n"
                                      f"Switch to the Shopping List panel to view it.")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not add to shopping list panel: {str(e)}")
            QMessageBox.information(self, "Shopping List Generated", 
                                  f"Shopping list with {len(shopping_list)} items has been generated.")
    def export_menu(self):

        """Export menu plan to file"""

        try:

            from services.export_service import export_service

            

            # Get menu data from table

            menu_data = []

            for row in range(self.menu_table.rowCount()):

                day = self.menu_table.item(row, 0).text() if self.menu_table.item(row, 0) else ''

                breakfast = self.menu_table.item(row, 1).text() if self.menu_table.item(row, 1) else ''

                lunch = self.menu_table.item(row, 2).text() if self.menu_table.item(row, 2) else ''

                dinner = self.menu_table.item(row, 3).text() if self.menu_table.item(row, 3) else ''

                

                if day:  # Only include rows with day data

                    menu_data.append({

                        'day': day,

                        'breakfast': breakfast,

                        'lunch': lunch,

                        'dinner': dinner,

                        'week': self.week_combo.currentText()

                    })

            

            # Show export options dialog

            

            dialog = QDialog(self)

            dialog.setWindowTitle("Export Menu Plan")

            dialog.setModal(True)

            dialog.resize(300, 200)

            

            layout = QVBoxLayout(dialog)

            layout.addWidget(QLabel("Select export format:"))

            

            # Format options

            format_group = QButtonGroup()

            csv_radio = QRadioButton("CSV")

            pdf_radio = QRadioButton("PDF")

            

            csv_radio.setChecked(True)

            format_group.addButton(csv_radio, 1)

            format_group.addButton(pdf_radio, 2)

            

            layout.addWidget(csv_radio)

            layout.addWidget(pdf_radio)

            

            button_layout = QHBoxLayout()

            export_btn = QPushButton("Export")

            cancel_btn = QPushButton("Cancel")

            

            export_btn.clicked.connect(dialog.accept)

            cancel_btn.clicked.connect(dialog.reject)

            

            button_layout.addWidget(export_btn)

            button_layout.addWidget(cancel_btn)

            layout.addLayout(button_layout)

            

            if dialog.exec() == QDialog.Accepted:

                selected_format = format_group.checkedId()

                if selected_format == 1:

                    export_service.export_data(self, menu_data, 'csv', "Menu Plan")

                elif selected_format == 2:

                    export_service.export_data(self, menu_data, 'pdf', "Menu Plan")

                    

        except ImportError:

            QMessageBox.information(self, "Export Menu Plan", 

                "Export functionality will be implemented here.\n\n"

                "Features will include:\n"

                "�� � CSV export\n"

                "�� � PDF menu plan\n"

                "�� � Weekly meal schedule\n"

                "�� � Shopping list integration")

        except Exception as e:

            QMessageBox.critical(self, "Export Error", f"Failed to export menu plan: {str(e)}")

    

    def import_menu(self):

        """Import menu plan from file"""

        from PySide6.QtWidgets import QFileDialog

        

        # Create import dialog

        dialog = QDialog(self)

        dialog.setWindowTitle("Import Menu Plan")

        dialog.setModal(True)

        dialog.resize(500, 400)

        

        layout = QVBoxLayout(dialog)

        

        # Header

        header_label = QLabel("Import Menu Plan")

        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")

        layout.addWidget(header_label)

        

        # File type selection

        type_group = QGroupBox("File Type")

        type_layout = QVBoxLayout(type_group)

        

        self.csv_radio = QRadioButton("CSV File")

        self.csv_radio.setChecked(True)

        self.excel_radio = QRadioButton("Excel File")

        self.json_radio = QRadioButton("JSON File")

        

        type_layout.addWidget(self.csv_radio)

        type_layout.addWidget(self.excel_radio)

        type_layout.addWidget(self.json_radio)

        

        layout.addWidget(type_group)

        

        # File selection

        file_group = QGroupBox("File Selection")

        file_layout = QVBoxLayout(file_group)

        

        file_path_layout = QHBoxLayout()

        file_path_layout.addWidget(QLabel("File:"))

        self.file_path_edit = QLineEdit()

        self.file_path_edit.setPlaceholderText("Select file to import...")

        file_path_layout.addWidget(self.file_path_edit)

        

        browse_btn = QPushButton("Browse...")

        browse_btn.clicked.connect(self.browse_menu_import_file)

        file_path_layout.addWidget(browse_btn)

        

        file_layout.addLayout(file_path_layout)

        layout.addWidget(file_group)

        

        # Import options

        options_group = QGroupBox("Import Options")

        options_layout = QVBoxLayout(options_group)

        

        # Week assignment

        week_layout = QHBoxLayout()

        week_layout.addWidget(QLabel("Target Week:"))

        self.target_week_combo = QComboBox()

        self.target_week_combo.addItems([

            "This Week", "Next Week", "Week 1", "Week 2", "Week 3", "Week 4"

        ])

        week_layout.addWidget(self.target_week_combo)

        options_layout.addLayout(week_layout)

        

        # Duplicate handling

        duplicate_layout = QHBoxLayout()

        duplicate_layout.addWidget(QLabel("Duplicate Handling:"))

        self.duplicate_combo = QComboBox()

        self.duplicate_combo.addItems([

            "Skip duplicates",

            "Update existing",

            "Replace all meals"

        ])

        duplicate_layout.addWidget(self.duplicate_combo)

        options_layout.addLayout(duplicate_layout)

        

        layout.addWidget(options_group)

        

        # Buttons

        button_layout = QHBoxLayout()

        import_btn = QPushButton("Import Menu")

        cancel_btn = QPushButton("Cancel")

        button_layout.addWidget(import_btn)

        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        

        # Connect signals

        import_btn.clicked.connect(dialog.accept)

        cancel_btn.clicked.connect(dialog.reject)

        

        if dialog.exec() == QDialog.Accepted:

            self.perform_menu_import()

    

    def browse_menu_import_file(self):

        """Browse for menu import file"""

        from PySide6.QtWidgets import QFileDialog

        

        if self.csv_radio.isChecked():

            file_filter = "CSV Files (*.csv);;All Files (*)"

        elif self.excel_radio.isChecked():

            file_filter = "Excel Files (*.xlsx *.xls);;All Files (*)"

        elif self.json_radio.isChecked():

            file_filter = "JSON Files (*.json);;All Files (*)"

        else:

            file_filter = "All Files (*)"

        

        file_path, _ = QFileDialog.getOpenFileName(

            self, "Select Menu File", "", file_filter

        )

        

        if file_path:

            self.file_path_edit.setText(file_path)

    

    def perform_menu_import(self):

        """Perform the menu import"""

        try:

            file_path = self.file_path_edit.text().strip()

            target_week = self.target_week_combo.currentText()

            duplicate_handling = self.duplicate_combo.currentText()

            

            if not file_path:

                QMessageBox.warning(self, "Validation Error", "Please select a file to import.")

                return

            

            if self.csv_radio.isChecked():

                self.import_menu_from_csv(file_path, target_week, duplicate_handling)

            elif self.excel_radio.isChecked():

                self.import_menu_from_excel(file_path, target_week, duplicate_handling)

            elif self.json_radio.isChecked():

                self.import_menu_from_json(file_path, target_week, duplicate_handling)

            

            # Refresh the menu display

            self.load_week_menu()

            

        except Exception as e:

            QMessageBox.critical(self, "Import Error", f"Failed to import menu plan: {str(e)}")

    

    def import_menu_from_csv(self, file_path, target_week, duplicate_handling):

        """Import menu plan from CSV file"""

        import csv

        from utils.db import get_connection

        from datetime import datetime, timedelta

        

        conn = get_connection()

        

        try:

            with open(file_path, 'r', encoding='utf-8') as file:

                reader = csv.DictReader(file)

                imported_count = 0

                

                for row in reader:

                    day = row.get('day', '').strip()

                    breakfast = row.get('breakfast', '').strip()

                    lunch = row.get('lunch', '').strip()

                    dinner = row.get('dinner', '').strip()

                    week = row.get('week', target_week).strip()

                    

                    if not day:

                        continue

                    

                    # Convert day name to date (simplified)

                    date = self._get_date_for_day(day, target_week)

                    

                    # Handle duplicates

                    if duplicate_handling == "Skip duplicates":

                        existing = conn.execute(

                            "SELECT id FROM menu_plan WHERE date = ? AND meal_type = 'breakfast'",

                            (date,)

                        ).fetchone()

                        if existing:

                            continue

                    

                    # Insert meals for the day

                    meals = [

                        ('breakfast', breakfast),

                        ('lunch', lunch),

                        ('dinner', dinner)

                    ]

                    

                    for meal_type, recipe in meals:

                        if recipe:  # Only insert if recipe is not empty

                            conn.execute("""

                                INSERT OR REPLACE INTO menu_plan 

                                (date, meal_type, recipe_id, title, notes)

                                VALUES (?, ?, ?, ?, ?)

                            """, (date, meal_type, None, recipe, f"Imported from {file_path}"))

                            imported_count += 1

                

                conn.commit()

                QMessageBox.information(self, "Import Complete", 

                                      f"Successfully imported {imported_count} meals from CSV file.")

        

        except Exception as e:

            conn.rollback()

            raise e

        finally:

            conn.close()

    

    def import_menu_from_excel(self, file_path, target_week, duplicate_handling):

        """Import menu plan from Excel file"""

        QMessageBox.information(self, "Excel Import", 

                               f"Excel import would process {file_path}.\n\n"

                               "This feature would:\n"

                               "�� � Parse Excel workbook\n"

                               "�� � Extract menu data\n"

                               "�� � Handle multiple sheets\n"

                               "�� � Validate data format")

    

    def import_menu_from_json(self, file_path, target_week, duplicate_handling):

        """Import menu plan from JSON file"""

        QMessageBox.information(self, "JSON Import", 

                               f"JSON import would process {file_path}.\n\n"

                               "This feature would:\n"

                               "�� � Parse JSON structure\n"

                               "�� � Extract menu data\n"

                               "�� � Handle nested objects\n"

                               "�� � Validate schema")

    

    def push_recipes_to_mobile(self):
        """Push selected recipes to mobile app for offline viewing"""
        try:
            # Get all recipes from the current menu
            recipes_to_push = self._extract_recipes_from_menu()
            
            if not recipes_to_push:
                QMessageBox.information(self, "No Recipes", 
                                      "No recipes found in the current menu to push to mobile.")
                return
            
            # Show recipe selection dialog
            selected_recipes = self._show_recipe_selection_dialog(recipes_to_push)
            
            if not selected_recipes:
                return
            
            # Push recipes to mobile sync service
            success_count = self._push_recipes_to_mobile_sync(selected_recipes)
            
            if success_count > 0:
                QMessageBox.information(self, "Success", 
                                      f"Successfully pushed {success_count} recipes to mobile app for offline viewing!")
            else:
                QMessageBox.warning(self, "Push Failed", 
                                  "Failed to push recipes to mobile app. Please check mobile sync service.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error pushing recipes to mobile: {str(e)}")
    
    def _extract_recipes_from_menu(self):
        """Extract all unique recipes from the current menu"""
        recipes = set()
        
        for row in range(self.menu_table.rowCount()):
            for col in range(1, 4):  # Skip day column, check breakfast, lunch, dinner
                item = self.menu_table.item(row, col)
                if item and item.text().strip():
                    recipe_name = item.text().strip()
                    if recipe_name and recipe_name not in ["", "None", "N/A"]:
                        recipes.add(recipe_name)
        
        return list(recipes)
    
    def _show_recipe_selection_dialog(self, recipes):
        """Show dialog to select which recipes to push to mobile"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Recipes for Mobile")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel("Select recipes to push to mobile app for offline viewing:")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Recipe selection list
        from PySide6.QtWidgets import QListWidget, QListWidgetItem
        
        self.recipe_list = QListWidget()
        self.recipe_list.setSelectionMode(QListWidget.MultiSelection)
        
        for recipe in recipes:
            item = QListWidgetItem(f"🍽️ {recipe}")
            item.setData(Qt.UserRole, recipe)
            item.setSelected(True)  # Select all by default
            self.recipe_list.addItem(item)
        
        layout.addWidget(self.recipe_list)
        
        # Options
        options_group = QGroupBox("Push Options")
        options_layout = QVBoxLayout(options_group)
        
        self.include_ingredients_check = QCheckBox("Include detailed ingredients")
        self.include_ingredients_check.setChecked(True)
        options_layout.addWidget(self.include_ingredients_check)
        
        self.include_instructions_check = QCheckBox("Include cooking instructions")
        self.include_instructions_check.setChecked(True)
        options_layout.addWidget(self.include_instructions_check)
        
        self.include_nutrition_check = QCheckBox("Include nutritional information")
        self.include_nutrition_check.setChecked(False)
        options_layout.addWidget(self.include_nutrition_check)
        
        self.optimize_for_mobile_check = QCheckBox("Optimize for mobile viewing")
        self.optimize_for_mobile_check.setChecked(True)
        options_layout.addWidget(self.optimize_for_mobile_check)
        
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(lambda: self._select_all_recipes(True))
        
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(lambda: self._select_all_recipes(False))
        
        push_btn = QPushButton("Push to Mobile")
        push_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(select_none_btn)
        button_layout.addStretch()
        button_layout.addWidget(push_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        if dialog.exec() == QDialog.Accepted:
            selected_recipes = []
            for i in range(self.recipe_list.count()):
                item = self.recipe_list.item(i)
                if item.isSelected():
                    recipe_name = item.data(Qt.UserRole)
                    selected_recipes.append({
                        'name': recipe_name,
                        'include_ingredients': self.include_ingredients_check.isChecked(),
                        'include_instructions': self.include_instructions_check.isChecked(),
                        'include_nutrition': self.include_nutrition_check.isChecked(),
                        'optimize_for_mobile': self.optimize_for_mobile_check.isChecked()
                    })
            return selected_recipes
        
        return []
    
    def _select_all_recipes(self, select_all):
        """Select or deselect all recipes in the list"""
        for i in range(self.recipe_list.count()):
            item = self.recipe_list.item(i)
            item.setSelected(select_all)
    
    def _push_recipes_to_mobile_sync(self, selected_recipes):
        """Push recipes to mobile sync service"""
        try:
            # Import mobile sync service
            from services.mobile_sync import get_mobile_sync_service
            
            mobile_sync = get_mobile_sync_service()
            success_count = 0
            
            for recipe_data in selected_recipes:
                # Get full recipe details from database
                recipe_details = self._get_recipe_details(recipe_data['name'])
                
                if recipe_details:
                    # Create mobile-optimized recipe format
                    mobile_recipe = self._create_mobile_recipe_format(recipe_details, recipe_data)
                    
                    # Add to mobile sync service
                    mobile_sync.add_recipe_to_mobile(mobile_recipe)
                    success_count += 1
            
            return success_count
            
        except ImportError:
            # Fallback if mobile sync service not available
            QMessageBox.warning(self, "Mobile Sync Unavailable", 
                              "Mobile sync service is not available. Please ensure mobile companion is properly configured.")
            return 0
        except Exception as e:
            print(f"Error pushing recipes to mobile sync: {str(e)}")
            return 0
    
    def _get_recipe_details(self, recipe_name):
        """Get full recipe details from database"""
        try:
            from utils.db import get_connection
            
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, ingredients, instructions, 
                       prep_time, cook_time, servings, category, 
                       difficulty, image_path, nutrition_info, notes
                FROM recipes 
                WHERE name = ?
            """, (recipe_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'description': result[2],
                    'ingredients': result[3],
                    'instructions': result[4],
                    'prep_time': result[5],
                    'cook_time': result[6],
                    'servings': result[7],
                    'category': result[8],
                    'difficulty': result[9],
                    'image_path': result[10],
                    'nutrition_info': result[11],
                    'notes': result[12]
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting recipe details: {str(e)}")
            return None
    
    def _create_mobile_recipe_format(self, recipe_details, push_options):
        """Create mobile-optimized recipe format"""
        mobile_recipe = {
            'id': f"mobile_{recipe_details['id']}",
            'name': recipe_details['name'],
            'description': recipe_details['description'],
            'category': recipe_details['category'],
            'prep_time': recipe_details['prep_time'],
            'cook_time': recipe_details['cook_time'],
            'servings': recipe_details['servings'],
            'difficulty': recipe_details['difficulty'],
            'pushed_at': self._get_current_timestamp(),
            'mobile_optimized': push_options['optimize_for_mobile']
        }
        
        # Add ingredients if requested
        if push_options['include_ingredients']:
            mobile_recipe['ingredients'] = recipe_details['ingredients']
        
        # Add instructions if requested
        if push_options['include_instructions']:
            mobile_recipe['instructions'] = recipe_details['instructions']
        
        # Add nutrition info if requested
        if push_options['include_nutrition'] and recipe_details['nutrition_info']:
            mobile_recipe['nutrition_info'] = recipe_details['nutrition_info']
        
        # Add notes
        if recipe_details['notes']:
            mobile_recipe['notes'] = recipe_details['notes']
        
        # Add image path if available
        if recipe_details['image_path']:
            mobile_recipe['image_path'] = recipe_details['image_path']
        
        return mobile_recipe
    
    def _get_current_timestamp(self):
        """Get current timestamp for mobile recipe"""
        from datetime import datetime
        return datetime.now().isoformat()

    def _get_date_for_day(self, day_name, week):

        """Get date for a given day name and week"""

        # Simplified implementation - in real app, would calculate actual dates

        day_mapping = {

            'Monday': '2024-01-15',

            'Tuesday': '2024-01-16',

            'Wednesday': '2024-01-17',

            'Thursday': '2024-01-18',

            'Friday': '2024-01-19',

            'Saturday': '2024-01-20',

            'Sunday': '2024-01-21'

        }

        return day_mapping.get(day_name, '2024-01-15')

