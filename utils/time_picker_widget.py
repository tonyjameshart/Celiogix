from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel
from PySide6.QtCore import Signal
from typing import Optional
from datetime import time


class TimePickerWidget(QWidget):
    """Widget for selecting time with hour and minute dropdowns"""
    
    time_changed = Signal(time)
    
    def __init__(self, parent=None, initial_time: Optional[time] = None):
        super().__init__(parent)
        self.selected_time = initial_time or time(9, 0)  # Default to 9:00 AM
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """Set up the time picker UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)  # Reduced spacing for tighter layout
        
        # Hour dropdown
        self.hour_combo = QComboBox()
        for hour in range(24):
            display_hour = hour if hour > 0 else 12  # Convert 0 to 12
            am_pm = "AM" if hour < 12 else "PM"
            self.hour_combo.addItem(f"{display_hour:02d} {am_pm}", hour)
        self.hour_combo.currentIndexChanged.connect(self.on_time_changed)
        layout.addWidget(self.hour_combo)
        
        # Colon separator
        colon_label = QLabel(":")
        colon_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        colon_label.setFixedWidth(10)  # Fixed width to control spacing
        layout.addWidget(colon_label)
        
        # Minute dropdown
        self.minute_combo = QComboBox()
        for minute in range(0, 60, 15):  # 15-minute intervals
            self.minute_combo.addItem(f"{minute:02d}", minute)
        self.minute_combo.currentIndexChanged.connect(self.on_time_changed)
        layout.addWidget(self.minute_combo)
    
    def on_time_changed(self):
        """Handle time selection changes"""
        hour = self.hour_combo.currentData()
        minute = self.minute_combo.currentData()
        self.selected_time = time(hour, minute)
        self.time_changed.emit(self.selected_time)
    
    def set_time(self, new_time: time):
        """Set the selected time"""
        self.selected_time = new_time
        
        # Update hour combo
        display_hour = new_time.hour if new_time.hour > 0 else 12
        am_pm = "AM" if new_time.hour < 12 else "PM"
        hour_text = f"{display_hour:02d} {am_pm}"
        
        for i in range(self.hour_combo.count()):
            if self.hour_combo.itemText(i) == hour_text:
                self.hour_combo.setCurrentIndex(i)
                break
        
        # Update minute combo
        minute = new_time.minute
        # Find closest 15-minute interval
        closest_minute = round(minute / 15) * 15
        if closest_minute >= 60:
            closest_minute = 0
        
        for i in range(self.minute_combo.count()):
            if self.minute_combo.itemData(i) == closest_minute:
                self.minute_combo.setCurrentIndex(i)
                break
    
    def get_time(self) -> time:
        """Get the selected time"""
        return self.selected_time
    
    def get_time_string(self) -> str:
        """Get the selected time as a string in HH:MM format"""
        return self.selected_time.strftime("%H:%M")
    
    def update_display(self):
        """Update the display to show current time"""
        self.set_time(self.selected_time)
