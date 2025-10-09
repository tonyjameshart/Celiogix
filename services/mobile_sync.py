#!/usr/bin/env python3
"""
Mobile companion sync service for real-time data synchronization
"""

import json
import hashlib
import requests
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtWidgets import QMessageBox

from utils.encryption import get_health_encryption
from utils.error_handling import handle_error, ErrorCategory, ErrorSeverity
from utils.caching import get_cache_manager


class SyncDataType(Enum):
    """Mobile sync data types"""
    BARCODE_SCAN = "barcode_scan"
    SYMPTOM_LOG = "symptom_log"
    MEAL_LOG = "meal_log"
    CALENDAR_EVENT = "calendar_event"
    MENU_ITEM = "menu_item"
    RESTAURANT_DATA = "restaurant_data"
    SAFE_PRODUCT = "safe_product"
    UNSAFE_PRODUCT = "unsafe_product"
    TRAVEL_KIT = "travel_kit"
    TRANSLATION_CARD = "translation_card"
    SHOPPING_LIST_ITEM = "shopping_list_item"
    MOBILE_RECIPE = "mobile_recipe"
    HEALTH_TEMPLATE = "health_template"
    HEALTH_REMINDER = "health_reminder"
    CARE_PROVIDER = "care_provider"


@dataclass
class BarcodeScanData:
    """Barcode scan data from mobile"""
    barcode: str
    product_name: str
    brand: str
    gluten_status: str  # 'safe', 'unsafe', 'unknown'
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    scan_timestamp: datetime
    location: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class SymptomLogData:
    """Enhanced symptom log data from mobile"""
    timestamp: datetime
    symptoms: List[str]
    severity: int  # 1-10 scale
    meal_context: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    voice_note_path: Optional[str] = None  # Path to voice recording
    photo_paths: Optional[List[str]] = None  # Paths to symptom photos
    duration_hours: Optional[float] = None  # How long symptoms lasted
    triggers_suspected: Optional[List[str]] = None  # Suspected triggers
    mood: Optional[str] = None  # 'good', 'fair', 'poor', 'terrible'
    energy_level: Optional[int] = None  # 1-10 scale
    gluten_exposure_suspected: Optional[bool] = None  # Whether gluten exposure suspected
    emergency_level: Optional[str] = None  # 'normal', 'concerning', 'urgent', 'emergency'


@dataclass
class HealthTemplateData:
    """Health logging templates for quick entry"""
    template_id: str
    template_name: str
    symptoms: List[str]
    severity_range: tuple  # (min, max) severity
    meal_context: Optional[str] = None
    common_triggers: Optional[List[str]] = None
    duration_estimate: Optional[float] = None
    emergency_level: Optional[str] = None
    description: Optional[str] = None


@dataclass
class HealthReminderData:
    """Health reminder configuration"""
    reminder_id: str
    reminder_type: str  # 'symptom_check', 'meal_log', 'medication', 'appointment'
    trigger_event: str  # 'meal_completed', 'time_based', 'location_based'
    delay_minutes: int  # Minutes after trigger
    message: str
    enabled: bool = True
    last_triggered: Optional[datetime] = None


@dataclass
class MealLogData:
    """Meal log data from mobile"""
    timestamp: datetime
    meal_type: str  # 'breakfast', 'lunch', 'dinner', 'snack'
    items: List[str]
    restaurant: Optional[str] = None
    location: Optional[str] = None
    gluten_safety_confirmed: bool = False
    notes: Optional[str] = None


@dataclass
class RestaurantData:
    """Restaurant data for location-based finder"""
    name: str
    address: str
    latitude: float
    longitude: float
    gluten_free_options: bool
    dedicated_kitchen: bool
    staff_training: str  # 'excellent', 'good', 'basic', 'unknown'
    user_rating: float
    price_range: str
    cuisine_type: str
    last_updated: datetime


@dataclass
class ShoppingListItemData:
    """Shopping list item data from mobile"""
    item_name: str
    quantity: str
    category: str
    store: str
    purchased: bool
    timestamp: datetime
    priority: str = "Medium"  # 'High', 'Medium', 'Low'
    notes: Optional[str] = None
    gluten_free: bool = True  # Default to GF for celiac users


@dataclass
class MobileRecipeData:
    """Recipe data optimized for mobile offline viewing"""
    id: str
    name: str
    description: str
    category: str
    prep_time: str
    cook_time: str
    servings: int
    difficulty: str
    ingredients: Optional[str] = None
    instructions: Optional[str] = None
    nutrition_info: Optional[str] = None
    notes: Optional[str] = None
    image_path: Optional[str] = None
    pushed_at: str = ""
    mobile_optimized: bool = True
    gluten_free_verified: bool = True  # All recipes from desktop are GF


@dataclass
class TravelKitData:
    """Travel kit offline data"""
    country: str
    language: str
    emergency_contacts: List[str]
    safe_restaurants: List[RestaurantData]
    translation_cards: List[str]
    local_gluten_free_brands: List[str]
    cultural_food_notes: str


@dataclass
class CareProviderData:
    """Care provider contact information"""
    provider_id: str
    name: str
    title: str  # 'Dr.', 'RN', 'Dietitian', etc.
    specialty: str  # 'Gastroenterologist', 'Primary Care', 'Nutritionist', etc.
    organization: str  # Hospital, clinic, practice name
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    emergency_contact: bool = False
    preferred_contact_method: str = "phone"  # 'phone', 'email', 'both'
    last_appointment: Optional[str] = None
    next_appointment: Optional[str] = None
    created_date: str = ""
    updated_date: str = ""


