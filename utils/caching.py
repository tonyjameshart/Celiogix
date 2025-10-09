#!/usr/bin/env python3
"""
Caching utilities for performance optimization
"""

import time
import json
import sqlite3
from typing import Any, Dict, List, Optional, Callable, Union
from functools import wraps
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    timestamp: float
    ttl: float  # Time to live in seconds
    access_count: int = 0
    last_accessed: float = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return time.time() - self.timestamp > self.ttl
    
    def touch(self):
        """Update access information"""
        self.access_count += 1
        self.last_accessed = time.time()


class MemoryCache:
    """In-memory cache with TTL and size limits"""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 300):
        """
        Initialize memory cache
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default time to live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        if entry.is_expired():
            self.remove(key)
            return None
        
        # Update access information
        entry.touch()
        self._update_access_order(key)
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        # Remove from access order if already exists
        if key in self.cache:
            self._remove_from_access_order(key)
        
        # Create new entry
        entry = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl=ttl,
            access_count=0,
            last_accessed=time.time()
        )
        
        self.cache[key] = entry
        self.access_order.append(key)
        
        # Enforce size limit
        if len(self.cache) > self.max_size:
            self._evict_lru()
    
    def remove(self, key: str) -> bool:
        """
        Remove key from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key was removed, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            self._remove_from_access_order(key)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.access_order.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries
        
        Returns:
            Number of entries removed
        """
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]
        
        for key in expired_keys:
            self.remove(key)
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        total_accesses = sum(entry.access_count for entry in self.cache.values())
        avg_accesses = total_accesses / total_entries if total_entries > 0 else 0
        
        return {
            'total_entries': total_entries,
            'max_size': self.max_size,
            'total_accesses': total_accesses,
            'average_accesses': avg_accesses,
            'memory_usage': sum(len(str(entry.value)) for entry in self.cache.values())
        }
    
    def _update_access_order(self, key: str) -> None:
        """Update access order for LRU tracking"""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def _remove_from_access_order(self, key: str) -> None:
        """Remove key from access order"""
        if key in self.access_order:
            self.access_order.remove(key)
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if self.access_order:
            lru_key = self.access_order[0]
            self.remove(lru_key)


class DatabaseCache:
    """Database-backed cache for persistent caching"""
    
    def __init__(self, db_path: str = "data/cache.db", default_ttl: float = 3600):
        """
        Initialize database cache
        
        Args:
            db_path: Path to cache database
            default_ttl: Default time to live in seconds
        """
        self.db_path = db_path
        self.default_ttl = default_ttl
        self._init_database()
    
    def _init_database(self):
        """Initialize cache database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                timestamp REAL NOT NULL,
                ttl REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                last_accessed REAL DEFAULT 0
            )
        """)
        
        # Create index for cleanup
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON cache_entries(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from database cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT value, timestamp, ttl FROM cache_entries WHERE key = ?
        """, (key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        value_str, timestamp, ttl = row
        
        # Check if expired
        if time.time() - timestamp > ttl:
            self.remove(key)
            return None
        
        # Update access information
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cache_entries 
            SET access_count = access_count + 1, last_accessed = ?
            WHERE key = ?
        """, (time.time(), key))
        conn.commit()
        conn.close()
        
        # Deserialize value
        try:
            return json.loads(value_str)
        except (json.JSONDecodeError, TypeError):
            return value_str
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in database cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        # Serialize value
        try:
            value_str = json.dumps(value)
        except (TypeError, ValueError):
            value_str = str(value)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO cache_entries 
            (key, value, timestamp, ttl, access_count, last_accessed)
            VALUES (?, ?, ?, ?, 0, ?)
        """, (key, value_str, time.time(), ttl, time.time()))
        
        conn.commit()
        conn.close()
    
    def remove(self, key: str) -> bool:
        """Remove key from database cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
        affected = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return affected
    
    def clear(self) -> None:
        """Clear all cache entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM cache_entries")
        
        conn.commit()
        conn.close()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        current_time = time.time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM cache_entries 
            WHERE timestamp + ttl < ?
        """, (current_time,))
        
        affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM cache_entries")
        total_entries = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(access_count) FROM cache_entries")
        total_accesses = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT AVG(access_count) FROM cache_entries")
        avg_accesses = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_entries': total_entries,
            'total_accesses': total_accesses,
            'average_accesses': avg_accesses,
            'database_size': self._get_database_size()
        }
    
    def _get_database_size(self) -> int:
        """Get database file size"""
        import os
        try:
            return os.path.getsize(self.db_path)
        except OSError:
            return 0


class CacheManager:
    """Centralized cache management"""
    
    def __init__(self):
        self.memory_cache = MemoryCache(max_size=1000, default_ttl=300)
        self.database_cache = DatabaseCache(default_ttl=3600)
        self._cleanup_timer = None
        self._start_cleanup_timer()
    
    def get(self, key: str, use_database: bool = False) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            use_database: Whether to use database cache
            
        Returns:
            Cached value or None
        """
        if use_database:
            return self.database_cache.get(key)
        else:
            return self.memory_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None, use_database: bool = False) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            use_database: Whether to use database cache
        """
        if use_database:
            self.database_cache.set(key, value, ttl)
        else:
            self.memory_cache.set(key, value, ttl)
    
    def remove(self, key: str, use_database: bool = False) -> bool:
        """Remove key from cache"""
        if use_database:
            return self.database_cache.remove(key)
        else:
            return self.memory_cache.remove(key)
    
    def clear(self, use_database: bool = False) -> None:
        """Clear cache"""
        if use_database:
            self.database_cache.clear()
        else:
            self.memory_cache.clear()
    
    def get_stats(self, use_database: bool = False) -> Dict[str, Any]:
        """Get cache statistics"""
        if use_database:
            return self.database_cache.get_stats()
        else:
            return self.memory_cache.get_stats()
    
    def _start_cleanup_timer(self):
        """Start periodic cleanup timer"""
        from PySide6.QtCore import QTimer
        
        self._cleanup_timer = QTimer()
        self._cleanup_timer.timeout.connect(self._cleanup_expired)
        self._cleanup_timer.start(300000)  # Cleanup every 5 minutes
    
    def _cleanup_expired(self):
        """Clean up expired entries"""
        memory_removed = self.memory_cache.cleanup_expired()
        db_removed = self.database_cache.cleanup_expired()
        
        if memory_removed > 0 or db_removed > 0:
            print(f"Cache cleanup: removed {memory_removed} memory entries, {db_removed} database entries")


def cached(ttl: float = 300, use_database: bool = False, key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        use_database: Whether to use database cache
        key_prefix: Prefix for cache keys
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = "_".join(key_parts)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key, use_database)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl, use_database)
            
            return result
        
        return wrapper
    return decorator


def lazy_load(loader_func: Callable, cache_key: str, ttl: float = 3600, use_database: bool = True):
    """
    Lazy load data with caching
    
    Args:
        loader_func: Function to load data
        cache_key: Cache key for the data
        ttl: Time to live in seconds
        use_database: Whether to use database cache
        
    Returns:
        Lazy loader function
    """
    def lazy_loader(*args, **kwargs):
        # Try to get from cache first
        cached_data = cache_manager.get(cache_key, use_database)
        if cached_data is not None:
            return cached_data
        
        # Load data using loader function
        data = loader_func(*args, **kwargs)
        
        # Cache the data
        cache_manager.set(cache_key, data, ttl, use_database)
        
        return data
    
    return lazy_loader


# Global cache manager instance
cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get global cache manager"""
    return cache_manager
