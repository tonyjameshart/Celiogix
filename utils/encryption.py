#!/usr/bin/env python3
"""
Data encryption utilities for sensitive health information
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional, Union


class DataEncryption:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self, password: Optional[str] = None):
        """
        Initialize encryption with optional password
        
        Args:
            password: Optional password for key derivation. If None, uses default key.
        """
        self.password = password or self._get_default_password()
        self._key = None
        self._fernet = None
        self._initialize_encryption()
    
    def _get_default_password(self) -> str:
        """Get default password from environment or generate one"""
        default_password = os.getenv('CELIOGIX_ENCRYPTION_PASSWORD')
        if not default_password:
            # Generate a default password based on system info
            import platform
            import getpass
            system_info = f"{platform.node()}{getpass.getuser()}{platform.system()}"
            default_password = hashlib.sha256(system_info.encode()).hexdigest()[:32]
        return default_password
    
    def _initialize_encryption(self):
        """Initialize encryption key and Fernet instance"""
        try:
            # Derive key from password
            password_bytes = self.password.encode()
            salt = b'celiogix_salt_2024'  # In production, use random salt stored separately
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            self._key = key
            self._fernet = Fernet(key)
            
        except Exception as e:
            raise Exception(f"Failed to initialize encryption: {e}")
    
    def encrypt_string(self, data: str) -> str:
        """
        Encrypt a string
        
        Args:
            data: String to encrypt
            
        Returns:
            Base64 encoded encrypted string
        """
        if not data:
            return ""
        
        try:
            data_bytes = data.encode('utf-8')
            encrypted_data = self._fernet.encrypt(data_bytes)
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to encrypt string: {e}")
    
    def decrypt_string(self, encrypted_data: str) -> str:
        """
        Decrypt a string
        
        Args:
            encrypted_data: Base64 encoded encrypted string
            
        Returns:
            Decrypted string
        """
        if not encrypted_data:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self._fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to decrypt string: {e}")
    
    def encrypt_dict(self, data: dict) -> dict:
        """
        Encrypt sensitive fields in a dictionary
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Dictionary with encrypted sensitive fields
        """
        encrypted_data = data.copy()
        
        # Define sensitive fields that should be encrypted
        sensitive_fields = [
            'symptoms', 'notes', 'description', 'medication_notes',
            'allergy_info', 'medical_notes', 'diagnosis_notes'
        ]
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt_string(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict) -> dict:
        """
        Decrypt sensitive fields in a dictionary
        
        Args:
            data: Dictionary with encrypted sensitive fields
            
        Returns:
            Dictionary with decrypted sensitive fields
        """
        decrypted_data = data.copy()
        
        # Define sensitive fields that should be decrypted
        sensitive_fields = [
            'symptoms', 'notes', 'description', 'medication_notes',
            'allergy_info', 'medical_notes', 'diagnosis_notes'
        ]
        
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt_string(str(decrypted_data[field]))
                except:
                    # If decryption fails, keep original value (might be unencrypted legacy data)
                    pass
        
        return decrypted_data
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file
        
        Args:
            file_path: Path to file to encrypt
            output_path: Optional output path. If None, adds .enc extension
            
        Returns:
            Path to encrypted file
        """
        if not output_path:
            output_path = file_path + '.enc'
        
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self._fernet.encrypt(file_data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            return output_path
        except Exception as e:
            raise Exception(f"Failed to encrypt file: {e}")
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file
        
        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Optional output path. If None, removes .enc extension
            
        Returns:
            Path to decrypted file
        """
        if not output_path:
            if encrypted_file_path.endswith('.enc'):
                output_path = encrypted_file_path[:-4]
            else:
                output_path = encrypted_file_path + '.dec'
        
        try:
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return output_path
        except Exception as e:
            raise Exception(f"Failed to decrypt file: {e}")
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password for storage
        
        Args:
            password: Password to hash
            
        Returns:
            Hashed password string
        """
        salt = os.urandom(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return base64.urlsafe_b64encode(salt + pwdhash).decode('ascii')
    
    def verify_password(self, stored_password: str, provided_password: str) -> bool:
        """
        Verify a password against stored hash
        
        Args:
            stored_password: Stored hashed password
            provided_password: Password to verify
            
        Returns:
            True if password matches
        """
        try:
            stored = base64.urlsafe_b64decode(stored_password.encode('ascii'))
            salt = stored[:32]
            stored_hash = stored[32:]
            pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
            return pwdhash == stored_hash
        except:
            return False


class HealthDataEncryption:
    """Specialized encryption for health data with field-specific handling"""
    
    def __init__(self, password: Optional[str] = None):
        self.encryption = DataEncryption(password)
    
    def encrypt_health_entry(self, entry: dict) -> dict:
        """
        Encrypt a health log entry
        
        Args:
            entry: Health log entry dictionary
            
        Returns:
            Encrypted health log entry
        """
        # Create a copy to avoid modifying original
        encrypted_entry = entry.copy()
        
        # Encrypt sensitive fields
        sensitive_fields = ['symptoms', 'notes', 'medication_notes', 'allergy_info']
        
        for field in sensitive_fields:
            if field in encrypted_entry and encrypted_entry[field]:
                encrypted_entry[field] = self.encryption.encrypt_string(str(encrypted_entry[field]))
        
        # Add encryption flag
        encrypted_entry['_encrypted'] = True
        
        return encrypted_entry
    
    def decrypt_health_entry(self, entry: dict) -> dict:
        """
        Decrypt a health log entry
        
        Args:
            entry: Encrypted health log entry dictionary
            
        Returns:
            Decrypted health log entry
        """
        # Create a copy to avoid modifying original
        decrypted_entry = entry.copy()
        
        # Check if entry is encrypted
        if not decrypted_entry.get('_encrypted', False):
            return decrypted_entry
        
        # Decrypt sensitive fields
        sensitive_fields = ['symptoms', 'notes', 'medication_notes', 'allergy_info']
        
        for field in sensitive_fields:
            if field in decrypted_entry and decrypted_entry[field]:
                try:
                    decrypted_entry[field] = self.encryption.decrypt_string(str(decrypted_entry[field]))
                except:
                    # If decryption fails, keep original value
                    pass
        
        # Remove encryption flag
        decrypted_entry.pop('_encrypted', None)
        
        return decrypted_entry
    
    def encrypt_recipe_notes(self, recipe: dict) -> dict:
        """
        Encrypt sensitive fields in a recipe
        
        Args:
            recipe: Recipe dictionary
            
        Returns:
            Encrypted recipe dictionary
        """
        encrypted_recipe = recipe.copy()
        
        # Encrypt sensitive fields
        sensitive_fields = ['notes', 'allergy_warnings', 'dietary_restrictions']
        
        for field in sensitive_fields:
            if field in encrypted_recipe and encrypted_recipe[field]:
                encrypted_recipe[field] = self.encryption.encrypt_string(str(encrypted_recipe[field]))
        
        return encrypted_recipe
    
    def decrypt_recipe_notes(self, recipe: dict) -> dict:
        """
        Decrypt sensitive fields in a recipe
        
        Args:
            recipe: Encrypted recipe dictionary
            
        Returns:
            Decrypted recipe dictionary
        """
        decrypted_recipe = recipe.copy()
        
        # Decrypt sensitive fields
        sensitive_fields = ['notes', 'allergy_warnings', 'dietary_restrictions']
        
        for field in sensitive_fields:
            if field in decrypted_recipe and decrypted_recipe[field]:
                try:
                    decrypted_recipe[field] = self.encryption.decrypt_string(str(decrypted_recipe[field]))
                except:
                    # If decryption fails, keep original value
                    pass
        
        return decrypted_recipe


# Global encryption instances
_health_encryption = None
_general_encryption = None


def get_health_encryption(password: Optional[str] = None) -> HealthDataEncryption:
    """Get global health data encryption instance"""
    global _health_encryption
    if _health_encryption is None:
        _health_encryption = HealthDataEncryption(password)
    return _health_encryption


def get_general_encryption(password: Optional[str] = None) -> DataEncryption:
    """Get global general encryption instance"""
    global _general_encryption
    if _general_encryption is None:
        _general_encryption = DataEncryption(password)
    return _general_encryption
