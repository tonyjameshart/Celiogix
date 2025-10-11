# path: services/enhanced_features.py
"""
Enhanced Features Integration for CeliacShield

Integrates all new features into existing panels with minimal code changes.
"""

from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout
from PySide6.QtCore import Qt

from services.nutrition_analyzer import nutrition_analyzer
from services.restaurant_finder import restaurant_finder
from services.ingredient_correlator import ingredient_correlator
from services.smart_shopping import smart_shopping_service


class EnhancedFeatures:
    """Integration class for all enhanced features"""
    
    @staticmethod
    def enhance_barcode_scan_results(product_info, parent_widget):
        """Enhance barcode scan results with nutrition data"""
        if hasattr(product_info, 'detailed_nutrition') and product_info.detailed_nutrition:
            nutrition = product_info.detailed_nutrition
            
            # Create enhanced display dialog
            dialog = QDialog(parent_widget)
            dialog.setWindowTitle(f"Enhanced Product Analysis: {product_info.name}")
            dialog.setModal(True)
            dialog.resize(600, 500)
            
            layout = QVBoxLayout(dialog)
            
            # Basic product info
            basic_info = QLabel(f"""
📦 Product: {product_info.name}
🏷️ Brand: {product_info.brand}
🔍 UPC: {product_info.upc}
✅ Gluten-Free: {'Yes' if product_info.gluten_free else 'No'}
            """)
            layout.addWidget(basic_info)
            
            # Enhanced nutrition info
            nutrition_info = QLabel(f"""
📊 Nutrition Analysis (per 100g):
• Calories: {nutrition.calories:.0f}
• Protein: {nutrition.protein_g:.1f}g
• Carbs: {nutrition.carbs_g:.1f}g
• Fiber: {nutrition.fiber_g:.1f}g
• Fat: {nutrition.fat_g:.1f}g
• Sodium: {nutrition.sodium_mg:.0f}mg
• Iron: {nutrition.iron_mg:.1f}mg
• Calcium: {nutrition.calcium_mg:.0f}mg
            """)
            layout.addWidget(nutrition_info)
            
            # Safety assessment
            if product_info.gluten_warning:
                warning_label = QLabel(f"⚠️ Warning: {product_info.gluten_warning}")
                warning_label.setStyleSheet("color: red; font-weight: bold;")
                layout.addWidget(warning_label)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec()
    
    @staticmethod
    def show_smart_shopping_suggestions(shopping_list, parent_widget):
        """Show smart shopping suggestions"""
        try:
            user_preferences = {
                'max_price_per_item': 10.0,
                'preferred_brands': ['Udi\'s', 'King Arthur', 'Bob\'s Red Mill'],
                'favorite_cuisines': ['american', 'mediterranean']
            }
            
            purchase_history = [
                {'item_name': 'gluten-free bread', 'brand': 'Udi\'s', 'frequency': 5},
                {'item_name': 'rice flour', 'brand': 'Bob\'s Red Mill', 'frequency': 3}
            ]
            
            suggestions = smart_shopping_service.generate_smart_suggestions(
                shopping_list, user_preferences, purchase_history
            )
            
            # Show suggestions dialog
            dialog = QDialog(parent_widget)
            dialog.setWindowTitle("💡 Smart Shopping Suggestions")
            dialog.setModal(True)
            dialog.resize(700, 400)
            
            layout = QVBoxLayout(dialog)
            
            header = QLabel("Personalized product suggestions based on your preferences:")
            layout.addWidget(header)
            
            # Suggestions table
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Product", "Brand", "Reason", "Confidence"])
            table.setRowCount(len(suggestions))
            
            for row, suggestion in enumerate(suggestions):
                table.setItem(row, 0, QTableWidgetItem(suggestion.product_name))
                table.setItem(row, 1, QTableWidgetItem(suggestion.brand))
                table.setItem(row, 2, QTableWidgetItem(suggestion.reason))
                table.setItem(row, 3, QTableWidgetItem(f"{suggestion.confidence_score:.0%}"))
            
            layout.addWidget(table)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(parent_widget, "Error", f"Failed to generate suggestions: {str(e)}")
    
    @staticmethod
    def show_restaurant_finder(parent_widget):
        """Show enhanced restaurant finder"""
        try:
            # Default coordinates (NYC)
            latitude, longitude = 40.7128, -74.0060
            
            restaurants = restaurant_finder.find_nearby_restaurants(latitude, longitude, 10)
            
            dialog = QDialog(parent_widget)
            dialog.setWindowTitle("🍴 Nearby Gluten-Free Restaurants")
            dialog.setModal(True)
            dialog.resize(800, 500)
            
            layout = QVBoxLayout(dialog)
            
            header = QLabel("Celiac-safe restaurants near you (sorted by safety score):")
            layout.addWidget(header)
            
            # Restaurant table
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Name", "Cuisine", "Distance", "Safety Score", "Rating"])
            table.setRowCount(len(restaurants))
            
            for row, restaurant in enumerate(restaurants):
                table.setItem(row, 0, QTableWidgetItem(restaurant.name))
                table.setItem(row, 1, QTableWidgetItem(restaurant.cuisine_type))
                table.setItem(row, 2, QTableWidgetItem(f"{restaurant.distance_km:.1f} km"))
                
                safety_item = QTableWidgetItem(f"{restaurant.celiac_friendly_score}/100")
                if restaurant.celiac_friendly_score >= 80:
                    safety_item.setBackground(Qt.green)
                elif restaurant.celiac_friendly_score >= 60:
                    safety_item.setBackground(Qt.yellow)
                else:
                    safety_item.setBackground(Qt.red)
                table.setItem(row, 3, safety_item)
                
                table.setItem(row, 4, QTableWidgetItem(f"{restaurant.rating:.1f}⭐"))
            
            layout.addWidget(table)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(parent_widget, "Error", f"Failed to find restaurants: {str(e)}")
    
    @staticmethod
    def analyze_ingredient_correlations(health_logs, meal_logs, parent_widget):
        """Analyze ingredient-symptom correlations"""
        try:
            if not health_logs or not meal_logs:
                QMessageBox.information(parent_widget, "Insufficient Data", 
                    "Need more health and meal data for correlation analysis.")
                return
            
            results = ingredient_correlator.analyze_ingredient_correlations(health_logs, meal_logs)
            
            # Show results dialog
            dialog = QDialog(parent_widget)
            dialog.setWindowTitle("🔍 Ingredient Correlation Analysis")
            dialog.setModal(True)
            dialog.resize(700, 500)
            
            layout = QVBoxLayout(dialog)
            
            # Summary
            summary = results.get('summary', {})
            summary_text = f"""
📊 Analysis Summary:
• Correlations found: {summary.get('total_correlations_found', 0)}
• High-risk ingredients: {summary.get('high_risk_ingredients', 0)}
• Patterns identified: {summary.get('patterns_identified', 0)}
• Most problematic: {summary.get('most_problematic_ingredient', 'None')}
            """
            
            summary_label = QLabel(summary_text)
            summary_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
            layout.addWidget(summary_label)
            
            # Risk ingredients
            risk_ingredients = results.get('risk_ingredients', [])
            if risk_ingredients:
                risk_label = QLabel("⚠️ Ingredients to Monitor:")
                risk_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
                layout.addWidget(risk_label)
                
                risk_text = ""
                for ingredient in risk_ingredients[:5]:  # Top 5
                    risk_text += f"• {ingredient['ingredient']} ({ingredient['risk_level']})\n"
                
                risk_display = QLabel(risk_text)
                layout.addWidget(risk_display)
            
            # Recommendations
            recommendations = results.get('recommendations', [])
            if recommendations:
                rec_label = QLabel("💡 Recommendations:")
                rec_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
                layout.addWidget(rec_label)
                
                rec_text = ""
                for rec in recommendations[:3]:  # Top 3
                    rec_text += f"• {rec['title']}: {rec['action']}\n"
                
                rec_display = QLabel(rec_text)
                rec_display.setWordWrap(True)
                layout.addWidget(rec_display)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(parent_widget, "Error", f"Failed to analyze correlations: {str(e)}")
    
    @staticmethod
    def optimize_shopping_trip(shopping_list, parent_widget):
        """Optimize shopping trip"""
        try:
            preferred_stores = ['Grocery Store', 'Health Food Store', 'Warehouse Store']
            optimization = smart_shopping_service.optimize_shopping_trip(shopping_list, preferred_stores)
            
            dialog = QDialog(parent_widget)
            dialog.setWindowTitle("🛒 Shopping Trip Optimization")
            dialog.setModal(True)
            dialog.resize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Trip summary
            summary_text = f"""
📊 Optimized Trip Summary:
• Estimated time: {optimization.estimated_time} minutes
• Estimated cost: ${optimization.estimated_cost:.2f}
• Stores to visit: {len(optimization.store_route)}
            """
            
            summary_label = QLabel(summary_text)
            summary_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
            layout.addWidget(summary_label)
            
            # Store route
            if optimization.store_route:
                route_label = QLabel("🗺️ Optimal Store Route:")
                route_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
                layout.addWidget(route_label)
                
                route_text = " → ".join(optimization.store_route)
                route_display = QLabel(route_text)
                layout.addWidget(route_display)
            
            # Money-saving tips
            if optimization.money_saving_tips:
                tips_label = QLabel("💰 Money-Saving Tips:")
                tips_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
                layout.addWidget(tips_label)
                
                tips_text = "\n".join(f"• {tip}" for tip in optimization.money_saving_tips[:3])
                tips_display = QLabel(tips_text)
                tips_display.setWordWrap(True)
                layout.addWidget(tips_display)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(parent_widget, "Error", f"Failed to optimize trip: {str(e)}")


# Global instance
enhanced_features = EnhancedFeatures()