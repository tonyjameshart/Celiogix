# path: services/nutrition_analyzer.py
"""
Professional Nutrition Analysis Service for CeliacShield

Provides comprehensive nutrition calculations and analysis for recipes and meals.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
import json


@dataclass
class NutritionData:
    """Comprehensive nutrition information"""
    calories: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fiber_g: float = 0
    sugar_g: float = 0
    fat_g: float = 0
    saturated_fat_g: float = 0
    sodium_mg: float = 0
    calcium_mg: float = 0
    iron_mg: float = 0
    vitamin_d_mcg: float = 0
    folate_mcg: float = 0
    gluten_free_score: float = 100  # 0-100 safety score


class NutritionAnalyzer:
    """Professional nutrition analysis service"""
    
    def __init__(self):
        self.usda_api_key = "DEMO_KEY"  # Replace with actual API key
        self.nutrition_cache = {}
        
        # Gluten-free nutrition guidelines
        self.gf_guidelines = {
            'fiber_daily_min': 25,  # grams
            'protein_daily_min': 50,  # grams
            'calcium_daily_min': 1000,  # mg
            'iron_daily_min': 18,  # mg
            'folate_daily_min': 400,  # mcg
            'vitamin_d_daily_min': 20  # mcg
        }
    
    def analyze_recipe_nutrition(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze complete nutrition profile of a recipe"""
        total_nutrition = NutritionData()
        ingredient_analysis = []
        
        for ingredient in recipe.get('ingredients', []):
            ing_nutrition = self.get_ingredient_nutrition(ingredient)
            ingredient_analysis.append({
                'ingredient': ingredient.get('name', ''),
                'nutrition': ing_nutrition,
                'gluten_free_verified': self.verify_gluten_free_status(ingredient)
            })
            
            # Add to totals
            total_nutrition.calories += ing_nutrition.calories
            total_nutrition.protein_g += ing_nutrition.protein_g
            total_nutrition.carbs_g += ing_nutrition.carbs_g
            total_nutrition.fiber_g += ing_nutrition.fiber_g
            total_nutrition.fat_g += ing_nutrition.fat_g
            total_nutrition.sodium_mg += ing_nutrition.sodium_mg
            total_nutrition.calcium_mg += ing_nutrition.calcium_mg
            total_nutrition.iron_mg += ing_nutrition.iron_mg
            total_nutrition.folate_mcg += ing_nutrition.folate_mcg
        
        # Calculate per-serving nutrition
        servings = recipe.get('servings', 1)
        per_serving = self._divide_nutrition(total_nutrition, servings)
        
        return {
            'total_nutrition': total_nutrition,
            'per_serving_nutrition': per_serving,
            'ingredient_breakdown': ingredient_analysis,
            'nutrition_score': self._calculate_nutrition_score(per_serving),
            'celiac_safety_score': self._calculate_celiac_safety_score(ingredient_analysis),
            'daily_value_percentages': self._calculate_daily_values(per_serving),
            'nutrition_highlights': self._get_nutrition_highlights(per_serving)
        }
    
    def get_ingredient_nutrition(self, ingredient: Dict[str, Any]) -> NutritionData:
        """Get nutrition data for a single ingredient"""
        ingredient_name = ingredient.get('name', '').lower()
        quantity = float(ingredient.get('quantity', 1))
        
        # Check cache first
        cache_key = f"{ingredient_name}_{quantity}"
        if cache_key in self.nutrition_cache:
            return self.nutrition_cache[cache_key]
        
        # Try USDA FoodData Central API
        nutrition_data = self._query_usda_nutrition(ingredient_name, quantity)
        
        if not nutrition_data:
            # Fallback to built-in nutrition database
            nutrition_data = self._get_builtin_nutrition(ingredient_name, quantity)
        
        # Cache result
        self.nutrition_cache[cache_key] = nutrition_data
        return nutrition_data
    
    def _query_usda_nutrition(self, ingredient_name: str, quantity: float) -> Optional[NutritionData]:
        """Query USDA FoodData Central for nutrition information"""
        try:
            # Search for food item
            search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search"
            search_params = {
                'query': ingredient_name,
                'api_key': self.usda_api_key,
                'pageSize': 1
            }
            
            response = requests.get(search_url, params=search_params, timeout=5)
            if response.status_code != 200:
                return None
            
            search_data = response.json()
            if not search_data.get('foods'):
                return None
            
            # Get detailed nutrition for first result
            food_id = search_data['foods'][0]['fdcId']
            detail_url = f"https://api.nal.usda.gov/fdc/v1/food/{food_id}"
            detail_params = {'api_key': self.usda_api_key}
            
            detail_response = requests.get(detail_url, params=detail_params, timeout=5)
            if detail_response.status_code != 200:
                return None
            
            food_data = detail_response.json()
            return self._parse_usda_nutrition(food_data, quantity)
            
        except Exception as e:
            print(f"USDA API error for {ingredient_name}: {e}")
            return None
    
    def _parse_usda_nutrition(self, food_data: Dict, quantity: float) -> NutritionData:
        """Parse USDA nutrition data"""
        nutrition = NutritionData()
        
        # Map USDA nutrient IDs to our fields
        nutrient_map = {
            1008: 'calories',      # Energy
            1003: 'protein_g',     # Protein
            1005: 'carbs_g',       # Carbohydrate
            1079: 'fiber_g',       # Fiber
            1063: 'sugar_g',       # Sugars
            1004: 'fat_g',         # Total lipid (fat)
            1258: 'saturated_fat_g', # Saturated fatty acids
            1093: 'sodium_mg',     # Sodium
            1087: 'calcium_mg',    # Calcium
            1089: 'iron_mg',       # Iron
            1114: 'vitamin_d_mcg', # Vitamin D
            1177: 'folate_mcg'     # Folate
        }
        
        for nutrient in food_data.get('foodNutrients', []):
            nutrient_id = nutrient.get('nutrient', {}).get('id')
            if nutrient_id in nutrient_map:
                field_name = nutrient_map[nutrient_id]
                value = nutrient.get('amount', 0) * quantity / 100  # Per 100g to actual quantity
                setattr(nutrition, field_name, value)
        
        return nutrition
    
    def _get_builtin_nutrition(self, ingredient_name: str, quantity: float) -> NutritionData:
        """Get nutrition from built-in database"""
        # Simplified nutrition database for common GF ingredients
        nutrition_db = {
            'rice flour': NutritionData(calories=366, protein_g=5.9, carbs_g=80.1, fiber_g=2.4, fat_g=1.4),
            'almond flour': NutritionData(calories=571, protein_g=21.2, carbs_g=21.7, fiber_g=12.5, fat_g=49.9),
            'quinoa': NutritionData(calories=368, protein_g=14.1, carbs_g=64.2, fiber_g=7.0, fat_g=6.1),
            'gluten-free oats': NutritionData(calories=389, protein_g=16.9, carbs_g=66.3, fiber_g=10.6, fat_g=6.9),
            'coconut flour': NutritionData(calories=400, protein_g=19.3, carbs_g=60.8, fiber_g=38.5, fat_g=13.3),
            'chicken breast': NutritionData(calories=165, protein_g=31.0, carbs_g=0, fiber_g=0, fat_g=3.6),
            'salmon': NutritionData(calories=208, protein_g=25.4, carbs_g=0, fiber_g=0, fat_g=12.4),
            'eggs': NutritionData(calories=155, protein_g=13.0, carbs_g=1.1, fiber_g=0, fat_g=10.6),
            'spinach': NutritionData(calories=23, protein_g=2.9, carbs_g=3.6, fiber_g=2.2, fat_g=0.4),
            'sweet potato': NutritionData(calories=86, protein_g=1.6, carbs_g=20.1, fiber_g=3.0, fat_g=0.1)
        }
        
        base_nutrition = nutrition_db.get(ingredient_name, NutritionData())
        
        # Scale by quantity (assuming per 100g base values)
        scale_factor = quantity / 100
        return NutritionData(
            calories=base_nutrition.calories * scale_factor,
            protein_g=base_nutrition.protein_g * scale_factor,
            carbs_g=base_nutrition.carbs_g * scale_factor,
            fiber_g=base_nutrition.fiber_g * scale_factor,
            fat_g=base_nutrition.fat_g * scale_factor,
            sodium_mg=base_nutrition.sodium_mg * scale_factor,
            calcium_mg=base_nutrition.calcium_mg * scale_factor,
            iron_mg=base_nutrition.iron_mg * scale_factor,
            folate_mcg=base_nutrition.folate_mcg * scale_factor
        )
    
    def verify_gluten_free_status(self, ingredient: Dict[str, Any]) -> Dict[str, Any]:
        """Verify gluten-free status of ingredient"""
        ingredient_name = ingredient.get('name', '').lower()
        
        # High-risk ingredients
        gluten_risks = {
            'wheat': {'risk': 'high', 'reason': 'Contains gluten protein'},
            'barley': {'risk': 'high', 'reason': 'Contains gluten protein'},
            'rye': {'risk': 'high', 'reason': 'Contains gluten protein'},
            'oats': {'risk': 'medium', 'reason': 'Cross-contamination risk - use certified GF'},
            'soy sauce': {'risk': 'high', 'reason': 'Usually contains wheat - use tamari'},
            'beer': {'risk': 'high', 'reason': 'Made from barley - use GF beer'}
        }
        
        for risk_ingredient, risk_info in gluten_risks.items():
            if risk_ingredient in ingredient_name:
                return {
                    'verified_gluten_free': False,
                    'risk_level': risk_info['risk'],
                    'warning': risk_info['reason'],
                    'alternatives': self._get_gf_alternatives(risk_ingredient)
                }
        
        return {
            'verified_gluten_free': True,
            'risk_level': 'low',
            'warning': None,
            'alternatives': []
        }
    
    def _get_gf_alternatives(self, ingredient: str) -> List[str]:
        """Get gluten-free alternatives for risky ingredients"""
        alternatives = {
            'wheat': ['rice flour', 'almond flour', 'GF flour blend'],
            'barley': ['rice', 'quinoa', 'millet'],
            'rye': ['rice flour', 'buckwheat flour'],
            'oats': ['certified GF oats', 'quinoa flakes'],
            'soy sauce': ['tamari (GF)', 'coconut aminos'],
            'beer': ['GF beer', 'hard cider', 'wine']
        }
        return alternatives.get(ingredient, [])
    
    def _calculate_nutrition_score(self, nutrition: NutritionData) -> int:
        """Calculate overall nutrition score (0-100)"""
        score = 50  # Base score
        
        # Protein bonus
        if nutrition.protein_g >= 20:
            score += 15
        elif nutrition.protein_g >= 10:
            score += 10
        
        # Fiber bonus
        if nutrition.fiber_g >= 5:
            score += 15
        elif nutrition.fiber_g >= 3:
            score += 10
        
        # Healthy fats
        if 10 <= nutrition.fat_g <= 35:
            score += 10
        
        # Low sodium bonus
        if nutrition.sodium_mg < 600:
            score += 10
        
        # Penalties
        if nutrition.sodium_mg > 1500:
            score -= 15
        if nutrition.sugar_g > 25:
            score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_celiac_safety_score(self, ingredient_analysis: List[Dict]) -> int:
        """Calculate celiac safety score based on ingredients"""
        total_score = 100
        
        for analysis in ingredient_analysis:
            if not analysis['gluten_free_verified']['verified_gluten_free']:
                risk_level = analysis['gluten_free_verified']['risk_level']
                if risk_level == 'high':
                    total_score -= 50
                elif risk_level == 'medium':
                    total_score -= 25
                else:
                    total_score -= 10
        
        return max(0, total_score)
    
    def _calculate_daily_values(self, nutrition: NutritionData) -> Dict[str, float]:
        """Calculate daily value percentages"""
        return {
            'fiber': (nutrition.fiber_g / self.gf_guidelines['fiber_daily_min']) * 100,
            'protein': (nutrition.protein_g / self.gf_guidelines['protein_daily_min']) * 100,
            'calcium': (nutrition.calcium_mg / self.gf_guidelines['calcium_daily_min']) * 100,
            'iron': (nutrition.iron_mg / self.gf_guidelines['iron_daily_min']) * 100,
            'folate': (nutrition.folate_mcg / self.gf_guidelines['folate_daily_min']) * 100
        }
    
    def _get_nutrition_highlights(self, nutrition: NutritionData) -> List[str]:
        """Get nutrition highlights for display"""
        highlights = []
        
        if nutrition.protein_g >= 20:
            highlights.append("High in protein")
        if nutrition.fiber_g >= 5:
            highlights.append("Excellent source of fiber")
        if nutrition.iron_mg >= 3:
            highlights.append("Good source of iron")
        if nutrition.calcium_mg >= 200:
            highlights.append("Rich in calcium")
        if nutrition.folate_mcg >= 80:
            highlights.append("Good source of folate")
        
        return highlights
    
    def _divide_nutrition(self, nutrition: NutritionData, servings: int) -> NutritionData:
        """Divide nutrition data by number of servings"""
        return NutritionData(
            calories=nutrition.calories / servings,
            protein_g=nutrition.protein_g / servings,
            carbs_g=nutrition.carbs_g / servings,
            fiber_g=nutrition.fiber_g / servings,
            sugar_g=nutrition.sugar_g / servings,
            fat_g=nutrition.fat_g / servings,
            saturated_fat_g=nutrition.saturated_fat_g / servings,
            sodium_mg=nutrition.sodium_mg / servings,
            calcium_mg=nutrition.calcium_mg / servings,
            iron_mg=nutrition.iron_mg / servings,
            vitamin_d_mcg=nutrition.vitamin_d_mcg / servings,
            folate_mcg=nutrition.folate_mcg / servings
        )


# Global instance
nutrition_analyzer = NutritionAnalyzer()