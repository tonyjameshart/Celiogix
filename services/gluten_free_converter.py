# path: services/gluten_free_converter.py
"""
Gluten-Free Recipe Converter Service

Analyzes recipe ingredients and suggests gluten-free alternatives.
"""

from typing import Dict, List, Any, Optional
import re


class GlutenFreeConverter:
    """Service to convert recipes to gluten-free alternatives"""
    
    def __init__(self):
        self.gluten_ingredients = {
            # Wheat-based ingredients
            'wheat flour': 'gluten-free flour blend',
            'all-purpose flour': 'gluten-free flour blend',
            'bread flour': 'gluten-free bread flour',
            'cake flour': 'gluten-free cake flour',
            'pastry flour': 'gluten-free pastry flour',
            'whole wheat flour': 'gluten-free whole grain flour',
            'wheat': 'quinoa or rice',
            'wheat berries': 'quinoa or rice',
            'wheat germ': 'ground flaxseed',
            'wheat bran': 'rice bran or oat bran',
            
            # Barley-based ingredients
            'barley': 'quinoa or rice',
            'barley flour': 'gluten-free flour blend',
            'pearl barley': 'quinoa or rice',
            'barley malt': 'rice malt or maple syrup',
            'malt extract': 'rice malt or maple syrup',
            'malt vinegar': 'apple cider vinegar',
            
            # Rye-based ingredients
            'rye flour': 'gluten-free flour blend',
            'rye': 'quinoa or rice',
            'rye bread': 'gluten-free bread',
            
            # Other gluten-containing ingredients
            'semolina': 'cornmeal or polenta',
            'durum': 'gluten-free pasta',
            'bulgur': 'quinoa or rice',
            'couscous': 'quinoa or rice',
            'spelt': 'quinoa or rice',
            'kamut': 'quinoa or rice',
            'triticale': 'quinoa or rice',
            'farro': 'quinoa or rice',
            'einkorn': 'quinoa or rice',
            
            # Processed ingredients that may contain gluten
            'soy sauce': 'tamari (gluten-free soy sauce)',
            'teriyaki sauce': 'gluten-free teriyaki sauce',
            'worcestershire sauce': 'gluten-free worcestershire sauce',
            'maltodextrin': 'potato starch or cornstarch',
            'modified food starch': 'potato starch or cornstarch',
            'hydrolyzed vegetable protein': 'gluten-free vegetable protein',
            'textured vegetable protein': 'gluten-free vegetable protein',
            'seitan': 'tempeh or tofu',
            'imitation crab': 'real crab or shrimp',
            'beer': 'gluten-free beer or wine',
            'ale': 'gluten-free beer',
            'lager': 'gluten-free beer',
            'stout': 'gluten-free beer',
        }
        
        self.gluten_free_flours = [
            'almond flour', 'coconut flour', 'rice flour', 'tapioca flour',
            'potato starch', 'cornstarch', 'arrowroot powder', 'xanthan gum',
            'guar gum', 'psyllium husk powder', 'buckwheat flour', 'quinoa flour',
            'millet flour', 'sorghum flour', 'teff flour', 'amaranth flour'
        ]
        
        self.gluten_free_binders = [
            'xanthan gum', 'guar gum', 'psyllium husk powder', 'chia seeds',
            'flax seeds', 'eggs', 'applesauce', 'banana', 'yogurt'
        ]
    
    def analyze_recipe(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze recipe and suggest gluten-free alternatives"""
        ingredients = recipe_data.get('ingredients', [])
        
        analysis = {
            'has_gluten': False,
            'gluten_ingredients': [],
            'suggested_replacements': [],
            'conversion_notes': [],
            'difficulty_level': 'Easy',
            'estimated_cost_change': 'Minimal'
        }
        
        for ingredient in ingredients:
            if isinstance(ingredient, dict):
                ingredient_name = ingredient.get('name', '').lower()
                amount = ingredient.get('amount', '')
            else:
                ingredient_name = str(ingredient).lower()
                amount = ''
            
            # Check if ingredient contains gluten
            gluten_match = self._find_gluten_ingredient(ingredient_name)
            if gluten_match:
                analysis['has_gluten'] = True
                analysis['gluten_ingredients'].append({
                    'original': ingredient_name,
                    'amount': amount,
                    'replacement': gluten_match,
                    'category': self._categorize_ingredient(ingredient_name)
                })
                
                analysis['suggested_replacements'].append({
                    'original': f"{amount} {ingredient_name}" if amount else ingredient_name,
                    'replacement': f"{amount} {gluten_match}" if amount else gluten_match,
                    'notes': self._get_replacement_notes(ingredient_name, gluten_match)
                })
        
        # Add conversion notes
        if analysis['has_gluten']:
            analysis['conversion_notes'] = self._generate_conversion_notes(analysis)
            analysis['difficulty_level'] = self._assess_difficulty(analysis)
            analysis['estimated_cost_change'] = self._estimate_cost_change(analysis)
        
        return analysis
    
    def _find_gluten_ingredient(self, ingredient_name: str) -> Optional[str]:
        """Find if ingredient contains gluten and suggest replacement"""
        ingredient_name = ingredient_name.lower().strip()
        
        # Direct match
        if ingredient_name in self.gluten_ingredients:
            return self.gluten_ingredients[ingredient_name]
        
        # Partial match for compound ingredients
        for gluten_ingredient, replacement in self.gluten_ingredients.items():
            if gluten_ingredient in ingredient_name:
                return replacement
        
        # Check for flour patterns
        if 'flour' in ingredient_name and not any(gf in ingredient_name for gf in self.gluten_free_flours):
            return 'gluten-free flour blend'
        
        return None
    
    def _categorize_ingredient(self, ingredient_name: str) -> str:
        """Categorize the gluten ingredient"""
        if 'flour' in ingredient_name:
            return 'Flour'
        elif any(grain in ingredient_name for grain in ['wheat', 'barley', 'rye', 'spelt', 'kamut']):
            return 'Grain'
        elif 'sauce' in ingredient_name:
            return 'Sauce/Condiment'
        elif ingredient_name in ['beer', 'ale', 'lager', 'stout']:
            return 'Beverage'
        else:
            return 'Other'
    
    def _get_replacement_notes(self, original: str, replacement: str) -> str:
        """Get specific notes for ingredient replacement"""
        notes = {
            'wheat flour': 'May need additional binding agents like xanthan gum',
            'all-purpose flour': 'Use 1:1 ratio, may need xanthan gum for structure',
            'bread flour': 'Add extra binding agents for better rise',
            'soy sauce': 'Ensure tamari is certified gluten-free',
            'beer': 'Use gluten-free beer or substitute with wine/broth',
            'couscous': 'Cook quinoa or rice according to package directions'
        }
        
        return notes.get(original, 'Follow package directions for best results')
    
    def _generate_conversion_notes(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate general conversion notes"""
        notes = [
            "Gluten-free flours often need additional binding agents for structure.",
            "Consider adding xanthan gum (1/4 tsp per cup of flour) for better texture.",
            "Gluten-free baked goods may be denser - don't overmix.",
            "Allow extra time for gluten-free breads to rise.",
            "Test small batches first to adjust flavors and textures."
        ]
        
        # Add specific notes based on ingredients found
        categories = set(item['category'] for item in analysis['gluten_ingredients'])
        
        if 'Flour' in categories:
            notes.append("For baking, consider using a commercial gluten-free flour blend.")
        
        if 'Sauce/Condiment' in categories:
            notes.append("Always check labels for hidden gluten in sauces and condiments.")
        
        if 'Beverage' in categories:
            notes.append("Gluten-free beer alternatives may have different flavor profiles.")
        
        return notes
    
    def _assess_difficulty(self, analysis: Dict[str, Any]) -> str:
        """Assess conversion difficulty"""
        gluten_count = len(analysis['gluten_ingredients'])
        categories = set(item['category'] for item in analysis['gluten_ingredients'])
        
        if gluten_count <= 2 and 'Flour' not in categories:
            return 'Easy'
        elif gluten_count <= 4 and 'Flour' in categories:
            return 'Medium'
        else:
            return 'Advanced'
    
    def _estimate_cost_change(self, analysis: Dict[str, Any]) -> str:
        """Estimate cost change for conversion"""
        gluten_count = len(analysis['gluten_ingredients'])
        
        if gluten_count <= 2:
            return 'Minimal (+$1-3)'
        elif gluten_count <= 4:
            return 'Moderate (+$3-8)'
        else:
            return 'Significant (+$8-15)'
    
    def convert_recipe(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert recipe to gluten-free version"""
        analysis = self.analyze_recipe(recipe_data)
        
        if not analysis['has_gluten']:
            return recipe_data  # Already gluten-free
        
        # Create converted recipe
        converted_recipe = recipe_data.copy()
        converted_ingredients = []
        
        for ingredient in recipe_data.get('ingredients', []):
            if isinstance(ingredient, dict):
                ingredient_name = ingredient.get('name', '').lower()
                amount = ingredient.get('amount', '')
            else:
                ingredient_name = str(ingredient).lower()
                amount = ''
            
            replacement = self._find_gluten_ingredient(ingredient_name)
            if replacement:
                converted_ingredients.append({
                    'name': replacement,
                    'amount': amount,
                    'original': ingredient_name,
                    'converted': True
                })
            else:
                converted_ingredients.append(ingredient)
        
        converted_recipe['ingredients'] = converted_ingredients
        converted_recipe['name'] = f"Gluten-Free {recipe_data.get('name', 'Recipe')}"
        converted_recipe['notes'] = f"Converted to gluten-free. Original recipe: {recipe_data.get('name', 'Recipe')}\n\n" + \
                                   "\n".join(analysis['conversion_notes'])
        
        return converted_recipe


# Global instance
gluten_free_converter = GlutenFreeConverter()
