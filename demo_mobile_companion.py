#!/usr/bin/env python3
"""
Demo script for CeliacShield Mobile Companion Integration
Shows the mobile companion features and desktop command center
"""

import sys
import os
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QTabWidget
from PySide6.QtCore import Qt

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mobile_companion_integration import MobileCompanionIntegration
from services.gluten_risk_analyzer import get_gluten_risk_analyzer
from services.translation_cards import get_translation_cards_service


class MobileCompanionDemo(QMainWindow):
    """Demo application for mobile companion features"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌍 CeliacShield Mobile Companion Ecosystem - Demo")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize mobile companion integration
        self.mobile_integration = MobileCompanionIntegration()
        
        self.setup_ui()
        self.setup_demo_data()
    
    def setup_ui(self):
        """Set up the demo UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_label = QLabel("🌍 CeliacShield Mobile Companion Ecosystem")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background-color: #ecf0f1;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("""
        Desktop Command Center + Mobile Always-With-You Companion
        
        📱 Mobile App: Barcode scanning, symptom tracking, meal logging, restaurant finder, travel kit
        🖥️ Desktop App: Analytics, database management, travel planning, comprehensive reporting
        🔄 Real-time sync between devices for seamless celiac disease management
        """)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Tab widget for different demos
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add demo tabs
        self.setup_mobile_companion_tab()
        self.setup_gluten_analysis_tab()
        self.setup_translation_tab()
        self.setup_features_tab()
    
    def setup_mobile_companion_tab(self):
        """Set up mobile companion demo tab"""
        # Get the mobile companion panel
        mobile_panel = self.mobile_integration.get_mobile_companion_panel()
        self.tab_widget.addTab(mobile_panel, "📱 Mobile Companion")
    
    def setup_gluten_analysis_tab(self):
        """Set up gluten analysis demo tab"""
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)
        
        # Header
        header_label = QLabel("🔍 Gluten Risk Analysis Demo")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Demo products
        demo_products = [
            {
                'name': 'Udi\'s Gluten-Free Bread',
                'ingredients': 'Water, tapioca starch, brown rice flour, potato starch, canola oil, egg whites, sugar, yeast, salt, xanthan gum',
                'barcode': '123456789012'
            },
            {
                'name': 'Wheat Bread (Regular)',
                'ingredients': 'Wheat flour, water, yeast, salt, sugar, vegetable oil, preservatives',
                'barcode': '987654321098'
            },
            {
                'name': 'Soy Sauce (Questionable)',
                'ingredients': 'Soybeans, wheat, salt, water, preservatives',
                'barcode': '456789123456'
            }
        ]
        
        # Analyze each product
        analyzer = get_gluten_risk_analyzer()
        
        for product in demo_products:
            result = analyzer.analyze_product(
                product['name'], 
                product['ingredients'], 
                product['barcode']
            )
            
            # Create product analysis widget
            product_widget = self.create_product_analysis_widget(product, result)
            layout.addWidget(product_widget)
        
        layout.addStretch()
        self.tab_widget.addTab(analysis_widget, "🔍 Gluten Analysis")
    
    def create_product_analysis_widget(self, product, result):
        """Create widget for product analysis result"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        # Product name
        name_label = QLabel(f"📦 {product['name']}")
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(name_label)
        
        # Risk level with color coding
        risk_color = {
            'safe': '#27ae60',
            'low_risk': '#f39c12',
            'medium_risk': '#e67e22',
            'high_risk': '#e74c3c',
            'unsafe': '#c0392b',
            'unknown': '#95a5a6'
        }
        
        risk_label = QLabel(f"Risk Level: {result.risk_level.value.upper()}")
        risk_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {risk_color.get(result.risk_level.value, '#95a5a6')};
                background-color: rgba(255,255,255,0.8);
                padding: 5px;
                border-radius: 4px;
            }}
        """)
        layout.addWidget(risk_label)
        
        # Confidence score
        confidence_label = QLabel(f"Confidence: {result.confidence_score:.1%}")
        confidence_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        layout.addWidget(confidence_label)
        
        # Recommendation
        recommendation_label = QLabel(f"💡 {result.recommendation}")
        recommendation_label.setStyleSheet("font-size: 12px; color: #2c3e50; font-style: italic;")
        recommendation_label.setWordWrap(True)
        layout.addWidget(recommendation_label)
        
        # Problematic ingredients if any
        if result.problematic_ingredients:
            ingredients_label = QLabel(f"⚠️ Problematic: {', '.join(result.problematic_ingredients)}")
            ingredients_label.setStyleSheet("font-size: 11px; color: #e74c3c;")
            layout.addWidget(ingredients_label)
        
        return widget
    
    def setup_translation_tab(self):
        """Set up translation cards demo tab"""
        translation_widget = QWidget()
        layout = QVBoxLayout(translation_widget)
        
        # Header
        header_label = QLabel("🗣️ Translation Cards Demo")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Language selection
        from PySide6.QtWidgets import QComboBox, QTextEdit, QHBoxLayout
        
        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel("Select Language:"))
        
        language_combo = QComboBox()
        translation_service = get_translation_cards_service()
        languages = translation_service.get_available_languages()
        
        for lang_code in languages:
            lang_name = translation_service.get_language_name(lang_code)
            language_combo.addItem(f"{lang_name} ({lang_code.upper()})", lang_code)
        
        language_layout.addWidget(language_combo)
        language_layout.addStretch()
        
        layout.addLayout(language_layout)
        
        # Translation display
        translation_display = QTextEdit()
        translation_display.setReadOnly(True)
        translation_display.setMaximumHeight(200)
        translation_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        layout.addWidget(translation_display)
        
        # Update translation when language changes
        def update_translation():
            lang_code = language_combo.currentData()
            translation = translation_service.get_translation_card(lang_code)
            if translation:
                text = f"Language: {translation.language}\n\n"
                text += f"Message:\n{translation.message}\n\n"
                if translation.pronunciation:
                    text += f"Pronunciation: {translation.pronunciation}\n\n"
                if translation.cultural_notes:
                    text += f"Cultural Notes: {translation.cultural_notes}"
                translation_display.setPlainText(text)
        
        language_combo.currentTextChanged.connect(update_translation)
        update_translation()  # Show initial translation
        
        layout.addStretch()
        self.tab_widget.addTab(translation_widget, "🗣️ Translation Cards")
    
    def setup_features_tab(self):
        """Set up features overview tab"""
        features_widget = QWidget()
        layout = QVBoxLayout(features_widget)
        
        # Header
        header_label = QLabel("🌟 Mobile Companion Features Overview")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(header_label)
        
        # Features overview
        features_text = """
