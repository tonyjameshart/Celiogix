# path: services/ingredient_correlator.py
"""
Ingredient Correlation Service for CeliacShield

Analyzes correlations between ingredients and health symptoms for better tracking.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from collections import defaultdict, Counter


@dataclass
class IngredientCorrelation:
    """Correlation between ingredient and symptoms"""
    ingredient: str
    symptom: str
    correlation_strength: float  # 0-1 scale
    occurrences: int
    confidence_level: str  # 'low', 'medium', 'high'
    risk_assessment: str  # 'safe', 'caution', 'avoid'
    notes: str = ""


@dataclass
class SymptomPattern:
    """Pattern analysis for symptoms"""
    pattern_id: str
    ingredients_involved: List[str]
    symptoms: List[str]
    frequency: int
    severity_avg: float
    time_pattern: str  # 'immediate', 'delayed', 'variable'
    confidence: float


class IngredientCorrelator:
    """Analyzes ingredient-symptom correlations for better health tracking"""
    
    def __init__(self):
        self.correlation_threshold = 0.3  # Minimum correlation to report
        self.min_occurrences = 3  # Minimum occurrences for reliable correlation
        
        # Known problematic ingredients for celiacs
        self.known_triggers = {
            'wheat': {'risk': 'high', 'symptoms': ['bloating', 'diarrhea', 'fatigue', 'headache']},
            'barley': {'risk': 'high', 'symptoms': ['stomach pain', 'nausea', 'fatigue']},
            'rye': {'risk': 'high', 'symptoms': ['digestive issues', 'fatigue', 'brain fog']},
            'oats': {'risk': 'medium', 'symptoms': ['mild bloating', 'digestive discomfort']},
            'soy sauce': {'risk': 'high', 'symptoms': ['immediate reaction', 'stomach pain']},
            'beer': {'risk': 'high', 'symptoms': ['bloating', 'diarrhea', 'headache']},
            'malt': {'risk': 'high', 'symptoms': ['severe reaction', 'multiple symptoms']},
            'cross-contamination': {'risk': 'medium', 'symptoms': ['mild to moderate symptoms']}
        }
    
    def analyze_ingredient_correlations(self, health_logs: List[Dict], 
                                      meal_logs: List[Dict]) -> Dict[str, Any]:
        """Analyze correlations between ingredients and symptoms"""
        
        # Combine health and meal data
        combined_data = self._combine_health_meal_data(health_logs, meal_logs)
        
        # Calculate correlations
        correlations = self._calculate_correlations(combined_data)
        
        # Identify patterns
        patterns = self._identify_patterns(combined_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(correlations, patterns)
        
        return {
            'correlations': correlations,
            'patterns': patterns,
            'recommendations': recommendations,
            'summary': self._generate_summary(correlations, patterns),
            'risk_ingredients': self._identify_risk_ingredients(correlations),
            'safe_ingredients': self._identify_safe_ingredients(combined_data, correlations)
        }
    
    def _combine_health_meal_data(self, health_logs: List[Dict], 
                                 meal_logs: List[Dict]) -> List[Dict]:
        """Combine health and meal logs for correlation analysis"""
        combined_data = []
        
        for health_log in health_logs:
            health_time = datetime.fromisoformat(health_log.get('timestamp', ''))
            symptoms = health_log.get('symptoms', [])
            severity = health_log.get('severity', 0)
            
            # Find meals within 24 hours before symptoms
            related_meals = []
            for meal_log in meal_logs:
                meal_time = datetime.fromisoformat(meal_log.get('timestamp', ''))
                time_diff = health_time - meal_time
                
                # Consider meals from 30 minutes to 24 hours before symptoms
                if timedelta(minutes=30) <= time_diff <= timedelta(hours=24):
                    related_meals.append({
                        'items': meal_log.get('items', []),
                        'time_before_symptoms': time_diff.total_seconds() / 3600,  # hours
                        'meal_type': meal_log.get('meal_type', ''),
                        'restaurant': meal_log.get('restaurant', ''),
                        'gluten_safety_confirmed': meal_log.get('gluten_safety_confirmed', False)
                    })
            
            if related_meals:  # Only include health logs with related meals
                combined_data.append({
                    'health_log': health_log,
                    'symptoms': symptoms,
                    'severity': severity,
                    'timestamp': health_time,
                    'related_meals': related_meals
                })
        
        return combined_data
    
    def _calculate_correlations(self, combined_data: List[Dict]) -> List[IngredientCorrelation]:
        """Calculate ingredient-symptom correlations"""
        correlations = []
        
        # Count ingredient-symptom co-occurrences
        ingredient_symptom_counts = defaultdict(lambda: defaultdict(int))
        ingredient_total_counts = defaultdict(int)
        symptom_total_counts = defaultdict(int)
        total_entries = len(combined_data)
        
        for entry in combined_data:
            symptoms = entry['symptoms']
            severity = entry['severity']
            
            # Extract ingredients from related meals
            ingredients = set()
            for meal in entry['related_meals']:
                for item in meal['items']:
                    # Simple ingredient extraction (in production, use NLP)
                    ingredients.update(self._extract_ingredients(item))
            
            # Count co-occurrences
            for ingredient in ingredients:
                ingredient_total_counts[ingredient] += 1
                for symptom in symptoms:
                    ingredient_symptom_counts[ingredient][symptom] += severity  # Weight by severity
                    symptom_total_counts[symptom] += 1
        
        # Calculate correlation coefficients
        for ingredient, symptom_counts in ingredient_symptom_counts.items():
            for symptom, weighted_count in symptom_counts.items():
                if ingredient_total_counts[ingredient] >= self.min_occurrences:
                    # Simple correlation calculation
                    correlation = weighted_count / (ingredient_total_counts[ingredient] * 10)  # Normalize
                    correlation = min(1.0, correlation)  # Cap at 1.0
                    
                    if correlation >= self.correlation_threshold:
                        confidence = self._calculate_confidence(
                            ingredient_total_counts[ingredient],
                            weighted_count,
                            total_entries
                        )
                        
                        risk_assessment = self._assess_risk(ingredient, correlation, confidence)
                        
                        correlations.append(IngredientCorrelation(
                            ingredient=ingredient,
                            symptom=symptom,
                            correlation_strength=correlation,
                            occurrences=ingredient_total_counts[ingredient],
                            confidence_level=confidence,
                            risk_assessment=risk_assessment,
                            notes=self._get_correlation_notes(ingredient, symptom, correlation)
                        ))
        
        # Sort by correlation strength
        correlations.sort(key=lambda x: x.correlation_strength, reverse=True)
        return correlations
    
    def _extract_ingredients(self, food_item: str) -> List[str]:
        """Extract ingredients from food item description"""
        # Simple keyword extraction (in production, use NLP/ML)
        food_item_lower = food_item.lower()
        
        ingredients = []
        
        # Check for known problematic ingredients
        for trigger in self.known_triggers.keys():
            if trigger in food_item_lower:
                ingredients.append(trigger)
        
        # Common ingredient keywords
        ingredient_keywords = [
            'flour', 'bread', 'pasta', 'noodles', 'pizza', 'cake', 'cookie',
            'sauce', 'dressing', 'marinade', 'seasoning', 'spice',
            'cheese', 'milk', 'butter', 'cream', 'yogurt',
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna',
            'rice', 'quinoa', 'potato', 'corn', 'beans', 'lentils',
            'tomato', 'onion', 'garlic', 'pepper', 'mushroom',
            'oil', 'vinegar', 'lemon', 'herbs'
        ]
        
        for keyword in ingredient_keywords:
            if keyword in food_item_lower:
                ingredients.append(keyword)
        
        return ingredients
    
    def _calculate_confidence(self, ingredient_count: int, co_occurrence: int, 
                            total_entries: int) -> str:
        """Calculate confidence level for correlation"""
        if ingredient_count >= 10 and co_occurrence >= 5:
            return 'high'
        elif ingredient_count >= 5 and co_occurrence >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _assess_risk(self, ingredient: str, correlation: float, confidence: str) -> str:
        """Assess risk level for ingredient"""
        # Check known triggers first
        if ingredient in self.known_triggers:
            known_risk = self.known_triggers[ingredient]['risk']
            if known_risk == 'high':
                return 'avoid'
            elif known_risk == 'medium':
                return 'caution'
        
        # Assess based on correlation and confidence
        if correlation >= 0.7 and confidence in ['high', 'medium']:
            return 'avoid'
        elif correlation >= 0.5 and confidence != 'low':
            return 'caution'
        else:
            return 'safe'
    
    def _get_correlation_notes(self, ingredient: str, symptom: str, correlation: float) -> str:
        """Generate notes for correlation"""
        if ingredient in self.known_triggers:
            return f"Known gluten-containing ingredient. {self.known_triggers[ingredient]['risk'].title()} risk."
        
        if correlation >= 0.8:
            return "Strong correlation detected. Consider avoiding this ingredient."
        elif correlation >= 0.6:
            return "Moderate correlation. Monitor carefully when consuming."
        else:
            return "Weak correlation. May be coincidental."
    
    def _identify_patterns(self, combined_data: List[Dict]) -> List[SymptomPattern]:
        """Identify symptom patterns"""
        patterns = []
        
        # Group by ingredient combinations
        combination_patterns = defaultdict(list)
        
        for entry in combined_data:
            # Get all ingredients from related meals
            all_ingredients = set()
            for meal in entry['related_meals']:
                for item in meal['items']:
                    all_ingredients.update(self._extract_ingredients(item))
            
            # Create combination key (sorted for consistency)
            if len(all_ingredients) >= 2:  # Only consider combinations
                combo_key = tuple(sorted(all_ingredients))
                combination_patterns[combo_key].append(entry)
        
        # Analyze patterns with sufficient data
        pattern_id = 1
        for combo, entries in combination_patterns.items():
            if len(entries) >= 3:  # Minimum occurrences for pattern
                symptoms = []
                severities = []
                time_patterns = []
                
                for entry in entries:
                    symptoms.extend(entry['symptoms'])
                    severities.append(entry['severity'])
                    
                    # Analyze timing
                    avg_time = sum(meal['time_before_symptoms'] 
                                 for meal in entry['related_meals']) / len(entry['related_meals'])
                    if avg_time <= 2:
                        time_patterns.append('immediate')
                    elif avg_time <= 8:
                        time_patterns.append('delayed')
                    else:
                        time_patterns.append('variable')
                
                # Determine dominant time pattern
                time_pattern_counts = Counter(time_patterns)
                dominant_time_pattern = time_pattern_counts.most_common(1)[0][0]
                
                # Calculate confidence based on consistency
                confidence = len(entries) / 10.0  # Simple confidence calculation
                confidence = min(1.0, confidence)
                
                patterns.append(SymptomPattern(
                    pattern_id=f"pattern_{pattern_id}",
                    ingredients_involved=list(combo),
                    symptoms=list(set(symptoms)),  # Unique symptoms
                    frequency=len(entries),
                    severity_avg=sum(severities) / len(severities),
                    time_pattern=dominant_time_pattern,
                    confidence=confidence
                ))
                pattern_id += 1
        
        return patterns
    
    def _generate_recommendations(self, correlations: List[IngredientCorrelation], 
                                patterns: List[SymptomPattern]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Ingredient-specific recommendations
        avoid_ingredients = [c for c in correlations if c.risk_assessment == 'avoid']
        caution_ingredients = [c for c in correlations if c.risk_assessment == 'caution']
        
        if avoid_ingredients:
            recommendations.append({
                'type': 'avoid_ingredients',
                'priority': 'high',
                'title': 'Ingredients to Avoid',
                'description': 'These ingredients show strong correlation with your symptoms',
                'ingredients': [c.ingredient for c in avoid_ingredients[:5]],  # Top 5
                'action': 'Eliminate these ingredients from your diet'
            })
        
        if caution_ingredients:
            recommendations.append({
                'type': 'caution_ingredients',
                'priority': 'medium',
                'title': 'Ingredients to Monitor',
                'description': 'These ingredients may trigger symptoms - consume with caution',
                'ingredients': [c.ingredient for c in caution_ingredients[:5]],
                'action': 'Monitor symptoms when consuming these ingredients'
            })
        
        # Pattern-based recommendations
        high_confidence_patterns = [p for p in patterns if p.confidence >= 0.5]
        if high_confidence_patterns:
            for pattern in high_confidence_patterns[:3]:  # Top 3 patterns
                recommendations.append({
                    'type': 'ingredient_combination',
                    'priority': 'high' if pattern.confidence >= 0.7 else 'medium',
                    'title': f'Avoid Ingredient Combination',
                    'description': f'This combination frequently causes {", ".join(pattern.symptoms)}',
                    'ingredients': pattern.ingredients_involved,
                    'action': f'Avoid consuming these ingredients together'
                })
        
        # Timing recommendations
        immediate_patterns = [p for p in patterns if p.time_pattern == 'immediate']
        if immediate_patterns:
            recommendations.append({
                'type': 'timing_pattern',
                'priority': 'medium',
                'title': 'Immediate Reaction Triggers',
                'description': 'These ingredients cause immediate symptoms',
                'ingredients': [ing for pattern in immediate_patterns 
                              for ing in pattern.ingredients_involved],
                'action': 'Be extra cautious with these ingredients'
            })
        
        return recommendations
    
    def _generate_summary(self, correlations: List[IngredientCorrelation], 
                         patterns: List[SymptomPattern]) -> Dict[str, Any]:
        """Generate analysis summary"""
        return {
            'total_correlations_found': len(correlations),
            'high_risk_ingredients': len([c for c in correlations if c.risk_assessment == 'avoid']),
            'medium_risk_ingredients': len([c for c in correlations if c.risk_assessment == 'caution']),
            'patterns_identified': len(patterns),
            'high_confidence_patterns': len([p for p in patterns if p.confidence >= 0.7]),
            'most_problematic_ingredient': correlations[0].ingredient if correlations else None,
            'analysis_confidence': 'high' if len(correlations) >= 5 else 'medium' if len(correlations) >= 2 else 'low'
        }
    
    def _identify_risk_ingredients(self, correlations: List[IngredientCorrelation]) -> List[Dict[str, Any]]:
        """Identify high-risk ingredients"""
        risk_ingredients = []
        
        for correlation in correlations:
            if correlation.risk_assessment in ['avoid', 'caution']:
                risk_ingredients.append({
                    'ingredient': correlation.ingredient,
                    'risk_level': correlation.risk_assessment,
                    'correlation_strength': correlation.correlation_strength,
                    'primary_symptoms': correlation.symptom,
                    'confidence': correlation.confidence_level,
                    'recommendation': self._get_ingredient_recommendation(correlation)
                })
        
        return risk_ingredients
    
    def _identify_safe_ingredients(self, combined_data: List[Dict], 
                                 correlations: List[IngredientCorrelation]) -> List[str]:
        """Identify ingredients that appear safe"""
        # Get all ingredients that appear in meals
        all_ingredients = set()
        for entry in combined_data:
            for meal in entry['related_meals']:
                for item in meal['items']:
                    all_ingredients.update(self._extract_ingredients(item))
        
        # Get ingredients with correlations
        correlated_ingredients = {c.ingredient for c in correlations}
        
        # Safe ingredients are those without significant correlations
        safe_ingredients = list(all_ingredients - correlated_ingredients)
        
        # Filter out known problematic ingredients
        safe_ingredients = [ing for ing in safe_ingredients 
                          if ing not in self.known_triggers]
        
        return safe_ingredients[:10]  # Return top 10 safe ingredients
    
    def _get_ingredient_recommendation(self, correlation: IngredientCorrelation) -> str:
        """Get specific recommendation for ingredient"""
        if correlation.risk_assessment == 'avoid':
            return f"Eliminate {correlation.ingredient} from your diet completely"
        elif correlation.risk_assessment == 'caution':
            return f"Limit {correlation.ingredient} and monitor symptoms carefully"
        else:
            return f"{correlation.ingredient} appears safe in moderation"
    
    def get_ingredient_safety_report(self, ingredient: str, 
                                   correlations: List[IngredientCorrelation]) -> Dict[str, Any]:
        """Get detailed safety report for specific ingredient"""
        ingredient_correlations = [c for c in correlations if c.ingredient == ingredient]
        
        if not ingredient_correlations:
            return {
                'ingredient': ingredient,
                'safety_status': 'unknown',
                'message': 'No correlation data available for this ingredient'
            }
        
        # Aggregate correlation data
        total_correlation = sum(c.correlation_strength for c in ingredient_correlations)
        avg_correlation = total_correlation / len(ingredient_correlations)
        symptoms = [c.symptom for c in ingredient_correlations]
        risk_level = ingredient_correlations[0].risk_assessment  # Assuming same risk for all
        
        return {
            'ingredient': ingredient,
            'safety_status': risk_level,
            'average_correlation': avg_correlation,
            'associated_symptoms': symptoms,
            'total_occurrences': sum(c.occurrences for c in ingredient_correlations),
            'confidence_level': ingredient_correlations[0].confidence_level,
            'recommendation': self._get_ingredient_recommendation(ingredient_correlations[0]),
            'alternatives': self._get_safe_alternatives(ingredient)
        }
    
    def _get_safe_alternatives(self, ingredient: str) -> List[str]:
        """Get safe alternatives for problematic ingredient"""
        alternatives = {
            'wheat': ['rice flour', 'almond flour', 'coconut flour', 'quinoa flour'],
            'flour': ['gluten-free flour blend', 'rice flour', 'almond flour'],
            'bread': ['gluten-free bread', 'rice cakes', 'corn tortillas'],
            'pasta': ['gluten-free pasta', 'rice noodles', 'zucchini noodles'],
            'soy sauce': ['tamari', 'coconut aminos', 'liquid aminos'],
            'beer': ['gluten-free beer', 'wine', 'hard cider'],
            'oats': ['certified gluten-free oats', 'quinoa flakes', 'rice cereal']
        }
        
        return alternatives.get(ingredient, [])


# Global instance
ingredient_correlator = IngredientCorrelator()