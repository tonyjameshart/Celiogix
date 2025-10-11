#!/usr/bin/env python3
"""
Image Crop Dialog for Recipe Management
Provides interactive image cropping with fixed center and aspect ratio
"""

import os
from PIL import Image
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QSlider, QSpinBox, QGroupBox, QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor


class ImageCropDialog(QDialog):
    """Dialog for cropping images with fixed center and aspect ratio"""
    
    # Signal emitted when crop is accepted with the cropped image path
    image_cropped = Signal(str)
    
    def __init__(self, image_path, target_aspect_ratio=(280, 180), parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.target_aspect_ratio = target_aspect_ratio
        self.original_image = None
        self.current_scale = 1.0
        self.crop_size = 100  # Percentage of image to crop
        
        self.setWindowTitle("Crop Recipe Image")
        self.setModal(True)
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_image()
    
    def setup_ui(self):
        """Set up the crop dialog UI"""
        layout = QVBoxLayout(self)
        
        # Image preview area
        self.image_label = QLabel()
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                background-color: #f0f0f0;
            }
        """)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(False)  # We'll handle scaling manually
        layout.addWidget(self.image_label)
        
        # Controls
        controls_group = QGroupBox("Crop Controls")
        controls_layout = QGridLayout(controls_group)
        
        # Crop size slider
        controls_layout.addWidget(QLabel("Crop Size:"), 0, 0)
        self.crop_slider = QSlider(Qt.Horizontal)
        self.crop_slider.setRange(20, 100)
        self.crop_slider.setValue(80)
        self.crop_slider.valueChanged.connect(self.update_crop_preview)
        controls_layout.addWidget(self.crop_slider, 0, 1)
        
        self.crop_spinbox = QSpinBox()
        self.crop_spinbox.setRange(20, 100)
        self.crop_spinbox.setValue(80)
        self.crop_spinbox.setSuffix("%")
        self.crop_spinbox.valueChanged.connect(self.on_crop_size_changed)
        controls_layout.addWidget(self.crop_spinbox, 0, 2)
        
        # Aspect ratio info
        aspect_ratio = self.target_aspect_ratio[0] / self.target_aspect_ratio[1]
        controls_layout.addWidget(QLabel(f"Target Aspect Ratio: {aspect_ratio:.2f}:1"), 1, 0, 1, 3)
        
        # Preview info
        self.info_label = QLabel()
        controls_layout.addWidget(self.info_label, 2, 0, 1, 3)
        
        layout.addWidget(controls_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        
        self.crop_btn = QPushButton("Crop & Apply")
        self.crop_btn.clicked.connect(self.apply_crop)
        self.crop_btn.setDefault(True)
        button_layout.addWidget(self.crop_btn)
        
        layout.addLayout(button_layout)
        
        # Connect slider and spinbox
        self.crop_slider.valueChanged.connect(self.crop_spinbox.setValue)
        self.crop_spinbox.valueChanged.connect(self.crop_slider.setValue)
    
    def load_image(self):
        """Load the original image"""
        try:
            self.original_image = Image.open(self.image_path)
            self.update_crop_preview()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            self.reject()
    
    def on_crop_size_changed(self, value):
        """Handle crop size change"""
        self.crop_size = value
        self.update_crop_preview()
    
    def update_crop_preview(self):
        """Update the crop preview"""
        if not self.original_image:
            return
        
        # Calculate crop dimensions
        img_width, img_height = self.original_image.size
        target_width, target_height = self.target_aspect_ratio
        
        # Calculate the crop size based on percentage
        crop_scale = self.crop_size / 100.0
        
        # Calculate crop dimensions maintaining aspect ratio
        if img_width / img_height > target_width / target_height:
            # Image is wider than target - crop width
            crop_height = img_height * crop_scale
            crop_width = crop_height * (target_width / target_height)
        else:
            # Image is taller than target - crop height
            crop_width = img_width * crop_scale
            crop_height = crop_width * (target_height / target_width)
        
        # Center the crop
        crop_x = (img_width - crop_width) / 2
        crop_y = (img_height - crop_height) / 2
        
        # Create preview image
        preview_img = self.original_image.copy()
        
        # Create a semi-transparent overlay to show crop area
        overlay = Image.new('RGBA', preview_img.size, (0, 0, 0, 0))
        
        # Draw crop rectangle
        from PIL import ImageDraw
        draw = ImageDraw.Draw(overlay)
        
        # Fill outside crop area with semi-transparent black
        draw.rectangle([0, 0, img_width, img_height], fill=(0, 0, 0, 128))
        
        # Clear the crop area
        draw.rectangle([crop_x, crop_y, crop_x + crop_width, crop_y + crop_height], fill=(0, 0, 0, 0))
        
        # Draw crop border
        border_width = max(2, int(min(crop_width, crop_height) * 0.01))
        draw.rectangle([crop_x, crop_y, crop_x + crop_width, crop_y + crop_height], 
                      outline=(255, 255, 255, 255), width=border_width)
        
        # Composite images
        if preview_img.mode != 'RGBA':
            preview_img = preview_img.convert('RGBA')
        
        preview_img = Image.alpha_composite(preview_img, overlay)
        
        # Convert to QPixmap and display
        preview_img = preview_img.convert('RGB')
        
        # Scale to fit preview area while maintaining aspect ratio
        preview_label_size = self.image_label.size()
        preview_width = preview_label_size.width() - 20
        preview_height = preview_label_size.height() - 20
        
        preview_img.thumbnail((preview_width, preview_height), Image.Resampling.LANCZOS)
        
        # Convert to QPixmap
        import io
        img_bytes = io.BytesIO()
        preview_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(img_bytes.getvalue())
        
        self.image_label.setPixmap(pixmap)
        
        # Update info
        self.info_label.setText(
            f"Original: {img_width}×{img_height} | "
            f"Crop: {int(crop_width)}×{int(crop_height)} | "
            f"Center: ({int(crop_x)}, {int(crop_y)})"
        )
    
    def apply_crop(self):
        """Apply the crop and return the cropped image"""
        if not self.original_image:
            return
        
        try:
            img_width, img_height = self.original_image.size
            target_width, target_height = self.target_aspect_ratio
            
            # Calculate crop dimensions
            crop_scale = self.crop_size / 100.0
            
            if img_width / img_height > target_width / target_height:
                # Image is wider than target - crop width
                crop_height = img_height * crop_scale
                crop_width = crop_height * (target_width / target_height)
            else:
                # Image is taller than target - crop height
                crop_width = img_width * crop_scale
                crop_height = crop_width * (target_height / target_width)
            
            # Center the crop
            crop_x = (img_width - crop_width) / 2
            crop_y = (img_height - crop_height) / 2
            
            # Perform the crop
            crop_box = (crop_x, crop_y, crop_x + crop_width, crop_y + crop_height)
            cropped_img = self.original_image.crop(crop_box)
            
            # Resize to target dimensions
            final_img = cropped_img.resize(self.target_aspect_ratio, Image.Resampling.LANCZOS)
            
            # Save the cropped image
            cropped_path = self.image_path.replace('.', '_cropped.')
            final_img.save(cropped_path, 'JPEG', quality=95)
            
            self.image_cropped.emit(cropped_path)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to crop image: {str(e)}")
    
    def get_cropped_image_path(self):
        """Get the path to the cropped image (for use after dialog closes)"""
        return self.image_path.replace('.', '_cropped.')


def crop_image_with_dialog(image_path, target_aspect_ratio=(280, 180), parent=None):
    """
    Open image crop dialog and return the cropped image path
    
    Args:
        image_path: Path to the original image
        target_aspect_ratio: Target aspect ratio as (width, height)
        parent: Parent widget
        
    Returns:
        str: Path to cropped image, or None if cancelled
    """
    dialog = ImageCropDialog(image_path, target_aspect_ratio, parent)
    
    if dialog.exec() == QDialog.Accepted:
        return dialog.get_cropped_image_path()
    
    return None
