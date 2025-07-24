import pytest
import pytest_asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json
from datetime import datetime

# Configurar variables de entorno para testing
os.environ["ENVIRONMENT"] = "test"
os.environ["ENCRYPTION_KEY"] = "test_encryption_key"
os.environ["CONFIG_SERVICE_URL"] = "http://localhost:8000"
os.environ["GEMINI_API_KEY"] = "test_gemini_api_key"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test_db"
os.environ["AUTH_SERVICE_URL"] = "http://localhost:8001"

from app.main import app


@pytest.fixture
def client():
    """Cliente de prueba síncrono para FastAPI"""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client():
    """Cliente de prueba asíncrono para FastAPI"""
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture
def valid_auth_token():
    """Token de autenticación válido para pruebas"""
    return "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6OTk5OTk5OTk5OX0.test_signature"


@pytest.fixture
def invalid_auth_token():
    """Token de autenticación inválido para pruebas"""
    return "Bearer invalid_token_123"


@pytest.fixture
def mock_auth_result():
    """Resultado mock de autenticación exitosa"""
    return {
        "token": "test_token",
        "user": "testuser",
        "user_id": "test_user_id_123",
        "valid": True
    }


@pytest.fixture
def mock_file_content():
    """Contenido mock de archivo de configuración"""
    return """# Configuración de red de prueba
interface eth0
    address 192.168.1.100
    netmask 255.255.255.0
    gateway 192.168.1.1

# Configuración de firewall
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# DNS servers
nameserver 8.8.8.8
nameserver 8.8.4.4"""


@pytest.fixture
def mock_config_service_response():
    """Respuesta mock del servicio de configuración"""
    def _mock_response(encrypted_content: str = "dGVzdCBjb250ZW50"):
        return {
            "success": True,
            "message": "Configuración obtenida exitosamente",
            "data": {
                "filename": "test_config.txt",
                "content": encrypted_content,
                "size": 1024,
                "last_modified": "2024-01-01T00:00:00Z"
            }
        }
    return _mock_response


@pytest.fixture
def mock_gemini_response():
    """Respuesta mock de Google Gemini API"""
    return {
        "analysis_date": "2024-01-01T12:00:00Z",
        "safe": False,
        "problems": [
            {
                "problem": "Puerto SSH expuesto sin restricciones",
                "severity": "alta",
                "recommendation": "Configurar iptables para limitar acceso SSH a IPs específicas"
            },
            {
                "problem": "DNS público sin configuración de seguridad",
                "severity": "media",
                "recommendation": "Considerar usar DNS privado o configurar filtrado DNS"
            }
        ]
    }


@pytest.fixture
def mock_mongodb():
    """Mock para conexión MongoDB"""
    with patch('app.services.mongodb_service.mongodb_service') as mock_mongo:
        mock_mongo.connect.return_value = None
        mock_mongo.disconnect.return_value = None
        mock_mongo.is_connected.return_value = True
        yield mock_mongo


@pytest.fixture
def mock_analysis_repository():
    """Mock para el repositorio de análisis"""
    with patch('app.model.analysis_repository.AnalysisRepository') as mock_repo:
        mock_instance = Mock()
        mock_instance.save_analysis_record.return_value = {"id": "test_record_id"}
        mock_repo.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_auth_middleware():
    """Mock para el middleware de autenticación"""
    def _mock_auth_success(request):
        return {
            "authenticated": True,
            "token": "test_token",
            "user": "testuser"
        }
    
    # Mock tanto la clase como la función validate_token del AuthClient
    with patch('app.services.auth_client.AuthClient.validate_token') as mock_validate, \
         patch('app.services.auth_middleware.auth_middleware.__call__', side_effect=_mock_auth_success) as mock_middleware:
        
        # Configure el mock para validate_token
        mock_validate.return_value = (True, {"user": "testuser", "user_id": "test_user_id_123"})
        
        yield mock_middleware


@pytest.fixture
def mock_config_service():
    """Mock para llamadas al servicio de configuración"""
    # Mock específico para el método del usecase en lugar de httpx completo
    async def _mock_get_file_content(encrypted_filename, token=None):
        return """# Test network configuration
interface eth0
    address 192.168.1.100
    netmask 255.255.255.0
    gateway 192.168.1.1

# Firewall configuration
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# DNS servers
nameserver 8.8.8.8
nameserver 8.8.4.4"""
    
    with patch('app.usecase.analysis_usecase.AnalysisUseCase._get_file_content_from_config_service', side_effect=_mock_get_file_content) as mock_get:
        yield mock_get


@pytest.fixture
def mock_gemini_api():
    """Mock para Google Gemini API"""
    def _mock_generate_content(prompt, generation_config=None):
        mock_response = Mock()
        mock_response.text = json.dumps({
            "analysis_date": "2024-01-01T12:00:00Z",
            "safe": False,
            "problems": [
                {
                    "problem": "Puerto SSH expuesto sin restricciones",
                    "severity": "alta",
                    "recommendation": "Configurar iptables para limitar acceso SSH a IPs específicas"
                },
                {
                    "problem": "DNS público sin configuración de seguridad",
                    "severity": "media", 
                    "recommendation": "Considerar usar DNS privado o configurar filtrado DNS"
                }
            ]
        })
        return mock_response
    
    # Mock del método asíncrono _call_gemini_api directamente
    async def _mock_call_gemini_api(model, prompt):
        mock_response = Mock()
        mock_response.text = json.dumps({
            "analysis_date": "2024-01-01T12:00:00Z",
            "safe": False,
            "problems": [
                {
                    "problem": "Puerto SSH expuesto sin restricciones",
                    "severity": "alta",
                    "recommendation": "Configurar iptables para limitar acceso SSH a IPs específicas"
                },
                {
                    "problem": "DNS público sin configuración de seguridad",
                    "severity": "media", 
                    "recommendation": "Considerar usar DNS privado o configurar filtrado DNS"
                }
            ]
        })
        return mock_response
    
    with patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch('google.generativeai.configure') as mock_configure, \
         patch('app.usecase.analysis_usecase.AnalysisUseCase._call_gemini_api', side_effect=_mock_call_gemini_api) as mock_call:
        
        mock_model = Mock()
        mock_model.generate_content.side_effect = _mock_generate_content
        mock_model_class.return_value = mock_model
        
        yield mock_call


@pytest.fixture
def mock_encrypt_service():
    """Mock para el servicio de encriptación"""
    with patch('app.services.encrypt.Encrypt') as mock_encrypt_class:
        mock_encrypt = Mock()
        mock_encrypt.encrypt.return_value = "encrypted_filename_123"
        mock_encrypt.decrypt.return_value = "# Test network configuration\ninterface eth0"
        mock_encrypt.ofuscar_base64.return_value = "base64_filename_123"
        mock_encrypt.desofuscar_base64.return_value = "# Test network configuration\ninterface eth0"
        mock_encrypt_class.return_value = mock_encrypt
        yield mock_encrypt


@pytest.fixture
def mock_logger():
    """Mock para el sistema de logging"""
    with patch('app.services.logger.Logger') as mock_logger_class:
        mock_logger = Mock()
        mock_logger.set_context.return_value = None
        mock_logger.info.return_value = None
        mock_logger.error.return_value = None
        mock_logger.success.return_value = None
        mock_logger.warning.return_value = None
        mock_logger_class.return_value = mock_logger
        yield mock_logger 