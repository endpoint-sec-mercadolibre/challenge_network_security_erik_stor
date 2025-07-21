import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import hashlib

class Encrypt:
    """Clase para manejar operaciones de encriptación compatibles con config-service"""
    
    def __init__(self):
        # Usar la misma clave secreta que config-service
        self.secret_key = os.getenv('ENCRYPTION_KEY', 'default-secret-key-32-chars-long')
        # Asegurar que la clave tenga 32 bytes para AES-256
        self.secret_key = hashlib.sha256(self.secret_key.encode()).digest()
    
    def to_base64(self, text: str) -> str:
        """
        Convierte un string a base64
        
        Args:
            text: Texto a convertir
            
        Returns:
            str: String codificado en base64
        """
        try:
            return base64.b64encode(text.encode('utf-8')).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error al convertir a base64: {e}")
    
    def from_base64(self, base64_text: str) -> str:
        """
        Decodifica un string desde base64
        
        Args:
            base64_text: Texto en base64
            
        Returns:
            str: String decodificado
        """
        try:
            return base64.b64decode(base64_text.encode('utf-8')).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error al decodificar desde base64: {e}")
    
    def encrypt_aes(self, text: str) -> str:
        """
        Encripta un string usando AES-256-CBC
        
        Args:
            text: Texto a encriptar
            
        Returns:
            str: String encriptado
        """
        try:
            # Generar IV aleatorio
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            
            # Crear IV usando la clave
            iv = hashlib.md5(self.secret_key).digest()
            
            # Crear cipher
            cipher = Cipher(
                algorithms.AES(self.secret_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            # Encriptar
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(128).padder()
            
            padded_data = padder.update(text.encode('utf-8')) + padder.finalize()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Convertir a base64 para almacenamiento seguro
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error al encriptar con AES: {e}")
    
    def decrypt_aes(self, encrypted_text: str) -> str:
        """
        Desencripta un string usando AES-256-CBC
        
        Args:
            encrypted_text: Texto encriptado
            
        Returns:
            str: String desencriptado
        """
        try:
            # Decodificar de base64
            encrypted_data = base64.b64decode(encrypted_text.encode('utf-8'))
            
            # Crear IV usando la clave
            iv = hashlib.md5(self.secret_key).digest()
            
            # Crear cipher
            cipher = Cipher(
                algorithms.AES(self.secret_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            # Desencriptar
            decryptor = cipher.decryptor()
            unpadder = padding.PKCS7(128).unpadder()
            
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
            
            return unpadded_data.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error al desencriptar con AES: {e}")
    
    def to_base64_and_encrypt(self, text: str) -> str:
        """
        Convierte un string a base64 y luego lo encripta con AES
        (Mismo algoritmo que config-service)
        
        Args:
            text: Texto a procesar
            
        Returns:
            str: String convertido a base64 y encriptado
        """
        try:
            encrypted = self.encrypt_aes(text)
            return self.to_base64(encrypted)
        except Exception as e:
            raise Exception(f"Error al convertir a base64 y encriptar: {e}")
    
    def decrypt_and_from_base64(self, encrypted_text: str) -> str:
        """
        Desencripta un string y luego lo decodifica desde base64
        (Mismo algoritmo que config-service)
        
        Args:
            encrypted_text: Texto encriptado
            
        Returns:
            str: String desencriptado y decodificado desde base64
        """
        try:
            decrypted_text = self.from_base64(encrypted_text)
            return self.decrypt_aes(decrypted_text)
        except Exception as e:
            raise Exception(f"Error al desencriptar y decodificar desde base64: {e}")
    
    def is_valid_base64(self, text: str) -> bool:
        """
        Valida si un string es válido en base64
        
        Args:
            text: Texto a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        try:
            base64.b64decode(text)
            return True
        except Exception:
            return False 