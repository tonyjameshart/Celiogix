# path: services/import_service.py
"""
Import Service for PySide6 Application

Provides comprehensive import functionality for all application data.
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from PySide6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PySide6.QtCore import QThread, Signal, QObject
import pandas as pd
from pathlib import Path


class ImportWorker(QObject):
    """Worker thread for import operations"""
    
    progress = Signal(int)
    finished = Signal(bool, str)
    status = Signal(str)
    
    def __init__(self, import_type: str, file_path: str, target_panel: str, options: Dict[str, Any] = None):
        super().__init__()
        self.import_type = import_type
        self.file_path = file_path
        self.target_panel = target_panel
        self.options = options or {}
    
    def run(self):
        """Run import operation"""
        try:
            self.status.emit(f"Starting {self.import_type} import...")
            
            if self.import_type == "csv":
                self.import_csv()
            elif self.import_type == "json":
                self.import_json()
            elif self.import_type == "excel":
                self.import_excel()
            else:
                raise ValueError(f"Unsupported import type: {self.import_type}")
            
            self.finished.emit(True, "Import completed successfully!")
            
        except Exception as e:
            self.finished.emit(False, f"Import failed: {str(e)}")
    
    def import_csv(self):
        """Import CSV file"""
        try:
            import csv
            from pathlib import Path
            
            self.progress.emit("Reading CSV file...", 20)
            
            with open(self.file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
            
            self.progress.emit("Processing CSV data...", 50)
            
            # Process the data based on panel type
            if self.panel_type == 'pantry':
                self._process_pantry_data(data)
            elif self.panel_type == 'health_log':
                self._process_health_data(data)
            elif self.panel_type == 'cookbook':
                self._process_recipe_data(data)
            elif self.panel_type == 'shopping_list':
                self._process_shopping_data(data)
            elif self.panel_type == 'menu':
                self._process_menu_data(data)
            elif self.panel_type == 'calendar':
                self._process_calendar_data(data)
            else:
                raise ValueError(f"Unsupported panel type: {self.panel_type}")
            
            self.progress.emit("CSV import completed", 100)
            
        except Exception as e:
            raise Exception(f"CSV import failed: {str(e)}")
    
    def import_json(self):
        """Import JSON file"""
        try:
            import json
            from pathlib import Path
            
            self.progress.emit("Reading JSON file...", 20)
            
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            self.progress.emit("Processing JSON data...", 50)
            
            # Handle both single objects and arrays
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                # If it's a dict, try to find the data array
                items = data.get('data', data.get('items', [data]))
            else:
                raise ValueError("Invalid JSON format")
            
            # Process the data based on panel type
            if self.panel_type == 'pantry':
                self._process_pantry_data(items)
            elif self.panel_type == 'health_log':
                self._process_health_data(items)
            elif self.panel_type == 'cookbook':
                self._process_recipe_data(items)
            elif self.panel_type == 'shopping_list':
                self._process_shopping_data(items)
            elif self.panel_type == 'menu':
                self._process_menu_data(items)
            elif self.panel_type == 'calendar':
                self._process_calendar_data(items)
            else:
                raise ValueError(f"Unsupported panel type: {self.panel_type}")
            
            self.progress.emit("JSON import completed", 100)
            
        except Exception as e:
            raise Exception(f"JSON import failed: {str(e)}")
    
    def import_excel(self):
        """Import Excel file"""
        try:
            import pandas as pd
            
            self.progress.emit("Reading Excel file...", 20)
            
            # Read Excel file
            df = pd.read_excel(self.file_path)
            data = df.to_dict('records')
            
            self.progress.emit("Processing Excel data...", 50)
            
            # Process the data based on panel type
            if self.panel_type == 'pantry':
                self._process_pantry_data(data)
            elif self.panel_type == 'health_log':
                self._process_health_data(data)
            elif self.panel_type == 'cookbook':
                self._process_recipe_data(data)
            elif self.panel_type == 'shopping_list':
                self._process_shopping_data(data)
            elif self.panel_type == 'menu':
                self._process_menu_data(data)
            elif self.panel_type == 'calendar':
                self._process_calendar_data(data)
            else:
                raise ValueError(f"Unsupported panel type: {self.panel_type}")
            
            self.progress.emit("Excel import completed", 100)
            
        except Exception as e:
            raise Exception(f"Excel import failed: {str(e)}")
    
    def _process_pantry_data(self, data):
        """Process pantry data"""
        from utils.db import get_connection
        conn = get_connection()
        
        for item in data:
            # Map common column names
            name = item.get('name', item.get('item_name', item.get('Name', '')))
            quantity = item.get('quantity', item.get('Quantity', '1'))
            unit = item.get('unit', item.get('Unit', ''))
            category = item.get('category', item.get('Category', 'Other'))
            expiry_date = item.get('expiry_date', item.get('Expiry Date', ''))
            gluten_free = item.get('gluten_free', item.get('Gluten Free', 'Yes'))
            notes = item.get('notes', item.get('Notes', ''))
            
            if name:
                conn.execute("""
                    INSERT OR REPLACE INTO pantry (name, quantity, unit, category, expiration, gf_flag, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, quantity, unit, category, expiry_date, gluten_free, notes))
        
        conn.commit()
    
    def _process_health_data(self, data):
        """Process health log data"""
        from utils.db import get_connection
        conn = get_connection()
        
        for item in data:
            # Map common column names
            date = item.get('date', item.get('Date', ''))
            time = item.get('time', item.get('Time', ''))
            meal = item.get('meal', item.get('Meal', ''))
            items = item.get('items', item.get('Items', ''))
            symptoms = item.get('symptoms', item.get('Symptoms', ''))
            notes = item.get('notes', item.get('Notes', ''))
            
            if date:
                conn.execute("""
                    INSERT OR REPLACE INTO health_log (date, time, meal, items, symptoms, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (date, time, meal, items, symptoms, notes))
        
        conn.commit()
    
    def _process_recipe_data(self, data):
        """Process recipe data"""
        from utils.db import get_connection
        conn = get_connection()
        
        for item in data:
            # Map common column names
            title = item.get('title', item.get('name', item.get('Title', '')))
            ingredients = item.get('ingredients', item.get('Ingredients', ''))
            instructions = item.get('instructions', item.get('Instructions', ''))
            category = item.get('category', item.get('Category', 'Other'))
            prep_time = item.get('prep_time', item.get('Prep Time', ''))
            cook_time = item.get('cook_time', item.get('Cook Time', ''))
            servings = item.get('servings', item.get('Servings', 4))
            
            if title:
                conn.execute("""
                    INSERT OR REPLACE INTO recipes (title, ingredients, instructions, category, prep_time, cook_time, servings)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (title, ingredients, instructions, category, prep_time, cook_time, servings))
        
        conn.commit()
    
    def _process_shopping_data(self, data):
        """Process shopping list data"""
        from utils.db import get_connection
        conn = get_connection()
        
        for item in data:
            # Map common column names
            item_name = item.get('item', item.get('item_name', item.get('Item', '')))
            quantity = item.get('quantity', item.get('Quantity', ''))
            category = item.get('category', item.get('Category', 'Other'))
            store = item.get('store', item.get('Store', ''))
            priority = item.get('priority', item.get('Priority', 'Medium'))
            notes = item.get('notes', item.get('Notes', ''))
            
            if item_name:
                conn.execute("""
                    INSERT OR REPLACE INTO shopping_list (item, item_name, quantity, category, store, priority, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (item_name, item_name, quantity, category, store, priority, notes))
        
        conn.commit()
    
    def _process_menu_data(self, data):
        """Process menu data"""
        from utils.db import get_connection
        conn = get_connection()
        
        for item in data:
            # Map common column names
            date = item.get('date', item.get('Date', ''))
            meal = item.get('meal', item.get('Meal', ''))
            title = item.get('title', item.get('recipe', item.get('Title', '')))
            notes = item.get('notes', item.get('Notes', ''))
            
            if date and meal:
                conn.execute("""
                    INSERT OR REPLACE INTO menu_plan (date, meal, title, notes)
                    VALUES (?, ?, ?, ?)
                """, (date, meal, title, notes))
        
        conn.commit()
    
    def _process_calendar_data(self, data):
        """Process calendar data"""
        from utils.db import get_connection
        conn = get_connection()
        
        for item in data:
            # Map common column names
            name = item.get('name', item.get('event', item.get('Name', '')))
            date = item.get('date', item.get('Date', ''))
            time = item.get('time', item.get('Time', ''))
            event_type = item.get('type', item.get('event_type', item.get('Type', 'Personal')))
            description = item.get('description', item.get('Description', ''))
            
            if name and date:
                conn.execute("""
                    INSERT OR REPLACE INTO calendar_events (name, date, time, event_type, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, date, time, event_type, description))
        
        conn.commit()


