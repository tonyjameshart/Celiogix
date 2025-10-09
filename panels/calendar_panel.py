# path: panels/calendar_panel_pyside6.py
"""
Calendar Panel for PySide6 Application with Care Provider Integration
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QMessageBox,
    QDialog, QDialogButtonBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from panels.base_panel import BasePanel
from panels.context_menu_mixin import CalendarContextMenuMixin
from services.care_provider_service import get_care_provider_service


class CalendarPanel(CalendarContextMenuMixin, BasePanel):
    """Calendar panel for PySide6 with Care Provider integration"""
    
    def __init__(self, master=None, app=None):
        super().__init__(master, app)
        self.care_provider_service = get_care_provider_service()
        self.care_provider_service.appointment_created.connect(self.on_appointment_created)
    
    def setup_ui(self):
        """Set up the calendar panel UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)  # Reduced spacing between elements
        
        # Date selection and navigation
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(QLabel("Month:"))
        self.month_combo = QComboBox()
        self.month_combo.addItems(["January", "February", "March", "April", "May", "June", 
                                 "July", "August", "September", "October", "November", "December"])
        self.month_combo.currentTextChanged.connect(self.load_calendar)
        nav_layout.addWidget(self.month_combo)
        
        nav_layout.addWidget(QLabel("Year:"))
        self.year_combo = QComboBox()
        
        # Get current year and set range to 5 years before and after
        from datetime import datetime
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Add years from 5 years before to 5 years after current year
        self.year_combo.addItems([str(year) for year in range(current_year-5, current_year+6)])
        
        # Set default to current year and month
        self.year_combo.setCurrentText(str(current_year))
        self.month_combo.setCurrentIndex(current_month - 1)  # Month combo is 0-indexed
        
        self.year_combo.currentTextChanged.connect(self.load_calendar)
        nav_layout.addWidget(self.year_combo)
        
        # Add view mode selection
        nav_layout.addWidget(QLabel("View:"))
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Month", "Week", "Year"])
        self.view_mode_combo.setCurrentText("Month")
        self.view_mode_combo.currentTextChanged.connect(self.on_view_mode_changed)
        nav_layout.addWidget(self.view_mode_combo)
        
        nav_layout.addStretch()
        
        # Add Today button
        today_btn = QPushButton("📅 Today")
        today_btn.clicked.connect(self.go_to_today)
        today_btn.setToolTip("Go to current date")
        nav_layout.addWidget(today_btn)
        
        add_event_btn = QPushButton("Add Event")
        add_event_btn.clicked.connect(self.add_event)
        nav_layout.addWidget(add_event_btn)
        
        create_appointment_btn = QPushButton("📅 Create Appointment")
        create_appointment_btn.clicked.connect(self.create_appointment_from_provider)
        create_appointment_btn.setToolTip("Create appointment with a care provider")
        nav_layout.addWidget(create_appointment_btn)
        
        main_layout.addLayout(nav_layout)
        
        # Calendar view (simplified as a table)
        self.calendar_table = QTableWidget()
        self.calendar_table.setColumnCount(7)
        self.calendar_table.setHorizontalHeaderLabels(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
        
        # Set equal column widths for calendar days
        header = self.calendar_table.horizontalHeader()
        header.setStretchLastSection(False)  # Disable stretch last section
        header.setSectionResizeMode(QHeaderView.Stretch)  # Make all columns equal width
        
        self.calendar_table.setAlternatingRowColors(True)
        self.calendar_table.itemDoubleClicked.connect(self.view_day_events)
        
        # Apply custom delegate to suppress selection borders
        from utils.custom_delegates import CleanSelectionDelegate
        self.calendar_table.setItemDelegate(CleanSelectionDelegate())
        
        # Add minimal custom styling - delegate handles selection
        self.calendar_table.setStyleSheet("""
            QTableWidget::item {
                padding: 6px;
                border: none;          /* no cell border */
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;    /* visible selected background */
                color: #1976d2;               /* selected text color */
                /* no border here */
            }
        """)
        
        main_layout.addWidget(self.calendar_table)
        
        # Event list
        events_layout = QHBoxLayout()
        events_layout.addWidget(QLabel("Events:"))
        self.events_list = QTableWidget()
        self.events_list.setColumnCount(3)
        self.events_list.setHorizontalHeaderLabels(["Date", "Event", "Type"])
        self.events_list.horizontalHeader().setStretchLastSection(True)
        self.events_list.setMaximumHeight(150)
        self.events_list.itemDoubleClicked.connect(self.edit_event)
        
        # Apply custom delegate to suppress selection borders
        from utils.custom_delegates import CleanSelectionDelegate
        self.events_list.setItemDelegate(CleanSelectionDelegate())
        
        # Add minimal custom styling - delegate handles selection
        self.events_list.setStyleSheet("""
            QTableWidget::item {
                padding: 6px;
                border: none;          /* no cell border */
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;    /* visible selected background */
                color: #1976d2;               /* selected text color */
                /* no border here */
            }
        """)
        
        events_layout.addWidget(self.events_list)
        
        main_layout.addLayout(events_layout)
        
        # Event management buttons
        button_layout = QHBoxLayout()
        
        self.edit_event_btn = QPushButton("Edit Event")
        self.edit_event_btn.clicked.connect(self.edit_event)
        self.edit_event_btn.setEnabled(False)
        
        self.delete_event_btn = QPushButton("Delete Event")
        self.delete_event_btn.clicked.connect(self.delete_event)
        self.delete_event_btn.setEnabled(False)
        
        export_btn = QPushButton("Export Calendar")
        export_btn.clicked.connect(self.export_calendar)
        
        import_btn = QPushButton("Import Calendar")
        import_btn.clicked.connect(self.import_calendar)
        
        button_layout.addWidget(self.edit_event_btn)
        button_layout.addWidget(self.delete_event_btn)
        button_layout.addStretch()
        button_layout.addWidget(export_btn)
        button_layout.addWidget(import_btn)
        
        main_layout.addLayout(button_layout)
        
        # Connect selection changes
        self.events_list.selectionModel().selectionChanged.connect(self.on_event_selection_changed)
        
        # Load initial calendar
        self.load_calendar()
    
    def load_calendar(self):
        """Load calendar for the selected month and year"""
        # Check if calendar table is initialized
        if not hasattr(self, 'calendar_table') or not self.calendar_table:
            return
            
        view_mode = self.view_mode_combo.currentText()
        
        if view_mode == "Month":
            self.load_month_view()
        elif view_mode == "Week":
            self.load_week_view()
        else:  # Year view
            self.load_year_view()
        
        # Load events for the selected period
        self.load_events()
    
    def load_month_view(self):
        """Load month view calendar"""
        from datetime import datetime, timedelta
        import calendar
        
        month = self.month_combo.currentText()
        year = int(self.year_combo.currentText())
        
        # Convert month name to number
        month_num = datetime.strptime(month, "%B").month
        
        # Get first day of month and number of days
        first_day = datetime(year, month_num, 1)
        days_in_month = calendar.monthrange(year, month_num)[1]
        
        # Get the day of week for the first day (0=Monday, 6=Sunday)
        # Adjust to match our calendar (0=Sunday, 6=Saturday)
        first_weekday = (first_day.weekday() + 1) % 7
        
        # Reset table to month view (7 columns, proper headers)
        self.calendar_table.setColumnCount(7)
        self.calendar_table.setHorizontalHeaderLabels(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
        
        # Clear the table
        self.calendar_table.setRowCount(6)
        for row in range(6):
            for col in range(7):
                self.calendar_table.setItem(row, col, QTableWidgetItem(""))
        
        # Fill in the calendar
        current_day = 1
        for row in range(6):
            for col in range(7):
                if row == 0 and col < first_weekday:
                    # Empty cells before first day of month
                    continue
                elif current_day <= days_in_month:
                    day_item = QTableWidgetItem(str(current_day))
                    
                    # Highlight weekends
                    if col == 0 or col == 6:  # Sunday or Saturday
                        day_item.setBackground(Qt.lightGray)
                    
                    # Mark today if it's the current date
                    today = datetime.now()
                    if (year == today.year and month_num == today.month and 
                        current_day == today.day):
                        day_item.setBackground(Qt.yellow)
                    
                    # Mark some days with events (sample data)
                    if current_day in [5, 12, 15, 22, 28]:
                        day_item.setText(f"{current_day} 📅")
                        day_item.setToolTip("Has events scheduled")
                    
                    self.calendar_table.setItem(row, col, day_item)
                    current_day += 1
    
    def load_week_view(self):
        """Load week view calendar"""
        from datetime import datetime, timedelta
        
        month = self.month_combo.currentText()
        year = int(self.year_combo.currentText())
        
        # Convert month name to number
        month_num = datetime.strptime(month, "%B").month
        
        # Get current date or first day of selected month
        current_date = datetime.now()
        if year != current_date.year or month_num != current_date.month:
            current_date = datetime(year, month_num, 1)
        
        # Find the start of the week (Sunday)
        days_since_sunday = current_date.weekday() + 1  # +1 because weekday() returns 0=Monday
        week_start = current_date - timedelta(days=days_since_sunday)
        
        # Reset table to week view (7 columns, proper headers)
        self.calendar_table.setColumnCount(7)
        self.calendar_table.setHorizontalHeaderLabels(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
        
        # Clear the table and set to single row
        self.calendar_table.setRowCount(1)
        for col in range(7):
            self.calendar_table.setItem(0, col, QTableWidgetItem(""))
        
        # Fill in the week
        for col in range(7):
            day_date = week_start + timedelta(days=col)
            day_item = QTableWidgetItem(f"{day_date.day}")
            
            # Highlight weekends
            if col == 0 or col == 6:  # Sunday or Saturday
                day_item.setBackground(Qt.lightGray)
            
            # Highlight today
            today = datetime.now()
            if (day_date.year == today.year and day_date.month == today.month and 
                day_date.day == today.day):
                day_item.setBackground(Qt.yellow)
            
            # Mark some days with events (sample data)
            if day_date.day in [5, 12, 15, 22, 28]:
                day_item.setText(f"{day_date.day} 📅")
                day_item.setToolTip("Has events scheduled")
            
            self.calendar_table.setItem(0, col, day_item)
    
    def on_view_mode_changed(self):
        """Handle view mode change"""
        self.load_calendar()
    
    def go_to_today(self):
        """Go to current date and highlight today"""
        from datetime import datetime
        import calendar
        
        today = datetime.now()
        current_year = today.year
        current_month = today.month
        current_day = today.day
        
        # Update year and month dropdowns to current date
        self.year_combo.setCurrentText(str(current_year))
        self.month_combo.setCurrentIndex(current_month - 1)  # Month combo is 0-indexed
        
        # Reload calendar to show current date
        self.load_calendar()
        
        # Select today's date in the calendar table
        self._select_today_in_table(current_year, current_month, current_day)
    
    def _select_today_in_table(self, year, month, day):
        """Select today's date in the calendar table"""
        from datetime import datetime
        import calendar
        
        # Only select if we're in month view and showing the current month
        if self.view_mode_combo.currentText() != "Month":
            return
            
        current_month = self.month_combo.currentText()
        current_year = int(self.year_combo.currentText())
        
        # Convert month name to number
        month_num = datetime.strptime(current_month, "%B").month
        
        # Only select if we're viewing the current month
        if year != current_year or month != month_num:
            return
        
        # Calculate the position of today's date in the calendar grid
        first_day = datetime(year, month, 1)
        first_weekday = (first_day.weekday() + 1) % 7  # Adjust for Sunday=0
        
        # Find the row and column for today's date
        row = (day - 1 + first_weekday) // 7
        col = (day - 1 + first_weekday) % 7
        
        # Make sure the position is valid
        if 0 <= row < self.calendar_table.rowCount() and 0 <= col < self.calendar_table.columnCount():
            # Clear any existing selection
            self.calendar_table.clearSelection()
            
            # Select the today's date cell
            self.calendar_table.setCurrentCell(row, col)
            
            # Ensure the cell is visible
            self.calendar_table.scrollToItem(self.calendar_table.item(row, col))
    
    def load_year_view(self):
        """Load year view calendar showing all 12 months"""
        from datetime import datetime
        import calendar
        
        year = int(self.year_combo.currentText())
        
        # Set up table for year view (4 rows x 3 columns for 12 months)
        self.calendar_table.setRowCount(4)
        self.calendar_table.setColumnCount(3)
        
        # Update header labels for year view (quarters)
        self.calendar_table.setHorizontalHeaderLabels(["Q1", "Q2", "Q3"])
        
        # Month names for reference
        month_names = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        
        # Clear all cells first
        for row in range(4):
            for col in range(3):
                self.calendar_table.setItem(row, col, QTableWidgetItem(""))
        
        # Fill in the year view
        for month_idx in range(12):
            row = month_idx // 3
            col = month_idx % 3
            
            month_name = month_names[month_idx]
            month_num = month_idx + 1
            
            # Get number of days in this month
            days_in_month = calendar.monthrange(year, month_num)[1]
            
            # Create month cell content
            month_text = f"{month_name}\n{days_in_month} days"
            
            # Highlight current month if it's the current year
            today = datetime.now()
            if year == today.year and month_num == today.month:
                month_text += "\n📅 Current"
            
            month_item = QTableWidgetItem(month_text)
            month_item.setTextAlignment(Qt.AlignCenter)
            
            # Highlight current month
            if year == today.year and month_num == today.month:
                month_item.setBackground(Qt.yellow)
            
            # Highlight months with events (sample data)
            if month_num in [1, 3, 6, 9, 12]:  # Sample months with events
                month_item.setBackground(Qt.lightBlue)
            
            self.calendar_table.setItem(row, col, month_item)
    
    def load_events(self):
        """Load events for the selected month"""
        sample_events = [
            ("2024-01-05", "Doctor Appointment", "Health"),
            ("2024-01-12", "Gluten-Free Cooking Class", "Education"),
            ("2024-01-15", "Blood Test", "Health"),
            ("2024-01-22", "Nutritionist Visit", "Health"),
            ("2024-01-28", "Family Dinner", "Social")
        ]
        
        self.events_list.setRowCount(len(sample_events))
        for row, (date, event, event_type) in enumerate(sample_events):
            self.events_list.setItem(row, 0, QTableWidgetItem(date))
            self.events_list.setItem(row, 1, QTableWidgetItem(event))
            self.events_list.setItem(row, 2, QTableWidgetItem(event_type))
    
    def on_event_selection_changed(self):
        """Handle event selection changes"""
        has_selection = len(self.events_list.selectedItems()) > 0
        self.edit_event_btn.setEnabled(has_selection)
        self.delete_event_btn.setEnabled(has_selection)
    
    def add_event(self):
        """Add a new event"""
        # Create add event dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Event")
        dialog.setModal(True)
        dialog.setMinimumSize(400, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel("Add New Event")
        header_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header_label)
        
        # Event name
        name_layout = QHBoxLayout()
        name_layout.setSpacing(10)  # Reduced spacing between label and input
        name_layout.addWidget(QLabel("Event Name:"))
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter event name...")
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        
        # Date
        date_layout = QHBoxLayout()
        date_layout.setSpacing(10)  # Reduced spacing between label and input
        date_layout.addWidget(QLabel("Date:"))
        from utils.date_picker_widget import DatePickerWidget
        date_picker = DatePickerWidget()
        date_layout.addWidget(date_picker)
        layout.addLayout(date_layout)
        
        # Time
        time_layout = QHBoxLayout()
        time_layout.setSpacing(10)  # Reduced spacing between label and input
        time_layout.addWidget(QLabel("Time:"))
        from utils.time_picker_widget import TimePickerWidget
        time_picker = TimePickerWidget()
        time_layout.addWidget(time_picker)
        layout.addLayout(time_layout)
        
        # Event type
        type_layout = QHBoxLayout()
        type_layout.setSpacing(10)  # Reduced spacing between label and input
        type_layout.addWidget(QLabel("Event Type:"))
        type_combo = QComboBox()
        type_combo.addItems([
            "Medical Appointment",
            "Doctor Visit",
            "Lab Test",
            "Medication Reminder",
            "Meal Planning",
            "Shopping",
            "Exercise",
            "Social Event",
            "Work",
            "Other"
        ])
        type_layout.addWidget(type_combo)
        layout.addLayout(type_layout)
        
        # Priority
        priority_layout = QHBoxLayout()
        priority_layout.setSpacing(10)  # Reduced spacing between label and input
        priority_layout.addWidget(QLabel("Priority:"))
        priority_combo = QComboBox()
        priority_combo.addItems(["Low", "Medium", "High", "Urgent"])
        priority_layout.addWidget(priority_combo)
        layout.addLayout(priority_layout)
        
        # Description
        desc_layout = QVBoxLayout()
        desc_layout.setSpacing(5)  # Reduced spacing between label and input
        desc_layout.addWidget(QLabel("Description:"))
        desc_edit = QTextEdit()
        desc_edit.setMaximumHeight(100)
        desc_edit.setPlaceholderText("Add event description, notes, or special instructions...")
        desc_layout.addWidget(desc_edit)
        layout.addLayout(desc_layout)
        
        # Reminder
        reminder_layout = QHBoxLayout()
        reminder_layout.setSpacing(10)  # Reduced spacing between label and input
        reminder_layout.addWidget(QLabel("Reminder:"))
        reminder_combo = QComboBox()
        reminder_combo.addItems(["None", "15 minutes", "1 hour", "1 day", "1 week"])
        reminder_layout.addWidget(reminder_combo)
        layout.addLayout(reminder_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Add Event")
        save_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        if dialog.exec() == QDialog.Accepted:
            name = name_edit.text().strip()
            selected_date = date_picker.get_date()
            date = selected_date.strftime("%Y-%m-%d")
            time = time_picker.get_time_string()
            event_type = type_combo.currentText()
            priority = priority_combo.currentText()
            description = desc_edit.toPlainText().strip()
            reminder = reminder_combo.currentText()
            
            if not name:
                QMessageBox.warning(self, "Validation Error", "Event name is required.")
                return
            
            # Add to events list
            row_position = self.events_list.rowCount()
            self.events_list.insertRow(row_position)
            self.events_list.setItem(row_position, 0, QTableWidgetItem(date))
            self.events_list.setItem(row_position, 1, QTableWidgetItem(name))
            self.events_list.setItem(row_position, 2, QTableWidgetItem(event_type))
            
            # Save to database
            self._save_event_to_database(0, name, date, time, event_type, priority, description, reminder)
            
            # Refresh events list and calendar
            self.load_events()
            self.load_calendar()  # Refresh calendar to show new events
            
            QMessageBox.information(self, "Success", f"Event '{name}' added successfully!")
    
    def edit_event(self):
        """Edit selected event"""
        current_row = self.events_list.currentRow()
        if current_row >= 0:
            event_name = self.events_list.item(current_row, 1).text()
            event_date = self.events_list.item(current_row, 0).text()
            event_type = self.events_list.item(current_row, 2).text()
            
            # Create edit dialog (similar to add dialog but pre-filled)
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit Event: {event_name}")
            dialog.setModal(True)
            dialog.setMinimumSize(400, 500)
            
            layout = QVBoxLayout(dialog)
            
            # Header
            header_label = QLabel(f"Edit Event: {event_name}")
            header_label.setFont(QFont("Arial", 12, QFont.Bold))
            layout.addWidget(header_label)
            
            # Event name
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Event Name:"))
            name_edit = QLineEdit(event_name)
            name_layout.addWidget(name_edit)
            layout.addLayout(name_layout)
            
            # Date
            date_layout = QHBoxLayout()
            date_layout.addWidget(QLabel("Date:"))
            date_edit = QLineEdit(event_date)
            date_layout.addWidget(date_edit)
            layout.addLayout(date_layout)
            
            # Time
            time_layout = QHBoxLayout()
            time_layout.addWidget(QLabel("Time:"))
            from utils.time_picker_widget import TimePickerWidget
            from datetime import time
            time_picker = TimePickerWidget(initial_time=time(9, 0))  # Default time
            time_layout.addWidget(time_picker)
            layout.addLayout(time_layout)
            
            # Event type
            type_layout = QHBoxLayout()
            type_layout.addWidget(QLabel("Event Type:"))
            type_combo = QComboBox()
            type_combo.addItems([
                "Medical Appointment",
                "Health Check",
                "Symptom Tracking",
                "Medication Reminder",
                "Diet Planning",
                "Exercise",
                "Social Event",
                "Work",
                "Other"
            ])
            type_combo.setCurrentText(event_type)
            type_layout.addWidget(type_combo)
            layout.addLayout(type_layout)
            
            # Priority
            priority_layout = QHBoxLayout()
            priority_layout.addWidget(QLabel("Priority:"))
            priority_combo = QComboBox()
            priority_combo.addItems(["Low", "Medium", "High", "Urgent"])
            priority_layout.addWidget(priority_combo)
            layout.addLayout(priority_layout)
            
            # Description
            desc_layout = QVBoxLayout()
            desc_layout.addWidget(QLabel("Description:"))
            desc_edit = QTextEdit("")
            desc_edit.setMaximumHeight(100)
            desc_edit.setPlaceholderText("Add event description or notes...")
            layout.addLayout(desc_layout)
            
            # Reminder
            reminder_layout = QHBoxLayout()
            reminder_layout.addWidget(QLabel("Reminder:"))
            reminder_combo = QComboBox()
            reminder_combo.addItems(["None", "15 minutes", "1 hour", "1 day", "1 week"])
            reminder_layout.addWidget(reminder_combo)
            layout.addLayout(reminder_layout)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            save_btn = QPushButton("Update Event")
            save_btn.clicked.connect(dialog.accept)
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            if dialog.exec() == QDialog.Accepted:
                new_name = name_edit.text().strip()
                new_date = date_edit.text().strip()
                new_time = time_picker.get_time_string()
                event_type = type_combo.currentText()
                priority = priority_combo.currentText()
                description = desc_edit.toPlainText().strip()
                reminder = reminder_combo.currentText()
                
                if not new_name:
                    QMessageBox.warning(self, "Validation Error", "Event name is required.")
                    return
                
                if not new_date:
                    QMessageBox.warning(self, "Validation Error", "Event date is required.")
                    return
                
                # Update the event
                self.events_list.setItem(current_row, 0, QTableWidgetItem(new_date))
                self.events_list.setItem(current_row, 1, QTableWidgetItem(new_name))
                self.events_list.setItem(current_row, 2, QTableWidgetItem(event_type))
                
                # Save to database
                self._save_event_to_database(current_row, new_name, new_date, new_time, event_type, priority, description, reminder)
                
                # Refresh events list and calendar
                self.load_events()
                self.load_calendar()  # Refresh calendar to show updated events
                
                QMessageBox.information(self, "Success", "Event updated successfully!")
    
    def _save_event_to_database(self, row_id: int, name: str, date: str, time: str, event_type: str, priority: str, description: str, reminder: str):
        """Save event to database"""
        try:
            from utils.db import get_connection
            
            db = get_connection()
            cursor = db.cursor()
            
            # Create calendar_events table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT,
                    category TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Update event in database
            if row_id > 0:
                cursor.execute("""
                    UPDATE calendar_events 
                    SET title = ?, date = ?, time = ?, category = ?, description = ?
                    WHERE id = ?
                """, (name, date, time, event_type, description, row_id + 1))
            else:
                cursor.execute("""
                    INSERT INTO calendar_events (title, date, time, category, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, date, time, event_type, description))
            
            db.commit()
            
        except Exception as e:
            print(f"Error saving event to database: {str(e)}")
    
    def delete_event(self):
        """Delete selected event"""
        current_row = self.events_list.currentRow()
        if current_row >= 0:
            event_name = self.events_list.item(current_row, 1).text()
            reply = QMessageBox.question(self, "Delete Event", 
                                       f"Are you sure you want to delete '{event_name}'?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.events_list.removeRow(current_row)
    
    def view_day_events(self):
        """View events for selected day"""
        current_item = self.calendar_table.currentItem()
        if current_item:
            day = current_item.text().replace("📅", "").strip()
            if day.isdigit():
                # Get the current month and year
                month = self.month_combo.currentText()
                year = int(self.year_combo.currentText())
                
                # Create a proper date string
                from datetime import datetime
                try:
                    month_num = datetime.strptime(month, "%B").month
                    date_str = f"{year}-{month_num:02d}-{int(day):02d}"
                    
                    # Get events for this specific date
                    events_for_day = []
                    for row in range(self.events_list.rowCount()):
                        event_date_item = self.events_list.item(row, 0)
                        if event_date_item and event_date_item.text() == date_str:
                            event_name_item = self.events_list.item(row, 1)
                            event_type_item = self.events_list.item(row, 2)
                            if event_name_item and event_type_item:
                                events_for_day.append(f"• {event_name_item.text()} ({event_type_item.text()})")
                    
                    # Display events or show message if none
                    if events_for_day:
                        events_text = f"Events for {month} {day}, {year}:\n\n" + "\n".join(events_for_day)
                    else:
                        events_text = f"No events scheduled for {month} {day}, {year}."
                    
                    # Create a proper dialog to show events
                    dialog = QDialog(self)
                    dialog.setWindowTitle(f"Events for {month} {day}, {year}")
                    dialog.setModal(True)
                    dialog.resize(400, 300)
                    
                    layout = QVBoxLayout(dialog)
                    
                    # Event list
                    events_text_edit = QTextEdit()
                    events_text_edit.setPlainText(events_text)
                    events_text_edit.setReadOnly(True)
                    layout.addWidget(events_text_edit)
                    
                    # Buttons
                    button_layout = QHBoxLayout()
                    close_btn = QPushButton("Close")
                    close_btn.clicked.connect(dialog.accept)
                    button_layout.addWidget(close_btn)
                    
                    # Add event button
                    add_event_btn = QPushButton("Add Event")
                    add_event_btn.clicked.connect(lambda: self.add_event_for_date(date_str, dialog))
                    button_layout.addWidget(add_event_btn)
                    
                    layout.addLayout(button_layout)
                    dialog.exec()
                    
                except ValueError:
                    QMessageBox.warning(self, "Error", "Invalid date format.")
    
    def add_event_for_date(self, date_str, parent_dialog):
        """Add an event for a specific date"""
        parent_dialog.accept()  # Close the day events dialog
        
        # Set the date in the add event dialog
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Create a simplified add event dialog for this specific date
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Add Event for {date_obj.strftime('%B %d, %Y')}")
            dialog.setModal(True)
            dialog.setMinimumSize(400, 300)
            
            layout = QVBoxLayout(dialog)
            
            # Event name
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Event Name:"))
            name_edit = QLineEdit()
            name_edit.setPlaceholderText("Enter event name...")
            name_layout.addWidget(name_edit)
            layout.addLayout(name_layout)
            
            # Event type
            type_layout = QHBoxLayout()
            type_layout.addWidget(QLabel("Event Type:"))
            type_combo = QComboBox()
            type_combo.addItems([
                "Medical Appointment",
                "Doctor Visit",
                "Lab Test",
                "Medication Reminder",
                "Meal Planning",
                "Shopping",
                "Exercise",
                "Social Event",
                "Work",
                "Other"
            ])
            type_layout.addWidget(type_combo)
            layout.addLayout(type_layout)
            
            # Time
            time_layout = QHBoxLayout()
            time_layout.addWidget(QLabel("Time:"))
            from utils.time_picker_widget import TimePickerWidget
            time_picker = TimePickerWidget()
            time_layout.addWidget(time_picker)
            layout.addLayout(time_layout)
            
            # Description
            desc_layout = QVBoxLayout()
            desc_layout.addWidget(QLabel("Description:"))
            desc_edit = QTextEdit()
            desc_edit.setMaximumHeight(80)
            desc_edit.setPlaceholderText("Add event description or notes...")
            desc_layout.addWidget(desc_edit)
            layout.addLayout(desc_layout)
            
            # Buttons
            button_layout = QHBoxLayout()
            save_btn = QPushButton("Add Event")
            cancel_btn = QPushButton("Cancel")
            
            save_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            if dialog.exec() == QDialog.Accepted:
                name = name_edit.text().strip()
                event_type = type_combo.currentText()
                time = time_picker.get_time_string()
                description = desc_edit.toPlainText().strip()
                
                if not name:
                    QMessageBox.warning(self, "Validation Error", "Event name is required.")
                    return
                
                # Add to events list
                row_position = self.events_list.rowCount()
                self.events_list.insertRow(row_position)
                self.events_list.setItem(row_position, 0, QTableWidgetItem(date_str))
                self.events_list.setItem(row_position, 1, QTableWidgetItem(name))
                self.events_list.setItem(row_position, 2, QTableWidgetItem(event_type))
                
                # Save to database
                self._save_event_to_database(0, name, date_str, time, event_type, "Medium", description, "")
                
                # Refresh events list and calendar
                self.load_events()
                self.load_calendar()
                
                QMessageBox.information(self, "Success", f"Event '{name}' added successfully!")
                
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid date format.")
    
    def export_calendar(self):
        """Export calendar events to file"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Calendar", "calendar_export", 
            "CSV Files (*.csv);;PDF Files (*.pdf);;iCal Files (*.ics)"
        )
        
        if file_path:
            try:
                # Get calendar data from events list
                calendar_data = []
                
                for row in range(self.events_list.rowCount()):
                    if self.events_list.item(row, 0):  # Check if row has data
                        date = self.events_list.item(row, 0).text()
                        event = self.events_list.item(row, 1).text()
                        event_type = self.events_list.item(row, 2).text()
                        
                        calendar_data.append({
                            'date': date,
                            'event': event,
                            'type': event_type,
                            'time': '09:00',  # Default time
                            'description': event,
                            'priority': 'Medium'  # Default priority
                        })
                
                # Export based on file extension
                if file_path.endswith('.csv'):
                    self._export_to_csv(file_path, calendar_data)
                elif file_path.endswith('.pdf'):
                    self._export_to_pdf(file_path, calendar_data)
                elif file_path.endswith('.ics'):
                    self._export_to_ical(file_path, calendar_data)
                
                QMessageBox.information(self, "Export Successful", 
                                      f"Calendar exported to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", 
                                   f"Failed to export calendar: {str(e)}")
    
    def _export_to_csv(self, file_path: str, data: list):
        """Export calendar data to CSV"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'time', 'event', 'type', 'priority', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    
    def _export_to_pdf(self, file_path: str, data: list):
        """Export calendar data to PDF"""
        QMessageBox.information(self, "PDF Export", 
                              f"PDF export would create a formatted calendar at {file_path}")
    
    def _export_to_ical(self, file_path: str, data: list):
        """Export calendar data to iCal format"""
        QMessageBox.information(self, "iCal Export", 
                              f"iCal export would create a calendar file at {file_path}")
    
    def import_calendar(self):
        """Import calendar events from file"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Calendar", "", 
            "CSV Files (*.csv);;Excel Files (*.xlsx);;iCal Files (*.ics)"
        )
        
        if file_path:
            if file_path.endswith('.csv'):
                self.import_calendar_from_csv(file_path)
            elif file_path.endswith('.xlsx'):
                self.import_calendar_from_excel(file_path)
            elif file_path.endswith('.ics'):
                self.import_calendar_from_ical(file_path)
    
    def import_calendar_from_csv(self, file_path: str):
        """Import calendar events from CSV file"""
        try:
            import csv
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                imported_count = 0
                for row in reader:
                    # Extract event data
                    name = row.get('event', row.get('name', '')).strip()
                    date = row.get('date', '').strip()
                    time = row.get('time', '09:00').strip()
                    event_type = row.get('type', 'Other').strip()
                    priority = row.get('priority', 'Medium').strip()
                    description = row.get('description', '').strip()
                    
                    if name and date:
                        # Add to events list
                        row_position = self.events_list.rowCount()
                        self.events_list.insertRow(row_position)
                        self.events_list.setItem(row_position, 0, QTableWidgetItem(date))
                        self.events_list.setItem(row_position, 1, QTableWidgetItem(name))
                        self.events_list.setItem(row_position, 2, QTableWidgetItem(event_type))
                        
                        # Save to database
                        self._save_event_to_database(0, name, date, time, event_type, priority, description, "")
                        imported_count += 1
                
                QMessageBox.information(self, "Import Successful", 
                                      f"Successfully imported {imported_count} events from CSV file.")
                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", 
                               f"Failed to import CSV file: {str(e)}")
    
    def import_calendar_from_excel(self, file_path: str):
        """Import calendar events from Excel file"""
        QMessageBox.information(self, "Excel Import", 
                              f"Excel import would process {file_path}.\n\n"
                              "This feature would:\n"
                              "• Parse Excel format\n"
                              "• Extract calendar events\n"
                              "• Handle multiple sheets\n"
                              "• Import event details")
    
    def import_calendar_from_ical(self, file_path: str):
        """Import calendar events from iCal file"""
        QMessageBox.information(self, "iCal Import", 
                              f"iCal import would process {file_path}.\n\n"
                              "This feature would:\n"
                              "• Parse iCal format\n"
                              "• Extract calendar events\n"
                              "• Handle recurring events\n"
                              "• Import event details")
    
    def create_appointment_from_provider(self):
        """Create appointment with a care provider"""
        # Get all care providers
        providers = self.care_provider_service.get_providers()
        
        if not providers:
            QMessageBox.information(self, "No Providers", 
                                  "No care providers found. Please add providers in the Health Log panel first.")
            return
        
        # Create provider selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Appointment with Care Provider")
        dialog.setModal(True)
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Header
        header_label = QLabel("Select Care Provider for Appointment")
        header_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header_label)
        
        # Provider selection
        provider_group = QGroupBox("Select Provider")
        provider_layout = QVBoxLayout(provider_group)
        
        self.provider_table = QTableWidget()
        self.provider_table.setColumnCount(4)
        self.provider_table.setHorizontalHeaderLabels(["Name", "Specialty", "Organization", "Phone"])
        self.provider_table.horizontalHeader().setStretchLastSection(True)
        self.provider_table.setAlternatingRowColors(True)
        self.provider_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.provider_table.setMaximumHeight(200)
        
        # Apply custom delegate to suppress selection borders
        from utils.custom_delegates import CleanSelectionDelegate
        self.provider_table.setItemDelegate(CleanSelectionDelegate())
        
        # Populate provider table
        self.provider_table.setRowCount(len(providers))
        for row, provider in enumerate(providers):
            self.provider_table.setItem(row, 0, QTableWidgetItem(f"{provider.title} {provider.name}".strip()))
            self.provider_table.setItem(row, 1, QTableWidgetItem(provider.specialty))
            self.provider_table.setItem(row, 2, QTableWidgetItem(provider.organization))
            self.provider_table.setItem(row, 3, QTableWidgetItem(provider.phone or ""))
            # Store provider ID in user data
            self.provider_table.item(row, 0).setData(Qt.UserRole, provider.provider_id)
        
        provider_layout.addWidget(self.provider_table)
        layout.addWidget(provider_group)
        
        # Appointment details
        details_group = QGroupBox("Appointment Details")
        details_layout = QFormLayout(details_group)
        
        # Event name
        self.appointment_name_edit = QLineEdit()
        self.appointment_name_edit.setPlaceholderText("Auto-generated from provider selection")
        details_layout.addRow("Event Name:", self.appointment_name_edit)
        
        # Date
        self.appointment_date_edit = QLineEdit()
        self.appointment_date_edit.setPlaceholderText("YYYY-MM-DD")
        details_layout.addRow("Date:", self.appointment_date_edit)
        
        # Time
        from utils.time_picker_widget import TimePickerWidget
        self.appointment_time_picker = TimePickerWidget()
        details_layout.addRow("Time:", self.appointment_time_picker)
        
        # Event type
        self.appointment_type_combo = QComboBox()
        self.appointment_type_combo.addItems([
            "Medical Appointment",
            "Doctor Visit", 
            "Lab Test",
            "Follow-up Visit",
            "Consultation",
            "Emergency Visit"
        ])
        details_layout.addRow("Event Type:", self.appointment_type_combo)
        
        # Priority
        self.appointment_priority_combo = QComboBox()
        self.appointment_priority_combo.addItems(["Low", "Medium", "High", "Urgent"])
        details_layout.addRow("Priority:", self.appointment_priority_combo)
        
        # Description
        self.appointment_desc_edit = QTextEdit()
        self.appointment_desc_edit.setMaximumHeight(80)
        self.appointment_desc_edit.setPlaceholderText("Appointment notes, preparation instructions, etc.")
        details_layout.addRow("Description:", self.appointment_desc_edit)
        
        layout.addWidget(details_group)
        
        # Connect provider selection to auto-fill appointment name
        self.provider_table.itemSelectionChanged.connect(self.update_appointment_name)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.Accepted:
            selected_row = self.provider_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "No Selection", "Please select a care provider.")
                return
            
            provider_id = self.provider_table.item(selected_row, 0).data(Qt.UserRole)
            provider = self.care_provider_service.get_provider(provider_id)
            
            if not provider:
                QMessageBox.warning(self, "Error", "Selected provider not found.")
                return
            
            # Get appointment details
            name = self.appointment_name_edit.text().strip()
            date = self.appointment_date_edit.text().strip()
            time = self.appointment_time_picker.get_time_string()
            event_type = self.appointment_type_combo.currentText()
            priority = self.appointment_priority_combo.currentText()
            description = self.appointment_desc_edit.toPlainText().strip()
            
            # Validation
            if not date:
                QMessageBox.warning(self, "Validation Error", "Appointment date is required.")
                return
            
            if not time:
                QMessageBox.warning(self, "Validation Error", "Appointment time is required.")
                return
            
            # Create appointment data
            appointment_data = {
                'title': name or f"Appointment with {provider.title} {provider.name}",
                'date': date,
                'time': time,
                'event_type': event_type,
                'priority': priority,
                'description': description,
                'provider_name': f"{provider.title} {provider.name}".strip(),
                'provider_specialty': provider.specialty,
                'provider_organization': provider.organization,
                'provider_phone': provider.phone,
                'provider_email': provider.email
            }
            
            # Add to events list
            row_position = self.events_list.rowCount()
            self.events_list.insertRow(row_position)
            self.events_list.setItem(row_position, 0, QTableWidgetItem(date))
            self.events_list.setItem(row_position, 1, QTableWidgetItem(appointment_data['title']))
            self.events_list.setItem(row_position, 2, QTableWidgetItem(event_type))
            
            # Save to database
            self._save_event_to_database(0, appointment_data['title'], date, time, 
                                       event_type, priority, description, "")
            
            # Refresh events list and calendar
            self.load_events()
            self.load_calendar()  # Refresh calendar to show new appointment
            
            QMessageBox.information(self, "Success", 
                                  f"Appointment with {provider.name} created successfully!")
    
    def update_appointment_name(self):
        """Update appointment name based on selected provider"""
        selected_row = self.provider_table.currentRow()
        if selected_row >= 0:
            provider_id = self.provider_table.item(selected_row, 0).data(Qt.UserRole)
            provider = self.care_provider_service.get_provider(provider_id)
            
            if provider:
                provider_name = f"{provider.title} {provider.name}".strip()
                event_type = self.appointment_type_combo.currentText()
                appointment_name = f"{event_type} with {provider_name}"
                self.appointment_name_edit.setText(appointment_name)
    
    def on_appointment_created(self, appointment_data):
        """Handle appointment created signal from care provider service"""
        # This method is called when an appointment is created from the Health Log panel
        # We can refresh the calendar or show a notification
        QMessageBox.information(self, "Appointment Created", 
                              f"Appointment '{appointment_data.get('title', '')}' created successfully!")
        self.load_events()  # Refresh the events list
    
    def refresh(self):
        """Refresh panel data"""
        self.load_calendar()
        self.load_events()
