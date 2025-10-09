# path: services/recipe_enhancement.py
"""
Recipe Enhancement Services for Celiogix

Implements advanced recipe features like ranking, scaling, substitution, and conversion.
"""

import re
import math
from typing import Dict, List, Any, Optional, Tuple
from fractions import Fraction


class RecipeRanker:
    """Ranks recipes based on gluten-free safety and user preferences"""
    
    def __init__(self):
        self.trusted_sources = [
            'glutenfreegoddess.com',
            'kingarthurbaking.com', 
            'simplygluten-free.com',
            'celiac.org',
            'beyondceliac.org',
            'gluten.org'
        ]
        
        self.gluten_warnings = [
            'wheat', 'flour (not specified as gf)', 'soy sauce (not specified as gf)',
            'beer', 'barley', 'malt', 'rye', 'bulgur', 'couscous', 'seitan'
        ]
    
    def rank_recipes(self, recipes: List[Dict], preferences: Dict[str, Any]) -> List[Dict]:
        """Rank recipes based on relevance and safety"""
        scored_recipes = []
        
        for recipe in recipes:
            score = 0
            
            # Gluten-free verification (highest priority)
            if recipe.get('is_verified_gluten_free'):
                score += 50
            elif recipe.get('is_gluten_free'):
                score += 30
                
            if self._has_gluten_warnings(recipe):
                score -= 30
            
            # User preferences
            if preferences.get('max_time') and recipe.get('total_time', 0) <= preferences['max_time']:
                score += 20
                
            if preferences.get('favorite_cuisines') and recipe.get('cuisine') in preferences['favorite_cuisines']:
                score += 15
                
            # Recipe completeness
            if recipe.get('ingredients') and len(recipe['ingredients']) > 0:
                score += 10
            if recipe.get('instructions') and len(recipe['instructions']) > 0:
                score += 10
            if recipe.get('image'):
                score += 5
            if recipe.get('nutrition'):
                score += 5
                
            # Source reliability
            source_url = recipe.get('source_url', '')
            if any(trusted_source in source_url for trusted_source in self.trusted_sources):
                score += 25
                
            # Time-based relevance
            total_time = recipe.get('total_time', 0)
            if total_time <= 20:
                score += 10  # Quick meals bonus
            elif total_time <= 30:
                score += 5
                
            # Nutrition quality
            nutrition = recipe.get('nutrition', {})
            if nutrition.get('fiber_g', 0) > 5:
                score += 5  # High fiber
            if nutrition.get('protein_g', 0) > 15:
                score += 5  # Good protein
                
            recipe['relevance_score'] = score
            scored_recipes.append(recipe)
            
        return sorted(scored_recipes, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    def _has_gluten_warnings(self, recipe: Dict) -> bool:
        """Check if recipe contains gluten warnings"""
        ingredients_text = ' '.join([
            ing.get('name', '') + ' ' + ing.get('notes', '')
            for ing in recipe.get('ingredients', [])
        ]).lower()
        
        return any(warning in ingredients_text for warning in self.gluten_warnings)


class RecipeScaler:
    """Scales recipes to different serving sizes"""
    
    def __init__(self):
        self.fraction_map = {
            0.125: '⅛',
            0.25: '¼', 
            0.333: '⅓',
            0.5: '½',
            0.667: '⅔',
            0.75: '¾'
        }
    
    def scale_recipe(self, recipe: Dict, target_servings: int) -> Dict:
        """Scale recipe to target number of servings"""
        original_servings = recipe.get('servings', 1)
        if original_servings <= 0:
            original_servings = 1
            
        scale_factor = target_servings / original_servings
        
        scaled_recipe = recipe.copy()
        scaled_recipe['servings'] = target_servings
        scaled_recipe['original_servings'] = original_servings
        scaled_recipe['scale_factor'] = scale_factor
        
        # Scale ingredients
        scaled_recipe['ingredients'] = [
            self._scale_ingredient(ing, scale_factor)
            for ing in recipe.get('ingredients', [])
        ]
        
        # Scale nutrition
        if recipe.get('nutrition'):
            scaled_recipe['nutrition'] = self._scale_nutrition(recipe['nutrition'], scale_factor)
            
        return scaled_recipe
    
    def _scale_ingredient(self, ingredient: Dict, scale_factor: float) -> Dict:
        """Scale a single ingredient"""
        scaled_ing = ingredient.copy()
        
        # Try multiple quantity field names (quantity, amount, etc.)
        qty_field = None
        qty_value = None
        
        for field in ['quantity', 'amount', 'qty']:
            if field in ingredient and ingredient[field]:
                try:
                    qty_value = float(ingredient[field])
                    qty_field = field
                    break
                except (ValueError, TypeError):
                    continue
        
        if qty_value is not None and qty_field:
            try:
                scaled_qty = qty_value * scale_factor
                scaled_ing[qty_field] = scaled_qty
                scaled_ing['display_quantity'] = self._format_scaled_quantity(scaled_qty, ingredient.get('unit', ''))
                # Also update the amount field for compatibility
                if qty_field != 'amount':
                    scaled_ing['amount'] = scaled_qty
            except (ValueError, TypeError):
                scaled_ing['display_quantity'] = ingredient.get(qty_field, '')
        else:
            # No valid quantity found, keep original
            scaled_ing['display_quantity'] = ingredient.get('quantity', ingredient.get('amount', ''))
                
        return scaled_ing
    
    def _format_scaled_quantity(self, quantity: float, unit: str) -> str:
        """Format scaled quantity with fractions"""
        whole = math.floor(quantity)
        decimal = quantity - whole
        
        # Find closest fraction
        fraction_str = ''
        min_diff = 1
        for value, symbol in self.fraction_map.items():
            diff = abs(decimal - value)
            if diff < min_diff and diff < 0.05:
                min_diff = diff
                fraction_str = symbol
        
        # Format the quantity part
        if whole > 0 and fraction_str:
            qty_str = f"{whole} {fraction_str}"
        elif whole > 0:
            qty_str = str(whole)
        elif fraction_str:
            qty_str = fraction_str
        else:
            # Format decimal nicely
            if quantity == int(quantity):
                qty_str = str(int(quantity))
            else:
                qty_str = f"{quantity:.2f}".rstrip('0').rstrip('.')
        
        # Add unit if present
        if unit and unit.strip():
            return f"{qty_str} {unit.strip()}"
        else:
            return qty_str
    
    def _scale_nutrition(self, nutrition: Dict, scale_factor: float) -> Dict:
        """Scale nutrition values"""
        scaled_nutrition = {}
        for key, value in nutrition.items():
            if isinstance(value, (int, float)):
                scaled_nutrition[key] = round(value * scale_factor, 1)
            else:
                scaled_nutrition[key] = value
        return scaled_nutrition


class IngredientSubstitution:
    """Provides gluten-free ingredient substitutions"""
    
    def __init__(self):
        self.substitutions = {
            # Gluten-containing → GF alternatives
            'all-purpose flour': [
                {'ingredient': 'gluten-free all-purpose flour blend', 'ratio': 1.0, 'notes': 'Cup-for-cup replacement'},
                {'ingredient': 'almond flour', 'ratio': 1.0, 'notes': 'Best for cookies and quick breads'},
                {'ingredient': 'rice flour + xanthan gum', 'ratio': 1.0, 'notes': 'Add 1/4 tsp xanthan gum per cup'}
            ],
            'soy sauce': [
                {'ingredient': 'tamari (gluten-free)', 'ratio': 1.0, 'notes': 'Ensure labeled gluten-free'},
                {'ingredient': 'coconut aminos', 'ratio': 1.0, 'notes': 'Slightly sweeter, soy-free option'}
            ],
            'bread crumbs': [
                {'ingredient': 'gluten-free bread crumbs', 'ratio': 1.0, 'notes': 'Store-bought or homemade'},
                {'ingredient': 'crushed gluten-free cornflakes', 'ratio': 1.0, 'notes': 'Extra crispy coating'},
                {'ingredient': 'almond meal', 'ratio': 0.75, 'notes': 'Nutty flavor, lower carb'}
            ],
            'pasta': [
                {'ingredient': 'gluten-free pasta', 'ratio': 1.0, 'notes': 'Rice, corn, or chickpea-based'},
                {'ingredient': 'zucchini noodles', 'ratio': 1.5, 'notes': 'Low-carb, cook briefly'},
                {'ingredient': 'rice noodles', 'ratio': 1.0, 'notes': 'Naturally gluten-free'}
            ],
            'beer': [
                {'ingredient': 'gluten-free beer', 'ratio': 1.0, 'notes': 'Made from sorghum or rice'},
                {'ingredient': 'chicken broth', 'ratio': 1.0, 'notes': 'For cooking, non-alcoholic'},
                {'ingredient': 'hard cider', 'ratio': 1.0, 'notes': 'Naturally gluten-free'}
            ],
            'oats': [
                {'ingredient': 'certified gluten-free oats', 'ratio': 1.0, 'notes': 'Essential to use certified'},
                {'ingredient': 'quinoa flakes', 'ratio': 1.0, 'notes': 'Higher protein alternative'}
            ],
            
            # Common dietary substitutions
            'butter': [
                {'ingredient': 'coconut oil', 'ratio': 1.0, 'notes': 'Dairy-free, use refined for neutral flavor'},
                {'ingredient': 'vegan butter', 'ratio': 1.0, 'notes': 'Dairy-free, similar texture'},
                {'ingredient': 'olive oil', 'ratio': 0.75, 'notes': 'For savory dishes'}
            ],
            'milk': [
                {'ingredient': 'almond milk', 'ratio': 1.0, 'notes': 'Low calorie, neutral flavor'},
                {'ingredient': 'oat milk', 'ratio': 1.0, 'notes': 'Creamy texture, ensure GF certified'},
                {'ingredient': 'coconut milk', 'ratio': 1.0, 'notes': 'Rich and creamy'}
            ],
            'eggs': [
                {'ingredient': 'flax egg (1 tbsp ground flax + 3 tbsp water)', 'ratio': 1.0, 'notes': 'Let sit 5 minutes to thicken'},
                {'ingredient': 'chia egg (1 tbsp chia + 3 tbsp water)', 'ratio': 1.0, 'notes': 'Similar to flax egg'},
                {'ingredient': 'applesauce', 'ratio': 0.25, 'notes': '1/4 cup per egg, for baking'}
            ]
        }
    
    def find_substitutes(self, ingredient_name: str) -> List[Dict]:
        """Find substitutes for an ingredient"""
        normalized = ingredient_name.lower().strip()
        
        # Exact match
        if normalized in self.substitutions:
            return self.substitutions[normalized]
        
        # Partial match
        for key, subs in self.substitutions.items():
            if key in normalized or normalized in key:
                return subs
                
        return []
    
    def suggest_gluten_free_alternatives(self, recipe: Dict) -> List[Dict]:
        """Suggest GF alternatives for non-GF ingredients in recipe"""
        suggestions = []
        
        for ingredient in recipe.get('ingredients', []):
            if not ingredient.get('is_gluten_free', True):
                subs = self.find_substitutes(ingredient.get('name', ''))
                if subs:
                    suggestions.append({
                        'original': ingredient,
                        'alternatives': subs
                    })
                    
        return suggestions
    
    def apply_substitution(self, recipe: Dict, ingredient_id: str, substitution: Dict) -> Dict:
        """Apply a substitution to a recipe"""
        updated_recipe = recipe.copy()
        
        # Find and update the ingredient
        for i, ing in enumerate(updated_recipe.get('ingredients', [])):
            if ing.get('id') == ingredient_id:
                updated_recipe['ingredients'][i] = {
                    **ing,
                    'name': substitution['ingredient'],
                    'quantity': ing.get('quantity', 1) * substitution['ratio'],
                    'is_gluten_free': True,
                    'gluten_warning': None,
                    'notes': f"{ing.get('notes', '')} - {substitution['notes']}".strip()
                }
                break
                
        # Update recipe metadata
        updated_recipe['title'] = f"{recipe['title']} (Modified)"
        updated_recipe['notes'] = f"{recipe.get('notes', '')}\n\nSubstitutions made:\n- {substitution['ingredient']} for original ingredient"
        
        return updated_recipe


class RecipeConverter:
    """Converts traditional recipes to gluten-free"""
    
    def __init__(self):
        self.substitution_engine = IngredientSubstitution()
    
    def convert_to_gluten_free(self, recipe: Dict) -> Dict:
        """Convert recipe to gluten-free with suggestions"""
        suggestions = self.substitution_engine.suggest_gluten_free_alternatives(recipe)
        
        if not suggestions:
            return {
                'is_already_gluten_free': True,
                'recipe': recipe,
                'message': 'This recipe is already gluten-free!'
            }
        
        return {
            'is_already_gluten_free': False,
            'original_recipe': recipe,
            'suggestions': suggestions,
            'auto_convert': lambda: self._auto_convert(recipe, suggestions),
            'manual_convert': lambda: self._show_conversion_wizard(recipe, suggestions)
        }
    
    def _auto_convert(self, recipe: Dict, suggestions: List[Dict]) -> Dict:
        """Automatically convert recipe using best substitutions"""
        converted = recipe.copy()
        
        # Apply first (best) substitution for each ingredient
        for suggestion in suggestions:
            best_sub = suggestion['alternatives'][0]  # First is usually best
            converted = self.substitution_engine.apply_substitution(
                converted, 
                suggestion['original'].get('id', ''), 
                best_sub
            )
        
        # Add conversion notes
        converted['title'] = f"Gluten-Free {converted['title']}"
        converted['description'] = f"{converted.get('description', '')}\n\n✅ Converted to gluten-free"
        converted['tags'] = converted.get('tags', []) + ['gluten-free', 'converted']
        
        return converted
    
    def _show_conversion_wizard(self, recipe: Dict, suggestions: List[Dict]) -> Dict:
        """Show conversion wizard steps"""
        return {
            'steps': [
                {
                    'step_number': i + 1,
                    'original': sug['original'].get('name', ''),
                    'alternatives': sug['alternatives'],
                    'selected': None  # User selects
                }
                for i, sug in enumerate(suggestions)
            ]
        }


class RecipeExporter:
    """Exports recipes in various formats"""
    
    def export_recipe(self, recipe: Dict, format_type: str) -> str:
        """Export recipe in specified format"""
        if format_type == 'markdown':
            return self._export_as_markdown(recipe)
        elif format_type == 'plain_text':
            return self._export_as_plain_text(recipe)
        elif format_type == 'json':
            return self._export_as_json(recipe)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _export_as_markdown(self, recipe: Dict) -> str:
        """Export recipe as Markdown"""
        md = f"# {recipe.get('title', 'Untitled Recipe')}\n\n"
        
        if recipe.get('description'):
            md += f"{recipe['description']}\n\n"
        
        # Recipe info
        md += "## Info\n\n"
        md += f"- **Prep Time:** {recipe.get('prep_time', 'N/A')} minutes\n"
        md += f"- **Cook Time:** {recipe.get('cook_time', 'N/A')} minutes\n"
        md += f"- **Total Time:** {recipe.get('total_time', 'N/A')} minutes\n"
        md += f"- **Servings:** {recipe.get('servings', 'N/A')}\n"
        md += f"- **Difficulty:** {recipe.get('difficulty', 'N/A')}\n\n"
        
        if recipe.get('tags'):
            md += f"**Tags:** {', '.join(recipe['tags'])}\n\n"
        
        # Ingredients
        md += "## Ingredients\n\n"
        for ing in recipe.get('ingredients', []):
            qty = ing.get('quantity', '')
            unit = ing.get('unit', '')
            name = ing.get('name', '')
            prep = ing.get('notes', '')
            
            qty_str = f"{qty} {unit} " if qty and unit else f"{qty} " if qty else ""
            prep_str = f", {prep}" if prep else ""
            
            md += f"- {qty_str}{name}{prep_str}\n"
            
            if ing.get('gluten_warning'):
                md += f"  - ⚠️ {ing['gluten_warning']}\n"
        
        # Instructions
        md += "\n## Instructions\n\n"
        instructions = recipe.get('instructions', '')
        if instructions:
            if isinstance(instructions, str):
                # Split by common delimiters to create steps
                if '\n' in instructions:
                    # Split by newlines
                    instruction_list = [step.strip() for step in instructions.split('\n') if step.strip()]
                elif '. ' in instructions:
                    # Split by periods followed by space
                    instruction_list = [step.strip() + '.' for step in instructions.split('. ') if step.strip()]
                else:
                    # Single instruction
                    instruction_list = [instructions]
                
                for i, instruction in enumerate(instruction_list, 1):
                    md += f"{i}. {instruction}\n\n"
            elif isinstance(instructions, list):
                # Already a list
                for i, instruction in enumerate(instructions, 1):
                    md += f"{i}. {instruction}\n\n"
            else:
                # Fallback
                md += f"1. {instructions}\n\n"
        
        # Nutrition
        if recipe.get('nutrition'):
            md += "## Nutrition (per serving)\n\n"
            nutrition = recipe['nutrition']
            md += f"- Calories: {nutrition.get('calories', 'N/A')}\n"
            md += f"- Protein: {nutrition.get('protein_g', 'N/A')}g\n"
            md += f"- Carbs: {nutrition.get('carbs_g', 'N/A')}g\n"
            md += f"- Fiber: {nutrition.get('fiber_g', 'N/A')}g\n"
            md += f"- Fat: {nutrition.get('fat_g', 'N/A')}g\n\n"
        
        # Notes
        if recipe.get('notes'):
            md += f"## Notes\n\n{recipe['notes']}\n\n"
        
        # Source
        if recipe.get('source_url'):
            md += f"---\n*Source: {recipe['source_url']}*\n"
        
        return md
    
    def _export_as_plain_text(self, recipe: Dict) -> str:
        """Export recipe as plain text"""
        text = f"{recipe.get('title', 'Untitled Recipe')}\n"
        text += "=" * len(recipe.get('title', 'Untitled Recipe')) + "\n\n"
        
        if recipe.get('description'):
            text += f"{recipe['description']}\n\n"
        
        # Recipe info
        text += f"Prep Time: {recipe.get('prep_time', 'N/A')} minutes\n"
        text += f"Cook Time: {recipe.get('cook_time', 'N/A')} minutes\n"
        text += f"Total Time: {recipe.get('total_time', 'N/A')} minutes\n"
        text += f"Servings: {recipe.get('servings', 'N/A')}\n"
        text += f"Difficulty: {recipe.get('difficulty', 'N/A')}\n\n"
        
        # Ingredients
        text += "INGREDIENTS:\n"
        text += "-" * 20 + "\n"
        for ing in recipe.get('ingredients', []):
            qty = ing.get('quantity', '')
            unit = ing.get('unit', '')
            name = ing.get('name', '')
            
            qty_str = f"{qty} {unit} " if qty and unit else f"{qty} " if qty else ""
            text += f"• {qty_str}{name}\n"
        
        # Instructions
        text += "\nINSTRUCTIONS:\n"
        text += "-" * 20 + "\n"
        instructions = recipe.get('instructions', '')
        if instructions:
            if isinstance(instructions, str):
                # Split by common delimiters to create steps
                if '\n' in instructions:
                    # Split by newlines
                    instruction_list = [step.strip() for step in instructions.split('\n') if step.strip()]
                elif '. ' in instructions:
                    # Split by periods followed by space
                    instruction_list = [step.strip() + '.' for step in instructions.split('. ') if step.strip()]
                else:
                    # Single instruction
                    instruction_list = [instructions]
                
                for i, instruction in enumerate(instruction_list, 1):
                    text += f"{i}. {instruction}\n\n"
            elif isinstance(instructions, list):
                # Already a list
                for i, instruction in enumerate(instructions, 1):
                    text += f"{i}. {instruction}\n\n"
            else:
                # Fallback
                text += f"1. {instructions}\n\n"
        
        # Notes
        if recipe.get('notes'):
            text += f"NOTES:\n{recipe['notes']}\n"
        
        return text
    
    def _export_as_json(self, recipe: Dict) -> str:
        """Export recipe as JSON"""
        import json
        return json.dumps(recipe, indent=2, ensure_ascii=False)


# Global instances
recipe_ranker = RecipeRanker()
recipe_scaler = RecipeScaler()
ingredient_substitution = IngredientSubstitution()
recipe_converter = RecipeConverter()
recipe_exporter = RecipeExporter()
