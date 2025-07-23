import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import json

from app.main import (
    app,
    health_check,
    _add_basic_openapi_info,
    _is_public_path,
    _is_http_method,
    _add_security_to_method,
    _apply_security_to_paths,
    custom_openapi
)


class TestMain:
    """Tests para el módulo main"""

    def test_app_creation(self):
        """Test que valida la creación de la aplicación FastAPI"""
        assert app is not None
        assert app.title == "Analysis Service API"
        assert app.version == "1.0.0"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"

    def test_health_endpoint(self):
        """Test del endpoint de salud"""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "analysis-service"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_health_check_function(self):
        """Test de la función health_check directamente"""
        result = await health_check()
        
        assert result["status"] == "healthy"
        assert result["service"] == "analysis-service"
        assert result["version"] == "1.0.0"
        assert "timestamp" in result

    def test_is_public_path(self):
        """Test de la función _is_public_path"""
        # Rutas públicas
        assert _is_public_path("/health") is True
        assert _is_public_path("/docs") is True
        assert _is_public_path("/redoc") is True
        assert _is_public_path("/openapi.json") is True
        assert _is_public_path("/favicon.ico") is True
        
        # Rutas privadas
        assert _is_public_path("/api/v1/analyze") is False
        assert _is_public_path("/private") is False
        assert _is_public_path("/admin") is False

    def test_is_http_method(self):
        """Test de la función _is_http_method"""
        # Métodos HTTP válidos
        assert _is_http_method("get") is True
        assert _is_http_method("POST") is True
        assert _is_http_method("put") is True
        assert _is_http_method("DELETE") is True
        assert _is_http_method("patch") is True
        
        # Métodos inválidos
        assert _is_http_method("invalid") is False
        assert _is_http_method("connect") is False
        assert _is_http_method("trace") is False

    def test_add_security_to_method(self):
        """Test de la función _add_security_to_method"""
        # Método sin seguridad
        path_method = {}
        _add_security_to_method(path_method)
        assert "security" in path_method
        assert {"bearerAuth": []} in path_method["security"]
        
        # Método con seguridad existente pero sin bearerAuth
        path_method = {"security": [{"apiKey": []}]}
        _add_security_to_method(path_method)
        assert len(path_method["security"]) == 2
        assert {"bearerAuth": []} in path_method["security"]
        
        # Método ya con bearerAuth
        path_method = {"security": [{"bearerAuth": []}]}
        _add_security_to_method(path_method)
        assert len(path_method["security"]) == 1

    def test_add_basic_openapi_info(self):
        """Test de la función _add_basic_openapi_info"""
        openapi_schema = {
            "info": {},
            "components": {}
        }
        
        _add_basic_openapi_info(openapi_schema)
        
        assert "contact" in openapi_schema["info"]
        assert "license" in openapi_schema["info"]
        assert "securitySchemes" in openapi_schema["components"]

    def test_apply_security_to_paths(self):
        """Test de la función _apply_security_to_paths"""
        openapi_schema = {
            "paths": {
                "/health": {
                    "get": {"summary": "Health check"}
                },
                "/api/analyze": {
                    "post": {"summary": "Analyze file"},
                    "get": {"summary": "Get analysis"}
                },
                "/docs": {
                    "get": {"summary": "Documentation"}
                }
            }
        }
        
        _apply_security_to_paths(openapi_schema)
        
        # Ruta pública no debe tener seguridad
        assert "security" not in openapi_schema["paths"]["/health"]["get"]
        assert "security" not in openapi_schema["paths"]["/docs"]["get"]
        
        # Ruta privada debe tener seguridad
        assert "security" in openapi_schema["paths"]["/api/analyze"]["post"]
        assert "security" in openapi_schema["paths"]["/api/analyze"]["get"]
        assert {"bearerAuth": []} in openapi_schema["paths"]["/api/analyze"]["post"]["security"]

    @patch('app.main.get_openapi')
    def test_custom_openapi(self, mock_get_openapi):
        """Test de la función custom_openapi"""
        # Configurar mock
        mock_get_openapi.return_value = {
            "info": {},
            "components": {},
            "paths": {
                "/test": {
                    "get": {"summary": "Test endpoint"}
                }
            }
        }
        
        # Limpiar el schema existente
        app.openapi_schema = None
        
        result = custom_openapi()
        
        assert result is not None
        assert "info" in result
        assert "components" in result
        assert "security" in result
        assert result["security"] == [{"bearerAuth": []}]
        
        # Segunda llamada debe retornar el schema cacheado
        result2 = custom_openapi()
        assert result2 is result

    @patch('app.main.mongodb_service.connect')
    @patch('builtins.print')
    def test_startup_event_success(self, mock_print, mock_connect):
        """Test del evento startup exitoso"""
        import asyncio
        from app.main import startup_event
        
        mock_connect.return_value = None
        
        # Ejecutar evento startup
        asyncio.run(startup_event())
        
        mock_connect.assert_called_once()
        mock_print.assert_called_with("✅ Conexión a MongoDB establecida exitosamente")

    @patch('app.main.mongodb_service.connect')
    @patch('builtins.print')
    def test_startup_event_failure(self, mock_print, mock_connect):
        """Test del evento startup con error"""
        import asyncio
        from app.main import startup_event
        
        mock_connect.side_effect = Exception("Connection failed")
        
        # Ejecutar evento startup
        asyncio.run(startup_event())
        
        mock_connect.assert_called_once()
        mock_print.assert_called_with("❌ Error al conectar a MongoDB: Connection failed")

    @patch('app.main.mongodb_service.disconnect')
    @patch('builtins.print')
    def test_shutdown_event_success(self, mock_print, mock_disconnect):
        """Test del evento shutdown exitoso"""
        import asyncio
        from app.main import shutdown_event
        
        mock_disconnect.return_value = None
        
        # Ejecutar evento shutdown
        asyncio.run(shutdown_event())
        
        mock_disconnect.assert_called_once()
        mock_print.assert_called_with("✅ Conexión a MongoDB cerrada exitosamente")

    @patch('app.main.mongodb_service.disconnect')
    @patch('builtins.print')
    def test_shutdown_event_failure(self, mock_print, mock_disconnect):
        """Test del evento shutdown con error"""
        import asyncio
        from app.main import shutdown_event
        
        mock_disconnect.side_effect = Exception("Disconnect failed")
        
        # Ejecutar evento shutdown
        asyncio.run(shutdown_event())
        
        mock_disconnect.assert_called_once()
        mock_print.assert_called_with("❌ Error al cerrar conexión a MongoDB: Disconnect failed") 