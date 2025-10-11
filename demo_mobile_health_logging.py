#!/usr/bin/env python3
"""
Demo script for Mobile Health Logging Features
Showcases the enhanced symptom tracking with templates, emergency alerts, and pattern analysis
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.mobile_sync import MobileSyncService, SymptomLogData, HealthTemplateData, HealthReminderData
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit, QMessageBox, QTabWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class MobileHealthLoggingDemo(QMainWindow):
    """Demo window for mobile health logging features"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏥 Mobile Health Logging Demo")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize mobile sync service
        self.mobile_sync = MobileSyncService()
        
        self.setup_ui()
        self.load_demo_data()
    
    def setup_ui(self):
        """Set up the demo UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("🏥 Enhanced Mobile Health Logging Demo")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Health Templates Tab
        self.setup_templates_tab()
        
        # Symptom Logging Tab
        self.setup_symptom_logging_tab()
        
        # Pattern Analysis Tab
        self.setup_pattern_analysis_tab()
        
        # Health Reminders Tab
        self.setup_reminders_tab()
        
        # Demo Actions
        self.setup_demo_actions(layout)
    
    def setup_templates_tab(self):
        """Set up health templates tab"""
        templates_widget = QWidget()
        layout = QVBoxLayout(templates_widget)
        
        # Header
        header = QLabel("⚡ Health Templates for Quick Entry")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Template buttons
        template_layout = QVBoxLayout()
        
        mild_btn = QPushButton("😐 Mild Symptoms Template")
        mild_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        mild_btn.clicked.connect(lambda: self.demo_template_usage("mild_symptoms"))
        
        moderate_btn = QPushButton("😟 Moderate Symptoms Template")
        moderate_btn.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        moderate_btn.clicked.connect(lambda: self.demo_template_usage("moderate_symptoms"))
        
        severe_btn = QPushButton("😰 Severe Symptoms Template")
        severe_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        severe_btn.clicked.connect(lambda: self.demo_template_usage("severe_symptoms"))
        
        gluten_btn = QPushButton("🌾 Gluten Reaction Template")
        gluten_btn.setStyleSheet("background-color: #8e44ad; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        gluten_btn.clicked.connect(lambda: self.demo_template_usage("gluten_reaction"))
        
        template_layout.addWidget(mild_btn)
        template_layout.addWidget(moderate_btn)
        template_layout.addWidget(severe_btn)
        template_layout.addWidget(gluten_btn)
        
        layout.addLayout(template_layout)
        
        # Template info
        info_text = QTextEdit()
        info_text.setMaximumHeight(200)
        info_text.setReadOnly(True)
        info_text.setPlainText("""
Health Templates provide quick entry for common symptom scenarios:

• Mild Symptoms: Fatigue, mild discomfort, slight headache (Severity: 1-3)
• Moderate Symptoms: Stomach pain, nausea, headache, joint pain (Severity: 4-6)
• Severe Symptoms: Severe pain, vomiting, diarrhea, dizziness (Severity: 7-9)
• Gluten Reaction: Severe reaction symptoms with suspected gluten exposure (Severity: 6-10)

