# path: utils/date_picker_widget.py
"""
Date Picker Widget for PySide6 Application

Provides a reusable date picker with calendar popup and direct date input options.
"""

from typing import Optional
from datetime import datetime, date
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QCalendarWidget,
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox,
    QMessageBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont


class DatePickerWidget(QWidget):
    """Reusable date picker widget with calendar popup and direct input"""
    
    def __init__(self, parent=None, initial_date: Optional[date] = None):
        super().__init__(parent)
        self.selected_date = initial_date or date.today()
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """Set up the date picker UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Date input field
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("YYYY-MM-DD")
        self.date_edit.setMaximumWidth(120)
        self.date_edit.textChanged.connect(self.on_text_changed)
        self.date_edit.returnPressed.connect(self.validate_and_set_date)
        self.date_edit.editingFinished.connect(self.validate_and_set_date)  # Validate on focus loss
        layout.addWidget(self.date_edit)
        
        # Calendar popup button - themed with calendar icon
        self.calendar_btn = QPushButton("📅")
        self.calendar_btn.setMaximumWidth(35)
        self.calendar_btn.setMinimumWidth(35)
        self.calendar_btn.setToolTip("Open calendar to select date")
        self.calendar_btn.clicked.connect(self.show_calendar_popup)
        # Theme-integrated button styling
        self.calendar_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #2e7d32;
                border-radius: 4px;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #2e7d32);
                color: white;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66bb6a, stop:1 #388e3c);
                border-color: #1b5e20;
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2e7d32, stop:1 #1b5e20);
                border-color: #0d3e0d;
            }
        """)
        layout.addWidget(self.calendar_btn)
    
    def on_text_changed(self, text: str):
        """Handle text changes in date input field"""
        # Remove auto-formatting to allow manual editing
        # Users can type dates freely and validation happens on Enter or focus loss
        pass
    
    def validate_and_set_date(self):
        """Validate and set date from text input"""
        text = self.date_edit.text().strip()
        if not text:
            return
        
        try:
            # Try to parse the date
            if len(text) == 10 and text.count('-') == 2:
                # Format: YYYY-MM-DD
                parsed_date = datetime.strptime(text, "%Y-%m-%d").date()
            elif len(text) == 8 and text.count('/') == 2:
                # Format: MM/DD/YYYY
                parsed_date = datetime.strptime(text, "%m/%d/%Y").date()
            elif len(text) == 8 and text.count('/') == 2:
                # Format: DD/MM/YYYY
                parsed_date = datetime.strptime(text, "%d/%m/%Y").date()
            else:
                raise ValueError("Invalid date format")
            
            self.set_date(parsed_date)
            
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Date", 
                              f"Please enter a valid date in YYYY-MM-DD format.\n\n"
                              f"Error: {str(e)}")
            self.update_display()  # Reset to current date
    
    def show_calendar_popup(self):
        """Show calendar popup for date selection"""
        dialog = DatePickerDialog(self, self.selected_date)
        if dialog.exec() == QDialog.Accepted:
            selected_date = dialog.get_selected_date()
            if selected_date:
                self.set_date(selected_date)
    
    def set_today(self):
        """Set date to today"""
        self.set_date(date.today())
    
    def set_date(self, new_date: date):
        """Set the selected date"""
        self.selected_date = new_date
        self.update_display()
    
    def get_date(self) -> date:
        """Get the selected date"""
        return self.selected_date
    
    def update_display(self):
        """Update the display to show current date"""
        self.date_edit.setText(self.selected_date.strftime("%Y-%m-%d"))


