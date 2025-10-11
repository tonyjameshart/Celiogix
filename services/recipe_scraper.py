# path: services/recipe_scraper.py
"""
Recipe Scraper Service for CeliacShield

Provides web scraping functionality for importing recipes from various gluten-free websites.
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse


class RecipeScraper:
    """Main recipe scraper class"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Known gluten-free recipe sites and their parsing rules
        self.site_rules = {
            'mamaknowsglutenfree.com': {
                'title': ['h1.entry-title', 'h1', '.recipe-title'],
                'ingredients': ['.wprm-recipe-ingredient', '.ingredient', '.recipe-ingredient'],
                'instructions': ['.wprm-recipe-instruction', '.instruction', '.recipe-instruction'],
                'prep_time': ['.wprm-recipe-prep-time', '.prep-time', '.recipe-prep-time'],
                'cook_time': ['.wprm-recipe-cook-time', '.cook-time', '.recipe-cook-time'],
                'servings': ['.wprm-recipe-servings', '.servings', '.recipe-servings'],
                'description': ['.entry-content p', '.recipe-description', '.description']
            },
            'justlovecooking.com': {
                'title': ['h1.entry-title', 'h1', '.recipe-title'],
                'ingredients': ['.wprm-recipe-ingredient', '.ingredient', '.recipe-ingredient'],
                'instructions': ['.wprm-recipe-instruction', '.instruction', '.recipe-instruction'],
                'prep_time': ['.wprm-recipe-prep-time', '.prep-time', '.recipe-prep-time'],
                'cook_time': ['.wprm-recipe-cook-time', '.cook-time', '.recipe-cook-time'],
                'servings': ['.wprm-recipe-servings', '.servings', '.recipe-servings'],
                'description': ['.entry-content p', '.recipe-description', '.description']
            },
            'glutenfreegoddess.com': {
                'title': ['h1.entry-title', 'h1', '.recipe-title'],
                'ingredients': ['.wprm-recipe-ingredient', '.ingredient', '.recipe-ingredient'],
                'instructions': ['.wprm-recipe-instruction', '.instruction', '.recipe-instruction'],
                'prep_time': ['.wprm-recipe-prep-time', '.prep-time', '.recipe-prep-time'],
                'cook_time': ['.wprm-recipe-cook-time', '.cook-time', '.recipe-cook-time'],
                'servings': ['.wprm-recipe-servings', '.servings', '.recipe-servings'],
                'description': ['.entry-content p', '.recipe-description', '.description']
            },
            'simplygluten-free.com': {
                'title': ['h1.entry-title', 'h1', '.recipe-title'],
                'ingredients': ['.wprm-recipe-ingredient', '.ingredient', '.recipe-ingredient'],
                'instructions': ['.wprm-recipe-instruction', '.instruction', '.recipe-instruction'],
                'prep_time': ['.wprm-recipe-prep-time', '.prep-time', '.recipe-prep-time'],
                'cook_time': ['.wprm-recipe-cook-time', '.cook-time', '.recipe-cook-time'],
                'servings': ['.wprm-recipe-servings', '.servings', '.recipe-servings'],
                'description': ['.entry-content p', '.recipe-description', '.description']
            }
        }
    
    def scrape_recipe_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single recipe from a URL"""
        try:
            # Get the webpage
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Determine the site and get parsing rules
            domain = urlparse(url).netloc.lower()
            site_rules = self._get_site_rules(domain)
            
            # Extract recipe data
            recipe_data = self._extract_recipe_data(soup, site_rules)
            
            if recipe_data and recipe_data.get('name'):
                # Add metadata
                recipe_data['source_url'] = url
                recipe_data['scraped_at'] = self._get_current_timestamp()
                
                # Validate and clean the data
                recipe_data = self._validate_and_clean_recipe(recipe_data)
                
                return recipe_data
            else:
                return None
                
        except Exception as e:
            print(f"Error scraping recipe from {url}: {str(e)}")
            return None
    
    def scrape_recipes_from_url(self, url: str) -> List[Dict[str, Any]]:
        """Scrape multiple recipes from a URL (recipe listing page)"""
        try:
            # Get the webpage
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find recipe links
            recipe_links = self._find_recipe_links(soup, url)
            
            recipes = []
            for link in recipe_links[:10]:  # Limit to 10 recipes to avoid overwhelming
                recipe_data = self.scrape_recipe_from_url(link)
                if recipe_data:
                    recipes.append(recipe_data)
            
            return recipes
            
        except Exception as e:
            print(f"Error scraping recipes from {url}: {str(e)}")
            return []
    
    def _get_site_rules(self, domain: str) -> Dict[str, List[str]]:
        """Get parsing rules for a specific domain"""
        # Check for exact match first
        if domain in self.site_rules:
            return self.site_rules[domain]
        
        # Check for partial matches
        for site, rules in self.site_rules.items():
            if site in domain or domain in site:
                return rules
        
        # Return generic rules
        return {
            'title': ['h1', '.recipe-title', '.entry-title', 'title'],
            'ingredients': ['.ingredient', '.recipe-ingredient', '[class*="ingredient"]'],
            'instructions': ['.instruction', '.recipe-instruction', '[class*="instruction"]'],
            'prep_time': ['.prep-time', '.recipe-prep-time', '[class*="prep"]'],
            'cook_time': ['.cook-time', '.recipe-cook-time', '[class*="cook"]'],
            'servings': ['.servings', '.recipe-servings', '[class*="serving"]'],
            'description': ['.recipe-description', '.description', '.entry-content p']
        }
    
    def _extract_recipe_data(self, soup: BeautifulSoup, rules: Dict[str, List[str]]) -> Dict[str, Any]:
        """Extract recipe data using the provided rules"""
        recipe_data = {}
        
        # Extract title
        recipe_data['name'] = self._extract_text_by_selectors(soup, rules.get('title', []))
        
        # Extract description
        recipe_data['description'] = self._extract_text_by_selectors(soup, rules.get('description', []))
        
        # Extract ingredients
        ingredients = self._extract_ingredients(soup, rules.get('ingredients', []))
        recipe_data['ingredients'] = ingredients
        
        # Extract instructions
        instructions = self._extract_instructions(soup, rules.get('instructions', []))
        recipe_data['instructions'] = instructions
        
        # Extract timing information
        prep_time = self._extract_text_by_selectors(soup, rules.get('prep_time', []))
        cook_time = self._extract_text_by_selectors(soup, rules.get('cook_time', []))
        
        recipe_data['prep_time'] = self._parse_time(prep_time)
        recipe_data['cook_time'] = self._parse_time(cook_time)
        
        # Calculate total time
        total_time = self._calculate_total_time(recipe_data['prep_time'], recipe_data['cook_time'])
        recipe_data['total_time'] = total_time
        
        # Extract servings
        servings = self._extract_text_by_selectors(soup, rules.get('servings', []))
        recipe_data['servings'] = self._parse_servings(servings)
        
        # Set defaults
        recipe_data['category'] = self._determine_category(recipe_data.get('name', ''))
        recipe_data['difficulty'] = self._determine_difficulty(ingredients, instructions)
        recipe_data['notes'] = ''
        
        return recipe_data
    
    def _extract_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """Extract text using a list of CSS selectors"""
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text:
                    return text
        return ''
    
    def _extract_ingredients(self, soup: BeautifulSoup, selectors: List[str]) -> List[Dict[str, str]]:
        """Extract ingredients list"""
        ingredients = []
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text:
                    # Parse ingredient text
                    parsed_ingredient = self._parse_ingredient_text(text)
                    if parsed_ingredient:
                        ingredients.append(parsed_ingredient)
            
            if ingredients:  # If we found ingredients with this selector, use them
                break
        
        return ingredients
    
    def _extract_instructions(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """Extract cooking instructions"""
        instructions = []
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text:
                    instructions.append(text)
            
            if instructions:  # If we found instructions with this selector, use them
                break
        
        return '\n'.join(instructions)
    
    def _parse_ingredient_text(self, text: str) -> Dict[str, str]:
        """Parse ingredient text into structured format with enhanced parsing"""
        # Remove common prefixes
        text = re.sub(r'^[•\-\*\d+\.\)]\s*', '', text)
        text = text.strip()
        
        if not text:
            return None
        
        # Enhanced ingredient parsing (handles Unicode conversion internally)
        parsed = self._parse_ingredient_with_units(text)
        if parsed:
            return parsed
        
        # Fallback: just ingredient name
        return {
            'name': text,
            'amount': '',
            'unit': ''
        }
    
    def _parse_ingredient_with_units(self, text: str) -> Dict[str, str]:
        """Enhanced ingredient parser that handles complex formats"""
        import re
        
        # Unicode fraction mapping
        unicode_fractions = {
            '½': '1/2',
            '¼': '1/4', 
            '¾': '3/4',
            '⅓': '1/3',
            '⅔': '2/3',
            '⅛': '1/8',
            '⅜': '3/8',
            '⅝': '5/8',
            '⅞': '7/8'
        }
        
        # Comprehensive list of measurement units and their variations
        units = [
            # Volume (ordered by length to match longer patterns first)
            'fluid ounces', 'fluid ounce',
            'tablespoons', 'tablespoon',
            'teaspoons', 'teaspoon',
            'milliliters', 'milliliter',
            'fl oz', 'fl. oz.',
            'tbsp', 'tbsp.', 'tbs', 'tbs.',
            'tsp', 'tsp.', 'ts', 'ts.',
            'ml', 'ml.',
            'cup', 'cups', 'c', 'c.',
            'pint', 'pints', 'pt', 'pt.',
            'quart', 'quarts', 'qt', 'qt.',
            'gallon', 'gallons', 'gal', 'gal.',
            'liter', 'liters', 'l', 'l.',
            
            # Weight
            'pounds', 'pound',
            'ounces', 'ounce',
            'kilograms', 'kilogram',
            'lbs', 'lbs.',
            'lb', 'lb.',
            'oz', 'oz.',
            'kg', 'kg.',
            'grams', 'gram',
            'g', 'g.',
            
            # Count/Size
            'pieces', 'piece',
            'slices', 'slice',
            'cloves', 'clove',
            'heads', 'head',
            'bunches', 'bunch',
            'cans', 'can',
            'packages', 'package',
            'bags', 'bag',
            'bottles', 'bottle',
            'jars', 'jar',
            'boxes', 'box',
            'pc', 'pc.',
            'pkg', 'pkg.',
            
            # Size descriptors
            'extra large', 'xl',
            'large', 'medium', 'small',
            'whole', 'half', 'quarter',
            'diced', 'chopped', 'sliced', 'minced', 'grated',
            'fresh', 'dried', 'frozen', 'canned'
        ]
        
        # Step 1a: Try to match mixed Unicode fractions first (e.g., "2½ cups flour")
        mixed_unicode_pattern = r'^(\d+)([\u00BD\u00BC\u00BE\u2153\u2154\u215B\u215C\u215D\u215E])\s+([a-zA-Z]+)\s+(.+)$'
        match = re.match(mixed_unicode_pattern, text, re.IGNORECASE)
        if match:
            whole_number = match.group(1)
            unicode_fraction = match.group(2)
            potential_unit = match.group(3).strip()
            ingredient_name = match.group(4).strip()
            
            # Convert Unicode fraction to ASCII
            ascii_fraction = unicode_fractions.get(unicode_fraction, unicode_fraction)
            
            # Check if the potential unit is in our units list
            for unit in units:
                if potential_unit.lower() == unit.lower():
                    return {
                        'name': ingredient_name,
                        'amount': f"{whole_number} {ascii_fraction}",
                        'unit': unit
                    }
        
        # Step 1b: Try to match mixed numbers (e.g., "2 1/2 cups flour")
        mixed_pattern = r'^(\d+)\s+(\d+\/\d+)\s+([a-zA-Z]+)\s+(.+)$'
        match = re.match(mixed_pattern, text, re.IGNORECASE)
        if match:
            whole_number = match.group(1)
            fraction = match.group(2)
            potential_unit = match.group(3).strip()
            ingredient_name = match.group(4).strip()
            
            # Check if the potential unit is in our units list
            for unit in units:
                if potential_unit.lower() == unit.lower():
                    return {
                        'name': ingredient_name,
                        'amount': f"{whole_number} {fraction}",
                        'unit': unit
                    }
        
        # Convert remaining Unicode fractions to ASCII equivalents
        for unicode_char, ascii_equiv in unicode_fractions.items():
            text = text.replace(unicode_char, ascii_equiv)
        
        # Step 2: Try simple fractions (e.g., "1/2 cup flour")
        simple_fraction_pattern = r'^(\d+\/\d+)\s+([a-zA-Z]+)\s+(.+)$'
        match = re.match(simple_fraction_pattern, text, re.IGNORECASE)
        if match:
            amount = match.group(1)
            potential_unit = match.group(2).strip()
            ingredient_name = match.group(3).strip()
            
            # Check if the potential unit is in our units list
            for unit in units:
                if potential_unit.lower() == unit.lower():
                    return {
                        'name': ingredient_name,
                        'amount': amount,
                        'unit': unit
                    }
        
        # Step 3: Try decimal amounts (e.g., "2.5 cups flour")
        decimal_pattern = r'^(\d+\.\d+)\s+([a-zA-Z]+)\s+(.+)$'
        match = re.match(decimal_pattern, text, re.IGNORECASE)
        if match:
            amount = match.group(1)
            potential_unit = match.group(2).strip()
            ingredient_name = match.group(3).strip()
            
            # Check if the potential unit is in our units list
            for unit in units:
                if potential_unit.lower() == unit.lower():
                    return {
                        'name': ingredient_name,
                        'amount': amount,
                        'unit': unit
                    }
        
        # Step 4: Try whole numbers (e.g., "2 cups flour")
        whole_number_pattern = r'^(\d+)\s+([a-zA-Z]+)\s+(.+)$'
        match = re.match(whole_number_pattern, text, re.IGNORECASE)
        if match:
            amount = match.group(1)
            potential_unit = match.group(2).strip()
            ingredient_name = match.group(3).strip()
            
            # Check if the potential unit is in our units list
            for unit in units:
                if potential_unit.lower() == unit.lower():
                    return {
                        'name': ingredient_name,
                        'amount': amount,
                        'unit': unit
                    }
        
        # Step 5: Try without unit (e.g., "2 eggs")
        no_unit_pattern = r'^(\d+(?:\.\d+)?(?:\/\d+)?)\s+(.+)$'
        match = re.match(no_unit_pattern, text)
        if match:
            amount = match.group(1).strip()
            ingredient_name = match.group(2).strip()
            
            return {
                'name': ingredient_name,
                'amount': amount,
                'unit': ''
            }
        
        return None
    
    def test_ingredient_parsing(self):
        """Test method for ingredient parsing - can be called for debugging"""
        test_cases = [
            "2 1/2 cups masa harina",
            "2 1/4 cups warm water", 
            "1 1/4 tsp salt",
            "1 cup shredded mozzarella",
            "2 tablespoons olive oil",
            "1/2 teaspoon vanilla extract",
            "1 large onion, diced",
            "3 cloves garlic, minced",
            "1 lb ground beef",
            "12 oz pasta",
            "1 can diced tomatoes",
            "2 eggs",
            "1/4 cup fresh basil",
            "2 1/2 cups all-purpose flour",
            "1/2 cup butter",
            "3 tsp baking powder",
            "1/4 lb cheese",
            # Unicode fraction tests
            "½ cup sugar",
            "¼ teaspoon salt",
            "¾ cup flour",
            "2½ cups water",
            "1¼ tsp vanilla"
        ]
        
        print("Testing ingredient parsing:")
        for test_case in test_cases:
            result = self._parse_ingredient_text(test_case)
            print(f"'{test_case}' -> {result}")
    
    def _parse_time(self, time_text: str) -> str:
        """Parse time text and return standardized format"""
        if not time_text:
            return ''
        
        # Extract numbers and units
        time_match = re.search(r'(\d+)\s*(?:min|minute|minutes|hour|hours|hr|hrs)', time_text.lower())
        if time_match:
            number = int(time_match.group(1))
            unit = time_match.group(0).split(str(number))[1].strip()
            
            if 'hour' in unit or 'hr' in unit:
                return f"{number} hour{'s' if number > 1 else ''}"
            else:
                return f"{number} min"
        
        return time_text.strip()
    
    def _calculate_total_time(self, prep_time: str, cook_time: str) -> str:
        """Calculate total cooking time"""
        prep_minutes = self._time_to_minutes(prep_time)
        cook_minutes = self._time_to_minutes(cook_time)
        
        total_minutes = prep_minutes + cook_minutes
        
        if total_minutes == 0:
            return ''
        
        if total_minutes >= 60:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if minutes > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{total_minutes} min"
    
    def _time_to_minutes(self, time_text: str) -> int:
        """Convert time text to minutes"""
        if not time_text:
            return 0
        
        # Extract numbers
        numbers = re.findall(r'\d+', time_text)
        if not numbers:
            return 0
        
        minutes = 0
        if 'hour' in time_text.lower() or 'hr' in time_text.lower():
            minutes += int(numbers[0]) * 60
            if len(numbers) > 1:
                minutes += int(numbers[1])
        else:
            minutes = int(numbers[0])
        
        return minutes
    
    def _parse_servings(self, servings_text: str) -> int:
        """Parse servings text to integer"""
        if not servings_text:
            return 4  # Default
        
        # Extract numbers
        numbers = re.findall(r'\d+', servings_text)
        if numbers:
            return int(numbers[0])
        
        return 4
    
    def _determine_category(self, recipe_name: str) -> str:
        """Determine recipe category based on name"""
        name_lower = recipe_name.lower()
        
        if any(word in name_lower for word in ['pancake', 'waffle', 'muffin', 'breakfast', 'cereal', 'oatmeal']):
            return 'Breakfast'
        elif any(word in name_lower for word in ['salad', 'sandwich', 'wrap', 'lunch', 'soup']):
            return 'Lunch'
        elif any(word in name_lower for word in ['dinner', 'main', 'chicken', 'beef', 'pasta', 'rice']):
            return 'Dinner'
        elif any(word in name_lower for word in ['cookie', 'cake', 'pie', 'dessert', 'sweet', 'chocolate']):
            return 'Dessert'
        elif any(word in name_lower for word in ['snack', 'trail', 'mix', 'bar', 'cracker']):
            return 'Snack'
        else:
            return 'Other'
    
    def _determine_difficulty(self, ingredients: List[Dict], instructions: str) -> str:
        """Determine recipe difficulty based on ingredients and instructions"""
        ingredient_count = len(ingredients)
        instruction_length = len(instructions.split('\n'))
        
        if ingredient_count <= 5 and instruction_length <= 3:
            return 'Easy'
        elif ingredient_count <= 10 and instruction_length <= 8:
            return 'Medium'
        else:
            return 'Hard'
    
    def _find_recipe_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find recipe links on a listing page"""
        links = []
        
        # Common selectors for recipe links
        selectors = [
            'a[href*="recipe"]',
            'a[href*="post"]',
            '.recipe-title a',
            '.entry-title a',
            'h2 a',
            'h3 a'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    # Convert relative URLs to absolute
                    full_url = urljoin(base_url, href)
                    if full_url not in links:
                        links.append(full_url)
        
        return links
    
    def _validate_and_clean_recipe(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean scraped recipe data"""
        # Ensure required fields
        if not recipe_data.get('name'):
            return None
        
        # Clean and validate ingredients
        ingredients = recipe_data.get('ingredients', [])
        cleaned_ingredients = []
        for ingredient in ingredients:
            if isinstance(ingredient, dict) and ingredient.get('name'):
                cleaned_ingredients.append(ingredient)
        
        recipe_data['ingredients'] = cleaned_ingredients
        
        # Ensure we have at least some ingredients and instructions
        if not cleaned_ingredients or not recipe_data.get('instructions'):
            return None
        
        return recipe_data
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Convenience functions for easy importing
def scrape_recipe_from_url(url: str) -> Optional[Dict[str, Any]]:
    """Scrape a single recipe from a URL"""
    scraper = RecipeScraper()
    return scraper.scrape_recipe_from_url(url)


def scrape_recipes_from_url(url: str) -> List[Dict[str, Any]]:
    """Scrape multiple recipes from a URL"""
    scraper = RecipeScraper()
    return scraper.scrape_recipes_from_url(url)


# Global instance for convenience
recipe_scraper = RecipeScraper()


def check_scraper_dependencies():
    """Check if all required dependencies for recipe scraping are available"""
    missing_deps = []
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        import bs4
    except ImportError:
        missing_deps.append("beautifulsoup4")
    
    return missing_deps


def is_scraper_available():
    """Check if recipe scraper is fully functional"""
    return len(check_scraper_dependencies()) == 0