class MobileSyncService(QObject):
    """Mobile companion synchronization service"""
    
    # Signals
    sync_started = Signal()
    sync_progress = Signal(int)
    sync_finished = Signal(bool)
    data_received = Signal(str, dict)  # data_type, data
    location_update = Signal(float, float)  # latitude, longitude
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cache_manager = get_cache_manager()
        self.encryption = get_health_encryption()
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.sync_mobile_data)
        self.auto_sync_enabled = False
        self.sync_interval = 30  # 30 seconds
        
        # Mobile data storage
        self.barcode_scans = []
        self.symptom_logs = []
        self.meal_logs = []
        self.restaurant_data = []
        self.shopping_list_items = []
        self.mobile_recipes = []  # Recipes pushed from desktop for offline viewing
        self.health_templates = []  # Quick entry templates for health logging
        self.health_reminders = []  # Smart reminders for health tracking
        self.care_providers = []  # Care provider contacts
        self.travel_kits = {}
        
        # Location tracking
        self.current_location = None
        self.location_timer = QTimer()
        self.location_timer.timeout.connect(self.update_location)
    
    def enable_auto_sync(self, interval_seconds: int = 30):
        """Enable automatic mobile sync"""
        self.auto_sync_enabled = True
        self.sync_interval = interval_seconds * 1000
        self.sync_timer.start(self.sync_interval)
    
    def disable_auto_sync(self):
        """Disable automatic mobile sync"""
        self.auto_sync_enabled = False
        self.sync_timer.stop()
    
    def sync_mobile_data(self):
        """Sync data with mobile companion"""
        if not self.auto_sync_enabled:
            return
        
        self.sync_started.emit()
        
        try:
            # Simulate mobile data sync
            # In real implementation, this would connect to mobile app via API/WebSocket
            self._simulate_mobile_data()
            self.sync_finished.emit(True)
            
        except Exception as e:
            handle_error(
                e, ErrorCategory.NETWORK, ErrorSeverity.MEDIUM,
                context={'operation': 'mobile_sync'}
            )
            self.sync_finished.emit(False)
    
    def _simulate_mobile_data(self):
        """Simulate receiving data from mobile app"""
        # Simulate barcode scan
        if len(self.barcode_scans) < 10:  # Limit for demo
            scan_data = BarcodeScanData(
                barcode="123456789012",
                product_name="Gluten-Free Bread",
                brand="Udi's",
                gluten_status="safe",
                risk_level="low",
                scan_timestamp=datetime.now(),
                location="Whole Foods Market"
            )
            self.add_barcode_scan(scan_data)
        
        # Simulate symptom log
        if len(self.symptom_logs) < 5:
            symptom_data = SymptomLogData(
                timestamp=datetime.now(),
                symptoms=["bloating", "fatigue"],
                severity=3,
                meal_context="Dinner at restaurant",
                location="Downtown"
            )
            self.add_symptom_log(symptom_data)
        
        # Simulate shopping list item
        if len(self.shopping_list_items) < 8:  # Limit for demo
            shopping_item = ShoppingListItemData(
                item_name="Gluten-Free Pasta",
                quantity="2 boxes",
                category="Pantry",
                store="Grocery Store",
                purchased=False,
                timestamp=datetime.now(),
                priority="Medium",
                notes="Brown rice pasta preferred",
                gluten_free=True
            )
            self.add_shopping_list_item(shopping_item)
    
    def add_barcode_scan(self, scan_data: BarcodeScanData):
        """Add barcode scan data from mobile"""
        self.barcode_scans.append(scan_data)
        
        # Cache for offline access
        cache_key = f"barcode_scan_{scan_data.barcode}_{scan_data.scan_timestamp.timestamp()}"
        self.cache_manager.set(cache_key, asdict(scan_data), ttl=86400)  # 24 hours
        
        # Emit signal
        self.data_received.emit(SyncDataType.BARCODE_SCAN.value, asdict(scan_data))
        
        # Update product database
        self._update_product_database(scan_data)
    
    def add_symptom_log(self, symptom_data: SymptomLogData):
        """Add symptom log data from mobile with enhanced features"""
        self.symptom_logs.append(symptom_data)
        
        # Encrypt sensitive health data
        encrypted_data = self.encryption.encrypt_dict(asdict(symptom_data))
        
        # Cache for offline access with longer TTL for health data
        cache_key = f"symptom_log_{symptom_data.timestamp.timestamp()}"
        self.cache_manager.set(cache_key, encrypted_data, ttl=259200)  # 3 days
        
        # Check for emergency level and trigger alerts
        if hasattr(symptom_data, 'emergency_level') and symptom_data.emergency_level in ['urgent', 'emergency']:
            self._trigger_emergency_alert(symptom_data)
        
        # Update health patterns and trigger smart reminders
        self._update_health_patterns(symptom_data)
        
        # Emit signal
        self.data_received.emit(SyncDataType.SYMPTOM_LOG.value, asdict(symptom_data))
    
    def add_symptom_log_with_media(self, symptom_data: Dict[str, Any]):
        """Add symptom log with voice notes and photos"""
        try:
            # Create enhanced symptom log data
            enhanced_symptom = SymptomLogData(
                timestamp=datetime.fromisoformat(symptom_data.get('timestamp', datetime.now().isoformat())),
                symptoms=symptom_data.get('symptoms', []),
                severity=symptom_data.get('severity', 1),
                meal_context=symptom_data.get('meal_context'),
                location=symptom_data.get('location'),
                notes=symptom_data.get('notes'),
                voice_note_path=symptom_data.get('voice_note_path'),
                photo_paths=symptom_data.get('photo_paths', []),
                duration_hours=symptom_data.get('duration_hours'),
                triggers_suspected=symptom_data.get('triggers_suspected', []),
                mood=symptom_data.get('mood'),
                energy_level=symptom_data.get('energy_level'),
                gluten_exposure_suspected=symptom_data.get('gluten_exposure_suspected'),
                emergency_level=symptom_data.get('emergency_level', 'normal')
            )
            
            self.add_symptom_log(enhanced_symptom)
            return True
            
        except Exception as e:
            print(f"Error adding symptom log with media: {str(e)}")
            return False
    
    def _trigger_emergency_alert(self, symptom_data: SymptomLogData):
        """Trigger emergency alert for urgent symptoms"""
        alert_message = f"""
🚨 EMERGENCY HEALTH ALERT 🚨

Severity: {symptom_data.severity}/10
Symptoms: {', '.join(symptom_data.symptoms)}
Emergency Level: {symptom_data.emergency_level}
Time: {symptom_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Location: {symptom_data.location or 'Unknown'}

Notes: {symptom_data.notes or 'None'}

Please seek immediate medical attention if symptoms worsen.
        """
        
        # In a real implementation, this would trigger:
        # - Push notification to emergency contacts
        # - Automatic emergency services contact if critical
        # - Log to emergency health log
        print(f"EMERGENCY ALERT: {alert_message}")
    
    def _update_health_patterns(self, symptom_data: SymptomLogData):
        """Update health patterns and trigger smart reminders"""
        # Analyze recent symptoms for patterns
        recent_symptoms = self.get_recent_symptoms(hours=24)
        
        # Check for pattern triggers
        if len(recent_symptoms) >= 3:
            # Pattern detected - trigger reminder for pattern analysis
            self._schedule_pattern_reminder(symptom_data)
    
    def get_recent_symptoms(self, hours: int = 24) -> List[SymptomLogData]:
        """Get recent symptoms within specified hours"""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [symptom for symptom in self.symptom_logs if symptom.timestamp >= cutoff_time]
    
    def _schedule_pattern_reminder(self, symptom_data: SymptomLogData):
        """Schedule smart reminder based on symptom patterns"""
        # Enhanced pattern-based reminder scheduling
        if symptom_data.severity >= 7:
            # High severity - schedule follow-up reminder
            reminder = HealthReminderData(
                reminder_id=f"followup_{symptom_data.timestamp.timestamp()}",
                reminder_type="symptom_check",
                trigger_event="time_based",
                delay_minutes=60,  # 1 hour later
                message="Follow-up check: How are your symptoms now?",
                enabled=True
            )
            self.add_health_reminder(reminder)
        
        # Schedule meal-related reminder if gluten exposure suspected
        if hasattr(symptom_data, 'gluten_exposure_suspected') and symptom_data.gluten_exposure_suspected:
            reminder = HealthReminderData(
                reminder_id=f"meal_avoidance_{symptom_data.timestamp.timestamp()}",
                reminder_type="meal_log",
                trigger_event="time_based",
                delay_minutes=180,  # 3 hours later
                message="Remember to avoid similar foods that may have caused this reaction.",
                enabled=True
            )
            self.add_health_reminder(reminder)
        
        # Schedule pattern tracking reminder for recurring symptoms
        if hasattr(symptom_data, 'triggers_suspected') and symptom_data.triggers_suspected:
            reminder = HealthReminderData(
                reminder_id=f"pattern_tracking_{symptom_data.timestamp.timestamp()}",
                reminder_type="symptom_check",
                trigger_event="time_based",
                delay_minutes=1440,  # 24 hours later
                message="Pattern check: Are you experiencing similar symptoms? Track any triggers.",
                enabled=True
            )
            self.add_health_reminder(reminder)
    
    def get_smart_reminders(self, context: str = "general") -> List[HealthReminderData]:
        """Get context-aware smart reminders"""
        smart_reminders = []
        
        if context == "meal_time":
            # Meal-related reminders
            meal_reminder = HealthReminderData(
                reminder_id="meal_symptom_check",
                reminder_type="meal_log",
                trigger_event="meal_completed",
                delay_minutes=30,
                message="How are you feeling after your meal? Log any symptoms or reactions.",
                enabled=True
            )
            smart_reminders.append(meal_reminder)
            
        elif context == "high_risk_time":
            # High-risk time reminders (evening, when symptoms often worsen)
            evening_reminder = HealthReminderData(
                reminder_id="evening_check",
                reminder_type="symptom_check",
                trigger_event="time_based",
                delay_minutes=0,  # Immediate
                message="Evening check-in: How are your symptoms? This is often when they worsen.",
                enabled=True
            )
            smart_reminders.append(evening_reminder)
            
        elif context == "pattern_detected":
            # Pattern-based reminders
            pattern_reminder = HealthReminderData(
                reminder_id="pattern_alert",
                reminder_type="symptom_check",
                trigger_event="pattern_based",
                delay_minutes=0,
                message="Pattern Alert: We've detected a potential trigger pattern. Please be extra careful.",
                enabled=True
            )
            smart_reminders.append(pattern_reminder)
        
        return smart_reminders
    
    def trigger_contextual_reminder(self, event_type: str, additional_data: Dict[str, Any] = None):
        """Trigger contextual reminders based on events"""
        if event_type == "meal_logged":
            # Trigger meal-related reminders
            meal_reminders = self.get_smart_reminders("meal_time")
            for reminder in meal_reminders:
                self.add_health_reminder(reminder)
                
        elif event_type == "high_severity_symptom":
            # Trigger high-severity reminders
            severity_reminder = HealthReminderData(
                reminder_id=f"severity_alert_{datetime.now().timestamp()}",
                reminder_type="symptom_check",
                trigger_event="severity_based",
                delay_minutes=30,
                message="High severity symptoms detected. Monitor closely and consider medical attention.",
                enabled=True
            )
            self.add_health_reminder(severity_reminder)
            
        elif event_type == "gluten_exposure_suspected":
            # Trigger gluten exposure reminders
            gluten_reminder = HealthReminderData(
                reminder_id=f"gluten_alert_{datetime.now().timestamp()}",
                reminder_type="symptom_check",
                trigger_event="gluten_exposure",
                delay_minutes=60,
                message="Gluten exposure suspected. Monitor symptoms closely and avoid similar foods.",
                enabled=True
            )
            self.add_health_reminder(gluten_reminder)
    
    def get_reminder_notifications(self) -> List[Dict[str, Any]]:
        """Get active reminder notifications"""
        notifications = []
        current_time = datetime.now()
        
        for reminder in self.health_reminders:
            if not reminder.enabled:
                continue
                
            # Check if reminder should be triggered
            should_trigger = False
            
            if reminder.trigger_event == "time_based":
                # Time-based reminders (simplified logic)
                should_trigger = True
            elif reminder.trigger_event == "meal_completed":
                # Meal-based reminders
                should_trigger = True
            elif reminder.trigger_event == "pattern_based":
                # Pattern-based reminders
                should_trigger = True
            
            if should_trigger:
                notification = {
                    'id': reminder.reminder_id,
                    'type': reminder.reminder_type,
                    'message': reminder.message,
                    'priority': 'high' if reminder.reminder_type == 'symptom_check' else 'medium',
                    'timestamp': current_time.isoformat(),
                    'action_required': True
                }
                notifications.append(notification)
        
        return notifications
    
    def add_meal_log(self, meal_data: MealLogData):
        """Add meal log data from mobile"""
        self.meal_logs.append(meal_data)
        
        # Cache for offline access
        cache_key = f"meal_log_{meal_data.timestamp.timestamp()}"
        self.cache_manager.set(cache_key, asdict(meal_data), ttl=86400)
        
        # Emit signal
        self.data_received.emit(SyncDataType.MEAL_LOG.value, asdict(meal_data))
    
    def add_restaurant_data(self, restaurant_data: RestaurantData):
        """Add restaurant data from mobile"""
        self.restaurant_data.append(restaurant_data)
        
        # Cache for offline access
        cache_key = f"restaurant_{restaurant_data.name}_{restaurant_data.latitude}_{restaurant_data.longitude}"
        self.cache_manager.set(cache_key, asdict(restaurant_data), ttl=604800)  # 7 days
        
        # Emit signal
        self.data_received.emit(SyncDataType.RESTAURANT_DATA.value, asdict(restaurant_data))
    
    def add_shopping_list_item(self, shopping_item: ShoppingListItemData):
        """Add shopping list item from mobile"""
        self.shopping_list_items.append(shopping_item)
        
        # Cache for offline access
        cache_key = f"shopping_item_{shopping_item.item_name}_{shopping_item.timestamp.timestamp()}"
        self.cache_manager.set(cache_key, asdict(shopping_item), ttl=86400)  # 24 hours
        
        # Emit signal
        self.data_received.emit(SyncDataType.SHOPPING_LIST_ITEM.value, asdict(shopping_item))
    
    def add_recipe_to_mobile(self, recipe_data: Dict[str, Any]):
        """Add recipe to mobile for offline viewing"""
        try:
            # Convert dict to MobileRecipeData
            mobile_recipe = MobileRecipeData(
                id=recipe_data.get('id', ''),
                name=recipe_data.get('name', ''),
                description=recipe_data.get('description', ''),
                category=recipe_data.get('category', ''),
                prep_time=recipe_data.get('prep_time', ''),
                cook_time=recipe_data.get('cook_time', ''),
                servings=recipe_data.get('servings', 1),
                difficulty=recipe_data.get('difficulty', ''),
                ingredients=recipe_data.get('ingredients'),
                instructions=recipe_data.get('instructions'),
                nutrition_info=recipe_data.get('nutrition_info'),
                notes=recipe_data.get('notes'),
                image_path=recipe_data.get('image_path'),
                pushed_at=recipe_data.get('pushed_at', ''),
                mobile_optimized=recipe_data.get('mobile_optimized', True),
                gluten_free_verified=recipe_data.get('gluten_free_verified', True)
            )
            
            # Add to storage
            self.mobile_recipes.append(mobile_recipe)
            
            # Cache for offline access with longer TTL (recipes don't change often)
            cache_key = f"recipe_{mobile_recipe.id}"
            self.cache_manager.set(cache_key, asdict(mobile_recipe), ttl=604800)  # 7 days
            
            # Emit signal
            self.data_received.emit(SyncDataType.MOBILE_RECIPE.value, asdict(mobile_recipe))
            
            return True
            
        except Exception as e:
            print(f"Error adding recipe to mobile: {str(e)}")
            return False
    
    def add_travel_kit(self, country: str, travel_kit: TravelKitData):
        """Add travel kit data"""
        self.travel_kits[country] = travel_kit
        
        # Cache for offline access
        cache_key = f"travel_kit_{country}"
        self.cache_manager.set(cache_key, asdict(travel_kit), ttl=2592000)  # 30 days
    
    def _update_product_database(self, scan_data: BarcodeScanData):
        """Update product database with scan data"""
        try:
            from utils.db import get_connection
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Create product database if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_database (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode TEXT UNIQUE,
                    product_name TEXT,
                    brand TEXT,
                    gluten_status TEXT,
                    risk_level TEXT,
                    last_scan_date TEXT,
                    scan_count INTEGER DEFAULT 1
                )
            """)
            
            # Insert or update product
            cursor.execute("""
                INSERT OR REPLACE INTO product_database 
                (barcode, product_name, brand, gluten_status, risk_level, last_scan_date, scan_count)
                VALUES (?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT scan_count FROM product_database WHERE barcode = ?), 0) + 1)
            """, (
                scan_data.barcode,
                scan_data.product_name,
                scan_data.brand,
                scan_data.gluten_status,
                scan_data.risk_level,
                scan_data.scan_timestamp.isoformat(),
                scan_data.barcode
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            handle_error(
                e, ErrorCategory.DATABASE, ErrorSeverity.MEDIUM,
                context={'operation': 'update_product_database', 'barcode': scan_data.barcode}
            )
    
    def get_safe_products(self) -> List[Dict[str, Any]]:
        """Get list of safe products from mobile scans"""
        safe_products = []
        
        for scan in self.barcode_scans:
            if scan.gluten_status == 'safe':
                safe_products.append({
                    'barcode': scan.barcode,
                    'product_name': scan.product_name,
                    'brand': scan.brand,
                    'last_scan': scan.scan_timestamp,
                    'location': scan.location
                })
        
        return safe_products
    
    def get_unsafe_products(self) -> List[Dict[str, Any]]:
        """Get list of unsafe products from mobile scans"""
        unsafe_products = []
        
        for scan in self.barcode_scans:
            if scan.gluten_status == 'unsafe':
                unsafe_products.append({
                    'barcode': scan.barcode,
                    'product_name': scan.product_name,
                    'brand': scan.brand,
                    'risk_level': scan.risk_level,
                    'last_scan': scan.scan_timestamp,
                    'location': scan.location
                })
        
        return unsafe_products
    
    def get_symptom_patterns(self) -> Dict[str, Any]:
        """Analyze symptom patterns from mobile data"""
        if not self.symptom_logs:
            return {}
        
        # Group symptoms by time of day
        morning_symptoms = []
        afternoon_symptoms = []
        evening_symptoms = []
        
        for log in self.symptom_logs:
            hour = log.timestamp.hour
            if 6 <= hour < 12:
                morning_symptoms.extend(log.symptoms)
            elif 12 <= hour < 18:
                afternoon_symptoms.extend(log.symptoms)
            else:
                evening_symptoms.extend(log.symptoms)
        
        # Calculate averages
        avg_severity = sum(log.severity for log in self.symptom_logs) / len(self.symptom_logs)
        
        return {
            'total_logs': len(self.symptom_logs),
            'average_severity': avg_severity,
            'most_common_symptoms': self._get_most_common_symptoms(),
            'symptoms_by_time': {
                'morning': morning_symptoms,
                'afternoon': afternoon_symptoms,
                'evening': evening_symptoms
            }
        }
    
    def _get_most_common_symptoms(self) -> List[tuple]:
        """Get most common symptoms from logs"""
        symptom_counts = {}
        
        for log in self.symptom_logs:
            for symptom in log.symptoms:
                symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
        
        return sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)
    
    def get_nearby_restaurants(self, latitude: float, longitude: float, radius_km: float = 5.0) -> List[RestaurantData]:
        """Get nearby gluten-free restaurants"""
        nearby_restaurants = []
        
        for restaurant in self.restaurant_data:
            distance = self._calculate_distance(
                latitude, longitude,
                restaurant.latitude, restaurant.longitude
            )
            
            if distance <= radius_km:
                nearby_restaurants.append(restaurant)
        
        # Sort by distance
        nearby_restaurants.sort(key=lambda r: self._calculate_distance(
            latitude, longitude, r.latitude, r.longitude
        ))
        
        return nearby_restaurants
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        import math
        
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def get_shopping_list_items(self, store_filter: Optional[str] = None, category_filter: Optional[str] = None) -> List[ShoppingListItemData]:
        """Get shopping list items with optional filters"""
        filtered_items = self.shopping_list_items.copy()
        
        if store_filter and store_filter != "All Stores":
            filtered_items = [item for item in filtered_items if item.store == store_filter]
        
        if category_filter and category_filter != "All Categories":
            filtered_items = [item for item in filtered_items if item.category == category_filter]
        
        # Sort by priority (High, Medium, Low), then by item name
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        filtered_items.sort(key=lambda x: (priority_order.get(x.priority, 1), x.item_name))
        
        return filtered_items
    
    def update_shopping_list_item_purchased(self, item_name: str, store: str, purchased: bool):
        """Update purchased status of a shopping list item"""
        for item in self.shopping_list_items:
            if item.item_name == item_name and item.store == store:
                item.purchased = purchased
                # Update cache
                cache_key = f"shopping_item_{item.item_name}_{item.timestamp.timestamp()}"
                self.cache_manager.set(cache_key, asdict(item), ttl=86400)
                break
    
    def get_shopping_list_stats(self) -> Dict[str, Any]:
        """Get shopping list statistics"""
        total_items = len(self.shopping_list_items)
        purchased_items = sum(1 for item in self.shopping_list_items if item.purchased)
        pending_items = total_items - purchased_items
        
        # Count by store
        store_counts = {}
        for item in self.shopping_list_items:
            store_counts[item.store] = store_counts.get(item.store, 0) + 1
        
        # Count by category
        category_counts = {}
        for item in self.shopping_list_items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1
        
        return {
            'total_items': total_items,
            'purchased_items': purchased_items,
            'pending_items': pending_items,
            'completion_percentage': (purchased_items / total_items * 100) if total_items > 0 else 0,
            'store_counts': store_counts,
            'category_counts': category_counts
        }
    
    def get_translation_card(self, language: str) -> str:
        """Get translation card for specified language"""
        translation_cards = {
            'english': "I have Celiac Disease, a serious autoimmune condition. I must eat strictly gluten-free to avoid getting sick. Gluten is a protein found in wheat, rye, and barley. Even tiny amounts — from shared surfaces, utensils, fryers, or cooking water — can cause a reaction. Can you please help me choose a safe gluten-free option? Thank you so much for your help — I really appreciate it!",
            'spanish': "Tengo enfermedad celíaca, una condición autoinmune grave. Debo comer estrictamente sin gluten para evitar enfermarme. El gluten es una proteína que se encuentra en el trigo, el centeno y la cebada. Incluso cantidades muy pequeñas — de superficies compartidas, utensilios, freidoras o agua de cocción — pueden causar una reacción. ¿Podrías ayudarme a elegir una opción segura sin gluten? ¡Muchas gracias por tu ayuda — realmente lo aprecio!",
            'french': "J'ai la maladie cœliaque, une maladie auto-immune grave. Je dois manger strictement sans gluten pour éviter de tomber malade. Le gluten est une protéine présente dans le blé, le seigle et l'orge. Même de très petites quantités — provenant de surfaces partagées, d'ustensiles, de friteuses ou d'eau de cuisson — peuvent causer une réaction. Pouvez-vous m'aider à choisir une option sûre sans gluten ? Merci beaucoup pour votre aide — je l'apprécie vraiment !",
            'german': "Ich habe Zöliakie, eine ernste Autoimmunerkrankung. Ich muss streng glutenfrei essen, um nicht krank zu werden. Gluten ist ein Protein, das in Weizen, Roggen und Gerste vorkommt. Selbst winzige Mengen — von geteilten Oberflächen, Utensilien, Frittiergeräten oder Kochwasser — können eine Reaktion verursachen. Können Sie mir bitte helfen, eine sichere glutenfreie Option zu wählen? Vielen Dank für Ihre Hilfe — ich schätze es wirklich sehr!",
            'italian': "Ho la malattia celiaca, una condizione autoimmune grave. Devo mangiare rigorosamente senza glutine per evitare di ammalarmi. Il glutine è una proteina presente nel grano, nella segale e nell'orzo. Anche piccole quantità — da superfici condivise, utensili, friggitrici o acqua di cottura — possono causare una reazione. Potreste aiutarmi a scegliere un'opzione sicura senza glutine? Grazie mille per il vostro aiuto — lo apprezzo davvero!",
            'portuguese': "Tenho doença celíaca, uma condição autoimune séria. Devo comer estritamente sem glúten para evitar ficar doente. O glúten é uma proteína encontrada no trigo, centeio e cevada. Mesmo pequenas quantidades — de superfícies compartilhadas, utensílios, fritadeiras ou água de cozimento — podem causar uma reação. Você poderia me ajudar a escolher uma opção segura sem glúten? Muito obrigado pela sua ajuda — eu realmente agradeço!",
            'japanese': "私はセリアック病という深刻な自己免疫疾患を患っています。病気を避けるために、厳格にグルテンフリーで食事をする必要があります。グルテンは小麦、ライ麦、大麦に含まれるタンパク質です。共有の表面、調理器具、フライヤー、または調理水からの微量でも反応を引き起こす可能性があります。安全なグルテンフリーの選択肢を選ぶのを手伝っていただけますか？ご協力いただき、本当にありがとうございます！",
            'chinese': "我患有乳糜泻，这是一种严重的自身免疫性疾病。我必须严格无麸质饮食以避免生病。麸质是存在于小麦、黑麦和大麦中的蛋白质。即使是极少量——来自共享表面、器具、油炸锅或烹饪水——也可能引起反应。您能帮我选择一个安全的无麸质选择吗？非常感谢您的帮助——我真的很感激！",
            'arabic': "لدي مرض الاضطرابات الهضمية، وهي حالة مناعية ذاتية خطيرة. يجب أن أتناول طعامًا خاليًا من الغلوتين بشكل صارم لتجنب المرض. الغلوتين هو بروتين موجود في القمح والجاودار والشعير. حتى الكميات الصغيرة جداً - من الأسطح المشتركة أو الأدوات أو المقليات أو ماء الطهي - يمكن أن تسبب رد فعل. هل يمكنك مساعدتي في اختيار خيار آمن خالٍ من الغلوتين؟ شكراً جزيلاً لمساعدتك - أقدر ذلك حقاً!",
            'hindi': "मुझे सीलिएक रोग है, जो एक गंभीर ऑटोइम्यून स्थिति है। बीमार होने से बचने के लिए मुझे सख्ती से ग्लूटेन-मुक्त भोजन करना चाहिए। ग्लूटेन गेहूं, राई और जौ में पाया जाने वाला प्रोटीन है। यहां तक कि बहुत कम मात्रा - साझा सतहों, बर्तनों, फ्रायर या पकाने के पानी से - प्रतिक्रिया का कारण बन सकती है। क्या आप मुझे एक सुरक्षित ग्लूटेन-मुक्त विकल्प चुनने में मदद कर सकते हैं? आपकी मदद के लिए बहुत धन्यवाद - मैं वास्तव में इसकी सराहना करता हूं!"
        }
        
        return translation_cards.get(language.lower(), translation_cards['english'])
    
    def get_mobile_recipes(self, category_filter: Optional[str] = None) -> List[MobileRecipeData]:
        """Get mobile recipes with optional category filter"""
        if category_filter and category_filter != "All Categories":
            return [recipe for recipe in self.mobile_recipes if recipe.category == category_filter]
        return self.mobile_recipes.copy()
    
    def get_mobile_recipe(self, recipe_id: str) -> Optional[MobileRecipeData]:
        """Get specific mobile recipe by ID"""
        for recipe in self.mobile_recipes:
            if recipe.id == recipe_id:
                return recipe
        return None
    
    def get_mobile_recipe_categories(self) -> List[str]:
        """Get unique categories from mobile recipes"""
        categories = set()
        for recipe in self.mobile_recipes:
            if recipe.category:
                categories.add(recipe.category)
        return sorted(list(categories))
    
    def get_mobile_recipe_stats(self) -> Dict[str, Any]:
        """Get mobile recipe statistics"""
        total_recipes = len(self.mobile_recipes)
        
        # Count by category
        category_counts = {}
        for recipe in self.mobile_recipes:
            category_counts[recipe.category] = category_counts.get(recipe.category, 0) + 1
        
        # Count by difficulty
        difficulty_counts = {}
        for recipe in self.mobile_recipes:
            difficulty_counts[recipe.difficulty] = difficulty_counts.get(recipe.difficulty, 0) + 1
        
        return {
            'total_recipes': total_recipes,
            'category_counts': category_counts,
            'difficulty_counts': difficulty_counts
        }
    
    def add_health_template(self, template_data: Dict[str, Any]):
        """Add health template for quick entry"""
        try:
            template = HealthTemplateData(
                template_id=template_data.get('template_id', ''),
                template_name=template_data.get('template_name', ''),
                symptoms=template_data.get('symptoms', []),
                severity_range=template_data.get('severity_range', (1, 5)),
                meal_context=template_data.get('meal_context'),
                common_triggers=template_data.get('common_triggers', []),
                duration_estimate=template_data.get('duration_estimate'),
                emergency_level=template_data.get('emergency_level', 'normal'),
                description=template_data.get('description', '')
            )
            
            # Add to storage
            self.health_templates.append(template)
            
            # Cache for offline access
            cache_key = f"health_template_{template.template_id}"
            self.cache_manager.set(cache_key, asdict(template), ttl=604800)  # 7 days
            
            # Emit signal
            self.data_received.emit(SyncDataType.HEALTH_TEMPLATE.value, asdict(template))
            
            return True
            
        except Exception as e:
            print(f"Error adding health template: {str(e)}")
            return False
    
    def get_health_templates(self) -> List[HealthTemplateData]:
        """Get all health templates"""
        return self.health_templates.copy()
    
    def get_health_template(self, template_id: str) -> Optional[HealthTemplateData]:
        """Get specific health template by ID"""
        for template in self.health_templates:
            if template.template_id == template_id:
                return template
        return None
    
    def add_health_reminder(self, reminder_data: Dict[str, Any]):
        """Add health reminder configuration"""
        try:
            reminder = HealthReminderData(
                reminder_id=reminder_data.get('reminder_id', ''),
                reminder_type=reminder_data.get('reminder_type', ''),
                trigger_event=reminder_data.get('trigger_event', ''),
                delay_minutes=reminder_data.get('delay_minutes', 0),
                message=reminder_data.get('message', ''),
                enabled=reminder_data.get('enabled', True),
                last_triggered=None
            )
            
            # Add to storage
            self.health_reminders.append(reminder)
            
            # Cache for offline access
            cache_key = f"health_reminder_{reminder.reminder_id}"
            self.cache_manager.set(cache_key, asdict(reminder), ttl=604800)  # 7 days
            
            # Emit signal
            self.data_received.emit(SyncDataType.HEALTH_REMINDER.value, asdict(reminder))
            
            return True
            
        except Exception as e:
            print(f"Error adding health reminder: {str(e)}")
            return False
    
    def get_health_reminders(self) -> List[HealthReminderData]:
        """Get all health reminders"""
        return self.health_reminders.copy()
    
    def get_enabled_health_reminders(self) -> List[HealthReminderData]:
        """Get only enabled health reminders"""
        return [reminder for reminder in self.health_reminders if reminder.enabled]
    
    def add_care_provider(self, provider_data: Dict[str, Any]):
        """Add care provider to mobile sync"""
        try:
            # Convert dict to CareProviderData
            care_provider = CareProviderData(
                provider_id=provider_data.get('provider_id', ''),
                name=provider_data.get('name', ''),
                title=provider_data.get('title', ''),
                specialty=provider_data.get('specialty', ''),
                organization=provider_data.get('organization', ''),
                phone=provider_data.get('phone'),
                email=provider_data.get('email'),
                address=provider_data.get('address'),
                city=provider_data.get('city'),
                state=provider_data.get('state'),
                zip_code=provider_data.get('zip_code'),
                website=provider_data.get('website'),
                notes=provider_data.get('notes'),
                emergency_contact=provider_data.get('emergency_contact', False),
                preferred_contact_method=provider_data.get('preferred_contact_method', 'phone'),
                last_appointment=provider_data.get('last_appointment'),
                next_appointment=provider_data.get('next_appointment'),
                created_date=provider_data.get('created_date', datetime.now().isoformat()),
                updated_date=provider_data.get('updated_date', datetime.now().isoformat())
            )
            
            # Add to storage
            self.care_providers.append(care_provider)
            
            # Cache for offline access with longer TTL (providers don't change often)
            cache_key = f"care_provider_{care_provider.provider_id}"
            self.cache_manager.set(cache_key, asdict(care_provider), ttl=604800)  # 7 days
            
            # Emit signal
            self.data_received.emit(SyncDataType.CARE_PROVIDER.value, asdict(care_provider))
            
            return True
            
        except Exception as e:
            print(f"Error adding care provider: {str(e)}")
            return False
    
    def get_care_providers(self, specialty_filter: Optional[str] = None) -> List[CareProviderData]:
        """Get all care providers, optionally filtered by specialty"""
        providers = self.care_providers.copy()
        
        if specialty_filter:
            providers = [p for p in providers if specialty_filter.lower() in p.specialty.lower()]
        
        return providers
    
    def get_care_provider(self, provider_id: str) -> Optional[CareProviderData]:
        """Get specific care provider by ID"""
        for provider in self.care_providers:
            if provider.provider_id == provider_id:
                return provider
        return None
    
    def get_emergency_providers(self) -> List[CareProviderData]:
        """Get emergency care providers"""
        return [provider for provider in self.care_providers if provider.emergency_contact]
    
    def get_provider_specialties(self) -> List[str]:
        """Get list of unique provider specialties"""
        specialties = set()
        for provider in self.care_providers:
            if provider.specialty:
                specialties.add(provider.specialty)
        return sorted(list(specialties))
    
    def update_care_provider(self, provider_id: str, provider_data: Dict[str, Any]) -> bool:
        """Update existing care provider"""
        try:
            for i, provider in enumerate(self.care_providers):
                if provider.provider_id == provider_id:
                    # Update provider data
                    updated_provider = CareProviderData(
                        provider_id=provider_data.get('provider_id', provider.provider_id),
                        name=provider_data.get('name', provider.name),
                        title=provider_data.get('title', provider.title),
                        specialty=provider_data.get('specialty', provider.specialty),
                        organization=provider_data.get('organization', provider.organization),
                        phone=provider_data.get('phone', provider.phone),
                        email=provider_data.get('email', provider.email),
                        address=provider_data.get('address', provider.address),
                        city=provider_data.get('city', provider.city),
                        state=provider_data.get('state', provider.state),
                        zip_code=provider_data.get('zip_code', provider.zip_code),
                        website=provider_data.get('website', provider.website),
                        notes=provider_data.get('notes', provider.notes),
                        emergency_contact=provider_data.get('emergency_contact', provider.emergency_contact),
                        preferred_contact_method=provider_data.get('preferred_contact_method', provider.preferred_contact_method),
                        last_appointment=provider_data.get('last_appointment', provider.last_appointment),
                        next_appointment=provider_data.get('next_appointment', provider.next_appointment),
                        created_date=provider.created_date,  # Keep original
                        updated_date=datetime.now().isoformat()
                    )
                    
                    self.care_providers[i] = updated_provider
                    
                    # Update cache
                    cache_key = f"care_provider_{provider_id}"
                    self.cache_manager.set(cache_key, asdict(updated_provider), ttl=604800)
                    
                    # Emit signal
                    self.data_received.emit(SyncDataType.CARE_PROVIDER.value, asdict(updated_provider))
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error updating care provider: {str(e)}")
            return False
    
    def delete_care_provider(self, provider_id: str) -> bool:
        """Delete care provider"""
        try:
            for i, provider in enumerate(self.care_providers):
                if provider.provider_id == provider_id:
                    deleted_provider = self.care_providers.pop(i)
                    
                    # Remove from cache
                    cache_key = f"care_provider_{provider_id}"
                    self.cache_manager.remove(cache_key)
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting care provider: {str(e)}")
            return False
    
    def export_mobile_data(self, data_type: str) -> Dict[str, Any]:
        """Export mobile data for desktop analysis"""
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'data_type': data_type,
            'total_records': 0
        }
        
        if data_type == 'barcode_scans':
            export_data['records'] = [asdict(scan) for scan in self.barcode_scans]
            export_data['total_records'] = len(self.barcode_scans)
        elif data_type == 'symptom_logs':
            export_data['records'] = [asdict(log) for log in self.symptom_logs]
            export_data['total_records'] = len(self.symptom_logs)
        elif data_type == 'meal_logs':
            export_data['records'] = [asdict(log) for log in self.meal_logs]
            export_data['total_records'] = len(self.meal_logs)
        elif data_type == 'restaurants':
            export_data['records'] = [asdict(restaurant) for restaurant in self.restaurant_data]
            export_data['total_records'] = len(self.restaurant_data)
        elif data_type == 'shopping_list':
            export_data['records'] = [asdict(item) for item in self.shopping_list_items]
            export_data['total_records'] = len(self.shopping_list_items)
        elif data_type == 'mobile_recipes':
            export_data['records'] = [asdict(recipe) for recipe in self.mobile_recipes]
            export_data['total_records'] = len(self.mobile_recipes)
        elif data_type == 'care_providers':
            export_data['records'] = [asdict(provider) for provider in self.care_providers]
            export_data['total_records'] = len(self.care_providers)
            export_data['specialties'] = self.get_provider_specialties()
            export_data['emergency_providers'] = len(self.get_emergency_providers())
        
        return export_data
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get mobile sync status"""
        return {
            'auto_sync_enabled': self.auto_sync_enabled,
            'sync_interval': self.sync_interval,
            'total_barcode_scans': len(self.barcode_scans),
            'total_symptom_logs': len(self.symptom_logs),
            'total_meal_logs': len(self.meal_logs),
            'total_restaurants': len(self.restaurant_data),
            'total_shopping_list_items': len(self.shopping_list_items),
            'total_mobile_recipes': len(self.mobile_recipes),
            'travel_kits_available': list(self.travel_kits.keys()),
            'last_sync': datetime.now().isoformat()
        }


# Global mobile sync service instance
_mobile_sync_service = None


def get_mobile_sync_service() -> MobileSyncService:
    """Get global mobile sync service"""
    global _mobile_sync_service
    if _mobile_sync_service is None:
        _mobile_sync_service = MobileSyncService()
    return _mobile_sync_service
