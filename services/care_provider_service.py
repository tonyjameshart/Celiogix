# path: services/care_provider_service.py
"""
Care Provider Service for managing healthcare provider contacts
"""

import os
import sqlite3
import webbrowser
import subprocess
import platform
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import asdict

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

from utils.db import get_connection
from services.mobile_sync import CareProviderData


class CareProviderService(QObject):
    """Service for managing care provider contacts and appointments"""
    
    # Signals
    provider_added = Signal(CareProviderData)
    provider_updated = Signal(CareProviderData)
    provider_deleted = Signal(str)  # provider_id
    appointment_created = Signal(dict)  # appointment data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conn = get_connection()
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure care provider tables exist in database"""
        try:
            cursor = self.conn.cursor()
            
            # Create care_providers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS care_providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    title TEXT,
                    specialty TEXT,
                    organization TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    website TEXT,
                    notes TEXT,
                    emergency_contact BOOLEAN DEFAULT 0,
                    preferred_contact_method TEXT DEFAULT 'phone',
                    last_appointment TEXT,
                    next_appointment TEXT,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_care_providers_specialty 
                ON care_providers(specialty)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_care_providers_emergency 
                ON care_providers(emergency_contact)
            """)
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Error creating care provider tables: {str(e)}")
    
    def add_provider(self, provider_data: Dict[str, Any]) -> bool:
        """Add a new care provider"""
        try:
            # Generate provider ID if not provided
            if not provider_data.get('provider_id'):
                provider_data['provider_id'] = f"provider_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO care_providers (
                    provider_id, name, title, specialty, organization,
                    phone, email, address, city, state, zip_code,
                    website, notes, emergency_contact, preferred_contact_method,
                    last_appointment, next_appointment, created_date, updated_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                provider_data['provider_id'],
                provider_data['name'],
                provider_data.get('title', ''),
                provider_data.get('specialty', ''),
                provider_data.get('organization', ''),
                provider_data.get('phone', ''),
                provider_data.get('email', ''),
                provider_data.get('address', ''),
                provider_data.get('city', ''),
                provider_data.get('state', ''),
                provider_data.get('zip_code', ''),
                provider_data.get('website', ''),
                provider_data.get('notes', ''),
                provider_data.get('emergency_contact', False),
                provider_data.get('preferred_contact_method', 'phone'),
                provider_data.get('last_appointment', ''),
                provider_data.get('next_appointment', ''),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            
            # Create CareProviderData object and emit signal
            provider = self._dict_to_care_provider_data(provider_data)
            self.provider_added.emit(provider)
            
            return True
            
        except Exception as e:
            print(f"Error adding care provider: {str(e)}")
            return False
    
    def get_providers(self, specialty_filter: Optional[str] = None, 
                     emergency_only: bool = False) -> List[CareProviderData]:
        """Get care providers with optional filtering"""
        try:
            cursor = self.conn.cursor()
            
            query = "SELECT * FROM care_providers WHERE 1=1"
            params = []
            
            if specialty_filter:
                query += " AND specialty LIKE ?"
                params.append(f"%{specialty_filter}%")
            
            if emergency_only:
                query += " AND emergency_contact = 1"
            
            query += " ORDER BY name"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            providers = []
            for row in rows:
                provider_data = {
                    'provider_id': row[1],
                    'name': row[2],
                    'title': row[3] or '',
                    'specialty': row[4] or '',
                    'organization': row[5] or '',
                    'phone': row[6] or '',
                    'email': row[7] or '',
                    'address': row[8] or '',
                    'city': row[9] or '',
                    'state': row[10] or '',
                    'zip_code': row[11] or '',
                    'website': row[12] or '',
                    'notes': row[13] or '',
                    'emergency_contact': bool(row[14]),
                    'preferred_contact_method': row[15] or 'phone',
                    'last_appointment': row[16] or '',
                    'next_appointment': row[17] or '',
                    'created_date': row[18] or '',
                    'updated_date': row[19] or ''
                }
                
                providers.append(self._dict_to_care_provider_data(provider_data))
            
            return providers
            
        except Exception as e:
            print(f"Error getting care providers: {str(e)}")
            return []
    
    def get_provider(self, provider_id: str) -> Optional[CareProviderData]:
        """Get specific care provider by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM care_providers WHERE provider_id = ?", (provider_id,))
            row = cursor.fetchone()
            
            if row:
                provider_data = {
                    'provider_id': row[1],
                    'name': row[2],
                    'title': row[3] or '',
                    'specialty': row[4] or '',
                    'organization': row[5] or '',
                    'phone': row[6] or '',
                    'email': row[7] or '',
                    'address': row[8] or '',
                    'city': row[9] or '',
                    'state': row[10] or '',
                    'zip_code': row[11] or '',
                    'website': row[12] or '',
                    'notes': row[13] or '',
                    'emergency_contact': bool(row[14]),
                    'preferred_contact_method': row[15] or 'phone',
                    'last_appointment': row[16] or '',
                    'next_appointment': row[17] or '',
                    'created_date': row[18] or '',
                    'updated_date': row[19] or ''
                }
                
                return self._dict_to_care_provider_data(provider_data)
            
            return None
            
        except Exception as e:
            print(f"Error getting care provider: {str(e)}")
            return None
    
    def update_provider(self, provider_id: str, provider_data: Dict[str, Any]) -> bool:
        """Update existing care provider"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE care_providers SET
                    name = ?, title = ?, specialty = ?, organization = ?,
                    phone = ?, email = ?, address = ?, city = ?, state = ?, zip_code = ?,
                    website = ?, notes = ?, emergency_contact = ?, preferred_contact_method = ?,
                    last_appointment = ?, next_appointment = ?, updated_date = ?
                WHERE provider_id = ?
            """, (
                provider_data['name'],
                provider_data.get('title', ''),
                provider_data.get('specialty', ''),
                provider_data.get('organization', ''),
                provider_data.get('phone', ''),
                provider_data.get('email', ''),
                provider_data.get('address', ''),
                provider_data.get('city', ''),
                provider_data.get('state', ''),
                provider_data.get('zip_code', ''),
                provider_data.get('website', ''),
                provider_data.get('notes', ''),
                provider_data.get('emergency_contact', False),
                provider_data.get('preferred_contact_method', 'phone'),
                provider_data.get('last_appointment', ''),
                provider_data.get('next_appointment', ''),
                datetime.now().isoformat(),
                provider_id
            ))
            
            self.conn.commit()
            
            # Emit signal
            provider = self._dict_to_care_provider_data(provider_data)
            self.provider_updated.emit(provider)
            
            return True
            
        except Exception as e:
            print(f"Error updating care provider: {str(e)}")
            return False
    
    def delete_provider(self, provider_id: str) -> bool:
        """Delete care provider"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM care_providers WHERE provider_id = ?", (provider_id,))
            self.conn.commit()
            
            # Emit signal
            self.provider_deleted.emit(provider_id)
            
            return True
            
        except Exception as e:
            print(f"Error deleting care provider: {str(e)}")
            return False
    
    def get_specialties(self) -> List[str]:
        """Get list of unique specialties"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT specialty FROM care_providers WHERE specialty IS NOT NULL AND specialty != '' ORDER BY specialty")
            rows = cursor.fetchall()
            
            return [row[0] for row in rows]
            
        except Exception as e:
            print(f"Error getting specialties: {str(e)}")
            return []
    
    def contact_provider(self, provider: CareProviderData, contact_method: str = None) -> bool:
        """Contact provider via phone or email"""
        try:
            if contact_method is None:
                contact_method = provider.preferred_contact_method
            
            if contact_method == 'phone' and provider.phone:
                return self._make_phone_call(provider.phone)
            elif contact_method == 'email' and provider.email:
                return self._send_email(provider.email)
            elif contact_method == 'both':
                # Try phone first, then email
                if provider.phone:
                    return self._make_phone_call(provider.phone)
                elif provider.email:
                    return self._send_email(provider.email)
            
            return False
            
        except Exception as e:
            print(f"Error contacting provider: {str(e)}")
            return False
    
    def _make_phone_call(self, phone_number: str) -> bool:
        """Initiate phone call (opens default phone app)"""
        try:
            # Clean phone number
            clean_number = ''.join(filter(str.isdigit, phone_number))
            
            if platform.system() == "Windows":
                # Windows - open default phone app
                subprocess.run(['start', f'tel:{phone_number}'], shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', f'tel:{phone_number}'])
            elif platform.system() == "Linux":
                subprocess.run(['xdg-open', f'tel:{phone_number}'])
            
            return True
            
        except Exception as e:
            print(f"Error making phone call: {str(e)}")
            return False
    
    def _send_email(self, email_address: str) -> bool:
        """Open default email client with provider's email"""
        try:
            mailto_url = f"mailto:{email_address}"
            webbrowser.open(mailto_url)
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def create_appointment_from_provider(self, provider: CareProviderData, 
                                       appointment_data: Dict[str, Any]) -> bool:
        """Create calendar appointment from care provider"""
        try:
            # Add provider information to appointment data
            appointment_data['provider_name'] = f"{provider.title} {provider.name}".strip()
            appointment_data['provider_specialty'] = provider.specialty
            appointment_data['provider_organization'] = provider.organization
            appointment_data['provider_phone'] = provider.phone
            appointment_data['provider_email'] = provider.email
            
            # Emit signal for calendar integration
            self.appointment_created.emit(appointment_data)
            
            return True
            
        except Exception as e:
            print(f"Error creating appointment: {str(e)}")
            return False
    
    def search_providers(self, search_term: str) -> List[CareProviderData]:
        """Search providers by name, specialty, or organization"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM care_providers 
                WHERE name LIKE ? OR specialty LIKE ? OR organization LIKE ?
                ORDER BY name
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            rows = cursor.fetchall()
            
            providers = []
            for row in rows:
                provider_data = {
                    'provider_id': row[1],
                    'name': row[2],
                    'title': row[3] or '',
                    'specialty': row[4] or '',
                    'organization': row[5] or '',
                    'phone': row[6] or '',
                    'email': row[7] or '',
                    'address': row[8] or '',
                    'city': row[9] or '',
                    'state': row[10] or '',
                    'zip_code': row[11] or '',
                    'website': row[12] or '',
                    'notes': row[13] or '',
                    'emergency_contact': bool(row[14]),
                    'preferred_contact_method': row[15] or 'phone',
                    'last_appointment': row[16] or '',
                    'next_appointment': row[17] or '',
                    'created_date': row[18] or '',
                    'updated_date': row[19] or ''
                }
                
                providers.append(self._dict_to_care_provider_data(provider_data))
            
            return providers
            
        except Exception as e:
            print(f"Error searching providers: {str(e)}")
            return []
    
    def get_provider_statistics(self) -> Dict[str, Any]:
        """Get care provider statistics"""
        try:
            cursor = self.conn.cursor()
            
            # Total providers
            cursor.execute("SELECT COUNT(*) FROM care_providers")
            total_providers = cursor.fetchone()[0]
            
            # Emergency providers
            cursor.execute("SELECT COUNT(*) FROM care_providers WHERE emergency_contact = 1")
            emergency_providers = cursor.fetchone()[0]
            
            # Providers by specialty
            cursor.execute("""
                SELECT specialty, COUNT(*) 
                FROM care_providers 
                WHERE specialty IS NOT NULL AND specialty != '' 
                GROUP BY specialty 
                ORDER BY COUNT(*) DESC
            """)
            specialty_counts = dict(cursor.fetchall())
            
            # Recent additions (last 30 days)
            thirty_days_ago = (datetime.now().timestamp() - 30 * 24 * 60 * 60)
            cursor.execute("""
                SELECT COUNT(*) FROM care_providers 
                WHERE created_date > datetime(?, 'unixepoch')
            """, (thirty_days_ago,))
            recent_additions = cursor.fetchone()[0]
            
            return {
                'total_providers': total_providers,
                'emergency_providers': emergency_providers,
                'specialty_counts': specialty_counts,
                'recent_additions': recent_additions,
                'top_specialties': list(specialty_counts.keys())[:5]
            }
            
        except Exception as e:
            print(f"Error getting provider statistics: {str(e)}")
            return {}
    
    def _dict_to_care_provider_data(self, data: Dict[str, Any]) -> CareProviderData:
        """Convert dictionary to CareProviderData object"""
        return CareProviderData(
            provider_id=data['provider_id'],
            name=data['name'],
            title=data.get('title', ''),
            specialty=data.get('specialty', ''),
            organization=data.get('organization', ''),
            phone=data.get('phone'),
            email=data.get('email'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            website=data.get('website'),
            notes=data.get('notes'),
            emergency_contact=data.get('emergency_contact', False),
            preferred_contact_method=data.get('preferred_contact_method', 'phone'),
            last_appointment=data.get('last_appointment'),
            next_appointment=data.get('next_appointment'),
            created_date=data.get('created_date', ''),
            updated_date=data.get('updated_date', '')
        )


def get_care_provider_service() -> CareProviderService:
    """Get singleton care provider service instance"""
    global _care_provider_service
    if _care_provider_service is None:
        _care_provider_service = CareProviderService()
    return _care_provider_service


# Global service instance
_care_provider_service = None
