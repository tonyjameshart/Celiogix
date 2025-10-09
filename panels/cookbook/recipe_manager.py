# path: panels/cookbook/recipe_manager.py
"""
Recipe management and database operations
"""

import sqlite3
from typing import Dict, List, Optional, Any
from utils.db import get_connection


class RecipeManager:
    """Manages recipe data and database operations"""
    
    def __init__(self):
        self.conn = get_connection()
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure required tables exist"""
        cursor = self.conn.cursor()
        
        # Create recipes table
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
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                modified_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        
        # Create categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                description TEXT,
                color TEXT,
                icon TEXT,
                sort_order INTEGER,
                FOREIGN KEY (parent_id) REFERENCES categories (id)
            )
        """)
        
        self.conn.commit()
    
    def load_recipes(self) -> List[Dict[str, Any]]:
        """Load all recipes from database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.*, c.name as category_name 
            FROM recipes r 
            LEFT JOIN categories c ON r.category_id = c.id 
            ORDER BY r.name
        """)
        
        columns = [description[0] for description in cursor.description]
        recipes = []
        
        for row in cursor.fetchall():
            recipe = dict(zip(columns, row))
            recipes.append(recipe)
        
        return recipes
    
    def get_recipe(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific recipe by ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.*, c.name as category_name 
            FROM recipes r 
            LEFT JOIN categories c ON r.category_id = c.id 
            WHERE r.id = ?
        """, (recipe_id,))
        
        row = cursor.fetchone()
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        
        return None
    
    def save_recipe(self, recipe_data: Dict[str, Any]) -> int:
        """Save a new recipe"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO recipes (
                name, category_id, description, ingredients, instructions,
                prep_time, cook_time, servings, difficulty, image_path, is_favorite
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            recipe_data.get('name', ''),
            recipe_data.get('category_id'),
            recipe_data.get('description', ''),
            recipe_data.get('ingredients', ''),
            recipe_data.get('instructions', ''),
            recipe_data.get('prep_time', 0),
            recipe_data.get('cook_time', 0),
            recipe_data.get('servings', 1),
            recipe_data.get('difficulty', 'Easy'),
            recipe_data.get('image_path', ''),
            recipe_data.get('is_favorite', False)
        ))
        
        recipe_id = cursor.lastrowid
        self.conn.commit()
        return recipe_id
    
    def update_recipe(self, recipe_id: int, recipe_data: Dict[str, Any]) -> bool:
        """Update an existing recipe"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            UPDATE recipes SET
                name = ?, category_id = ?, description = ?, ingredients = ?,
                instructions = ?, prep_time = ?, cook_time = ?, servings = ?,
                difficulty = ?, image_path = ?, is_favorite = ?,
                modified_date = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            recipe_data.get('name', ''),
            recipe_data.get('category_id'),
            recipe_data.get('description', ''),
            recipe_data.get('ingredients', ''),
            recipe_data.get('instructions', ''),
            recipe_data.get('prep_time', 0),
            recipe_data.get('cook_time', 0),
            recipe_data.get('servings', 1),
            recipe_data.get('difficulty', 'Easy'),
            recipe_data.get('image_path', ''),
            recipe_data.get('is_favorite', False),
            recipe_id
        ))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_filtered_recipes(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get recipes with applied filters"""
        recipes = self.load_recipes()
        
        if not filters:
            return recipes
        
        # Apply filters
        filtered_recipes = recipes
        
        if filters.get('search_text'):
            search_text = filters['search_text'].lower()
            filtered_recipes = [
                r for r in filtered_recipes
                if search_text in r['name'].lower() or
                   search_text in (r['description'] or '').lower() or
                   search_text in (r['ingredients'] or '').lower()
            ]
        
        if filters.get('category_id'):
            filtered_recipes = [
                r for r in filtered_recipes
                if r['category_id'] == filters['category_id']
            ]
        
        if filters.get('favorites_only'):
            filtered_recipes = [
                r for r in filtered_recipes
                if r['is_favorite']
            ]
        
        return filtered_recipes
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM categories 
            ORDER BY sort_order, name
        """)
        
        columns = [description[0] for description in cursor.description]
        categories = []
        
        for row in cursor.fetchall():
            category = dict(zip(columns, row))
            categories.append(category)
        
        return categories
    
    def scrape_recipe_from_web(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape recipe from web URL"""
        try:
            from services.recipe_scraper import RecipeScraper
            scraper = RecipeScraper()
            return scraper.scrape_recipe(url)
        except Exception as e:
            print(f"Error scraping recipe: {e}")
            return None
    
    def toggle_favorite(self, recipe_id: int) -> bool:
        """Toggle favorite status of a recipe"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE recipes 
            SET is_favorite = NOT is_favorite,
                modified_date = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (recipe_id,))
        
        self.conn.commit()
        return cursor.rowcount > 0
