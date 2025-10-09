#!/usr/bin/env python3
"""
Secure database operations with encryption support
"""

import sqlite3
from typing import Dict, List, Any, Optional, Union
from contextlib import contextmanager
from .db import get_connection, safe_commit, execute_with_retry
from .encryption import get_health_encryption, get_general_encryption


class SecureDatabase:
    """Database operations with automatic encryption/decryption"""
    
    def __init__(self, encryption_password: Optional[str] = None):
        self.health_encryption = get_health_encryption(encryption_password)
        self.general_encryption = get_general_encryption(encryption_password)
    
    @contextmanager
    def get_secure_connection(self):
        """Get secure database connection with encryption support"""
        conn = get_connection()
        try:
            yield conn
        finally:
            conn.close()
    
    def insert_health_entry(self, entry_data: Dict[str, Any]) -> int:
        """
        Insert encrypted health entry
        
        Args:
            entry_data: Health entry data dictionary
            
        Returns:
            ID of inserted entry
        """
        # Encrypt sensitive data
        encrypted_entry = self.health_encryption.encrypt_health_entry(entry_data)
        
        with self.get_secure_connection() as conn:
            cursor = conn.cursor()
            
            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    time TEXT,
                    meal_type TEXT,
                    symptoms TEXT,
                    bristol_scale INTEGER,
                    hydration_liters REAL,
                    fiber_grams REAL,
                    mood TEXT,
                    energy_level INTEGER,
                    notes TEXT,
                    risk_level TEXT,
                    severity INTEGER,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                INSERT INTO health_log (
                    date, time, meal_type, symptoms, bristol_scale,
                    hydration_liters, fiber_grams, mood, energy_level,
                    notes, risk_level, severity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                encrypted_entry.get('date', ''),
                encrypted_entry.get('time', ''),
                encrypted_entry.get('meal_type', ''),
                encrypted_entry.get('symptoms', ''),
                encrypted_entry.get('bristol_scale'),
                encrypted_entry.get('hydration_liters'),
                encrypted_entry.get('fiber_grams'),
                encrypted_entry.get('mood', ''),
                encrypted_entry.get('energy_level'),
                encrypted_entry.get('notes', ''),
                encrypted_entry.get('risk_level', ''),
                encrypted_entry.get('severity')
            ))
            
            entry_id = cursor.lastrowid
            safe_commit(conn)
            return entry_id
    
    def get_health_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Get and decrypt health entry
        
        Args:
            entry_id: ID of health entry
            
        Returns:
            Decrypted health entry or None
        """
        with self.get_secure_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM health_log WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                entry = dict(zip(columns, row))
                return self.health_encryption.decrypt_health_entry(entry)
            
            return None
    
    def get_health_entries(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get and decrypt health entries
        
        Args:
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            
        Returns:
            List of decrypted health entries
        """
        with self.get_secure_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM health_log ORDER BY date DESC, time DESC"
            params = []
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            columns = [description[0] for description in cursor.description]
            entries = []
            
            for row in cursor.fetchall():
                entry = dict(zip(columns, row))
                decrypted_entry = self.health_encryption.decrypt_health_entry(entry)
                entries.append(decrypted_entry)
            
            return entries
    
    def update_health_entry(self, entry_id: int, entry_data: Dict[str, Any]) -> bool:
        """
        Update encrypted health entry
        
        Args:
            entry_id: ID of health entry to update
            entry_data: Updated health entry data
            
        Returns:
            True if update successful
        """
        # Encrypt sensitive data
        encrypted_entry = self.health_encryption.encrypt_health_entry(entry_data)
        
        with self.get_secure_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE health_log SET
                    date = ?, time = ?, meal_type = ?, symptoms = ?,
                    bristol_scale = ?, hydration_liters = ?, fiber_grams = ?,
                    mood = ?, energy_level = ?, notes = ?, risk_level = ?,
                    severity = ?
                WHERE id = ?
            """, (
                encrypted_entry.get('date', ''),
                encrypted_entry.get('time', ''),
                encrypted_entry.get('meal_type', ''),
                encrypted_entry.get('symptoms', ''),
                encrypted_entry.get('bristol_scale'),
                encrypted_entry.get('hydration_liters'),
                encrypted_entry.get('fiber_grams'),
                encrypted_entry.get('mood', ''),
                encrypted_entry.get('energy_level'),
                encrypted_entry.get('notes', ''),
                encrypted_entry.get('risk_level', ''),
                encrypted_entry.get('severity'),
                entry_id
            ))
            
            safe_commit(conn)
            return cursor.rowcount > 0
    
    def delete_health_entry(self, entry_id: int) -> bool:
        """
        Delete health entry
        
        Args:
            entry_id: ID of health entry to delete
            
        Returns:
            True if deletion successful
        """
        with self.get_secure_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM health_log WHERE id = ?", (entry_id,))
            safe_commit(conn)
            return cursor.rowcount > 0
    
    def insert_recipe_with_notes(self, recipe_data: Dict[str, Any]) -> int:
        """
        Insert recipe with encrypted notes
        
        Args:
            recipe_data: Recipe data dictionary
            
        Returns:
            ID of inserted recipe
        """
        # Encrypt sensitive recipe data
        encrypted_recipe = self.health_encryption.encrypt_recipe_notes(recipe_data)
        
        with self.get_secure_connection() as conn:
            cursor = conn.cursor()
            
            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    description TEXT,
                    ingredients TEXT,
                    instructions TEXT,
                    prep_time INTEGER,
                    cook_time INTEGER,
                    servings INTEGER,
                    difficulty TEXT,
                    image_path TEXT,
                    is_favorite BOOLEAN DEFAULT 0,
                    notes TEXT,
                    allergy_warnings TEXT,
                    dietary_restrictions TEXT,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    modified_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            """)
            
            cursor.execute("""
                INSERT INTO recipes (
                    name, category_id, description, ingredients, instructions,
                    prep_time, cook_time, servings, difficulty, image_path,
                    is_favorite, notes, allergy_warnings, dietary_restrictions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                encrypted_recipe.get('name', ''),
                encrypted_recipe.get('category_id'),
                encrypted_recipe.get('description', ''),
                encrypted_recipe.get('ingredients', ''),
                encrypted_recipe.get('instructions', ''),
                encrypted_recipe.get('prep_time', 0),
                encrypted_recipe.get('cook_time', 0),
                encrypted_recipe.get('servings', 1),
                encrypted_recipe.get('difficulty', 'Easy'),
                encrypted_recipe.get('image_path', ''),
                encrypted_recipe.get('is_favorite', False),
                encrypted_recipe.get('notes', ''),
                encrypted_recipe.get('allergy_warnings', ''),
                encrypted_recipe.get('dietary_restrictions', '')
            ))
            
            recipe_id = cursor.lastrowid
            safe_commit(conn)
            return recipe_id
    
    def get_recipe_with_notes(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """
        Get and decrypt recipe with notes
        
        Args:
            recipe_id: ID of recipe
            
        Returns:
            Decrypted recipe or None
        """
        with self.get_secure_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                recipe = dict(zip(columns, row))
                return self.health_encryption.decrypt_recipe_notes(recipe)
            
            return None
    
    def encrypt_database_backup(self, backup_path: str, output_path: Optional[str] = None) -> str:
        """
        Create encrypted database backup
        
        Args:
            backup_path: Path to database backup
            output_path: Optional output path for encrypted backup
            
        Returns:
            Path to encrypted backup
        """
        if not output_path:
            output_path = backup_path + '.enc'
        
        return self.general_encryption.encrypt_file(backup_path, output_path)
    
    def decrypt_database_backup(self, encrypted_backup_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt database backup
        
        Args:
            encrypted_backup_path: Path to encrypted backup
            output_path: Optional output path for decrypted backup
            
        Returns:
            Path to decrypted backup
        """
        if not output_path:
            if encrypted_backup_path.endswith('.enc'):
                output_path = encrypted_backup_path[:-4]
            else:
                output_path = encrypted_backup_path + '.dec'
        
        return self.general_encryption.decrypt_file(encrypted_backup_path, output_path)
    
    def set_encryption_password(self, password: str):
        """
        Set new encryption password
        
        Args:
            password: New encryption password
        """
        self.health_encryption = get_health_encryption(password)
        self.general_encryption = get_general_encryption(password)


# Global secure database instance
_secure_db = None


def get_secure_database(encryption_password: Optional[str] = None) -> SecureDatabase:
    """Get global secure database instance"""
    global _secure_db
    if _secure_db is None:
        _secure_db = SecureDatabase(encryption_password)
    return _secure_db
