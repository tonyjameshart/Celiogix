# path: panels/pantry_panel_pyside6.py
"""
Pantry Panel for PySide6 Application

Manages pantry inventory with gluten-free safety tracking.
"""

from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QDateEdit,
    QMessageBox, QSplitter, QFrame, QDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from panels.base_panel import BasePanel
from panels.context_menu_mixin import PantryContextMenuMixin


class PantryPanel(PantryContextMenuMixin, BasePanel):
    """Pantry management panel for PySide6"""
    
    def __init__(self, master=None, app=None):
        super().__init__(master, app)
    
    def setup_ui(self):
        """Set up the pantry panel UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # UPC Scanning section
        upc_layout = QHBoxLayout()
        upc_layout.addWidget(QLabel("UPC Code:"))
        self.upc_input = QLineEdit()
        self.upc_input.setPlaceholderText("Enter UPC code or scan barcode...")
        self.upc_input.returnPressed.connect(self.scan_upc)
        upc_layout.addWidget(self.upc_input)
        
        self.scan_btn = QPushButton("Scan UPC")
        self.scan_btn.clicked.connect(self.scan_upc)
        upc_layout.addWidget(self.scan_btn)
        
        self.bulk_import_btn = QPushButton("Bulk Import")
        self.bulk_import_btn.clicked.connect(self.bulk_import_items)
        upc_layout.addWidget(self.bulk_import_btn)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_pantry)
        upc_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(upc_layout)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left side - Add/Edit form
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        # Add item form
        form_group = QGroupBox("Add/Edit Item")
        form_group_layout = QVBoxLayout(form_group)
        
        # Item name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Item Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter item name")
        name_layout.addWidget(self.name_edit)
        form_group_layout.addLayout(name_layout)
        
        # Category
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Grains & Flours",
            "Baking",
            "Canned Goods",
            "Dairy",
            "Meat & Seafood",
            "Fruits & Vegetables",
            "Spices & Seasonings",
            "Snacks",
            "Beverages",
            "Other"
        ])
        category_layout.addWidget(self.category_combo)
        form_group_layout.addLayout(category_layout)
        
        # Quantity
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Quantity:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(0, 9999)
        self.quantity_spin.setValue(1)
        quantity_layout.addWidget(self.quantity_spin)
        form_group_layout.addLayout(quantity_layout)
        
        # Unit
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel("Unit:"))
        self.unit_combo = QComboBox()
        self.unit_combo.addItems([
            "pieces", "cups", "tbsp", "tsp", "lbs", "oz", "grams", 
            "ml", "liters", "cans", "boxes", "bags"
        ])
        unit_layout.addWidget(self.unit_combo)
        form_group_layout.addLayout(unit_layout)
        
        # Expiration date
        exp_layout = QHBoxLayout()
        exp_layout.addWidget(QLabel("Expiration:"))
        self.exp_date = QDateEdit()
        self.exp_date.setDate(QDate.currentDate().addDays(30))
        exp_layout.addWidget(self.exp_date)
        form_group_layout.addLayout(exp_layout)
        
        # Gluten-free status
        gf_layout = QHBoxLayout()
        gf_layout.addWidget(QLabel("Gluten-Free:"))
        self.gf_combo = QComboBox()
        self.gf_combo.addItems(["Yes", "No", "Unknown"])
        gf_layout.addWidget(self.gf_combo)
        form_group_layout.addLayout(gf_layout)
        
        # Notes
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Additional notes...")
        notes_layout.addWidget(self.notes_edit)
        form_group_layout.addLayout(notes_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Item")
        add_button.clicked.connect(self.add_item)
        button_layout.addWidget(add_button)
        
        update_button = QPushButton("Update Item")
        update_button.clicked.connect(self.update_item)
        button_layout.addWidget(update_button)
        
        clear_button = QPushButton("Clear Form")
        clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(clear_button)
        
        form_group_layout.addLayout(button_layout)
        form_layout.addWidget(form_group)
        
        splitter.addWidget(form_widget)
        
        # Right side - Item list
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        # Item list
        list_group = QGroupBox("Pantry Items")
        list_group_layout = QVBoxLayout(list_group)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search items...")
        self.search_edit.textChanged.connect(self.filter_items)
        search_layout.addWidget(self.search_edit)
        list_group_layout.addLayout(search_layout)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels([
            "Name", "Category", "Quantity", "Unit", "Expiration", "GF Status", "Notes"
        ])
        
        # Set table properties
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name column
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Notes column
        
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.itemSelectionChanged.connect(self.on_item_selected)
        
        # Apply custom delegate to suppress selection borders
        from utils.custom_delegates import CleanSelectionDelegate
        self.items_table.setItemDelegate(CleanSelectionDelegate())
        
        # Add minimal custom styling - delegate handles selection
        self.items_table.setStyleSheet("""
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
        
        list_group_layout.addWidget(self.items_table)
        
        # Item actions
        action_layout = QHBoxLayout()
        
        delete_button = QPushButton("Delete Item")
        delete_button.clicked.connect(self.delete_item)
        action_layout.addWidget(delete_button)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_items)
        action_layout.addWidget(refresh_button)
        
        action_layout.addStretch()
        list_group_layout.addLayout(action_layout)
        
        list_layout.addWidget(list_group)
        splitter.addWidget(list_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 500])
        
        # Load initial data
        self.refresh_items()
    
    def add_item(self):
        """Add new item to pantry"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an item name.")
            return
        
        try:
            # Save to database
            item_id = self._save_item_to_database()
            if item_id:
                QMessageBox.information(self, "Success", "Item added successfully!")
                self.clear_form()
                self.refresh_items()
            else:
                QMessageBox.warning(self, "Error", "Failed to save item to database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add item: {str(e)}")
    
    def update_item(self):
        """Update selected item"""
        current_row = self.items_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to edit.")
            return
        
        try:
            from utils.edit_dialogs import PantryItemEditDialog
            
            # Get current item data
            item_data = {
                'name': self.items_table.item(current_row, 0).text(),
                'category': self.items_table.item(current_row, 1).text(),
                'quantity': int(self.items_table.item(current_row, 2).text()),
                'unit': self.items_table.item(current_row, 3).text(),
                'expiration_date': self.items_table.item(current_row, 4).text(),
                'gluten_free': self.items_table.item(current_row, 5).text(),
                'upc_code': '',
                'notes': ''
            }
            
            # Open edit dialog
            dialog = PantryItemEditDialog(self)
            dialog.set_data(item_data)
            
            if dialog.exec() == QDialog.Accepted:
                new_data = dialog.get_data()
                
                # Update database
                if self._update_item_in_database(current_row, new_data):
                    # Update table with new data
                    self.items_table.setItem(current_row, 0, QTableWidgetItem(new_data['name']))
                    self.items_table.setItem(current_row, 1, QTableWidgetItem(new_data['category']))
                    self.items_table.setItem(current_row, 2, QTableWidgetItem(str(new_data['quantity'])))
                    self.items_table.setItem(current_row, 3, QTableWidgetItem(new_data['unit']))
                    self.items_table.setItem(current_row, 4, QTableWidgetItem(new_data['expiration_date']))
                    self.items_table.setItem(current_row, 5, QTableWidgetItem(new_data['gluten_free']))
                    
                    QMessageBox.information(self, "Success", "Item updated successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update item in database.")
                
        except ImportError:
            # Fallback implementation when edit dialog is not available
            self._fallback_edit_item(current_row)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update item: {str(e)}")
    
    def _fallback_edit_item(self, row: int):
        """Fallback edit functionality when dialog is not available"""
        # Get current item data
        item_data = {
            'name': self.items_table.item(row, 0).text(),
            'category': self.items_table.item(row, 1).text(),
            'quantity': self.items_table.item(row, 2).text(),
            'unit': self.items_table.item(row, 3).text(),
            'expiration_date': self.items_table.item(row, 4).text(),
            'gluten_free': self.items_table.item(row, 5).text(),
            'upc_code': '',
            'notes': ''
        }
        
        # Create simple edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Pantry Item")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Item name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Item Name:"))
        name_edit = QLineEdit(item_data['name'])
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        
        # Category
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        category_combo = QComboBox()
        category_combo.addItems([
            "Grains & Flours", "Proteins", "Dairy", "Vegetables", "Fruits",
            "Beverages", "Snacks", "Condiments", "Frozen", "Canned", "Other"
        ])
        category_combo.setCurrentText(item_data['category'])
        category_layout.addWidget(category_combo)
        layout.addLayout(category_layout)
        
        # Quantity
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Quantity:"))
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, 1000)
        quantity_spin.setValue(int(item_data['quantity']))
        quantity_layout.addWidget(quantity_spin)
        layout.addLayout(quantity_layout)
        
        # Unit
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel("Unit:"))
        unit_combo = QComboBox()
        unit_combo.addItems([
            "pieces", "lbs", "kg", "oz", "g", "cups", "tbsp", "tsp", "ml", "L", "packages", "boxes"
        ])
        unit_combo.setCurrentText(item_data['unit'])
        unit_layout.addWidget(unit_combo)
        layout.addLayout(unit_layout)
        
        # Expiration date
        expiration_layout = QHBoxLayout()
        expiration_layout.addWidget(QLabel("Expiration Date:"))
        expiration_edit = QLineEdit(item_data['expiration_date'])
        expiration_edit.setPlaceholderText("YYYY-MM-DD")
        expiration_layout.addWidget(expiration_edit)
        layout.addLayout(expiration_layout)
        
        # Gluten-free status
        gluten_layout = QHBoxLayout()
        gluten_layout.addWidget(QLabel("Gluten-Free:"))
        gluten_combo = QComboBox()
        gluten_combo.addItems(["Yes", "No", "Unknown"])
        gluten_combo.setCurrentText(item_data['gluten_free'])
        gluten_layout.addWidget(gluten_combo)
        layout.addLayout(gluten_layout)
        
        # UPC Code
        upc_layout = QHBoxLayout()
        upc_layout.addWidget(QLabel("UPC Code:"))
        upc_edit = QLineEdit(item_data['upc_code'])
        upc_edit.setPlaceholderText("Enter UPC code...")
        upc_layout.addWidget(upc_edit)
        layout.addLayout(upc_layout)
        
        # Notes
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        notes_edit = QTextEdit(item_data['notes'])
        notes_edit.setMaximumHeight(100)
        notes_edit.setPlaceholderText("Additional notes...")
        notes_layout.addWidget(notes_edit)
        layout.addLayout(notes_layout)
        
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
            # Update table with new data
            self.items_table.setItem(row, 0, QTableWidgetItem(name_edit.text()))
            self.items_table.setItem(row, 1, QTableWidgetItem(category_combo.currentText()))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(quantity_spin.value())))
            self.items_table.setItem(row, 3, QTableWidgetItem(unit_combo.currentText()))
            self.items_table.setItem(row, 4, QTableWidgetItem(expiration_edit.text()))
            self.items_table.setItem(row, 5, QTableWidgetItem(gluten_combo.currentText()))
            
            QMessageBox.information(self, "Success", "Item updated successfully!")
    
    def delete_item(self):
        """Delete selected item"""
        if not self.items_table.currentRow() >= 0:
            QMessageBox.warning(self, "Selection Error", "Please select an item to delete.")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this item?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete from database
                if self._delete_item_from_database():
                    QMessageBox.information(self, "Success", "Item deleted successfully!")
                    self.refresh_items()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete item from database.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete item: {str(e)}")
    
    def clear_form(self):
        """Clear the form"""
        self.name_edit.clear()
        self.category_combo.setCurrentIndex(0)
        self.quantity_spin.setValue(1)
        self.unit_combo.setCurrentIndex(0)
        self.exp_date.setDate(QDate.currentDate().addDays(30))
        self.gf_combo.setCurrentIndex(0)
        self.notes_edit.clear()
    
    def filter_items(self):
        """Filter items based on search text"""
        search_text = self.search_edit.text().lower()
        
        for row in range(self.items_table.rowCount()):
            item_name = self.items_table.item(row, 0)
            if item_name:
                match = search_text in item_name.text().lower()
                self.items_table.setRowHidden(row, not match)
    
    def on_item_selected(self):
        """Handle item selection"""
        current_row = self.items_table.currentRow()
        if current_row >= 0:
            # Populate form with selected item data
            self.name_edit.setText(self.items_table.item(current_row, 0).text())
            # Set other fields based on selected item...
    
    def scan_upc(self):
        """Scan UPC code and check for gluten safety"""
        upc_code = self.upc_input.text().strip()
        if not upc_code:
            QMessageBox.warning(self, "No UPC", "Please enter a UPC code to scan.")
            return

        try:
            from services.upc_scanner import upc_scanner
            
            # Show progress dialog
            progress_dialog = QMessageBox(self)
            progress_dialog.setWindowTitle("Scanning UPC")
            progress_dialog.setText(f"Scanning UPC: {upc_code}\n\nChecking gluten safety...")
            progress_dialog.setStandardButtons(QMessageBox.Cancel)
            progress_dialog.setModal(False)  # Make it non-modal so it can be closed
            progress_dialog.buttonClicked.connect(lambda: self._close_progress_dialog(progress_dialog))
            progress_dialog.show()
            
            # Process events to ensure dialog is visible
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import QTimer
            QApplication.processEvents()
            
            # Set up a timeout timer to close the dialog if it gets stuck
            timeout_timer = QTimer()
            timeout_timer.setSingleShot(True)
            timeout_timer.timeout.connect(lambda: self._close_progress_dialog(progress_dialog))
            timeout_timer.start(10000)  # 10 second timeout
            
            try:
                # Scan the UPC code
                product_info = upc_scanner.scan_upc(upc_code)
                
                # Stop the timeout timer
                timeout_timer.stop()
                
                # Close progress dialog first
                self._close_progress_dialog(progress_dialog)
                
                if product_info:
                    # Show product information and gluten safety
                    self._show_product_info(product_info)
                else:
                    QMessageBox.warning(self, "Product Not Found", 
                        f"Could not find information for UPC: {upc_code}\n\n"
                        "This product may not be in our database or the UPC code may be invalid.")
                    
            except Exception as scan_error:
                # Ensure progress dialog is closed even on error
                self._close_progress_dialog(progress_dialog)
                raise scan_error
                
        except ImportError:
            # Fallback when scanner service is not available
            self._fallback_upc_scan(upc_code)
        except Exception as e:
            # Ensure any progress dialog is closed
            try:
                if 'progress_dialog' in locals():
                    self._close_progress_dialog(progress_dialog)
            except:
                pass
            QMessageBox.critical(self, "Scan Error", f"Failed to scan UPC: {str(e)}")
    
    def _close_progress_dialog(self, dialog):
        """Safely close progress dialog"""
        if dialog:
            try:
                dialog.close()
                dialog.deleteLater()
            except:
                pass
    
    def _show_product_info(self, product_info):
        """Show detailed product information and gluten safety analysis"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Product Information: {product_info.name}")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Product header
        header_layout = QHBoxLayout()
        
        # Product image (if available)
        if product_info.image_url:
            try:
                from PySide6.QtGui import QPixmap
                from PySide6.QtCore import QUrl
                from PySide6.QtWidgets import QLabel
                
                # Load image from URL (simplified - in real app you'd cache images)
                image_label = QLabel("Product Image")
                image_label.setFixedSize(100, 100)
                image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
                header_layout.addWidget(image_label)
            except:
                pass
        
        # Product details
        details_layout = QVBoxLayout()
        
        name_label = QLabel(f"<h2>{product_info.name}</h2>")
        details_layout.addWidget(name_label)
        
        brand_label = QLabel(f"<b>Brand:</b> {product_info.brand}")
        details_layout.addWidget(brand_label)
        
        category_label = QLabel(f"<b>Category:</b> {product_info.category}")
        details_layout.addWidget(category_label)
        
        upc_label = QLabel(f"<b>UPC:</b> {product_info.upc}")
        details_layout.addWidget(upc_label)
        
        details_layout.addStretch()
        header_layout.addLayout(details_layout)
        layout.addLayout(header_layout)
        
        # Gluten safety section
        safety_group = QGroupBox("Gluten Safety Analysis")
        safety_layout = QVBoxLayout(safety_group)
        
        # Safety status
        if product_info.gluten_free is True:
            safety_status = QLabel("✅ <b>GLUTEN-FREE</b> - Safe for celiac consumption")
            safety_status.setStyleSheet("color: green; font-size: 14px; padding: 10px; background-color: #e8f5e8; border-radius: 5px;")
        elif product_info.gluten_free is False:
            safety_status = QLabel("⚠️ <b>CONTAINS GLUTEN</b> - Not safe for celiac consumption")
            safety_status.setStyleSheet("color: red; font-size: 14px; padding: 10px; background-color: #ffe8e8; border-radius: 5px;")
        else:
            safety_status = QLabel("❓ <b>UNKNOWN</b> - Gluten-free status cannot be determined")
            safety_status.setStyleSheet("color: orange; font-size: 14px; padding: 10px; background-color: #fff3e0; border-radius: 5px;")
        
        safety_layout.addWidget(safety_status)
        
        # Warning message
        if product_info.gluten_warning:
            warning_label = QLabel(f"<b>Warning:</b> {product_info.gluten_warning}")
            warning_label.setWordWrap(True)
            warning_label.setStyleSheet("color: #d32f2f; padding: 5px;")
            safety_layout.addWidget(warning_label)
        
        # Confidence level
        confidence_label = QLabel(f"<b>Confidence Level:</b> {product_info.confidence * 100:.0f}%")
        safety_layout.addWidget(confidence_label)
        
        layout.addWidget(safety_group)
        
        # Ingredients section
        if product_info.ingredients:
            ingredients_group = QGroupBox("Ingredients")
            ingredients_layout = QVBoxLayout(ingredients_group)
            
            ingredients_text = ", ".join(product_info.ingredients)
            ingredients_label = QLabel(ingredients_text)
            ingredients_label.setWordWrap(True)
            ingredients_layout.addWidget(ingredients_label)
            
            layout.addWidget(ingredients_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        if product_info.gluten_free is True:
            add_to_pantry_btn = QPushButton("Add to Pantry")
            add_to_pantry_btn.clicked.connect(lambda: self._add_product_to_pantry(product_info))
            button_layout.addWidget(add_to_pantry_btn)
        
        find_alternatives_btn = QPushButton("Find GF Alternatives")
        find_alternatives_btn.clicked.connect(lambda: self._show_alternatives(product_info))
        button_layout.addWidget(find_alternatives_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _add_product_to_pantry(self, product_info):
        """Add scanned product to pantry"""
        # Pre-fill the form with product information
        self.name_edit.setText(product_info.name)
        self.category_combo.setCurrentText(product_info.category)
        
        # Set gluten-free status
        if product_info.gluten_free is True:
            self.gluten_free_checkbox.setChecked(True)
        
        QMessageBox.information(self, "Product Added", 
            f"Product '{product_info.name}' has been added to the form.\n"
            "Please review and adjust quantities before saving.")
    
    def _show_alternatives(self, product_info):
        """Show gluten-free alternatives for the product"""
        try:
            from services.upc_scanner import upc_scanner
            
            alternatives = upc_scanner.get_gluten_free_alternatives(product_info)
            
            if alternatives:
                dialog = QDialog(self)
                dialog.setWindowTitle("Gluten-Free Alternatives")
                dialog.setModal(True)
                dialog.resize(500, 400)
                
                layout = QVBoxLayout(dialog)
                layout.addWidget(QLabel(f"<h3>Gluten-Free Alternatives for: {product_info.name}</h3>"))
                
                for alt in alternatives:
                    alt_group = QGroupBox(f"{alt['name']} - {alt['brand']}")
                    alt_layout = QVBoxLayout(alt_group)
                    alt_layout.addWidget(QLabel(alt['notes']))
                    layout.addWidget(alt_group)
                
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)
                
                dialog.exec()
            else:
                QMessageBox.information(self, "No Alternatives", 
                    "No specific gluten-free alternatives found for this product.\n"
                    "Try searching for similar gluten-free products in your local store.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to find alternatives: {str(e)}")
    
    def _fallback_upc_scan(self, upc_code):
        """Fallback UPC scanning when service is not available"""
        QMessageBox.information(self, "UPC Scan", 
            f"Scanning UPC: {upc_code}\n\n"
            "UPC scanning functionality will be implemented here.\n\n"
            "Features will include:\n"
            "• Real-time gluten-free safety checking\n"
            "• Product information lookup\n"
            "• Ingredient analysis\n"
            "• Gluten-free alternative suggestions")
        # 1. Query a gluten-free product database
        # 2. Check for gluten ingredients
        # 3. Return safety status
        # 4. Auto-populate the form with product info
    
    def bulk_import_items(self):
        """Import multiple items from file"""
        from PySide6.QtWidgets import QFileDialog
        
        # Create bulk import dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Bulk Import Pantry Items")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel("Bulk Import Pantry Items")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout(options_group)
        
        # Import type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Import Type:"))
        self.import_type_combo = QComboBox()
        self.import_type_combo.addItems([
            "CSV File",
            "Excel File",
            "UPC Database",
            "Template Import"
        ])
        type_layout.addWidget(self.import_type_combo)
        options_layout.addLayout(type_layout)
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("File:"))
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select file to import...")
        file_layout.addWidget(self.file_path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_import_file)
        file_layout.addWidget(browse_btn)
        options_layout.addLayout(file_layout)
        
        # Import settings
        settings_group = QGroupBox("Import Settings")
        settings_layout = QVBoxLayout(settings_group)
        
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
        settings_layout.addLayout(duplicate_layout)
        
        # Category assignment
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Default Category:"))
        self.default_category_edit = QLineEdit()
        self.default_category_edit.setPlaceholderText("e.g., Pantry, Frozen, etc.")
        category_layout.addWidget(self.default_category_edit)
        settings_layout.addLayout(category_layout)
        
        layout.addWidget(options_group)
        layout.addWidget(settings_group)
        
        # Preview section
        preview_group = QGroupBox("Import Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(5)
        self.preview_table.setHorizontalHeaderLabels(["Name", "Brand", "Category", "Expiry", "Notes"])
        self.preview_table.setMaximumHeight(200)
        preview_layout.addWidget(self.preview_table)
        
        preview_btn = QPushButton("Preview Import")
        preview_btn.clicked.connect(self.preview_bulk_import)
        preview_layout.addWidget(preview_btn)
        
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        import_btn = QPushButton("Import Items")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(import_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        import_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        self.import_type_combo.currentTextChanged.connect(self.update_import_options)
        
        # Initialize
        self.update_import_options()
        
        if dialog.exec() == QDialog.Accepted:
            self.perform_bulk_import()
            QMessageBox.information(self, "Success", "Bulk import completed successfully!")
    
    def browse_import_file(self):
        """Browse for import file"""
        from PySide6.QtWidgets import QFileDialog
        
        import_type = self.import_type_combo.currentText()
        
        if "CSV" in import_type:
            file_filter = "CSV Files (*.csv);;All Files (*)"
        elif "Excel" in import_type:
            file_filter = "Excel Files (*.xlsx *.xls);;All Files (*)"
        else:
            file_filter = "All Files (*)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Import File", "", file_filter
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def update_import_options(self):
        """Update import options based on type"""
        import_type = self.import_type_combo.currentText()
        
        # Enable/disable file selection based on type
        if import_type == "UPC Database":
            self.file_path_edit.setEnabled(False)
            self.file_path_edit.setPlaceholderText("UPC database import - no file needed")
        else:
            self.file_path_edit.setEnabled(True)
            self.file_path_edit.setPlaceholderText("Select file to import...")
    
    def preview_bulk_import(self):
        """Preview bulk import data"""
        try:
            import_type = self.import_type_combo.currentText()
            file_path = self.file_path_edit.text().strip()
            
            if import_type != "UPC Database" and not file_path:
                QMessageBox.warning(self, "Validation Error", "Please select a file to import.")
            return
        
            # Generate sample preview data
            sample_data = [
                ["Gluten-Free Bread", "Udi's", "Bakery", "2024-02-15", "Whole grain"],
                ["Almond Milk", "Silk", "Dairy", "2024-03-01", "Unsweetened"],
                ["Quinoa", "Bob's Red Mill", "Grains", "2024-12-31", "Organic"],
                ["Coconut Oil", "Spectrum", "Cooking", "2024-06-30", "Virgin"],
                ["GF Pasta", "Barilla", "Pasta", "2024-08-15", "Brown rice"]
            ]
            
            # Populate preview table
            self.preview_table.setRowCount(len(sample_data))
            for row, data in enumerate(sample_data):
                for col, value in enumerate(data):
                    self.preview_table.setItem(row, col, QTableWidgetItem(value))
            
        except Exception as e:
            QMessageBox.critical(self, "Preview Error", f"Failed to preview import: {str(e)}")
    
    def perform_bulk_import(self):
        """Perform the bulk import operation"""
        try:
            import_type = self.import_type_combo.currentText()
            file_path = self.file_path_edit.text().strip()
            duplicate_handling = self.duplicate_combo.currentText()
            default_category = self.default_category_edit.text().strip() or "Pantry"
            
            if import_type == "UPC Database":
                # Import from UPC database (placeholder)
                self.import_from_upc_database()
            else:
                # Import from file
                if not file_path:
                    QMessageBox.warning(self, "Validation Error", "Please select a file to import.")
                    return
                
                self.import_from_file(file_path, duplicate_handling, default_category)
            
            # Refresh the pantry display
            self.load_pantry()
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import items: {str(e)}")
    
    def import_from_upc_database(self):
        """Import items from UPC database"""
        # This would integrate with the UPC scanner service
        QMessageBox.information(self, "UPC Database Import", 
                               "UPC database import would scan for gluten-free products.\n\n"
                               "This feature would:\n"
                               "• Query gluten-free product databases\n"
                               "• Import product information\n"
                               "• Set appropriate categories\n"
                               "• Add gluten-free verification")
    
    def import_from_file(self, file_path, duplicate_handling, default_category):
        """Import items from file"""
        import csv
        from utils.db import get_connection
        
        conn = get_connection()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                if file_path.endswith('.csv'):
                    reader = csv.DictReader(file)
                    imported_count = 0
                    
                    for row in reader:
                        name = row.get('name', '').strip()
                        brand = row.get('brand', '').strip()
                        category = row.get('category', default_category).strip()
                        expiry = row.get('expiry', '').strip()
                        notes = row.get('notes', '').strip()
                        
                        if not name:
                            continue
                
                        # Handle duplicates
                        if duplicate_handling == "Skip duplicates":
                            existing = conn.execute(
                                "SELECT id FROM pantry WHERE name = ? AND brand = ?",
                                (name, brand)
                            ).fetchone()
                            if existing:
                                continue
                        
                        # Insert item
                        conn.execute("""
                            INSERT OR REPLACE INTO pantry 
                            (name, brand, category, expiry_date, notes)
                            VALUES (?, ?, ?, ?, ?)
                        """, (name, brand, category, expiry, notes))
                        imported_count += 1
                    
                    conn.commit()
                    QMessageBox.information(self, "Import Complete", 
                                          f"Successfully imported {imported_count} items from CSV file.")
                
                else:
                    QMessageBox.warning(self, "File Format", 
                                      "Currently only CSV files are supported for bulk import.")
        
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def export_pantry(self):
        """Export pantry data to file"""
        try:
            from services.export_service import export_service
            
            # Get pantry data from table
            pantry_data = []
            for row in range(self.items_table.rowCount()):
                item_data = {
                    'name': self.items_table.item(row, 0).text() if self.items_table.item(row, 0) else '',
                    'category': self.items_table.item(row, 1).text() if self.items_table.item(row, 1) else '',
                    'quantity': self.items_table.item(row, 2).text() if self.items_table.item(row, 2) else '',
                    'unit': self.items_table.item(row, 3).text() if self.items_table.item(row, 3) else '',
                    'expiration_date': self.items_table.item(row, 4).text() if self.items_table.item(row, 4) else '',
                    'gluten_free': self.items_table.item(row, 5).text() if self.items_table.item(row, 5) else ''
                }
                pantry_data.append(item_data)
            
            # Show export options dialog
            from PySide6.QtWidgets import QRadioButton, QButtonGroup
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Export Pantry Data")
            dialog.setModal(True)
            dialog.resize(300, 200)
            
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Select export format:"))
            
            button_group = QButtonGroup()
            csv_radio = QRadioButton("CSV (for spreadsheet programs)")
            csv_radio.setChecked(True)
            excel_radio = QRadioButton("Excel (with formatting)")
            pdf_radio = QRadioButton("PDF (printable report)")
            
            button_group.addButton(csv_radio, 0)
            button_group.addButton(excel_radio, 1)
            button_group.addButton(pdf_radio, 2)
            
            layout.addWidget(csv_radio)
            layout.addWidget(excel_radio)
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
                selected_format = button_group.checkedId()
                if selected_format == 0:
                    export_service.export_pantry_data(self, pantry_data)
                elif selected_format == 1:
                    export_service.export_data(self, pantry_data, 'excel', "Pantry Inventory")
                elif selected_format == 2:
                    export_service.export_data(self, pantry_data, 'pdf', "Pantry Inventory Report")
                    
        except ImportError:
            QMessageBox.information(self, "Export Pantry", "Export functionality will be implemented here.\n\nFeatures will include:\n• CSV export\n• Excel export\n• JSON export\n• Shopping list generation")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export pantry data: {str(e)}")
    
    def refresh_items(self):
        """Refresh the items table"""
        try:
            from utils.db import get_connection
            
            db = get_connection()
            cursor = db.cursor()
            
            # Load pantry items from database
            cursor.execute("""
                SELECT name, category, quantity, unit, expiration, 
                       gf_flag, brand, '', notes, ''
                FROM pantry 
                ORDER BY name
            """)
            
            items = cursor.fetchall()
            
            # Clear existing data
            self.items_table.setRowCount(len(items))
            
            for row, item in enumerate(items):
                name, category, quantity, unit, expiration, gf_flag, brand, upc_code, notes, created_at = item
                
                # Populate table
                self.items_table.setItem(row, 0, QTableWidgetItem(name or ""))
                self.items_table.setItem(row, 1, QTableWidgetItem(category or ""))
                self.items_table.setItem(row, 2, QTableWidgetItem(str(quantity) if quantity else ""))
                self.items_table.setItem(row, 3, QTableWidgetItem(unit or ""))
                self.items_table.setItem(row, 4, QTableWidgetItem(expiration or ""))
                self.items_table.setItem(row, 5, QTableWidgetItem(gf_flag or "Unknown"))
                self.items_table.setItem(row, 6, QTableWidgetItem(brand or ""))
            
            # If no items in database, add sample items
            if len(items) == 0:
                self._load_sample_items()
                
        except Exception as e:
            print(f"Error loading pantry items from database: {e}")
            # Fallback to sample items
            self._load_sample_items()
    
    def _load_sample_items(self):
        """Load sample items when database is empty"""
        sample_items = [
            ["Gluten-Free Bread", "Grains & Flours", "2", "loaves", "2024-02-15", "Yes", "Udi's brand"],
            ["Rice Flour", "Grains & Flours", "1", "lbs", "2025-01-01", "Yes", "Bob's Red Mill"],
            ["Chicken Stock", "Canned Goods", "3", "cans", "2024-06-01", "Unknown", "Check ingredients"],
            ["Almond Milk", "Dairy", "1", "carton", "2024-02-01", "Yes", "Unsweetened"],
        ]
        
        self.items_table.setRowCount(len(sample_items))
        for i, item in enumerate(sample_items):
            for j, value in enumerate(item):
                self.items_table.setItem(i, j, QTableWidgetItem(value))
    
    def refresh(self):
        """Refresh panel data"""
        self.refresh_items()
    
    def _save_item_to_database(self):
        """Save pantry item to database and return item ID"""
        try:
            from utils.db import get_connection
            
            db = get_connection()
            cursor = db.cursor()
            
            # Get form data
            name = self.name_edit.text().strip()
            category = self.category_combo.currentText()
            quantity = self.quantity_spin.value()
            unit = self.unit_edit.text().strip()
            expiry_date = self.expiry_date_edit.date().toString("yyyy-MM-dd") if self.expiry_date_edit.date().isValid() else None
            is_gluten_free = self.gluten_free_combo.currentText() == "Yes"
            brand = self.brand_edit.text().strip()
            upc_code = self.upc_input.text().strip()
            notes = self.notes_edit.toPlainText().strip()
            
            # Insert item
            cursor.execute("""
                INSERT INTO pantry (name, category, quantity, unit, expiration, 
                                  gf_flag, brand, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, category, quantity, unit, expiry_date,
                "YES" if is_gluten_free else "NO", brand, notes
            ))
            
            item_id = cursor.lastrowid
            db.commit()
            return item_id
            
        except Exception as e:
            print(f"Error saving pantry item to database: {e}")
            return None
    
    def _update_item_in_database(self, row, item_data):
        """Update pantry item in database"""
        try:
            from utils.db import get_connection
            
            db = get_connection()
            cursor = db.cursor()
            
            # Get current item name to find the record
            current_name = self.items_table.item(row, 0).text()
            
            # Parse gluten-free status
            is_gluten_free = item_data['gluten_free'] == "Yes"
            
            # Update item
            cursor.execute("""
                UPDATE pantry_items 
                SET name = ?, category = ?, quantity = ?, unit = ?, expiry_date = ?,
                    is_gluten_free = ?, brand = ?, notes = ?, updated_at = datetime('now')
                WHERE name = ?
            """, (
                item_data['name'],
                item_data['category'],
                item_data['quantity'],
                item_data['unit'],
                item_data['expiration_date'],
                is_gluten_free,
                item_data.get('brand', ''),
                item_data.get('notes', ''),
                current_name
            ))
            
            db.commit()
            return True
                
        except Exception as e:
            print(f"Error updating pantry item in database: {e}")
            return False
    
    def _delete_item_from_database(self):
        """Delete pantry item from database"""
        try:
            from utils.db import get_connection
            
            current_row = self.items_table.currentRow()
            if current_row < 0:
                return False
            
            # Get item name to delete
            item_name = self.items_table.item(current_row, 0).text()
            
            db = get_connection()
            cursor = db.cursor()
            
            # Delete item
            cursor.execute("DELETE FROM pantry_items WHERE name = ?", (item_name,))
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error deleting pantry item from database: {e}")
            return False
