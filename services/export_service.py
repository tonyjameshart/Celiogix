# path: services/export_service.py
"""
Export Service for PySide6 Application

Provides comprehensive export functionality for all application data.
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from PySide6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PySide6.QtCore import QThread, Signal, QObject
import pandas as pd


class ExportWorker(QObject):
    """Worker thread for export operations"""
    
    progress = Signal(int)
    finished = Signal(bool, str)
    status = Signal(str)
    
    def __init__(self, export_type: str, data: Any, file_path: str, options: Dict[str, Any] = None):
        super().__init__()
        self.export_type = export_type
        self.data = data
        self.file_path = file_path
        self.options = options or {}
    
    def run(self):
        """Run export operation"""
        try:
            self.status.emit(f"Starting {self.export_type} export...")
            
            if self.export_type == "csv":
                self.export_csv()
            elif self.export_type == "json":
                self.export_json()
            elif self.export_type == "excel":
                self.export_excel()
            elif self.export_type == "pdf":
                self.export_pdf()
            elif self.export_type == "html":
                self.export_html()
            else:
                raise ValueError(f"Unsupported export type: {self.export_type}")
            
            self.finished.emit(True, "Export completed successfully!")
            
        except Exception as e:
            self.finished.emit(False, f"Export failed: {str(e)}")
    
    def export_csv(self):
        """Export data to CSV"""
        self.status.emit("Writing CSV file...")
        
        if isinstance(self.data, list) and len(self.data) > 0:
            # Determine if it's a list of dictionaries or list of lists
            if isinstance(self.data[0], dict):
                # List of dictionaries
                df = pd.DataFrame(self.data)
                df.to_csv(self.file_path, index=False, encoding='utf-8')
            else:
                # List of lists
                with open(self.file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(self.data)
        else:
            raise ValueError("Invalid data format for CSV export")
        
        self.progress.emit(100)
    
    def export_json(self):
        """Export data to JSON"""
        self.status.emit("Writing JSON file...")
        
        with open(self.file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.data, jsonfile, indent=2, ensure_ascii=False, default=str)
        
        self.progress.emit(100)
    
    def export_excel(self):
        """Export data to Excel"""
        self.status.emit("Writing Excel file...")
        
        if isinstance(self.data, dict):
            # Multiple sheets
            with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                for sheet_name, sheet_data in self.data.items():
                    if isinstance(sheet_data, list) and len(sheet_data) > 0:
                        if isinstance(sheet_data[0], dict):
                            df = pd.DataFrame(sheet_data)
                        else:
                            df = pd.DataFrame(sheet_data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # Single sheet
            if isinstance(self.data, list) and len(self.data) > 0:
                if isinstance(self.data[0], dict):
                    df = pd.DataFrame(self.data)
                else:
                    df = pd.DataFrame(self.data)
                df.to_excel(self.file_path, index=False)
        
        self.progress.emit(100)
    
    def export_pdf(self):
        """Export data to PDF"""
        self.status.emit("Generating PDF...")
        
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(self.file_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            title = Paragraph(self.options.get('title', 'Data Export'), title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=10,
                alignment=1
            )
            date_text = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style)
            story.append(date_text)
            story.append(Spacer(1, 30))
            
            # Data table
            if isinstance(self.data, list) and len(self.data) > 0:
                if isinstance(self.data[0], dict):
                    # List of dictionaries
                    headers = list(self.data[0].keys())
                    table_data = [headers]
                    
                    for row in self.data:
                        table_data.append([str(row.get(header, '')) for header in headers])
                else:
                    # List of lists
                    table_data = self.data
                
                # Create table
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
            
            # Build PDF
            doc.build(story)
            
        except ImportError:
            raise ImportError("ReportLab is required for PDF export. Install with: pip install reportlab")
        
        self.progress.emit(100)
    
    def export_html(self):
        """Export data to HTML"""
        self.status.emit("Generating HTML...")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.options.get('title', 'Data Export')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #4caf50; text-align: center; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .export-info {{ text-align: center; color: #666; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>{self.options.get('title', 'Data Export')}</h1>
            <div class="export-info">
                Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        """
        
        if isinstance(self.data, list) and len(self.data) > 0:
            if isinstance(self.data[0], dict):
                # List of dictionaries
                headers = list(self.data[0].keys())
                html_content += "<table><thead><tr>"
                for header in headers:
                    html_content += f"<th>{header}</th>"
                html_content += "</tr></thead><tbody>"
                
                for row in self.data:
                    html_content += "<tr>"
                    for header in headers:
                        html_content += f"<td>{row.get(header, '')}</td>"
                    html_content += "</tr>"
                
                html_content += "</tbody></table>"
            else:
                # List of lists
                html_content += "<table><tbody>"
                for row in self.data:
                    html_content += "<tr>"
                    for cell in row:
                        html_content += f"<td>{cell}</td>"
                    html_content += "</tr>"
                html_content += "</tbody></table>"
        
        html_content += """
        </body>
        </html>
        """
        
        with open(self.file_path, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)
        
        self.progress.emit(100)


