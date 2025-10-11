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
                "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;All Files (*)"
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
    
    def process_and_save_image(self, source_path, recipe_id, parent=None, enable_crop=True):
        """Process image (resize/crop) and save to recipe_images folder"""
        try:
            if not source_path or not os.path.exists(source_path):
                return None
            
            # Check if image needs cropping (if enable_crop is True)
            processed_path = source_path
            if enable_crop:
                # Check if image aspect ratio matches recipe card ratio
                with Image.open(source_path) as img:
                    img_ratio = img.width / img.height
                    card_ratio = self.thumbnail_size[0] / self.thumbnail_size[1]
                    
                    # If aspect ratios are significantly different, offer cropping
                    ratio_diff = abs(img_ratio - card_ratio) / card_ratio
                    if ratio_diff > 0.1:  # More than 10% difference
                        try:
                            from utils.image_crop_dialog import crop_image_with_dialog
                            cropped_path = crop_image_with_dialog(
                                source_path, 
                                self.thumbnail_size, 
                                parent
                            )
                            if cropped_path and os.path.exists(cropped_path):
                                processed_path = cropped_path
                                # Clean up the temporary cropped file after processing
                                self._temp_files_to_cleanup = getattr(self, '_temp_files_to_cleanup', [])
                                self._temp_files_to_cleanup.append(cropped_path)
                        except ImportError:
                            # Fallback to old behavior if crop dialog not available
                            pass
            
            # Generate filename with WebP extension for better compression
            filename = f"recipe_{recipe_id}.webp"
            destination_path = os.path.join(self.images_folder, filename)
            
            # Open and process image
            with Image.open(processed_path) as img:
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
                
                # If image was cropped, it should already be the right size
                # Otherwise, resize maintaining aspect ratio
                if processed_path == source_path:
                    img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                else:
                    # Ensure the cropped image is exactly the right size
                    img = img.resize(self.thumbnail_size, Image.Resampling.LANCZOS)
                
                # Save processed image in WebP format for better compression
                img.save(destination_path, 'WEBP', quality=85, optimize=True)
            
            return destination_path
            
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Failed to process image: {str(e)}")
            return None
    
    def get_image_path(self, recipe_id):
        """Get the image path for a recipe"""
        if not recipe_id:
            return None
        
        # Look for image files with this recipe ID
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
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
        default_path = os.path.join(self.images_folder, "default_recipe.webp")
        
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
            
            img.save(path, 'WEBP', quality=85)
            
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
    
    def cleanup_temp_files(self):
        """Clean up temporary files created during processing"""
        if hasattr(self, '_temp_files_to_cleanup'):
            for temp_file in self._temp_files_to_cleanup:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    print(f"Error cleaning up temp file {temp_file}: {e}")
            self._temp_files_to_cleanup.clear()
    
    def convert_to_webp(self, recipe_id):
        """Convert existing recipe image to WebP format"""
        try:
            # Find existing image
            existing_path = self.get_image_path(recipe_id)
            if not existing_path:
                return None
            
            # Skip if already WebP
            if existing_path.lower().endswith('.webp'):
                return existing_path
            
            # Create WebP version
            webp_path = os.path.join(self.images_folder, f"recipe_{recipe_id}.webp")
            
            with Image.open(existing_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as WebP
                img.save(webp_path, 'WEBP', quality=85, optimize=True)
            
            # Remove old image file
            try:
                os.unlink(existing_path)
            except Exception as e:
                print(f"Error removing old image file: {e}")
            
            return webp_path
            
        except Exception as e:
            print(f"Error converting image to WebP: {e}")
            return None
    
    def get_supported_formats(self):
        """Get list of supported image formats"""
        return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']


# Global instance
recipe_image_service = RecipeImageService()
