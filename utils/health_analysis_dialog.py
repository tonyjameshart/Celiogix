# path: utils/health_analysis_dialog.py
"""
Health Analysis Dialog for displaying pattern analysis results
"""

from typing import Dict, List, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton,
    QScrollArea, QWidget, QGroupBox, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import io
import base64


class HealthAnalysisWorker(QThread):
    """Worker thread for health analysis"""
    analysis_complete = Signal(dict)
    progress_update = Signal(str, int)
    
    def __init__(self, db_path: str, days_back: int = 90):
        super().__init__()
        self.db_path = db_path
        self.days_back = days_back
    
    def run(self):
        try:
            from services.health_pattern_analyzer import HealthPatternAnalyzer
            
            self.progress_update.emit("Initializing analyzer...", 10)
            analyzer = HealthPatternAnalyzer(self.db_path)
            
            self.progress_update.emit("Fetching health data...", 30)
            entries = analyzer.get_health_entries(self.days_back)
            
            self.progress_update.emit("Analyzing symptom patterns...", 50)
            insights = analyzer.generate_health_insights(entries)
            
            self.progress_update.emit("Analysis complete!", 100)
            self.analysis_complete.emit(insights)
            
        except Exception as e:
            self.analysis_complete.emit({'error': str(e)})


class HealthAnalysisDialog(QDialog):
    """Dialog for displaying comprehensive health analysis"""
    
    def __init__(self, parent=None, db_path: str = "data/celiogix.db"):
        super().__init__(parent)
        self.db_path = db_path
        self.insights = None
        self.setWindowTitle("Health Pattern Analysis")
        self.setModal(True)
        self.resize(900, 700)
        
        self.setup_ui()
        self.start_analysis()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Progress bar for analysis
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(True)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Starting analysis...")
        layout.addWidget(self.progress_label)
        
        # Main content (hidden until analysis complete)
        self.content_widget = QWidget()
        self.content_widget.setVisible(False)
        layout.addWidget(self.content_widget)
        
        content_layout = QVBoxLayout(self.content_widget)
        
        # Tab widget for different analysis sections
        self.tab_widget = QTabWidget()
        content_layout.addWidget(self.tab_widget)
        
        # Summary tab
        self.summary_tab = self.create_summary_tab()
        self.tab_widget.addTab(self.summary_tab, "Summary")
        
        # Symptom patterns tab
        self.symptoms_tab = self.create_symptoms_tab()
        self.tab_widget.addTab(self.symptoms_tab, "Symptom Patterns")
        
        # Gluten exposure tab
        self.exposure_tab = self.create_exposure_tab()
        self.tab_widget.addTab(self.exposure_tab, "Gluten Exposure")
        
        # Nutritional impact tab
        self.nutrition_tab = self.create_nutrition_tab()
        self.tab_widget.addTab(self.nutrition_tab, "Nutritional Impact")
        
        # Health trends tab
        self.trends_tab = self.create_trends_tab()
        self.tab_widget.addTab(self.trends_tab, "Health Trends")
        
        # Recommendations tab
        self.recommendations_tab = self.create_recommendations_tab()
        self.tab_widget.addTab(self.recommendations_tab, "Recommendations")
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        content_layout.addWidget(close_btn)
    
    def create_summary_tab(self):
        """Create summary tab"""
        tab = QScrollArea()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.summary_content = QTextEdit()
        self.summary_content.setReadOnly(True)
        layout.addWidget(self.summary_content)
        
        tab.setWidget(widget)
        return tab
    
    def create_symptoms_tab(self):
        """Create symptom patterns tab"""
        tab = QScrollArea()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Symptom patterns table
        self.symptoms_table = QTableWidget()
        self.symptoms_table.setColumnCount(6)
        self.symptoms_table.setHorizontalHeaderLabels([
            "Symptom", "Frequency", "Avg Severity", "Avg Duration", "Trigger Foods", "Confidence"
        ])
        self.symptoms_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.symptoms_table)
        
        tab.setWidget(widget)
        return tab
    
    def create_exposure_tab(self):
        """Create gluten exposure tab"""
        tab = QScrollArea()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Exposure incidents table
        self.exposure_table = QTableWidget()
        self.exposure_table.setColumnCount(5)
        self.exposure_table.setHorizontalHeaderLabels([
            "Date", "Suspected Food", "Symptoms", "Severity", "Duration"
        ])
        self.exposure_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.exposure_table)
        
        tab.setWidget(widget)
        return tab
    
    def create_nutrition_tab(self):
        """Create nutritional impact tab"""
        tab = QScrollArea()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Nutritional impacts table
        self.nutrition_table = QTableWidget()
        self.nutrition_table.setColumnCount(5)
        self.nutrition_table.setHorizontalHeaderLabels([
            "Nutrient", "Deficiency Risk", "Symptom Correlation", "Recommended", "Current Avg"
        ])
        self.nutrition_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.nutrition_table)
        
        tab.setWidget(widget)
        return tab
    
    def create_trends_tab(self):
        """Create health trends tab"""
        tab = QScrollArea()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Health trends table
        self.trends_table = QTableWidget()
        self.trends_table.setColumnCount(5)
        self.trends_table.setHorizontalHeaderLabels([
            "Metric", "Time Period", "Trend", "Change %", "Significance"
        ])
        self.trends_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.trends_table)
        
        tab.setWidget(widget)
        return tab
    
    def create_recommendations_tab(self):
        """Create recommendations tab"""
        tab = QScrollArea()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.recommendations_content = QTextEdit()
        self.recommendations_content.setReadOnly(True)
        layout.addWidget(self.recommendations_content)
        
        tab.setWidget(widget)
        return tab
    
    def start_analysis(self):
        """Start the health analysis in a separate thread"""
        self.worker = HealthAnalysisWorker(self.db_path)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.analysis_complete.connect(self.on_analysis_complete)
        self.worker.start()
    
    def update_progress(self, message: str, percentage: int):
        """Update progress bar and label"""
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(message)
    
    def on_analysis_complete(self, insights: Dict[str, Any]):
        """Handle analysis completion"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.content_widget.setVisible(True)
        
        if 'error' in insights:
            self.summary_content.setText(f"Error during analysis: {insights['error']}")
            return
        
        self.insights = insights
        self.populate_tabs()
    
    def populate_tabs(self):
        """Populate all tabs with analysis results"""
        self.populate_summary()
        self.populate_symptoms()
        self.populate_exposure()
        self.populate_nutrition()
        self.populate_trends()
        self.populate_recommendations()
    
    def populate_summary(self):
        """Populate summary tab"""
        summary = self.insights.get('summary', {})
        
        summary_text = f"""
