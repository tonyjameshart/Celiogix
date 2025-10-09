#!/usr/bin/env python3
"""
Mobile Companion Panel - Desktop command center for mobile app integration
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QTabWidget, QGroupBox,
    QTextEdit, QComboBox, QSpinBox, QCheckBox, QMessageBox,
    QProgressBar, QSplitter, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap, QIcon

from panels.base_panel import BasePanel
from panels.context_menu_mixin import ContextMenuMixin
from services.mobile_sync import (
    get_mobile_sync_service, BarcodeScanData, SymptomLogData, 
    MealLogData, RestaurantData, TravelKitData, ShoppingListItemData
)


class MobileCompanionPanel(ContextMenuMixin, BasePanel):
    """Mobile companion command center panel"""
    
    # Signals
    mobile_data_updated = Signal(str, dict)  # data_type, data
    sync_status_changed = Signal(bool)
    
    def __init__(self, master=None, app=None):
        super().__init__(master, app)
        self.mobile_sync = get_mobile_sync_service()
        self.setup_mobile_connections()
        self.setup_ui()
    
    def setup_mobile_connections(self):
        """Set up connections to mobile sync service"""
        self.mobile_sync.data_received.connect(self.on_mobile_data_received)
        self.mobile_sync.sync_finished.connect(self.on_sync_finished)
        self.mobile_sync.sync_started.connect(self.on_sync_started)
    
    def setup_ui(self):
        """Set up the mobile companion panel UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("📱 Mobile Companion Command Center")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Sync status indicator
        self.sync_status_label = QLabel("🔄 Syncing...")
        self.sync_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        header_layout.addWidget(self.sync_status_label)
        
        main_layout.addLayout(header_layout)
        
        # Main content tabs
        self.tab_widget = QTabWidget()
        self.setup_barcode_scan_tab()
        self.setup_symptom_tracking_tab()
        self.setup_meal_logging_tab()
        self.setup_restaurant_finder_tab()
        self.setup_travel_kit_tab()
        self.setup_shopping_list_tab()
        self.setup_mobile_recipes_tab()
        self.setup_analytics_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Control panel
        self.setup_control_panel(main_layout)
        
        # Enable mobile sync
        self.mobile_sync.enable_auto_sync(30)  # 30 second intervals
    
    def setup_barcode_scan_tab(self):
        """Set up barcode scan monitoring tab"""
        scan_widget = QWidget()
        layout = QVBoxLayout(scan_widget)
        
        # Scan summary
        summary_group = QGroupBox("📊 Scan Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.scan_stats_layout = QHBoxLayout()
        self.safe_scans_label = QLabel("Safe Scans: 0")
        self.unsafe_scans_label = QLabel("Unsafe Scans: 0")
        self.unknown_scans_label = QLabel("Unknown Scans: 0")
        
        self.scan_stats_layout.addWidget(self.safe_scans_label)
        self.scan_stats_layout.addWidget(self.unsafe_scans_label)
        self.scan_stats_layout.addWidget(self.unknown_scans_label)
        self.scan_stats_layout.addStretch()
        
        summary_layout.addLayout(self.scan_stats_layout)
        layout.addWidget(summary_group)
        
        # Recent scans table
        recent_group = QGroupBox("🔍 Recent Scans")
        recent_layout = QVBoxLayout(recent_group)
        
        self.scans_table = QTableWidget()
        self.scans_table.setColumnCount(6)
        self.scans_table.setHorizontalHeaderLabels([
            "Timestamp", "Product", "Brand", "Status", "Risk", "Location"
        ])
        self.scans_table.horizontalHeader().setStretchLastSection(True)
        self.scans_table.setAlternatingRowColors(True)
        self.scans_table.setMaximumHeight(300)
        
        recent_layout.addWidget(self.scans_table)
        layout.addWidget(recent_group)
        
        # Product database
        db_group = QGroupBox("🗃️ Product Database")
        db_layout = QVBoxLayout(db_group)
        
        db_controls_layout = QHBoxLayout()
        refresh_db_btn = QPushButton("🔄 Refresh Database")
        export_db_btn = QPushButton("📤 Export Database")
        search_db_btn = QPushButton("🔍 Search Products")
        
        refresh_db_btn.clicked.connect(self.refresh_product_database)
        export_db_btn.clicked.connect(self.export_product_database)
        search_db_btn.clicked.connect(self.search_products)
        
        db_controls_layout.addWidget(refresh_db_btn)
        db_controls_layout.addWidget(export_db_btn)
        db_controls_layout.addWidget(search_db_btn)
        db_controls_layout.addStretch()
        
        db_layout.addLayout(db_controls_layout)
        
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels([
            "Barcode", "Product Name", "Brand", "Status", "Last Scan"
        ])
        self.product_table.horizontalHeader().setStretchLastSection(True)
        self.product_table.setAlternatingRowColors(True)
        
        db_layout.addWidget(self.product_table)
        layout.addWidget(db_group)
        
        self.tab_widget.addTab(scan_widget, "📱 Barcode Scans")
    
    def setup_symptom_tracking_tab(self):
        """Set up enhanced symptom tracking tab"""
        symptom_widget = QWidget()
        layout = QVBoxLayout(symptom_widget)
        
        # Enhanced symptom summary
        summary_group = QGroupBox("📊 Enhanced Symptom Tracking Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.symptom_stats_layout = QHBoxLayout()
        self.total_symptoms_label = QLabel("Total Logs: 0")
        self.avg_severity_label = QLabel("Avg Severity: 0.0")
        self.emergency_alerts_label = QLabel("Emergency Alerts: 0")
        self.patterns_detected_label = QLabel("Patterns: 0")
        
        self.symptom_stats_layout.addWidget(self.total_symptoms_label)
        self.symptom_stats_layout.addWidget(self.avg_severity_label)
        self.symptom_stats_layout.addWidget(self.emergency_alerts_label)
        self.symptom_stats_layout.addWidget(self.patterns_detected_label)
        self.symptom_stats_layout.addStretch()
        
        summary_layout.addLayout(self.symptom_stats_layout)
        layout.addWidget(summary_group)
        
        # Quick entry templates
        templates_group = QGroupBox("⚡ Quick Entry Templates")
        templates_layout = QVBoxLayout(templates_group)
        
        templates_buttons_layout = QHBoxLayout()
        
        mild_symptoms_btn = QPushButton("😐 Mild Symptoms")
        mild_symptoms_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; border-radius: 3px;")
        mild_symptoms_btn.clicked.connect(lambda: self.use_health_template("mild_symptoms"))
        
        moderate_symptoms_btn = QPushButton("😟 Moderate Symptoms")
        moderate_symptoms_btn.setStyleSheet("background-color: #f39c12; color: white; padding: 8px; border-radius: 3px;")
        moderate_symptoms_btn.clicked.connect(lambda: self.use_health_template("moderate_symptoms"))
        
        severe_symptoms_btn = QPushButton("😰 Severe Symptoms")
        severe_symptoms_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px; border-radius: 3px;")
        severe_symptoms_btn.clicked.connect(lambda: self.use_health_template("severe_symptoms"))
        
        gluten_reaction_btn = QPushButton("🌾 Gluten Reaction")
        gluten_reaction_btn.setStyleSheet("background-color: #8e44ad; color: white; padding: 8px; border-radius: 3px;")
        gluten_reaction_btn.clicked.connect(lambda: self.use_health_template("gluten_reaction"))
        
        templates_buttons_layout.addWidget(mild_symptoms_btn)
        templates_buttons_layout.addWidget(moderate_symptoms_btn)
        templates_buttons_layout.addWidget(severe_symptoms_btn)
        templates_buttons_layout.addWidget(gluten_reaction_btn)
        templates_buttons_layout.addStretch()
        
        templates_layout.addLayout(templates_buttons_layout)
        layout.addWidget(templates_group)
        
        # Symptom patterns
        patterns_group = QGroupBox("📈 Symptom Patterns & Analytics")
        patterns_layout = QVBoxLayout(patterns_group)
        
        self.symptom_patterns_text = QTextEdit()
        self.symptom_patterns_text.setMaximumHeight(150)
        self.symptom_patterns_text.setReadOnly(True)
        patterns_layout.addWidget(self.symptom_patterns_text)
        
        layout.addWidget(patterns_group)
        
        # Enhanced symptom logs
        logs_group = QGroupBox("📝 Enhanced Symptom Logs")
        logs_layout = QVBoxLayout(logs_group)
        
        self.symptom_table = QTableWidget()
        self.symptom_table.setColumnCount(7)
        self.symptom_table.setHorizontalHeaderLabels([
            "Timestamp", "Symptoms", "Severity", "Emergency", "Location", "Media", "Notes"
        ])
        self.symptom_table.horizontalHeader().setStretchLastSection(True)
        self.symptom_table.setAlternatingRowColors(True)
        self.symptom_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.symptom_table.itemDoubleClicked.connect(self.view_symptom_details)
        
        logs_layout.addWidget(self.symptom_table)
        layout.addWidget(logs_group)
        
        # Smart Reminders Section
        reminders_group = QGroupBox("🔔 Smart Health Reminders")
        reminders_layout = QVBoxLayout(reminders_group)
        
        # Reminder controls
        reminder_controls_layout = QHBoxLayout()
        
        add_meal_reminder_btn = QPushButton("🍽️ Add Meal Reminder")
        add_meal_reminder_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; border-radius: 3px;")
        add_meal_reminder_btn.clicked.connect(self.add_smart_meal_reminder)
        
        add_symptom_reminder_btn = QPushButton("🏥 Add Symptom Reminder")
        add_symptom_reminder_btn.setStyleSheet("background-color: #e67e22; color: white; padding: 8px; border-radius: 3px;")
        add_symptom_reminder_btn.clicked.connect(self.add_smart_symptom_reminder)
        
        view_notifications_btn = QPushButton("🔔 View Notifications")
        view_notifications_btn.setStyleSheet("background-color: #3498db; color: white; padding: 8px; border-radius: 3px;")
        view_notifications_btn.clicked.connect(self.view_smart_notifications)
        
        reminder_controls_layout.addWidget(add_meal_reminder_btn)
        reminder_controls_layout.addWidget(add_symptom_reminder_btn)
        reminder_controls_layout.addWidget(view_notifications_btn)
        reminder_controls_layout.addStretch()
        
        reminders_layout.addLayout(reminder_controls_layout)
        
        # Active reminders display
        self.active_reminders_text = QTextEdit()
        self.active_reminders_text.setMaximumHeight(120)
        self.active_reminders_text.setReadOnly(True)
        reminders_layout.addWidget(self.active_reminders_text)
        
        layout.addWidget(reminders_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        add_symptom_btn = QPushButton("➕ Add Symptom Log")
        add_symptom_btn.clicked.connect(self.add_symptom_log)
        
        view_details_btn = QPushButton("👁️ View Details")
        view_details_btn.clicked.connect(self.view_symptom_details)
        view_details_btn.setEnabled(False)
        
        export_symptoms_btn = QPushButton("📤 Export Symptoms")
        export_symptoms_btn.clicked.connect(self.export_symptom_data)
        
        clear_symptoms_btn = QPushButton("🗑️ Clear All")
        clear_symptoms_btn.clicked.connect(self.clear_symptom_logs)
        
        action_layout.addWidget(add_symptom_btn)
        action_layout.addWidget(view_details_btn)
        action_layout.addWidget(export_symptoms_btn)
        action_layout.addWidget(clear_symptoms_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        # Connect selection changes
        self.symptom_table.selectionModel().selectionChanged.connect(
            lambda: view_details_btn.setEnabled(len(self.symptom_table.selectedItems()) > 0)
        )
        
        self.tab_widget.addTab(symptom_widget, "🏥 Enhanced Symptom Tracking")
    
    def setup_meal_logging_tab(self):
        """Set up meal logging tab"""
        meal_widget = QWidget()
        layout = QVBoxLayout(meal_widget)
        
        # Meal summary
        summary_group = QGroupBox("🍽️ Meal Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.meal_stats_layout = QHBoxLayout()
        self.total_meals_label = QLabel("Total Meals: 0")
        self.safe_meals_label = QLabel("Safe Meals: 0")
        self.restaurant_meals_label = QLabel("Restaurant Meals: 0")
        
        self.meal_stats_layout.addWidget(self.total_meals_label)
        self.meal_stats_layout.addWidget(self.safe_meals_label)
        self.meal_stats_layout.addWidget(self.restaurant_meals_label)
        self.meal_stats_layout.addStretch()
        
        summary_layout.addLayout(self.meal_stats_layout)
        layout.addWidget(summary_group)
        
        # Meal logs
        logs_group = QGroupBox("📝 Meal Logs")
        logs_layout = QVBoxLayout(logs_group)
        
        self.meal_table = QTableWidget()
        self.meal_table.setColumnCount(6)
        self.meal_table.setHorizontalHeaderLabels([
            "Timestamp", "Meal Type", "Items", "Restaurant", "Location", "Safety Confirmed"
        ])
        self.meal_table.horizontalHeader().setStretchLastSection(True)
        self.meal_table.setAlternatingRowColors(True)
        
        logs_layout.addWidget(self.meal_table)
        layout.addWidget(logs_group)
        
        self.tab_widget.addTab(meal_widget, "🍽️ Meal Logging")
    
    def setup_restaurant_finder_tab(self):
        """Set up restaurant finder tab"""
        restaurant_widget = QWidget()
        layout = QVBoxLayout(restaurant_widget)
        
        # Location controls
        location_group = QGroupBox("📍 Location & Search")
        location_layout = QVBoxLayout(location_group)
        
        location_controls = QHBoxLayout()
        location_label = QLabel("Search Radius:")
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 50)
        self.radius_spin.setValue(5)
        self.radius_spin.setSuffix(" km")
        
        search_btn = QPushButton("🔍 Find Nearby Restaurants")
        search_btn.clicked.connect(self.search_nearby_restaurants)
        
        location_controls.addWidget(location_label)
        location_controls.addWidget(self.radius_spin)
        location_controls.addWidget(search_btn)
        location_controls.addStretch()
        
        location_layout.addLayout(location_controls)
        layout.addWidget(location_group)
        
        # Restaurant results
        results_group = QGroupBox("🍴 Nearby Gluten-Free Restaurants")
        results_layout = QVBoxLayout(results_group)
        
        self.restaurant_table = QTableWidget()
        self.restaurant_table.setColumnCount(7)
        self.restaurant_table.setHorizontalHeaderLabels([
            "Name", "Cuisine", "Distance", "GF Options", "Dedicated Kitchen", "Staff Training", "Rating"
        ])
        self.restaurant_table.horizontalHeader().setStretchLastSection(True)
        self.restaurant_table.setAlternatingRowColors(True)
        
        results_layout.addWidget(self.restaurant_table)
        layout.addWidget(results_group)
        
        self.tab_widget.addTab(restaurant_widget, "🍴 Restaurant Finder")
    
    def setup_travel_kit_tab(self):
        """Set up travel kit tab"""
        travel_widget = QWidget()
        layout = QVBoxLayout(travel_widget)
        
        # Travel kit selection
        selection_group = QGroupBox("🌍 Travel Kit Selection")
        selection_layout = QVBoxLayout(selection_group)
        
        kit_controls = QHBoxLayout()
        country_label = QLabel("Country:")
        self.country_combo = QComboBox()
        self.country_combo.addItems([
            "Spain", "France", "Italy", "Germany", "Japan", "China", 
            "Mexico", "Brazil", "India", "Australia", "Canada"
        ])
        
        load_kit_btn = QPushButton("📥 Load Travel Kit")
        load_kit_btn.clicked.connect(self.load_travel_kit)
        
        kit_controls.addWidget(country_label)
        kit_controls.addWidget(self.country_combo)
        kit_controls.addWidget(load_kit_btn)
        kit_controls.addStretch()
        
        selection_layout.addLayout(kit_controls)
        layout.addWidget(selection_group)
        
        # Translation cards
        translation_group = QGroupBox("🗣️ Translation Cards")
        translation_layout = QVBoxLayout(translation_group)
        
        language_controls = QHBoxLayout()
        language_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "English", "Spanish", "French", "German", "Italian", 
            "Portuguese", "Japanese", "Chinese", "Arabic", "Hindi"
        ])
        
        show_translation_btn = QPushButton("📋 Show Translation")
        show_translation_btn.clicked.connect(self.show_translation_card)
        
        language_controls.addWidget(language_label)
        language_controls.addWidget(self.language_combo)
        language_controls.addWidget(show_translation_btn)
        language_controls.addStretch()
        
        translation_layout.addLayout(language_controls)
        
        self.translation_text = QTextEdit()
        self.translation_text.setMaximumHeight(200)
        self.translation_text.setReadOnly(True)
        translation_layout.addWidget(self.translation_text)
        
        layout.addWidget(translation_group)
        
        # Safe restaurants in country
        country_restaurants_group = QGroupBox("🍴 Safe Restaurants in Country")
        country_restaurants_layout = QVBoxLayout(country_restaurants_group)
        
        self.country_restaurant_table = QTableWidget()
        self.country_restaurant_table.setColumnCount(4)
        self.country_restaurant_table.setHorizontalHeaderLabels([
            "Name", "Location", "Cuisine Type", "Rating"
        ])
        self.country_restaurant_table.horizontalHeader().setStretchLastSection(True)
        self.country_restaurant_table.setAlternatingRowColors(True)
        
        country_restaurants_layout.addWidget(self.country_restaurant_table)
        layout.addWidget(country_restaurants_group)
        
        self.tab_widget.addTab(travel_widget, "✈️ Travel Kit")
    
    def setup_shopping_list_tab(self):
        """Set up shopping list tab"""
        shopping_widget = QWidget()
        layout = QVBoxLayout(shopping_widget)
        
        # Shopping list summary
        summary_group = QGroupBox("📋 Shopping List Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.shopping_stats_layout = QHBoxLayout()
        self.total_items_label = QLabel("Total Items: 0")
        self.purchased_items_label = QLabel("Purchased: 0")
        self.pending_items_label = QLabel("Pending: 0")
        self.completion_label = QLabel("Completion: 0%")
        
        self.shopping_stats_layout.addWidget(self.total_items_label)
        self.shopping_stats_layout.addWidget(self.purchased_items_label)
        self.shopping_stats_layout.addWidget(self.pending_items_label)
        self.shopping_stats_layout.addWidget(self.completion_label)
        self.shopping_stats_layout.addStretch()
        
        summary_layout.addLayout(self.shopping_stats_layout)
        layout.addWidget(summary_group)
        
        # Filters
        filter_group = QGroupBox("🔍 Filters")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Store:"))
        self.shopping_store_filter = QComboBox()
        self.shopping_store_filter.addItems([
            "All Stores", "Grocery Store", "Health Food Store", 
            "Farmers Market", "Bulk Store", "Online Order", "Specialty Store", "Other"
        ])
        self.shopping_store_filter.currentTextChanged.connect(self.filter_shopping_by_store)
        filter_layout.addWidget(self.shopping_store_filter)
        
        filter_layout.addWidget(QLabel("Category:"))
        self.shopping_category_filter = QComboBox()
        self.shopping_category_filter.addItems([
            "All Categories", "Produce", "Meat & Seafood", "Dairy & Eggs", 
            "Pantry", "Frozen", "Bakery (GF)", "Beverages", "Health & Beauty", "Other"
        ])
        self.shopping_category_filter.currentTextChanged.connect(self.filter_shopping_by_category)
        filter_layout.addWidget(self.shopping_category_filter)
        
        filter_layout.addStretch()
        layout.addWidget(filter_group)
        
        # Shopping list table
        shopping_list_group = QGroupBox("🛒 Shopping List Items")
        shopping_list_layout = QVBoxLayout(shopping_list_group)
        
        self.shopping_table = QTableWidget()
        self.shopping_table.setColumnCount(8)
        self.shopping_table.setHorizontalHeaderLabels([
            "Item", "Quantity", "Store", "Category", "Priority", "Purchased", "Gluten-Free", "Notes"
        ])
        self.shopping_table.horizontalHeader().setStretchLastSection(True)
        self.shopping_table.setAlternatingRowColors(True)
        self.shopping_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.shopping_table.itemChanged.connect(self.on_shopping_item_changed)
        
        shopping_list_layout.addWidget(self.shopping_table)
        layout.addWidget(shopping_list_group)
        
        # Action buttons
        action_group = QGroupBox("⚙️ Actions")
        action_layout = QHBoxLayout(action_group)
        
        add_item_btn = QPushButton("➕ Add Item")
        add_item_btn.clicked.connect(self.add_shopping_item)
        
        mark_purchased_btn = QPushButton("✅ Mark as Purchased")
        mark_purchased_btn.clicked.connect(self.mark_items_purchased)
        
        clear_purchased_btn = QPushButton("🗑️ Clear Purchased")
        clear_purchased_btn.clicked.connect(self.clear_purchased_items)
        
        export_shopping_btn = QPushButton("📤 Export Shopping List")
        export_shopping_btn.clicked.connect(self.export_shopping_list_data)
        
        action_layout.addWidget(add_item_btn)
        action_layout.addWidget(mark_purchased_btn)
        action_layout.addWidget(clear_purchased_btn)
        action_layout.addWidget(export_shopping_btn)
        action_layout.addStretch()
        
        layout.addWidget(action_group)
        
        self.tab_widget.addTab(shopping_widget, "🛒 Shopping List")
    
    def setup_mobile_recipes_tab(self):
        """Set up mobile recipes tab"""
        recipes_widget = QWidget()
        layout = QVBoxLayout(recipes_widget)
        
        # Recipe summary
        summary_group = QGroupBox("📱 Mobile Recipes Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.recipe_stats_layout = QHBoxLayout()
        self.total_recipes_label = QLabel("Total Recipes: 0")
        self.categories_label = QLabel("Categories: 0")
        self.last_pushed_label = QLabel("Last Pushed: Never")
        
        self.recipe_stats_layout.addWidget(self.total_recipes_label)
        self.recipe_stats_layout.addWidget(self.categories_label)
        self.recipe_stats_layout.addWidget(self.last_pushed_label)
        self.recipe_stats_layout.addStretch()
        
        summary_layout.addLayout(self.recipe_stats_layout)
        layout.addWidget(summary_group)
        
        # Recipe filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category Filter:"))
        
        self.recipe_category_filter = QComboBox()
        self.recipe_category_filter.addItem("All Categories")
        self.recipe_category_filter.currentTextChanged.connect(self.filter_mobile_recipes)
        filter_layout.addWidget(self.recipe_category_filter)
        
        filter_layout.addStretch()
        
        refresh_recipes_btn = QPushButton("🔄 Refresh")
        refresh_recipes_btn.clicked.connect(self.refresh_mobile_recipes)
        filter_layout.addWidget(refresh_recipes_btn)
        
        layout.addLayout(filter_layout)
        
        # Recipe list
        self.recipes_table = QTableWidget()
        self.recipes_table.setColumnCount(6)
        self.recipes_table.setHorizontalHeaderLabels([
            "Recipe Name", "Category", "Prep Time", "Cook Time", "Servings", "Difficulty"
        ])
        self.recipes_table.horizontalHeader().setStretchLastSection(True)
        self.recipes_table.setAlternatingRowColors(True)
        self.recipes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recipes_table.itemDoubleClicked.connect(self.view_mobile_recipe)
        layout.addWidget(self.recipes_table)
        
        # Recipe actions
        recipe_actions_layout = QHBoxLayout()
        
        view_recipe_btn = QPushButton("👁️ View Recipe")
        view_recipe_btn.clicked.connect(self.view_mobile_recipe)
        view_recipe_btn.setEnabled(False)
        
        export_recipes_btn = QPushButton("📤 Export Recipes")
        export_recipes_btn.clicked.connect(self.export_mobile_recipes)
        
        clear_recipes_btn = QPushButton("🗑️ Clear All")
        clear_recipes_btn.clicked.connect(self.clear_mobile_recipes)
        
        recipe_actions_layout.addWidget(view_recipe_btn)
        recipe_actions_layout.addWidget(export_recipes_btn)
        recipe_actions_layout.addWidget(clear_recipes_btn)
        recipe_actions_layout.addStretch()
        
        layout.addLayout(recipe_actions_layout)
        
        # Connect selection changes
        self.recipes_table.selectionModel().selectionChanged.connect(
            lambda: view_recipe_btn.setEnabled(len(self.recipes_table.selectedItems()) > 0)
        )
        
        self.tab_widget.addTab(recipes_widget, "📖 Mobile Recipes")
    
    def setup_analytics_tab(self):
        """Set up analytics and insights tab"""
        analytics_widget = QWidget()
        layout = QVBoxLayout(analytics_widget)
        
        # Data insights
        insights_group = QGroupBox("📊 Data Insights")
        insights_layout = QVBoxLayout(insights_group)
        
        self.insights_text = QTextEdit()
        self.insights_text.setMaximumHeight(200)
        self.insights_text.setReadOnly(True)
        insights_layout.addWidget(self.insights_text)
        
        layout.addWidget(insights_group)
        
        # Export options
        export_group = QGroupBox("📤 Data Export")
        export_layout = QVBoxLayout(export_group)
        
        export_buttons_layout = QHBoxLayout()
        
        export_all_btn = QPushButton("📊 Export All Data")
        export_scans_btn = QPushButton("📱 Export Scans")
        export_symptoms_btn = QPushButton("🏥 Export Symptoms")
        export_meals_btn = QPushButton("🍽️ Export Meals")
        export_shopping_btn = QPushButton("🛒 Export Shopping List")
        
        export_all_btn.clicked.connect(self.export_all_data)
        export_scans_btn.clicked.connect(self.export_scan_data)
        export_symptoms_btn.clicked.connect(self.export_symptom_data)
        export_meals_btn.clicked.connect(self.export_meal_data)
        export_shopping_btn.clicked.connect(self.export_shopping_list_data)
        
        export_buttons_layout.addWidget(export_all_btn)
        export_buttons_layout.addWidget(export_scans_btn)
        export_buttons_layout.addWidget(export_symptoms_btn)
        export_buttons_layout.addWidget(export_meals_btn)
        export_buttons_layout.addWidget(export_shopping_btn)
        
        export_layout.addLayout(export_buttons_layout)
        layout.addWidget(export_group)
        
        self.tab_widget.addTab(analytics_widget, "📊 Analytics")
    
    def setup_control_panel(self, parent_layout):
        """Set up control panel"""
        control_group = QGroupBox("🎛️ Mobile Sync Controls")
        control_layout = QHBoxLayout(control_group)
        
        # Sync controls
        sync_controls = QHBoxLayout()
        
        self.auto_sync_checkbox = QCheckBox("Enable Auto Sync")
        self.auto_sync_checkbox.setChecked(True)
        self.auto_sync_checkbox.toggled.connect(self.toggle_auto_sync)
        
        sync_now_btn = QPushButton("🔄 Sync Now")
        sync_now_btn.clicked.connect(self.manual_sync)
        
        sync_controls.addWidget(self.auto_sync_checkbox)
        sync_controls.addWidget(sync_now_btn)
        
        # Sync interval
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Sync Interval:")
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setRange(10, 300)
        self.sync_interval_spin.setValue(30)
        self.sync_interval_spin.setSuffix(" sec")
        self.sync_interval_spin.valueChanged.connect(self.update_sync_interval)
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.sync_interval_spin)
        
        control_layout.addLayout(sync_controls)
        control_layout.addLayout(interval_layout)
        control_layout.addStretch()
        
        parent_layout.addWidget(control_group)
    
    def on_mobile_data_received(self, data_type: str, data: dict):
        """Handle data received from mobile"""
        self.mobile_data_updated.emit(data_type, data)
        
        # Update UI based on data type
        if data_type == 'barcode_scan':
            self.update_barcode_scan_display()
        elif data_type == 'symptom_log':
            self.update_symptom_display()
        elif data_type == 'meal_log':
            self.update_meal_display()
        elif data_type == 'restaurant_data':
            self.update_restaurant_display()
        elif data_type == 'shopping_list_item':
            self.update_shopping_list_display()
        elif data_type == 'mobile_recipe':
            self.update_mobile_recipes_display()
    
    def on_sync_started(self):
        """Handle sync started"""
        self.sync_status_label.setText("🔄 Syncing...")
        self.sync_status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
    
    def on_sync_finished(self, success: bool):
        """Handle sync finished"""
        if success:
            self.sync_status_label.setText("✅ Synced")
            self.sync_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.sync_status_label.setText("❌ Sync Failed")
            self.sync_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def update_barcode_scan_display(self):
        """Update barcode scan display"""
        scans = self.mobile_sync.barcode_scans
        
        # Update stats
        safe_count = sum(1 for scan in scans if scan.gluten_status == 'safe')
        unsafe_count = sum(1 for scan in scans if scan.gluten_status == 'unsafe')
        unknown_count = sum(1 for scan in scans if scan.gluten_status == 'unknown')
        
        self.safe_scans_label.setText(f"Safe Scans: {safe_count}")
        self.unsafe_scans_label.setText(f"Unsafe Scans: {unsafe_count}")
        self.unknown_scans_label.setText(f"Unknown Scans: {unknown_count}")
        
        # Update table
        self.scans_table.setRowCount(len(scans))
        for row, scan in enumerate(scans[-10:]):  # Show last 10 scans
            self.scans_table.setItem(row, 0, QTableWidgetItem(scan.scan_timestamp.strftime("%m/%d %H:%M")))
            self.scans_table.setItem(row, 1, QTableWidgetItem(scan.product_name))
            self.scans_table.setItem(row, 2, QTableWidgetItem(scan.brand))
            
            status_item = QTableWidgetItem(scan.gluten_status.title())
            if scan.gluten_status == 'safe':
                status_item.setBackground(Qt.green)
            elif scan.gluten_status == 'unsafe':
                status_item.setBackground(Qt.red)
            else:
                status_item.setBackground(Qt.yellow)
            self.scans_table.setItem(row, 3, status_item)
            
            self.scans_table.setItem(row, 4, QTableWidgetItem(scan.risk_level.title()))
            self.scans_table.setItem(row, 5, QTableWidgetItem(scan.location or "Unknown"))
    
    def update_symptom_display(self):
        """Update enhanced symptom tracking display"""
        logs = self.mobile_sync.symptom_logs
        
        # Update patterns
        patterns = self.mobile_sync.get_symptom_patterns()
        if patterns:
            patterns_text = f"""
Total Symptom Logs: {patterns['total_logs']}
Average Severity: {patterns['average_severity']:.1f}/10

Most Common Symptoms:
"""
            for symptom, count in patterns['most_common_symptoms'][:5]:
                patterns_text += f"• {symptom}: {count} occurrences\n"
            
            self.symptom_patterns_text.setPlainText(patterns_text)
        
        # Update enhanced summary
        emergency_count = 0
        pattern_count = 0
        
        for log in logs:
            emergency_level = getattr(log, 'emergency_level', 'normal')
            if emergency_level in ['urgent', 'emergency']:
                emergency_count += 1
            
            if hasattr(log, 'triggers_suspected') and log.triggers_suspected:
                pattern_count += 1
        
        total_symptoms = len(logs)
        avg_severity = sum(log.severity for log in logs) / total_symptoms if total_symptoms > 0 else 0
        
        self.total_symptoms_label.setText(f"Total Logs: {total_symptoms}")
        self.avg_severity_label.setText(f"Avg Severity: {avg_severity:.1f}")
        self.emergency_alerts_label.setText(f"Emergency Alerts: {emergency_count}")
        self.patterns_detected_label.setText(f"Patterns: {pattern_count}")
        
        # Update pattern analysis
        self.update_symptom_patterns_display()
        
        # Update enhanced table
        self.symptom_table.setRowCount(0)
        for log in logs[-20:]:  # Show last 20 logs
            row = self.symptom_table.rowCount()
            self.symptom_table.insertRow(row)
            
            # Enhanced columns
            self.symptom_table.setItem(row, 0, QTableWidgetItem(log.timestamp.strftime("%m/%d %H:%M")))
            self.symptom_table.setItem(row, 1, QTableWidgetItem(", ".join(log.symptoms)))
            self.symptom_table.setItem(row, 2, QTableWidgetItem(f"{log.severity}/10"))
            
            # Emergency level
            emergency_level = getattr(log, 'emergency_level', 'normal')
            self.symptom_table.setItem(row, 3, QTableWidgetItem(emergency_level))
            
            # Location
            location = log.location or 'Not specified'
            self.symptom_table.setItem(row, 4, QTableWidgetItem(location))
            
            # Media attachments
            media_info = []
            if hasattr(log, 'voice_note_path') and log.voice_note_path:
                media_info.append("🎤 Voice")
            if hasattr(log, 'photo_paths') and log.photo_paths:
                media_info.append(f"📷 {len(log.photo_paths)} Photos")
            
            media_str = ', '.join(media_info) if media_info else 'None'
            self.symptom_table.setItem(row, 5, QTableWidgetItem(media_str))
            
            # Notes (truncated)
            notes = log.notes or ''
            if len(notes) > 50:
                notes = notes[:47] + "..."
            self.symptom_table.setItem(row, 6, QTableWidgetItem(notes))
    
    def update_symptom_patterns_display(self):
        """Update symptom patterns analysis display"""
        logs = self.mobile_sync.symptom_logs
        
        if not logs:
            self.symptom_patterns_text.setPlainText("No symptom data available for pattern analysis.")
            return
        
        # Basic pattern analysis
        patterns_text = f"""📊 Recent Symptom Analysis:
        
Total Logs: {len(logs)}
Average Severity: {sum(log.severity for log in logs) / len(logs):.1f}/10

🔍 Pattern Insights:
"""
        
        # Count symptoms
        symptom_counts = {}
        for log in logs:
            for symptom in log.symptoms:
                symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
        
        # Most common symptoms
        most_common = sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        patterns_text += "\nMost Frequent Symptoms:\n"
        for symptom, count in most_common:
            patterns_text += f"• {symptom}: {count} times\n"
        
        # Emergency patterns
        emergency_logs = [log for log in logs if getattr(log, 'emergency_level', 'normal') in ['urgent', 'emergency']]
        if emergency_logs:
            patterns_text += f"\n🚨 Emergency Events: {len(emergency_logs)} recent incidents\n"
        
        # Trigger patterns
        trigger_logs = [log for log in logs if hasattr(log, 'triggers_suspected') and log.triggers_suspected]
        if trigger_logs:
            patterns_text += f"🔍 Triggered Events: {len(trigger_logs)} with suspected triggers\n"
        
        # Time patterns (simplified)
        recent_logs = [log for log in logs if log.timestamp.date() == datetime.now().date()]
        if recent_logs:
            patterns_text += f"📅 Today's Logs: {len(recent_logs)} entries\n"
        
        self.symptom_patterns_text.setPlainText(patterns_text.strip())
    
    def update_meal_display(self):
        """Update meal logging display"""
        logs = self.mobile_sync.meal_logs
        
        # Update stats
        total_meals = len(logs)
        safe_meals = sum(1 for log in logs if log.gluten_safety_confirmed)
        restaurant_meals = sum(1 for log in logs if log.restaurant)
        
        self.total_meals_label.setText(f"Total Meals: {total_meals}")
        self.safe_meals_label.setText(f"Safe Meals: {safe_meals}")
        self.restaurant_meals_label.setText(f"Restaurant Meals: {restaurant_meals}")
        
        # Update table
        self.meal_table.setRowCount(len(logs))
        for row, log in enumerate(logs[-20:]):  # Show last 20 logs
            self.meal_table.setItem(row, 0, QTableWidgetItem(log.timestamp.strftime("%m/%d %H:%M")))
            self.meal_table.setItem(row, 1, QTableWidgetItem(log.meal_type.title()))
            self.meal_table.setItem(row, 2, QTableWidgetItem(", ".join(log.items)))
            self.meal_table.setItem(row, 3, QTableWidgetItem(log.restaurant or ""))
            self.meal_table.setItem(row, 4, QTableWidgetItem(log.location or ""))
            
            safety_item = QTableWidgetItem("✅ Yes" if log.gluten_safety_confirmed else "❌ No")
            safety_item.setBackground(Qt.green if log.gluten_safety_confirmed else Qt.red)
            self.meal_table.setItem(row, 5, safety_item)
    
    def update_restaurant_display(self):
        """Update restaurant finder display"""
        restaurants = self.mobile_sync.restaurant_data
        
        # Update table
        self.restaurant_table.setRowCount(len(restaurants))
        for row, restaurant in enumerate(restaurants):
            self.restaurant_table.setItem(row, 0, QTableWidgetItem(restaurant.name))
            self.restaurant_table.setItem(row, 1, QTableWidgetItem(restaurant.cuisine_type))
            self.restaurant_table.setItem(row, 2, QTableWidgetItem("N/A"))  # Distance calculated on demand
            self.restaurant_table.setItem(row, 3, QTableWidgetItem("✅ Yes" if restaurant.gluten_free_options else "❌ No"))
            self.restaurant_table.setItem(row, 4, QTableWidgetItem("✅ Yes" if restaurant.dedicated_kitchen else "❌ No"))
            self.restaurant_table.setItem(row, 5, QTableWidgetItem(restaurant.staff_training.title()))
            self.restaurant_table.setItem(row, 6, QTableWidgetItem(f"{restaurant.user_rating:.1f}⭐"))
    
    def update_shopping_list_display(self):
        """Update shopping list display"""
        items = self.mobile_sync.get_shopping_list_items()
        
        # Update stats
        stats = self.mobile_sync.get_shopping_list_stats()
        self.total_items_label.setText(f"Total Items: {stats['total_items']}")
        self.purchased_items_label.setText(f"Purchased: {stats['purchased_items']}")
        self.pending_items_label.setText(f"Pending: {stats['pending_items']}")
        self.completion_label.setText(f"Completion: {stats['completion_percentage']:.1f}%")
        
        # Update table
        self.shopping_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.shopping_table.setItem(row, 0, QTableWidgetItem(item.item_name))
            self.shopping_table.setItem(row, 1, QTableWidgetItem(item.quantity))
            self.shopping_table.setItem(row, 2, QTableWidgetItem(item.store))
            self.shopping_table.setItem(row, 3, QTableWidgetItem(item.category))
            
            # Priority with color coding
            priority_item = QTableWidgetItem(item.priority)
            if item.priority == "High":
                priority_item.setBackground(Qt.red)
            elif item.priority == "Medium":
                priority_item.setBackground(Qt.yellow)
            else:
                priority_item.setBackground(Qt.green)
            self.shopping_table.setItem(row, 4, priority_item)
            
            # Purchased checkbox
            purchased_item = QTableWidgetItem()
            purchased_item.setCheckState(Qt.Checked if item.purchased else Qt.Unchecked)
            purchased_item.setText("Yes" if item.purchased else "No")
            if item.purchased:
                purchased_item.setBackground(Qt.green)
            self.shopping_table.setItem(row, 5, purchased_item)
            
            # Gluten-free indicator
            gf_item = QTableWidgetItem("✅ Yes" if item.gluten_free else "❌ No")
            if item.gluten_free:
                gf_item.setBackground(Qt.green)
            else:
                gf_item.setBackground(Qt.red)
            self.shopping_table.setItem(row, 6, gf_item)
            
            # Notes
            self.shopping_table.setItem(row, 7, QTableWidgetItem(item.notes or ""))
    
    def filter_shopping_by_store(self):
        """Filter shopping list by store"""
        store_filter = self.shopping_store_filter.currentText()
        self.update_shopping_list_display()
        
        if store_filter != "All Stores":
            for row in range(self.shopping_table.rowCount()):
                store_item = self.shopping_table.item(row, 2)  # Store column
                if store_item and store_item.text() != store_filter:
                    self.shopping_table.setRowHidden(row, True)
    
    def filter_shopping_by_category(self):
        """Filter shopping list by category"""
        category_filter = self.shopping_category_filter.currentText()
        self.update_shopping_list_display()
        
        if category_filter != "All Categories":
            for row in range(self.shopping_table.rowCount()):
                category_item = self.shopping_table.item(row, 3)  # Category column
                if category_item and category_item.text() != category_filter:
                    self.shopping_table.setRowHidden(row, True)
    
    def on_shopping_item_changed(self, item):
        """Handle shopping list item changes"""
        if item.column() == 5:  # Purchased column
            row = item.row()
            item_name = self.shopping_table.item(row, 0).text()
            store = self.shopping_table.item(row, 2).text()
            purchased = item.checkState() == Qt.Checked
            
            # Update in mobile sync service
            self.mobile_sync.update_shopping_list_item_purchased(item_name, store, purchased)
            
            # Update text
            item.setText("Yes" if purchased else "No")
            if purchased:
                item.setBackground(Qt.green)
            else:
                item.setBackground(Qt.transparent)
    
    def add_shopping_item(self):
        """Add new shopping list item"""
        # Simple dialog to add items
        from PySide6.QtWidgets import QInputDialog
        
        item_name, ok = QInputDialog.getText(self, "Add Shopping Item", "Enter item name:")
        if ok and item_name:
            quantity, ok = QInputDialog.getText(self, "Add Shopping Item", "Enter quantity:", text="1")
            if ok:
                # Create new shopping list item
                shopping_item = ShoppingListItemData(
                    item_name=item_name,
                    quantity=quantity or "1",
                    category="Other",
                    store="Grocery Store",
                    purchased=False,
                    timestamp=datetime.now(),
                    priority="Medium",
                    notes="",
                    gluten_free=True
                )
                
                self.mobile_sync.add_shopping_list_item(shopping_item)
                self.update_shopping_list_display()
    
    def mark_items_purchased(self):
        """Mark selected items as purchased"""
        selected_rows = set()
        for item in self.shopping_table.selectedItems():
            selected_rows.add(item.row())
        
        for row in selected_rows:
            purchased_item = self.shopping_table.item(row, 5)
            if purchased_item:
                purchased_item.setCheckState(Qt.Checked)
                self.on_shopping_item_changed(purchased_item)
    
    def clear_purchased_items(self):
        """Clear all purchased items from the list"""
        reply = QMessageBox.question(self, "Clear Purchased Items", 
                                   "Are you sure you want to remove all purchased items from the shopping list?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Remove purchased items from mobile sync service
            self.mobile_sync.shopping_list_items = [
                item for item in self.mobile_sync.shopping_list_items if not item.purchased
            ]
            self.update_shopping_list_display()
    
    def export_shopping_list_data(self):
        """Export shopping list data"""
        export_data = self.mobile_sync.export_mobile_data('shopping_list')
        QMessageBox.information(self, "Export Shopping List", f"Exported {export_data['total_records']} shopping list items!")
    
    def toggle_auto_sync(self, enabled: bool):
        """Toggle auto sync"""
        if enabled:
            self.mobile_sync.enable_auto_sync(self.sync_interval_spin.value())
        else:
            self.mobile_sync.disable_auto_sync()
    
    def manual_sync(self):
        """Trigger manual sync"""
        self.mobile_sync.sync_mobile_data()
    
    def update_sync_interval(self, interval: int):
        """Update sync interval"""
        if self.auto_sync_checkbox.isChecked():
            self.mobile_sync.enable_auto_sync(interval)
    
    def search_nearby_restaurants(self):
        """Search for nearby restaurants"""
        # In a real implementation, this would get actual GPS coordinates
        # For demo, use default coordinates
        latitude, longitude = 40.7128, -74.0060  # New York City
        
        radius = self.radius_spin.value()
        nearby_restaurants = self.mobile_sync.get_nearby_restaurants(latitude, longitude, radius)
        
        self.restaurant_table.setRowCount(len(nearby_restaurants))
        for row, restaurant in enumerate(nearby_restaurants):
            distance = self.mobile_sync._calculate_distance(
                latitude, longitude, restaurant.latitude, restaurant.longitude
            )
            
            self.restaurant_table.setItem(row, 0, QTableWidgetItem(restaurant.name))
            self.restaurant_table.setItem(row, 1, QTableWidgetItem(restaurant.cuisine_type))
            self.restaurant_table.setItem(row, 2, QTableWidgetItem(f"{distance:.1f} km"))
            self.restaurant_table.setItem(row, 3, QTableWidgetItem("✅ Yes" if restaurant.gluten_free_options else "❌ No"))
            self.restaurant_table.setItem(row, 4, QTableWidgetItem("✅ Yes" if restaurant.dedicated_kitchen else "❌ No"))
            self.restaurant_table.setItem(row, 5, QTableWidgetItem(restaurant.staff_training.title()))
            self.restaurant_table.setItem(row, 6, QTableWidgetItem(f"{restaurant.user_rating:.1f}⭐"))
    
    def show_translation_card(self):
        """Show translation card for selected language"""
        language = self.language_combo.currentText().lower()
        translation = self.mobile_sync.get_translation_card(language)
        self.translation_text.setPlainText(translation)
    
    def load_travel_kit(self):
        """Load travel kit for selected country"""
        country = self.country_combo.currentText()
        
        # In a real implementation, this would load actual travel kit data
        # For demo, create sample data
        travel_kit = TravelKitData(
            country=country,
            language="English",
            emergency_contacts=["Emergency: 911", "Celiac Support: +1-555-CELIAC"],
            safe_restaurants=[],
            translation_cards=["I have Celiac Disease..."],
            local_gluten_free_brands=["Local GF Brand 1", "Local GF Brand 2"],
            cultural_food_notes=f"Cultural notes for {country}..."
        )
        
        self.mobile_sync.add_travel_kit(country, travel_kit)
        
        # Update country restaurant table
        self.country_restaurant_table.setRowCount(len(travel_kit.safe_restaurants))
        for row, restaurant in enumerate(travel_kit.safe_restaurants):
            self.country_restaurant_table.setItem(row, 0, QTableWidgetItem(restaurant.name))
            self.country_restaurant_table.setItem(row, 1, QTableWidgetItem(restaurant.address))
            self.country_restaurant_table.setItem(row, 2, QTableWidgetItem(restaurant.cuisine_type))
            self.country_restaurant_table.setItem(row, 3, QTableWidgetItem(f"{restaurant.user_rating:.1f}⭐"))
    
    def refresh_product_database(self):
        """Refresh product database"""
        # In a real implementation, this would refresh from actual database
        QMessageBox.information(self, "Refresh Database", "Product database refreshed successfully!")
    
    def export_product_database(self):
        """Export product database"""
        safe_products = self.mobile_sync.get_safe_products()
        unsafe_products = self.mobile_sync.get_unsafe_products()
        
        export_data = {
            'safe_products': safe_products,
            'unsafe_products': unsafe_products,
            'export_timestamp': datetime.now().isoformat()
        }
        
        QMessageBox.information(self, "Export Database", f"Exported {len(safe_products)} safe and {len(unsafe_products)} unsafe products!")
    
    def search_products(self):
        """Search products in database"""
        QMessageBox.information(self, "Search Products", "Product search functionality would be implemented here!")
    
    def export_scan_data(self):
        """Export barcode scan data"""
        export_data = self.mobile_sync.export_mobile_data('barcode_scans')
        QMessageBox.information(self, "Export Scans", f"Exported {export_data['total_records']} barcode scans!")
    
    def export_symptom_data(self):
        """Export symptom data"""
        export_data = self.mobile_sync.export_mobile_data('symptom_logs')
        QMessageBox.information(self, "Export Symptoms", f"Exported {export_data['total_records']} symptom logs!")
    
    def export_meal_data(self):
        """Export meal data"""
        export_data = self.mobile_sync.export_mobile_data('meal_logs')
        QMessageBox.information(self, "Export Meals", f"Exported {export_data['total_records']} meal logs!")
    
    def export_all_data(self):
        """Export all mobile data"""
        total_records = (
            len(self.mobile_sync.barcode_scans) +
            len(self.mobile_sync.symptom_logs) +
            len(self.mobile_sync.meal_logs) +
            len(self.mobile_sync.restaurant_data) +
            len(self.mobile_sync.shopping_list_items)
        )
        
        QMessageBox.information(self, "Export All Data", f"Exported {total_records} total records from mobile companion!")
    
    def update_mobile_recipes_display(self):
        """Update mobile recipes display"""
        recipes = self.mobile_sync.get_mobile_recipes()
        
        # Update stats
        stats = self.mobile_sync.get_mobile_recipe_stats()
        self.total_recipes_label.setText(f"Total Recipes: {stats['total_recipes']}")
        self.categories_label.setText(f"Categories: {len(stats['category_counts'])}")
        
        # Update last pushed time
        if recipes:
            latest_recipe = max(recipes, key=lambda r: r.pushed_at if r.pushed_at else "")
            if latest_recipe.pushed_at:
                from datetime import datetime
                try:
                    pushed_time = datetime.fromisoformat(latest_recipe.pushed_at.replace('Z', '+00:00'))
                    self.last_pushed_label.setText(f"Last Pushed: {pushed_time.strftime('%Y-%m-%d %H:%M')}")
                except:
                    self.last_pushed_label.setText(f"Last Pushed: {latest_recipe.pushed_at}")
            else:
                self.last_pushed_label.setText("Last Pushed: Unknown")
        else:
            self.last_pushed_label.setText("Last Pushed: Never")
        
        # Update category filter
        self.recipe_category_filter.clear()
        self.recipe_category_filter.addItem("All Categories")
        categories = self.mobile_sync.get_mobile_recipe_categories()
        for category in categories:
            self.recipe_category_filter.addItem(category)
        
        # Update table
        self.recipes_table.setRowCount(len(recipes))
        for row, recipe in enumerate(recipes):
            self.recipes_table.setItem(row, 0, QTableWidgetItem(recipe.name))
            self.recipes_table.setItem(row, 1, QTableWidgetItem(recipe.category or "Unknown"))
            self.recipes_table.setItem(row, 2, QTableWidgetItem(recipe.prep_time or "N/A"))
            self.recipes_table.setItem(row, 3, QTableWidgetItem(recipe.cook_time or "N/A"))
            self.recipes_table.setItem(row, 4, QTableWidgetItem(str(recipe.servings)))
            self.recipes_table.setItem(row, 5, QTableWidgetItem(recipe.difficulty or "Unknown"))
    
    def filter_mobile_recipes(self):
        """Filter mobile recipes by category"""
        category_filter = self.recipe_category_filter.currentText()
        recipes = self.mobile_sync.get_mobile_recipes(category_filter)
        
        self.recipes_table.setRowCount(len(recipes))
        for row, recipe in enumerate(recipes):
            self.recipes_table.setItem(row, 0, QTableWidgetItem(recipe.name))
            self.recipes_table.setItem(row, 1, QTableWidgetItem(recipe.category or "Unknown"))
            self.recipes_table.setItem(row, 2, QTableWidgetItem(recipe.prep_time or "N/A"))
            self.recipes_table.setItem(row, 3, QTableWidgetItem(recipe.cook_time or "N/A"))
            self.recipes_table.setItem(row, 4, QTableWidgetItem(str(recipe.servings)))
            self.recipes_table.setItem(row, 5, QTableWidgetItem(recipe.difficulty or "Unknown"))
    
    def view_mobile_recipe(self):
        """View selected mobile recipe details"""
        current_row = self.recipes_table.currentRow()
        if current_row >= 0:
            recipe_name = self.recipes_table.item(current_row, 0).text()
            
            # Find recipe in mobile sync
            recipes = self.mobile_sync.get_mobile_recipes()
            recipe = next((r for r in recipes if r.name == recipe_name), None)
            
            if recipe:
                self.show_mobile_recipe_dialog(recipe)
    
    def show_mobile_recipe_dialog(self, recipe):
        """Show mobile recipe details dialog"""
        from PySide6.QtWidgets import QDialog, QTextEdit, QScrollArea
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Mobile Recipe: {recipe.name}")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Recipe header
        header_label = QLabel(f"🍽️ {recipe.name}")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Recipe info
        info_text = f"""
📋 Category: {recipe.category or 'Unknown'}
⏱️ Prep Time: {recipe.prep_time or 'N/A'}
🔥 Cook Time: {recipe.cook_time or 'N/A'}
👥 Servings: {recipe.servings}
⭐ Difficulty: {recipe.difficulty or 'Unknown'}
📱 Mobile Optimized: {'Yes' if recipe.mobile_optimized else 'No'}
🌾 Gluten-Free Verified: {'Yes' if recipe.gluten_free_verified else 'No'}
        """
        
        info_label = QLabel(info_text.strip())
        info_label.setStyleSheet("background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Description
        if recipe.description:
            desc_label = QLabel("📝 Description:")
            desc_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(desc_label)
            
            desc_text = QTextEdit()
            desc_text.setPlainText(recipe.description)
            desc_text.setMaximumHeight(100)
            desc_text.setReadOnly(True)
            layout.addWidget(desc_text)
        
        # Ingredients
        if recipe.ingredients:
            ing_label = QLabel("🥘 Ingredients:")
            ing_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(ing_label)
            
            ing_text = QTextEdit()
            ing_text.setPlainText(recipe.ingredients)
            ing_text.setMaximumHeight(150)
            ing_text.setReadOnly(True)
            layout.addWidget(ing_text)
        
        # Instructions
        if recipe.instructions:
            inst_label = QLabel("👨‍🍳 Instructions:")
            inst_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(inst_label)
            
            inst_text = QTextEdit()
            inst_text.setPlainText(recipe.instructions)
            inst_text.setReadOnly(True)
            layout.addWidget(inst_text)
        
        # Notes
        if recipe.notes:
            notes_label = QLabel("📝 Notes:")
            notes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(notes_label)
            
            notes_text = QTextEdit()
            notes_text.setPlainText(recipe.notes)
            notes_text.setMaximumHeight(100)
            notes_text.setReadOnly(True)
            layout.addWidget(notes_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def export_mobile_recipes(self):
        """Export mobile recipes to file"""
        recipes = self.mobile_sync.get_mobile_recipes()
        if not recipes:
            QMessageBox.information(self, "No Recipes", "No mobile recipes to export.")
            return
        
        export_data = self.mobile_sync.export_mobile_data('mobile_recipes')
        
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Mobile Recipes", 
            f"mobile_recipes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Export Complete", 
                                  f"Successfully exported {len(recipes)} recipes to {file_path}")
    
    def clear_mobile_recipes(self):
        """Clear all mobile recipes"""
        reply = QMessageBox.question(self, "Clear Mobile Recipes", 
                                   "Are you sure you want to clear all mobile recipes? This action cannot be undone.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.mobile_sync.mobile_recipes.clear()
            self.update_mobile_recipes_display()
            QMessageBox.information(self, "Recipes Cleared", "All mobile recipes have been cleared.")
    
    def refresh_mobile_recipes(self):
        """Refresh mobile recipes display"""
        self.update_mobile_recipes_display()
    
    def use_health_template(self, template_type: str):
        """Use predefined health template for quick entry"""
        template_data = self.get_health_template_data(template_type)
        if template_data:
            self.show_symptom_entry_dialog(template_data)
    
    def get_health_template_data(self, template_type: str) -> Dict[str, Any]:
        """Get predefined health template data"""
        templates = {
            "mild_symptoms": {
                "template_name": "Mild Symptoms",
                "symptoms": ["Fatigue", "Mild stomach discomfort", "Slight headache"],
                "severity_range": (1, 3),
                "emergency_level": "normal",
                "description": "Common mild symptoms that may not require immediate attention"
            },
            "moderate_symptoms": {
                "template_name": "Moderate Symptoms",
                "symptoms": ["Stomach pain", "Nausea", "Headache", "Joint pain"],
                "severity_range": (4, 6),
                "emergency_level": "concerning",
                "description": "Moderate symptoms that should be monitored closely"
            },
            "severe_symptoms": {
                "template_name": "Severe Symptoms",
                "symptoms": ["Severe stomach pain", "Vomiting", "Diarrhea", "Dizziness", "Fever"],
                "severity_range": (7, 9),
                "emergency_level": "urgent",
                "description": "Severe symptoms that may require medical attention"
            },
            "gluten_reaction": {
                "template_name": "Gluten Reaction",
                "symptoms": ["Severe stomach pain", "Nausea", "Vomiting", "Diarrhea", "Fatigue", "Brain fog"],
                "severity_range": (6, 10),
                "emergency_level": "urgent",
                "description": "Suspected gluten exposure reaction",
                "gluten_exposure_suspected": True,
                "triggers_suspected": ["Gluten exposure", "Cross-contamination"]
            }
        }
        return templates.get(template_type, {})
    
    def show_symptom_entry_dialog(self, template_data: Dict[str, Any]):
        """Show enhanced symptom entry dialog with template"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox, QCheckBox, QPushButton, QSlider
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📝 Log Symptoms - {template_data.get('template_name', 'Custom')}")
        dialog.setModal(True)
        dialog.resize(600, 700)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"📝 Log Symptoms: {template_data.get('template_name', 'Custom Entry')}")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Symptoms selection
        symptoms_layout = QVBoxLayout()
        symptoms_layout.addWidget(QLabel("🏥 Symptoms (select all that apply):"))
        
        symptoms_list = template_data.get('symptoms', [])
        symptom_checkboxes = {}
        for symptom in symptoms_list:
            checkbox = QCheckBox(symptom)
            checkbox.setChecked(True)  # Pre-select template symptoms
            symptom_checkboxes[symptom] = checkbox
            symptoms_layout.addWidget(checkbox)
        
        # Additional symptoms input
        additional_symptoms_edit = QLineEdit()
        additional_symptoms_edit.setPlaceholderText("Add additional symptoms (comma-separated)...")
        symptoms_layout.addWidget(additional_symptoms_edit)
        
        layout.addLayout(symptoms_layout)
        
        # Severity slider
        severity_layout = QHBoxLayout()
        severity_layout.addWidget(QLabel("⚠️ Severity (1-10):"))
        
        severity_slider = QSlider(Qt.Horizontal)
        severity_slider.setMinimum(1)
        severity_slider.setMaximum(10)
        severity_slider.setValue(template_data.get('severity_range', (5, 5))[0])
        
        severity_label = QLabel(str(severity_slider.value()))
        severity_slider.valueChanged.connect(lambda v: severity_label.setText(str(v)))
        
        severity_layout.addWidget(severity_slider)
        severity_layout.addWidget(severity_label)
        layout.addLayout(severity_layout)
        
        # Emergency level
        emergency_layout = QHBoxLayout()
        emergency_layout.addWidget(QLabel("🚨 Emergency Level:"))
        
        emergency_combo = QComboBox()
        emergency_combo.addItems(["normal", "concerning", "urgent", "emergency"])
        emergency_combo.setCurrentText(template_data.get('emergency_level', 'normal'))
        emergency_layout.addWidget(emergency_combo)
        emergency_layout.addStretch()
        
        layout.addLayout(emergency_layout)
        
        # Mood and energy
        mood_energy_layout = QHBoxLayout()
        mood_energy_layout.addWidget(QLabel("😊 Mood:"))
        
        mood_combo = QComboBox()
        mood_combo.addItems(["good", "fair", "poor", "terrible"])
        mood_energy_layout.addWidget(mood_combo)
        
        mood_energy_layout.addWidget(QLabel("⚡ Energy Level (1-10):"))
        energy_spin = QSpinBox()
        energy_spin.setMinimum(1)
        energy_spin.setMaximum(10)
        energy_spin.setValue(5)
        mood_energy_layout.addWidget(energy_spin)
        
        layout.addLayout(mood_energy_layout)
        
        # Meal context
        meal_layout = QHBoxLayout()
        meal_layout.addWidget(QLabel("🍽️ Recent Meal Context:"))
        meal_context_edit = QLineEdit()
        meal_context_edit.setPlaceholderText("Describe recent meals or food consumed...")
        meal_layout.addWidget(meal_context_edit)
        
        layout.addLayout(meal_layout)
        
        # Suspected triggers
        triggers_layout = QVBoxLayout()
        triggers_layout.addWidget(QLabel("🔍 Suspected Triggers:"))
        
        gluten_exposure_check = QCheckBox("Gluten exposure suspected")
        gluten_exposure_check.setChecked(template_data.get('gluten_exposure_suspected', False))
        triggers_layout.addWidget(gluten_exposure_check)
        
        triggers_edit = QLineEdit()
        triggers_edit.setPlaceholderText("Other suspected triggers (comma-separated)...")
        triggers_layout.addWidget(triggers_edit)
        
        layout.addLayout(triggers_layout)
        
        # Notes
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("📝 Additional Notes:"))
        notes_edit = QTextEdit()
        notes_edit.setMaximumHeight(100)
        notes_edit.setPlaceholderText("Add any additional notes about symptoms, duration, etc...")
        notes_layout.addWidget(notes_edit)
        
        layout.addLayout(notes_layout)
        
        # Media options (simulated)
        media_layout = QVBoxLayout()
        media_layout.addWidget(QLabel("📸 Media Attachments (Mobile Feature):"))
        
        voice_note_check = QCheckBox("🎤 Voice Note")
        photo_check = QCheckBox("📷 Photo")
        voice_note_check.setEnabled(False)  # Desktop simulation
        photo_check.setEnabled(False)  # Desktop simulation
        
        media_layout.addWidget(voice_note_check)
        media_layout.addWidget(photo_check)
        
        layout.addLayout(media_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Symptom Log")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 5px;")
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px;")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.Accepted:
            # Collect data
            selected_symptoms = [text for text, checkbox in symptom_checkboxes.items() if checkbox.isChecked()]
            
            additional_symptoms = additional_symptoms_edit.text().strip()
            if additional_symptoms:
                selected_symptoms.extend([s.strip() for s in additional_symptoms.split(',') if s.strip()])
            
            triggers = []
            if gluten_exposure_check.isChecked():
                triggers.append("Gluten exposure")
            
            additional_triggers = triggers_edit.text().strip()
            if additional_triggers:
                triggers.extend([t.strip() for t in additional_triggers.split(',') if t.strip()])
            
            symptom_data = {
                'timestamp': datetime.now().isoformat(),
                'symptoms': selected_symptoms,
                'severity': severity_slider.value(),
                'emergency_level': emergency_combo.currentText(),
                'mood': mood_combo.currentText(),
                'energy_level': energy_spin.value(),
                'meal_context': meal_context_edit.text().strip() or None,
                'triggers_suspected': triggers,
                'gluten_exposure_suspected': gluten_exposure_check.isChecked(),
                'notes': notes_edit.toPlainText().strip() or None,
                'voice_note_path': None,  # Would be set by mobile app
                'photo_paths': []  # Would be set by mobile app
            }
            
            # Add to mobile sync
            success = self.mobile_sync.add_symptom_log_with_media(symptom_data)
            
            if success:
                QMessageBox.information(self, "Success", "Symptom log saved successfully!")
                self.update_symptom_display()
            else:
                QMessageBox.warning(self, "Error", "Failed to save symptom log.")
    
    def add_symptom_log(self):
        """Add custom symptom log"""
        self.show_symptom_entry_dialog({})
    
    def view_symptom_details(self):
        """View detailed symptom information"""
        current_row = self.symptom_table.currentRow()
        if current_row >= 0:
            # Get symptom data from table
            timestamp_item = self.symptom_table.item(current_row, 0)
            if timestamp_item:
                timestamp_str = timestamp_item.text()
                
                # Find matching symptom in mobile sync
                symptoms = self.mobile_sync.symptom_logs
                matching_symptom = None
                
                for symptom in symptoms:
                    if symptom.timestamp.strftime('%Y-%m-%d %H:%M') == timestamp_str:
                        matching_symptom = symptom
                        break
                
                if matching_symptom:
                    self.show_symptom_details_dialog(matching_symptom)
    
    def show_symptom_details_dialog(self, symptom_data):
        """Show detailed symptom information dialog"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Symptom Details - {symptom_data.timestamp.strftime('%Y-%m-%d %H:%M')}")
        dialog.setModal(True)
        dialog.resize(500, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"🏥 Symptom Log Details")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Basic info
        info_text = f"""
📅 Timestamp: {symptom_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
🏥 Symptoms: {', '.join(symptom_data.symptoms)}
⚠️ Severity: {symptom_data.severity}/10
🚨 Emergency Level: {getattr(symptom_data, 'emergency_level', 'normal')}
📍 Location: {symptom_data.location or 'Not specified'}
        """
        
        info_label = QLabel(info_text.strip())
        info_label.setStyleSheet("background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Enhanced details if available
        if hasattr(symptom_data, 'mood') and symptom_data.mood:
            mood_text = QLabel(f"😊 Mood: {symptom_data.mood}")
            layout.addWidget(mood_text)
        
        if hasattr(symptom_data, 'energy_level') and symptom_data.energy_level:
            energy_text = QLabel(f"⚡ Energy Level: {symptom_data.energy_level}/10")
            layout.addWidget(energy_text)
        
        if hasattr(symptom_data, 'triggers_suspected') and symptom_data.triggers_suspected:
            triggers_text = QLabel(f"🔍 Suspected Triggers: {', '.join(symptom_data.triggers_suspected)}")
            layout.addWidget(triggers_text)
        
        if hasattr(symptom_data, 'gluten_exposure_suspected') and symptom_data.gluten_exposure_suspected:
            gluten_text = QLabel("🌾 Gluten Exposure Suspected: Yes")
            gluten_text.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(gluten_text)
        
        # Notes
        if symptom_data.notes:
            notes_label = QLabel("📝 Notes:")
            notes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(notes_label)
            
            notes_text = QTextEdit()
            notes_text.setPlainText(symptom_data.notes)
            notes_text.setReadOnly(True)
            notes_text.setMaximumHeight(100)
            layout.addWidget(notes_text)
        
        # Media attachments
        if hasattr(symptom_data, 'voice_note_path') and symptom_data.voice_note_path:
            voice_label = QLabel(f"🎤 Voice Note: {symptom_data.voice_note_path}")
            layout.addWidget(voice_label)
        
        if hasattr(symptom_data, 'photo_paths') and symptom_data.photo_paths:
            photos_label = QLabel(f"📷 Photos: {len(symptom_data.photo_paths)} attached")
            layout.addWidget(photos_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def clear_symptom_logs(self):
        """Clear all symptom logs"""
        reply = QMessageBox.question(self, "Clear Symptom Logs", 
                                   "Are you sure you want to clear all symptom logs? This action cannot be undone.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.mobile_sync.symptom_logs.clear()
            self.update_symptom_display()
            QMessageBox.information(self, "Logs Cleared", "All symptom logs have been cleared.")
    
    def add_smart_meal_reminder(self):
        """Add smart meal reminder"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🍽️ Add Smart Meal Reminder")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel("🍽️ Smart Meal Reminder")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Delay input
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("⏰ Delay after meal (minutes):"))
        
        delay_spin = QSpinBox()
        delay_spin.setMinimum(5)
        delay_spin.setMaximum(180)
        delay_spin.setValue(30)
        delay_spin.setSuffix(" min")
        delay_layout.addWidget(delay_spin)
        delay_layout.addStretch()
        
        layout.addLayout(delay_layout)
        
        # Message input
        message_layout = QVBoxLayout()
        message_layout.addWidget(QLabel("💬 Reminder Message:"))
        
        message_edit = QLineEdit()
        message_edit.setPlaceholderText("How are you feeling after your meal? Log any symptoms or reactions.")
        message_edit.setText("How are you feeling after your meal? Log any symptoms or reactions.")
        message_layout.addWidget(message_edit)
        
        layout.addLayout(message_layout)
        
        # Trigger context
        context_layout = QHBoxLayout()
        context_layout.addWidget(QLabel("🎯 Trigger Context:"))
        
        context_combo = QComboBox()
        context_combo.addItems(["meal_completed", "time_based", "location_based"])
        context_layout.addWidget(context_combo)
        context_layout.addStretch()
        
        layout.addLayout(context_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Add Reminder")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 5px;")
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px;")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.Accepted:
            from services.mobile_sync import HealthReminderData
            
            reminder = HealthReminderData(
                reminder_id=f"meal_reminder_{datetime.now().timestamp()}",
                reminder_type="meal_log",
                trigger_event=context_combo.currentText(),
                delay_minutes=delay_spin.value(),
                message=message_edit.text().strip(),
                enabled=True
            )
            
            self.mobile_sync.add_health_reminder(reminder)
            QMessageBox.information(self, "Reminder Added", "Smart meal reminder added successfully!")
            self.update_active_reminders_display()
    
    def add_smart_symptom_reminder(self):
        """Add smart symptom reminder"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QComboBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🏥 Add Smart Symptom Reminder")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel("🏥 Smart Symptom Reminder")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Reminder type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("🏥 Reminder Type:"))
        
        type_combo = QComboBox()
        type_combo.addItems(["symptom_check", "medication", "appointment", "pattern_analysis"])
        type_layout.addWidget(type_combo)
        type_layout.addStretch()
        
        layout.addLayout(type_layout)
        
        # Delay input
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("⏰ Delay (minutes):"))
        
        delay_spin = QSpinBox()
        delay_spin.setMinimum(5)
        delay_spin.setMaximum(1440)
        delay_spin.setValue(120)
        delay_spin.setSuffix(" min")
        delay_layout.addWidget(delay_spin)
        delay_layout.addStretch()
        
        layout.addLayout(delay_layout)
        
        # Message input
        message_layout = QVBoxLayout()
        message_layout.addWidget(QLabel("💬 Reminder Message:"))
        
        message_edit = QLineEdit()
        message_edit.setPlaceholderText("Time for your symptom check-in. How are you feeling?")
        message_edit.setText("Time for your symptom check-in. How are you feeling?")
        message_layout.addWidget(message_edit)
        
        layout.addLayout(message_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Add Reminder")
        save_btn.setStyleSheet("background-color: #e67e22; color: white; padding: 10px; border-radius: 5px;")
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px;")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.Accepted:
            from services.mobile_sync import HealthReminderData
            
            reminder = HealthReminderData(
                reminder_id=f"symptom_reminder_{datetime.now().timestamp()}",
                reminder_type=type_combo.currentText(),
                trigger_event="time_based",
                delay_minutes=delay_spin.value(),
                message=message_edit.text().strip(),
                enabled=True
            )
            
            self.mobile_sync.add_health_reminder(reminder)
            QMessageBox.information(self, "Reminder Added", "Smart symptom reminder added successfully!")
            self.update_active_reminders_display()
    
    def view_smart_notifications(self):
        """View smart reminder notifications"""
        notifications = self.mobile_sync.get_reminder_notifications()
        
        if not notifications:
            QMessageBox.information(self, "No Notifications", "No active reminder notifications at this time.")
            return
        
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"🔔 Smart Notifications ({len(notifications)} active)")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel(f"🔔 Active Smart Notifications ({len(notifications)})")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Notifications display
        notifications_text = QTextEdit()
        notifications_text.setReadOnly(True)
        
        display_text = ""
        for i, notification in enumerate(notifications, 1):
            priority_icon = "🚨" if notification['priority'] == 'high' else "🔔"
            display_text += f"{priority_icon} {i}. [{notification['type'].title()}] {notification['message']}\n"
            display_text += f"   Priority: {notification['priority'].title()} | Time: {notification['timestamp']}\n\n"
        
        notifications_text.setPlainText(display_text.strip())
        layout.addWidget(notifications_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        dismiss_btn = QPushButton("✅ Dismiss All")
        dismiss_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 5px;")
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("background-color: #95a5a6; color: white; padding: 10px; border-radius: 5px;")
        
        button_layout.addWidget(dismiss_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        dismiss_btn.clicked.connect(lambda: self.dismiss_notifications(notifications))
        close_btn.clicked.connect(dialog.accept)
        
        dialog.exec()
    
    def dismiss_notifications(self, notifications):
        """Dismiss reminder notifications"""
        # In a real implementation, this would mark notifications as dismissed
        # For demo purposes, we'll just show a confirmation
        QMessageBox.information(self, "Notifications Dismissed", 
                              f"Dismissed {len(notifications)} reminder notifications.")
    
    def update_active_reminders_display(self):
        """Update active reminders display"""
        reminders = self.mobile_sync.health_reminders
        
        if not reminders:
            self.active_reminders_text.setPlainText("No active health reminders.")
            return
        
        display_text = "🔔 Active Health Reminders:\n\n"
        
        for reminder in reminders:
            status = "✅ Enabled" if reminder.enabled else "❌ Disabled"
            display_text += f"• {reminder.reminder_type.title()} - {reminder.message[:40]}...\n"
            display_text += f"  Trigger: {reminder.trigger_event} ({reminder.delay_minutes} min) - {status}\n\n"
        
        self.active_reminders_text.setPlainText(display_text.strip())

    def refresh(self):
        """Refresh panel data"""
        self.update_barcode_scan_display()
        self.update_symptom_display()
        self.update_meal_display()
        self.update_restaurant_display()
        self.update_shopping_list_display()
        self.update_mobile_recipes_display()
        self.update_active_reminders_display()
    
    def closeEvent(self, event):
        """Handle panel close"""
        self.mobile_sync.disable_auto_sync()
        super().closeEvent(event)