class DatePickerDialog(QDialog):
    """Calendar popup dialog for date selection"""
    
    def __init__(self, parent=None, initial_date: Optional[date] = None):
        super().__init__(parent)
        self.selected_date = initial_date or date.today()
        self.setWindowTitle("Select Date")
        self.setModal(True)
        self.resize(400, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the calendar dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Select Date")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Quick navigation
        nav_layout = QHBoxLayout()
        
        # Month selection
        nav_layout.addWidget(QLabel("Month:"))
        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        self.month_combo.currentTextChanged.connect(self.on_month_changed)
        nav_layout.addWidget(self.month_combo)
        
        # Year selection
        nav_layout.addWidget(QLabel("Year:"))
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2100)
        self.year_spin.valueChanged.connect(self.on_year_changed)
        nav_layout.addWidget(self.year_spin)
        
        # Today button
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(self.go_to_today)
        nav_layout.addWidget(today_btn)
        
        nav_layout.addStretch()
        layout.addLayout(nav_layout)
        
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        layout.addWidget(self.calendar)
        
        # Direct date input section
        input_group = QWidget()
        input_layout = QHBoxLayout(input_group)
        
        input_layout.addWidget(QLabel("Or enter date:"))
        
        # Date input field
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        self.date_input.setMaximumWidth(120)
        self.date_input.returnPressed.connect(self.on_date_entered)
        input_layout.addWidget(self.date_input)
        
        # Set button
        set_btn = QPushButton("Set")
        set_btn.clicked.connect(self.on_date_entered)
        input_layout.addWidget(set_btn)
        
        input_layout.addStretch()
        layout.addWidget(input_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initialize with current date
        self.initialize_date()
    
    def initialize_date(self):
        """Initialize dialog with current date"""
        self.month_combo.setCurrentIndex(self.selected_date.month - 1)
        self.year_spin.setValue(self.selected_date.year)
        self.calendar.setSelectedDate(QDate(self.selected_date.year, self.selected_date.month, self.selected_date.day))
        self.date_input.setText(self.selected_date.strftime("%Y-%m-%d"))
    
    def on_month_changed(self):
        """Handle month selection change"""
        month = self.month_combo.currentIndex() + 1
        year = self.year_spin.value()
        
        # Update calendar
        current_date = self.calendar.selectedDate()
        new_date = QDate(year, month, min(current_date.day(), 28))  # Use 28 to avoid month overflow
        self.calendar.setSelectedDate(new_date)
    
    def on_year_changed(self):
        """Handle year selection change"""
        month = self.month_combo.currentIndex() + 1
        year = self.year_spin.value()
        
        # Update calendar
        current_date = self.calendar.selectedDate()
        new_date = QDate(year, month, min(current_date.day(), 28))  # Use 28 to avoid month overflow
        self.calendar.setSelectedDate(new_date)
    
    def on_date_selected(self, qdate: QDate):
        """Handle calendar date selection"""
        self.selected_date = qdate.toPython()
        self.date_input.setText(self.selected_date.strftime("%Y-%m-%d"))
    
    def on_date_entered(self):
        """Handle direct date input"""
        text = self.date_input.text().strip()
        if not text:
            return
        
        try:
            # Try to parse the date
            if len(text) == 10 and text.count('-') == 2:
                # Format: YYYY-MM-DD
                parsed_date = datetime.strptime(text, "%Y-%m-%d").date()
            elif len(text) == 8 and text.count('/') == 2:
                # Format: MM/DD/YYYY
                parsed_date = datetime.strptime(text, "%m/%d/%Y").date()
            elif len(text) == 8 and text.count('/') == 2:
                # Format: DD/MM/YYYY
                parsed_date = datetime.strptime(text, "%d/%m/%Y").date()
            else:
                raise ValueError("Invalid date format")
            
            self.selected_date = parsed_date
            
            # Update calendar and dropdowns
            self.calendar.setSelectedDate(QDate(parsed_date.year, parsed_date.month, parsed_date.day))
            self.month_combo.setCurrentIndex(parsed_date.month - 1)
            self.year_spin.setValue(parsed_date.year)
            
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Date", 
                              f"Please enter a valid date in YYYY-MM-DD format.\n\n"
                              f"Error: {str(e)}")
            self.date_input.setText(self.selected_date.strftime("%Y-%m-%d"))
    
    def go_to_today(self):
        """Go to today's date"""
        today = date.today()
        self.selected_date = today
        self.calendar.setSelectedDate(QDate(today.year, today.month, today.day))
        self.month_combo.setCurrentIndex(today.month - 1)
        self.year_spin.setValue(today.year)
        self.date_input.setText(today.strftime("%Y-%m-%d"))
    
    def get_selected_date(self) -> date:
        """Get the selected date"""
        return self.selected_date
