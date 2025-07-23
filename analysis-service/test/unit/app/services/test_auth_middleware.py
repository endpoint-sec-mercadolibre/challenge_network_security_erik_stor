import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.services.auth_middleware import AuthMiddleware, auth_middleware


class TestAuthMiddleware:
    """Tests para la clase AuthMiddleware"""

    def setup_method(self):
        """Configuración antes de cada test"""
        # Crear mocks
        self.mock_auth_client = AsyncMock()
        self.mock_logger = MagicMock()
        
        # Patchear el logger global y las clases
        self.logger_patcher = patch('app.services.auth_middleware.logger', self.mock_logger)
        self.auth_client_patcher = patch('app.services.auth_middleware.AuthClient', return_value=self.mock_auth_client)
        
        self.logger_patcher.start()
        self.auth_client_patcher.start()
        
        # Crear instancia del middleware
        self.middleware = AuthMiddleware()
        
    def teardown_method(self):
        """Limpieza después de cada test"""
        self.logger_patcher.stop()
        self.auth_client_patcher.stop()

    def create_mock_request(self, path: str, method: str = "GET", headers: dict = None):
        """Función auxiliar para crear peticiones mock"""
        request = MagicMock(spec=Request)
        request.url.path = path
        request.method = method
        request.headers = headers or {}
        return request

    def test_auth_middleware_initialization(self):
        """Test que valida la inicialización del middleware"""
        assert self.middleware.auth_client is not None
        assert self.middleware.security is not None

    def test_requires_auth_public_paths(self):
        """Test que valida rutas públicas que no requieren autenticación"""
        public_paths = [
            "/health",
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/favicon.ico",
            "/swagger"
        ]
        
        for path in public_paths:
            assert not self.middleware._requires_auth(path), f"Path {path} should not require auth"

    def test_requires_auth_public_paths_with_subpaths(self):
        """Test que valida subpaths de rutas públicas"""
        public_subpaths = [
            "/docs/swagger",
            "/swagger/ui",
            "/health/check"
        ]
        
        for path in public_subpaths:
            assert not self.middleware._requires_auth(path), f"Path {path} should not require auth"

    def test_requires_auth_protected_paths(self):
        """Test que valida rutas protegidas que requieren autenticación"""
        protected_paths = [
            "/api/analysis",
            "/api/users",
            "/private",
            "/admin",
            "/",
            "/api"
        ]
        
        for path in protected_paths:
            assert self.middleware._requires_auth(path), f"Path {path} should require auth"

    def test_extract_token_from_header_valid(self):
        """Test que valida la extracción correcta de token"""
        auth_header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
        token = self.middleware._extract_token_from_header(auth_header)
        
        assert token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"

    def test_extract_token_from_header_none(self):
        """Test que valida el manejo de header None"""
        token = self.middleware._extract_token_from_header(None)
        assert token is None

    def test_extract_token_from_header_empty(self):
        """Test que valida el manejo de header vacío"""
        token = self.middleware._extract_token_from_header("")
        assert token is None

    def test_extract_token_from_header_invalid_format(self):
        """Test que valida el manejo de formato inválido"""
        invalid_headers = [
            "Basic token123",
            "token123",
            "Bearer",
            "Bearer ",
            "bearer token123"
        ]
        
        for header in invalid_headers:
            token = self.middleware._extract_token_from_header(header)
            if header == "Bearer ":
                assert token == ""  # Bearer seguido de espacio devuelve string vacío
            else:
                assert token is None, f"Header {header} should return None"

    @pytest.mark.asyncio
    async def test_validate_token_success(self):
        """Test que valida token válido"""
        self.mock_auth_client.validate_token.return_value = (True, {"user": "test"})
        
        result = await self.middleware._validate_token("valid_token")
        
        assert result is True
        self.mock_auth_client.validate_token.assert_called_once_with("valid_token")

    @pytest.mark.asyncio
    async def test_validate_token_invalid(self):
        """Test que valida token inválido"""
        self.mock_auth_client.validate_token.return_value = (False, None)
        
        result = await self.middleware._validate_token("invalid_token")
        
        assert result is False
        self.mock_auth_client.validate_token.assert_called_once_with("invalid_token")

    @pytest.mark.asyncio
    async def test_validate_token_exception(self):
        """Test que valida el manejo de excepciones en validación"""
        self.mock_auth_client.validate_token.side_effect = Exception("Auth service error")
        
        result = await self.middleware._validate_token("error_token")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_call_public_route(self):
        """Test que valida el manejo de rutas públicas"""
        request = self.create_mock_request("/health")
        
        result = await self.middleware(request, None)
        
        assert result == {"authenticated": False}
        self.mock_logger.set_context.assert_called_once_with(
            "AuthMiddleware", {"path": "/health", "method": "GET"}
        )
        self.mock_logger.info.assert_called_with("Ruta pública, saltando autenticación")

    @pytest.mark.asyncio
    async def test_call_protected_route_no_credentials_no_header(self):
        """Test que valida ruta protegida sin credenciales ni header"""
        request = self.create_mock_request("/api/protected")
        
        with pytest.raises(HTTPException) as exc_info:
            await self.middleware(request, None)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "TOKEN_REQUIRED"
        assert "Token de autenticación requerido" in exc_info.value.detail["message"]
        
        # Verificar logging
        self.mock_logger.error.assert_any_call("Token no proporcionado")

    @pytest.mark.asyncio
    async def test_call_protected_route_with_manual_header(self):
        """Test que valida ruta protegida con token en header manual"""
        headers = {"Authorization": "Bearer valid_token_123"}
        request = self.create_mock_request("/api/protected", headers=headers)
        
        # Configurar mock para token válido
        self.mock_auth_client.validate_token.return_value = (True, {"user": "test_user"})
        
        result = await self.middleware(request, None)
        
        expected_result = {
            "authenticated": True,
            "token": "valid_token_123",
            "user": "test_user"
        }
        assert result == expected_result
        
        # Verificar logging
        self.mock_logger.info.assert_any_call("Token encontrado en header Authorization manual")
        self.mock_logger.success.assert_called_with("Token validado correctamente")

    @pytest.mark.asyncio
    async def test_call_protected_route_with_credentials(self):
        """Test que valida ruta protegida con credenciales HTTPBearer"""
        request = self.create_mock_request("/api/protected")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="credentials_token")
        
        # Configurar mock para token válido
        self.mock_auth_client.validate_token.return_value = (True, {"user": "cred_user"})
        
        result = await self.middleware(request, credentials)
        
        expected_result = {
            "authenticated": True,
            "token": "credentials_token",
            "user": "cred_user"
        }
        assert result == expected_result
        
        # Verificar logging
        self.mock_logger.info.assert_any_call("Token obtenido de credentials")
        self.mock_logger.success.assert_called_with("Token validado correctamente")

    @pytest.mark.asyncio
    async def test_call_protected_route_invalid_token_credentials(self):
        """Test que valida ruta protegida con token inválido en credentials"""
        request = self.create_mock_request("/api/protected")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        
        # Configurar mock para token inválido
        self.mock_auth_client.validate_token.return_value = (False, None)
        
        with pytest.raises(HTTPException) as exc_info:
            await self.middleware(request, credentials)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "INVALID_TOKEN"
        assert "Token de autenticación inválido" in exc_info.value.detail["message"]
        
        # Verificar logging
        self.mock_logger.error.assert_any_call("Token inválido")

    @pytest.mark.asyncio
    async def test_call_protected_route_invalid_token_manual_header(self):
        """Test que valida ruta protegida con token inválido en header manual"""
        headers = {"Authorization": "Bearer invalid_token_123"}
        request = self.create_mock_request("/api/protected", headers=headers)
        
        # Configurar mock para token inválido
        self.mock_auth_client.validate_token.return_value = (False, None)
        
        with pytest.raises(HTTPException) as exc_info:
            await self.middleware(request, None)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_call_protected_route_auth_service_error(self):
        """Test que valida el manejo de errores del servicio de autenticación"""
        request = self.create_mock_request("/api/protected")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test_token")
        
        # Configurar mock para error del servicio
        self.mock_auth_client.validate_token.side_effect = Exception("Service unavailable")
        
        with pytest.raises(HTTPException) as exc_info:
            await self.middleware(request, credentials)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail["error_code"] == "AUTH_SERVICE_ERROR"
        assert "Error interno en validación de token" in exc_info.value.detail["message"]
        
        # Verificar logging
        self.mock_logger.error.assert_any_call("Error inesperado en validación de token: Service unavailable")

    @pytest.mark.asyncio
    async def test_call_protected_route_http_exception_passthrough(self):
        """Test que valida que las HTTPException se propagan correctamente"""
        request = self.create_mock_request("/api/protected")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test_token")
        
        # Configurar mock para lanzar HTTPException
        http_exception = HTTPException(status_code=403, detail="Forbidden")
        self.mock_auth_client.validate_token.side_effect = http_exception
        
        with pytest.raises(HTTPException) as exc_info:
            await self.middleware(request, credentials)
        
        # Debería propagar la misma excepción
        assert exc_info.value == http_exception
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_call_different_http_methods(self):
        """Test que valida diferentes métodos HTTP"""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        
        for method in methods:
            request = self.create_mock_request("/health", method=method)
            
            result = await self.middleware(request, None)
            
            assert result == {"authenticated": False}
            
            # Verificar que se configura el contexto con el método correcto
            context_calls = self.mock_logger.set_context.call_args_list
            # Buscar la llamada que corresponde a este método
            for call in context_calls:
                if call[0][1]["method"] == method:
                    assert call[0][1]["path"] == "/health"
                    break
            else:
                pytest.fail(f"No se encontró llamada de contexto para método {method}")

    @pytest.mark.asyncio
    async def test_call_various_public_paths(self):
        """Test que valida diferentes rutas públicas"""
        public_paths = [
            "/docs",
            "/docs/",
            "/swagger",
            "/swagger/ui",
            "/health/status",
            "/openapi.json"
        ]
        
        for path in public_paths:
            request = self.create_mock_request(path)
            
            result = await self.middleware(request, None)
            
            assert result == {"authenticated": False}, f"Path {path} should be public"

    @pytest.mark.asyncio
    async def test_call_manual_header_without_bearer(self):
        """Test que valida header manual sin formato Bearer"""
        headers = {"Authorization": "Basic dXNlcjpwYXNz"}  # Formato Basic
        request = self.create_mock_request("/api/protected", headers=headers)
        
        with pytest.raises(HTTPException) as exc_info:
            await self.middleware(request, None)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "TOKEN_REQUIRED"

    @pytest.mark.asyncio
    async def test_call_manual_header_bearer_empty_token(self):
        """Test que valida header Bearer con token vacío"""
        headers = {"Authorization": "Bearer "}
        request = self.create_mock_request("/api/protected", headers=headers)
        
        # Configurar mock para token vacío (debería ser inválido)
        self.mock_auth_client.validate_token.return_value = (False, None)
        
        with pytest.raises(HTTPException) as exc_info:
            await self.middleware(request, None)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_call_user_data_extraction(self):
        """Test que valida la extracción correcta de datos del usuario"""
        request = self.create_mock_request("/api/protected")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="user_token")
        
        # Configurar mock con datos completos del usuario
        user_data = {
            "user": {
                "id": 123,
                "username": "test_user",
                "email": "test@example.com",
                "roles": ["admin", "user"]
            },
            "permissions": ["read", "write"]
        }
        self.mock_auth_client.validate_token.return_value = (True, user_data)
        
        result = await self.middleware(request, credentials)
        
        expected_result = {
            "authenticated": True,
            "token": "user_token",
            "user": user_data["user"]
        }
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_call_user_data_missing(self):
        """Test que valida el manejo cuando faltan datos del usuario"""
        request = self.create_mock_request("/api/protected")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="minimal_token")
        
        # Configurar mock sin datos de usuario
        self.mock_auth_client.validate_token.return_value = (True, {})
        
        result = await self.middleware(request, credentials)
        
        expected_result = {
            "authenticated": True,
            "token": "minimal_token",
            "user": None  # get() debería devolver None
        }
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_error_detail_structure(self):
        """Test que valida la estructura de los detalles de error"""
        request = self.create_mock_request("/api/protected")
        
        # Test error TOKEN_REQUIRED
        with pytest.raises(HTTPException) as exc_info:
            await self.middleware(request, None)
        
        error_detail = exc_info.value.detail
        required_fields = ["success", "message", "error_code", "detail", "timestamp"]
        
        for field in required_fields:
            assert field in error_detail, f"Field {field} missing from error detail"
        
        assert error_detail["success"] is False
        assert error_detail["error_code"] == "TOKEN_REQUIRED"
        
        # Verificar que timestamp es llamado (el mock devuelve un MagicMock)
        # En el código real sería un string, pero en el test tenemos el mock
        self.mock_logger.get_timestamp.assert_called()

    @pytest.mark.asyncio
    async def test_timestamp_generation(self):
        """Test que valida la generación de timestamps en errores"""
        request = self.create_mock_request("/api/protected")
        
        # Configurar mock del timestamp
        self.mock_logger.get_timestamp.return_value = "2023-01-01T12:00:00Z"
        
        with pytest.raises(HTTPException) as exc_info:
            await self.middleware(request, None)
        
        assert exc_info.value.detail["timestamp"] == "2023-01-01T12:00:00Z"
        self.mock_logger.get_timestamp.assert_called()

    @pytest.mark.asyncio
    async def test_headers_logging_on_error(self):
        """Test que valida el logging de headers cuando hay error"""
        headers = {
            "User-Agent": "test-agent",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        request = self.create_mock_request("/api/protected", headers=headers)
        
        with pytest.raises(HTTPException):
            await self.middleware(request, None)
        
        # Verificar que se registraron los headers
        error_calls = [call.args[0] for call in self.mock_logger.error.call_args_list]
        headers_logged = False
        for call in error_calls:
            if "Headers disponibles:" in call:
                headers_logged = True
                break
        
        assert headers_logged, "Headers should be logged on error"


class TestAuthMiddlewareGlobalInstance:
    """Tests para la instancia global auth_middleware"""

    def test_global_instance_exists(self):
        """Test que valida que existe la instancia global"""
        assert auth_middleware is not None
        assert isinstance(auth_middleware, AuthMiddleware)

    def test_global_instance_is_singleton(self):
        """Test que valida que la instancia global es única"""
        from app.services.auth_middleware import auth_middleware as auth_middleware2
        
        # Ambas importaciones deberían referenciar la misma instancia
        assert auth_middleware is auth_middleware2

    def test_global_instance_has_auth_client(self):
        """Test que valida que la instancia global tiene auth_client"""
        assert auth_middleware.auth_client is not None

    def test_global_instance_has_security(self):
        """Test que valida que la instancia global tiene security"""
        assert auth_middleware.security is not None


class TestAuthMiddlewareEdgeCases:
    """Tests para casos límite y edge cases"""

    def setup_method(self):
        """Configuración antes de cada test"""
        # Crear mocks
        self.mock_auth_client = AsyncMock()
        self.mock_logger = MagicMock()
        
        # Patchear el logger global y las clases
        self.logger_patcher = patch('app.services.auth_middleware.logger', self.mock_logger)
        self.auth_client_patcher = patch('app.services.auth_middleware.AuthClient', return_value=self.mock_auth_client)
        
        self.logger_patcher.start()
        self.auth_client_patcher.start()
        
        # Crear instancia del middleware
        self.middleware = AuthMiddleware()
        
    def teardown_method(self):
        """Limpieza después de cada test"""
        self.logger_patcher.stop()
        self.auth_client_patcher.stop()

    def create_mock_request(self, path: str, method: str = "GET", headers: dict = None):
        """Función auxiliar para crear peticiones mock"""
        request = MagicMock(spec=Request)
        request.url.path = path
        request.method = method
        request.headers = headers or {}
        return request

    @pytest.mark.asyncio
    async def test_very_long_token(self):
        """Test que valida el manejo de tokens muy largos"""
        long_token = "a" * 10000
        request = self.create_mock_request("/api/protected")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=long_token)
        
        self.mock_auth_client.validate_token.return_value = (True, {"user": "test"})
        
        result = await self.middleware(request, credentials)
        
        assert result["token"] == long_token
        self.mock_auth_client.validate_token.assert_called_once_with(long_token)

    @pytest.mark.asyncio
    async def test_special_characters_in_token(self):
        """Test que valida el manejo de caracteres especiales en tokens"""
        special_token = "token.with-special_chars!@#$%^&*()+="
        request = self.create_mock_request("/api/protected")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=special_token)
        
        self.mock_auth_client.validate_token.return_value = (True, {"user": "test"})
        
        result = await self.middleware(request, credentials)
        
        assert result["token"] == special_token

    @pytest.mark.asyncio
    async def test_unicode_in_path(self):
        """Test que valida el manejo de caracteres Unicode en la ruta"""
        unicode_path = "/api/análisis/ñoño"
        request = self.create_mock_request(unicode_path)
        
        # Como es una ruta protegida sin token, debería fallar
        with pytest.raises(HTTPException):
            await self.middleware(request, None)

    def test_edge_case_paths(self):
        """Test que valida casos límite en rutas"""
        edge_cases = [
            ("/", True),  # Root path
            ("", True),  # Empty path actually requires auth in the real implementation
            ("/HEALTH", True),  # Case sensitive
            ("/health/", False),  # With trailing slash
            ("/healthcheck", False),  # Starts with /health, so doesn't require auth
            ("/docs-private", False),  # Starts with /docs, so doesn't require auth
            ("/api/docs", True),  # Different path that should require auth
        ]
        
        for path, should_require_auth in edge_cases:
            result = self.middleware._requires_auth(path)
            if should_require_auth:
                assert result, f"Path '{path}' should require auth"
            else:
                assert not result, f"Path '{path}' should not require auth" 