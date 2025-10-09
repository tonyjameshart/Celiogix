#!/usr/bin/env python3
"""
Demo script for Care Provider system integration
Shows the complete care provider workflow in Celiogix
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt

from services.care_provider_service import get_care_provider_service
from panels.health_log_panel import HealthLogPanel
from panels.calendar_panel import CalendarPanel


class CareProviderDemo(QMainWindow):
    """Demo window showcasing Care Provider functionality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Celiogix Care Provider System Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize services
        self.care_provider_service = get_care_provider_service()
        
        self.setup_ui()
        self.add_demo_data()
    
    def setup_ui(self):
        """Set up the demo UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_label = QLabel("🏥 Celiogix Care Provider System Demo")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("""
        This demo showcases the integrated Care Provider system that connects Health Logging, 
        Calendar Management, and Mobile Companion functionality.
        
        Features demonstrated:
        • Care Provider Management (add, edit, delete, search)
        • Clickable contact methods (call, email)
        • Quick appointment creation from providers
        • Integration between Health Log and Calendar panels
        • Mobile sync for care provider data
        """)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(desc_label)
        
        # Tab widget for panels
        self.tab_widget = QTabWidget()
        
        # Health Log Panel (with Care Providers tab)
        self.health_log_panel = HealthLogPanel()
        self.tab_widget.addTab(self.health_log_panel, "🏥 Health Log & Care Providers")
        
        # Calendar Panel (with appointment creation)
        self.calendar_panel = CalendarPanel()
        self.tab_widget.addTab(self.calendar_panel, "📅 Calendar & Appointments")
        
        layout.addWidget(self.tab_widget)
        
        # Demo buttons
        demo_layout = QVBoxLayout()
        
        demo_label = QLabel("Demo Actions:")
        demo_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        demo_layout.addWidget(demo_label)
        
        # Button to add demo providers
        add_demo_btn = QPushButton("📋 Add Demo Care Providers")
        add_demo_btn.clicked.connect(self.add_demo_providers)
        add_demo_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; border-radius: 3px;")
        demo_layout.addWidget(add_demo_btn)
        
        # Button to show provider statistics
        stats_btn = QPushButton("📊 Show Provider Statistics")
        stats_btn.clicked.connect(self.show_provider_statistics)
        stats_btn.setStyleSheet("background-color: #3498db; color: white; padding: 8px; border-radius: 3px;")
        demo_layout.addWidget(stats_btn)
        
        # Button to demonstrate appointment creation
        appointment_btn = QPushButton("📅 Create Demo Appointment")
        appointment_btn.clicked.connect(self.create_demo_appointment)
        appointment_btn.setStyleSheet("background-color: #e67e22; color: white; padding: 8px; border-radius: 3px;")
        demo_layout.addWidget(appointment_btn)
        
        # Button to clear all demo data
        clear_btn = QPushButton("🗑️ Clear All Demo Data")
        clear_btn.clicked.connect(self.clear_demo_data)
        clear_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px; border-radius: 3px;")
        demo_layout.addWidget(clear_btn)
        
        layout.addLayout(demo_layout)
    
    def add_demo_data(self):
        """Add initial demo data"""
        self.add_demo_providers()
    
    def add_demo_providers(self):
        """Add demo care providers"""
        demo_providers = [
            {
                'name': 'Dr. Sarah Johnson',
                'title': 'Dr.',
                'specialty': 'Gastroenterologist',
                'organization': 'City Medical Center',
                'phone': '(555) 123-4567',
                'email': 'sarah.johnson@citymedical.com',
                'address': '123 Medical Plaza',
                'city': 'Springfield',
                'state': 'IL',
                'zip_code': '62701',
                'website': 'www.citymedical.com',
                'notes': 'Specializes in celiac disease management',
                'emergency_contact': False,
                'preferred_contact_method': 'email',
                'last_appointment': '2024-01-15',
                'next_appointment': '2024-04-15'
            },
            {
                'name': 'Jennifer Martinez',
                'title': 'RD',
                'specialty': 'Nutritionist/Dietitian',
                'organization': 'Healthy Living Clinic',
                'phone': '(555) 234-5678',
                'email': 'j.martinez@healthyliving.com',
                'address': '456 Wellness Drive',
                'city': 'Springfield',
                'state': 'IL',
                'zip_code': '62702',
                'website': 'www.healthyliving.com',
                'notes': 'Certified gluten-free nutrition specialist',
                'emergency_contact': False,
                'preferred_contact_method': 'phone',
                'last_appointment': '2024-01-20',
                'next_appointment': '2024-03-20'
            },
            {
                'name': 'Dr. Michael Chen',
                'title': 'Dr.',
                'specialty': 'Primary Care',
                'organization': 'Family Health Associates',
                'phone': '(555) 345-6789',
                'email': 'm.chen@familyhealth.com',
                'address': '789 Main Street',
                'city': 'Springfield',
                'state': 'IL',
                'zip_code': '62703',
                'website': 'www.familyhealth.com',
                'notes': 'Primary care physician with celiac experience',
                'emergency_contact': True,
                'preferred_contact_method': 'both',
                'last_appointment': '2024-01-10',
                'next_appointment': '2024-04-10'
            },
            {
                'name': 'Dr. Lisa Thompson',
                'title': 'Dr.',
                'specialty': 'Endocrinologist',
                'organization': 'Endocrine Specialists',
                'phone': '(555) 456-7890',
                'email': 'l.thompson@endocrine.com',
                'address': '321 Specialist Blvd',
                'city': 'Springfield',
                'state': 'IL',
                'zip_code': '62704',
                'website': 'www.endocrine.com',
                'notes': 'Monitors diabetes and thyroid in celiac patients',
                'emergency_contact': False,
                'preferred_contact_method': 'email',
                'last_appointment': '2024-01-25',
                'next_appointment': '2024-05-25'
            },
            {
                'name': 'Dr. Robert Wilson',
                'title': 'Dr.',
                'specialty': 'Emergency Medicine',
                'organization': 'Springfield Emergency Hospital',
                'phone': '(555) 911-0000',
                'email': 'r.wilson@emergency.com',
                'address': '999 Emergency Lane',
                'city': 'Springfield',
                'state': 'IL',
                'zip_code': '62705',
                'website': 'www.emergency.com',
                'notes': 'Emergency care for severe reactions',
                'emergency_contact': True,
                'preferred_contact_method': 'phone',
                'last_appointment': '',
                'next_appointment': ''
            }
        ]
        
        added_count = 0
        for provider_data in demo_providers:
            success = self.care_provider_service.add_provider(provider_data)
            if success:
                added_count += 1
        
        QMessageBox.information(self, "Demo Data Added", 
                              f"Successfully added {added_count} demo care providers!\n\n"
                              "You can now:\n"
                              "• View providers in the Health Log panel\n"
                              "• Create appointments from the Calendar panel\n"
                              "• Test contact methods (call/email)\n"
                              "• Search and filter providers")
        
        # Refresh the panels
        if hasattr(self.health_log_panel, 'refresh_providers'):
            self.health_log_panel.refresh_providers()
    
    def show_provider_statistics(self):
        """Show care provider statistics"""
        stats = self.care_provider_service.get_provider_statistics()
        
        message = f"""
        📊 Care Provider Statistics:
        
        Total Providers: {stats.get('total_providers', 0)}
        Emergency Contacts: {stats.get('emergency_providers', 0)}
        Recent Additions: {stats.get('recent_additions', 0)}
        
        Top Specialties:
        """
        
        for specialty, count in list(stats.get('specialty_counts', {}).items())[:5]:
            message += f"• {specialty}: {count} providers\n"
        
        QMessageBox.information(self, "Provider Statistics", message)
    
    def create_demo_appointment(self):
        """Create a demo appointment"""
        providers = self.care_provider_service.get_providers()
        
        if not providers:
            QMessageBox.information(self, "No Providers", 
                                  "Please add demo providers first!")
            return
        
        # Get first provider for demo
        provider = providers[0]
        
        # Create appointment data
        appointment_data = {
            'title': f"Demo Appointment with {provider.title} {provider.name}",
            'date': '2024-02-15',
            'time': '10:00',
            'event_type': 'Medical Appointment',
            'priority': 'Medium',
            'description': f'Demo appointment with {provider.specialty} for routine checkup',
            'provider_name': f"{provider.title} {provider.name}",
            'provider_specialty': provider.specialty,
            'provider_organization': provider.organization,
            'provider_phone': provider.phone,
            'provider_email': provider.email
        }
        
        # Trigger the appointment creation signal
        self.care_provider_service.appointment_created.emit(appointment_data)
        
        QMessageBox.information(self, "Demo Appointment Created", 
                              f"Demo appointment created with {provider.name}!\n\n"
                              "Check the Calendar panel to see the appointment.")
    
    def clear_demo_data(self):
        """Clear all demo data"""
        reply = QMessageBox.question(self, "Clear Demo Data", 
                                   "Are you sure you want to clear all demo data?\n\n"
                                   "This will remove all care providers and appointments.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Clear providers (in a real app, you'd have a clear_all method)
            providers = self.care_provider_service.get_providers()
            for provider in providers:
                self.care_provider_service.delete_provider(provider.provider_id)
            
            QMessageBox.information(self, "Demo Data Cleared", 
                                  "All demo data has been cleared.")
            
            # Refresh panels
            if hasattr(self.health_log_panel, 'refresh_providers'):
                self.health_log_panel.refresh_providers()


def main():
    """Main demo function"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Celiogix Care Provider Demo")
    app.setApplicationVersion("1.0")
    
    # Create and show demo window
    demo = CareProviderDemo()
    demo.show()
    
    print("🏥 Celiogix Care Provider System Demo")
    print("=" * 50)
    print("Features demonstrated:")
    print("• Care Provider Management")
    print("• Health Log Integration")
    print("• Calendar Integration")
    print("• Contact Methods (Call/Email)")
    print("• Appointment Creation")
    print("• Mobile Sync Integration")
    print("=" * 50)
    print("Demo window opened. Try the demo actions!")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
