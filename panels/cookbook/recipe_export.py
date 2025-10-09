# path: panels/cookbook/recipe_export.py
"""
Recipe export functionality
"""

import os
from datetime import datetime
from typing import List, Dict, Any
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QTextStream
from PySide6.QtGui import QTextDocument


class RecipeExport:
    """Handles recipe export operations"""
    
    def __init__(self):
        pass
    
    def export_recipes(self, recipes: List[Dict[str, Any]]):
        """Export recipes to various formats"""
        if not recipes:
            QMessageBox.information(None, "Export Recipes", "No recipes to export.")
            return
        
        # Show format selection dialog
        format_dialog = self.show_format_selection_dialog()
        if not format_dialog:
            return
        
        format_type = format_dialog.get('format')
        file_path = format_dialog.get('file_path')
        
        if not file_path:
            return
        
        try:
            if format_type == 'txt':
                self.export_to_txt(recipes, file_path)
            elif format_type == 'html':
                self.export_to_html(recipes, file_path)
            elif format_type == 'pdf':
                self.export_to_pdf(recipes, file_path)
            elif format_type == 'csv':
                self.export_to_csv(recipes, file_path)
            
            QMessageBox.information(None, "Export Complete", f"Recipes exported successfully to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(None, "Export Error", f"Failed to export recipes: {str(e)}")
    
    def show_format_selection_dialog(self) -> Dict[str, str]:
        """Show format selection dialog"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup
        
        dialog = QDialog()
        dialog.setWindowTitle("Export Recipes")
        dialog.setModal(True)
        dialog.resize(300, 200)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Select export format:"))
        
        # Format selection
        format_group = QButtonGroup()
        
        txt_radio = QRadioButton("Text (.txt)")
        html_radio = QRadioButton("HTML (.html)")
        pdf_radio = QRadioButton("PDF (.pdf)")
        csv_radio = QRadioButton("CSV (.csv)")
        
        txt_radio.setChecked(True)
        
        format_group.addButton(txt_radio, 0)
        format_group.addButton(html_radio, 1)
        format_group.addButton(pdf_radio, 2)
        format_group.addButton(csv_radio, 3)
        
        layout.addWidget(txt_radio)
        layout.addWidget(html_radio)
        layout.addWidget(pdf_radio)
        layout.addWidget(csv_radio)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export")
        cancel_btn = QPushButton("Cancel")
        
        button_layout.addWidget(export_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Connect signals
        export_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.Accepted:
            # Get file path
            file_path, _ = QFileDialog.getSaveFileName(
                None, "Save Recipes As", 
                f"recipes_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                self.get_file_filter(format_group.checkedId())
            )
            
            if file_path:
                format_names = ['txt', 'html', 'pdf', 'csv']
                return {
                    'format': format_names[format_group.checkedId()],
                    'file_path': file_path
                }
        
        return None
    
    def get_file_filter(self, format_id: int) -> str:
        """Get file filter for format"""
        filters = {
            0: "Text Files (*.txt);;All Files (*)",
            1: "HTML Files (*.html);;All Files (*)",
            2: "PDF Files (*.pdf);;All Files (*)",
            3: "CSV Files (*.csv);;All Files (*)"
        }
        return filters.get(format_id, "All Files (*)")
    
    def export_to_txt(self, recipes: List[Dict[str, Any]], file_path: str):
        """Export recipes to text file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("COOKBOOK RECIPES\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total recipes: {len(recipes)}\n\n")
            
            for i, recipe in enumerate(recipes, 1):
                f.write(f"{i}. {recipe.get('name', 'Untitled Recipe')}\n")
                f.write("-" * 40 + "\n")
                
                if recipe.get('description'):
                    f.write(f"Description: {recipe.get('description', '')}\n\n")
                
                prep_time = recipe.get('prep_time', 0)
                cook_time = recipe.get('cook_time', 0)
                servings = recipe.get('servings', 1)
                difficulty = recipe.get('difficulty', 'Easy')
                
                f.write(f"Prep Time: {prep_time} min\n")
                f.write(f"Cook Time: {cook_time} min\n")
                f.write(f"Servings: {servings}\n")
                f.write(f"Difficulty: {difficulty}\n\n")
                
                if recipe.get('ingredients'):
                    f.write("INGREDIENTS:\n")
                    f.write(recipe.get('ingredients', '') + "\n\n")
                
                if recipe.get('instructions'):
                    f.write("INSTRUCTIONS:\n")
                    f.write(recipe.get('instructions', '') + "\n\n")
                
                f.write("=" * 50 + "\n\n")
    
    def export_to_html(self, recipes: List[Dict[str, Any]], file_path: str):
        """Export recipes to HTML file"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cookbook Recipes</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .recipe {{ margin-bottom: 40px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                .recipe-header {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px; }}
                .recipe-title {{ font-size: 24px; color: #2c3e50; margin: 0; }}
                .recipe-meta {{ color: #7f8c8d; margin-top: 10px; }}
                .ingredients, .instructions {{ margin-top: 20px; }}
                .ingredients h3, .instructions h3 {{ color: #27ae60; }}
                .ingredients {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                .instructions {{ background-color: #f0f8f0; padding: 15px; border-radius: 5px; }}
                pre {{ white-space: pre-wrap; font-family: inherit; }}
            </style>
        </head>
        <body>
            <h1>🍳 Cookbook Recipes</h1>
            <p><strong>Exported on:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Total recipes:</strong> {len(recipes)}</p>
        """
        
        for recipe in recipes:
            html_content += f"""
            <div class="recipe">
                <div class="recipe-header">
                    <h2 class="recipe-title">{recipe.get('name', 'Untitled Recipe')}</h2>
                    <div class="recipe-meta">
                        ⏱️ Prep: {recipe.get('prep_time', 0)} min | 
                        🍳 Cook: {recipe.get('cook_time', 0)} min | 
                        👥 Serves: {recipe.get('servings', 1)} | 
                        📊 Difficulty: {recipe.get('difficulty', 'Easy')}
                    </div>
                    {f'<p><em>{recipe.get("description", "")}</em></p>' if recipe.get('description') else ''}
                </div>
            """
            
            if recipe.get('ingredients'):
                html_content += f"""
                <div class="ingredients">
                    <h3>🥘 Ingredients</h3>
                    <pre>{recipe.get('ingredients', '')}</pre>
                </div>
                """
            
            if recipe.get('instructions'):
                html_content += f"""
                <div class="instructions">
                    <h3>📝 Instructions</h3>
                    <pre>{recipe.get('instructions', '')}</pre>
                </div>
                """
            
            html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def export_to_pdf(self, recipes: List[Dict[str, Any]], file_path: str):
        """Export recipes to PDF file"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            story.append(Paragraph("🍳 Cookbook Recipes", title_style))
            story.append(Spacer(1, 12))
            
            # Export info
            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=10,
                textColor='gray'
            )
            
            story.append(Paragraph(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
            story.append(Paragraph(f"Total recipes: {len(recipes)}", info_style))
            story.append(Spacer(1, 20))
            
            # Recipes
            for i, recipe in enumerate(recipes):
                if i > 0:
                    story.append(PageBreak())
                
                # Recipe title
                story.append(Paragraph(recipe.get('name', 'Untitled Recipe'), styles['Heading2']))
                story.append(Spacer(1, 12))
                
                # Recipe meta
                meta_text = f"⏱️ Prep: {recipe.get('prep_time', 0)} min | 🍳 Cook: {recipe.get('cook_time', 0)} min | 👥 Serves: {recipe.get('servings', 1)} | 📊 Difficulty: {recipe.get('difficulty', 'Easy')}"
                story.append(Paragraph(meta_text, styles['Normal']))
                story.append(Spacer(1, 12))
                
                # Description
                if recipe.get('description'):
                    story.append(Paragraph("<b>Description:</b>", styles['Heading3']))
                    story.append(Paragraph(recipe.get('description', ''), styles['Normal']))
                    story.append(Spacer(1, 12))
                
                # Ingredients
                if recipe.get('ingredients'):
                    story.append(Paragraph("<b>🥘 Ingredients:</b>", styles['Heading3']))
                    ingredients_text = recipe.get('ingredients', '').replace('\n', '<br/>')
                    story.append(Paragraph(ingredients_text, styles['Normal']))
                    story.append(Spacer(1, 12))
                
                # Instructions
                if recipe.get('instructions'):
                    story.append(Paragraph("<b>📝 Instructions:</b>", styles['Heading3']))
                    instructions_text = recipe.get('instructions', '').replace('\n', '<br/>')
                    story.append(Paragraph(instructions_text, styles['Normal']))
            
            doc.build(story)
            
        except ImportError:
            raise Exception("ReportLab library is required for PDF export. Please install it with: pip install reportlab")
    
    def export_to_csv(self, recipes: List[Dict[str, Any]], file_path: str):
        """Export recipes to CSV file"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Name', 'Category', 'Description', 'Prep Time', 'Cook Time', 
                'Servings', 'Difficulty', 'Ingredients', 'Instructions', 'Created Date'
            ])
            
            # Write recipe data
            for recipe in recipes:
                writer.writerow([
                    recipe.get('name', ''),
                    recipe.get('category_name', ''),
                    recipe.get('description', ''),
                    recipe.get('prep_time', 0),
                    recipe.get('cook_time', 0),
                    recipe.get('servings', 1),
                    recipe.get('difficulty', 'Easy'),
                    recipe.get('ingredients', ''),
                    recipe.get('instructions', ''),
                    recipe.get('created_date', '')
                ])
