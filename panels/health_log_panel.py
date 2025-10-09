# path: panels/health_log_panel_pyside6.py
"""
Health Log Panel for PySide6 Application

Manages health tracking with Gluten Guardian enhancements and Care Provider management.
"""

from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QDateEdit,
    QMessageBox, QRadioButton, QSlider, QScrollArea, QDialog,
    QTabWidget, QSplitter, QDialogButtonBox, QFormLayout,
    QCheckBox, QFrame
)
from utils.custom_widgets import NoSelectionTableWidget
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont

from panels.base_panel import BasePanel
from panels.context_menu_mixin import HealthLogContextMenuMixin
from services.care_provider_service import get_care_provider_service, CareProviderData


class CareProviderDialog(QDialog):
    """Dialog for adding/editing care providers"""
    
    def __init__(self, parent=None, provider_data: CareProviderData = None):
        super().__init__(parent)
        self.provider_data = provider_data
        self.setWindowTitle("Add Care Provider" if provider_data is None else "Edit Care Provider")
        self.setModal(True)
        self.setMinimumSize(500, 600)
        self.setup_ui()
        
        if provider_data:
            self.load_provider_data()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Scroll area for form
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)
        
        # Basic Information
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.title_edit = QLineEdit()
        self.specialty_combo = QComboBox()
        self.specialty_combo.setEditable(True)
        self.specialty_combo.addItems([
            "Primary Care", "Gastroenterologist", "Nutritionist/Dietitian", 
            "Endocrinologist", "Dermatologist", "Emergency Medicine",
            "Internal Medicine", "Family Medicine", "Other"
        ])
        self.organization_edit = QLineEdit()
        
        basic_layout.addRow("Name:", self.name_edit)
        basic_layout.addRow("Title:", self.title_edit)
        basic_layout.addRow("Specialty:", self.specialty_combo)
        basic_layout.addRow("Organization:", self.organization_edit)
        
        # Contact Information
        contact_group = QGroupBox("Contact Information")
        contact_layout = QFormLayout(contact_group)
        
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.website_edit = QLineEdit()
        self.preferred_contact_combo = QComboBox()
        self.preferred_contact_combo.addItems(["phone", "email", "both"])
        
        contact_layout.addRow("Phone:", self.phone_edit)
        contact_layout.addRow("Email:", self.email_edit)
        contact_layout.addRow("Website:", self.website_edit)
        contact_layout.addRow("Preferred Contact:", self.preferred_contact_combo)
        
        # Address Information
        address_group = QGroupBox("Address Information")
        address_layout = QFormLayout(address_group)
        
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(60)
        self.city_edit = QLineEdit()
        self.state_edit = QLineEdit()
        self.zip_edit = QLineEdit()
        
        address_layout.addRow("Address:", self.address_edit)
        address_layout.addRow("City:", self.city_edit)
        address_layout.addRow("State:", self.state_edit)
        address_layout.addRow("ZIP Code:", self.zip_edit)
        
        # Additional Information
        additional_group = QGroupBox("Additional Information")
        additional_layout = QFormLayout(additional_group)
        
        self.emergency_checkbox = QCheckBox("Emergency Contact")
        self.last_appointment_edit = QLineEdit()
        self.next_appointment_edit = QLineEdit()
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        
        additional_layout.addRow("Emergency Contact:", self.emergency_checkbox)
        additional_layout.addRow("Last Appointment:", self.last_appointment_edit)
        additional_layout.addRow("Next Appointment:", self.next_appointment_edit)
        additional_layout.addRow("Notes:", self.notes_edit)
        
        # Add groups to form
        form_layout.addWidget(basic_group)
        form_layout.addWidget(contact_group)
        form_layout.addWidget(address_group)
        form_layout.addWidget(additional_group)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_provider_data(self):
        """Load provider data into form"""
        if not self.provider_data:
            return
            
        self.name_edit.setText(self.provider_data.name)
        self.title_edit.setText(self.provider_data.title)
        
        # Set specialty
        specialty_index = self.specialty_combo.findText(self.provider_data.specialty)
        if specialty_index >= 0:
            self.specialty_combo.setCurrentIndex(specialty_index)
        else:
            self.specialty_combo.setCurrentText(self.provider_data.specialty)
        
        self.organization_edit.setText(self.provider_data.organization)
        self.phone_edit.setText(self.provider_data.phone or "")
        self.email_edit.setText(self.provider_data.email or "")
        self.website_edit.setText(self.provider_data.website or "")
        self.preferred_contact_combo.setCurrentText(self.provider_data.preferred_contact_method)
        
        self.address_edit.setPlainText(self.provider_data.address or "")
        self.city_edit.setText(self.provider_data.city or "")
        self.state_edit.setText(self.provider_data.state or "")
        self.zip_edit.setText(self.provider_data.zip_code or "")
        
        self.emergency_checkbox.setChecked(self.provider_data.emergency_contact)
        self.last_appointment_edit.setText(self.provider_data.last_appointment or "")
        self.next_appointment_edit.setText(self.provider_data.next_appointment or "")
        self.notes_edit.setPlainText(self.provider_data.notes or "")
    
    def get_provider_data(self) -> Dict[str, Any]:
        """Get provider data from form"""
        return {
            'name': self.name_edit.text().strip(),
            'title': self.title_edit.text().strip(),
            'specialty': self.specialty_combo.currentText().strip(),
            'organization': self.organization_edit.text().strip(),
            'phone': self.phone_edit.text().strip() or None,
            'email': self.email_edit.text().strip() or None,
            'website': self.website_edit.text().strip() or None,
            'preferred_contact_method': self.preferred_contact_combo.currentText(),
            'address': self.address_edit.toPlainText().strip() or None,
            'city': self.city_edit.text().strip() or None,
            'state': self.state_edit.text().strip() or None,
            'zip_code': self.zip_edit.text().strip() or None,
            'emergency_contact': self.emergency_checkbox.isChecked(),
            'last_appointment': self.last_appointment_edit.text().strip() or None,
            'next_appointment': self.next_appointment_edit.text().strip() or None,
            'notes': self.notes_edit.toPlainText().strip() or None,
            'provider_id': self.provider_data.provider_id if self.provider_data else None
        }


