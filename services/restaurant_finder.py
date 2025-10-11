# path: services/restaurant_finder.py
"""
Location-based Restaurant Finder Service for CeliacShield

Finds gluten-free restaurants based on location with safety ratings.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import requests
import json
import math


@dataclass
class RestaurantInfo:
    """Restaurant information with gluten-free details"""
    name: str
    address: str
    latitude: float
    longitude: float
    distance_km: float
    phone: Optional[str] = None
    website: Optional[str] = None
    cuisine_type: str = "Unknown"
    price_range: str = "$"
    rating: float = 0.0
    gluten_free_menu: bool = False
    dedicated_fryer: bool = False
    staff_training: str = "Unknown"
    celiac_friendly_score: int = 0
    user_reviews: List[str] = None
    verified_safe: bool = False


class RestaurantFinder:
    """Location-based restaurant finder with gluten-free focus"""
    
    def __init__(self):
        # In production, use actual API keys
        self.google_places_api_key = "YOUR_GOOGLE_PLACES_API_KEY"
        self.yelp_api_key = "YOUR_YELP_API_KEY"
        
        # Gluten-free restaurant chains database
        self.trusted_chains = {
            "chipotle": {"score": 85, "notes": "Good GF protocols, dedicated prep area"},
            "five guys": {"score": 90, "notes": "Dedicated GF buns, excellent protocols"},
            "in-n-out": {"score": 80, "notes": "Protein style available, clean prep"},
            "pf changs": {"score": 95, "notes": "Extensive GF menu, excellent training"},
            "outback steakhouse": {"score": 85, "notes": "GF menu available, good protocols"},
            "red robin": {"score": 80, "notes": "GF buns available, separate prep"},
            "olive garden": {"score": 75, "notes": "GF pasta available, cross-contamination risk"}
        }
        
        # Cuisine safety ratings
        self.cuisine_safety = {
            "american": 80,
            "mexican": 70,
            "italian": 60,  # High pasta/bread risk
            "asian": 50,    # Soy sauce risk
            "indian": 75,
            "mediterranean": 85,
            "seafood": 90,
            "steakhouse": 85
        }
    
    def find_nearby_restaurants(self, latitude: float, longitude: float, 
                              radius_km: float = 10) -> List[RestaurantInfo]:
        """Find gluten-free friendly restaurants near location"""
        restaurants = []
        
        # Try multiple data sources
        google_results = self._search_google_places(latitude, longitude, radius_km)
        yelp_results = self._search_yelp(latitude, longitude, radius_km)
        builtin_results = self._search_builtin_database(latitude, longitude, radius_km)
        
        # Combine and deduplicate results
        all_results = google_results + yelp_results + builtin_results
        restaurants = self._deduplicate_restaurants(all_results)
        
        # Sort by celiac safety score and distance
        restaurants.sort(key=lambda r: (r.celiac_friendly_score, -r.distance_km), reverse=True)
        
        return restaurants[:20]  # Return top 20 results
    
    def _search_google_places(self, lat: float, lng: float, radius_km: float) -> List[RestaurantInfo]:
        """Search Google Places API for restaurants"""
        try:
            # Convert km to meters for Google API
            radius_m = int(radius_km * 1000)
            
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': radius_m,
                'type': 'restaurant',
                'keyword': 'gluten free',
                'key': self.google_places_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            
            data = response.json()
            restaurants = []
            
            for place in data.get('results', []):
                restaurant = self._parse_google_place(place, lat, lng)
                if restaurant:
                    restaurants.append(restaurant)
            
            return restaurants
            
        except Exception as e:
            print(f"Google Places API error: {e}")
            return []
    
    def _search_yelp(self, lat: float, lng: float, radius_km: float) -> List[RestaurantInfo]:
        """Search Yelp API for restaurants"""
        try:
            url = "https://api.yelp.com/v3/businesses/search"
            headers = {'Authorization': f'Bearer {self.yelp_api_key}'}
            params = {
                'latitude': lat,
                'longitude': lng,
                'radius': int(radius_km * 1000),
                'categories': 'restaurants',
                'term': 'gluten free',
                'limit': 20
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code != 200:
                return []
            
            data = response.json()
            restaurants = []
            
            for business in data.get('businesses', []):
                restaurant = self._parse_yelp_business(business, lat, lng)
                if restaurant:
                    restaurants.append(restaurant)
            
            return restaurants
            
        except Exception as e:
            print(f"Yelp API error: {e}")
            return []
    
    def _search_builtin_database(self, lat: float, lng: float, radius_km: float) -> List[RestaurantInfo]:
        """Search built-in restaurant database"""
        # Sample restaurants for demonstration
        sample_restaurants = [
            {
                'name': 'Gluten-Free Bistro',
                'address': '123 Safe Street, Anytown',
                'lat': lat + 0.01,
                'lng': lng + 0.01,
                'cuisine': 'american',
                'rating': 4.5,
                'gluten_free_menu': True,
                'dedicated_fryer': True,
                'staff_training': 'excellent'
            },
            {
                'name': 'Celiac Safe Kitchen',
                'address': '456 Health Ave, Anytown',
                'lat': lat - 0.005,
                'lng': lng + 0.005,
                'cuisine': 'mediterranean',
                'rating': 4.8,
                'gluten_free_menu': True,
                'dedicated_fryer': True,
                'staff_training': 'excellent'
            },
            {
                'name': 'Farm Fresh Cafe',
                'address': '789 Organic Blvd, Anytown',
                'lat': lat + 0.008,
                'lng': lng - 0.003,
                'cuisine': 'american',
                'rating': 4.2,
                'gluten_free_menu': True,
                'dedicated_fryer': False,
                'staff_training': 'good'
            }
        ]
        
        restaurants = []
        for restaurant_data in sample_restaurants:
            distance = self._calculate_distance(lat, lng, restaurant_data['lat'], restaurant_data['lng'])
            if distance <= radius_km:
                restaurant = RestaurantInfo(
                    name=restaurant_data['name'],
                    address=restaurant_data['address'],
                    latitude=restaurant_data['lat'],
                    longitude=restaurant_data['lng'],
                    distance_km=distance,
                    cuisine_type=restaurant_data['cuisine'],
                    rating=restaurant_data['rating'],
                    gluten_free_menu=restaurant_data['gluten_free_menu'],
                    dedicated_fryer=restaurant_data['dedicated_fryer'],
                    staff_training=restaurant_data['staff_training'],
                    celiac_friendly_score=self._calculate_safety_score(restaurant_data),
                    verified_safe=True
                )
                restaurants.append(restaurant)
        
        return restaurants
    
    def _parse_google_place(self, place: Dict, user_lat: float, user_lng: float) -> Optional[RestaurantInfo]:
        """Parse Google Places result"""
        try:
            location = place.get('geometry', {}).get('location', {})
            lat = location.get('lat', 0)
            lng = location.get('lng', 0)
            
            distance = self._calculate_distance(user_lat, user_lng, lat, lng)
            
            # Determine cuisine type from place types
            cuisine = "american"
            place_types = place.get('types', [])
            if 'italian_restaurant' in place_types:
                cuisine = "italian"
            elif 'mexican_restaurant' in place_types:
                cuisine = "mexican"
            elif 'chinese_restaurant' in place_types or 'japanese_restaurant' in place_types:
                cuisine = "asian"
            
            restaurant = RestaurantInfo(
                name=place.get('name', 'Unknown'),
                address=place.get('vicinity', ''),
                latitude=lat,
                longitude=lng,
                distance_km=distance,
                cuisine_type=cuisine,
                rating=place.get('rating', 0),
                price_range='$' * place.get('price_level', 1),
                celiac_friendly_score=self._estimate_safety_score(place, cuisine)
            )
            
            return restaurant
            
        except Exception as e:
            print(f"Error parsing Google place: {e}")
            return None
    
    def _parse_yelp_business(self, business: Dict, user_lat: float, user_lng: float) -> Optional[RestaurantInfo]:
        """Parse Yelp business result"""
        try:
            coordinates = business.get('coordinates', {})
            lat = coordinates.get('latitude', 0)
            lng = coordinates.get('longitude', 0)
            
            distance = self._calculate_distance(user_lat, user_lng, lat, lng)
            
            # Extract cuisine from categories
            cuisine = "american"
            categories = business.get('categories', [])
            for category in categories:
                alias = category.get('alias', '').lower()
                if 'italian' in alias:
                    cuisine = "italian"
                elif 'mexican' in alias:
                    cuisine = "mexican"
                elif 'chinese' in alias or 'japanese' in alias or 'asian' in alias:
                    cuisine = "asian"
                elif 'mediterranean' in alias:
                    cuisine = "mediterranean"
                elif 'indian' in alias:
                    cuisine = "indian"
                break
            
            restaurant = RestaurantInfo(
                name=business.get('name', 'Unknown'),
                address=business.get('location', {}).get('display_address', [''])[0],
                latitude=lat,
                longitude=lng,
                distance_km=distance,
                phone=business.get('phone'),
                website=business.get('url'),
                cuisine_type=cuisine,
                rating=business.get('rating', 0),
                price_range=business.get('price', '$'),
                celiac_friendly_score=self._estimate_safety_score(business, cuisine)
            )
            
            return restaurant
            
        except Exception as e:
            print(f"Error parsing Yelp business: {e}")
            return None
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlng / 2) * math.sin(dlng / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return round(distance, 2)
    
    def _calculate_safety_score(self, restaurant_data: Dict) -> int:
        """Calculate celiac safety score for restaurant"""
        score = 50  # Base score
        
        # Gluten-free menu bonus
        if restaurant_data.get('gluten_free_menu'):
            score += 25
        
        # Dedicated fryer bonus
        if restaurant_data.get('dedicated_fryer'):
            score += 15
        
        # Staff training bonus
        training = restaurant_data.get('staff_training', 'unknown').lower()
        if training == 'excellent':
            score += 20
        elif training == 'good':
            score += 10
        elif training == 'basic':
            score += 5
        
        # Cuisine type adjustment
        cuisine = restaurant_data.get('cuisine', 'american').lower()
        cuisine_score = self.cuisine_safety.get(cuisine, 70)
        score = int(score * (cuisine_score / 100))
        
        # Rating bonus
        rating = restaurant_data.get('rating', 0)
        if rating >= 4.5:
            score += 10
        elif rating >= 4.0:
            score += 5
        
        return min(100, max(0, score))
    
    def _estimate_safety_score(self, place_data: Dict, cuisine: str) -> int:
        """Estimate safety score from limited data"""
        score = 40  # Lower base for unverified
        
        # Check if it's a trusted chain
        name = place_data.get('name', '').lower()
        for chain, chain_info in self.trusted_chains.items():
            if chain in name:
                return chain_info['score']
        
        # Cuisine adjustment
        cuisine_score = self.cuisine_safety.get(cuisine, 70)
        score = int(score * (cuisine_score / 100))
        
        # Rating bonus
        rating = place_data.get('rating', 0)
        if rating >= 4.5:
            score += 15
        elif rating >= 4.0:
            score += 10
        elif rating >= 3.5:
            score += 5
        
        return min(100, max(0, score))
    
    def _deduplicate_restaurants(self, restaurants: List[RestaurantInfo]) -> List[RestaurantInfo]:
        """Remove duplicate restaurants from combined results"""
        seen = set()
        unique_restaurants = []
        
        for restaurant in restaurants:
            # Create a key based on name and approximate location
            key = (
                restaurant.name.lower().strip(),
                round(restaurant.latitude, 3),
                round(restaurant.longitude, 3)
            )
            
            if key not in seen:
                seen.add(key)
                unique_restaurants.append(restaurant)
        
        return unique_restaurants
    
    def get_restaurant_details(self, restaurant: RestaurantInfo) -> Dict[str, Any]:
        """Get detailed information about a restaurant"""
        return {
            'basic_info': {
                'name': restaurant.name,
                'address': restaurant.address,
                'phone': restaurant.phone,
                'website': restaurant.website,
                'distance': f"{restaurant.distance_km} km away"
            },
            'gluten_free_info': {
                'celiac_safety_score': restaurant.celiac_friendly_score,
                'gluten_free_menu': restaurant.gluten_free_menu,
                'dedicated_fryer': restaurant.dedicated_fryer,
                'staff_training': restaurant.staff_training,
                'verified_safe': restaurant.verified_safe
            },
            'general_info': {
                'cuisine_type': restaurant.cuisine_type,
                'price_range': restaurant.price_range,
                'rating': restaurant.rating
            },
            'safety_tips': self._get_safety_tips(restaurant),
            'questions_to_ask': self._get_questions_to_ask(restaurant)
        }
    
    def _get_safety_tips(self, restaurant: RestaurantInfo) -> List[str]:
        """Get safety tips for dining at this restaurant"""
        tips = [
            "Always inform staff about your celiac disease",
            "Ask about gluten-free preparation procedures",
            "Verify ingredients in sauces and seasonings"
        ]
        
        if not restaurant.dedicated_fryer:
            tips.append("⚠️ Ask about shared fryers - avoid fried foods if shared")
        
        if restaurant.cuisine_type == "asian":
            tips.append("⚠️ Verify soy sauce is gluten-free (ask for tamari)")
        
        if restaurant.cuisine_type == "italian":
            tips.append("⚠️ High cross-contamination risk - ask about pasta water")
        
        if restaurant.celiac_friendly_score < 70:
            tips.append("⚠️ Lower safety score - be extra cautious")
        
        return tips
    
    def _get_questions_to_ask(self, restaurant: RestaurantInfo) -> List[str]:
        """Get questions to ask restaurant staff"""
        questions = [
            "Do you have a gluten-free menu?",
            "How do you prevent cross-contamination?",
            "Are your staff trained on celiac disease?",
            "Do you have a dedicated gluten-free preparation area?"
        ]
        
        if restaurant.cuisine_type in ["asian", "mexican"]:
            questions.append("Is your soy sauce gluten-free?")
        
        if restaurant.cuisine_type == "italian":
            questions.append("Do you use separate pasta water for gluten-free pasta?")
        
        return questions


# Global instance
restaurant_finder = RestaurantFinder()