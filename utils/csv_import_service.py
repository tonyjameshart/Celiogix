# path: utils/csv_import_service.py
"""
CSV Import Service for Gluten Guardian Mobile Data

Imports CSV files exported from the Android mobile app into the desktop application.
Supports health logs, barcode scans, and combined data formats.
"""

from __future__ import annotations

import csv
import datetime as _dt
from pathlib import Path
from typing import Any, List, Dict, Optional
import sqlite3

class CSVImportService:
    """Service for importing CSV data from mobile app"""
    
    def __init__(self, db: sqlite3.Connection):
        self.db = db
    
    def import_csv_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Import CSV file from mobile app.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Dictionary with import results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Determine file type based on headers
                headers = reader.fieldnames or []
                
                if 'Type' in headers:
                    return self._import_combined_data(reader)
                elif 'Barcode' in headers and 'Product_Name' in headers:
                    return self._import_barcode_scans(reader)
                elif 'Date' in headers and 'Meal' in headers:
                    return self._import_health_logs(reader)
                else:
                    return {
                        'success': False,
                        'message': 'Unknown CSV format',
                        'imported_count': 0
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'message': f'Error reading CSV file: {str(e)}',
                'imported_count': 0
            }
    
    def _import_health_logs(self, reader: csv.DictReader) -> Dict[str, Any]:
        """Import health logs from CSV"""
        imported_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
            try:
                # Map CSV columns to database columns
                health_log_data = {
                    'date': row.get('Date', '').strip(),
                    'time': row.get('Time', '').strip(),
                    'meal': row.get('Meal', '').strip(),
                    'items': row.get('Items', '').strip(),
                    'risk': row.get('Risk', 'none').strip(),
                    'onset_min': int(row.get('Onset_Minutes', 0) or 0),
                    'severity': int(row.get('Severity', 0) or 0),
                    'stool': int(row.get('Bristol_Type', 0) or 0),
                    'recipe': row.get('Recipe', '').strip(),
                    'symptoms': row.get('Symptoms', '').strip(),
                    'notes': row.get('Notes', '').strip(),
                    'hydration_liters': float(row.get('Hydration_Liters', 0) or 0),
                    'fiber_grams': float(row.get('Fiber_Grams', 0) or 0),
                    'mood': row.get('Mood', '').strip(),
                    'energy_level': int(row.get('Energy_Level', 5) or 5),
                }
                
                # Validate required fields
                if not health_log_data['date']:
                    errors.append(f"Row {row_num}: Missing date")
                    continue
                
                # Insert into database
                self.db.execute("""
                    INSERT OR REPLACE INTO health_log(
                        date, time, meal, items, risk, onset_min, severity, stool,
                        recipe, symptoms, notes, hydration_liters, fiber_grams,
                        mood, energy_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    health_log_data['date'],
                    health_log_data['time'],
                    health_log_data['meal'],
                    health_log_data['items'],
                    health_log_data['risk'],
                    health_log_data['onset_min'],
                    health_log_data['severity'],
                    health_log_data['stool'],
                    health_log_data['recipe'],
                    health_log_data['symptoms'],
                    health_log_data['notes'],
                    health_log_data['hydration_liters'],
                    health_log_data['fiber_grams'],
                    health_log_data['mood'],
                    health_log_data['energy_level']
                ))
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        self.db.commit()
        
        return {
            'success': True,
            'message': f'Imported {imported_count} health log entries',
            'imported_count': imported_count,
            'errors': errors
        }
    
    def _import_barcode_scans(self, reader: csv.DictReader) -> Dict[str, Any]:
        """Import barcode scans from CSV"""
        imported_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                scan_data = {
                    'barcode': row.get('Barcode', '').strip(),
                    'product_name': row.get('Product_Name', '').strip(),
                    'brand': row.get('Brand', '').strip(),
                    'ingredients': row.get('Ingredients', '').strip(),
                    'safety_status': row.get('Safety_Status', 'UNKNOWN').strip(),
                    'confidence': float(row.get('Confidence', 0) or 0),
                    'warnings': row.get('Warnings', '').strip(),
                }
                
                # Validate required fields
                if not scan_data['barcode']:
                    errors.append(f"Row {row_num}: Missing barcode")
                    continue
                
                # Insert into database (create table if it doesn't exist)
                self.db.execute("""
                    CREATE TABLE IF NOT EXISTS barcode_scans (
                        id INTEGER PRIMARY KEY,
                        barcode TEXT UNIQUE,
                        product_name TEXT,
                        brand TEXT,
                        ingredients TEXT,
                        gf_safety TEXT,
                        confidence REAL,
                        warnings TEXT,
                        scan_date TEXT
                    )
                """)
                
                self.db.execute("""
                    INSERT OR REPLACE INTO barcode_scans(
                        barcode, product_name, brand, ingredients, gf_safety,
                        confidence, warnings, scan_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    scan_data['barcode'],
                    scan_data['product_name'],
                    scan_data['brand'],
                    scan_data['ingredients'],
                    scan_data['safety_status'],
                    scan_data['confidence'],
                    scan_data['warnings']
                ))
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        self.db.commit()
        
        return {
            'success': True,
            'message': f'Imported {imported_count} barcode scans',
            'imported_count': imported_count,
            'errors': errors
        }
    
    def _import_combined_data(self, reader: csv.DictReader) -> Dict[str, Any]:
        """Import combined data from CSV"""
        health_logs_imported = 0
        scans_imported = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                data_type = row.get('Type', '').strip()
                
                if data_type == 'HEALTH_LOG':
                    # Import as health log
                    health_log_data = {
                        'date': row.get('Date', '').strip(),
                        'time': row.get('Time', '').strip(),
                        'meal': row.get('Meal', '').strip(),
                        'items': row.get('Items', '').strip(),
                        'risk': row.get('Risk', 'none').strip(),
                        'onset_min': int(row.get('Onset_Minutes', 0) or 0),
                        'severity': int(row.get('Severity', 0) or 0),
                        'stool': int(row.get('Bristol_Type', 0) or 0),
                        'recipe': row.get('Recipe', '').strip(),
                        'symptoms': row.get('Symptoms', '').strip(),
                        'notes': row.get('Notes', '').strip(),
                        'hydration_liters': float(row.get('Hydration_Liters', 0) or 0),
                        'fiber_grams': float(row.get('Fiber_Grams', 0) or 0),
                        'mood': row.get('Mood', '').strip(),
                        'energy_level': int(row.get('Energy_Level', 5) or 5),
                    }
                    
                    if health_log_data['date']:
                        self.db.execute("""
                            INSERT OR REPLACE INTO health_log(
                                date, time, meal, items, risk, onset_min, severity, stool,
                                recipe, symptoms, notes, hydration_liters, fiber_grams,
                                mood, energy_level
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            health_log_data['date'],
                            health_log_data['time'],
                            health_log_data['meal'],
                            health_log_data['items'],
                            health_log_data['risk'],
                            health_log_data['onset_min'],
                            health_log_data['severity'],
                            health_log_data['stool'],
                            health_log_data['recipe'],
                            health_log_data['symptoms'],
                            health_log_data['notes'],
                            health_log_data['hydration_liters'],
                            health_log_data['fiber_grams'],
                            health_log_data['mood'],
                            health_log_data['energy_level']
                        ))
                        health_logs_imported += 1
                
                elif data_type == 'BARCODE_SCAN':
                    # Import as barcode scan
                    scan_data = {
                        'barcode': row.get('Barcode', '').strip(),
                        'product_name': row.get('Product_Name', '').strip(),
                        'brand': row.get('Brand', '').strip(),
                        'ingredients': row.get('Ingredients', '').strip(),
                        'safety_status': row.get('Safety_Status', 'UNKNOWN').strip(),
                        'confidence': float(row.get('Confidence', 0) or 0),
                        'warnings': row.get('Warnings', '').strip(),
                    }
                    
                    if scan_data['barcode']:
                        self.db.execute("""
                            CREATE TABLE IF NOT EXISTS barcode_scans (
                                id INTEGER PRIMARY KEY,
                                barcode TEXT UNIQUE,
                                product_name TEXT,
                                brand TEXT,
                                ingredients TEXT,
                                gf_safety TEXT,
                                confidence REAL,
                                warnings TEXT,
                                scan_date TEXT
                            )
                        """)
                        
                        self.db.execute("""
                            INSERT OR REPLACE INTO barcode_scans(
                                barcode, product_name, brand, ingredients, gf_safety,
                                confidence, warnings, scan_date
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                        """, (
                            scan_data['barcode'],
                            scan_data['product_name'],
                            scan_data['brand'],
                            scan_data['ingredients'],
                            scan_data['safety_status'],
                            scan_data['confidence'],
                            scan_data['warnings']
                        ))
                        scans_imported += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        self.db.commit()
        
        total_imported = health_logs_imported + scans_imported
        
        return {
            'success': True,
            'message': f'Imported {health_logs_imported} health logs and {scans_imported} barcode scans',
            'imported_count': total_imported,
            'health_logs_count': health_logs_imported,
            'scans_count': scans_imported,
            'errors': errors
        }
    
    def validate_csv_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate CSV file before import.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Validation results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames or []
                
                # Check file type
                if 'Type' in headers:
                    file_type = 'combined'
                elif 'Barcode' in headers and 'Product_Name' in headers:
                    file_type = 'barcode_scans'
                elif 'Date' in headers and 'Meal' in headers:
                    file_type = 'health_logs'
                else:
                    return {
                        'valid': False,
                        'message': 'Unknown CSV format',
                        'file_type': 'unknown'
                    }
                
                # Count rows
                row_count = sum(1 for _ in reader)
                
                return {
                    'valid': True,
                    'message': f'Valid {file_type} CSV file with {row_count} data rows',
                    'file_type': file_type,
                    'row_count': row_count,
                    'headers': headers
                }
                
        except Exception as e:
            return {
                'valid': False,
                'message': f'Error validating CSV file: {str(e)}',
                'file_type': 'unknown'
            }