class HealthLogPanel(HealthLogContextMenuMixin, BasePanel):
    """Health log panel for PySide6 with Gluten Guardian features and Care Provider management"""
    
    def __init__(self, master=None, app=None):
        # Initialize care provider service before calling super().__init__()
        # because setup_ui() will be called during super().__init__()
        try:
            self.care_provider_service = get_care_provider_service()
        except Exception as e:
            print(f"Error initializing care provider service: {e}")
            # Create a dummy service to prevent attribute errors
            self.care_provider_service = None
        
        # Now call super().__init__() which will call setup_ui()
        super().__init__(master, app)
        
        # Connect signals after the UI is set up
        if self.care_provider_service:
            try:
                self.care_provider_service.provider_added.connect(self.on_provider_added)
                self.care_provider_service.provider_updated.connect(self.on_provider_updated)
                self.care_provider_service.provider_deleted.connect(self.on_provider_deleted)
                self.care_provider_service.appointment_created.connect(self.on_appointment_created)
            except Exception as e:
                print(f"Error connecting care provider service signals: {e}")
    
    def setup_ui(self):
        """Set up the health log panel UI with tabs"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self.setup_health_logging_tab()
        self.setup_care_providers_tab()
    
    def setup_health_logging_tab(self):
        """Set up the health logging tab"""
        health_widget = QWidget()
        layout = QVBoxLayout(health_widget)
        
        # Quick actions toolbar
        actions_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export Data")
        self.export_btn.clicked.connect(self.export_health_data)
        actions_layout.addWidget(self.export_btn)
        
        self.import_btn = QPushButton("Import Data")
        self.import_btn.clicked.connect(self.import_health_data)
        actions_layout.addWidget(self.import_btn)
        
        self.bulk_add_btn = QPushButton("Bulk Add")
        self.bulk_add_btn.clicked.connect(self.bulk_add_entries)
        actions_layout.addWidget(self.bulk_add_btn)
        
        self.analyze_btn = QPushButton("Analyze Patterns")
        self.analyze_btn.clicked.connect(self.analyze_patterns)
        actions_layout.addWidget(self.analyze_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Scroll area for the form
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Basic Information Group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QVBoxLayout(basic_group)
        
        # Date and Time
        datetime_layout = QHBoxLayout()
        datetime_layout.addWidget(QLabel("Date:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        datetime_layout.addWidget(self.date_edit)
        
        datetime_layout.addWidget(QLabel("Time:"))
        self.time_combo = QComboBox()
        self.time_combo.addItems([f"{h:02d}:{m:02d}" for h in range(24) for m in range(0, 60, 15)])
        datetime_layout.addWidget(self.time_combo)
        basic_layout.addLayout(datetime_layout)
        
        # Meal Type
        meal_layout = QHBoxLayout()
        meal_layout.addWidget(QLabel("Meal Type:"))
        self.meal_combo = QComboBox()
        self.meal_combo.addItems(["Breakfast", "Lunch", "Dinner", "Snack", "Other"])
        meal_layout.addWidget(self.meal_combo)
        basic_layout.addLayout(meal_layout)
        
        # Items Consumed
        items_layout = QVBoxLayout()
        items_layout.addWidget(QLabel("Items Consumed:"))
        self.items_edit = QTextEdit()
        self.items_edit.setMaximumHeight(60)
        self.items_edit.setPlaceholderText("Enter items consumed...")
        items_layout.addWidget(self.items_edit)
        basic_layout.addLayout(items_layout)
        
        scroll_layout.addWidget(basic_group)
        
        # Symptoms Group
        symptoms_group = QGroupBox("Symptoms & Assessment")
        symptoms_layout = QVBoxLayout(symptoms_group)
        
        # Risk Level
        risk_layout = QHBoxLayout()
        risk_layout.addWidget(QLabel("Risk Level:"))
        self.risk_combo = QComboBox()
        self.risk_combo.addItems(["none", "low", "med", "high"])
        risk_layout.addWidget(self.risk_combo)
        symptoms_layout.addLayout(risk_layout)
        
        # Onset and Severity
        onset_layout = QHBoxLayout()
        onset_layout.addWidget(QLabel("Onset (minutes):"))
        self.onset_spin = QSpinBox()
        self.onset_spin.setRange(0, 1440)  # Up to 24 hours
        onset_layout.addWidget(self.onset_spin)
        
        onset_layout.addWidget(QLabel("Severity (0-10):"))
        self.severity_spin = QSpinBox()
        self.severity_spin.setRange(0, 10)
        onset_layout.addWidget(self.severity_spin)
        symptoms_layout.addLayout(onset_layout)
        
        # Symptoms
        symptoms_text_layout = QVBoxLayout()
        symptoms_text_layout.addWidget(QLabel("Symptoms:"))
        self.symptoms_edit = QTextEdit()
        self.symptoms_edit.setMaximumHeight(60)
        self.symptoms_edit.setPlaceholderText("Describe symptoms...")
        symptoms_text_layout.addWidget(self.symptoms_edit)
        symptoms_layout.addLayout(symptoms_text_layout)
        
        scroll_layout.addWidget(symptoms_group)
        
        # Bristol Stool Scale Group
        bristol_group = QGroupBox("Bristol Stool Scale")
        bristol_layout = QVBoxLayout(bristol_group)
        
        self.bristol_buttons = []
        bristol_types = [
            "1 - Separate hard lumps (constipation)",
            "2 - Lumpy sausage",
            "3 - Cracked sausage",
            "4 - Smooth sausage (normal)",
            "5 - Soft blobs",
            "6 - Fluffy pieces",
            "7 - Watery (diarrhea)"
        ]
        
        for i, bristol_type in enumerate(bristol_types):
            radio = QRadioButton(bristol_type)
            self.bristol_buttons.append(radio)
            bristol_layout.addWidget(radio)
        
        # Set default to type 4 (normal)
        self.bristol_buttons[3].setChecked(True)
        scroll_layout.addWidget(bristol_group)
        
        # Gluten Guardian Tracking Group
        gg_group = QGroupBox("Gluten Guardian Tracking")
        gg_layout = QVBoxLayout(gg_group)
        
        # Hydration and Fiber
        hydration_layout = QHBoxLayout()
        hydration_layout.addWidget(QLabel("Hydration (L):"))
        self.hydration_spin = QSpinBox()
        self.hydration_spin.setRange(0, 10)
        self.hydration_spin.setSuffix(" L")
        hydration_layout.addWidget(self.hydration_spin)
        
        hydration_layout.addWidget(QLabel("Fiber (g):"))
        self.fiber_spin = QSpinBox()
        self.fiber_spin.setRange(0, 100)
        self.fiber_spin.setSuffix(" g")
        hydration_layout.addWidget(self.fiber_spin)
        gg_layout.addLayout(hydration_layout)
        
        # Mood
        mood_layout = QHBoxLayout()
        mood_layout.addWidget(QLabel("Mood:"))
        self.mood_combo = QComboBox()
        self.mood_combo.addItems(["😊", "😐", "😣", "😢", "😡"])
        mood_layout.addWidget(self.mood_combo)
        gg_layout.addLayout(mood_layout)
        
        # Energy Level
        energy_layout = QVBoxLayout()
        energy_layout.addWidget(QLabel("Energy Level (1-10):"))
        self.energy_slider = QSlider(Qt.Horizontal)
        self.energy_slider.setRange(1, 10)
        self.energy_slider.setValue(5)
        self.energy_label = QLabel("5")
        self.energy_slider.valueChanged.connect(lambda v: self.energy_label.setText(str(v)))
        energy_layout.addWidget(self.energy_slider)
        energy_layout.addWidget(self.energy_label)
        gg_layout.addLayout(energy_layout)
        
        scroll_layout.addWidget(gg_group)
        
        # Notes Group
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Additional notes...")
        notes_layout.addWidget(self.notes_edit)
        
        scroll_layout.addWidget(notes_group)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Entry")
        save_button.clicked.connect(self.save_entry)
        button_layout.addWidget(save_button)
        
        clear_button = QPushButton("Clear Form")
        clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(clear_button)
        
        analyze_button = QPushButton("Analyze Patterns")
        analyze_button.clicked.connect(self.analyze_patterns)
        button_layout.addWidget(analyze_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Health Log Entries Table
        entries_group = QGroupBox("Health Log Entries")
        entries_layout = QVBoxLayout(entries_group)
        
        self.entries_table = NoSelectionTableWidget()
        self.entries_table.setColumnCount(7)
        self.entries_table.setHorizontalHeaderLabels(["Date", "Time", "Meal", "Items", "Risk", "Severity", "Symptoms"])
        self.entries_table.setMaximumHeight(200)
        entries_layout.addWidget(self.entries_table)
        
        layout.addWidget(entries_group)
        
        self.tab_widget.addTab(health_widget, "🏥 Health Logging")
    
    def setup_care_providers_tab(self):
        """Set up the care providers tab"""
        providers_widget = QWidget()
        layout = QVBoxLayout(providers_widget)
        
        # Summary section
        summary_group = QGroupBox("📊 Care Provider Summary")
        summary_layout = QHBoxLayout(summary_group)
        
        self.total_providers_label = QLabel("Total Providers: 0")
        self.emergency_providers_label = QLabel("Emergency Contacts: 0")
        self.specialties_count_label = QLabel("Specialties: 0")
        
        summary_layout.addWidget(self.total_providers_label)
        summary_layout.addWidget(self.emergency_providers_label)
        summary_layout.addWidget(self.specialties_count_label)
        summary_layout.addStretch()
        
        layout.addWidget(summary_group)
        
        # Search and filter section
        search_group = QGroupBox("🔍 Search & Filter")
        search_layout = QVBoxLayout(search_group)
        
        # Search bar
        search_bar_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search providers by name, specialty, or organization...")
        self.search_edit.textChanged.connect(self.filter_providers)
        search_bar_layout.addWidget(self.search_edit)
        
        # Specialty filter
        self.specialty_filter_combo = QComboBox()
        self.specialty_filter_combo.addItem("All Specialties")
        self.specialty_filter_combo.currentTextChanged.connect(self.filter_providers)
        search_bar_layout.addWidget(self.specialty_filter_combo)
        
        # Emergency filter
        self.emergency_filter_checkbox = QCheckBox("Emergency Contacts Only")
        self.emergency_filter_checkbox.stateChanged.connect(self.filter_providers)
        search_bar_layout.addWidget(self.emergency_filter_checkbox)
        
        search_layout.addLayout(search_bar_layout)
        layout.addWidget(search_group)
        
        # Providers table
        table_group = QGroupBox("👩‍⚕️ Care Providers")
        table_layout = QVBoxLayout(table_group)
        
        self.providers_table = QTableWidget()
        self.providers_table.setColumnCount(8)
        self.providers_table.setHorizontalHeaderLabels([
            "Name", "Title", "Specialty", "Organization", "Phone", "Email", "Emergency", "Actions"
        ])
        self.providers_table.horizontalHeader().setStretchLastSection(True)
        self.providers_table.setAlternatingRowColors(True)
        self.providers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.providers_table.itemDoubleClicked.connect(self.edit_provider)
        
        # Apply custom delegate to suppress selection borders
        from utils.custom_delegates import CleanSelectionDelegate
        self.providers_table.setItemDelegate(CleanSelectionDelegate())
        
        table_layout.addWidget(self.providers_table)
        layout.addWidget(table_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        add_provider_btn = QPushButton("➕ Add Provider")
        add_provider_btn.clicked.connect(self.add_provider)
        add_provider_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; border-radius: 3px;")
        
        edit_provider_btn = QPushButton("✏️ Edit Provider")
        edit_provider_btn.clicked.connect(self.edit_provider)
        edit_provider_btn.setEnabled(False)
        
        delete_provider_btn = QPushButton("🗑️ Delete Provider")
        delete_provider_btn.clicked.connect(self.delete_provider)
        delete_provider_btn.setEnabled(False)
        delete_provider_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px; border-radius: 3px;")
        
        call_provider_btn = QPushButton("📞 Call")
        call_provider_btn.clicked.connect(self.call_provider)
        call_provider_btn.setEnabled(False)
        
        email_provider_btn = QPushButton("📧 Email")
        email_provider_btn.clicked.connect(self.email_provider)
        email_provider_btn.setEnabled(False)
        
        create_appointment_btn = QPushButton("📅 Create Appointment")
        create_appointment_btn.clicked.connect(self.create_appointment_from_provider)
        create_appointment_btn.setEnabled(False)
        
        refresh_providers_btn = QPushButton("🔄 Refresh")
        refresh_providers_btn.clicked.connect(self.refresh_providers)
        
        action_layout.addWidget(add_provider_btn)
        action_layout.addWidget(edit_provider_btn)
        action_layout.addWidget(delete_provider_btn)
        action_layout.addStretch()
        action_layout.addWidget(call_provider_btn)
        action_layout.addWidget(email_provider_btn)
        action_layout.addWidget(create_appointment_btn)
        action_layout.addStretch()
        action_layout.addWidget(refresh_providers_btn)
        
        layout.addLayout(action_layout)
        
        # Connect selection changes
        self.providers_table.selectionModel().selectionChanged.connect(
            lambda: self.update_provider_buttons(edit_provider_btn, delete_provider_btn, 
                                               call_provider_btn, email_provider_btn, create_appointment_btn)
        )
        
        self.tab_widget.addTab(providers_widget, "👩‍⚕️ Care Providers")
        
        # Load initial data
        self.refresh_providers()
    
    def update_provider_buttons(self, edit_btn, delete_btn, call_btn, email_btn, appointment_btn):
        """Update provider action buttons based on selection"""
        has_selection = len(self.providers_table.selectedItems()) > 0
        edit_btn.setEnabled(has_selection)
        delete_btn.setEnabled(has_selection)
        call_btn.setEnabled(has_selection)
        email_btn.setEnabled(has_selection)
        appointment_btn.setEnabled(has_selection)
    
    def add_provider(self):
        """Add new care provider"""
        if not self.care_provider_service:
            QMessageBox.warning(self, "Error", "Care provider service is not available.")
            return
            
        dialog = CareProviderDialog(self)
        if dialog.exec() == QDialog.Accepted:
            provider_data = dialog.get_provider_data()
            if provider_data['name']:  # Basic validation
                success = self.care_provider_service.add_provider(provider_data)
                if success:
                    QMessageBox.information(self, "Success", "Care provider added successfully!")
                    self.refresh_providers()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add care provider.")
            else:
                QMessageBox.warning(self, "Validation Error", "Provider name is required.")
    
    def edit_provider(self):
        """Edit selected care provider"""
        if not self.care_provider_service:
            QMessageBox.warning(self, "Error", "Care provider service is not available.")
            return
            
        selected_row = self.providers_table.currentRow()
        if selected_row < 0:
            return
        
        provider_id = self.providers_table.item(selected_row, 0).data(Qt.UserRole)
        provider = self.care_provider_service.get_provider(provider_id)
        
        if provider:
            dialog = CareProviderDialog(self, provider)
            if dialog.exec() == QDialog.Accepted:
                provider_data = dialog.get_provider_data()
                success = self.care_provider_service.update_provider(provider_id, provider_data)
                if success:
                    QMessageBox.information(self, "Success", "Care provider updated successfully!")
                    self.refresh_providers()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update care provider.")
    
    def delete_provider(self):
        """Delete selected care provider"""
        selected_row = self.providers_table.currentRow()
        if selected_row < 0:
            return
        
        provider_id = self.providers_table.item(selected_row, 0).data(Qt.UserRole)
        provider_name = self.providers_table.item(selected_row, 0).text()
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete {provider_name}?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = self.care_provider_service.delete_provider(provider_id)
            if success:
                QMessageBox.information(self, "Success", "Care provider deleted successfully!")
                self.refresh_providers()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete care provider.")
    
    def call_provider(self):
        """Call selected care provider"""
        selected_row = self.providers_table.currentRow()
        if selected_row < 0:
            return
        
        provider_id = self.providers_table.item(selected_row, 0).data(Qt.UserRole)
        provider = self.care_provider_service.get_provider(provider_id)
        
        if provider and provider.phone:
            success = self.care_provider_service.contact_provider(provider, "phone")
            if not success:
                QMessageBox.warning(self, "Error", "Failed to initiate phone call.")
        else:
            QMessageBox.information(self, "No Phone", "No phone number available for this provider.")
    
    def email_provider(self):
        """Email selected care provider"""
        selected_row = self.providers_table.currentRow()
        if selected_row < 0:
            return
        
        provider_id = self.providers_table.item(selected_row, 0).data(Qt.UserRole)
        provider = self.care_provider_service.get_provider(provider_id)
        
        if provider and provider.email:
            success = self.care_provider_service.contact_provider(provider, "email")
            if not success:
                QMessageBox.warning(self, "Error", "Failed to open email client.")
        else:
            QMessageBox.information(self, "No Email", "No email address available for this provider.")
    
    def create_appointment_from_provider(self):
        """Create appointment with selected care provider"""
        selected_row = self.providers_table.currentRow()
        if selected_row < 0:
            return
        
        provider_id = self.providers_table.item(selected_row, 0).data(Qt.UserRole)
        provider = self.care_provider_service.get_provider(provider_id)
        
        if provider:
            # Create appointment data
            appointment_data = {
                'title': f"Appointment with {provider.title} {provider.name}",
                'description': f"Healthcare appointment with {provider.specialty}",
                'start_time': '',  # Will be filled by calendar
                'end_time': '',    # Will be filled by calendar
                'category': 'healthcare'
            }
            
            success = self.care_provider_service.create_appointment_from_provider(provider, appointment_data)
            if success:
                QMessageBox.information(self, "Success", 
                                      f"Appointment created for {provider.name}. Please check the Calendar panel to set the date and time.")
            else:
                QMessageBox.warning(self, "Error", "Failed to create appointment.")
    
    def filter_providers(self):
        """Filter providers based on search criteria"""
        search_term = self.search_edit.text().strip()
        specialty_filter = self.specialty_filter_combo.currentText()
        emergency_only = self.emergency_filter_checkbox.isChecked()
        
        # Get filtered providers
        if search_term:
            providers = self.care_provider_service.search_providers(search_term)
        else:
            providers = self.care_provider_service.get_providers(
                specialty_filter if specialty_filter != "All Specialties" else None,
                emergency_only
            )
        
        self.update_providers_table(providers)
    
    def refresh_providers(self):
        """Refresh providers list and statistics"""
        if not self.care_provider_service:
            print("Care provider service is not available.")
            return
            
        # Update specialty filter
        specialties = self.care_provider_service.get_specialties()
        self.specialty_filter_combo.clear()
        self.specialty_filter_combo.addItem("All Specialties")
        self.specialty_filter_combo.addItems(specialties)
        
        # Update statistics
        stats = self.care_provider_service.get_provider_statistics()
        self.total_providers_label.setText(f"Total Providers: {stats.get('total_providers', 0)}")
        self.emergency_providers_label.setText(f"Emergency Contacts: {stats.get('emergency_providers', 0)}")
        self.specialties_count_label.setText(f"Specialties: {len(stats.get('specialty_counts', {}))}")
        
        # Update table
        providers = self.care_provider_service.get_providers()
        self.update_providers_table(providers)
    
    def update_providers_table(self, providers: List[CareProviderData]):
        """Update the providers table with given providers"""
        self.providers_table.setRowCount(len(providers))
        
        for row, provider in enumerate(providers):
            # Name (with provider_id as user data)
            name_item = QTableWidgetItem(f"{provider.title} {provider.name}".strip())
            name_item.setData(Qt.UserRole, provider.provider_id)
            self.providers_table.setItem(row, 0, name_item)
            
            # Title
            self.providers_table.setItem(row, 1, QTableWidgetItem(provider.title))
            
            # Specialty
            self.providers_table.setItem(row, 2, QTableWidgetItem(provider.specialty))
            
            # Organization
            self.providers_table.setItem(row, 3, QTableWidgetItem(provider.organization))
            
            # Phone
            phone_item = QTableWidgetItem(provider.phone or "")
            if provider.phone:
                phone_item.setToolTip(f"Click to call: {provider.phone}")
            self.providers_table.setItem(row, 4, phone_item)
            
            # Email
            email_item = QTableWidgetItem(provider.email or "")
            if provider.email:
                email_item.setToolTip(f"Click to email: {provider.email}")
            self.providers_table.setItem(row, 5, email_item)
            
            # Emergency
            emergency_item = QTableWidgetItem("🚨" if provider.emergency_contact else "")
            self.providers_table.setItem(row, 6, emergency_item)
            
            # Actions
            actions_item = QTableWidgetItem("📞 📧 📅")
            actions_item.setToolTip("Call, Email, Create Appointment")
            self.providers_table.setItem(row, 7, actions_item)
    
    # Signal handlers
    def on_provider_added(self, provider: CareProviderData):
        """Handle provider added signal"""
        self.refresh_providers()
    
    def on_provider_updated(self, provider: CareProviderData):
        """Handle provider updated signal"""
        self.refresh_providers()
    
    def on_provider_deleted(self, provider_id: str):
        """Handle provider deleted signal"""
        self.refresh_providers()
    
    def on_appointment_created(self, appointment_data: Dict[str, Any]):
        """Handle appointment created signal"""
        # This could trigger a refresh of the calendar panel
        QMessageBox.information(self, "Appointment Created", 
                              f"Appointment '{appointment_data.get('title', '')}' created successfully!")
    
    # Existing health logging methods (simplified for brevity)
    def save_entry(self):
        """Save health log entry"""
        try:
            if self._save_entry_to_database():
                QMessageBox.information(self, "Success", "Health log entry saved successfully!")
                self.clear_form()
                self.load_health_entries()
            else:
                QMessageBox.warning(self, "Error", "Failed to save entry to database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save entry: {str(e)}")
    
    def clear_form(self):
        """Clear the form"""
        self.date_edit.setDate(QDate.currentDate())
        self.items_edit.clear()
        self.risk_combo.setCurrentIndex(0)
        self.onset_spin.setValue(0)
        self.severity_spin.setValue(0)
        self.symptoms_edit.clear()
        self.bristol_buttons[3].setChecked(True)  # Default to type 4
        self.hydration_spin.setValue(0)
        self.fiber_spin.setValue(0)
        self.mood_combo.setCurrentIndex(0)
        self.energy_slider.setValue(5)
        self.notes_edit.clear()
    
    def analyze_patterns(self):
        """Analyze health patterns and correlations"""
        QMessageBox.information(self, "Pattern Analysis", "Health pattern analysis feature coming soon!")
    
    def export_health_data(self):
        """Export health data to file"""
        QMessageBox.information(self, "Export", "Health data export feature coming soon!")
    
    def import_health_data(self):
        """Import health data from file"""
        QMessageBox.information(self, "Import", "Health data import feature coming soon!")
    
    def bulk_add_entries(self):
        """Bulk add health entries"""
        QMessageBox.information(self, "Bulk Add", "Bulk add feature coming soon!")
    
    def refresh(self):
        """Refresh panel data"""
        self.load_health_entries()
        self.refresh_providers()
    
    def load_health_entries(self):
        """Load health log entries from database"""
        try:
            from utils.db import get_connection
            
            db = get_connection()
            cursor = db.cursor()
            cursor.execute("""
                SELECT date, time, meal_type, items, risk,
                       onset_min, severity, symptoms, stool,
                       hydration_liters, fiber_grams, mood, energy_level, notes
                FROM health_log 
                ORDER BY date DESC, time DESC 
                LIMIT 100
            """)
            entries = cursor.fetchall()
            
            # Clear existing data
            self.entries_table.setRowCount(len(entries))
            
            for row, entry in enumerate(entries):
                date, time, meal_type, items, risk, onset_min, severity, symptoms, stool, hydration_liters, fiber_grams, mood, energy_level, notes = entry
                
                # Populate table
                self.entries_table.setItem(row, 0, QTableWidgetItem(date or ""))
                self.entries_table.setItem(row, 1, QTableWidgetItem(time or ""))
                self.entries_table.setItem(row, 2, QTableWidgetItem(meal_type or ""))
                self.entries_table.setItem(row, 3, QTableWidgetItem(items or ""))
                self.entries_table.setItem(row, 4, QTableWidgetItem(risk or ""))
                self.entries_table.setItem(row, 5, QTableWidgetItem(str(severity) if severity else ""))
                self.entries_table.setItem(row, 6, QTableWidgetItem(symptoms or ""))
            
            # If no entries in database, show message
            if len(entries) == 0:
                self.entries_table.setRowCount(1)
                self.entries_table.setItem(0, 0, QTableWidgetItem("No health log entries found"))
                self.entries_table.setItem(0, 1, QTableWidgetItem("Add your first entry using the form above"))
                
        except Exception as e:
            print(f"Error loading health log entries from database: {e}")
            # Show error message
            self.entries_table.setRowCount(1)
            self.entries_table.setItem(0, 0, QTableWidgetItem("Error loading entries"))
            self.entries_table.setItem(0, 1, QTableWidgetItem(str(e)))
    
    def _save_entry_to_database(self):
        """Save health log entry to database"""
        try:
            from utils.db import get_connection
            
            db = get_connection()
            cursor = db.cursor()
            
            # Get form data
            date = self.date_edit.date().toString("yyyy-MM-dd")
            time = self.time_combo.currentText()
            meal_type = self.meal_combo.currentText()
            food_items = self.items_edit.toPlainText().strip()
            gluten_risk = self.risk_combo.currentText()
            onset_time = self.onset_spin.value()
            severity = self.severity_spin.value()
            symptoms = self.symptoms_edit.toPlainText().strip()
            
            # Get Bristol type
            bristol_type = None
            for i, button in enumerate(self.bristol_buttons):
                if button.isChecked():
                    bristol_type = i + 1
                    break
            
            hydration_level = self.hydration_spin.value()
            fiber_intake = self.fiber_spin.value()
            mood = self.mood_combo.currentText()
            energy_level = self.energy_slider.value()
            notes = self.notes_edit.toPlainText().strip()
            
            # Insert entry
            cursor.execute("""
                INSERT INTO health_log (date, time, meal_type, items, risk,
                                      onset_min, severity, symptoms, stool,
                                      hydration_liters, fiber_grams, mood, energy_level, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date, time, meal_type, food_items, gluten_risk,
                onset_time, severity, symptoms, bristol_type,
                hydration_level, fiber_intake, mood, energy_level, notes
            ))
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error saving health log entry to database: {e}")
            return False
