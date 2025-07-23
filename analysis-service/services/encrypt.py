import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class Encrypt:
    def __init__(self, password):
        """
        Inicializa el cifrador AES con una contraseña.
        
        Args:
            password (str): Contraseña para derivar la clave de cifrado
        """
        self.password = password.encode('utf-8')
    
    def _derive_key(self, salt):
        """
        Deriva una clave de 256 bits usando PBKDF2.
        
        Args:
            salt (bytes): Salt para la derivación de clave
            
        Returns:
            bytes: Clave derivada de 32 bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(self.password)
    
    def encrypt(self, plaintext):
        """
        Encripta el texto usando AES-256-GCM.
        
        Args:
            plaintext (str): Texto a encriptar
            
        Returns:
            str: Texto encriptado codificado en base64
        """
        # Generar salt e IV aleatorios
        salt = os.urandom(16)  # 128 bits
        iv = os.urandom(12)    # 96 bits para GCM
        
        # Derivar clave
        key = self._derive_key(salt)
        
        # Configurar cifrador
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        
        # Encriptar
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()
        
        # Combinar: salt (16) + iv (12) + tag (16) + ciphertext
        encrypted_data = salt + iv + encryptor.tag + ciphertext
        
        # Codificar en base64
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data):
        """
        Desencripta el texto usando AES-256-GCM.
        
        Args:
            encrypted_data (str): Texto encriptado codificado en base64
            
        Returns:
            str: Texto desencriptado
            
        Raises:
            Exception: Si la desencriptación falla
        """
        try:
            # Decodificar base64
            data = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Extraer componentes
            salt = data[:16]           # Primeros 16 bytes
            iv = data[16:28]          # Siguientes 12 bytes
            tag = data[28:44]         # Siguientes 16 bytes
            ciphertext = data[44:]    # Resto
            
            # Derivar clave
            key = self._derive_key(salt)
            
            # Configurar descifrador
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()
            
            # Desencriptar
            plaintext_bytes = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext_bytes.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error al desencriptar: {str(e)}")

    def ofuscar_base64(self, texto):
        """
        Ofusca un string convirtiéndolo a base64 y aplicando una transformación adicional.
        
        Args:
            texto (str): Texto a ofuscar
            
        Returns:
            str: Texto ofuscado
        """
        try:
            # Convertir a base64
            texto_bytes = texto.encode('utf-8')
            base64_texto = base64.b64encode(texto_bytes).decode('utf-8')
            
            # Aplicar transformación adicional: rotar caracteres
            caracteres = list(base64_texto)
            for i in range(len(caracteres)):
                if caracteres[i].isalpha():
                    # Rotar letras: A->B, B->C, ..., Z->A
                    if caracteres[i].isupper():
                        caracteres[i] = chr((ord(caracteres[i]) - ord('A') + 1) % 26 + ord('A'))
                    else:
                        caracteres[i] = chr((ord(caracteres[i]) - ord('a') + 1) % 26 + ord('a'))
                elif caracteres[i].isdigit():
                    # Rotar números: 0->1, 1->2, ..., 9->0
                    caracteres[i] = str((int(caracteres[i]) + 1) % 10)
            
            return ''.join(caracteres)
            
        except Exception as e:
            raise Exception(f"Error al ofuscar: {str(e)}")
    
    def desofuscar_base64(self, texto_ofuscado):
        """
        Desofusca un string que fue ofuscado con ofuscar_base64().
        
        Args:
            texto_ofuscado (str): Texto ofuscado a desofuscar
            
        Returns:
            str: Texto original desofuscado
            
        Raises:
            Exception: Si la desofuscación falla
        """
        try:
            # Revertir la transformación: rotar caracteres en dirección opuesta
            caracteres = list(texto_ofuscado)
            for i in range(len(caracteres)):
                if caracteres[i].isalpha():
                    # Rotar letras en dirección opuesta: B->A, C->B, ..., A->Z
                    if caracteres[i].isupper():
                        caracteres[i] = chr((ord(caracteres[i]) - ord('A') - 1) % 26 + ord('A'))
                    else:
                        caracteres[i] = chr((ord(caracteres[i]) - ord('a') - 1) % 26 + ord('a'))
                elif caracteres[i].isdigit():
                    # Rotar números en dirección opuesta: 1->0, 2->1, ..., 0->9
                    caracteres[i] = str((int(caracteres[i]) - 1) % 10)
            
            texto_base64 = ''.join(caracteres)
            
            # Decodificar base64
            texto_bytes = base64.b64decode(texto_base64.encode('utf-8'))
            return texto_bytes.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Error al desofuscar: {str(e)}")
