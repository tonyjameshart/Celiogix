# path: services/health_pattern_analyzer.py
"""
Health Pattern Analyzer for Celiac Disease Management

Provides comprehensive analysis of health patterns, symptom correlations,
gluten exposure tracking, and nutritional impact assessment.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics
import re


@dataclass
class HealthEntry:
    """Data class for health log entries"""
    id: int
    date: str
    time: str
    meal: str
    items: str
    risk: str
    onset_min: int
    severity: int
    stool: int
    recipe: str
    symptoms: str
    notes: str
    hydration_liters: float
    fiber_grams: float
    mood: str
    energy_level: int


@dataclass
class SymptomPattern:
    """Data class for identified symptom patterns"""
    symptoms: List[str]
    frequency: int
    severity_avg: float
    duration_avg: float
    trigger_foods: List[str]
    confidence: float


@dataclass
class GlutenExposure:
    """Data class for potential gluten exposure incidents"""
    date: str
    suspected_food: str
    symptoms: List[str]
    severity: float
    duration_hours: float
    recovery_time: float


@dataclass
class NutritionalImpact:
    """Data class for nutritional impact analysis"""
    nutrient: str
    deficiency_risk: float
    correlation_with_symptoms: float
    recommended_intake: float
    current_avg: float


@dataclass
class HealthTrend:
    """Data class for health trend analysis"""
    metric: str
    time_period: str
    trend_direction: str  # 'improving', 'declining', 'stable'
    change_percentage: float
    significance: float


class HealthPatternAnalyzer:
    """Main class for analyzing health patterns and correlations"""
    
    def __init__(self, db_path: str = "data/celiogix.db"):
        self.db_path = db_path
        
        # Gluten-containing ingredients to watch for
        self.gluten_ingredients = [
            'wheat', 'barley', 'rye', 'oats', 'malt', 'brewer\'s yeast',
            'flour', 'bread', 'pasta', 'couscous', 'bulgur', 'seitan',
            'soy sauce', 'teriyaki sauce', 'miso', 'beer', 'ale', 'lager',
            'malt vinegar', 'malt extract', 'malt syrup', 'malt flavoring',
            'hydrolyzed wheat protein', 'wheat starch', 'wheat germ',
            'barley malt', 'rye flour', 'spelt', 'triticale', 'kamut'
        ]
        
        # Common celiac symptoms
        self.celiac_symptoms = [
            'diarrhea', 'constipation', 'bloating', 'gas', 'abdominal pain',
            'nausea', 'vomiting', 'fatigue', 'headache', 'brain fog',
            'joint pain', 'skin rash', 'mouth sores', 'depression', 'anxiety',
            'weight loss', 'weight gain', 'malnutrition', 'anemia'
        ]
        
        # Bristol Stool Scale descriptions
        self.bristol_descriptions = {
            1: "Separate hard lumps, like nuts",
            2: "Sausage-shaped but lumpy", 
            3: "Like a sausage but with cracks on its surface",
            4: "Like a sausage or snake, smooth and soft",
            5: "Soft blobs with clear cut edges",
            6: "Mushy consistency with ragged edges",
            7: "Liquid consistency with no solid pieces"
        }
    
    def get_health_entries(self, days_back: int = 90) -> List[HealthEntry]:
        """Get health entries from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            cursor.execute("""
                SELECT id, date, time, meal, items, risk, onset_min, severity,
                       stool, recipe, symptoms, notes, hydration_liters, 
                       fiber_grams, mood, energy_level
                FROM health_log
                WHERE date >= ? AND date <= ?
                ORDER BY date DESC
            """, (start_date, end_date))
            
            entries = []
            for row in cursor.fetchall():
                entries.append(HealthEntry(
                    id=row[0],
                    date=row[1],
                    time=row[2] or "",
                    meal=row[3] or "",
                    items=row[4] or "",
                    risk=row[5] or "",
                    onset_min=row[6] or 0,
                    severity=row[7] or 0,
                    stool=row[8] or 4,
                    recipe=row[9] or "",
                    symptoms=row[10] or "",
                    notes=row[11] or "",
                    hydration_liters=row[12] or 0.0,
                    fiber_grams=row[13] or 0.0,
                    mood=row[14] or "neutral",
                    energy_level=row[15] or 5
                ))
            
            conn.close()
            return entries
            
        except Exception as e:
            print(f"Error fetching health entries: {str(e)}")
            return []
    
    def analyze_symptom_patterns(self, entries: List[HealthEntry]) -> List[SymptomPattern]:
        """Analyze patterns in symptoms"""
        symptom_frequency = defaultdict(int)
        symptom_severity = defaultdict(list)
        symptom_duration = defaultdict(list)
        symptom_triggers = defaultdict(set)
        
        for entry in entries:
            if entry.symptoms:
                symptoms = self._extract_symptoms(entry.symptoms)
                items = self._extract_food_items(entry.items_consumed)
                
                for symptom in symptoms:
                    symptom_frequency[symptom] += 1
                    symptom_severity[symptom].append(self._estimate_symptom_severity(entry))
                    symptom_duration[symptom].append(self._estimate_symptom_duration(entry))
                    
                    # Track potential triggers
                    for item in items:
                        if self._contains_gluten_ingredients(item):
                            symptom_triggers[symptom].add(item)
        
        # Create symptom patterns
        patterns = []
        for symptom, frequency in symptom_frequency.items():
            if frequency >= 3:  # Only include symptoms that occurred 3+ times
                avg_severity = statistics.mean(symptom_severity[symptom]) if symptom_severity[symptom] else 0
                avg_duration = statistics.mean(symptom_duration[symptom]) if symptom_duration[symptom] else 0
                confidence = min(1.0, frequency / 10.0)  # Higher frequency = higher confidence
                
                patterns.append(SymptomPattern(
                    symptoms=[symptom],
                    frequency=frequency,
                    severity_avg=avg_severity,
                    duration_avg=avg_duration,
                    trigger_foods=list(symptom_triggers[symptom]),
                    confidence=confidence
                ))
        
        # Sort by frequency and confidence
        patterns.sort(key=lambda x: (x.frequency, x.confidence), reverse=True)
        return patterns
    
    def detect_gluten_exposures(self, entries: List[HealthEntry]) -> List[GlutenExposure]:
        """Detect potential gluten exposure incidents"""
        exposures = []
        
        for entry in entries:
            if entry.items:
                items = self._extract_food_items(entry.items)
                gluten_items = [item for item in items if self._contains_gluten_ingredients(item)]
                
                if gluten_items and entry.symptoms:
                    symptoms = self._extract_symptoms(entry.symptoms)
                    severity = self._calculate_gluten_reaction_severity(entry)
                    
                    if severity > 0.3:  # Only include significant reactions
                        exposures.append(GlutenExposure(
                            date=entry.date,
                            suspected_food=", ".join(gluten_items),
                            symptoms=symptoms,
                            severity=severity,
                            duration_hours=self._estimate_symptom_duration(entry),
                            recovery_time=self._estimate_recovery_time(entry)
                        ))
        
        return exposures
    
    def analyze_nutritional_impact(self, entries: List[HealthEntry]) -> List[NutritionalImpact]:
        """Analyze nutritional impact on health"""
        nutritional_impacts = []
        
        # Analyze hydration impact
        hydration_data = [(entry.hydration_liters, self._get_health_score(entry)) 
                         for entry in entries if entry.hydration_liters > 0]
        if hydration_data:
            hydration_correlation = self._calculate_correlation(
                [d[0] for d in hydration_data], 
                [d[1] for d in hydration_data]
            )
            avg_hydration = statistics.mean([d[0] for d in hydration_data])
            
            nutritional_impacts.append(NutritionalImpact(
                nutrient="Hydration (L/day)",
                deficiency_risk=1.0 if avg_hydration < 2.0 else 0.0,
                correlation_with_symptoms=abs(hydration_correlation),
                recommended_intake=2.5,
                current_avg=avg_hydration
            ))
        
        # Analyze fiber impact
        fiber_data = [(entry.fiber_grams, self._get_health_score(entry)) 
                     for entry in entries if entry.fiber_grams > 0]
        if fiber_data:
            fiber_correlation = self._calculate_correlation(
                [d[0] for d in fiber_data], 
                [d[1] for d in fiber_data]
            )
            avg_fiber = statistics.mean([d[0] for d in fiber_data])
            
            nutritional_impacts.append(NutritionalImpact(
                nutrient="Fiber (g/day)",
                deficiency_risk=1.0 if avg_fiber < 25.0 else 0.0,
                correlation_with_symptoms=abs(fiber_correlation),
                recommended_intake=30.0,
                current_avg=avg_fiber
            ))
        
        return nutritional_impacts
    
    def analyze_health_trends(self, entries: List[HealthEntry]) -> List[HealthTrend]:
        """Analyze health trends over time"""
        trends = []
        
        if len(entries) < 7:  # Need at least a week of data
            return trends
        
        # Sort entries by date
        entries.sort(key=lambda x: x.date)
        
        # Analyze different metrics
        metrics = {
            'energy_level': [entry.energy_level for entry in entries],
            'bristol_scale': [entry.stool for entry in entries],
            'hydration': [entry.hydration_liters for entry in entries],
            'fiber': [entry.fiber_grams for entry in entries]
        }
        
        for metric_name, values in metrics.items():
            if len(values) >= 7:
                # Calculate trend over time
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = statistics.mean(first_half)
                second_avg = statistics.mean(second_half)
                
                change_percentage = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
                
                # Determine trend direction
                if change_percentage > 5:
                    trend_direction = 'improving'
                elif change_percentage < -5:
                    trend_direction = 'declining'
                else:
                    trend_direction = 'stable'
                
                # Calculate significance (how confident we are in this trend)
                significance = min(1.0, len(values) / 30.0)  # More data = more significant
                
                trends.append(HealthTrend(
                    metric=metric_name.replace('_', ' ').title(),
                    time_period=f"{len(entries)} days",
                    trend_direction=trend_direction,
                    change_percentage=abs(change_percentage),
                    significance=significance
                ))
        
        return trends
    
    def generate_health_insights(self, entries: List[HealthEntry]) -> Dict[str, Any]:
        """Generate comprehensive health insights"""
        insights = {
            'summary': {},
            'symptom_patterns': [],
            'gluten_exposures': [],
            'nutritional_impacts': [],
            'health_trends': [],
            'recommendations': []
        }
        
        if not entries:
            insights['summary'] = {'message': 'No health data available for analysis'}
            return insights
        
        # Generate summary statistics
        insights['summary'] = self._generate_summary_stats(entries)
        
        # Analyze different aspects
        insights['symptom_patterns'] = self.analyze_symptom_patterns(entries)
        insights['gluten_exposures'] = self.detect_gluten_exposures(entries)
        insights['nutritional_impacts'] = self.analyze_nutritional_impact(entries)
        insights['health_trends'] = self.analyze_health_trends(entries)
        
        # Generate recommendations
        insights['recommendations'] = self._generate_recommendations(insights)
        
        return insights
    
    # Helper methods
    
    def _extract_symptoms(self, symptoms_text: str) -> List[str]:
        """Extract individual symptoms from text"""
        if not symptoms_text:
            return []
        
        symptoms_text = symptoms_text.lower()
        found_symptoms = []
        
        for symptom in self.celiac_symptoms:
            if symptom in symptoms_text:
                found_symptoms.append(symptom)
        
        return found_symptoms
    
    def _extract_food_items(self, items_text: str) -> List[str]:
        """Extract food items from text"""
        if not items_text:
            return []
        
        # Split by common delimiters and clean up
        items = re.split(r'[,;|\n\r]+', items_text)
        return [item.strip() for item in items if item.strip()]
    
    def _contains_gluten_ingredients(self, food_item: str) -> bool:
        """Check if food item contains gluten ingredients"""
        food_item = food_item.lower()
        return any(ingredient in food_item for ingredient in self.gluten_ingredients)
    
    def _estimate_symptom_severity(self, entry: HealthEntry) -> float:
        """Estimate symptom severity based on entry data"""
        severity = 0.0
        
        # Bristol scale severity (1-2 or 6-7 are concerning)
        if entry.stool in [1, 2, 6, 7]:
            severity += 0.4
        
        # Low energy level
        if entry.energy_level <= 3:
            severity += 0.3
        
        # Poor mood
        if entry.mood in ['poor', 'terrible', 'awful']:
            severity += 0.3
        
        return min(1.0, severity)
    
    def _estimate_symptom_duration(self, entry: HealthEntry) -> float:
        """Estimate symptom duration in hours"""
        # This is a simplified estimation - in a real app you'd track actual duration
        if entry.stool in [1, 2, 6, 7]:
            return 24.0  # Assume digestive symptoms last about a day
        return 8.0  # Assume other symptoms last about 8 hours
    
    def _calculate_gluten_reaction_severity(self, entry: HealthEntry) -> float:
        """Calculate severity of potential gluten reaction"""
        severity = 0.0
        
        # Check for digestive symptoms
        digestive_symptoms = ['diarrhea', 'constipation', 'bloating', 'gas', 'abdominal pain']
        symptoms = self._extract_symptoms(entry.symptoms)
        
        for symptom in symptoms:
            if symptom in digestive_symptoms:
                severity += 0.3
            elif symptom in ['nausea', 'vomiting']:
                severity += 0.4
            elif symptom in ['fatigue', 'brain fog']:
                severity += 0.2
        
        # Check Bristol scale
        if entry.stool in [1, 2, 6, 7]:
            severity += 0.3
        
        return min(1.0, severity)
    
    def _estimate_recovery_time(self, entry: HealthEntry) -> float:
        """Estimate recovery time in hours"""
        severity = self._calculate_gluten_reaction_severity(entry)
        return 24.0 * severity  # Assume 1 day per severity unit
    
    def _get_health_score(self, entry: HealthEntry) -> float:
        """Calculate overall health score for an entry (0-1, higher is better)"""
        score = 0.5  # Base score
        
        # Bristol scale (4 is ideal)
        if entry.stool == 4:
            score += 0.2
        elif entry.stool in [3, 5]:
            score += 0.1
        
        # Energy level (higher is better)
        score += (entry.energy_level - 5) * 0.1
        
        # Mood
        if entry.mood in ['excellent', 'great', 'good']:
            score += 0.2
        elif entry.mood in ['poor', 'terrible']:
            score -= 0.2
        
        # Hydration (optimal around 2.5L)
        if 2.0 <= entry.hydration_liters <= 3.0:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate correlation coefficient between two lists"""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        try:
            x_mean = statistics.mean(x_values)
            y_mean = statistics.mean(y_values)
            
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
            x_variance = sum((x - x_mean) ** 2 for x in x_values)
            y_variance = sum((y - y_mean) ** 2 for y in y_values)
            
            if x_variance == 0 or y_variance == 0:
                return 0.0
            
            correlation = numerator / (x_variance * y_variance) ** 0.5
            return correlation
        except:
            return 0.0
    
    def _generate_summary_stats(self, entries: List[HealthEntry]) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not entries:
            return {}
        
        total_days = len(entries)
        symptoms_days = len([e for e in entries if e.symptoms])
        avg_energy = statistics.mean([e.energy_level for e in entries]) if entries else 0
        avg_bristol = statistics.mean([e.stool for e in entries]) if entries else 0
        hydration_values = [e.hydration_liters for e in entries if e.hydration_liters > 0]
        avg_hydration = statistics.mean(hydration_values) if hydration_values else 0
        fiber_values = [e.fiber_grams for e in entries if e.fiber_grams > 0]
        avg_fiber = statistics.mean(fiber_values) if fiber_values else 0
        
        return {
            'total_days_tracked': total_days,
            'days_with_symptoms': symptoms_days,
            'symptom_frequency': symptoms_days / total_days if total_days > 0 else 0,
            'average_energy_level': round(avg_energy, 1),
            'average_bristol_scale': round(avg_bristol, 1),
            'average_hydration_liters': round(avg_hydration, 1) if avg_hydration > 0 else 0,
            'average_fiber_grams': round(avg_fiber, 1) if avg_fiber > 0 else 0
        }
    
    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations based on analysis"""
        recommendations = []
        
        # Check symptom patterns
        symptom_patterns = insights.get('symptom_patterns', [])
        if symptom_patterns:
            top_symptom = symptom_patterns[0]
            if top_symptom.frequency >= 5:
                recommendations.append(f"Consider discussing recurring {top_symptom.symptoms[0]} with your healthcare provider")
        
        # Check gluten exposures
        gluten_exposures = insights.get('gluten_exposures', [])
        if gluten_exposures:
            recommendations.append("Consider reviewing food labels more carefully to avoid gluten exposure")
        
        # Check nutritional impacts
        nutritional_impacts = insights.get('nutritional_impacts', [])
        for impact in nutritional_impacts:
            if impact.deficiency_risk > 0.5:
                recommendations.append(f"Consider increasing {impact.nutrient} intake")
        
        # Check health trends
        health_trends = insights.get('health_trends', [])
        declining_trends = [t for t in health_trends if t.trend_direction == 'declining']
        if declining_trends:
            recommendations.append("Some health metrics are declining - consider consulting with your healthcare team")
        
        # General recommendations
        summary = insights.get('summary', {})
        symptom_frequency = summary.get('symptom_frequency', 0)
        if symptom_frequency > 0.3:  # More than 30% of days have symptoms
            recommendations.append("High symptom frequency detected - consider stricter gluten-free diet adherence")
        
        if not recommendations:
            recommendations.append("Keep up the great work! Continue tracking your health data.")
        
        return recommendations


# Convenience functions
def analyze_health_patterns(db_path: str = "data/celiogix.db", days_back: int = 90) -> Dict[str, Any]:
    """Analyze health patterns from the database"""
    analyzer = HealthPatternAnalyzer(db_path)
    entries = analyzer.get_health_entries(days_back)
    return analyzer.generate_health_insights(entries)


def get_symptom_correlations(db_path: str = "data/celiogix.db") -> List[SymptomPattern]:
    """Get symptom correlation patterns"""
    analyzer = HealthPatternAnalyzer(db_path)
    entries = analyzer.get_health_entries()
    return analyzer.analyze_symptom_patterns(entries)


def detect_gluten_exposures(db_path: str = "data/celiogix.db") -> List[GlutenExposure]:
    """Detect potential gluten exposure incidents"""
    analyzer = HealthPatternAnalyzer(db_path)
    entries = analyzer.get_health_entries()
    return analyzer.detect_gluten_exposures(entries)
