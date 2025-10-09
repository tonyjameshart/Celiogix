# path: panels/shopping_list_panel_pyside6.py
"""
Shopping List Panel for PySide6 Application
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QMessageBox, QDialog, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from panels.base_panel import BasePanel
from panels.context_menu_mixin import ShoppingListContextMenuMixin


class ShoppingListPanel(ShoppingListContextMenuMixin, BasePanel):
    """Shopping list panel for PySide6"""
    
    def __init__(self, master=None, app=None):
        super().__init__(master, app)
    
    def setup_ui(self):
        """Set up the shopping list panel UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Add item section
        add_layout = QHBoxLayout()
        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("Enter item to add...")
        self.item_input.returnPressed.connect(self.add_item)
        add_layout.addWidget(QLabel("Add Item:"))
        add_layout.addWidget(self.item_input)
        
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Qty")
        self.quantity_input.setMaximumWidth(80)
        add_layout.addWidget(QLabel("Qty:"))
        add_layout.addWidget(self.quantity_input)
        
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
        add_layout.addWidget(QLabel("Store:"))
        add_layout.addWidget(self.store_combo)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Produce", "Meat & Seafood", "Dairy & Eggs", "Pantry", 
            "Frozen", "Bakery (GF)", "Beverages", "Health & Beauty", "Other"
        ])
        add_layout.addWidget(QLabel("Category:"))
        add_layout.addWidget(self.category_combo)
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_item)
        add_layout.addWidget(add_btn)
        
        main_layout.addLayout(add_layout)
        
        # Store filter and organization
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Store:"))
        self.store_filter = QComboBox()
        self.store_filter.addItems(["All Stores", "Grocery Store", "Health Food Store", "Farmers Market", "Bulk Store", "Online Order", "Specialty Store", "Other"])
        self.store_filter.currentTextChanged.connect(self.filter_by_store)
        filter_layout.addWidget(self.store_filter)
        
        organize_btn = QPushButton("Organize by Store")
        organize_btn.clicked.connect(self.organize_by_store)
        filter_layout.addWidget(organize_btn)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        # Shopping list table
        self.shopping_table = QTableWidget()
        self.shopping_table.setColumnCount(5)
        self.shopping_table.setHorizontalHeaderLabels(["Store", "Item", "Quantity", "Category", "Purchased"])
        
        # Set up auto-sizing columns with minimum width
        header = self.shopping_table.horizontalHeader()
        header.setStretchLastSection(False)  # Disable stretch last section
        
        # Set resize mode to auto-size based on content with minimum width
        for col in range(5):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
            # Set minimum width to 20% of table width
            header.setMinimumSectionSize(int(self.shopping_table.width() * 0.2) if self.shopping_table.width() > 0 else 100)
        
        self.shopping_table.setAlternatingRowColors(True)
        self.shopping_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.shopping_table.itemChanged.connect(self.on_item_changed)
        
        # Apply custom delegate to suppress selection borders
        from utils.custom_delegates import CleanSelectionDelegate
        self.shopping_table.setItemDelegate(CleanSelectionDelegate())
        
        # Apply same styling as pantry table
        self.shopping_table.setStyleSheet("""
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
        
        # Connect resize event to update minimum section sizes
        self.shopping_table.resizeEvent = self.on_table_resize
        
        main_layout.addWidget(self.shopping_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.remove_btn = QPushButton("Remove Item")
        self.remove_btn.clicked.connect(self.remove_item)
        self.remove_btn.setEnabled(False)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        
        self.print_btn = QPushButton("Print List")
        self.print_btn.clicked.connect(self.print_list)
        
        self.export_btn = QPushButton("Export List")
        self.export_btn.clicked.connect(self.export_shopping_list)
        
        self.import_btn = QPushButton("Import List")
        self.import_btn.clicked.connect(self.import_shopping_list)
        
        button_layout.addWidget(self.remove_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.print_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Connect selection changes
        self.shopping_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # Load initial data
        self.load_shopping_list()

    def refresh(self):
        """Refresh panel data"""
        self.load_shopping_list()
    
    def load_shopping_list(self):
        """Load shopping list from database"""
        try:
            from utils.db import get_connection
            
            db = get_connection()
            cursor = db.cursor()
            
            # Load shopping list items from database
            cursor.execute("""
                SELECT store, name, '1', category, purchased, notes, created_at
                FROM shopping_list 
                ORDER BY id DESC
            """)
            
            items = cursor.fetchall()
            
            # Clear existing data
            self.shopping_table.setRowCount(len(items))
            
            for row, (store, item_name, quantity, category, purchased, notes, created_at) in enumerate(items):
                self.shopping_table.setItem(row, 0, QTableWidgetItem(store or ""))
                self.shopping_table.setItem(row, 1, QTableWidgetItem(item_name or ""))
                self.shopping_table.setItem(row, 2, QTableWidgetItem(quantity or ""))
                self.shopping_table.setItem(row, 3, QTableWidgetItem(category or ""))
                
                # Create checkbox for purchased column
                purchased_item = QTableWidgetItem()
                purchased_item.setCheckState(Qt.Checked if purchased else Qt.Unchecked)
                purchased_item.setText("Yes" if purchased else "No")
                self.shopping_table.setItem(row, 4, purchased_item)
                
            
            # If no items in database, add sample items
            if len(items) == 0:
                self._load_sample_shopping_items()
                
        except Exception as e:
            print(f"Error loading shopping list from database: {e}")
            # Fallback to sample items
            self._load_sample_shopping_items()
    
    def _load_sample_shopping_items(self):
        """Load sample shopping items when database is empty"""
        sample_items = [
            ("Health Food Store", "Gluten-Free Bread", "1 loaf", "Bakery (GF)", False),
            ("Grocery Store", "Almond Milk", "2 cartons", "Dairy & Eggs", False),
            ("Bulk Store", "Quinoa", "1 bag", "Pantry", False),
            ("Farmers Market", "Fresh Spinach", "1 bunch", "Produce", True),
            ("Grocery Store", "Chicken Breast", "2 lbs", "Meat & Seafood", False)
        ]
        
        self.shopping_table.setRowCount(len(sample_items))
        for row, (store, item, quantity, category, purchased) in enumerate(sample_items):
            self.shopping_table.setItem(row, 0, QTableWidgetItem(store))
            self.shopping_table.setItem(row, 1, QTableWidgetItem(item))
            self.shopping_table.setItem(row, 2, QTableWidgetItem(quantity))
            self.shopping_table.setItem(row, 3, QTableWidgetItem(category))
            
            # Create checkbox for purchased column
            purchased_item = QTableWidgetItem()
            purchased_item.setCheckState(Qt.Checked if purchased else Qt.Unchecked)
            purchased_item.setText("Yes" if purchased else "No")
            self.shopping_table.setItem(row, 4, purchased_item)
    
    def add_item(self):
        """Add item to shopping list"""
        item_text = self.item_input.text().strip()
        quantity_text = self.quantity_input.text().strip() or "1"
        store = self.store_combo.currentText()
        category = self.category_combo.currentText()
        
        if item_text:
            # Save to database first
            item_id = self._save_shopping_item_to_database(item_text, quantity_text, store, category)
            if item_id:
                # Clear inputs
                self.item_input.clear()
                self.quantity_input.clear()
                
                # Refresh the display to show the new item
                self.refresh()
                
                # Auto-organize by store if enabled
                self.organize_by_store()
            else:
                QMessageBox.warning(self, "Error", "Failed to save item to database.")
    
    def filter_by_store(self):
        """Filter shopping list by selected store"""
        selected_store = self.store_filter.currentText()
        
        if selected_store == "All Stores":
            # Show all rows
            for row in range(self.shopping_table.rowCount()):
                self.shopping_table.setRowHidden(row, False)
        else:
            # Hide rows that don't match the selected store
            for row in range(self.shopping_table.rowCount()):
                store_item = self.shopping_table.item(row, 0)
                if store_item and store_item.text() == selected_store:
                    self.shopping_table.setRowHidden(row, False)
                else:
                    self.shopping_table.setRowHidden(row, True)
    
    def organize_by_store(self):
        """Organize shopping list by store, then by category"""
        # Get all items
        items = []
        for row in range(self.shopping_table.rowCount()):
            store_item = self.shopping_table.item(row, 0)
            item_item = self.shopping_table.item(row, 1)
            quantity_item = self.shopping_table.item(row, 2)
            category_item = self.shopping_table.item(row, 3)
            purchased_item = self.shopping_table.item(row, 4)
            
            if all([store_item, item_item, quantity_item, category_item, purchased_item]):
                items.append({
                    'store': store_item.text(),
                    'item': item_item.text(),
                    'quantity': quantity_item.text(),
                    'category': category_item.text(),
                    'purchased': purchased_item.text(),
                    'check_state': purchased_item.checkState()
                })
        
        # Sort by store, then by category
        items.sort(key=lambda x: (x['store'], x['category'], x['item']))
        
        # Clear table and re-add sorted items
        self.shopping_table.setRowCount(0)
        
        for item_data in items:
            row = self.shopping_table.rowCount()
            self.shopping_table.insertRow(row)
            
            self.shopping_table.setItem(row, 0, QTableWidgetItem(item_data['store']))
            self.shopping_table.setItem(row, 1, QTableWidgetItem(item_data['item']))
            self.shopping_table.setItem(row, 2, QTableWidgetItem(item_data['quantity']))
            self.shopping_table.setItem(row, 3, QTableWidgetItem(item_data['category']))
            
            # Create checkbox for purchased column
            purchased_item = QTableWidgetItem()
            purchased_item.setCheckState(item_data['check_state'])
            purchased_item.setText(item_data['purchased'])
            self.shopping_table.setItem(row, 4, purchased_item)
    
    def _add_shopping_item(self, item, quantity, category, store="Grocery Store"):
        """Add shopping item programmatically (used by menu planning)"""
        row = self.shopping_table.rowCount()
        self.shopping_table.insertRow(row)
        self.shopping_table.setItem(row, 0, QTableWidgetItem(store))
        self.shopping_table.setItem(row, 1, QTableWidgetItem(item))
        self.shopping_table.setItem(row, 2, QTableWidgetItem(quantity))
        self.shopping_table.setItem(row, 3, QTableWidgetItem(category))
        
        # Create checkbox for purchased column
        purchased_item = QTableWidgetItem()
        purchased_item.setCheckState(Qt.Unchecked)
        purchased_item.setText("No")
        self.shopping_table.setItem(row, 4, purchased_item)
    
    def on_item_changed(self, item):
        """Handle item changes in the table"""
        if item.column() == 4:  # Purchased column (now column 4)
            if item.checkState() == Qt.Checked:
                item.setText("Yes")
            else:
                item.setText("No")
    
    def on_table_resize(self, event):
        """Handle table resize to update minimum section sizes"""
        # Update minimum section size to 20% of table width
        header = self.shopping_table.horizontalHeader()
        min_width = int(self.shopping_table.width() * 0.2) if self.shopping_table.width() > 0 else 100
        header.setMinimumSectionSize(min_width)
        
        # Call the original resize event
        QTableWidget.resizeEvent(self.shopping_table, event)
    
    def on_selection_changed(self):
        """Handle table selection changes"""
        has_selection = len(self.shopping_table.selectedItems()) > 0
        self.remove_btn.setEnabled(has_selection)
    
    def edit_item(self):
        """Edit selected shopping list item"""
        current_row = self.shopping_table.currentRow()
        if current_row >= 0:
            try:
                from utils.edit_dialogs import ShoppingItemEditDialog
                
                # Get current item data
                item_data = {
                    'store': self.shopping_table.item(current_row, 0).text(),
                    'item': self.shopping_table.item(current_row, 1).text(),
                    'quantity': self.shopping_table.item(current_row, 2).text(),
                    'category': self.shopping_table.item(current_row, 3).text(),
                    'priority': 'Medium',
                    'notes': ''
                }
                
                # Open edit dialog
                dialog = ShoppingItemEditDialog(self)
                dialog.set_data(item_data)
                
                if dialog.exec() == QDialog.Accepted:
                    new_data = dialog.get_data()
                    
                    # Update table with new data
                    self.shopping_table.setItem(current_row, 0, QTableWidgetItem(new_data['store']))
                    self.shopping_table.setItem(current_row, 1, QTableWidgetItem(new_data['item']))
                    self.shopping_table.setItem(current_row, 2, QTableWidgetItem(new_data['quantity']))
                    self.shopping_table.setItem(current_row, 3, QTableWidgetItem(new_data['category']))
                    
                    QMessageBox.information(self, "Success", "Shopping item updated successfully!")
                    
            except ImportError:
                item_name = self.shopping_table.item(current_row, 1).text()  # Item is now in column 1
                QMessageBox.information(self, "Edit Item", f"Edit functionality for '{item_name}' will be implemented here.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to edit item: {str(e)}")
    
    def remove_item(self):
        """Remove selected item from shopping list"""
        current_row = self.shopping_table.currentRow()
        if current_row >= 0:
            item_name = self.shopping_table.item(current_row, 1).text()  # Item is now in column 1
            reply = QMessageBox.question(self, "Remove Item", 
                                       f"Are you sure you want to remove '{item_name}' from the shopping list?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.shopping_table.removeRow(current_row)
    
    def clear_all(self):
        """Clear all items from shopping list"""
        reply = QMessageBox.question(self, "Clear All", 
                                   "Are you sure you want to clear all items from the shopping list?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.shopping_table.setRowCount(0)
    
    def print_list(self):
        """Print shopping list"""
        try:
            from services.export_service import export_service
            
            # Get shopping list data from table
            shopping_data = []
            for row in range(self.shopping_table.rowCount()):
                item_data = {
                    'item': self.shopping_table.item(row, 0).text() if self.shopping_table.item(row, 0) else '',
                    'quantity': self.shopping_table.item(row, 1).text() if self.shopping_table.item(row, 1) else '',
                    'category': self.shopping_table.item(row, 2).text() if self.shopping_table.item(row, 2) else '',
                    'priority': 'Medium',
                    'notes': ''
                }
                shopping_data.append(item_data)
            
            # Show export options dialog
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Export Shopping List")
            dialog.setModal(True)
            dialog.resize(300, 200)
            
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Select export format:"))
            
            button_group = QButtonGroup()
            csv_radio = QRadioButton("CSV (for spreadsheets)")
            csv_radio.setChecked(True)
            pdf_radio = QRadioButton("PDF (for printing)")
            html_radio = QRadioButton("HTML (web view)")
            
            button_group.addButton(csv_radio, 0)
            button_group.addButton(pdf_radio, 1)
            button_group.addButton(html_radio, 2)
            
            layout.addWidget(csv_radio)
            layout.addWidget(pdf_radio)
            layout.addWidget(html_radio)
            
            button_layout = QHBoxLayout()
            export_btn = QPushButton("Export")
            cancel_btn = QPushButton("Cancel")
            
            export_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(export_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            if dialog.exec() == QDialog.Accepted:
                selected_format = button_group.checkedId()
                if selected_format == 0:
                    export_service.export_shopping_list(self, shopping_data)
                elif selected_format == 1:
                    export_service.export_data(self, shopping_data, 'pdf', "Shopping List")
                elif selected_format == 2:
                    export_service.export_data(self, shopping_data, 'html', "Shopping List")
                    
        except ImportError:
            QMessageBox.information(self, "Print List", "Print functionality will be implemented here.")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export shopping list: {str(e)}")
    def export_shopping_list(self):

        """Export shopping list to file"""

        try:

            from services.export_service import export_service

            

            # Get shopping list data from table

            shopping_data = []

            for row in range(self.shopping_table.rowCount()):

                item_data = {

                    'store': self.shopping_table.item(row, 0).text() if self.shopping_table.item(row, 0) else '',

                    'item': self.shopping_table.item(row, 1).text() if self.shopping_table.item(row, 1) else '',

                    'quantity': self.shopping_table.item(row, 2).text() if self.shopping_table.item(row, 2) else '',

                    'category': self.shopping_table.item(row, 3).text() if self.shopping_table.item(row, 3) else '',

                    'purchased': 'Yes' if self.shopping_table.item(row, 4).checkState() == Qt.Checked else 'No'

                }

                shopping_data.append(item_data)

            

            # Show export options dialog

            

            dialog = QDialog(self)

            dialog.setWindowTitle("Export Shopping List")

            dialog.setModal(True)

            dialog.resize(300, 200)

            

            layout = QVBoxLayout(dialog)

            layout.addWidget(QLabel("Select export format:"))

            

            # Format options

            format_group = QButtonGroup()

            csv_radio = QRadioButton("CSV")

            pdf_radio = QRadioButton("PDF")

            html_radio = QRadioButton("HTML")

            

            csv_radio.setChecked(True)

            format_group.addButton(csv_radio, 1)

            format_group.addButton(pdf_radio, 2)

            format_group.addButton(html_radio, 3)

            

            layout.addWidget(csv_radio)

            layout.addWidget(pdf_radio)

            layout.addWidget(html_radio)

            

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

                    export_service.export_data(self, shopping_data, 'csv', "Shopping List")

                elif selected_format == 2:

                    export_service.export_data(self, shopping_data, 'pdf', "Shopping List")

                elif selected_format == 3:

                    export_service.export_data(self, shopping_data, 'html', "Shopping List")

                    

        except ImportError:

            QMessageBox.information(self, "Export Shopping List", 

                "Export functionality will be implemented here.\n\n"

                "Features will include:\n"

                "�� � CSV export\n"

                "�� � PDF shopping list\n"

                "�� � HTML printable format\n"

                "�� � Organized by store")

        except Exception as e:

            QMessageBox.critical(self, "Export Error", f"Failed to export shopping list: {str(e)}")

    

    def import_shopping_list(self):

        """Import shopping list from file"""

        from PySide6.QtWidgets import QFileDialog

        

        # Create import dialog

        dialog = QDialog(self)

        dialog.setWindowTitle("Import Shopping List")

        dialog.setModal(True)

        dialog.resize(500, 400)

        

        layout = QVBoxLayout(dialog)

        

        # Header

        header_label = QLabel("Import Shopping List")

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

        browse_btn.clicked.connect(self.browse_shopping_import_file)

        file_path_layout.addWidget(browse_btn)

        

        file_layout.addLayout(file_path_layout)

        layout.addWidget(file_group)

        

        # Import options

        options_group = QGroupBox("Import Options")

        options_layout = QVBoxLayout(options_group)

        

        # Duplicate handling

        duplicate_layout = QHBoxLayout()

        duplicate_layout.addWidget(QLabel("Duplicate Handling:"))

        self.duplicate_combo = QComboBox()

        self.duplicate_combo.addItems([

            "Skip duplicates",

            "Update existing",

            "Create new entries"

        ])

        duplicate_layout.addWidget(self.duplicate_combo)

        options_layout.addLayout(duplicate_layout)

        

        # Store assignment

        store_layout = QHBoxLayout()

        store_layout.addWidget(QLabel("Default Store:"))

        self.default_store_edit = QLineEdit()

        self.default_store_edit.setPlaceholderText("e.g., Grocery Store, etc.")

        store_layout.addWidget(self.default_store_edit)

        options_layout.addLayout(store_layout)

        

        layout.addWidget(options_group)

        

        # Buttons

        button_layout = QHBoxLayout()

        import_btn = QPushButton("Import List")

        cancel_btn = QPushButton("Cancel")

        button_layout.addWidget(import_btn)

        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        

        # Connect signals

        import_btn.clicked.connect(dialog.accept)

        cancel_btn.clicked.connect(dialog.reject)

        

        if dialog.exec() == QDialog.Accepted:

            self.perform_shopping_import()

    

    def browse_shopping_import_file(self):

        """Browse for shopping list import file"""

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

            self, "Select Shopping List File", "", file_filter

        )

        

        if file_path:

            self.file_path_edit.setText(file_path)

    

    def perform_shopping_import(self):

        """Perform the shopping list import"""

        try:

            file_path = self.file_path_edit.text().strip()

            duplicate_handling = self.duplicate_combo.currentText()

            default_store = self.default_store_edit.text().strip() or "Grocery Store"

            

            if not file_path:

                QMessageBox.warning(self, "Validation Error", "Please select a file to import.")

                return

            

            if self.csv_radio.isChecked():

                self.import_shopping_from_csv(file_path, duplicate_handling, default_store)

            elif self.excel_radio.isChecked():

                self.import_shopping_from_excel(file_path, duplicate_handling, default_store)

            elif self.json_radio.isChecked():

                self.import_shopping_from_json(file_path, duplicate_handling, default_store)

            

            # Refresh the shopping list display

            self.load_shopping_list()

            

        except Exception as e:

            QMessageBox.critical(self, "Import Error", f"Failed to import shopping list: {str(e)}")

    

    def import_shopping_from_csv(self, file_path, duplicate_handling, default_store):

        """Import shopping list from CSV file"""

        import csv

        from utils.db import get_connection

        

        conn = get_connection()

        

        try:

            with open(file_path, 'r', encoding='utf-8') as file:

                reader = csv.DictReader(file)

                imported_count = 0

                

                for row in reader:

                    item = row.get('item', '').strip()

                    quantity = row.get('quantity', '').strip()

                    category = row.get('category', '').strip()

                    store = row.get('store', default_store).strip()

                    priority = row.get('priority', 'Medium').strip()

                    notes = row.get('notes', '').strip()

                    

                    if not item:

                        continue

                    

                    # Handle duplicates

                    if duplicate_handling == "Skip duplicates":

                        existing = conn.execute(

                            "SELECT id FROM shopping_list WHERE item_name = ? AND store = ?",

                            (item, store)

                        ).fetchone()

                        if existing:

                            continue

                    

                    # Insert item

                    conn.execute("""

                        INSERT OR REPLACE INTO shopping_list 

                        (item, quantity, category, store, priority, notes)

                        VALUES (?, ?, ?, ?, ?, ?)

                    """, (item, quantity, category, store, priority, notes))

                    imported_count += 1

                

                conn.commit()

                QMessageBox.information(self, "Import Complete", 

                                      f"Successfully imported {imported_count} items from CSV file.")

        

        except Exception as e:

            conn.rollback()

            raise e

        finally:

            conn.close()

    

    def import_shopping_from_excel(self, file_path, duplicate_handling, default_store):

        """Import shopping list from Excel file"""

        QMessageBox.information(self, "Excel Import", 

                               f"Excel import would process {file_path}.\n\n"

                               "This feature would:\n"

                               "�� � Parse Excel workbook\n"

                               "�� � Extract shopping items\n"

                               "�� � Handle multiple sheets\n"

                               "�� � Validate data format")

    

    def import_shopping_from_json(self, file_path, duplicate_handling, default_store):

        """Import shopping list from JSON file"""

        QMessageBox.information(self, "JSON Import", 

                               f"JSON import would process {file_path}.\n\n"

                               "This feature would:\n"

                               "�� � Parse JSON structure\n"

                               "�� � Extract shopping items\n"

                               "�� � Handle nested objects\n"

                               "�� � Validate schema")


    def _save_shopping_item_to_database(self, item_name, quantity, store, category):
        """Save shopping list item to database and return item ID"""
        try:
            from utils.db import get_connection
            
            db = get_connection()
            cursor = db.cursor()
            
            # Insert item
            cursor.execute("""
                INSERT INTO shopping_list (name, item_name, store, category, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (item_name, item_name, store, category))
            
            item_id = cursor.lastrowid
            db.commit()
            return item_id
            
        except Exception as e:
            print(f"Error saving shopping list item to database: {e}")
            return None
