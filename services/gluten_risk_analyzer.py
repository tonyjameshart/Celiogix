#!/usr/bin/env python3
"""
Gluten risk analyzer for barcode scanning and ingredient analysis
"""

import re
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QObject, Signal


class RiskLevel(Enum):
    """Risk level enumeration"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    UNSAFE = "unsafe"
    UNKNOWN = "unknown"


class GlutenSource(Enum):
    """Gluten source enumeration"""
    WHEAT = "wheat"
    RYE = "rye"
    BARLEY = "barley"
    OATS = "oats"  # May contain gluten
    TRITICALE = "triticale"
    SPELT = "spelt"
    KAMUT = "kamut"
    FARRO = "farro"
    BULGUR = "bulgur"
    COUSCOUS = "couscous"


@dataclass
class GlutenRiskResult:
    """Gluten risk analysis result"""
    product_name: str
    barcode: Optional[str]
    risk_level: RiskLevel
    confidence_score: float  # 0.0 to 1.0
    detected_sources: List[GlutenSource]
    problematic_ingredients: List[str]
    safe_ingredients: List[str]
    cross_contamination_risk: bool
    manufacturing_notes: List[str]
    certification_status: Optional[str]
    recommendation: str


class GlutenRiskAnalyzer(QObject):
    """Analyzer for gluten risk in products and ingredients"""
    
    # Signals
    analysis_completed = Signal(GlutenRiskResult)
    risk_detected = Signal(RiskLevel, List[str])  # risk_level, problematic_ingredients
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gluten_sources = self._load_gluten_sources()
        self.hidden_gluten_terms = self._load_hidden_gluten_terms()
        self.safe_ingredients = self._load_safe_ingredients()
        self.certification_keywords = self._load_certification_keywords()
        self.manufacturing_risk_terms = self._load_manufacturing_risk_terms()
    
    def _load_gluten_sources(self) -> Dict[GlutenSource, List[str]]:
        """Load gluten source terms"""
        return {
            GlutenSource.WHEAT: [
                'wheat', 'wheat flour', 'wheat starch', 'wheat protein', 'wheat bran',
                'wheat germ', 'wheat berries', 'durum wheat', 'hard wheat', 'soft wheat',
                'wheat gluten', 'vital wheat gluten', 'wheat malt', 'wheat dextrin',
                'wheat fiber', 'wheat grass', 'wheat grass juice', 'wheat grass powder'
            ],
            GlutenSource.RYE: [
                'rye', 'rye flour', 'rye bread', 'rye meal', 'rye malt', 'rye starch'
            ],
            GlutenSource.BARLEY: [
                'barley', 'barley flour', 'barley malt', 'barley extract', 'barley starch',
                'barley protein', 'malt', 'malt extract', 'malt syrup', 'malt flavoring',
                'malt vinegar', 'maltodextrin', 'barley grass', 'barley grass juice'
            ],
            GlutenSource.OATS: [
                'oats', 'oat flour', 'oat bran', 'oat fiber', 'oat protein', 'oat starch',
                'oat extract', 'oatmeal', 'rolled oats', 'steel cut oats', 'quick oats'
            ],
            GlutenSource.TRITICALE: [
                'triticale', 'triticale flour', 'triticale starch'
            ],
            GlutenSource.SPELT: [
                'spelt', 'spelt flour', 'spelt starch', 'spelt protein'
            ],
            GlutenSource.KAMUT: [
                'kamut', 'kamut flour', 'kamut starch'
            ],
            GlutenSource.FARRO: [
                'farro', 'farro flour', 'emmer', 'emmer flour'
            ],
            GlutenSource.BULGUR: [
                'bulgur', 'bulgur wheat', 'cracked wheat'
            ],
            GlutenSource.COUSCOUS: [
                'couscous', 'pearl couscous', 'israeli couscous'
            ]
        }
    
    def _load_hidden_gluten_terms(self) -> List[str]:
        """Load hidden gluten terms that may not be obvious"""
        return [
            'modified food starch', 'food starch', 'starch', 'modified starch',
            'vegetable starch', 'corn starch', 'potato starch', 'tapioca starch',
            'natural flavoring', 'artificial flavoring', 'flavoring', 'natural flavors',
            'artificial flavors', 'spices', 'seasoning', 'seasonings', 'spice blend',
            'hydrolyzed vegetable protein', 'hydrolyzed plant protein', 'hvp',
            'textured vegetable protein', 'tvp', 'vegetable protein',
            'caramel color', 'caramel coloring', 'caramel',
            'dextrin', 'dextrose', 'glucose syrup', 'corn syrup',
            'soy sauce', 'teriyaki sauce', 'worcestershire sauce',
            'miso', 'tempeh', 'seitan', 'vital wheat gluten',
            'baking powder', 'baking soda', 'yeast extract',
            'mono and diglycerides', 'lecithin', 'lecithin (soy)',
            'gum arabic', 'xanthan gum', 'guar gum', 'locust bean gum',
            'vegetable oil', 'canola oil', 'soybean oil',
            'rice vinegar', 'distilled vinegar', 'white vinegar',
            'vanilla extract', 'vanilla flavoring',
            'smoke flavoring', 'liquid smoke',
            'broth', 'stock', 'bouillon', 'soup base',
            'thickener', 'thickening agent', 'binding agent'
        ]
    
    def _load_safe_ingredients(self) -> List[str]:
        """Load known safe ingredients"""
        return [
            'rice', 'rice flour', 'rice starch', 'rice bran',
            'corn', 'corn flour', 'cornmeal', 'corn starch', 'corn syrup',
            'potato', 'potato flour', 'potato starch', 'potato flakes',
            'tapioca', 'tapioca flour', 'tapioca starch',
            'quinoa', 'quinoa flour', 'quinoa flakes',
            'buckwheat', 'buckwheat flour', 'buckwheat groats',
            'amaranth', 'amaranth flour',
            'millet', 'millet flour',
            'sorghum', 'sorghum flour',
            'teff', 'teff flour',
            'arrowroot', 'arrowroot flour', 'arrowroot starch',
            'cassava', 'cassava flour', 'yuca',
            'coconut', 'coconut flour', 'coconut oil',
            'almond', 'almond flour', 'almond meal',
            'walnut', 'walnut flour',
            'pecan', 'pecan flour',
            'hazelnut', 'hazelnut flour',
            'sunflower seeds', 'sunflower seed flour',
            'pumpkin seeds', 'pumpkin seed flour',
            'flax seeds', 'flax meal', 'flaxseed',
            'chia seeds', 'chia flour',
            'hemp seeds', 'hemp flour',
            'psyllium husk', 'psyllium powder',
            'xanthan gum', 'guar gum', 'locust bean gum',
            'baking soda', 'baking powder (aluminum free)',
            'cream of tartar', 'tartaric acid',
            'salt', 'sea salt', 'kosher salt',
            'sugar', 'brown sugar', 'coconut sugar', 'maple syrup',
            'honey', 'agave nectar', 'stevia', 'erythritol',
            'cocoa powder', 'chocolate', 'cacao',
            'vanilla extract', 'vanilla bean',
            'cinnamon', 'nutmeg', 'ginger', 'turmeric',
            'garlic', 'onion', 'lemon', 'lime', 'orange'
        ]
    
    def _load_certification_keywords(self) -> List[str]:
        """Load gluten-free certification keywords"""
        return [
            'gluten free', 'gluten-free', 'gf', 'celiac safe',
            'certified gluten free', 'certified gluten-free',
            'gfco certified', 'gfco', 'gluten free certification organization',
            'nsf gluten free', 'nsf certified gluten free',
            'beyond celiac', 'celiac disease foundation',
            'may contain gluten', 'processed in facility with wheat',
            'made in facility that processes wheat', 'may contain wheat',
            'processed on shared equipment', 'shared equipment',
            'manufactured in facility that processes wheat'
        ]
    
    def _load_manufacturing_risk_terms(self) -> List[str]:
        """Load manufacturing risk terms"""
        return [
            'processed in facility with wheat', 'made in facility that processes wheat',
            'may contain wheat', 'processed on shared equipment',
            'shared equipment', 'manufactured in facility that processes wheat',
            'may contain gluten', 'processed in facility with gluten',
            'made on shared equipment with wheat', 'cross contamination',
            'facility also processes wheat', 'equipment also used for wheat',
            'may be processed on equipment that also processes wheat'
        ]
    
    def analyze_product(self, product_name: str, ingredients: str, 
                       barcode: Optional[str] = None, 
                       additional_info: Optional[str] = None) -> GlutenRiskResult:
        """
        Analyze product for gluten risk
        
        Args:
            product_name: Name of the product
            ingredients: Ingredients list as string
            barcode: Product barcode (optional)
            additional_info: Additional product information (optional)
            
        Returns:
            GlutenRiskResult with analysis
        """
        # Normalize inputs
        ingredients_lower = ingredients.lower()
        product_name_lower = product_name.lower()
        additional_lower = (additional_info or "").lower()
        
        # Analyze ingredients
        detected_sources = []
        problematic_ingredients = []
        safe_ingredients = []
        cross_contamination_risk = False
        manufacturing_notes = []
        certification_status = None
        
        # Check for direct gluten sources
        for source, terms in self.gluten_sources.items():
            for term in terms:
                if term in ingredients_lower:
                    detected_sources.append(source)
                    problematic_ingredients.append(term)
        
        # Check for hidden gluten terms
        for term in self.hidden_gluten_terms:
            if term in ingredients_lower:
                problematic_ingredients.append(term)
        
        # Check for safe ingredients
        for term in self.safe_ingredients:
            if term in ingredients_lower:
                safe_ingredients.append(term)
        
        # Check for certification keywords
        for term in self.certification_keywords:
            if term in ingredients_lower or term in product_name_lower or term in additional_lower:
                if 'gluten free' in term or 'gf' in term:
                    certification_status = "certified_gluten_free"
                elif 'may contain' in term or 'processed in facility' in term:
                    cross_contamination_risk = True
                    manufacturing_notes.append(term)
        
        # Check for manufacturing risk terms
        for term in self.manufacturing_risk_terms:
            if term in ingredients_lower or term in additional_lower:
                cross_contamination_risk = True
                manufacturing_notes.append(term)
        
        # Determine risk level and confidence
        risk_level, confidence = self._calculate_risk_level(
            detected_sources, problematic_ingredients, cross_contamination_risk,
            certification_status, safe_ingredients
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            risk_level, detected_sources, cross_contamination_risk, certification_status
        )
        
        result = GlutenRiskResult(
            product_name=product_name,
            barcode=barcode,
            risk_level=risk_level,
            confidence_score=confidence,
            detected_sources=detected_sources,
            problematic_ingredients=problematic_ingredients,
            safe_ingredients=safe_ingredients,
            cross_contamination_risk=cross_contamination_risk,
            manufacturing_notes=manufacturing_notes,
            certification_status=certification_status,
            recommendation=recommendation
        )
        
        # Emit signals
        self.analysis_completed.emit(result)
        if risk_level in [RiskLevel.HIGH_RISK, RiskLevel.UNSAFE]:
            self.risk_detected.emit(risk_level, problematic_ingredients)
        
        return result
    
    def _calculate_risk_level(self, detected_sources: List[GlutenSource],
                            problematic_ingredients: List[str],
                            cross_contamination_risk: bool,
                            certification_status: Optional[str],
                            safe_ingredients: List[str]) -> Tuple[RiskLevel, float]:
        """Calculate risk level and confidence score"""
        
        # Direct gluten sources present
        if detected_sources:
            return RiskLevel.UNSAFE, 0.95
        
        # Hidden gluten terms present
        if problematic_ingredients:
            # Check if it's a known safe ingredient
            safe_problematic = [ing for ing in problematic_ingredients if ing in safe_ingredients]
            if len(safe_problematic) == len(problematic_ingredients):
                # All problematic ingredients are actually safe
                return RiskLevel.SAFE, 0.8
            else:
                return RiskLevel.HIGH_RISK, 0.85
        
        # Cross contamination risk
        if cross_contamination_risk:
            if certification_status == "certified_gluten_free":
                return RiskLevel.LOW_RISK, 0.7
            else:
                return RiskLevel.MEDIUM_RISK, 0.75
        
        # Certified gluten-free
        if certification_status == "certified_gluten_free":
            return RiskLevel.SAFE, 0.9
        
        # Product name suggests gluten-free
        if any(term in self.certification_keywords for term in ['gluten free', 'gf']):
            return RiskLevel.SAFE, 0.8
        
        # Only safe ingredients detected
        if safe_ingredients and not problematic_ingredients:
            return RiskLevel.SAFE, 0.7
        
        # No clear indicators
        return RiskLevel.UNKNOWN, 0.5
    
    def _generate_recommendation(self, risk_level: RiskLevel,
                               detected_sources: List[GlutenSource],
                               cross_contamination_risk: bool,
                               certification_status: Optional[str]) -> str:
        """Generate recommendation based on analysis"""
        
        if risk_level == RiskLevel.SAFE:
            if certification_status == "certified_gluten_free":
                return "✅ SAFE: This product is certified gluten-free and safe for celiac consumption."
            else:
                return "✅ LIKELY SAFE: No gluten sources detected, but verify certification if possible."
        
        elif risk_level == RiskLevel.LOW_RISK:
            return "⚠️ LOW RISK: Minor cross-contamination risk. Consider your sensitivity level."
        
        elif risk_level == RiskLevel.MEDIUM_RISK:
            return "⚠️ MEDIUM RISK: Cross-contamination risk present. Not recommended for celiac consumption."
        
        elif risk_level == RiskLevel.HIGH_RISK:
            return "❌ HIGH RISK: Hidden gluten sources detected. Not safe for celiac consumption."
        
        elif risk_level == RiskLevel.UNSAFE:
            source_names = [source.value for source in detected_sources]
            return f"❌ UNSAFE: Contains gluten sources: {', '.join(source_names)}. Not safe for celiac consumption."
        
        else:  # UNKNOWN
            return "❓ UNKNOWN: Unable to determine gluten status. Contact manufacturer or avoid."
    
    def analyze_ingredient_list(self, ingredients: str) -> Dict[str, Any]:
        """Analyze ingredient list and return detailed breakdown"""
        ingredients_lower = ingredients.lower()
        
        analysis = {
            'total_ingredients': len(ingredients.split(',')),
            'gluten_sources_found': [],
            'hidden_gluten_found': [],
            'safe_ingredients_found': [],
            'certification_keywords': [],
            'manufacturing_risks': [],
            'risk_score': 0.0
        }
        
        # Check each category
        for source, terms in self.gluten_sources.items():
            for term in terms:
                if term in ingredients_lower:
                    analysis['gluten_sources_found'].append({
                        'source': source.value,
                        'term': term
                    })
        
        for term in self.hidden_gluten_terms:
            if term in ingredients_lower:
                analysis['hidden_gluten_found'].append(term)
        
        for term in self.safe_ingredients:
            if term in ingredients_lower:
                analysis['safe_ingredients_found'].append(term)
        
        for term in self.certification_keywords:
            if term in ingredients_lower:
                analysis['certification_keywords'].append(term)
        
        for term in self.manufacturing_risk_terms:
            if term in ingredients_lower:
                analysis['manufacturing_risks'].append(term)
        
        # Calculate risk score
        risk_score = 0.0
        if analysis['gluten_sources_found']:
            risk_score += 1.0
        if analysis['hidden_gluten_found']:
            risk_score += 0.7
        if analysis['manufacturing_risks']:
            risk_score += 0.5
        if analysis['certification_keywords'] and 'gluten free' in ' '.join(analysis['certification_keywords']):
            risk_score -= 0.3
        
        analysis['risk_score'] = min(1.0, max(0.0, risk_score))
        
        return analysis
    
    def get_gluten_free_alternatives(self, problematic_ingredient: str) -> List[str]:
        """Get gluten-free alternatives for problematic ingredient"""
        alternatives = {
            'wheat flour': ['rice flour', 'almond flour', 'coconut flour', 'tapioca flour'],
            'wheat starch': ['corn starch', 'potato starch', 'tapioca starch'],
            'soy sauce': ['tamari (gluten-free)', 'coconut aminos', 'gluten-free soy sauce'],
            'malt vinegar': ['apple cider vinegar', 'white vinegar', 'rice vinegar'],
            'beer': ['gluten-free beer', 'cider', 'wine', 'spirits'],
            'breadcrumbs': ['gluten-free breadcrumbs', 'almond meal', 'coconut flakes'],
            'pasta': ['rice pasta', 'quinoa pasta', 'corn pasta', 'zucchini noodles'],
            'couscous': ['quinoa', 'rice', 'millet', 'buckwheat groats']
        }
        
        return alternatives.get(problematic_ingredient.lower(), [])
    
    def validate_barcode(self, barcode: str) -> Dict[str, Any]:
        """Validate barcode format and return metadata"""
        barcode = barcode.strip()
        
        validation = {
            'is_valid': False,
            'format': None,
            'length': len(barcode),
            'checksum_valid': False,
            'country_code': None,
            'manufacturer': None
        }
        
        if not barcode.isdigit():
            return validation
        
        if len(barcode) == 13:  # EAN-13
            validation['format'] = 'EAN-13'
            validation['is_valid'] = self._validate_ean13_checksum(barcode)
            if validation['is_valid']:
                validation['country_code'] = barcode[:3]
        elif len(barcode) == 12:  # UPC-A
            validation['format'] = 'UPC-A'
            validation['is_valid'] = self._validate_upc_checksum(barcode)
        elif len(barcode) == 8:  # EAN-8
            validation['format'] = 'EAN-8'
            validation['is_valid'] = self._validate_ean8_checksum(barcode)
        
        return validation
    
    def _validate_ean13_checksum(self, barcode: str) -> bool:
        """Validate EAN-13 checksum"""
        if len(barcode) != 13:
            return False
        
        checksum = 0
        for i, digit in enumerate(barcode[:12]):
            checksum += int(digit) * (3 if i % 2 == 1 else 1)
        
        return (10 - (checksum % 10)) % 10 == int(barcode[12])
    
    def _validate_upc_checksum(self, barcode: str) -> bool:
        """Validate UPC-A checksum"""
        if len(barcode) != 12:
            return False
        
        checksum = 0
        for i, digit in enumerate(barcode[:11]):
            checksum += int(digit) * (3 if i % 2 == 1 else 1)
        
        return (10 - (checksum % 10)) % 10 == int(barcode[11])
    
    def _validate_ean8_checksum(self, barcode: str) -> bool:
        """Validate EAN-8 checksum"""
        if len(barcode) != 8:
            return False
        
        checksum = 0
        for i, digit in enumerate(barcode[:7]):
            checksum += int(digit) * (3 if i % 2 == 1 else 1)
        
        return (10 - (checksum % 10)) % 10 == int(barcode[7])


# Global gluten risk analyzer instance
_gluten_risk_analyzer = None


def get_gluten_risk_analyzer() -> GlutenRiskAnalyzer:
    """Get global gluten risk analyzer"""
    global _gluten_risk_analyzer
    if _gluten_risk_analyzer is None:
        _gluten_risk_analyzer = GlutenRiskAnalyzer()
    return _gluten_risk_analyzer
