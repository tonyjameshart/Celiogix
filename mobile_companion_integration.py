#!/usr/bin/env python3
"""
Mobile Companion Integration for CeliacShield Desktop Application
Main integration module that connects all mobile companion features
"""

import sys
import os
from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer, Signal, QObject

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.mobile_sync import get_mobile_sync_service, BarcodeScanData, SymptomLogData, MealLogData
from services.offline_cache import get_offline_cache_service
from services.translation_cards import get_translation_cards_service
from services.gluten_risk_analyzer import get_gluten_risk_analyzer, GlutenRiskResult
from panels.mobile_companion_panel import MobileCompanionPanel


class MobileCompanionIntegration(QObject):
    """Main integration class for mobile companion features"""
    
    # Signals
    mobile_data_received = Signal(str, dict)  # data_type, data
    sync_status_changed = Signal(bool)
    risk_alert = Signal(str, str)  # risk_level, message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize services
        self.mobile_sync = get_mobile_sync_service()
        self.offline_cache = get_offline_cache_service()
        self.translation_cards = get_translation_cards_service()
        self.gluten_analyzer = get_gluten_risk_analyzer()
        
        # Connect signals
        self.setup_signal_connections()
        
        # Initialize mobile companion panel
        self.mobile_panel = None
        
        # Start background services
        self.start_background_services()
    
    def setup_signal_connections(self):
        """Set up signal connections between services"""
        # Mobile sync signals
        self.mobile_sync.data_received.connect(self.on_mobile_data_received)
        self.mobile_sync.sync_finished.connect(self.sync_status_changed.emit)
        
        # Gluten analyzer signals
        self.gluten_analyzer.risk_detected.connect(self.on_risk_detected)
        
        # Translation cards signals
        self.translation_cards.translation_updated.connect(self.on_translation_updated)
    
    def start_background_services(self):
        """Start background services"""
        # Enable mobile sync with 30-second intervals
        self.mobile_sync.enable_auto_sync(30)
        
        # Start cache cleanup timer
        self.cache_cleanup_timer = QTimer()
        self.cache_cleanup_timer.timeout.connect(self.cleanup_cache)
        self.cache_cleanup_timer.start(3600000)  # 1 hour
    
    def on_mobile_data_received(self, data_type: str, data: dict):
        """Handle data received from mobile"""
        self.mobile_data_received.emit(data_type, data)
        
        # Process data based on type
        if data_type == 'barcode_scan':
            self.process_barcode_scan(data)
        elif data_type == 'symptom_log':
            self.process_symptom_log(data)
        elif data_type == 'meal_log':
            self.process_meal_log(data)
        elif data_type == 'restaurant_data':
            self.process_restaurant_data(data)
    
    def process_barcode_scan(self, scan_data: dict):
        """Process barcode scan data"""
        try:
            # Create barcode scan object
            scan = BarcodeScanData(
                barcode=scan_data.get('barcode', ''),
                product_name=scan_data.get('product_name', ''),
                brand=scan_data.get('brand', ''),
                gluten_status=scan_data.get('gluten_status', 'unknown'),
                risk_level=scan_data.get('risk_level', 'medium'),
                scan_timestamp=scan_data.get('scan_timestamp', ''),
                location=scan_data.get('location'),
                notes=scan_data.get('notes')
            )
            
            # Analyze for gluten risk if not already analyzed
            if scan.gluten_status == 'unknown' and scan_data.get('ingredients'):
                risk_result = self.gluten_analyzer.analyze_product(
                    scan.product_name,
                    scan_data.get('ingredients', ''),
                    scan.barcode
                )
                
                # Update scan data with analysis
                scan.gluten_status = risk_result.risk_level.value
                scan.risk_level = risk_result.risk_level.value
                if scan.notes:
                    scan.notes += f"\nAnalysis: {risk_result.recommendation}"
                else:
                    scan.notes = f"Analysis: {risk_result.recommendation}"
            
            # Cache the scan data
            self.offline_cache.cache_product_data(scan.barcode, {
                'name': scan.product_name,
                'brand': scan.brand,
                'gluten_status': scan.gluten_status,
                'risk_level': scan.risk_level,
                'confidence_score': 0.8
            })
            
        except Exception as e:
            print(f"Error processing barcode scan: {e}")
    
    def process_symptom_log(self, symptom_data: dict):
        """Process symptom log data"""
        try:
            # Create symptom log object
            log = SymptomLogData(
                timestamp=symptom_data.get('timestamp', ''),
                symptoms=symptom_data.get('symptoms', []),
                severity=symptom_data.get('severity', 5),
                meal_context=symptom_data.get('meal_context'),
                location=symptom_data.get('location'),
                notes=symptom_data.get('notes')
            )
            
            # Cache the symptom data
            cache_key = f"symptom_log_{log.timestamp}"
            self.offline_cache.cache_item(cache_key, {
                'timestamp': log.timestamp,
                'symptoms': log.symptoms,
                'severity': log.severity,
                'meal_context': log.meal_context,
                'location': log.location,
                'notes': log.notes
            }, 'symptom_log', ttl=86400)  # 24 hours
            
        except Exception as e:
            print(f"Error processing symptom log: {e}")
    
    def process_meal_log(self, meal_data: dict):
        """Process meal log data"""
        try:
            # Create meal log object
            log = MealLogData(
                timestamp=meal_data.get('timestamp', ''),
                meal_type=meal_data.get('meal_type', ''),
                items=meal_data.get('items', []),
                restaurant=meal_data.get('restaurant'),
                location=meal_data.get('location'),
                gluten_safety_confirmed=meal_data.get('gluten_safety_confirmed', False),
                notes=meal_data.get('notes')
            )
            
            # Cache the meal data
            cache_key = f"meal_log_{log.timestamp}"
            self.offline_cache.cache_item(cache_key, {
                'timestamp': log.timestamp,
                'meal_type': log.meal_type,
                'items': log.items,
                'restaurant': log.restaurant,
                'location': log.location,
                'gluten_safety_confirmed': log.gluten_safety_confirmed,
                'notes': log.notes
            }, 'meal_log', ttl=86400)  # 24 hours
            
        except Exception as e:
            print(f"Error processing meal log: {e}")
    
    def process_restaurant_data(self, restaurant_data: dict):
        """Process restaurant data"""
        try:
            # Cache the restaurant data
            self.offline_cache.cache_restaurant_data(restaurant_data)
            
        except Exception as e:
            print(f"Error processing restaurant data: {e}")
    
    def on_risk_detected(self, risk_level, problematic_ingredients):
        """Handle gluten risk detection"""
        risk_message = f"Gluten risk detected: {risk_level.value}"
        if problematic_ingredients:
            risk_message += f" - Problematic ingredients: {', '.join(problematic_ingredients)}"
        
        self.risk_alert.emit(risk_level.value, risk_message)
    
    def on_translation_updated(self, language_code: str, message: str):
        """Handle translation card update"""
        print(f"Translation updated for {language_code}: {message[:50]}...")
    
    def cleanup_cache(self):
        """Clean up expired cache items"""
        try:
            expired_count = self.offline_cache.cleanup_expired_cache()
            if expired_count > 0:
                print(f"Cleaned up {expired_count} expired cache items")
        except Exception as e:
            print(f"Error cleaning up cache: {e}")
    
    def get_mobile_companion_panel(self) -> MobileCompanionPanel:
        """Get or create mobile companion panel"""
        if self.mobile_panel is None:
            self.mobile_panel = MobileCompanionPanel()
        return self.mobile_panel
    
    def analyze_product_ingredients(self, product_name: str, ingredients: str, barcode: str = None) -> GlutenRiskResult:
        """Analyze product ingredients for gluten risk"""
        return self.gluten_analyzer.analyze_product(product_name, ingredients, barcode)
    
    def get_translation_card(self, language: str) -> str:
        """Get translation card for specified language"""
        card = self.translation_cards.get_translation_card(language)
        return card.message if card else ""
    
    def get_nearby_restaurants(self, latitude: float, longitude: float, radius_km: float = 5.0) -> List[Dict[str, Any]]:
        """Get nearby gluten-free restaurants"""
        return self.offline_cache.get_nearby_restaurants(latitude, longitude, radius_km)
    
    def get_safe_products(self) -> List[Dict[str, Any]]:
        """Get list of safe products from mobile scans"""
        return self.mobile_sync.get_safe_products()
    
    def get_unsafe_products(self) -> List[Dict[str, Any]]:
        """Get list of unsafe products from mobile scans"""
        return self.mobile_sync.get_unsafe_products()
    
    def get_symptom_patterns(self) -> Dict[str, Any]:
        """Get symptom pattern analysis"""
        return self.mobile_sync.get_symptom_patterns()
    
    def export_mobile_data(self, data_type: str) -> Dict[str, Any]:
        """Export mobile data for analysis"""
        return self.mobile_sync.export_mobile_data(data_type)
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.offline_cache.get_cache_statistics()
    
    def get_translation_statistics(self) -> Dict[str, Any]:
        """Get translation statistics"""
        return self.translation_cards.get_translation_statistics()
    
    def shutdown(self):
        """Shutdown mobile companion integration"""
        try:
            # Disable mobile sync
            self.mobile_sync.disable_auto_sync()
            
            # Stop timers
            if hasattr(self, 'cache_cleanup_timer'):
                self.cache_cleanup_timer.stop()
            
            print("Mobile companion integration shutdown complete")
            
        except Exception as e:
            print(f"Error during shutdown: {e}")


