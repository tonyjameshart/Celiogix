#!/usr/bin/env python3
"""
Demo script to showcase the shopping list functionality in the mobile companion application
"""

import sys
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import Qt

from panels.mobile_companion_panel import MobileCompanionPanel
from services.mobile_sync import ShoppingListItemData


class ShoppingListDemo(QMainWindow):
    """Demo window for shopping list functionality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛒 Mobile Companion Shopping List Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Add title
        title = QLabel("🛒 Mobile Companion Shopping List Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Add description
        description = QLabel("""
This demo showcases the shopping list functionality integrated into the mobile companion application.
The shopping list includes:
• Purchase checkboxes for each item
• Store and category filtering
• Priority levels with color coding
• Gluten-free indicators
• Real-time statistics and completion tracking
• Export functionality
• Integration with mobile sync service

Navigate to the "🛒 Shopping List" tab to see the functionality in action!
        """)
        description.setStyleSheet("font-size: 14px; color: #34495e; margin: 20px; padding: 20px; background-color: #ecf0f1; border-radius: 10px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add demo controls
        controls_layout = QVBoxLayout()
        
        add_sample_btn = QPushButton("➕ Add Sample Shopping Items")
        add_sample_btn.clicked.connect(self.add_sample_items)
        add_sample_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        clear_items_btn = QPushButton("🗑️ Clear All Items")
        clear_items_btn.clicked.connect(self.clear_all_items)
        clear_items_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        controls_layout.addWidget(add_sample_btn)
        controls_layout.addWidget(clear_items_btn)
        layout.addLayout(controls_layout)
        
        # Add mobile companion panel
        self.mobile_panel = MobileCompanionPanel(self)
        layout.addWidget(self.mobile_panel)
        
        # Add initial sample items
        self.add_sample_items()
    
    def add_sample_items(self):
        """Add sample shopping list items"""
        sample_items = [
            ShoppingListItemData(
                item_name="Gluten-Free Bread",
                quantity="2 loaves",
                category="Bakery (GF)",
                store="Health Food Store",
                purchased=False,
                timestamp=datetime.now(),
                priority="High",
                notes="Udi's or Canyon Bakehouse preferred",
                gluten_free=True
            ),
            ShoppingListItemData(
                item_name="Almond Milk",
                quantity="3 cartons",
                category="Dairy & Eggs",
                store="Grocery Store",
                purchased=True,
                timestamp=datetime.now(),
                priority="Medium",
                notes="Unsweetened vanilla",
                gluten_free=True
            ),
            ShoppingListItemData(
                item_name="Quinoa",
                quantity="1 bag",
                category="Pantry",
                store="Bulk Store",
                purchased=False,
                timestamp=datetime.now(),
                priority="Medium",
                notes="Organic if available",
                gluten_free=True
            ),
            ShoppingListItemData(
                item_name="Fresh Spinach",
                quantity="2 bags",
                category="Produce",
                store="Farmers Market",
                purchased=False,
                timestamp=datetime.now(),
                priority="High",
                notes="Organic preferred",
                gluten_free=True
            ),
            ShoppingListItemData(
                item_name="Chicken Breast",
                quantity="3 lbs",
                category="Meat & Seafood",
                store="Grocery Store",
                purchased=False,
                timestamp=datetime.now(),
                priority="Medium",
                notes="Free-range if available",
                gluten_free=True
            ),
            ShoppingListItemData(
                item_name="Gluten-Free Pasta",
                quantity="4 boxes",
                category="Pantry",
                store="Grocery Store",
                purchased=False,
                timestamp=datetime.now(),
                priority="Low",
                notes="Brown rice or quinoa pasta",
                gluten_free=True
            ),
            ShoppingListItemData(
                item_name="Coconut Oil",
                quantity="1 jar",
                category="Pantry",
                store="Health Food Store",
                purchased=True,
                timestamp=datetime.now(),
                priority="Low",
                notes="Virgin, unrefined",
                gluten_free=True
            ),
            ShoppingListItemData(
                item_name="GF Granola",
                quantity="1 bag",
                category="Pantry",
                store="Health Food Store",
                purchased=False,
                timestamp=datetime.now(),
                priority="Medium",
                notes="Low sugar, high protein",
                gluten_free=True
            )
        ]
        
        # Add items to mobile sync service
        for item in sample_items:
            self.mobile_panel.mobile_sync.add_shopping_list_item(item)
        
        # Update display
        self.mobile_panel.update_shopping_list_display()
        
        QMessageBox.information(self, "Sample Items Added", f"Added {len(sample_items)} sample shopping list items!")
    
    def clear_all_items(self):
        """Clear all shopping list items"""
        reply = QMessageBox.question(self, "Clear All Items", 
                                   "Are you sure you want to clear all shopping list items?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.mobile_panel.mobile_sync.shopping_list_items.clear()
            self.mobile_panel.update_shopping_list_display()
            QMessageBox.information(self, "Items Cleared", "All shopping list items have been cleared!")


def main():
    """Main function to run the demo"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Mobile Companion Shopping List Demo")
    app.setApplicationVersion("1.0")
    
    # Create and show demo window
    demo = ShoppingListDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
