#!/usr/bin/env python3
"""
Image Service for Recipe Management
Handles image upload, resize, and storage for recipe thumbnails
"""

import os
import shutil
from PIL import Image
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class RecipeImageService:
    """Service for handling recipe images"""
    
    def __init__(self):
        self.images_folder = "recipe_images"
        self.thumbnail_size = (300, 200)  # Width, Height
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        
        # Create images folder if it doesn't exist
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
    
    def select_image(self, parent=None):
        """Open file dialog to select an image"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                parent, 
                "Select Recipe Image", 
                "", 
                "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
            )
            
            if file_path:
                # Validate file size
                file_size = os.path.getsize(file_path)
                if file_size > self.max_file_size:
                    QMessageBox.warning(
                        parent, 
                        "File Too Large", 
                        f"Image file is too large ({file_size / 1024 / 1024:.1f}MB). "
                        f"Maximum size is {self.max_file_size / 1024 / 1024}MB."
                    )
                    return None
                
                return file_path
            
            return None
            
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Failed to select image: {str(e)}")
            return None
    
    def process_and_save_image(self, source_path, recipe_id, parent=None):
        """Process image (resize) and save to recipe_images folder"""
        try:
            if not source_path or not os.path.exists(source_path):
                return None
            
            # Generate filename based on recipe ID
            file_extension = os.path.splitext(source_path)[1].lower()
            filename = f"recipe_{recipe_id}{file_extension}"
            destination_path = os.path.join(self.images_folder, filename)
            
            # Open and process image
            with Image.open(source_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize image maintaining aspect ratio
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                
                # Save processed image
                img.save(destination_path, 'JPEG', quality=85, optimize=True)
            
            return destination_path
            
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Failed to process image: {str(e)}")
            return None
    
    def get_image_path(self, recipe_id):
        """Get the image path for a recipe"""
        if not recipe_id:
            return None
        
        # Look for image files with this recipe ID
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            image_path = os.path.join(self.images_folder, f"recipe_{recipe_id}{ext}")
            if os.path.exists(image_path):
                return image_path
        
        return None
    
    def load_image_pixmap(self, recipe_id, size=None):
        """Load image as QPixmap for display"""
        try:
            image_path = self.get_image_path(recipe_id)
            if not image_path or not os.path.exists(image_path):
                return None
            
            pixmap = QPixmap(image_path)
            
            if size:
                pixmap = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            return pixmap
            
        except Exception as e:
            print(f"Error loading image pixmap: {e}")
            return None
    
    def delete_image(self, recipe_id):
        """Delete image file for a recipe"""
        try:
            image_path = self.get_image_path(recipe_id)
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False
    
    def get_default_image_path(self):
        """Get path to default recipe image"""
        default_path = os.path.join(self.images_folder, "default_recipe.png")
        
        # Create default image if it doesn't exist
        if not os.path.exists(default_path):
            self._create_default_image(default_path)
        
        return default_path
    
    def _create_default_image(self, path):
        """Create a default recipe image"""
        try:
            # Create a simple default image
            img = Image.new('RGB', self.thumbnail_size, (240, 240, 240))
            
            # Add some text or icon (simplified for now)
            # In a real implementation, you might want to add text or an icon
            
            img.save(path, 'PNG')
            
        except Exception as e:
            print(f"Error creating default image: {e}")
    
    def validate_image_file(self, file_path):
        """Validate if file is a valid image"""
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def get_image_info(self, file_path):
        """Get image information (size, format, etc.)"""
        try:
            with Image.open(file_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_bytes': os.path.getsize(file_path)
                }
        except Exception as e:
            print(f"Error getting image info: {e}")
            return None


# Global instance
recipe_image_service = RecipeImageService()