Templates pre-fill common symptoms and severity ranges, making logging faster and more consistent.
        """.strip())
        layout.addWidget(info_text)
        
        self.tab_widget.addTab(templates_widget, "⚡ Templates")
    
    def setup_symptom_logging_tab(self):
        """Set up symptom logging tab"""
        logging_widget = QWidget()
        layout = QVBoxLayout(logging_widget)
        
        # Header
        header = QLabel("📝 Enhanced Symptom Logging")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Demo buttons
        demo_layout = QVBoxLayout()
        
        custom_btn = QPushButton("📝 Log Custom Symptoms")
        custom_btn.setStyleSheet("background-color: #3498db; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        custom_btn.clicked.connect(self.demo_custom_symptom_logging)
        
        emergency_btn = QPushButton("🚨 Log Emergency Symptoms")
        emergency_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        emergency_btn.clicked.connect(self.demo_emergency_logging)
        
        media_btn = QPushButton("📸 Log with Media Attachments")
        media_btn.setStyleSheet("background-color: #9b59b6; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        media_btn.clicked.connect(self.demo_media_logging)
        
        demo_layout.addWidget(custom_btn)
        demo_layout.addWidget(emergency_btn)
        demo_layout.addWidget(media_btn)
        
        layout.addLayout(demo_layout)
        
        # Recent logs display
        self.recent_logs_text = QTextEdit()
        self.recent_logs_text.setMaximumHeight(200)
        self.recent_logs_text.setReadOnly(True)
        layout.addWidget(self.recent_logs_text)
        
        # Update display
        self.update_recent_logs()
        
        self.tab_widget.addTab(logging_widget, "📝 Logging")
    
    def setup_pattern_analysis_tab(self):
        """Set up pattern analysis tab"""
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)
        
        # Header
        header = QLabel("📊 Symptom Pattern Analysis")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Analysis buttons
        analysis_layout = QVBoxLayout()
        
        analyze_btn = QPushButton("🔍 Analyze Patterns")
        analyze_btn.setStyleSheet("background-color: #16a085; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        analyze_btn.clicked.connect(self.demo_pattern_analysis)
        
        triggers_btn = QPushButton("🎯 Identify Triggers")
        triggers_btn.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        triggers_btn.clicked.connect(self.demo_trigger_analysis)
        
        trends_btn = QPushButton("📈 Show Trends")
        trends_btn.setStyleSheet("background-color: #3498db; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        trends_btn.clicked.connect(self.demo_trend_analysis)
        
        analysis_layout.addWidget(analyze_btn)
        analysis_layout.addWidget(triggers_btn)
        analysis_layout.addWidget(trends_btn)
        
        layout.addLayout(analysis_layout)
        
        # Analysis results
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        layout.addWidget(self.analysis_text)
        
        self.tab_widget.addTab(analysis_widget, "📊 Analysis")
    
    def setup_reminders_tab(self):
        """Set up health reminders tab"""
        reminders_widget = QWidget()
        layout = QVBoxLayout(reminders_widget)
        
        # Header
        header = QLabel("⏰ Smart Health Reminders")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(header)
        
        # Reminder demo buttons
        reminder_layout = QVBoxLayout()
        
        meal_reminder_btn = QPushButton("🍽️ Add Meal Check Reminder")
        meal_reminder_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        meal_reminder_btn.clicked.connect(self.demo_meal_reminder)
        
        symptom_reminder_btn = QPushButton("🏥 Add Symptom Check Reminder")
        symptom_reminder_btn.setStyleSheet("background-color: #e67e22; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        symptom_reminder_btn.clicked.connect(self.demo_symptom_reminder)
        
        medication_reminder_btn = QPushButton("💊 Add Medication Reminder")
        medication_reminder_btn.setStyleSheet("background-color: #8e44ad; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        medication_reminder_btn.clicked.connect(self.demo_medication_reminder)
        
        reminder_layout.addWidget(meal_reminder_btn)
        reminder_layout.addWidget(symptom_reminder_btn)
        reminder_layout.addWidget(medication_reminder_btn)
        
        layout.addLayout(reminder_layout)
        
        # Active reminders display
        self.reminders_text = QTextEdit()
        self.reminders_text.setMaximumHeight(200)
        self.reminders_text.setReadOnly(True)
        layout.addWidget(self.reminders_text)
        
        # Update display
        self.update_reminders_display()
        
        self.tab_widget.addTab(reminders_widget, "⏰ Reminders")
    
    def setup_demo_actions(self, layout):
        """Set up demo action buttons"""
        actions_layout = QVBoxLayout()
        
        # Clear data button
        clear_btn = QPushButton("🗑️ Clear All Demo Data")
        clear_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        clear_btn.clicked.connect(self.clear_demo_data)
        
        # Export data button
        export_btn = QPushButton("📤 Export Health Data")
        export_btn.setStyleSheet("background-color: #16a085; color: white; padding: 10px; border-radius: 5px; font-size: 12px;")
        export_btn.clicked.connect(self.export_health_data)
        
        actions_layout.addWidget(clear_btn)
        actions_layout.addWidget(export_btn)
        
        layout.addLayout(actions_layout)
    
    def load_demo_data(self):
        """Load demo health data"""
        # Add some demo symptom logs
        demo_logs = [
            {
                'timestamp': datetime.now() - timedelta(hours=2),
                'symptoms': ['Fatigue', 'Mild stomach discomfort'],
                'severity': 3,
                'location': 'Home',
                'notes': 'Feeling tired after lunch',
                'emergency_level': 'normal',
                'mood': 'fair',
                'energy_level': 6,
                'meal_context': 'Had a salad for lunch',
                'triggers_suspected': [],
                'gluten_exposure_suspected': False
            },
            {
                'timestamp': datetime.now() - timedelta(hours=6),
                'symptoms': ['Stomach pain', 'Nausea', 'Headache'],
                'severity': 6,
                'location': 'Restaurant',
                'notes': 'Started feeling sick after dinner',
                'emergency_level': 'concerning',
                'mood': 'poor',
                'energy_level': 4,
                'meal_context': 'Dinner at Italian restaurant',
                'triggers_suspected': ['Possible gluten exposure'],
                'gluten_exposure_suspected': True
            },
            {
                'timestamp': datetime.now() - timedelta(days=1),
                'symptoms': ['Severe stomach pain', 'Vomiting', 'Diarrhea'],
                'severity': 8,
                'location': 'Home',
                'notes': 'Severe reaction, very concerning',
                'emergency_level': 'urgent',
                'mood': 'terrible',
                'energy_level': 2,
                'meal_context': 'Breakfast with toast',
                'triggers_suspected': ['Gluten exposure', 'Cross-contamination'],
                'gluten_exposure_suspected': True,
                'voice_note_path': '/demo/voice_note_1.wav',
                'photo_paths': ['/demo/symptom_photo_1.jpg']
            }
        ]
        
        for log_data in demo_logs:
            self.mobile_sync.add_symptom_log_with_media(log_data)
        
        # Add some demo health templates
        demo_templates = [
            HealthTemplateData(
                template_id="mild_symptoms",
                template_name="Mild Symptoms",
                symptoms=["Fatigue", "Mild stomach discomfort", "Slight headache"],
                severity_range=(1, 3),
                emergency_level="normal",
                description="Common mild symptoms"
            ),
            HealthTemplateData(
                template_id="gluten_reaction",
                template_name="Gluten Reaction",
                symptoms=["Severe stomach pain", "Nausea", "Vomiting", "Diarrhea"],
                severity_range=(6, 10),
                emergency_level="urgent",
                description="Suspected gluten exposure reaction",
                common_triggers=["Gluten exposure", "Cross-contamination"]
            )
        ]
        
        for template in demo_templates:
            self.mobile_sync.add_health_template(template)
        
        # Add some demo health reminders
        demo_reminders = [
            HealthReminderData(
                reminder_id="meal_check_1",
                reminder_type="meal_log",
                trigger_event="meal_completed",
                delay_minutes=30,
                message="How are you feeling after your meal? Log any symptoms.",
                enabled=True
            ),
            HealthReminderData(
                reminder_id="symptom_check_1",
                reminder_type="symptom_check",
                trigger_event="time_based",
                delay_minutes=120,
                message="Time for your regular symptom check-in.",
                enabled=True
            )
        ]
        
        for reminder in demo_reminders:
            self.mobile_sync.add_health_reminder(reminder)
    
    def demo_template_usage(self, template_type: str):
        """Demo health template usage"""
        templates = {
            "mild_symptoms": {
                "name": "Mild Symptoms",
                "symptoms": ["Fatigue", "Mild stomach discomfort", "Slight headache"],
                "severity": 3,
                "emergency_level": "normal"
            },
            "moderate_symptoms": {
                "name": "Moderate Symptoms",
                "symptoms": ["Stomach pain", "Nausea", "Headache", "Joint pain"],
                "severity": 5,
                "emergency_level": "concerning"
            },
            "severe_symptoms": {
                "name": "Severe Symptoms",
                "symptoms": ["Severe stomach pain", "Vomiting", "Diarrhea", "Dizziness"],
                "severity": 8,
                "emergency_level": "urgent"
            },
            "gluten_reaction": {
                "name": "Gluten Reaction",
                "symptoms": ["Severe stomach pain", "Nausea", "Vomiting", "Diarrhea", "Brain fog"],
                "severity": 7,
                "emergency_level": "urgent"
            }
        }
        
        template = templates.get(template_type, {})
        if template:
            # Create symptom log using template
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'symptoms': template['symptoms'],
                'severity': template['severity'],
                'emergency_level': template['emergency_level'],
                'location': 'Demo Location',
                'notes': f'Demo log using {template["name"]} template',
                'mood': 'fair',
                'energy_level': 5,
                'meal_context': 'Demo meal context',
                'triggers_suspected': ['Demo trigger'],
                'gluten_exposure_suspected': template_type == 'gluten_reaction'
            }
            
            success = self.mobile_sync.add_symptom_log_with_media(log_data)
            
            if success:
                QMessageBox.information(self, "Template Used", 
                                      f"Successfully logged symptoms using {template['name']} template!")
                self.update_recent_logs()
            else:
                QMessageBox.warning(self, "Error", "Failed to log symptoms.")
    
    def demo_custom_symptom_logging(self):
        """Demo custom symptom logging"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'symptoms': ['Custom symptom 1', 'Custom symptom 2'],
            'severity': 4,
            'emergency_level': 'concerning',
            'location': 'Custom Location',
            'notes': 'This is a custom symptom log entry',
            'mood': 'poor',
            'energy_level': 6,
            'meal_context': 'Custom meal context',
            'triggers_suspected': ['Custom trigger'],
            'gluten_exposure_suspected': False
        }
        
        success = self.mobile_sync.add_symptom_log_with_media(log_data)
        
        if success:
            QMessageBox.information(self, "Custom Log Added", "Successfully logged custom symptoms!")
            self.update_recent_logs()
        else:
            QMessageBox.warning(self, "Error", "Failed to log custom symptoms.")
    
    def demo_emergency_logging(self):
        """Demo emergency symptom logging"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'symptoms': ['Severe abdominal pain', 'Difficulty breathing', 'Chest pain'],
            'severity': 9,
            'emergency_level': 'emergency',
            'location': 'Emergency Location',
            'notes': 'EMERGENCY: Severe symptoms requiring immediate attention',
            'mood': 'terrible',
            'energy_level': 1,
            'meal_context': 'Recent meal may have contained gluten',
            'triggers_suspected': ['Severe gluten exposure'],
            'gluten_exposure_suspected': True
        }
        
        success = self.mobile_sync.add_symptom_log_with_media(log_data)
        
        if success:
            QMessageBox.information(self, "Emergency Log Added", 
                                  "Emergency symptom log added! Alert triggered.")
            self.update_recent_logs()
        else:
            QMessageBox.warning(self, "Error", "Failed to log emergency symptoms.")
    
    def demo_media_logging(self):
        """Demo media attachment logging"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'symptoms': ['Rash', 'Swelling', 'Itching'],
            'severity': 6,
            'emergency_level': 'urgent',
            'location': 'Home',
            'notes': 'Allergic reaction with visible symptoms',
            'mood': 'poor',
            'energy_level': 4,
            'meal_context': 'Ate something new',
            'triggers_suspected': ['Food allergy'],
            'gluten_exposure_suspected': False,
            'voice_note_path': '/demo/voice_note_reaction.wav',
            'photo_paths': ['/demo/rash_photo_1.jpg', '/demo/swelling_photo_2.jpg']
        }
        
        success = self.mobile_sync.add_symptom_log_with_media(log_data)
        
        if success:
            QMessageBox.information(self, "Media Log Added", 
                                  "Symptom log with media attachments added!")
            self.update_recent_logs()
        else:
            QMessageBox.warning(self, "Error", "Failed to log symptoms with media.")
    
    def demo_pattern_analysis(self):
        """Demo pattern analysis"""
        logs = self.mobile_sync.symptom_logs
        
        if not logs:
            self.analysis_text.setPlainText("No symptom data available for analysis.")
            return
        
        # Basic pattern analysis
        analysis = f"""📊 Symptom Pattern Analysis Report
        
Total Logs Analyzed: {len(logs)}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🔍 Key Findings:
"""
        
        # Symptom frequency
        symptom_counts = {}
        for log in logs:
            for symptom in log.symptoms:
                symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
        
        most_common = sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        analysis += "\nMost Frequent Symptoms:\n"
        for symptom, count in most_common:
            analysis += f"• {symptom}: {count} occurrences ({count/len(logs)*100:.1f}%)\n"
        
        # Severity patterns
        avg_severity = sum(log.severity for log in logs) / len(logs)
        analysis += f"\nAverage Severity: {avg_severity:.1f}/10\n"
        
        # Emergency patterns
        emergency_logs = [log for log in logs if getattr(log, 'emergency_level', 'normal') in ['urgent', 'emergency']]
        if emergency_logs:
            analysis += f"\n🚨 Emergency Events: {len(emergency_logs)} ({len(emergency_logs)/len(logs)*100:.1f}%)\n"
        
        # Time patterns
        today_logs = [log for log in logs if log.timestamp.date() == datetime.now().date()]
        analysis += f"\n📅 Today's Logs: {len(today_logs)}\n"
        
        # Trigger patterns
        trigger_logs = [log for log in logs if hasattr(log, 'triggers_suspected') and log.triggers_suspected]
        if trigger_logs:
            analysis += f"\n🔍 Triggered Events: {len(trigger_logs)} ({len(trigger_logs)/len(logs)*100:.1f}%)\n"
        
        self.analysis_text.setPlainText(analysis)
    
    def demo_trigger_analysis(self):
        """Demo trigger analysis"""
        logs = self.mobile_sync.symptom_logs
        
        if not logs:
            self.analysis_text.setPlainText("No symptom data available for trigger analysis.")
            return
        
        # Trigger analysis
        trigger_counts = {}
        gluten_exposure_count = 0
        
        for log in logs:
            if hasattr(log, 'triggers_suspected') and log.triggers_suspected:
                for trigger in log.triggers_suspected:
                    trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
            
            if hasattr(log, 'gluten_exposure_suspected') and log.gluten_exposure_suspected:
                gluten_exposure_count += 1
        
        analysis = f"""🎯 Trigger Analysis Report
        
Total Logs: {len(logs)}
Gluten Exposure Suspected: {gluten_exposure_count} ({gluten_exposure_count/len(logs)*100:.1f}%)

🔍 Suspected Triggers:
"""
        
        if trigger_counts:
            sorted_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)
            for trigger, count in sorted_triggers:
                analysis += f"• {trigger}: {count} occurrences\n"
        else:
            analysis += "No specific triggers identified in recent logs.\n"
        
        # Recommendations
        analysis += f"""
💡 Recommendations:
• Monitor for patterns after gluten exposure: {gluten_exposure_count} suspected cases
• Track meal contexts for potential food triggers
• Consider elimination diet for frequent triggers
• Consult healthcare provider for persistent patterns
"""
        
        self.analysis_text.setPlainText(analysis)
    
    def demo_trend_analysis(self):
        """Demo trend analysis"""
        logs = self.mobile_sync.symptom_logs
        
        if not logs:
            self.analysis_text.setPlainText("No symptom data available for trend analysis.")
            return
        
        # Sort logs by timestamp
        sorted_logs = sorted(logs, key=lambda x: x.timestamp)
        
        # Calculate trends
        recent_logs = sorted_logs[-7:]  # Last 7 logs
        older_logs = sorted_logs[:-7] if len(sorted_logs) > 7 else []
        
        recent_avg_severity = sum(log.severity for log in recent_logs) / len(recent_logs) if recent_logs else 0
        older_avg_severity = sum(log.severity for log in older_logs) / len(older_logs) if older_logs else 0
        
        severity_trend = "improving" if recent_avg_severity < older_avg_severity else "worsening" if recent_avg_severity > older_avg_severity else "stable"
        
        analysis = f"""📈 Trend Analysis Report
        
Analysis Period: Last {len(recent_logs)} logs vs. previous {len(older_logs)} logs

📊 Severity Trends:
• Recent Average: {recent_avg_severity:.1f}/10
• Previous Average: {older_avg_severity:.1f}/10
• Trend: {severity_trend.title()}

🕒 Time Distribution:
• Today: {len([log for log in logs if log.timestamp.date() == datetime.now().date()])} logs
• This Week: {len([log for log in logs if log.timestamp >= datetime.now() - timedelta(days=7)])} logs
• This Month: {len([log for log in logs if log.timestamp >= datetime.now() - timedelta(days=30)])} logs

📅 Daily Patterns:
"""
        
        # Daily pattern analysis
        daily_counts = {}
        for log in logs:
            day = log.timestamp.strftime('%A')
            daily_counts[day] = daily_counts.get(day, 0) + 1
        
        if daily_counts:
            for day, count in sorted(daily_counts.items(), key=lambda x: x[1], reverse=True):
                analysis += f"• {day}: {count} logs\n"
        
        # Recommendations
        analysis += f"""
💡 Trend-Based Recommendations:
• Overall trend is {severity_trend}
• {'Continue current management approach' if severity_trend == 'improving' else 'Consider reviewing triggers and treatment' if severity_trend == 'worsening' else 'Monitor for any changes'}
• Track patterns on high-activity days
• Consider preventive measures during peak times
"""
        
        self.analysis_text.setPlainText(analysis)
    
    def demo_meal_reminder(self):
        """Demo meal check reminder"""
        reminder = HealthReminderData(
            reminder_id=f"meal_check_{datetime.now().timestamp()}",
            reminder_type="meal_log",
            trigger_event="meal_completed",
            delay_minutes=30,
            message="How are you feeling after your meal? Log any symptoms or reactions.",
            enabled=True
        )
        
        self.mobile_sync.add_health_reminder(reminder)
        QMessageBox.information(self, "Reminder Added", "Meal check reminder added!")
        self.update_reminders_display()
    
    def demo_symptom_reminder(self):
        """Demo symptom check reminder"""
        reminder = HealthReminderData(
            reminder_id=f"symptom_check_{datetime.now().timestamp()}",
            reminder_type="symptom_check",
            trigger_event="time_based",
            delay_minutes=120,
            message="Time for your regular symptom check-in. How are you feeling?",
            enabled=True
        )
        
        self.mobile_sync.add_health_reminder(reminder)
        QMessageBox.information(self, "Reminder Added", "Symptom check reminder added!")
        self.update_reminders_display()
    
    def demo_medication_reminder(self):
        """Demo medication reminder"""
        reminder = HealthReminderData(
            reminder_id=f"medication_{datetime.now().timestamp()}",
            reminder_type="medication",
            trigger_event="time_based",
            delay_minutes=480,  # 8 hours
            message="Time to take your medication. Don't forget to log any side effects.",
            enabled=True
        )
        
        self.mobile_sync.add_health_reminder(reminder)
        QMessageBox.information(self, "Reminder Added", "Medication reminder added!")
        self.update_reminders_display()
    
    def update_recent_logs(self):
        """Update recent logs display"""
        logs = self.mobile_sync.symptom_logs[-5:]  # Show last 5 logs
        
        if not logs:
            self.recent_logs_text.setPlainText("No recent symptom logs.")
            return
        
        display_text = "📝 Recent Symptom Logs:\n\n"
        
        for log in reversed(logs):  # Show newest first
            emergency_icon = "🚨" if getattr(log, 'emergency_level', 'normal') in ['urgent', 'emergency'] else "✅"
            media_icon = "📸" if hasattr(log, 'photo_paths') and log.photo_paths else "🎤" if hasattr(log, 'voice_note_path') and log.voice_note_path else ""
            
            display_text += f"{emergency_icon} {log.timestamp.strftime('%m/%d %H:%M')} - {', '.join(log.symptoms[:2])}{'...' if len(log.symptoms) > 2 else ''} (Severity: {log.severity}/10){media_icon}\n"
        
        self.recent_logs_text.setPlainText(display_text.strip())
    
    def update_reminders_display(self):
        """Update reminders display"""
        reminders = self.mobile_sync.health_reminders
        
        if not reminders:
            self.reminders_text.setPlainText("No active health reminders.")
            return
        
        display_text = "⏰ Active Health Reminders:\n\n"
        
        for reminder in reminders:
            status = "✅ Enabled" if reminder.enabled else "❌ Disabled"
            display_text += f"• {reminder.reminder_type.title()} - {reminder.message[:50]}...\n  Trigger: {reminder.trigger_event} ({reminder.delay_minutes} min delay) - {status}\n\n"
        
        self.reminders_text.setPlainText(display_text.strip())
    
    def clear_demo_data(self):
        """Clear all demo data"""
        reply = QMessageBox.question(self, "Clear Demo Data", 
                                   "Are you sure you want to clear all demo health data?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.mobile_sync.symptom_logs.clear()
            self.mobile_sync.health_templates.clear()
            self.mobile_sync.health_reminders.clear()
            
            self.update_recent_logs()
            self.update_reminders_display()
            self.analysis_text.clear()
            
            QMessageBox.information(self, "Data Cleared", "All demo health data has been cleared.")
    
    def export_health_data(self):
        """Export health data to JSON"""
        try:
            export_data = {
                'symptom_logs': [
                    {
                        'timestamp': log.timestamp.isoformat(),
                        'symptoms': log.symptoms,
                        'severity': log.severity,
                        'emergency_level': getattr(log, 'emergency_level', 'normal'),
                        'location': log.location,
                        'notes': log.notes,
                        'mood': getattr(log, 'mood', None),
                        'energy_level': getattr(log, 'energy_level', None),
                        'meal_context': getattr(log, 'meal_context', None),
                        'triggers_suspected': getattr(log, 'triggers_suspected', []),
                        'gluten_exposure_suspected': getattr(log, 'gluten_exposure_suspected', False),
                        'voice_note_path': getattr(log, 'voice_note_path', None),
                        'photo_paths': getattr(log, 'photo_paths', [])
                    }
                    for log in self.mobile_sync.symptom_logs
                ],
                'health_templates': [
                    {
                        'template_id': template.template_id,
                        'template_name': template.template_name,
                        'symptoms': template.symptoms,
                        'severity_range': template.severity_range,
                        'emergency_level': template.emergency_level,
                        'description': template.description
                    }
                    for template in self.mobile_sync.health_templates
                ],
                'health_reminders': [
                    {
                        'reminder_id': reminder.reminder_id,
                        'reminder_type': reminder.reminder_type,
                        'trigger_event': reminder.trigger_event,
                        'delay_minutes': reminder.delay_minutes,
                        'message': reminder.message,
                        'enabled': reminder.enabled
                    }
                    for reminder in self.mobile_sync.health_reminders
                ],
                'export_timestamp': datetime.now().isoformat(),
                'total_logs': len(self.mobile_sync.symptom_logs),
                'total_templates': len(self.mobile_sync.health_templates),
                'total_reminders': len(self.mobile_sync.health_reminders)
            }
            
            # Save to file
            filename = f"mobile_health_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import json
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            QMessageBox.information(self, "Export Successful", 
                                  f"Health data exported to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Mobile Health Logging Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("CeliacShield")
    
    # Create and show demo window
    demo = MobileHealthLoggingDemo()
    demo.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
