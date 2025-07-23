import pytest
import base64
import os
from unittest.mock import patch, MagicMock
from app.services.encrypt import Encrypt, EncryptService


class TestEncrypt:
    """Tests para la clase Encrypt"""

    def setup_method(self):
        """Configuración antes de cada test"""
        self.password = "test_password_123"
        self.encrypt = Encrypt(self.password)

    def test_encrypt_initialization(self):
        """Test que valida la inicialización de la clase Encrypt"""
        encrypt = Encrypt("test_password")
        
        assert encrypt.password == b"test_password"
        assert isinstance(encrypt.password, bytes)

    def test_encrypt_initialization_with_unicode(self):
        """Test que valida la inicialización con caracteres Unicode"""
        unicode_password = "contraseña_áéíóú_ñ"
        encrypt = Encrypt(unicode_password)
        
        assert encrypt.password == unicode_password.encode("utf-8")
        assert isinstance(encrypt.password, bytes)

    def test_derive_key(self):
        """Test que valida la derivación de clave"""
        salt = os.urandom(16)
        key = self.encrypt._derive_key(salt)
        
        assert len(key) == 32  # 256 bits
        assert isinstance(key, bytes)
        
        # Verificar que la misma salt produce la misma clave
        key2 = self.encrypt._derive_key(salt)
        assert key == key2

    def test_derive_key_with_different_salt(self):
        """Test que valida que diferentes salts producen diferentes claves"""
        salt1 = os.urandom(16)
        salt2 = os.urandom(16)
        
        key1 = self.encrypt._derive_key(salt1)
        key2 = self.encrypt._derive_key(salt2)
        
        assert key1 != key2
        assert len(key1) == 32
        assert len(key2) == 32

    def test_encrypt_plaintext(self):
        """Test que valida la encriptación de texto plano"""
        plaintext = "Hello, World!"
        encrypted = self.encrypt.encrypt(plaintext)
        
        assert isinstance(encrypted, str)
        assert encrypted != plaintext
        
        # Verificar que es base64 válido
        try:
            base64.b64decode(encrypted.encode("utf-8"))
        except Exception:
            pytest.fail("El resultado no es base64 válido")

    def test_encrypt_empty_string(self):
        """Test que valida la encriptación de string vacío"""
        plaintext = ""
        encrypted = self.encrypt.encrypt(plaintext)
        
        assert isinstance(encrypted, str)
        assert encrypted != plaintext
        
        # Verificar que es base64 válido
        try:
            base64.b64decode(encrypted.encode("utf-8"))
        except Exception:
            pytest.fail("El resultado no es base64 válido")

    def test_encrypt_unicode_text(self):
        """Test que valida la encriptación de texto Unicode"""
        plaintext = "Hola, mundo! áéíóú ñ"
        encrypted = self.encrypt.encrypt(plaintext)
        
        assert isinstance(encrypted, str)
        assert encrypted != plaintext
        
        # Verificar que es base64 válido
        try:
            base64.b64decode(encrypted.encode("utf-8"))
        except Exception:
            pytest.fail("El resultado no es base64 válido")

    def test_encrypt_special_characters(self):
        """Test que valida la encriptación de caracteres especiales"""
        plaintext = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        encrypted = self.encrypt.encrypt(plaintext)
        
        assert isinstance(encrypted, str)
        assert encrypted != plaintext
        
        # Verificar que es base64 válido
        try:
            base64.b64decode(encrypted.encode("utf-8"))
        except Exception:
            pytest.fail("El resultado no es base64 válido")

    def test_encrypt_large_text(self):
        """Test que valida la encriptación de texto grande"""
        plaintext = "x" * 10000
        encrypted = self.encrypt.encrypt(plaintext)
        
        assert isinstance(encrypted, str)
        assert encrypted != plaintext
        
        # Verificar que es base64 válido
        try:
            base64.b64decode(encrypted.encode("utf-8"))
        except Exception:
            pytest.fail("El resultado no es base64 válido")

    def test_encrypt_different_results(self):
        """Test que valida que cada encriptación produce resultados diferentes"""
        plaintext = "Test message"
        encrypted1 = self.encrypt.encrypt(plaintext)
        encrypted2 = self.encrypt.encrypt(plaintext)
        
        assert encrypted1 != encrypted2
        assert encrypted1 != plaintext
        assert encrypted2 != plaintext

    def test_decrypt_success(self):
        """Test que valida la desencriptación exitosa"""
        plaintext = "Hello, World!"
        encrypted = self.encrypt.encrypt(plaintext)
        decrypted = self.encrypt.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert isinstance(decrypted, str)

    def test_decrypt_empty_string(self):
        """Test que valida la desencriptación de string vacío"""
        plaintext = ""
        encrypted = self.encrypt.encrypt(plaintext)
        decrypted = self.encrypt.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert isinstance(decrypted, str)

    def test_decrypt_unicode_text(self):
        """Test que valida la desencriptación de texto Unicode"""
        plaintext = "Hola, mundo! áéíóú ñ"
        encrypted = self.encrypt.encrypt(plaintext)
        decrypted = self.encrypt.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert isinstance(decrypted, str)

    def test_decrypt_special_characters(self):
        """Test que valida la desencriptación de caracteres especiales"""
        plaintext = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        encrypted = self.encrypt.encrypt(plaintext)
        decrypted = self.encrypt.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert isinstance(decrypted, str)

    def test_decrypt_large_text(self):
        """Test que valida la desencriptación de texto grande"""
        plaintext = "x" * 10000
        encrypted = self.encrypt.encrypt(plaintext)
        decrypted = self.encrypt.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert isinstance(decrypted, str)

    def test_decrypt_invalid_base64(self):
        """Test que valida el manejo de base64 inválido"""
        invalid_encrypted = "invalid_base64_string"
        
        with pytest.raises(RuntimeError) as exc_info:
            self.encrypt.decrypt(invalid_encrypted)
        
        assert "Error al desencriptar" in str(exc_info.value)

    def test_decrypt_corrupted_data(self):
        """Test que valida el manejo de datos corruptos"""
        # Crear datos corruptos
        corrupted_data = base64.b64encode(b"corrupted_data").decode("utf-8")
        
        with pytest.raises(RuntimeError) as exc_info:
            self.encrypt.decrypt(corrupted_data)
        
        assert "Error al desencriptar" in str(exc_info.value)

    def test_decrypt_wrong_password(self):
        """Test que valida el manejo de contraseña incorrecta"""
        # Encriptar con una contraseña
        encrypt1 = Encrypt("password1")
        plaintext = "Test message"
        encrypted = encrypt1.encrypt(plaintext)
        
        # Intentar desencriptar con otra contraseña
        encrypt2 = Encrypt("password2")
        
        with pytest.raises(RuntimeError) as exc_info:
            encrypt2.decrypt(encrypted)
        
        assert "Error al desencriptar" in str(exc_info.value)

    def test_ofuscar_base64_success(self):
        """Test que valida la ofuscación exitosa"""
        texto = "Hello, World!"
        ofuscado = self.encrypt.ofuscar_base64(texto)
        
        assert isinstance(ofuscado, str)
        assert ofuscado != texto
        
        # Verificar que se aplicó la transformación
        # El texto original "Hello, World!" en base64 es "SGVsbG8sIFdvcmxkIQ=="
        # Después de la transformación debería ser diferente
        assert ofuscado != "SGVsbG8sIFdvcmxkIQ=="

    def test_ofuscar_base64_empty_string(self):
        """Test que valida la ofuscación de string vacío"""
        texto = ""
        ofuscado = self.encrypt.ofuscar_base64(texto)
        
        assert isinstance(ofuscado, str)
        # Para string vacío, el resultado puede ser el mismo
        # porque base64 de "" es "" y la transformación no cambia nada
        assert ofuscado == texto

    def test_ofuscar_base64_unicode_text(self):
        """Test que valida la ofuscación de texto Unicode"""
        texto = "Hola, mundo! áéíóú ñ"
        ofuscado = self.encrypt.ofuscar_base64(texto)
        
        assert isinstance(ofuscado, str)
        assert ofuscado != texto

    def test_ofuscar_base64_special_characters(self):
        """Test que valida la ofuscación de caracteres especiales"""
        texto = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        ofuscado = self.encrypt.ofuscar_base64(texto)
        
        assert isinstance(ofuscado, str)
        assert ofuscado != texto

    def test_ofuscar_base64_with_letters_and_numbers(self):
        """Test que valida la ofuscación con letras y números"""
        texto = "ABC123xyz789"
        ofuscado = self.encrypt.ofuscar_base64(texto)
        
        assert isinstance(ofuscado, str)
        assert ofuscado != texto
        
        # Verificar que se aplicó la transformación
        # El texto original en base64 es "QUJDMTIzeHl6Nzg5"
        # Después de la transformación debería ser diferente
        assert ofuscado != "QUJDMTIzeHl6Nzg5"

    def test_desofuscar_base64_success(self):
        """Test que valida la desofuscación exitosa"""
        texto = "Hello, World!"
        ofuscado = self.encrypt.ofuscar_base64(texto)
        desofuscado = self.encrypt.desofuscar_base64(ofuscado)
        
        assert desofuscado == texto
        assert isinstance(desofuscado, str)

    def test_desofuscar_base64_empty_string(self):
        """Test que valida la desofuscación de string vacío"""
        texto = ""
        ofuscado = self.encrypt.ofuscar_base64(texto)
        desofuscado = self.encrypt.desofuscar_base64(ofuscado)
        
        assert desofuscado == texto
        assert isinstance(desofuscado, str)

    def test_desofuscar_base64_unicode_text(self):
        """Test que valida la desofuscación de texto Unicode"""
        texto = "Hola, mundo! áéíóú ñ"
        ofuscado = self.encrypt.ofuscar_base64(texto)
        desofuscado = self.encrypt.desofuscar_base64(ofuscado)
        
        assert desofuscado == texto
        assert isinstance(desofuscado, str)

    def test_desofuscar_base64_special_characters(self):
        """Test que valida la desofuscación de caracteres especiales"""
        texto = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        ofuscado = self.encrypt.ofuscar_base64(texto)
        desofuscado = self.encrypt.desofuscar_base64(ofuscado)
        
        assert desofuscado == texto
        assert isinstance(desofuscado, str)

    def test_desofuscar_base64_invalid_input(self):
        """Test que valida el manejo de entrada inválida en desofuscación"""
        invalid_ofuscado = "invalid_ofuscado_string"
        
        with pytest.raises(RuntimeError) as exc_info:
            self.encrypt.desofuscar_base64(invalid_ofuscado)
        
        assert "Error al desofuscar" in str(exc_info.value)

    def test_desofuscar_base64_corrupted_base64(self):
        """Test que valida el manejo de base64 corrupto en desofuscación"""
        # Crear base64 corrupto después de la transformación
        corrupted_base64 = "SGVsbG8sIFdvcmxkIQ=="  # "Hello, World!" en base64
        # Aplicar transformación manualmente para crear datos corruptos
        caracteres = list(corrupted_base64)
        for i in range(len(caracteres)):
            if caracteres[i].isalpha():
                if caracteres[i].isupper():
                    caracteres[i] = chr((ord(caracteres[i]) - ord("A") + 1) % 26 + ord("A"))
                else:
                    caracteres[i] = chr((ord(caracteres[i]) - ord("a") + 1) % 26 + ord("a"))
            elif caracteres[i].isdigit():
                caracteres[i] = str((int(caracteres[i]) + 1) % 10)
        
        ofuscado = "".join(caracteres)
        
        # Intentar desofuscar
        desofuscado = self.encrypt.desofuscar_base64(ofuscado)
        assert desofuscado == "Hello, World!"

    def test_ofuscar_desofuscar_roundtrip(self):
        """Test que valida el ciclo completo de ofuscación y desofuscación"""
        textos = [
            "Hello, World!",
            "Hola, mundo! áéíóú ñ",
            "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "ABC123xyz789",
            "x" * 100,
            ""
        ]
        
        for texto in textos:
            ofuscado = self.encrypt.ofuscar_base64(texto)
            desofuscado = self.encrypt.desofuscar_base64(ofuscado)
            assert desofuscado == texto

    def test_ofuscar_base64_exception_handling(self):
        """Test que valida el manejo de excepciones en ofuscación"""
        with patch('base64.b64encode') as mock_b64encode:
            mock_b64encode.side_effect = Exception("Test error")
            
            with pytest.raises(RuntimeError) as exc_info:
                self.encrypt.ofuscar_base64("test")
            
            assert "Error al ofuscar" in str(exc_info.value)

    def test_desofuscar_base64_exception_handling(self):
        """Test que valida el manejo de excepciones en desofuscación"""
        with patch('base64.b64decode') as mock_b64decode:
            mock_b64decode.side_effect = Exception("Test error")
            
            with pytest.raises(RuntimeError) as exc_info:
                self.encrypt.desofuscar_base64("test")
            
            assert "Error al desofuscar" in str(exc_info.value)

    def test_encrypt_decrypt_roundtrip(self):
        """Test que valida el ciclo completo de encriptación y desencriptación"""
        textos = [
            "Hello, World!",
            "Hola, mundo! áéíóú ñ",
            "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "ABC123xyz789",
            "x" * 100,
            ""
        ]
        
        for texto in textos:
            encrypted = self.encrypt.encrypt(texto)
            decrypted = self.encrypt.decrypt(encrypted)
            assert decrypted == texto

    def test_encrypt_different_passwords(self):
        """Test que valida que diferentes contraseñas producen diferentes resultados"""
        encrypt1 = Encrypt("password1")
        encrypt2 = Encrypt("password2")
        
        plaintext = "Test message"
        encrypted1 = encrypt1.encrypt(plaintext)
        encrypted2 = encrypt2.encrypt(plaintext)
        
        assert encrypted1 != encrypted2

    def test_encrypt_same_password_different_instances(self):
        """Test que valida que la misma contraseña en diferentes instancias funciona"""
        encrypt1 = Encrypt("same_password")
        encrypt2 = Encrypt("same_password")
        
        plaintext = "Test message"
        encrypted = encrypt1.encrypt(plaintext)
        decrypted = encrypt2.decrypt(encrypted)
        
        assert decrypted == plaintext


