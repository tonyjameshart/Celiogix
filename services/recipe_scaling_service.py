#!/usr/bin/env python3
"""
Recipe Scaling Service

Provides comprehensive recipe scaling functionality with conversion charts
for volume, liquid, and weight measurements.
"""

import re
from typing import Dict, List, Tuple, Optional, Union
from fractions import Fraction


class RecipeScalingService:
    """Service for scaling recipes and converting between measurement units"""
    
    def __init__(self):
        """Initialize the scaling service with conversion charts"""
        self.setup_conversion_charts()
        self.setup_unit_aliases()
    
    def setup_conversion_charts(self):
        """Setup comprehensive conversion charts"""
        
        # Volume conversions (US measurements)
        self.volume_conversions = {
            # Cups to smaller units
            'cup': {
                'tablespoon': 16,
                'teaspoon': 48,
                'ml': 250,
                'fl oz': 8,
            },
            'cups': {
                'tablespoon': 16,
                'teaspoon': 48,
                'ml': 250,
                'fl oz': 8,
            },
            # Tablespoons
            'tablespoon': {
                'teaspoon': 3,
                'ml': 15,
                'fl oz': 0.5,
            },
            'tablespoons': {
                'teaspoon': 3,
                'ml': 15,
                'fl oz': 0.5,
            },
            'tbsp': {
                'teaspoon': 3,
                'ml': 15,
                'fl oz': 0.5,
            },
            'tbs': {
                'teaspoon': 3,
                'ml': 15,
                'fl oz': 0.5,
            },
            # Teaspoons
            'teaspoon': {
                'ml': 5,
                'fl oz': 1/6,
            },
            'teaspoons': {
                'ml': 5,
                'fl oz': 1/6,
            },
            'tsp': {
                'ml': 5,
                'fl oz': 1/6,
            },
            'ts': {
                'ml': 5,
                'fl oz': 1/6,
            },
            # Fluid ounces
            'fl oz': {
                'ml': 30,
                'tablespoon': 2,
                'teaspoon': 6,
            },
            'fluid ounce': {
                'ml': 30,
                'tablespoon': 2,
                'teaspoon': 6,
            },
            'fluid ounces': {
                'ml': 30,
                'tablespoon': 2,
                'teaspoon': 6,
            },
            # Milliliters
            'ml': {
                'fl oz': 1/30,
                'teaspoon': 0.2,
                'tablespoon': 1/15,
                'cup': 1/250,
            },
            'milliliter': {
                'fl oz': 1/30,
                'teaspoon': 0.2,
                'tablespoon': 1/15,
                'cup': 1/250,
            },
            'milliliters': {
                'fl oz': 1/30,
                'teaspoon': 0.2,
                'tablespoon': 1/15,
                'cup': 1/250,
            },
        }
        
        # Weight conversions
        self.weight_conversions = {
            'pound': {
                'ounce': 16,
                'gram': 453.6,
                'kg': 0.4536,
            },
            'pounds': {
                'ounce': 16,
                'gram': 453.6,
                'kg': 0.4536,
            },
            'lb': {
                'ounce': 16,
                'gram': 453.6,
                'kg': 0.4536,
            },
            'lbs': {
                'ounce': 16,
                'gram': 453.6,
                'kg': 0.4536,
            },
            'ounce': {
                'gram': 28.35,
                'kg': 0.02835,
                'pound': 1/16,
            },
            'ounces': {
                'gram': 28.35,
                'kg': 0.02835,
                'pound': 1/16,
            },
            'oz': {
                'gram': 28.35,
                'kg': 0.02835,
                'pound': 1/16,
            },
            'gram': {
                'ounce': 1/28.35,
                'kg': 0.001,
                'pound': 1/453.6,
            },
            'grams': {
                'ounce': 1/28.35,
                'kg': 0.001,
                'pound': 1/453.6,
            },
            'g': {
                'ounce': 1/28.35,
                'kg': 0.001,
                'pound': 1/453.6,
            },
            'kilogram': {
                'gram': 1000,
                'ounce': 35.274,
                'pound': 2.205,
            },
            'kilograms': {
                'gram': 1000,
                'ounce': 35.274,
                'pound': 2.205,
            },
            'kg': {
                'gram': 1000,
                'ounce': 35.274,
                'pound': 2.205,
            },
        }
        
        # Count-based units (no conversion needed)
        self.count_units = {
            'piece', 'pieces', 'pc', 'pc.',
            'slice', 'slices',
            'clove', 'cloves',
            'head', 'heads',
            'bunch', 'bunches',
            'can', 'cans',
            'package', 'packages', 'pkg', 'pkg.',
            'bag', 'bags',
            'bottle', 'bottles',
            'jar', 'jars',
            'box', 'boxes',
            'egg', 'eggs',
            'item', 'items',
        }
        
        # Special conversions for common fractions
        self.fraction_conversions = {
            '1/8': 0.125,
            '1/6': 0.167,
            '1/4': 0.25,
            '1/3': 0.333,
            '1/2': 0.5,
            '2/3': 0.667,
            '3/4': 0.75,
            '1': 1.0,
        }
    
    def setup_unit_aliases(self):
        """Setup unit aliases for flexible matching"""
        self.unit_aliases = {
            # Volume
            'cup': ['cup', 'cups', 'c', 'c.'],
            'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsp.', 'tbs', 'tbs.', 'tbl', 'tbl.'],
            'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsp.', 'ts', 'ts.'],
            'fl oz': ['fl oz', 'fl. oz.', 'floz', 'fluid ounce', 'fluid ounces'],
            'ml': ['ml', 'ml.', 'milliliter', 'milliliters'],
            'liter': ['liter', 'liters', 'l', 'l.'],
            'pint': ['pint', 'pints', 'pt', 'pt.'],
            'quart': ['quart', 'quarts', 'qt', 'qt.'],
            'gallon': ['gallon', 'gallons', 'gal', 'gal.'],
            
            # Weight
            'pound': ['pound', 'pounds', 'lb', 'lb.', 'lbs', 'lbs.'],
            'ounce': ['ounce', 'ounces', 'oz', 'oz.'],
            'gram': ['gram', 'grams', 'g', 'g.'],
            'kilogram': ['kilogram', 'kilograms', 'kg', 'kg.'],
        }
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string and return as float"""
        if not amount_str or not amount_str.strip():
            return 0.0
        
        amount_str = amount_str.strip()
        
        # Handle mixed numbers (e.g., "2 1/2")
        mixed_match = re.match(r'^(\d+)\s+(\d+/\d+)$', amount_str)
        if mixed_match:
            whole = float(mixed_match.group(1))
            fraction = self.parse_fraction(mixed_match.group(2))
            return whole + fraction
        
        # Handle simple fractions (e.g., "1/2")
        if '/' in amount_str:
            return self.parse_fraction(amount_str)
        
        # Handle decimals (e.g., "2.5")
        try:
            return float(amount_str)
        except ValueError:
            return 0.0
    
    def parse_fraction(self, fraction_str: str) -> float:
        """Parse fraction string and return as float"""
        if '/' in fraction_str:
            try:
                return float(Fraction(fraction_str))
            except (ValueError, ZeroDivisionError):
                return 0.0
        return 0.0
    
    def normalize_unit(self, unit: str) -> str:
        """Normalize unit to standard form"""
        if not unit:
            return ''
        
        unit = unit.lower().strip()
        
        # Check aliases
        for standard_unit, aliases in self.unit_aliases.items():
            if unit in aliases:
                return standard_unit
        
        return unit
    
    def convert_amount(self, amount: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert amount from one unit to another"""
        from_unit = self.normalize_unit(from_unit)
        to_unit = self.normalize_unit(to_unit)
        
        if not from_unit or not to_unit or from_unit == to_unit:
            return amount
        
        # Check if both units are count-based (no conversion)
        if from_unit in self.count_units and to_unit in self.count_units:
            return amount
        
        # Try volume conversions first
        if from_unit in self.volume_conversions and to_unit in self.volume_conversions[from_unit]:
            return amount * self.volume_conversions[from_unit][to_unit]
        
        # Try weight conversions
        if from_unit in self.weight_conversions and to_unit in self.weight_conversions[from_unit]:
            return amount * self.weight_conversions[from_unit][to_unit]
        
        # Try reverse conversions
        if to_unit in self.volume_conversions and from_unit in self.volume_conversions[to_unit]:
            return amount / self.volume_conversions[to_unit][from_unit]
        
        if to_unit in self.weight_conversions and from_unit in self.weight_conversions[to_unit]:
            return amount / self.weight_conversions[to_unit][from_unit]
        
        return None
    
    def scale_ingredient(self, ingredient: Dict[str, str], scale_factor: float, 
                        target_unit: Optional[str] = None) -> Dict[str, str]:
        """Scale a single ingredient"""
        if not ingredient or not isinstance(ingredient, dict):
            return ingredient
        
        name = ingredient.get('name', '')
        amount_str = ingredient.get('amount', '')
        unit = ingredient.get('unit', '')
        
        # Parse original amount
        original_amount = self.parse_amount(amount_str)
        
        # Calculate scaled amount
        scaled_amount = original_amount * scale_factor
        
        # Convert to target unit if specified
        if target_unit and unit:
            converted_amount = self.convert_amount(scaled_amount, unit, target_unit)
            if converted_amount is not None:
                scaled_amount = converted_amount
                unit = target_unit
        
        # Format the scaled amount
        scaled_amount_str = self.format_amount(scaled_amount)
        
        return {
            'name': name,
            'amount': scaled_amount_str,
            'unit': unit
        }
    
    def scale_recipe(self, ingredients: List[Dict[str, str]], scale_factor: float,
                    target_units: Optional[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """Scale a list of ingredients"""
        if not ingredients or not isinstance(ingredients, list):
            return ingredients
        
        scaled_ingredients = []
        for ingredient in ingredients:
            # Get target unit for this ingredient if specified
            ingredient_name = ingredient.get('name', '').lower()
            target_unit = None
            if target_units:
                for name_pattern, unit in target_units.items():
                    if name_pattern.lower() in ingredient_name:
                        target_unit = unit
                        break
            
            scaled_ingredient = self.scale_ingredient(ingredient, scale_factor, target_unit)
            scaled_ingredients.append(scaled_ingredient)
        
        return scaled_ingredients
    
    def format_amount(self, amount: float) -> str:
        """Format amount as a readable string"""
        if amount == 0:
            return '0'
        
        # Handle very small amounts
        if amount < 0.125:  # Less than 1/8
            if amount < 0.0625:  # Less than 1/16
                return "pinch"
            return "1/8"
        
        # Convert to fraction if it's close to a common fraction
        for fraction_str, decimal in self.fraction_conversions.items():
            if abs(amount - decimal) < 0.01:
                return fraction_str
        
        # Handle mixed numbers (e.g., 2.5 -> "2 1/2")
        if amount > 1 and amount % 1 != 0:
            whole = int(amount)
            decimal_part = amount - whole
            
            # Check if decimal part is close to a common fraction
            for fraction_str, decimal in self.fraction_conversions.items():
                if abs(decimal_part - decimal) < 0.01:
                    return f"{whole} {fraction_str}"
        
        # Format as decimal with appropriate precision
        if amount % 1 == 0:
            return str(int(amount))
        elif amount < 1:
            return f"{amount:.3f}".rstrip('0').rstrip('.')
        else:
            return f"{amount:.2f}".rstrip('0').rstrip('.')
    
    def get_conversion_suggestions(self, amount: float, unit: str) -> List[Tuple[str, str]]:
        """Get conversion suggestions for an amount and unit"""
        unit = self.normalize_unit(unit)
        suggestions = []
        
        if unit in self.volume_conversions:
            for target_unit, factor in self.volume_conversions[unit].items():
                converted_amount = amount * factor
                formatted_amount = self.format_amount(converted_amount)
                suggestions.append((formatted_amount, target_unit))
        
        elif unit in self.weight_conversions:
            for target_unit, factor in self.weight_conversions[unit].items():
                converted_amount = amount * factor
                formatted_amount = self.format_amount(converted_amount)
                suggestions.append((formatted_amount, target_unit))
        
        return suggestions
    
    def get_common_scales(self) -> List[Tuple[float, str]]:
        """Get common recipe scale factors"""
        return [
            (0.25, "1/4 (Quarter recipe)"),
            (0.5, "1/2 (Half recipe)"),
            (0.75, "3/4 recipe"),
            (1.0, "1x (Original)"),
            (1.25, "1 1/4 recipe"),
            (1.5, "1 1/2 recipe"),
            (2.0, "2x (Double)"),
            (2.5, "2 1/2 recipe"),
            (3.0, "3x (Triple)"),
            (4.0, "4x (Quadruple)"),
        ]


# Global instance
recipe_scaling_service = RecipeScalingService()