def create_mobile_companion_demo():
    """Create a demo application showing mobile companion features"""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("CeliacShield Mobile Companion - Desktop Command Center")
    window.setGeometry(100, 100, 1200, 800)
    
    # Create central widget with tabs
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # Create tab widget
    tab_widget = QTabWidget()
    layout.addWidget(tab_widget)
    
    # Initialize mobile companion integration
    mobile_integration = MobileCompanionIntegration()
    
    # Add mobile companion panel
    mobile_panel = mobile_integration.get_mobile_companion_panel()
    tab_widget.addTab(mobile_panel, "📱 Mobile Companion")
    
    # Add demo information
    from PySide6.QtWidgets import QLabel, QTextEdit
    
    demo_info = QTextEdit()
    demo_info.setPlainText("""
🌍 CELIOGIX MOBILE COMPANION ECOSYSTEM

DESKTOP COMMAND CENTER FEATURES:
✅ Real-time mobile data synchronization
✅ Barcode scan monitoring and analysis
✅ Symptom pattern tracking and analysis
✅ Meal logging and safety verification
✅ Restaurant finder with gluten-free filters
✅ Travel kit with offline translation cards
✅ Gluten risk analysis and product database
✅ Comprehensive data export and analytics

MOBILE APP FEATURES (Companion):
📱 Always-with-you barcode scanning
📱 Gluten risk determination in real-time
📱 Offline cache of safe/unsafe products
📱 Symptom tracking and meal logging
📱 Calendar view for appointments
📱 Location-based restaurant finder
📱 Travel kit mode with offline guides
📱 Translation cards in 20+ languages

INTEGRATION BENEFITS:
🔄 Seamless data sync between devices
📊 Comprehensive analytics and insights
🌐 Multi-language support for travel
🛡️ Enhanced safety through real-time analysis
📈 Pattern recognition for health management
💾 Offline capability for reliable access
🎯 Location-aware restaurant recommendations

The desktop app serves as the command center for comprehensive
celiac disease management, while the mobile app provides
always-available scanning and logging capabilities.
    """)
    demo_info.setReadOnly(True)
    tab_widget.addTab(demo_info, "ℹ️ About Mobile Companion")
    
    # Connect mobile integration signals
    mobile_integration.risk_alert.connect(lambda risk, msg: print(f"ALERT: {risk} - {msg}"))
    
    # Show window
    window.show()
    
    # Start the application
    sys.exit(app.exec())


if __name__ == "__main__":
    create_mobile_companion_demo()