<h2>Health Analysis Summary</h2>

<h3>📊 Data Overview</h3>
• <b>Total days tracked:</b> {summary.get('total_days_tracked', 0)} days
• <b>Days with symptoms:</b> {summary.get('days_with_symptoms', 0)} days
• <b>Symptom frequency:</b> {summary.get('symptom_frequency', 0):.1%} of tracked days

<h3>📈 Health Metrics</h3>
• <b>Average energy level:</b> {summary.get('average_energy_level', 0)}/10
• <b>Average Bristol scale:</b> {summary.get('average_bristol_scale', 0)}/7
• <b>Average hydration:</b> {summary.get('average_hydration_liters', 0)} L/day
• <b>Average fiber intake:</b> {summary.get('average_fiber_grams', 0)} g/day

<h3>🔍 Key Findings</h3>
"""
        
        # Add key findings based on analysis
        symptom_patterns = self.insights.get('symptom_patterns', [])
        if symptom_patterns:
            top_symptom = symptom_patterns[0]
            summary_text += f"• Most frequent symptom: <b>{top_symptom.symptoms[0]}</b> ({top_symptom.frequency} occurrences)<br>"
        
        gluten_exposures = self.insights.get('gluten_exposures', [])
        if gluten_exposures:
            summary_text += f"• Potential gluten exposures detected: <b>{len(gluten_exposures)}</b> incidents<br>"
        
        health_trends = self.insights.get('health_trends', [])
        declining_trends = [t for t in health_trends if t.trend_direction == 'declining']
        if declining_trends:
            summary_text += f"• Declining health trends: <b>{len(declining_trends)}</b> metrics<br>"
        
        self.summary_content.setHtml(summary_text)
    
    def populate_symptoms(self):
        """Populate symptom patterns table"""
        symptom_patterns = self.insights.get('symptom_patterns', [])
        
        self.symptoms_table.setRowCount(len(symptom_patterns))
        
        for row, pattern in enumerate(symptom_patterns):
            self.symptoms_table.setItem(row, 0, QTableWidgetItem(pattern.symptoms[0]))
            self.symptoms_table.setItem(row, 1, QTableWidgetItem(str(pattern.frequency)))
            self.symptoms_table.setItem(row, 2, QTableWidgetItem(f"{pattern.severity_avg:.2f}"))
            self.symptoms_table.setItem(row, 3, QTableWidgetItem(f"{pattern.duration_avg:.1f}h"))
            self.symptoms_table.setItem(row, 4, QTableWidgetItem(", ".join(pattern.trigger_foods[:3])))
            self.symptoms_table.setItem(row, 5, QTableWidgetItem(f"{pattern.confidence:.1%}"))
    
    def populate_exposure(self):
        """Populate gluten exposure table"""
        exposures = self.insights.get('gluten_exposures', [])
        
        self.exposure_table.setRowCount(len(exposures))
        
        for row, exposure in enumerate(exposures):
            self.exposure_table.setItem(row, 0, QTableWidgetItem(exposure.date))
            self.exposure_table.setItem(row, 1, QTableWidgetItem(exposure.suspected_food))
            self.exposure_table.setItem(row, 2, QTableWidgetItem(", ".join(exposure.symptoms)))
            self.exposure_table.setItem(row, 3, QTableWidgetItem(f"{exposure.severity:.2f}"))
            self.exposure_table.setItem(row, 4, QTableWidgetItem(f"{exposure.duration_hours:.1f}h"))
    
    def populate_nutrition(self):
        """Populate nutritional impact table"""
        nutritional_impacts = self.insights.get('nutritional_impacts', [])
        
        self.nutrition_table.setRowCount(len(nutritional_impacts))
        
        for row, impact in enumerate(nutritional_impacts):
            self.nutrition_table.setItem(row, 0, QTableWidgetItem(impact.nutrient))
            self.nutrition_table.setItem(row, 1, QTableWidgetItem(f"{impact.deficiency_risk:.1%}"))
            self.nutrition_table.setItem(row, 2, QTableWidgetItem(f"{impact.correlation_with_symptoms:.2f}"))
            self.nutrition_table.setItem(row, 3, QTableWidgetItem(str(impact.recommended_intake)))
            self.nutrition_table.setItem(row, 4, QTableWidgetItem(f"{impact.current_avg:.1f}"))
    
    def populate_trends(self):
        """Populate health trends table"""
        trends = self.insights.get('health_trends', [])
        
        self.trends_table.setRowCount(len(trends))
        
        for row, trend in enumerate(trends):
            self.trends_table.setItem(row, 0, QTableWidgetItem(trend.metric))
            self.trends_table.setItem(row, 1, QTableWidgetItem(trend.time_period))
            
            # Color code trend direction
            trend_item = QTableWidgetItem(trend.trend_direction.title())
            if trend.trend_direction == 'improving':
                trend_item.setBackground(QColor(200, 255, 200))
            elif trend.trend_direction == 'declining':
                trend_item.setBackground(QColor(255, 200, 200))
            else:
                trend_item.setBackground(QColor(255, 255, 200))
            
            self.trends_table.setItem(row, 2, trend_item)
            self.trends_table.setItem(row, 3, QTableWidgetItem(f"{trend.change_percentage:.1f}%"))
            self.trends_table.setItem(row, 4, QTableWidgetItem(f"{trend.significance:.1%}"))
    
    def populate_recommendations(self):
        """Populate recommendations tab"""
        recommendations = self.insights.get('recommendations', [])
        
        if not recommendations:
            self.recommendations_content.setText("No specific recommendations at this time.")
            return
        
        recommendations_text = "<h2>Personalized Health Recommendations</h2><br>"
        
        for i, rec in enumerate(recommendations, 1):
            recommendations_text += f"<b>{i}.</b> {rec}<br><br>"
        
        recommendations_text += """
<h3>General Celiac Management Tips:</h3>
• Continue strict adherence to gluten-free diet<br>
• Read food labels carefully and check for cross-contamination warnings<br>
• Keep detailed records of symptoms and food intake<br>
• Regular follow-ups with healthcare provider<br>
• Consider vitamin and mineral supplements as needed<br>
• Join celiac support groups for additional resources<br>
"""
        
        self.recommendations_content.setHtml(recommendations_text)