class ExportService:
    """Main export service for the application"""
    
    def __init__(self):
        self.supported_formats = {
            'csv': 'CSV Files (*.csv)',
            'json': 'JSON Files (*.json)',
            'excel': 'Excel Files (*.xlsx)',
            'pdf': 'PDF Files (*.pdf)',
            'html': 'HTML Files (*.html)'
        }
    
    def export_data(self, parent_widget, data: Any, export_type: str, 
                   title: str = "Data Export", filename: str = None) -> bool:
        """Export data to specified format"""
        try:
            # Get file path
            file_path = self._get_export_path(parent_widget, export_type, filename)
            if not file_path:
                return False
            
            # Create and run export worker
            worker = ExportWorker(export_type, data, file_path, {'title': title})
            
            # Show progress dialog
            progress_dialog = QProgressDialog(f"Exporting {export_type.upper()}...", "Cancel", 0, 100, parent_widget)
            progress_dialog.setWindowTitle("Export Progress")
            progress_dialog.setModal(True)
            progress_dialog.show()
            
            # Connect signals
            worker.progress.connect(progress_dialog.setValue)
            worker.status.connect(progress_dialog.setLabelText)
            worker.finished.connect(lambda success, message: self._handle_export_finished(progress_dialog, success, message))
            
            # Start worker thread
            thread = QThread()
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            thread.start()
            
            # Wait for completion
            while thread.isRunning():
                QApplication.processEvents()
            
            thread.wait()
            thread.deleteLater()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(parent_widget, "Export Error", f"Failed to export data: {str(e)}")
            return False
    
    def _get_export_path(self, parent_widget, export_type: str, filename: str = None) -> Optional[str]:
        """Get export file path from user"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.{export_type}"
        
        file_filter = self.supported_formats.get(export_type, "All Files (*)")
        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget, f"Export {export_type.upper()}", filename, file_filter)
        
        return file_path if file_path else None
    
    def _handle_export_finished(self, progress_dialog, success: bool, message: str):
        """Handle export completion"""
        progress_dialog.close()
        
        if success:
            QMessageBox.information(progress_dialog.parent(), "Export Complete", message)
        else:
            QMessageBox.critical(progress_dialog.parent(), "Export Failed", message)
    
    def export_pantry_data(self, parent_widget, pantry_data: List[Dict]) -> bool:
        """Export pantry data with gluten-free specific formatting"""
        return self.export_data(parent_widget, pantry_data, 'csv', 
                               "Pantry Inventory", "pantry_inventory.csv")
    
    def export_health_data(self, parent_widget, health_data: List[Dict]) -> bool:
        """Export health data with medical formatting"""
        return self.export_data(parent_widget, health_data, 'csv', 
                               "Health Log", "health_log.csv")
    
    def export_recipes(self, parent_widget, recipe_data: List[Dict]) -> bool:
        """Export recipe data"""
        return self.export_data(parent_widget, recipe_data, 'excel', 
                               "Recipe Collection", "recipes.xlsx")
    
    def export_shopping_list(self, parent_widget, shopping_data: List[Dict]) -> bool:
        """Export shopping list data"""
        return self.export_data(parent_widget, shopping_data, 'csv', 
                               "Shopping List", "shopping_list.csv")
    
    def export_menu_plan(self, parent_widget, menu_data: List[Dict]) -> bool:
        """Export menu plan data"""
        return self.export_data(parent_widget, menu_data, 'excel', 
                               "Menu Plan", "menu_plan.xlsx")
    
    def export_calendar_events(self, parent_widget, calendar_data: List[Dict]) -> bool:
        """Export calendar events"""
        return self.export_data(parent_widget, calendar_data, 'csv', 
                               "Calendar Events", "calendar_events.csv")
    
    def export_all_data(self, parent_widget, all_data: Dict[str, List[Dict]]) -> bool:
        """Export all application data to Excel with multiple sheets"""
        return self.export_data(parent_widget, all_data, 'excel', 
                               "Complete Data Export", "celiogix_export.xlsx")
    
    def export_doctor_report(self, parent_widget, health_data: List[Dict]) -> bool:
        """Export health data as PDF for doctor visits"""
        return self.export_data(parent_widget, health_data, 'pdf', 
                               "Health Report for Doctor", "health_report.pdf")


# Global export service instance
export_service = ExportService()
