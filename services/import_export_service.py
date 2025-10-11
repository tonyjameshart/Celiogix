#!/usr/bin/env python3
"""
Import/Export Service for CeliacShield Application
Handles bulk import/export operations for all panels
"""

import json
import csv
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from utils.db import get_connection
from utils.recipes import RecipeManager
from services.pantry import PantryService
from utils.shopping_list import ShoppingListManager
from utils.menu_planner import MenuPlanner
from utils.calendar import CalendarManager
from utils.health_log import HealthLogManager


class ImportExportService:
    """Service for handling bulk import/export operations"""
    
    def __init__(self):
        self.db = get_connection()
        self.recipe_manager = RecipeManager()
        self.pantry_service = PantryService()
        self.shopping_manager = ShoppingListManager()
        self.menu_planner = MenuPlanner()
        self.calendar_manager = CalendarManager()
        self.health_log_manager = HealthLogManager()
        
        # Supported formats
        self.supported_formats = {
            'csv': self._export_csv,
            'json': self._export_json,
            'excel': self._export_excel,
            'pdf': self._export_pdf
        }
        
        self.import_formats = {
            'csv': self._import_csv,
            'json': self._import_json,
            'excel': self._import_excel
        }
    
    def export_panel_data(self, panel_name: str, file_path: str, format_type: str = 'csv', 
                         include_metadata: bool = True) -> bool:
        """Export data for a specific panel"""
        try:
            if format_type not in self.supported_formats:
                raise ValueError(f"Unsupported format: {format_type}")
            
            # Get data based on panel
            data = self._get_panel_data(panel_name)
            if not data:
                raise ValueError(f"No data found for panel: {panel_name}")
            
            # Export using the appropriate method
            export_func = self.supported_formats[format_type]
            return export_func(data, file_path, panel_name, include_metadata)
            
        except Exception as e:
            print(f"Error exporting {panel_name} data: {e}")
            return False
    
    def import_panel_data(self, panel_name: str, file_path: str, 
                         overwrite_mode: bool = False) -> Tuple[bool, str]:
        """Import data for a specific panel"""
        try:
            # Determine format from file extension
            format_type = self._get_file_format(file_path)
            if format_type not in self.import_formats:
                return False, f"Unsupported file format: {format_type}"
            
            # Import using the appropriate method
            import_func = self.import_formats[format_type]
            data = import_func(file_path)
            
            if not data:
                return False, "No data found in file"
            
            # Import data into the appropriate panel
            success, message = self._import_to_panel(panel_name, data, overwrite_mode)
            return success, message
            
        except Exception as e:
            return False, f"Error importing {panel_name} data: {e}"
    
    def export_all_data(self, output_dir: str, format_type: str = 'json', 
                       include_metadata: bool = True) -> bool:
        """Export all application data"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            panels = ['cookbook', 'pantry', 'calendar', 'menu_planner', 'health_log', 'shopping_list']
            
            for panel in panels:
                data = self._get_panel_data(panel)
                if data:
                    filename = f"{panel}_export_{timestamp}.{format_type}"
                    file_path = os.path.join(output_dir, filename)
                    
                    export_func = self.supported_formats[format_type]
                    export_func(data, file_path, panel, include_metadata)
            
            # Create summary file
            summary_file = os.path.join(output_dir, f"export_summary_{timestamp}.txt")
            self._create_export_summary(summary_file, panels)
            
            return True
            
        except Exception as e:
            print(f"Error exporting all data: {e}")
            return False
    
    def _get_panel_data(self, panel_name: str) -> List[Dict[str, Any]]:
        """Get data for a specific panel"""
        try:
            if panel_name == 'cookbook':
                return self._get_recipe_data()
            elif panel_name == 'pantry':
                return self._get_pantry_data()
            elif panel_name == 'calendar':
                return self._get_calendar_data()
            elif panel_name == 'menu_planner':
                return self._get_menu_data()
            elif panel_name == 'health_log':
                return self._get_health_data()
            elif panel_name == 'shopping_list':
                return self._get_shopping_data()
            else:
                return []
        except Exception as e:
            print(f"Error getting {panel_name} data: {e}")
            return []
    
    def _get_recipe_data(self) -> List[Dict[str, Any]]:
        """Get recipe data"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, title, description, instructions, prep_time, cook_time,
                       servings, difficulty, category, tags, created_at, updated_at
                FROM recipes ORDER BY title
            """)
            
            recipes = []
            for row in cursor.fetchall():
                recipes.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'instructions': row[3],
                    'prep_time': row[4],
                    'cook_time': row[5],
                    'servings': row[6],
                    'difficulty': row[7],
                    'category': row[8],
                    'tags': row[9],
                    'created_at': row[10],
                    'updated_at': row[11]
                })
            
            # Get ingredients for each recipe
            for recipe in recipes:
                cursor.execute("""
                    SELECT ingredient_name, quantity, unit, notes
                    FROM recipe_ingredients WHERE recipe_id = ?
                    ORDER BY ingredient_name
                """, (recipe['id'],))
                
                ingredients = []
                for ing_row in cursor.fetchall():
                    ingredients.append({
                        'name': ing_row[0],
                        'quantity': ing_row[1],
                        'unit': ing_row[2],
                        'notes': ing_row[3]
                    })
                
                recipe['ingredients'] = ingredients
            
            return recipes
            
        except Exception as e:
            print(f"Error getting recipe data: {e}")
            return []
    
    def _get_pantry_data(self) -> List[Dict[str, Any]]:
        """Get pantry data"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, name, category, quantity, unit, expiration_date,
                       gluten_free, notes, created_at, updated_at
                FROM pantry_items ORDER BY name
            """)
            
            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'quantity': row[3],
                    'unit': row[4],
                    'expiration_date': row[5],
                    'gluten_free': row[6],
                    'notes': row[7],
                    'created_at': row[8],
                    'updated_at': row[9]
                })
            
            return items
            
        except Exception as e:
            print(f"Error getting pantry data: {e}")
            return []
    
    def _get_calendar_data(self) -> List[Dict[str, Any]]:
        """Get calendar data"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, title, description, start_date, end_date, event_type,
                       priority, reminder_minutes, created_at, updated_at
                FROM calendar_events ORDER BY start_date
            """)
            
            events = []
            for row in cursor.fetchall():
                events.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'start_date': row[3],
                    'end_date': row[4],
                    'event_type': row[5],
                    'priority': row[6],
                    'reminder_minutes': row[7],
                    'created_at': row[8],
                    'updated_at': row[9]
                })
            
            return events
            
        except Exception as e:
            print(f"Error getting calendar data: {e}")
            return []
    
    def _get_menu_data(self) -> List[Dict[str, Any]]:
        """Get menu planner data"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, date, meal_type, recipe_id, recipe_title, servings,
                       notes, created_at, updated_at
                FROM menu_plans ORDER BY date, meal_type
            """)
            
            meals = []
            for row in cursor.fetchall():
                meals.append({
                    'id': row[0],
                    'date': row[1],
                    'meal_type': row[2],
                    'recipe_id': row[3],
                    'recipe_title': row[4],
                    'servings': row[5],
                    'notes': row[6],
                    'created_at': row[7],
                    'updated_at': row[8]
                })
            
            return meals
            
        except Exception as e:
            print(f"Error getting menu data: {e}")
            return []
    
    def _get_health_data(self) -> List[Dict[str, Any]]:
        """Get health log data"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, date, symptoms, severity, notes, gluten_exposure,
                       created_at, updated_at
                FROM health_log ORDER BY date DESC
            """)
            
            entries = []
            for row in cursor.fetchall():
                entries.append({
                    'id': row[0],
                    'date': row[1],
                    'symptoms': row[2],
                    'severity': row[3],
                    'notes': row[4],
                    'gluten_exposure': row[5],
                    'created_at': row[6],
                    'updated_at': row[7]
                })
            
            return entries
            
        except Exception as e:
            print(f"Error getting health data: {e}")
            return []
    
    def _get_shopping_data(self) -> List[Dict[str, Any]]:
        """Get shopping list data"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT id, item_name, category, quantity, unit, store,
                       priority, notes, completed, created_at, updated_at
                FROM shopping_items ORDER BY priority DESC, item_name
            """)
            
            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row[0],
                    'item_name': row[1],
                    'category': row[2],
                    'quantity': row[3],
                    'unit': row[4],
                    'store': row[5],
                    'priority': row[6],
                    'notes': row[7],
                    'completed': row[8],
                    'created_at': row[9],
                    'updated_at': row[10]
                })
            
            return items
            
        except Exception as e:
            print(f"Error getting shopping data: {e}")
            return []
    
    def _export_csv(self, data: List[Dict[str, Any]], file_path: str, 
                   panel_name: str, include_metadata: bool = True) -> bool:
        """Export data to CSV format"""
        try:
            if not data:
                return False
            
            # Flatten nested data for CSV
            flattened_data = self._flatten_data_for_csv(data)
            
            # Get fieldnames from first item
            fieldnames = list(flattened_data[0].keys()) if flattened_data else []
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_data)
            
            # Add metadata if requested
            if include_metadata:
                self._add_csv_metadata(file_path, panel_name, len(data))
            
            return True
            
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False
    
    def _export_json(self, data: List[Dict[str, Any]], file_path: str, 
                    panel_name: str, include_metadata: bool = True) -> bool:
        """Export data to JSON format"""
        try:
            export_data = {
                'panel': panel_name,
                'export_date': datetime.now().isoformat(),
                'record_count': len(data),
                'data': data
            }
            
            if include_metadata:
                export_data['metadata'] = {
                    'version': '1.0',
                    'application': 'CeliacShield',
                    'format': 'json'
                }
            
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            return False
    
    def _export_excel(self, data: List[Dict[str, Any]], file_path: str, 
                     panel_name: str, include_metadata: bool = True) -> bool:
        """Export data to Excel format"""
        try:
            if not data:
                return False
            
            # Flatten nested data for Excel
            flattened_data = self._flatten_data_for_csv(data)
            
            # Create DataFrame
            df = pd.DataFrame(flattened_data)
            
            # Write to Excel with multiple sheets
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Main data sheet
                df.to_excel(writer, sheet_name='Data', index=False)
                
                # Metadata sheet if requested
                if include_metadata:
                    metadata_df = pd.DataFrame([{
                        'Panel': panel_name,
                        'Export Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Record Count': len(data),
                        'Application': 'CeliacShield',
                        'Version': '1.0'
                    }])
                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting Excel: {e}")
            return False
    
    def _export_pdf(self, data: List[Dict[str, Any]], file_path: str, 
                   panel_name: str, include_metadata: bool = True) -> bool:
        """Export data to PDF format"""
        try:
            if not data:
                return False
            
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            title = Paragraph(f"{panel_name.replace('_', ' ').title()} Export", title_style)
            elements.append(title)
            
            # Metadata
            if include_metadata:
                meta_style = ParagraphStyle(
                    'Metadata',
                    parent=styles['Normal'],
                    fontSize=10,
                    spaceAfter=20,
                    alignment=1
                )
                metadata = f"Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {len(data)} records"
                meta_para = Paragraph(metadata, meta_style)
                elements.append(meta_para)
                elements.append(Spacer(1, 20))
            
            # Flatten data for table
            flattened_data = self._flatten_data_for_csv(data)
            
            if flattened_data:
                # Prepare table data
                headers = list(flattened_data[0].keys())
                table_data = [headers]
                
                # Add data rows (limit to prevent huge PDFs)
                for item in flattened_data[:100]:  # Limit to 100 records
                    row = [str(item.get(header, '')) for header in headers]
                    table_data.append(row)
                
                # Create table
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                
                elements.append(table)
                
                # Add note if data was truncated
                if len(data) > 100:
                    note_style = ParagraphStyle(
                        'Note',
                        parent=styles['Normal'],
                        fontSize=9,
                        spaceAfter=20,
                        alignment=1
                    )
                    note = Paragraph(f"Note: Showing first 100 of {len(data)} records", note_style)
                    elements.append(note)
            
            # Build PDF
            doc.build(elements)
            return True
            
        except Exception as e:
            print(f"Error exporting PDF: {e}")
            return False
    
    def _flatten_data_for_csv(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Flatten nested data structures for CSV export"""
        flattened = []
        
        for item in data:
            flat_item = {}
            for key, value in item.items():
                if isinstance(value, list):
                    # Convert list to string representation
                    flat_item[key] = json.dumps(value) if value else ''
                elif isinstance(value, dict):
                    # Convert dict to string representation
                    flat_item[key] = json.dumps(value) if value else ''
                else:
                    flat_item[key] = value
            flattened.append(flat_item)
        
        return flattened
    
    def _add_csv_metadata(self, file_path: str, panel_name: str, record_count: int):
        """Add metadata to CSV file"""
        try:
            # Read existing content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create metadata comment
            metadata = f"# CeliacShield Export - {panel_name}\n"
            metadata += f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            metadata += f"# Record Count: {record_count}\n"
            metadata += f"# Application Version: 1.0\n"
            metadata += f"#\n"
            
            # Write back with metadata
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(metadata + content)
                
        except Exception as e:
            print(f"Error adding CSV metadata: {e}")
    
    def _get_file_format(self, file_path: str) -> str:
        """Determine file format from extension"""
        ext = Path(file_path).suffix.lower().lstrip('.')
        return ext if ext in self.import_formats else 'unknown'
    
    def _import_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Import data from CSV file"""
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Skip metadata lines
                lines = csvfile.readlines()
                data_lines = []
                for line in lines:
                    if not line.strip().startswith('#'):
                        data_lines.append(line)
                
                # Parse CSV
                reader = csv.DictReader(data_lines)
                for row in reader:
                    # Convert string representations back to objects
                    for key, value in row.items():
                        if value and (value.startswith('[') or value.startswith('{')):
                            try:
                                row[key] = json.loads(value)
                            except:
                                pass  # Keep as string if parsing fails
                    data.append(row)
            
            return data
            
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return []
    
    def _import_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Import data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                import_data = json.load(jsonfile)
            
            # Handle different JSON structures
            if isinstance(import_data, dict):
                if 'data' in import_data:
                    return import_data['data']
                else:
                    return [import_data]
            elif isinstance(import_data, list):
                return import_data
            else:
                return []
                
        except Exception as e:
            print(f"Error importing JSON: {e}")
            return []
    
    def _import_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """Import data from Excel file"""
        try:
            # Read the first sheet
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Convert DataFrame to list of dictionaries
            data = df.to_dict('records')
            
            # Convert NaN values to None
            for item in data:
                for key, value in item.items():
                    if pd.isna(value):
                        item[key] = None
            
            return data
            
        except Exception as e:
            print(f"Error importing Excel: {e}")
            return []
    
    def _import_to_panel(self, panel_name: str, data: List[Dict[str, Any]], 
                        overwrite_mode: bool = False) -> Tuple[bool, str]:
        """Import data into the appropriate panel"""
        try:
            if panel_name == 'cookbook':
                return self._import_recipes(data, overwrite_mode)
            elif panel_name == 'pantry':
                return self._import_pantry_items(data, overwrite_mode)
            elif panel_name == 'calendar':
                return self._import_calendar_events(data, overwrite_mode)
            elif panel_name == 'menu_planner':
                return self._import_menu_plans(data, overwrite_mode)
            elif panel_name == 'health_log':
                return self._import_health_entries(data, overwrite_mode)
            elif panel_name == 'shopping_list':
                return self._import_shopping_items(data, overwrite_mode)
            else:
                return False, f"Unknown panel: {panel_name}"
                
        except Exception as e:
            return False, f"Error importing to {panel_name}: {e}"
    
    def _import_recipes(self, data: List[Dict[str, Any]], overwrite_mode: bool = False) -> Tuple[bool, str]:
        """Import recipe data"""
        try:
            cursor = self.db.cursor()
            imported_count = 0
            skipped_count = 0
            
            for recipe_data in data:
                # Check if recipe already exists
                cursor.execute("SELECT id FROM recipes WHERE title = ?", (recipe_data.get('title'),))
                existing = cursor.fetchone()
                
                if existing and not overwrite_mode:
                    skipped_count += 1
                    continue
                
                # Insert or update recipe
                if existing and overwrite_mode:
                    # Update existing recipe
                    cursor.execute("""
                        UPDATE recipes SET description=?, instructions=?, prep_time=?,
                                          cook_time=?, servings=?, difficulty=?, category=?,
                                          tags=?, updated_at=?
                        WHERE id=?
                    """, (
                        recipe_data.get('description', ''),
                        recipe_data.get('instructions', ''),
                        recipe_data.get('prep_time', 0),
                        recipe_data.get('cook_time', 0),
                        recipe_data.get('servings', 1),
                        recipe_data.get('difficulty', 'Easy'),
                        recipe_data.get('category', ''),
                        recipe_data.get('tags', ''),
                        datetime.now().isoformat(),
                        existing[0]
                    ))
                    recipe_id = existing[0]
                else:
                    # Insert new recipe
                    cursor.execute("""
                        INSERT INTO recipes (title, description, instructions, prep_time,
                                           cook_time, servings, difficulty, category, tags,
                                           created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        recipe_data.get('title', ''),
                        recipe_data.get('description', ''),
                        recipe_data.get('instructions', ''),
                        recipe_data.get('prep_time', 0),
                        recipe_data.get('cook_time', 0),
                        recipe_data.get('servings', 1),
                        recipe_data.get('difficulty', 'Easy'),
                        recipe_data.get('category', ''),
                        recipe_data.get('tags', ''),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                    recipe_id = cursor.lastrowid
                
                # Import ingredients
                if 'ingredients' in recipe_data:
                    # Clear existing ingredients if updating
                    if existing and overwrite_mode:
                        cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
                    
                    for ingredient in recipe_data['ingredients']:
                        cursor.execute("""
                            INSERT INTO recipe_ingredients (recipe_id, ingredient_name, quantity, unit, notes)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            recipe_id,
                            ingredient.get('name', ''),
                            ingredient.get('quantity', 0),
                            ingredient.get('unit', ''),
                            ingredient.get('notes', '')
                        ))
                
                imported_count += 1
            
            self.db.commit()
            return True, f"Imported {imported_count} recipes, skipped {skipped_count} existing"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error importing recipes: {e}"
    
    def _import_pantry_items(self, data: List[Dict[str, Any]], overwrite_mode: bool = False) -> Tuple[bool, str]:
        """Import pantry item data"""
        try:
            cursor = self.db.cursor()
            imported_count = 0
            skipped_count = 0
            
            for item_data in data:
                # Check if item already exists
                cursor.execute("SELECT id FROM pantry_items WHERE name = ?", (item_data.get('name'),))
                existing = cursor.fetchone()
                
                if existing and not overwrite_mode:
                    skipped_count += 1
                    continue
                
                # Insert or update item
                if existing and overwrite_mode:
                    cursor.execute("""
                        UPDATE pantry_items SET category=?, quantity=?, unit=?, expiration_date=?,
                                                gluten_free=?, notes=?, updated_at=?
                        WHERE id=?
                    """, (
                        item_data.get('category', ''),
                        item_data.get('quantity', 0),
                        item_data.get('unit', ''),
                        item_data.get('expiration_date'),
                        item_data.get('gluten_free', False),
                        item_data.get('notes', ''),
                        datetime.now().isoformat(),
                        existing[0]
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO pantry_items (name, category, quantity, unit, expiration_date,
                                                gluten_free, notes, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item_data.get('name', ''),
                        item_data.get('category', ''),
                        item_data.get('quantity', 0),
                        item_data.get('unit', ''),
                        item_data.get('expiration_date'),
                        item_data.get('gluten_free', False),
                        item_data.get('notes', ''),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                
                imported_count += 1
            
            self.db.commit()
            return True, f"Imported {imported_count} pantry items, skipped {skipped_count} existing"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error importing pantry items: {e}"
    
    def _import_calendar_events(self, data: List[Dict[str, Any]], overwrite_mode: bool = False) -> Tuple[bool, str]:
        """Import calendar event data"""
        try:
            cursor = self.db.cursor()
            imported_count = 0
            skipped_count = 0
            
            for event_data in data:
                # Check if event already exists
                cursor.execute("SELECT id FROM calendar_events WHERE title = ? AND start_date = ?", 
                             (event_data.get('title'), event_data.get('start_date')))
                existing = cursor.fetchone()
                
                if existing and not overwrite_mode:
                    skipped_count += 1
                    continue
                
                # Insert or update event
                if existing and overwrite_mode:
                    cursor.execute("""
                        UPDATE calendar_events SET description=?, end_date=?, event_type=?,
                                                  priority=?, reminder_minutes=?, updated_at=?
                        WHERE id=?
                    """, (
                        event_data.get('description', ''),
                        event_data.get('end_date'),
                        event_data.get('event_type', ''),
                        event_data.get('priority', 1),
                        event_data.get('reminder_minutes', 0),
                        datetime.now().isoformat(),
                        existing[0]
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO calendar_events (title, description, start_date, end_date,
                                                   event_type, priority, reminder_minutes,
                                                   created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        event_data.get('title', ''),
                        event_data.get('description', ''),
                        event_data.get('start_date'),
                        event_data.get('end_date'),
                        event_data.get('event_type', ''),
                        event_data.get('priority', 1),
                        event_data.get('reminder_minutes', 0),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                
                imported_count += 1
            
            self.db.commit()
            return True, f"Imported {imported_count} calendar events, skipped {skipped_count} existing"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error importing calendar events: {e}"
    
    def _import_menu_plans(self, data: List[Dict[str, Any]], overwrite_mode: bool = False) -> Tuple[bool, str]:
        """Import menu plan data"""
        try:
            cursor = self.db.cursor()
            imported_count = 0
            skipped_count = 0
            
            for meal_data in data:
                # Check if meal already exists
                cursor.execute("SELECT id FROM menu_plans WHERE date = ? AND meal_type = ?", 
                             (meal_data.get('date'), meal_data.get('meal_type')))
                existing = cursor.fetchone()
                
                if existing and not overwrite_mode:
                    skipped_count += 1
                    continue
                
                # Insert or update meal
                if existing and overwrite_mode:
                    cursor.execute("""
                        UPDATE menu_plans SET recipe_id=?, recipe_title=?, servings=?, notes=?, updated_at=?
                        WHERE id=?
                    """, (
                        meal_data.get('recipe_id'),
                        meal_data.get('recipe_title', ''),
                        meal_data.get('servings', 1),
                        meal_data.get('notes', ''),
                        datetime.now().isoformat(),
                        existing[0]
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO menu_plans (date, meal_type, recipe_id, recipe_title, servings, notes, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        meal_data.get('date'),
                        meal_data.get('meal_type', ''),
                        meal_data.get('recipe_id'),
                        meal_data.get('recipe_title', ''),
                        meal_data.get('servings', 1),
                        meal_data.get('notes', ''),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                
                imported_count += 1
            
            self.db.commit()
            return True, f"Imported {imported_count} menu plans, skipped {skipped_count} existing"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error importing menu plans: {e}"
    
    def _import_health_entries(self, data: List[Dict[str, Any]], overwrite_mode: bool = False) -> Tuple[bool, str]:
        """Import health log data"""
        try:
            cursor = self.db.cursor()
            imported_count = 0
            skipped_count = 0
            
            for entry_data in data:
                # Check if entry already exists
                cursor.execute("SELECT id FROM health_log WHERE date = ?", (entry_data.get('date'),))
                existing = cursor.fetchone()
                
                if existing and not overwrite_mode:
                    skipped_count += 1
                    continue
                
                # Insert or update entry
                if existing and overwrite_mode:
                    cursor.execute("""
                        UPDATE health_log SET symptoms=?, severity=?, notes=?, gluten_exposure=?, updated_at=?
                        WHERE id=?
                    """, (
                        entry_data.get('symptoms', ''),
                        entry_data.get('severity', 1),
                        entry_data.get('notes', ''),
                        entry_data.get('gluten_exposure', False),
                        datetime.now().isoformat(),
                        existing[0]
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO health_log (date, symptoms, severity, notes, gluten_exposure, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entry_data.get('date'),
                        entry_data.get('symptoms', ''),
                        entry_data.get('severity', 1),
                        entry_data.get('notes', ''),
                        entry_data.get('gluten_exposure', False),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                
                imported_count += 1
            
            self.db.commit()
            return True, f"Imported {imported_count} health entries, skipped {skipped_count} existing"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error importing health entries: {e}"
    
    def _import_shopping_items(self, data: List[Dict[str, Any]], overwrite_mode: bool = False) -> Tuple[bool, str]:
        """Import shopping list data"""
        try:
            cursor = self.db.cursor()
            imported_count = 0
            skipped_count = 0
            
            for item_data in data:
                # Check if item already exists
                cursor.execute("SELECT id FROM shopping_items WHERE item_name = ?", (item_data.get('item_name'),))
                existing = cursor.fetchone()
                
                if existing and not overwrite_mode:
                    skipped_count += 1
                    continue
                
                # Insert or update item
                if existing and overwrite_mode:
                    cursor.execute("""
                        UPDATE shopping_items SET category=?, quantity=?, unit=?, store=?,
                                                  priority=?, notes=?, completed=?, updated_at=?
                        WHERE id=?
                    """, (
                        item_data.get('category', ''),
                        item_data.get('quantity', 0),
                        item_data.get('unit', ''),
                        item_data.get('store', ''),
                        item_data.get('priority', 1),
                        item_data.get('notes', ''),
                        item_data.get('completed', False),
                        datetime.now().isoformat(),
                        existing[0]
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO shopping_items (item_name, category, quantity, unit, store,
                                                   priority, notes, completed, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item_data.get('item_name', ''),
                        item_data.get('category', ''),
                        item_data.get('quantity', 0),
                        item_data.get('unit', ''),
                        item_data.get('store', ''),
                        item_data.get('priority', 1),
                        item_data.get('notes', ''),
                        item_data.get('completed', False),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                
                imported_count += 1
            
            self.db.commit()
            return True, f"Imported {imported_count} shopping items, skipped {skipped_count} existing"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error importing shopping items: {e}"
    
    def _create_export_summary(self, file_path: str, panels: List[str]):
        """Create a summary file for the export"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("CeliacShield Data Export Summary\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Application: CeliacShield v1.0\n")
                f.write(f"Exported Panels: {', '.join(panels)}\n\n")
                
                # Add record counts
                for panel in panels:
                    data = self._get_panel_data(panel)
                    count = len(data) if data else 0
                    f.write(f"{panel.replace('_', ' ').title()}: {count} records\n")
                
                f.write(f"\nExport completed successfully.\n")
                
        except Exception as e:
            print(f"Error creating export summary: {e}")