class ImportService:
    """Centralized import service for all application data"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'excel']
        self.panel_mappings = {
            'pantry': self._import_pantry_data,
            'health_log': self._import_health_data,
            'cookbook': self._import_recipe_data,
            'shopping_list': self._import_shopping_data,
            'menu': self._import_menu_data,
            'calendar': self._import_calendar_data
        }
    
    def show_import_dialog(self, parent, panel_type: str) -> Optional[str]:
        """Show import file selection dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            f"Import {panel_type.replace('_', ' ').title()} Data",
            "",
            "All Supported Files (*.csv *.json *.xlsx *.xls);;CSV Files (*.csv);;JSON Files (*.json);;Excel Files (*.xlsx *.xls)"
        )
        return file_path if file_path else None
    
    def import_data(self, parent, panel_type: str, file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Import data from file for specified panel"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                return self._import_csv_data(parent, panel_type, file_path, options)
            elif file_ext in ['.xlsx', '.xls']:
                return self._import_excel_data(parent, panel_type, file_path, options)
            elif file_ext == '.json':
                return self._import_json_data(parent, panel_type, file_path, options)
            else:
                return {
                    'success': False,
                    'message': f'Unsupported file format: {file_ext}',
                    'imported_count': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Import failed: {str(e)}',
                'imported_count': 0
            }
    
    def _import_csv_data(self, parent, panel_type: str, file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Import CSV data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
            
            if panel_type in self.panel_mappings:
                return self.panel_mappings[panel_type](data, options)
            else:
                return {
                    'success': False,
                    'message': f'Unknown panel type: {panel_type}',
                    'imported_count': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'CSV import failed: {str(e)}',
                'imported_count': 0
            }
    
    def _import_excel_data(self, parent, panel_type: str, file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Import Excel data"""
        try:
            df = pd.read_excel(file_path)
            data = df.to_dict('records')
            
            if panel_type in self.panel_mappings:
                return self.panel_mappings[panel_type](data, options)
            else:
                return {
                    'success': False,
                    'message': f'Unknown panel type: {panel_type}',
                    'imported_count': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Excel import failed: {str(e)}',
                'imported_count': 0
            }
    
    def _import_json_data(self, parent, panel_type: str, file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Import JSON data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if panel_type in self.panel_mappings:
                return self.panel_mappings[panel_type](data, options)
            else:
                return {
                    'success': False,
                    'message': f'Unknown panel type: {panel_type}',
                    'imported_count': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'JSON import failed: {str(e)}',
                'imported_count': 0
            }
    
    def _import_pantry_data(self, data: List[Dict], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Import pantry data"""
        try:
            from utils.db import get_connection
            conn = get_connection()
            imported_count = 0
            
            for item in data:
                # Map CSV columns to database columns
                name = item.get('name', item.get('item_name', item.get('Name', '')))
                quantity = item.get('quantity', item.get('Quantity', '1'))
                unit = item.get('unit', item.get('Unit', ''))
                category = item.get('category', item.get('Category', 'Other'))
                expiry_date = item.get('expiry_date', item.get('Expiry Date', ''))
                gluten_free = item.get('gluten_free', item.get('Gluten Free', 'Yes'))
                notes = item.get('notes', item.get('Notes', ''))
                
                if name:
                    conn.execute("""
                        INSERT OR REPLACE INTO pantry_items 
                        (name, quantity, unit, category, expiry_date, gluten_free, notes, created_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, quantity, unit, category, expiry_date, gluten_free, notes, datetime.now().isoformat()))
                    imported_count += 1
            
            conn.commit()
            return {
                'success': True,
                'message': f'Successfully imported {imported_count} pantry items',
                'imported_count': imported_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Pantry import failed: {str(e)}',
                'imported_count': 0
            }
    
    def _import_health_data(self, data: List[Dict], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Import health log data"""
        try:
            from utils.db import get_connection
            conn = get_connection()
            imported_count = 0
            
            for entry in data:
                # Map CSV columns to database columns
                date = entry.get('date', entry.get('Date', ''))
                time = entry.get('time', entry.get('Time', ''))
                meal = entry.get('meal', entry.get('Meal', ''))
                items = entry.get('items', entry.get('Items', entry.get('items_consumed', '')))
                symptoms = entry.get('symptoms', entry.get('Symptoms', ''))
                stool = entry.get('stool', entry.get('Bristol Scale', entry.get('bristol_scale', '')))
                hydration = entry.get('hydration', entry.get('Hydration', entry.get('hydration_liters', '0')))
                fiber = entry.get('fiber', entry.get('Fiber', entry.get('fiber_grams', '0')))
                mood = entry.get('mood', entry.get('Mood', ''))
                energy = entry.get('energy', entry.get('Energy', entry.get('energy_level', '5')))
                notes = entry.get('notes', entry.get('Notes', ''))
                
                if date:
                    conn.execute("""
                        INSERT OR REPLACE INTO health_log 
                        (date, time, meal, items, symptoms, stool, hydration_liters, fiber_grams, mood, energy_level, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (date, time, meal, items, symptoms, stool, hydration, fiber, mood, energy, notes))
                    imported_count += 1
            
            conn.commit()
            return {
                'success': True,
                'message': f'Successfully imported {imported_count} health entries',
                'imported_count': imported_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Health data import failed: {str(e)}',
                'imported_count': 0
            }
    
    def _import_recipe_data(self, data: List[Dict], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Import recipe data"""
        try:
            from utils.db import get_connection
            conn = get_connection()
            imported_count = 0
            
            for recipe in data:
                title = recipe.get('title', recipe.get('Title', recipe.get('name', '')))
                description = recipe.get('description', recipe.get('Description', ''))
                prep_time = recipe.get('prep_time', recipe.get('Prep Time', '0'))
                cook_time = recipe.get('cook_time', recipe.get('Cook Time', '0'))
                servings = recipe.get('servings', recipe.get('Servings', '1'))
                difficulty = recipe.get('difficulty', recipe.get('Difficulty', 'Medium'))
                cuisine_type = recipe.get('cuisine', recipe.get('Cuisine', ''))
                ingredients = recipe.get('ingredients', recipe.get('Ingredients', ''))
                instructions = recipe.get('instructions', recipe.get('Instructions', ''))
                notes = recipe.get('notes', recipe.get('Notes', ''))
                gluten_free = recipe.get('gluten_free', recipe.get('Gluten Free', 'Yes'))
                
                if title:
                    conn.execute("""
                        INSERT OR REPLACE INTO recipes 
                        (title, description, prep_time_minutes, cook_time_minutes, servings, 
                         difficulty, cuisine_type, ingredients, instructions, notes, gluten_free, created_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (title, description, prep_time, cook_time, servings, difficulty, 
                          cuisine_type, ingredients, instructions, notes, gluten_free, datetime.now().isoformat()))
                    imported_count += 1
            
            conn.commit()
            return {
                'success': True,
                'message': f'Successfully imported {imported_count} recipes',
                'imported_count': imported_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Recipe import failed: {str(e)}',
                'imported_count': 0
            }
    
    def _import_shopping_data(self, data: List[Dict], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Import shopping list data"""
        try:
            from utils.db import get_connection
            conn = get_connection()
            imported_count = 0
            
            for item in data:
                name = item.get('item', item.get('Item', item.get('name', '')))
                quantity = item.get('quantity', item.get('Quantity', '1'))
                category = item.get('category', item.get('Category', 'Other'))
                store = item.get('store', item.get('Store', 'Grocery Store'))
                priority = item.get('priority', item.get('Priority', 'Medium'))
                notes = item.get('notes', item.get('Notes', ''))
                
                if name:
                    conn.execute("""
                        INSERT OR REPLACE INTO shopping_list 
                        (item, quantity, category, store, priority, notes, created_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (name, quantity, category, store, priority, notes, datetime.now().isoformat()))
                    imported_count += 1
            
            conn.commit()
            return {
                'success': True,
                'message': f'Successfully imported {imported_count} shopping items',
                'imported_count': imported_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Shopping list import failed: {str(e)}',
                'imported_count': 0
            }
    
    def _import_menu_data(self, data: List[Dict], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Import menu planning data"""
        try:
            from utils.db import get_connection
            conn = get_connection()
            imported_count = 0
            
            for meal in data:
                date = meal.get('date', meal.get('Date', ''))
                meal_type = meal.get('meal_type', meal.get('Meal Type', meal.get('meal', '')))
                recipe = meal.get('recipe', meal.get('Recipe', meal.get('title', '')))
                notes = meal.get('notes', meal.get('Notes', ''))
                time = meal.get('time', meal.get('Time', '12:00'))
                
                if date and recipe:
                    conn.execute("""
                        INSERT OR REPLACE INTO menu_plan 
                        (date, meal, title, notes, time)
                        VALUES (?, ?, ?, ?, ?)
                    """, (date, meal_type, recipe, notes, time))
                    imported_count += 1
            
            conn.commit()
            return {
                'success': True,
                'message': f'Successfully imported {imported_count} menu items',
                'imported_count': imported_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Menu import failed: {str(e)}',
                'imported_count': 0
            }
    
    def _import_calendar_data(self, data: List[Dict], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Import calendar event data"""
        try:
            from utils.db import get_connection
            conn = get_connection()
            imported_count = 0
            
            for event in data:
                name = event.get('name', event.get('Name', event.get('title', '')))
                date = event.get('date', event.get('Date', ''))
                time = event.get('time', event.get('Time', ''))
                event_type = event.get('type', event.get('Type', event.get('event_type', 'Other')))
                priority = event.get('priority', event.get('Priority', 'Medium'))
                description = event.get('description', event.get('Description', event.get('notes', '')))
                reminder = event.get('reminder', event.get('Reminder', 'None'))
                
                if name and date:
                    conn.execute("""
                        INSERT OR REPLACE INTO calendar_events 
                        (name, date, time, event_type, priority, description, reminder, created_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, date, time, event_type, priority, description, reminder, datetime.now().isoformat()))
                    imported_count += 1
            
            conn.commit()
            return {
                'success': True,
                'message': f'Successfully imported {imported_count} calendar events',
                'imported_count': imported_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Calendar import failed: {str(e)}',
                'imported_count': 0
            }


# Create global instance
import_service = ImportService()
