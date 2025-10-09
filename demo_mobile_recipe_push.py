#!/usr/bin/env python3
"""
Demo script for mobile recipe push functionality
Shows how recipes from the menu panel can be pushed to mobile for offline viewing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt
from services.mobile_sync import get_mobile_sync_service, MobileRecipeData
from datetime import datetime


class MobileRecipePushDemo(QMainWindow):
    """Demo window for mobile recipe push functionality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📱 Mobile Recipe Push Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Get mobile sync service
        self.mobile_sync = get_mobile_sync_service()
        
        self.setup_ui()
        self.load_demo_recipes()
    
    def setup_ui(self):
        """Set up the demo UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("📱 Mobile Recipe Push Demo")
        header_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("""
        This demo shows how recipes from the menu panel can be pushed to the mobile app 
        for offline viewing. Users can select recipes from their meal plans and send them 
        to their mobile device for convenient access while cooking or shopping.
        """)
        desc_label.setStyleSheet("""
            font-size: 14px;
            color: #34495e;
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Demo buttons
        demo_layout = QVBoxLayout()
        
        # Add demo recipes button
        add_recipes_btn = QPushButton("🍽️ Add Demo Recipes to Mobile")
        add_recipes_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_recipes_btn.clicked.connect(self.add_demo_recipes)
        demo_layout.addWidget(add_recipes_btn)
        
        # View mobile recipes button
        view_recipes_btn = QPushButton("📖 View Mobile Recipes")
        view_recipes_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        view_recipes_btn.clicked.connect(self.view_mobile_recipes)
        demo_layout.addWidget(view_recipes_btn)
        
        # Export recipes button
        export_recipes_btn = QPushButton("📤 Export Mobile Recipes")
        export_recipes_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        export_recipes_btn.clicked.connect(self.export_mobile_recipes)
        demo_layout.addWidget(export_recipes_btn)
        
        # Clear recipes button
        clear_recipes_btn = QPushButton("🗑️ Clear Mobile Recipes")
        clear_recipes_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_recipes_btn.clicked.connect(self.clear_mobile_recipes)
        demo_layout.addWidget(clear_recipes_btn)
        
        layout.addLayout(demo_layout)
        
        # Status label
        self.status_label = QLabel("Ready to demo mobile recipe push functionality")
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin-top: 20px;
        """)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Stats label
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("""
            font-size: 12px;
            color: #95a5a6;
            margin-top: 10px;
        """)
        layout.addWidget(self.stats_label)
        
        layout.addStretch()
    
    def load_demo_recipes(self):
        """Load demo recipes into mobile sync"""
        demo_recipes = [
            {
                'id': 'mobile_demo_1',
                'name': 'Gluten-Free Pancakes',
                'description': 'Fluffy, delicious gluten-free pancakes perfect for breakfast',
                'category': 'Breakfast',
                'prep_time': '10 minutes',
                'cook_time': '15 minutes',
                'servings': 4,
                'difficulty': 'Easy',
                'ingredients': '''
• 1 cup gluten-free flour blend
• 2 tablespoons sugar
• 1 teaspoon baking powder
• 1/2 teaspoon salt
• 1 cup milk (dairy or non-dairy)
• 1 egg
• 2 tablespoons melted butter
• 1 teaspoon vanilla extract
                ''',
                'instructions': '''
1. In a large bowl, whisk together flour, sugar, baking powder, and salt
2. In another bowl, whisk together milk, egg, melted butter, and vanilla
3. Pour wet ingredients into dry ingredients and stir until just combined
4. Heat a griddle or large skillet over medium heat
5. Pour 1/4 cup batter for each pancake
6. Cook until bubbles form on surface, then flip
7. Cook until golden brown on both sides
8. Serve warm with maple syrup
                ''',
                'notes': 'For best results, let batter rest for 5 minutes before cooking',
                'pushed_at': datetime.now().isoformat(),
                'mobile_optimized': True,
                'gluten_free_verified': True
            },
            {
                'id': 'mobile_demo_2',
                'name': 'Quinoa Salad',
                'description': 'Nutritious and colorful quinoa salad with fresh vegetables',
                'category': 'Lunch',
                'prep_time': '15 minutes',
                'cook_time': '20 minutes',
                'servings': 6,
                'difficulty': 'Easy',
                'ingredients': '''
• 1 cup quinoa
• 2 cups water
• 1 cucumber, diced
• 1 bell pepper, diced
• 1 cup cherry tomatoes, halved
• 1/4 cup red onion, diced
• 1/4 cup fresh herbs (parsley, mint)
• 1/4 cup olive oil
• 2 tablespoons lemon juice
• Salt and pepper to taste
                ''',
                'instructions': '''
1. Rinse quinoa thoroughly in cold water
2. Bring water to boil, add quinoa, reduce heat and simmer for 15 minutes
3. Remove from heat and let stand for 5 minutes, then fluff with fork
4. Let quinoa cool completely
5. In a large bowl, combine cooled quinoa with vegetables
6. Whisk together olive oil, lemon juice, salt and pepper
7. Pour dressing over salad and toss gently
8. Garnish with fresh herbs and serve
                ''',
                'notes': 'Can be made ahead and stored in refrigerator for up to 3 days',
                'pushed_at': datetime.now().isoformat(),
                'mobile_optimized': True,
                'gluten_free_verified': True
            },
            {
                'id': 'mobile_demo_3',
                'name': 'Baked Salmon',
                'description': 'Simple and delicious baked salmon with herbs',
                'category': 'Dinner',
                'prep_time': '10 minutes',
                'cook_time': '20 minutes',
                'servings': 4,
                'difficulty': 'Easy',
                'ingredients': '''
• 4 salmon fillets (6 oz each)
• 2 tablespoons olive oil
• 2 cloves garlic, minced
• 1 tablespoon fresh dill
• 1 tablespoon fresh parsley
• 1 lemon, sliced
• Salt and pepper to taste
                ''',
                'instructions': '''
1. Preheat oven to 400°F (200°C)
2. Line baking sheet with parchment paper
3. Place salmon fillets on prepared sheet
4. Drizzle with olive oil and season with salt and pepper
5. Sprinkle with minced garlic and fresh herbs
6. Top each fillet with lemon slices
7. Bake for 15-20 minutes until fish flakes easily
8. Serve immediately with steamed vegetables
                ''',
                'notes': 'Fish is done when it flakes easily with a fork',
                'pushed_at': datetime.now().isoformat(),
                'mobile_optimized': True,
                'gluten_free_verified': True
            }
        ]
        
        # Add demo recipes to mobile sync
        for recipe_data in demo_recipes:
            self.mobile_sync.add_recipe_to_mobile(recipe_data)
        
        self.update_status()
    
    def add_demo_recipes(self):
        """Add demo recipes to mobile sync"""
        self.load_demo_recipes()
        self.status_label.setText("✅ Demo recipes added to mobile sync! Check the Mobile Companion panel to view them.")
        self.update_status()
    
    def view_mobile_recipes(self):
        """View mobile recipes in a dialog"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        
        recipes = self.mobile_sync.get_mobile_recipes()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("📖 Mobile Recipes")
        dialog.setModal(True)
        dialog.resize(700, 600)
        
        layout = QVBoxLayout(dialog)
        
        if recipes:
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            
            content = "📱 MOBILE RECIPES FOR OFFLINE VIEWING\n\n"
            content += f"Total Recipes: {len(recipes)}\n"
            content += "=" * 50 + "\n\n"
            
            for i, recipe in enumerate(recipes, 1):
                content += f"{i}. {recipe.name}\n"
                content += f"   Category: {recipe.category}\n"
                content += f"   Prep Time: {recipe.prep_time}\n"
                content += f"   Cook Time: {recipe.cook_time}\n"
                content += f"   Servings: {recipe.servings}\n"
                content += f"   Difficulty: {recipe.difficulty}\n"
                content += f"   Mobile Optimized: {'Yes' if recipe.mobile_optimized else 'No'}\n"
                content += f"   Gluten-Free Verified: {'Yes' if recipe.gluten_free_verified else 'No'}\n"
                content += f"   Pushed At: {recipe.pushed_at}\n"
                
                if recipe.description:
                    content += f"   Description: {recipe.description}\n"
                
                content += "\n" + "-" * 40 + "\n\n"
            
            text_edit.setPlainText(content)
            layout.addWidget(text_edit)
        else:
            no_recipes_label = QLabel("No mobile recipes available. Add some demo recipes first!")
            no_recipes_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_recipes_label)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def export_mobile_recipes(self):
        """Export mobile recipes to file"""
        recipes = self.mobile_sync.get_mobile_recipes()
        
        if not recipes:
            self.status_label.setText("❌ No mobile recipes to export. Add some demo recipes first!")
            return
        
        export_data = self.mobile_sync.export_mobile_data('mobile_recipes')
        
        # Save to demo file
        import json
        filename = f"mobile_recipes_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.status_label.setText(f"✅ Successfully exported {len(recipes)} recipes to {filename}")
        except Exception as e:
            self.status_label.setText(f"❌ Error exporting recipes: {str(e)}")
        
        self.update_status()
    
    def clear_mobile_recipes(self):
        """Clear all mobile recipes"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, "Clear Mobile Recipes",
            "Are you sure you want to clear all mobile recipes?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.mobile_sync.mobile_recipes.clear()
            self.status_label.setText("🗑️ All mobile recipes cleared!")
            self.update_status()
    
    def update_status(self):
        """Update status and stats"""
        recipes = self.mobile_sync.get_mobile_recipes()
        stats = self.mobile_sync.get_mobile_recipe_stats()
        
        stats_text = f"""
        📊 Mobile Recipe Stats:
        • Total Recipes: {stats['total_recipes']}
        • Categories: {len(stats['category_counts'])}
        • Categories: {', '.join(stats['category_counts'].keys()) if stats['category_counts'] else 'None'}
        """
        
        self.stats_label.setText(stats_text)


def main():
    """Run the mobile recipe push demo"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    demo = MobileRecipePushDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
