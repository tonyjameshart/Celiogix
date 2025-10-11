# path: services/upc_scanner.py
"""
UPC Scanner Service for CeliacShield

Provides UPC/barcode scanning functionality with gluten-free safety checking.
"""

import requests
import json
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime
from services.nutrition_analyzer import nutrition_analyzer, NutritionData


@dataclass
class ProductInfo:
    """Data class for product information"""
    upc: str
    name: str
    brand: str
    category: str
    gluten_free: Optional[bool]
    gluten_warning: Optional[str]
    ingredients: List[str]
    nutrition_info: Dict[str, Any]
    detailed_nutrition: Optional[NutritionData]
    image_url: Optional[str]
    source: str
    confidence: float


class UPCScanner:
    """Main UPC scanner class for gluten-free product checking"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Gluten-containing ingredients to watch for
        self.gluten_ingredients = [
            'wheat', 'barley', 'rye', 'oats', 'malt', 'brewer\'s yeast',
            'flour', 'bread', 'pasta', 'couscous', 'bulgur', 'seitan',
            'soy sauce', 'teriyaki sauce', 'miso', 'beer', 'ale', 'lager',
            'malt vinegar', 'malt extract', 'malt syrup', 'malt flavoring',
            'hydrolyzed wheat protein', 'wheat starch', 'wheat germ',
            'barley malt', 'rye flour', 'spelt', 'triticale', 'kamut'
        ]
        
        # Gluten-free certification indicators
        self.gf_certifications = [
            'gluten-free', 'gluten free', 'gf', 'certified gluten-free',
            'celiac safe', 'no gluten', 'free from gluten'
        ]
    
    def scan_upc(self, upc_code: str) -> Optional[ProductInfo]:
        """Scan UPC code and return product information with gluten safety check"""
        try:
            # Clean and validate UPC code
            upc_code = self._clean_upc(upc_code)
            if not self._validate_upc(upc_code):
                return None
            
            # Check both UPC databases for comprehensive information
            product_data = self._get_comprehensive_product_data(upc_code)
            
            if product_data:
                # Analyze for gluten safety
                gluten_analysis = self._analyze_gluten_safety(product_data)
                
                # Get detailed nutrition analysis
                detailed_nutrition = self._get_detailed_nutrition(product_data)
                
                return ProductInfo(
                    upc=upc_code,
                    name=product_data.get('name', 'Unknown Product'),
                    brand=product_data.get('brand', 'Unknown Brand'),
                    category=product_data.get('category', 'Unknown Category'),
                    gluten_free=gluten_analysis['is_gluten_free'],
                    gluten_warning=gluten_analysis['warning'],
                    ingredients=product_data.get('ingredients', []),
                    nutrition_info=product_data.get('nutrition', {}),
                    detailed_nutrition=detailed_nutrition,
                    image_url=product_data.get('image_url'),
                    source=product_data.get('source', 'Unknown'),
                    confidence=gluten_analysis['confidence']
                )
            
            return None
            
        except Exception as e:
            print(f"Error scanning UPC {upc_code}: {str(e)}")
            return None
    
    def _clean_upc(self, upc_code: str) -> str:
        """Clean and normalize UPC code for both UPC-A (12 digits) and EAN-13 (13 digits)"""
        # Remove any non-digit characters
        cleaned = ''.join(filter(str.isdigit, upc_code))
        
        # Handle different barcode formats
        if len(cleaned) == 12:
            # Check if this is actually an EAN-13 that needs padding
            if self._is_likely_ean13(cleaned):
                # Pad with leading zero for EAN-13
                return '0' + cleaned
            else:
                # UPC-A format (12 digits)
                return cleaned
        elif len(cleaned) == 13:
            # EAN-13 format (13 digits)
            return cleaned
        elif len(cleaned) == 8:
            # UPC-E format (8 digits) - convert to UPC-A
            return self._convert_upc_e_to_upc_a(cleaned)
        elif len(cleaned) < 12:
            # Pad with leading zeros for UPC-A
            return cleaned.zfill(12)
        elif len(cleaned) > 13:
            # Truncate to EAN-13 length
            return cleaned[:13]
        else:
            # Default to 12 digits for UPC-A
            return cleaned.zfill(12)
    
    def _is_likely_ean13(self, upc_code: str) -> bool:
        """Check if a 12-digit code is likely an EAN-13 that needs padding"""
        # Try both validations - if UPC-A fails but EAN-13 (with padding) passes, it's EAN-13
        digits = [int(d) for d in upc_code]
        
        # Test UPC-A validation
        try:
            odd_sum = sum(digits[i] for i in range(0, 11, 2))
            even_sum = sum(digits[i] for i in range(1, 11, 2))
            total = odd_sum + (even_sum * 3)
            checksum = (10 - (total % 10)) % 10
            upc_a_valid = digits[11] == checksum
        except:
            upc_a_valid = False
        
        # Test EAN-13 validation (with leading zero)
        try:
            ean_digits = [0] + digits  # Add leading zero
            ean_odd_sum = sum(ean_digits[i] for i in range(0, 12, 2))
            ean_even_sum = sum(ean_digits[i] for i in range(1, 12, 2))
            ean_total = ean_odd_sum + (ean_even_sum * 3)
            ean_checksum = (10 - (ean_total % 10)) % 10
            ean13_valid = ean_digits[12] == ean_checksum
        except:
            ean13_valid = False
        
        # If UPC-A fails but EAN-13 passes, it's likely EAN-13
        return not upc_a_valid and ean13_valid
    
    def _convert_upc_e_to_upc_a(self, upc_e: str) -> str:
        """Convert UPC-E (8 digits) to UPC-A (12 digits)"""
        if len(upc_e) != 8:
            return upc_e.zfill(12)
        
        # UPC-E to UPC-A conversion logic
        # This is a simplified conversion - in practice, this would need
        # the full UPC-E expansion table
        return upc_e.zfill(12)
    
    def _get_comprehensive_product_data(self, upc_code: str) -> Optional[Dict]:
        """Get comprehensive product data by checking both UPC databases"""
        print(f"Scanning UPC {upc_code} across multiple databases...")
        
        # Initialize combined product data
        combined_data = {
            'name': '',
            'brand': '',
            'category': '',
            'ingredients': [],
            'nutrition': {},
            'image_url': None,
            'sources': [],
            'confidence_score': 0
        }
        
        # Check OpenFoodFacts (primary - best for ingredients and nutrition)
        print("  Checking OpenFoodFacts...")
        of_data = self._get_from_openfoodfacts(upc_code)
        if of_data:
            print(f"    [FOUND] OpenFoodFacts: {of_data.get('name', 'Unknown')}")
            combined_data['name'] = of_data.get('name', '')
            combined_data['brand'] = of_data.get('brand', '')
            combined_data['category'] = of_data.get('category', '')
            combined_data['ingredients'] = of_data.get('ingredients', [])
            combined_data['nutrition'] = of_data.get('nutrition', {})
            combined_data['image_url'] = of_data.get('image_url')
            combined_data['sources'].append('OpenFoodFacts')
            combined_data['confidence_score'] += 40  # High confidence for ingredient data
        else:
            print("    [NOT FOUND] OpenFoodFacts")
        
        # Check UPCItemDB (secondary - good for basic product info)
        print("  Checking UPCItemDB...")
        upc_data = self._get_from_upcitemdb(upc_code)
        if upc_data:
            print(f"    [FOUND] UPCItemDB: {upc_data.get('name', 'Unknown')}")
            
            # Merge data, preferring OpenFoodFacts for ingredients but UPCItemDB for missing fields
            if not combined_data['name']:
                combined_data['name'] = upc_data.get('name', '')
            if not combined_data['brand']:
                combined_data['brand'] = upc_data.get('brand', '')
            if not combined_data['category']:
                combined_data['category'] = upc_data.get('category', '')
            if not combined_data['image_url']:
                combined_data['image_url'] = upc_data.get('image_url')
            
            combined_data['sources'].append('UPCItemDB')
            combined_data['confidence_score'] += 30  # Good confidence for basic info
        else:
            print("    [NOT FOUND] UPCItemDB")
        
        # Try BarcodeLookup if available (tertiary)
        print("  Checking BarcodeLookup...")
        barcode_data = self._get_from_barcodelookup(upc_code)
        if barcode_data:
            print(f"    [FOUND] BarcodeLookup: {barcode_data.get('name', 'Unknown')}")
            
            # Merge additional data
            if not combined_data['name']:
                combined_data['name'] = barcode_data.get('name', '')
            if not combined_data['brand']:
                combined_data['brand'] = barcode_data.get('brand', '')
            if not combined_data['category']:
                combined_data['category'] = barcode_data.get('category', '')
            if not combined_data['image_url']:
                combined_data['image_url'] = barcode_data.get('image_url')
            
            combined_data['sources'].append('BarcodeLookup')
            combined_data['confidence_score'] += 20
        else:
            print("    [NOT FOUND] BarcodeLookup")
        
        # Check if we found any data
        if combined_data['sources']:
            # Normalize confidence score
            combined_data['confidence_score'] = min(100, combined_data['confidence_score'])
            
            # Create source string
            combined_data['source'] = ', '.join(combined_data['sources'])
            
            print(f"  [SUCCESS] Product found in {len(combined_data['sources'])} database(s): {combined_data['source']}")
            print(f"    Confidence: {combined_data['confidence_score']}%")
            
            # Clean up the combined data for return
            return {
                'name': combined_data['name'],
                'brand': combined_data['brand'],
                'category': combined_data['category'],
                'ingredients': combined_data['ingredients'],
                'nutrition': combined_data['nutrition'],
                'image_url': combined_data['image_url'],
                'source': combined_data['source'],
                'confidence': combined_data['confidence_score'] / 100.0  # Convert to 0-1 scale
            }
        else:
            print(f"  [NOT FOUND] Product not found in any database")
            return None
    
    def _validate_upc(self, upc_code: str) -> bool:
        """Validate UPC code format and checksum for both UPC-A (12 digits) and EAN-13 (13 digits)"""
        if len(upc_code) not in [12, 13]:
            return False
        
        try:
            digits = [int(d) for d in upc_code]
            
            if len(upc_code) == 12:
                # UPC-A validation (12 digits)
                # Calculate checksum
                odd_sum = sum(digits[i] for i in range(0, 11, 2))
                even_sum = sum(digits[i] for i in range(1, 11, 2))
                total = odd_sum + (even_sum * 3)
                checksum = (10 - (total % 10)) % 10
                return digits[11] == checksum
                
            elif len(upc_code) == 13:
                # EAN-13 validation (13 digits)
                # Calculate checksum
                odd_sum = sum(digits[i] for i in range(0, 12, 2))
                even_sum = sum(digits[i] for i in range(1, 12, 2))
                total = odd_sum + (even_sum * 3)
                checksum = (10 - (total % 10)) % 10
                return digits[12] == checksum
            
            return False
            
        except (ValueError, IndexError):
            return False
    
    def _get_from_openfoodfacts(self, upc_code: str) -> Optional[Dict]:
        """Get product data from OpenFoodFacts API"""
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{upc_code}.json"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 1 and data.get('product'):
                    product = data['product']
                    
                    return {
                        'name': product.get('product_name', ''),
                        'brand': product.get('brands', ''),
                        'category': product.get('categories', ''),
                        'ingredients': product.get('ingredients_text', '').split(', ') if product.get('ingredients_text') else [],
                        'nutrition': product.get('nutriments', {}),
                        'image_url': product.get('image_url'),
                        'source': 'OpenFoodFacts'
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from OpenFoodFacts: {str(e)}")
            return None
    
    def _get_from_upcitemdb(self, upc_code: str) -> Optional[Dict]:
        """Get product data from UPCItemDB API"""
        try:
            url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={upc_code}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 'OK' and data.get('items'):
                    item = data['items'][0]
                    
                    # Extract better product information
                    title = item.get('title', '')
                    brand = item.get('brand', '')
                    
                    # Try to extract brand from title if not provided separately
                    if not brand and title:
                        # Common brand patterns
                        brand_patterns = ['Kraft', 'General Mills', 'Kellogg', 'Nestle', 'Hershey', 'Campbell', 'Heinz']
                        for pattern in brand_patterns:
                            if pattern.lower() in title.lower():
                                brand = pattern
                                break
                    
                    # Try to extract category from description or title
                    category = item.get('category', '')
                    if not category and title:
                        # Simple category detection based on keywords
                        title_lower = title.lower()
                        if any(word in title_lower for word in ['bread', 'cereal', 'pasta', 'flour']):
                            category = 'Grains & Flours'
                        elif any(word in title_lower for word in ['milk', 'cheese', 'yogurt', 'butter']):
                            category = 'Dairy'
                        elif any(word in title_lower for word in ['chicken', 'beef', 'pork', 'fish', 'meat']):
                            category = 'Proteins'
                        elif any(word in title_lower for word in ['apple', 'banana', 'orange', 'fruit']):
                            category = 'Fruits'
                        elif any(word in title_lower for word in ['carrot', 'lettuce', 'tomato', 'vegetable']):
                            category = 'Vegetables'
                        elif any(word in title_lower for word in ['candy', 'chocolate', 'cookie', 'snack']):
                            category = 'Snacks'
                        elif any(word in title_lower for word in ['soup', 'sauce', 'condiment']):
                            category = 'Condiments'
                        else:
                            category = 'Other'
                    
                    # Get the best image URL
                    image_url = None
                    if item.get('images'):
                        images = item['images']
                        # Prefer higher resolution images
                        if len(images) > 0:
                            image_url = images[0]
                    
                    return {
                        'name': title,
                        'brand': brand,
                        'category': category,
                        'ingredients': [],  # UPCItemDB doesn't provide ingredients
                        'nutrition': {},
                        'image_url': image_url,
                        'source': 'UPCItemDB',
                        'description': item.get('description', ''),
                        'model': item.get('model', ''),
                        'color': item.get('color', ''),
                        'size': item.get('size', '')
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from UPCItemDB: {str(e)}")
            return None
    
    def _get_from_barcodelookup(self, upc_code: str) -> Optional[Dict]:
        """Get product data from BarcodeLookup API (limited free tier)"""
        try:
            # Note: This is a placeholder for BarcodeLookup API
            # In a real implementation, you would need an API key
            url = f"https://api.barcodelookup.com/v2/products?barcode={upc_code}&formatted=y&key=YOUR_API_KEY"
            
            # For now, return None since we don't have an API key
            return None
            
        except Exception as e:
            print(f"Error fetching from BarcodeLookup: {str(e)}")
            return None
    
    def _analyze_gluten_safety(self, product_data: Dict) -> Dict[str, Any]:
        """Analyze product for gluten safety with enhanced multi-source analysis"""
        ingredients_text = ' '.join(product_data.get('ingredients', [])).lower()
        product_name = product_data.get('name', '').lower()
        product_category = product_data.get('category', '').lower()
        product_brand = product_data.get('brand', '').lower()
        
        # Combine all text for analysis
        all_text = f"{product_name} {product_brand} {product_category} {ingredients_text}"
        
        print(f"    Analyzing gluten safety for: {product_data.get('name', 'Unknown')}")
        print(f"    Sources: {product_data.get('source', 'Unknown')}")
        
        # Check for gluten-free certifications
        gf_certified = any(cert in all_text for cert in self.gf_certifications)
        if gf_certified:
            print(f"    [CERTIFIED] Found gluten-free certification indicators")
        
        # Check for gluten-containing ingredients
        gluten_ingredients_found = []
        for gluten_ing in self.gluten_ingredients:
            if gluten_ing in all_text:
                gluten_ingredients_found.append(gluten_ing)
        
        if gluten_ingredients_found:
            print(f"    [WARNING] Found potential gluten ingredients: {', '.join(gluten_ingredients_found)}")
        
        # Enhanced confidence calculation based on data sources
        base_confidence = 0.5
        data_confidence = product_data.get('confidence', 0.5)  # From database coverage
        
        # Adjust confidence based on ingredient data availability
        if ingredients_text.strip():
            base_confidence += 0.3  # High confidence with ingredient data
        elif product_name.strip():
            base_confidence += 0.1  # Medium confidence with product name only
        
        # Determine gluten-free status with enhanced logic
        if gf_certified and not gluten_ingredients_found:
            confidence = min(0.95, base_confidence + data_confidence * 0.2)
            print(f"    [SAFE] Product appears gluten-free (confidence: {confidence:.1%})")
            return {
                'is_gluten_free': True,
                'warning': None,
                'confidence': confidence
            }
        elif gf_certified and gluten_ingredients_found:
            confidence = min(0.9, base_confidence + data_confidence * 0.1)
            print(f"    [CONFLICT] Conflicting information detected (confidence: {confidence:.1%})")
            return {
                'is_gluten_free': False,
                'warning': f"Contains gluten ingredients: {', '.join(gluten_ingredients_found)} despite gluten-free claims",
                'confidence': confidence
            }
        elif gluten_ingredients_found:
            confidence = min(0.95, base_confidence + data_confidence * 0.2)
            print(f"    [UNSAFE] Product contains gluten (confidence: {confidence:.1%})")
            return {
                'is_gluten_free': False,
                'warning': f"Contains gluten ingredients: {', '.join(gluten_ingredients_found)}",
                'confidence': confidence
            }
        elif ingredients_text.strip():
            # Has ingredients but no gluten found - could be safe
            confidence = min(0.8, base_confidence + data_confidence * 0.15)
            print(f"    [LIKELY SAFE] No gluten detected in ingredients (confidence: {confidence:.1%})")
            return {
                'is_gluten_free': True,
                'warning': "No gluten ingredients detected, but verify gluten-free certification",
                'confidence': confidence
            }
        else:
            # No ingredient information available
            confidence = min(0.4, base_confidence * 0.8)
            print(f"    [UNKNOWN] Unable to determine gluten status (confidence: {confidence:.1%})")
            return {
                'is_gluten_free': None,  # Unknown
                'warning': "Unable to determine gluten-free status - no ingredient information available from any database",
                'confidence': confidence
            }
    
    def get_gluten_free_alternatives(self, product_info: ProductInfo) -> List[Dict[str, str]]:
        """Suggest gluten-free alternatives for non-GF products"""
        alternatives = []
        
        # Common gluten-free alternatives
        alternatives_db = {
            'bread': [
                {'name': 'Gluten-Free Bread', 'brand': 'Udi\'s', 'notes': 'Soft and similar to regular bread'},
                {'name': 'Gluten-Free Bread', 'brand': 'Canyon Bakehouse', 'notes': 'Great for sandwiches'},
                {'name': 'Gluten-Free Bread', 'brand': 'Schar', 'notes': 'European-style gluten-free bread'}
            ],
            'pasta': [
                {'name': 'Gluten-Free Pasta', 'brand': 'Barilla', 'notes': 'Rice and corn blend'},
                {'name': 'Gluten-Free Pasta', 'brand': 'Jovial', 'notes': 'Brown rice pasta'},
                {'name': 'Gluten-Free Pasta', 'brand': 'Banza', 'notes': 'Chickpea pasta, high protein'}
            ],
            'flour': [
                {'name': 'Gluten-Free All-Purpose Flour', 'brand': 'King Arthur', 'notes': 'Cup-for-cup replacement'},
                {'name': 'Gluten-Free Flour', 'brand': 'Bob\'s Red Mill', 'notes': '1:1 baking flour'},
                {'name': 'Gluten-Free Flour', 'brand': 'Cup4Cup', 'notes': 'Professional-grade flour blend'}
            ]
        }
        
        # Find alternatives based on product category or name
        product_name_lower = product_info.name.lower()
        for category, alt_list in alternatives_db.items():
            if category in product_name_lower or category in product_info.category.lower():
                alternatives.extend(alt_list)
        
        return alternatives
    
    def _get_detailed_nutrition(self, product_data: Dict) -> Optional[NutritionData]:
        """Get detailed nutrition analysis for product"""
        try:
            # Create mock ingredient for nutrition analysis
            mock_ingredient = {
                'name': product_data.get('name', ''),
                'quantity': 100  # Per 100g serving
            }
            
            # Get nutrition data
            nutrition_data = nutrition_analyzer.get_ingredient_nutrition(mock_ingredient)
            
            # Enhance with product-specific data if available
            product_nutrition = product_data.get('nutrition', {})
            if product_nutrition:
                # Override with actual product data where available
                if 'calories' in product_nutrition:
                    nutrition_data.calories = float(product_nutrition['calories'])
                if 'protein' in product_nutrition:
                    nutrition_data.protein_g = float(product_nutrition['protein'])
                if 'carbs' in product_nutrition:
                    nutrition_data.carbs_g = float(product_nutrition['carbs'])
                if 'fiber' in product_nutrition:
                    nutrition_data.fiber_g = float(product_nutrition['fiber'])
                if 'fat' in product_nutrition:
                    nutrition_data.fat_g = float(product_nutrition['fat'])
                if 'sodium' in product_nutrition:
                    nutrition_data.sodium_mg = float(product_nutrition['sodium'])
            
            return nutrition_data
            
        except Exception as e:
            print(f"Error getting detailed nutrition: {e}")
            return None


# Convenience functions for easy importing
def scan_upc_code(upc_code: str) -> Optional[ProductInfo]:
    """Scan a UPC code and return product information"""
    scanner = UPCScanner()
    return scanner.scan_upc(upc_code)


def check_gluten_safety(product_info: ProductInfo) -> Dict[str, Any]:
    """Check gluten safety of a product"""
    scanner = UPCScanner()
    return scanner._analyze_gluten_safety({
        'name': product_info.name,
        'ingredients': product_info.ingredients,
        'category': product_info.category
    })


# Global instance for convenience
upc_scanner = UPCScanner()