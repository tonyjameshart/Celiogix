# path: services/smart_shopping.py
"""
Smart Shopping Service for CeliacShield

Provides intelligent product suggestions and shopping optimization for gluten-free needs.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json


@dataclass
class ProductSuggestion:
    """Smart product suggestion"""
    product_name: str
    brand: str
    category: str
    confidence_score: float  # 0-1 how confident we are in this suggestion
    reason: str  # Why this product is suggested
    price_range: str
    availability: str
    gluten_free_certified: bool
    nutritional_benefits: List[str]
    user_preference_match: float  # 0-1 how well it matches user preferences


@dataclass
class ShoppingOptimization:
    """Shopping trip optimization"""
    store_route: List[str]  # Optimal store order
    category_order: List[str]  # Optimal category order within store
    estimated_time: int  # Minutes
    estimated_cost: float
    money_saving_tips: List[str]
    bulk_buy_suggestions: List[str]


class SmartShoppingService:
    """Intelligent shopping suggestions and optimization"""
    
    def __init__(self):
        # Product database with gluten-free focus
        self.gf_product_database = {
            'bread': [
                {'name': 'Gluten-Free Sandwich Bread', 'brand': "Udi's", 'price': 4.99, 'rating': 4.2},
                {'name': 'Artisan GF Bread', 'brand': 'Canyon Bakehouse', 'price': 5.49, 'rating': 4.5},
                {'name': 'Soft White Bread', 'brand': 'Schar', 'price': 4.79, 'rating': 4.0}
            ],
            'pasta': [
                {'name': 'GF Penne', 'brand': 'Barilla', 'price': 2.99, 'rating': 4.3},
                {'name': 'Brown Rice Pasta', 'brand': 'Jovial', 'price': 3.49, 'rating': 4.4},
                {'name': 'Chickpea Pasta', 'brand': 'Banza', 'price': 3.99, 'rating': 4.1}
            ],
            'flour': [
                {'name': 'GF All-Purpose Flour', 'brand': 'King Arthur', 'price': 6.99, 'rating': 4.6},
                {'name': '1-to-1 Baking Flour', 'brand': "Bob's Red Mill", 'price': 5.99, 'rating': 4.3},
                {'name': 'Cup4Cup Flour', 'brand': 'Cup4Cup', 'price': 8.99, 'rating': 4.7}
            ],
            'snacks': [
                {'name': 'GF Crackers', 'brand': 'Mary\'s Gone Crackers', 'price': 4.49, 'rating': 4.2},
                {'name': 'Rice Cakes', 'brand': 'Lundberg', 'price': 3.99, 'rating': 4.0},
                {'name': 'GF Pretzels', 'brand': 'Snyder\'s of Hanover', 'price': 3.79, 'rating': 4.1}
            ]
        }
        
        # Store layouts for optimization
        self.store_layouts = {
            'grocery_store': ['produce', 'dairy', 'meat', 'frozen', 'pantry', 'bakery', 'health'],
            'health_food_store': ['supplements', 'produce', 'refrigerated', 'pantry', 'frozen', 'personal_care'],
            'warehouse_store': ['produce', 'meat', 'dairy', 'frozen', 'pantry', 'household']
        }
        
        # Nutritional priorities for celiacs
        self.celiac_nutrition_priorities = {
            'fiber': 8,      # High priority - often deficient
            'iron': 9,       # Very high - absorption issues
            'calcium': 8,    # High - dairy alternatives needed
            'b_vitamins': 9, # Very high - fortified grains avoided
            'vitamin_d': 7,  # Medium-high - absorption issues
            'protein': 6     # Medium - generally adequate
        }
    
    def generate_smart_suggestions(self, shopping_list: List[Dict], 
                                 user_preferences: Dict[str, Any],
                                 purchase_history: List[Dict]) -> List[ProductSuggestion]:
        """Generate intelligent product suggestions"""
        suggestions = []
        
        # Analyze current shopping list
        for item in shopping_list:
            item_name = item.get('item_name', '').lower()
            category = item.get('category', '').lower()
            
            # Get category-based suggestions
            category_suggestions = self._get_category_suggestions(category, user_preferences)
            suggestions.extend(category_suggestions)
            
            # Get item-specific suggestions
            item_suggestions = self._get_item_suggestions(item_name, user_preferences, purchase_history)
            suggestions.extend(item_suggestions)
        
        # Add nutritional gap suggestions
        nutrition_suggestions = self._suggest_nutritional_gaps(shopping_list, user_preferences)
        suggestions.extend(nutrition_suggestions)
        
        # Add seasonal/promotional suggestions
        seasonal_suggestions = self._get_seasonal_suggestions(user_preferences)
        suggestions.extend(seasonal_suggestions)
        
        # Remove duplicates and sort by confidence
        suggestions = self._deduplicate_suggestions(suggestions)
        suggestions.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return suggestions[:15]  # Return top 15 suggestions
    
    def _get_category_suggestions(self, category: str, 
                                user_preferences: Dict[str, Any]) -> List[ProductSuggestion]:
        """Get suggestions based on product category"""
        suggestions = []
        
        if category in self.gf_product_database:
            products = self.gf_product_database[category]
            
            for product in products:
                # Calculate confidence based on rating and user preferences
                confidence = self._calculate_product_confidence(product, user_preferences)
                
                if confidence >= 0.6:  # Only suggest high-confidence products
                    suggestion = ProductSuggestion(
                        product_name=product['name'],
                        brand=product['brand'],
                        category=category,
                        confidence_score=confidence,
                        reason=f"Highly rated {category} option",
                        price_range=self._get_price_range(product['price']),
                        availability="Widely available",
                        gluten_free_certified=True,
                        nutritional_benefits=self._get_nutritional_benefits(category),
                        user_preference_match=self._calculate_preference_match(product, user_preferences)
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _get_item_suggestions(self, item_name: str, user_preferences: Dict[str, Any],
                           purchase_history: List[Dict]) -> List[ProductSuggestion]:
        """Get suggestions for specific item"""
        suggestions = []
        
        # Check purchase history for patterns
        similar_purchases = [p for p in purchase_history 
                           if item_name in p.get('item_name', '').lower()]
        
        if similar_purchases:
            # Suggest based on purchase patterns
            most_bought_brand = self._get_most_frequent_brand(similar_purchases)
            if most_bought_brand:
                suggestion = ProductSuggestion(
                    product_name=f"{most_bought_brand} {item_name}",
                    brand=most_bought_brand,
                    category=self._categorize_item(item_name),
                    confidence_score=0.8,
                    reason="Based on your purchase history",
                    price_range="$",
                    availability="Previously purchased",
                    gluten_free_certified=True,
                    nutritional_benefits=[],
                    user_preference_match=0.9
                )
                suggestions.append(suggestion)
        
        # Suggest alternatives based on item type
        alternatives = self._get_item_alternatives(item_name)
        for alt in alternatives:
            suggestion = ProductSuggestion(
                product_name=alt['name'],
                brand=alt['brand'],
                category=self._categorize_item(item_name),
                confidence_score=0.7,
                reason=f"Alternative to {item_name}",
                price_range=self._get_price_range(alt.get('price', 5.0)),
                availability="Check availability",
                gluten_free_certified=True,
                nutritional_benefits=alt.get('benefits', []),
                user_preference_match=0.6
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _suggest_nutritional_gaps(self, shopping_list: List[Dict],
                                user_preferences: Dict[str, Any]) -> List[ProductSuggestion]:
        """Suggest products to fill nutritional gaps"""
        suggestions = []
        
        # Analyze current list for nutritional content
        current_nutrition = self._analyze_list_nutrition(shopping_list)
        
        # Identify gaps based on celiac nutritional needs
        gaps = []
        for nutrient, priority in self.celiac_nutrition_priorities.items():
            if current_nutrition.get(nutrient, 0) < priority:
                gaps.append(nutrient)
        
        # Suggest products to fill gaps
        for gap in gaps:
            gap_products = self._get_nutrient_rich_products(gap)
            for product in gap_products:
                suggestion = ProductSuggestion(
                    product_name=product['name'],
                    brand=product['brand'],
                    category=product['category'],
                    confidence_score=0.75,
                    reason=f"Rich in {gap} - important for celiac health",
                    price_range=self._get_price_range(product.get('price', 4.0)),
                    availability="Health food stores",
                    gluten_free_certified=True,
                    nutritional_benefits=[f"High in {gap}"],
                    user_preference_match=0.6
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _get_seasonal_suggestions(self, user_preferences: Dict[str, Any]) -> List[ProductSuggestion]:
        """Get seasonal product suggestions"""
        suggestions = []
        current_month = datetime.now().month
        
        # Seasonal suggestions
        seasonal_products = {
            'winter': [
                {'name': 'GF Hot Chocolate Mix', 'brand': 'Swiss Miss', 'category': 'beverages'},
                {'name': 'GF Soup Mix', 'brand': 'Pacific Foods', 'category': 'pantry'}
            ],
            'spring': [
                {'name': 'Fresh Asparagus', 'brand': 'Local Farm', 'category': 'produce'},
                {'name': 'GF Granola', 'brand': 'Kind', 'category': 'breakfast'}
            ],
            'summer': [
                {'name': 'GF Ice Cream', 'brand': 'Ben & Jerry\'s', 'category': 'frozen'},
                {'name': 'Fresh Berries', 'brand': 'Local Farm', 'category': 'produce'}
            ],
            'fall': [
                {'name': 'GF Pumpkin Bread Mix', 'brand': 'King Arthur', 'category': 'baking'},
                {'name': 'Butternut Squash', 'brand': 'Local Farm', 'category': 'produce'}
            ]
        }
        
        # Determine season
        if current_month in [12, 1, 2]:
            season = 'winter'
        elif current_month in [3, 4, 5]:
            season = 'spring'
        elif current_month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'fall'
        
        for product in seasonal_products.get(season, []):
            suggestion = ProductSuggestion(
                product_name=product['name'],
                brand=product['brand'],
                category=product['category'],
                confidence_score=0.65,
                reason=f"Seasonal {season} item",
                price_range="$",
                availability="Seasonal availability",
                gluten_free_certified=True,
                nutritional_benefits=[],
                user_preference_match=0.5
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def optimize_shopping_trip(self, shopping_list: List[Dict],
                             preferred_stores: List[str]) -> ShoppingOptimization:
        """Optimize shopping trip for efficiency"""
        
        # Group items by store type
        store_assignments = self._assign_items_to_stores(shopping_list, preferred_stores)
        
        # Optimize store order (closest first, then by item availability)
        optimal_store_order = self._optimize_store_order(store_assignments, preferred_stores)
        
        # Optimize category order within each store
        category_orders = {}
        for store in optimal_store_order:
            if store in self.store_layouts:
                store_items = store_assignments.get(store, [])
                category_orders[store] = self._optimize_category_order(store_items, store)
        
        # Calculate estimates
        estimated_time = self._estimate_shopping_time(store_assignments, optimal_store_order)
        estimated_cost = self._estimate_shopping_cost(shopping_list)
        
        # Generate money-saving tips
        money_tips = self._generate_money_saving_tips(shopping_list, store_assignments)
        
        # Generate bulk buying suggestions
        bulk_suggestions = self._generate_bulk_suggestions(shopping_list)
        
        return ShoppingOptimization(
            store_route=optimal_store_order,
            category_order=category_orders.get(optimal_store_order[0], []) if optimal_store_order else [],
            estimated_time=estimated_time,
            estimated_cost=estimated_cost,
            money_saving_tips=money_tips,
            bulk_buy_suggestions=bulk_suggestions
        )
    
    def _assign_items_to_stores(self, shopping_list: List[Dict], 
                              preferred_stores: List[str]) -> Dict[str, List[Dict]]:
        """Assign items to optimal stores"""
        assignments = {store: [] for store in preferred_stores}
        
        for item in shopping_list:
            category = item.get('category', '').lower()
            
            # Assign based on category and store specialization
            if category in ['health', 'supplements', 'organic']:
                if 'Health Food Store' in preferred_stores:
                    assignments['Health Food Store'].append(item)
                else:
                    assignments[preferred_stores[0]].append(item)
            elif category in ['bulk', 'household']:
                if 'Warehouse Store' in preferred_stores:
                    assignments['Warehouse Store'].append(item)
                else:
                    assignments[preferred_stores[0]].append(item)
            else:
                # Default to first preferred store (usually grocery store)
                assignments[preferred_stores[0]].append(item)
        
        return assignments
    
    def _optimize_store_order(self, store_assignments: Dict[str, List[Dict]], 
                            preferred_stores: List[str]) -> List[str]:
        """Optimize order of store visits"""
        # Simple optimization: visit stores with most items first
        store_item_counts = {store: len(items) for store, items in store_assignments.items() if items}
        
        # Sort by item count (descending)
        optimal_order = sorted(store_item_counts.keys(), 
                             key=lambda x: store_item_counts[x], reverse=True)
        
        return optimal_order
    
    def _optimize_category_order(self, items: List[Dict], store: str) -> List[str]:
        """Optimize category order within store"""
        if store not in self.store_layouts:
            return []
        
        # Get categories present in shopping list
        item_categories = set(item.get('category', '').lower() for item in items)
        
        # Filter store layout to only include categories we need
        optimal_order = [cat for cat in self.store_layouts[store] if cat in item_categories]
        
        return optimal_order
    
    def _estimate_shopping_time(self, store_assignments: Dict[str, List[Dict]], 
                              store_order: List[str]) -> int:
        """Estimate total shopping time in minutes"""
        base_time_per_store = 15  # Base time for entering/exiting store
        time_per_item = 2  # Minutes per item
        travel_time_between_stores = 10  # Minutes between stores
        
        total_time = 0
        
        for i, store in enumerate(store_order):
            items = store_assignments.get(store, [])
            store_time = base_time_per_store + (len(items) * time_per_item)
            total_time += store_time
            
            # Add travel time (except for last store)
            if i < len(store_order) - 1:
                total_time += travel_time_between_stores
        
        return total_time
    
    def _estimate_shopping_cost(self, shopping_list: List[Dict]) -> float:
        """Estimate total shopping cost"""
        total_cost = 0
        
        for item in shopping_list:
            category = item.get('category', '').lower()
            quantity = item.get('quantity', '1')
            
            # Extract numeric quantity
            try:
                qty_num = float(''.join(filter(str.isdigit, str(quantity))))
                if qty_num == 0:
                    qty_num = 1
            except:
                qty_num = 1
            
            # Estimate price based on category
            category_prices = {
                'produce': 3.0,
                'meat': 8.0,
                'dairy': 4.0,
                'pantry': 5.0,
                'frozen': 6.0,
                'bakery': 5.0,
                'health': 7.0
            }
            
            estimated_price = category_prices.get(category, 5.0) * qty_num
            total_cost += estimated_price
        
        return round(total_cost, 2)
    
    def _generate_money_saving_tips(self, shopping_list: List[Dict],
                                  store_assignments: Dict[str, List[Dict]]) -> List[str]:
        """Generate money-saving tips"""
        tips = []
        
        # Generic money-saving tips
        tips.extend([
            "Check store apps for digital coupons before shopping",
            "Compare unit prices, not just package prices",
            "Consider store brands for basic items",
            "Shop sales and stock up on non-perishables"
        ])
        
        # Category-specific tips
        categories = set(item.get('category', '') for item in shopping_list)
        
        if 'produce' in categories:
            tips.append("Buy seasonal produce for better prices")
        
        if 'meat' in categories:
            tips.append("Buy meat in bulk and freeze portions")
        
        if 'pantry' in categories:
            tips.append("Stock up on GF pantry staples during sales")
        
        return tips[:5]  # Return top 5 tips
    
    def _generate_bulk_suggestions(self, shopping_list: List[Dict]) -> List[str]:
        """Generate bulk buying suggestions"""
        suggestions = []
        
        # Items that are good for bulk buying
        bulk_friendly_categories = ['pantry', 'frozen', 'health', 'household']
        bulk_friendly_items = ['rice', 'quinoa', 'flour', 'pasta', 'canned goods']
        
        for item in shopping_list:
            category = item.get('category', '').lower()
            item_name = item.get('item_name', '').lower()
            
            if (category in bulk_friendly_categories or 
                any(bulk_item in item_name for bulk_item in bulk_friendly_items)):
                suggestions.append(f"Consider buying {item.get('item_name', '')} in bulk")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    # Helper methods
    def _calculate_product_confidence(self, product: Dict, user_preferences: Dict) -> float:
        """Calculate confidence score for product suggestion"""
        base_confidence = 0.5
        
        # Rating bonus
        rating = product.get('rating', 0)
        if rating >= 4.5:
            base_confidence += 0.3
        elif rating >= 4.0:
            base_confidence += 0.2
        elif rating >= 3.5:
            base_confidence += 0.1
        
        # Price preference
        price = product.get('price', 0)
        max_price = user_preferences.get('max_price_per_item', 10.0)
        if price <= max_price:
            base_confidence += 0.2
        
        return min(1.0, base_confidence)
    
    def _get_price_range(self, price: float) -> str:
        """Convert price to range string"""
        if price < 3.0:
            return "$"
        elif price < 6.0:
            return "$$"
        elif price < 10.0:
            return "$$$"
        else:
            return "$$$$"
    
    def _get_nutritional_benefits(self, category: str) -> List[str]:
        """Get nutritional benefits for category"""
        benefits = {
            'bread': ['Carbohydrates', 'B vitamins (if fortified)'],
            'pasta': ['Carbohydrates', 'Protein (if legume-based)'],
            'flour': ['Versatile baking', 'Protein (if almond/coconut)'],
            'snacks': ['Convenient energy', 'Fiber (if whole grain)']
        }
        return benefits.get(category, [])
    
    def _calculate_preference_match(self, product: Dict, user_preferences: Dict) -> float:
        """Calculate how well product matches user preferences"""
        match_score = 0.5  # Base score
        
        # Brand preference
        preferred_brands = user_preferences.get('preferred_brands', [])
        if product.get('brand') in preferred_brands:
            match_score += 0.3
        
        # Price preference
        max_price = user_preferences.get('max_price_per_item', 10.0)
        if product.get('price', 0) <= max_price:
            match_score += 0.2
        
        return min(1.0, match_score)
    
    def _get_most_frequent_brand(self, purchases: List[Dict]) -> Optional[str]:
        """Get most frequently purchased brand"""
        brand_counts = {}
        for purchase in purchases:
            brand = purchase.get('brand', '')
            if brand:
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        if brand_counts:
            return max(brand_counts, key=brand_counts.get)
        return None
    
    def _categorize_item(self, item_name: str) -> str:
        """Categorize item based on name"""
        item_lower = item_name.lower()
        
        if any(word in item_lower for word in ['bread', 'bagel', 'muffin']):
            return 'bakery'
        elif any(word in item_lower for word in ['pasta', 'noodle', 'spaghetti']):
            return 'pasta'
        elif any(word in item_lower for word in ['flour', 'mix', 'baking']):
            return 'baking'
        elif any(word in item_lower for word in ['snack', 'chip', 'cracker']):
            return 'snacks'
        else:
            return 'pantry'
    
    def _get_item_alternatives(self, item_name: str) -> List[Dict]:
        """Get alternatives for specific item"""
        alternatives = {
            'bread': [
                {'name': 'Rice Cakes', 'brand': 'Lundberg', 'benefits': ['Low calorie', 'Versatile']},
                {'name': 'Corn Tortillas', 'brand': 'Mission', 'benefits': ['Naturally GF', 'Flexible']}
            ],
            'pasta': [
                {'name': 'Zucchini Noodles', 'brand': 'Fresh', 'benefits': ['Low carb', 'High nutrients']},
                {'name': 'Shirataki Noodles', 'brand': 'Miracle Noodle', 'benefits': ['Very low calorie']}
            ]
        }
        
        for key in alternatives:
            if key in item_name.lower():
                return alternatives[key]
        
        return []
    
    def _analyze_list_nutrition(self, shopping_list: List[Dict]) -> Dict[str, int]:
        """Analyze nutritional content of shopping list"""
        nutrition_scores = {
            'fiber': 0,
            'iron': 0,
            'calcium': 0,
            'b_vitamins': 0,
            'vitamin_d': 0,
            'protein': 0
        }
        
        # Simple scoring based on categories
        for item in shopping_list:
            category = item.get('category', '').lower()
            
            if category == 'produce':
                nutrition_scores['fiber'] += 2
                nutrition_scores['vitamin_d'] += 1
            elif category == 'meat':
                nutrition_scores['protein'] += 3
                nutrition_scores['iron'] += 2
            elif category == 'dairy':
                nutrition_scores['calcium'] += 3
                nutrition_scores['protein'] += 1
            elif 'fortified' in item.get('item_name', '').lower():
                nutrition_scores['b_vitamins'] += 2
                nutrition_scores['iron'] += 1
        
        return nutrition_scores
    
    def _get_nutrient_rich_products(self, nutrient: str) -> List[Dict]:
        """Get products rich in specific nutrient"""
        nutrient_products = {
            'fiber': [
                {'name': 'GF High-Fiber Cereal', 'brand': 'Nature\'s Path', 'category': 'breakfast'},
                {'name': 'Chia Seeds', 'brand': 'Spectrum', 'category': 'health'}
            ],
            'iron': [
                {'name': 'Iron-Fortified GF Cereal', 'brand': 'General Mills', 'category': 'breakfast'},
                {'name': 'Spinach', 'brand': 'Fresh', 'category': 'produce'}
            ],
            'calcium': [
                {'name': 'Fortified Almond Milk', 'brand': 'Silk', 'category': 'dairy'},
                {'name': 'Sardines', 'brand': 'Wild Planet', 'category': 'pantry'}
            ],
            'b_vitamins': [
                {'name': 'Nutritional Yeast', 'brand': 'Bragg', 'category': 'health'},
                {'name': 'B-Complex Supplement', 'brand': 'Nature Made', 'category': 'supplements'}
            ]
        }
        
        return nutrient_products.get(nutrient, [])
    
    def _deduplicate_suggestions(self, suggestions: List[ProductSuggestion]) -> List[ProductSuggestion]:
        """Remove duplicate suggestions"""
        seen = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            key = (suggestion.product_name.lower(), suggestion.brand.lower())
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions


# Global instance
smart_shopping_service = SmartShoppingService()