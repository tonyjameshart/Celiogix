#!/usr/bin/env python3
"""
Offline cache service for mobile companion data
"""

import json
import sqlite3
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from PySide6.QtCore import QObject, Signal, QTimer
from utils.encryption import get_health_encryption
from utils.error_handling import handle_error, ErrorCategory, ErrorSeverity


@dataclass
class CacheItem:
    """Cache item with metadata"""
    key: str
    data: Any
    data_type: str
    timestamp: datetime
    ttl: int  # Time to live in seconds
    checksum: str
    device_id: str
    sync_status: str  # 'local', 'synced', 'pending', 'conflict'


class OfflineCacheService(QObject):
    """Service for managing offline cache of mobile data"""
    
    # Signals
    cache_updated = Signal(str, dict)  # data_type, data
    sync_required = Signal(str, list)  # operation, items
    conflict_detected = Signal(str, dict, dict)  # data_type, local, remote
    
    def __init__(self, cache_db_path: str = "data/mobile_cache.db", parent=None):
        super().__init__(parent)
        self.cache_db_path = cache_db_path
        self.encryption = get_health_encryption()
        self.device_id = self._generate_device_id()
        self.cache_items = {}
        self.sync_queue = []
        
        self._init_cache_database()
        self._load_cache_items()
    
    def _generate_device_id(self) -> str:
        """Generate unique device ID"""
        import platform
        import uuid
        
        system_info = f"{platform.node()}{platform.system()}{platform.machine()}"
        return hashlib.sha256(system_info.encode()).hexdigest()[:16]
    
    def _init_cache_database(self):
        """Initialize cache database"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS offline_cache (
                key TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                data_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ttl INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                device_id TEXT NOT NULL,
                sync_status TEXT NOT NULL,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                data_type TEXT NOT NULL,
                item_key TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_database (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                product_name TEXT NOT NULL,
                brand TEXT,
                gluten_status TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                ingredients TEXT,
                allergen_info TEXT,
                certification TEXT,
                last_updated TEXT NOT NULL,
                scan_count INTEGER DEFAULT 1,
                confidence_score REAL DEFAULT 0.0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS restaurant_database (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                gluten_free_options BOOLEAN NOT NULL,
                dedicated_kitchen BOOLEAN NOT NULL,
                staff_training TEXT NOT NULL,
                user_rating REAL DEFAULT 0.0,
                price_range TEXT,
                cuisine_type TEXT,
                last_updated TEXT NOT NULL,
                visit_count INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_cache_items(self):
        """Load cache items from database"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM offline_cache")
        rows = cursor.fetchall()
        
        for row in rows:
            key, data_str, data_type, timestamp_str, ttl, checksum, device_id, sync_status = row
            
            try:
                # Decrypt data if it's sensitive
                if data_type in ['symptom_log', 'meal_log']:
                    data = self.encryption.decrypt_dict(json.loads(data_str))
                else:
                    data = json.loads(data_str)
                
                timestamp = datetime.fromisoformat(timestamp_str)
                
                cache_item = CacheItem(
                    key=key,
                    data=data,
                    data_type=data_type,
                    timestamp=timestamp,
                    ttl=ttl,
                    checksum=checksum,
                    device_id=device_id,
                    sync_status=sync_status
                )
                
                self.cache_items[key] = cache_item
                
            except Exception as e:
                handle_error(
                    e, ErrorCategory.DATABASE, ErrorSeverity.LOW,
                    context={'operation': 'load_cache_item', 'key': key}
                )
        
        conn.close()
    
    def cache_item(self, key: str, data: Any, data_type: str, ttl: int = 86400) -> bool:
        """
        Cache an item offline
        
        Args:
            key: Unique cache key
            data: Data to cache
            data_type: Type of data
            ttl: Time to live in seconds
            
        Returns:
            True if cached successfully
        """
        try:
            # Calculate checksum
            data_str = json.dumps(data, sort_keys=True)
            checksum = hashlib.md5(data_str.encode()).hexdigest()
            
            # Encrypt sensitive data
            if data_type in ['symptom_log', 'meal_log']:
                encrypted_data = self.encryption.encrypt_dict(data)
                data_str = json.dumps(encrypted_data)
            
            # Create cache item
            cache_item = CacheItem(
                key=key,
                data=data,
                data_type=data_type,
                timestamp=datetime.now(),
                ttl=ttl,
                checksum=checksum,
                device_id=self.device_id,
                sync_status='local'
            )
            
            # Store in memory
            self.cache_items[key] = cache_item
            
            # Store in database
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO offline_cache 
                (key, data, data_type, timestamp, ttl, checksum, device_id, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key, data_str, data_type, cache_item.timestamp.isoformat(),
                ttl, checksum, self.device_id, 'local'
            ))
            
            conn.commit()
            conn.close()
            
            # Add to sync queue
            self._add_to_sync_queue('cache', data_type, key, data)
            
            # Emit signal
            self.cache_updated.emit(data_type, data)
            
            return True
            
        except Exception as e:
            handle_error(
                e, ErrorCategory.DATABASE, ErrorSeverity.MEDIUM,
                context={'operation': 'cache_item', 'key': key, 'data_type': data_type}
            )
            return False
    
    def get_cached_item(self, key: str) -> Optional[Any]:
        """Get cached item"""
        if key not in self.cache_items:
            return None
        
        cache_item = self.cache_items[key]
        
        # Check if expired
        if datetime.now() - cache_item.timestamp > timedelta(seconds=cache_item.ttl):
            self._remove_cache_item(key)
            return None
        
        return cache_item.data
    
    def get_cached_items_by_type(self, data_type: str) -> List[Any]:
        """Get all cached items of a specific type"""
        items = []
        
        for cache_item in self.cache_items.values():
            if cache_item.data_type == data_type:
                # Check if expired
                if datetime.now() - cache_item.timestamp <= timedelta(seconds=cache_item.ttl):
                    items.append(cache_item.data)
        
        return items
    
    def _remove_cache_item(self, key: str):
        """Remove cache item"""
        if key in self.cache_items:
            del self.cache_items[key]
        
        # Remove from database
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM offline_cache WHERE key = ?", (key,))
        conn.commit()
        conn.close()
    
    def _add_to_sync_queue(self, operation: str, data_type: str, key: str, data: Any):
        """Add item to sync queue"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sync_queue (operation, data_type, item_key, data, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                operation, data_type, key, json.dumps(data), datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            # Emit sync required signal
            self.sync_required.emit(operation, [{'key': key, 'data': data, 'type': data_type}])
            
        except Exception as e:
            handle_error(
                e, ErrorCategory.DATABASE, ErrorSeverity.LOW,
                context={'operation': 'add_to_sync_queue', 'key': key}
            )
    
    def cache_product_data(self, barcode: str, product_data: Dict[str, Any]) -> bool:
        """Cache product data from barcode scan"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO product_database 
                (barcode, product_name, brand, gluten_status, risk_level, 
                 ingredients, allergen_info, certification, last_updated, scan_count, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT scan_count FROM product_database WHERE barcode = ?), 0) + 1, ?)
            """, (
                barcode,
                product_data.get('name', ''),
                product_data.get('brand', ''),
                product_data.get('gluten_status', 'unknown'),
                product_data.get('risk_level', 'medium'),
                product_data.get('ingredients', ''),
                product_data.get('allergen_info', ''),
                product_data.get('certification', ''),
                datetime.now().isoformat(),
                barcode,
                product_data.get('confidence_score', 0.0)
            ))
            
            conn.commit()
            conn.close()
            
            # Cache in offline cache as well
            cache_key = f"product_{barcode}"
            self.cache_item(cache_key, product_data, 'product_data', ttl=604800)  # 7 days
            
            return True
            
        except Exception as e:
            handle_error(
                e, ErrorCategory.DATABASE, ErrorSeverity.MEDIUM,
                context={'operation': 'cache_product_data', 'barcode': barcode}
            )
            return False
    
    def get_product_data(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product data from cache"""
        # First check offline cache
        cache_key = f"product_{barcode}"
        cached_data = self.get_cached_item(cache_key)
        if cached_data:
            return cached_data
        
        # Check database
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT product_name, brand, gluten_status, risk_level, 
                   ingredients, allergen_info, certification, last_updated, 
                   scan_count, confidence_score
            FROM product_database WHERE barcode = ?
        """, (barcode,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            product_data = {
                'barcode': barcode,
                'name': row[0],
                'brand': row[1],
                'gluten_status': row[2],
                'risk_level': row[3],
                'ingredients': row[4],
                'allergen_info': row[5],
                'certification': row[6],
                'last_updated': row[7],
                'scan_count': row[8],
                'confidence_score': row[9]
            }
            
            # Cache for faster access
            self.cache_item(cache_key, product_data, 'product_data', ttl=604800)
            
            return product_data
        
        return None
    
    def cache_restaurant_data(self, restaurant_data: Dict[str, Any]) -> bool:
        """Cache restaurant data"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO restaurant_database 
                (name, address, latitude, longitude, gluten_free_options, 
                 dedicated_kitchen, staff_training, user_rating, price_range, 
                 cuisine_type, last_updated, visit_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT visit_count FROM restaurant_database 
                             WHERE name = ? AND address = ?), 0) + 1)
            """, (
                restaurant_data.get('name', ''),
                restaurant_data.get('address', ''),
                restaurant_data.get('latitude', 0.0),
                restaurant_data.get('longitude', 0.0),
                restaurant_data.get('gluten_free_options', False),
                restaurant_data.get('dedicated_kitchen', False),
                restaurant_data.get('staff_training', 'unknown'),
                restaurant_data.get('user_rating', 0.0),
                restaurant_data.get('price_range', ''),
                restaurant_data.get('cuisine_type', ''),
                datetime.now().isoformat(),
                restaurant_data.get('name', ''),
                restaurant_data.get('address', '')
            ))
            
            conn.commit()
            conn.close()
            
            # Cache in offline cache
            cache_key = f"restaurant_{restaurant_data.get('name', '')}_{restaurant_data.get('latitude', 0)}_{restaurant_data.get('longitude', 0)}"
            self.cache_item(cache_key, restaurant_data, 'restaurant_data', ttl=604800)  # 7 days
            
            return True
            
        except Exception as e:
            handle_error(
                e, ErrorCategory.DATABASE, ErrorSeverity.MEDIUM,
                context={'operation': 'cache_restaurant_data'}
            )
            return False
    
    def get_nearby_restaurants(self, latitude: float, longitude: float, radius_km: float = 5.0) -> List[Dict[str, Any]]:
        """Get nearby restaurants from cache"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, address, latitude, longitude, gluten_free_options, 
                   dedicated_kitchen, staff_training, user_rating, price_range, 
                   cuisine_type, last_updated, visit_count
            FROM restaurant_database
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        nearby_restaurants = []
        
        for row in rows:
            name, address, lat, lon, gf_options, dedicated_kitchen, staff_training, rating, price_range, cuisine, last_updated, visit_count = row
            
            # Calculate distance
            distance = self._calculate_distance(latitude, longitude, lat, lon)
            
            if distance <= radius_km:
                restaurant_data = {
                    'name': name,
                    'address': address,
                    'latitude': lat,
                    'longitude': lon,
                    'gluten_free_options': bool(gf_options),
                    'dedicated_kitchen': bool(dedicated_kitchen),
                    'staff_training': staff_training,
                    'user_rating': rating,
                    'price_range': price_range,
                    'cuisine_type': cuisine,
                    'last_updated': last_updated,
                    'visit_count': visit_count,
                    'distance_km': distance
                }
                
                nearby_restaurants.append(restaurant_data)
        
        # Sort by distance
        nearby_restaurants.sort(key=lambda x: x['distance_km'])
        
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
    
    def cleanup_expired_cache(self) -> int:
        """Clean up expired cache items"""
        expired_keys = []
        current_time = datetime.now()
        
        for key, cache_item in self.cache_items.items():
            if current_time - cache_item.timestamp > timedelta(seconds=cache_item.ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_cache_item(key)
        
        return len(expired_keys)
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_items = len(self.cache_items)
        
        type_counts = {}
        for cache_item in self.cache_items.values():
            type_counts[cache_item.data_type] = type_counts.get(cache_item.data_type, 0) + 1
        
        return {
            'total_items': total_items,
            'type_counts': type_counts,
            'device_id': self.device_id,
            'database_size': self._get_database_size()
        }
    
    def _get_database_size(self) -> int:
        """Get database file size"""
        import os
        try:
            return os.path.getsize(self.cache_db_path)
        except OSError:
            return 0
    
    def export_cache_data(self, data_type: Optional[str] = None) -> Dict[str, Any]:
        """Export cache data"""
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'device_id': self.device_id,
            'data_type': data_type,
            'items': []
        }
        
        for cache_item in self.cache_items.values():
            if data_type is None or cache_item.data_type == data_type:
                export_data['items'].append({
                    'key': cache_item.key,
                    'data': cache_item.data,
                    'data_type': cache_item.data_type,
                    'timestamp': cache_item.timestamp.isoformat(),
                    'ttl': cache_item.ttl,
                    'checksum': cache_item.checksum,
                    'sync_status': cache_item.sync_status
                })
        
        return export_data
    
    def import_cache_data(self, import_data: Dict[str, Any]) -> int:
        """Import cache data"""
        imported_count = 0
        
        for item_data in import_data.get('items', []):
            try:
                key = item_data['key']
                data = item_data['data']
                data_type = item_data['data_type']
                ttl = item_data.get('ttl', 86400)
                
                if self.cache_item(key, data, data_type, ttl):
                    imported_count += 1
                    
            except Exception as e:
                handle_error(
                    e, ErrorCategory.DATABASE, ErrorSeverity.LOW,
                    context={'operation': 'import_cache_item', 'key': item_data.get('key', 'unknown')}
                )
        
        return imported_count


# Global offline cache service instance
_offline_cache_service = None


def get_offline_cache_service() -> OfflineCacheService:
    """Get global offline cache service"""
    global _offline_cache_service
    if _offline_cache_service is None:
        _offline_cache_service = OfflineCacheService()
    return _offline_cache_service
