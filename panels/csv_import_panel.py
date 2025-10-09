# path: panels/csv_import_panel_pyside6.py
"""
CSV Import Panel for PySide6 Desktop Application

Provides UI for importing CSV files from the mobile app into the desktop application.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QGroupBox, QRadioButton, QProgressBar,
    QFileDialog, QMessageBox, QFrame, QSplitter, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QTextCursor

from utils.csv_import_service import CSVImportService
from utils.db import get_connection
from panels.base_panel import BasePanel
from panels.context_menu_mixin import CSVImportContextMenuMixin


class CSVImportWorker(QThread):
    """Worker thread for CSV import operations"""
    
    progress = Signal(str)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, import_service: CSVImportService, file_path: Path):
        super().__init__()
        self.import_service = import_service
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress.emit("Starting import...")
            result = self.import_service.import_csv_file(self.file_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class CSVImportPanel(CSVImportContextMenuMixin, BasePanel):
    """Panel for importing CSV files from mobile app"""
    
    def __init__(self, master=None, app=None):
        super().__init__(master, app)
        self.db = get_connection()
        self.import_service = CSVImportService(self.db)
        self.worker = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("Import Mobile Data")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # File selection section
        file_group = QGroupBox("Select CSV File")
        file_layout = QVBoxLayout(file_group)
        
        # File path display
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(QLabel("File:"))
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setPlaceholderText("No file selected")
        file_path_layout.addWidget(self.file_path_edit, 1)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_file)
        file_path_layout.addWidget(browse_button)
        
        file_layout.addLayout(file_path_layout)
        main_layout.addWidget(file_group)
        
        # File validation section
        validation_group = QGroupBox("File Validation")
        validation_layout = QVBoxLayout(validation_group)
        
        self.validation_text = QTextEdit()
        self.validation_text.setMaximumHeight(100)
        self.validation_text.setReadOnly(True)
        self.validation_text.setPlaceholderText("File validation results will appear here...")
        validation_layout.addWidget(self.validation_text)
        
        main_layout.addWidget(validation_group)
        
        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout(options_group)
        
        # Import mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Import Mode:"))
        
        self.replace_radio = QRadioButton("Replace existing data")
        self.replace_radio.setChecked(True)
        mode_layout.addWidget(self.replace_radio)
        
        self.skip_radio = QRadioButton("Skip existing data")
        mode_layout.addWidget(self.skip_radio)
        
        mode_layout.addStretch()
        options_layout.addLayout(mode_layout)
        
        # Import button
        button_layout = QHBoxLayout()
        self.import_button = QPushButton("Import CSV File")
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self.import_csv)
        button_layout.addWidget(self.import_button)
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        options_layout.addLayout(button_layout)
        
        main_layout.addWidget(options_group)
        
        # Progress section
        progress_group = QGroupBox("Import Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_label = QLabel("Ready to import...")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(progress_group)
        
        # Results section
        results_group = QGroupBox("Import Results")
        results_layout = QVBoxLayout(results_group)
        
        # Results text with scrollbar
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Import results will appear here...")
        results_layout.addWidget(self.results_text)
        
        main_layout.addWidget(results_group, 1)  # Give it more space
    
    def browse_file(self):
        """Browse for CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV files (*.csv);;All files (*.*)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
            self.validate_file()
    
    def validate_file(self):
        """Validate selected CSV file"""
        file_path = self.file_path_edit.text()
        if not file_path:
            return
        
        try:
            validation_result = self.import_service.validate_csv_file(Path(file_path))
            
            self.validation_text.clear()
            
            if validation_result['valid']:
                self.validation_text.append(f"✓ {validation_result['message']}")
                self.validation_text.append(f"File Type: {validation_result['file_type']}")
                self.validation_text.append(f"Data Rows: {validation_result['row_count']}")
                self.validation_text.append(f"Headers: {', '.join(validation_result['headers'])}")
                self.import_button.setEnabled(True)
            else:
                self.validation_text.append(f"✗ {validation_result['message']}")
                self.import_button.setEnabled(False)
                
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", f"Error validating file: {str(e)}")
            self.import_button.setEnabled(False)
    
    def import_csv(self):
        """Import CSV file"""
        file_path = self.file_path_edit.text()
        if not file_path:
            QMessageBox.warning(self, "No File", "Please select a CSV file first.")
            return
        
        try:
            # Start progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.progress_label.setText("Importing CSV file...")
            self.import_button.setEnabled(False)
            
            # Create and start worker thread
            self.worker = CSVImportWorker(self.import_service, Path(file_path))
            self.worker.progress.connect(self.progress_label.setText)
            self.worker.finished.connect(self.import_finished)
            self.worker.error.connect(self.import_error)
            self.worker.start()
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.progress_label.setText("Import failed!")
            QMessageBox.critical(self, "Import Error", f"Error importing file: {str(e)}")
            self.import_button.setEnabled(True)
    
    def import_finished(self, result: Dict[str, Any]):
        """Handle import completion"""
        self.progress_bar.setVisible(False)
        
        # Display results
        self.display_results(result)
        
        if result['success']:
            self.progress_label.setText("Import completed successfully!")
            QMessageBox.information(
                self,
                "Import Complete",
                f"Successfully imported {result['imported_count']} records."
            )
        else:
            self.progress_label.setText("Import failed!")
            QMessageBox.critical(self, "Import Failed", result['message'])
        
        self.import_button.setEnabled(True)
    
    def import_error(self, error_message: str):
        """Handle import error"""
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Import failed!")
        QMessageBox.critical(self, "Import Error", f"Error importing file: {error_message}")
        self.import_button.setEnabled(True)
    
    def display_results(self, result: Dict[str, Any]):
        """Display import results"""
        self.results_text.clear()
        
        # Header
        self.results_text.append("IMPORT RESULTS")
        self.results_text.append("=" * 50)
        self.results_text.append("")
        
        # Status
        status = "SUCCESS" if result['success'] else "FAILED"
        self.results_text.append(f"Status: {status}")
        self.results_text.append(f"Message: {result['message']}")
        self.results_text.append(f"Records Imported: {result['imported_count']}")
        self.results_text.append("")
        
        # Detailed counts if available
        if 'health_logs_count' in result:
            self.results_text.append(f"Health Logs: {result['health_logs_count']}")
        if 'scans_count' in result:
            self.results_text.append(f"Barcode Scans: {result['scans_count']}")
        
        # Errors if any
        if result.get('errors'):
            self.results_text.append("")
            self.results_text.append("ERRORS:")
            self.results_text.append("-" * 20)
            for error in result['errors']:
                self.results_text.append(f"• {error}")
        
        # Scroll to top
        cursor = self.results_text.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.results_text.setTextCursor(cursor)
    
    def clear_form(self):
        """Clear the form"""
        self.file_path_edit.clear()
        self.validation_text.clear()
        self.results_text.clear()
        self.progress_label.setText("Ready to import...")
        self.progress_bar.setVisible(False)
        self.import_button.setEnabled(False)