🌍 CELIOGIX MOBILE COMPANION ECOSYSTEM

📱 MOBILE APP FEATURES (Always-With-You):
• 🔍 Real-time barcode scanning with instant gluten risk analysis
• 📊 Symptom tracking and meal logging with photo capture
• 📅 Calendar integration for appointments and meal planning
• 🍴 Location-based restaurant finder with gluten-free filters
• ✈️ Travel kit mode with offline guides and translation cards
• 🗣️ Translation cards in 20+ languages for safe dining
• 💾 Offline cache of 100,000+ safe/unsafe products
• 🔄 Real-time sync with desktop command center

🖥️ DESKTOP COMMAND CENTER FEATURES:
• 📊 Comprehensive analytics and pattern recognition
• 🗃️ Product database management and updates
• 🌍 Travel planning with country-specific guides
• 📈 Health trend analysis and reporting
• 🔄 Data synchronization and backup
• 📤 Export capabilities for healthcare providers
• 🎛️ Advanced configuration and customization

🔄 INTEGRATION BENEFITS:
• Seamless data sync between mobile and desktop
• Comprehensive analytics combining all data sources
• Enhanced safety through real-time risk analysis
• Travel confidence with offline translation cards
• Pattern recognition for better health management
• Multi-device accessibility for complete coverage

🛡️ SECURITY & PRIVACY:
• End-to-end encryption for all sensitive data
• HIPAA compliance for health information
• Local data storage with optional cloud backup
• Granular privacy controls and data management
• Transparent data usage policies

🎯 TARGET OUTCOMES:
• Reduced gluten exposure through better scanning
• Improved symptom management through pattern recognition
• Enhanced travel confidence with translation support
• Better restaurant safety through community data
• Comprehensive health tracking for healthcare providers
        """
        
        features_display = QTextEdit()
        features_display.setPlainText(features_text)
        features_display.setReadOnly(True)
        features_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 15px;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(features_display)
        
        self.tab_widget.addTab(features_widget, "🌟 Features Overview")
    
    def setup_demo_data(self):
        """Set up demo data for the mobile companion"""
        # Simulate some mobile data
        mobile_sync = self.mobile_integration.mobile_sync
        
        # Add sample barcode scans
        sample_scans = [
            BarcodeScanData(
                barcode="123456789012",
                product_name="Udi's Gluten-Free Bread",
                brand="Udi's",
                gluten_status="safe",
                risk_level="low",
                scan_timestamp=datetime.now(),
                location="Whole Foods Market"
            ),
            BarcodeScanData(
                barcode="987654321098",
                product_name="Regular Wheat Bread",
                brand="Generic",
                gluten_status="unsafe",
                risk_level="high",
                scan_timestamp=datetime.now(),
                location="Local Grocery"
            )
        ]
        
        for scan in sample_scans:
            mobile_sync.add_barcode_scan(scan)
        
        # Add sample symptom logs
        sample_symptoms = [
            SymptomLogData(
                timestamp=datetime.now(),
                symptoms=["bloating", "fatigue"],
                severity=3,
                meal_context="Lunch at restaurant",
                location="Downtown"
            ),
            SymptomLogData(
                timestamp=datetime.now(),
                symptoms=["stomach pain", "nausea"],
                severity=7,
                meal_context="Dinner at home",
                location="Home"
            )
        ]
        
        for symptom in sample_symptoms:
            mobile_sync.add_symptom_log(symptom)
    
    def closeEvent(self, event):
        """Handle application close"""
        self.mobile_integration.shutdown()
        super().closeEvent(event)


def main():
    """Main function to run the demo"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("CeliacShield Mobile Companion Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = MobileCompanionDemo()
    demo.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