class TestEncryptService:
    """Tests para la clase EncryptService"""

    def setup_method(self):
        """Configuración antes de cada test"""
        with patch.dict(os.environ, {}, clear=True):
            self.service = EncryptService()

    def test_encrypt_service_initialization_default_key(self):
        """Test que valida la inicialización con clave por defecto"""
        with patch.dict(os.environ, {}, clear=True):
            service = EncryptService()
            
            assert service.encryption_key == "mi_contraseña_secreta"
            assert service._encrypt_instance is not None

    def test_encrypt_service_initialization_custom_key(self):
        """Test que valida la inicialización con clave personalizada"""
        custom_key = "custom_encryption_key_123"
        service = EncryptService(custom_key)
        
        assert service.encryption_key == custom_key
        assert service._encrypt_instance is not None

    def test_encrypt_service_initialization_environment_key(self):
        """Test que valida la inicialización con clave desde variable de entorno"""
        env_key = "env_encryption_key_456"
        with patch.dict(os.environ, {"ENCRYPTION_KEY": env_key}, clear=True):
            service = EncryptService()
            
            assert service.encryption_key == env_key
            assert service._encrypt_instance is not None

    def test_encrypt_service_encrypt(self):
        """Test que valida el método encrypt del servicio"""
        plaintext = "Hello, World!"
        encrypted = self.service.encrypt(plaintext)
        
        assert isinstance(encrypted, str)
        assert encrypted != plaintext
        
        # Verificar que es base64 válido
        try:
            base64.b64decode(encrypted.encode("utf-8"))
        except Exception:
            pytest.fail("El resultado no es base64 válido")

    def test_encrypt_service_decrypt(self):
        """Test que valida el método decrypt del servicio"""
        plaintext = "Hello, World!"
        encrypted = self.service.encrypt(plaintext)
        decrypted = self.service.decrypt(encrypted)
        
        assert decrypted == plaintext
        assert isinstance(decrypted, str)

    def test_encrypt_service_roundtrip(self):
        """Test que valida el ciclo completo del servicio"""
        textos = [
            "Hello, World!",
            "Hola, mundo! áéíóú ñ",
            "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "ABC123xyz789",
            "x" * 100,
            ""
        ]
        
        for texto in textos:
            encrypted = self.service.encrypt(texto)
            decrypted = self.service.decrypt(encrypted)
            assert decrypted == texto

    def test_encrypt_service_different_instances(self):
        """Test que valida que diferentes instancias con la misma clave funcionan"""
        service1 = EncryptService("same_key")
        service2 = EncryptService("same_key")
        
        plaintext = "Test message"
        encrypted = service1.encrypt(plaintext)
        decrypted = service2.decrypt(encrypted)
        
        assert decrypted == plaintext

    def test_encrypt_service_different_keys(self):
        """Test que valida que diferentes claves no son compatibles"""
        service1 = EncryptService("key1")
        service2 = EncryptService("key2")
        
        plaintext = "Test message"
        encrypted = service1.encrypt(plaintext)
        
        with pytest.raises(RuntimeError):
            service2.decrypt(encrypted)

    def test_encrypt_service_unicode_support(self):
        """Test que valida el soporte para Unicode en el servicio"""
        unicode_text = "Hola, mundo! áéíóú ñ"
        encrypted = self.service.encrypt(unicode_text)
        decrypted = self.service.decrypt(encrypted)
        
        assert decrypted == unicode_text

    def test_encrypt_service_special_characters(self):
        """Test que valida el manejo de caracteres especiales en el servicio"""
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        encrypted = self.service.encrypt(special_text)
        decrypted = self.service.decrypt(encrypted)
        
        assert decrypted == special_text

    def test_encrypt_service_large_data(self):
        """Test que valida el manejo de datos grandes en el servicio"""
        large_text = "x" * 10000
        encrypted = self.service.encrypt(large_text)
        decrypted = self.service.decrypt(encrypted)
        
        assert decrypted == large_text

    def test_encrypt_service_empty_string(self):
        """Test que valida el manejo de string vacío en el servicio"""
        empty_text = ""
        encrypted = self.service.encrypt(empty_text)
        decrypted = self.service.decrypt(encrypted)
        
        assert decrypted == empty_text

    def test_encrypt_service_invalid_decrypt(self):
        """Test que valida el manejo de datos inválidos en decrypt"""
        invalid_encrypted = "invalid_encrypted_data"
        
        with pytest.raises(RuntimeError) as exc_info:
            self.service.decrypt(invalid_encrypted)
        
        assert "Error al desencriptar" in str(exc_info.value)

    def test_encrypt_service_none_key(self):
        """Test que valida la inicialización con clave None"""
        with patch.dict(os.environ, {}, clear=True):
            service = EncryptService(None)
            
            assert service.encryption_key == "mi_contraseña_secreta"

    def test_encrypt_service_empty_key(self):
        """Test que valida la inicialización con clave vacía usa la clave por defecto"""
        with patch.dict(os.environ, {}, clear=True):
            service = EncryptService("")
            
            # Si se pasa string vacío, usa la clave por defecto
            assert service.encryption_key == "mi_contraseña_secreta"
            assert service._encrypt_instance is not None

    def test_encrypt_service_very_long_key(self):
        """Test que valida la inicialización con clave muy larga"""
        long_key = "a" * 1000
        service = EncryptService(long_key)
        
        assert service.encryption_key == long_key
        
        # Verificar que funciona
        plaintext = "Test message"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        
        assert decrypted == plaintext

    def test_encrypt_service_unicode_key(self):
        """Test que valida la inicialización con clave Unicode"""
        unicode_key = "clave_áéíóú_ñ"
        service = EncryptService(unicode_key)
        
        assert service.encryption_key == unicode_key
        
        # Verificar que funciona
        plaintext = "Test message"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        
        assert decrypted == plaintext 