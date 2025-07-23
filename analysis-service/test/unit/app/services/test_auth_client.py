import pytest
import os
import aiohttp
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.auth_client import AuthClient


class MockResponse:
    """Mock personalizado para respuestas HTTP"""
    def __init__(self, status, json_data=None, text_data=None, raise_json_error=False, raise_text_error=False):
        self.status = status
        self._json_data = json_data
        self._text_data = text_data
        self._raise_json_error = raise_json_error
        self._raise_text_error = raise_text_error

    async def json(self):
        if self._raise_json_error:
            raise Exception("JSON parse error")
        return self._json_data

    async def text(self):
        if self._raise_text_error:
            raise Exception("Text read error")
        return self._text_data


class MockSession:
    """Mock personalizado para sesión HTTP"""
    def __init__(self, response):
        self.response = response
        self.post_calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def post(self, url, json=None):
        self.post_calls.append((url, json))
        return MockResponseContext(self.response)


class MockResponseContext:
    """Mock personalizado para el context manager de respuesta"""
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class TestAuthClient:
    """Tests para el cliente de autenticación"""

    def setup_method(self):
        """Configuración antes de cada test"""
        with patch("app.services.auth_client.Logger") as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            self.client = AuthClient()
            self.client.logger = mock_logger

    def test_auth_client_initialization(self):
        """Test que valida la inicialización del cliente"""
        with patch("app.services.auth_client.Logger") as mock_logger_class:
            client = AuthClient()

            assert client.logger is not None
            assert client.auth_service_url == "http://localhost:8001"
            assert client.timeout.total == 10
            mock_logger_class.assert_called_once()

    def test_auth_client_initialization_with_custom_url(self):
        """Test que valida la inicialización con URL personalizada"""
        with patch.dict(
            os.environ, {"AUTH_SERVICE_URL": "http://custom-auth:9000"}, clear=True
        ), patch("app.services.auth_client.Logger"):
            client = AuthClient()

            assert client.auth_service_url == "http://custom-auth:9000"

    @pytest.mark.asyncio
    async def test_validate_token_success(self):
        """Test que valida un token exitosamente"""
        token = "valid.jwt.token"
        mock_response_data = {
            "valid": True,
            "user": {"id": 123, "username": "test_user"},
            "exp": 1234567890,
        }

        mock_response = MockResponse(200, json_data=mock_response_data)
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "success"
        ) as mock_success, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is True
            assert data == mock_response_data

            # Verificar que se configuró el contexto
            mock_set_context.assert_called_once_with(
                "AuthClient.validate_token",
                {
                    "token_length": len(token),
                    "auth_service_url": self.client.auth_service_url,
                },
            )

            # Verificar logs
            mock_info.assert_any_call("Validando token con servicio de autenticación")
            mock_info.assert_any_call("Respuesta del servicio de autenticación: 200")
            mock_success.assert_called_once_with(
                "Token validado exitosamente",
                {"valid": True, "response_data": mock_response_data},
            )

            # Verificar que se hizo la petición correcta
            assert len(mock_session.post_calls) == 1
            url, json_data = mock_session.post_calls[0]
            assert url == f"{self.client.auth_service_url}/validate"
            assert json_data == {"token": token}

    @pytest.mark.asyncio
    async def test_validate_token_invalid_token(self):
        """Test que valida un token inválido"""
        token = "invalid.jwt.token"

        mock_response = MockResponse(401)
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "error"
        ) as mock_error, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is False
            assert data is None

            # Verificar logs
            mock_info.assert_any_call("Validando token con servicio de autenticación")
            mock_info.assert_any_call("Respuesta del servicio de autenticación: 401")
            mock_error.assert_called_once_with(
                "Token inválido según el servicio de autenticación"
            )

    @pytest.mark.asyncio
    async def test_validate_token_bad_request(self):
        """Test que valida un token con formato incorrecto"""
        token = "malformed.token"

        mock_response = MockResponse(400, json_data={"error": "Invalid token format"})
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "error"
        ) as mock_error, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is False
            assert data is None

            # Verificar logs
            mock_info.assert_any_call("Validando token con servicio de autenticación")
            mock_info.assert_any_call("Respuesta del servicio de autenticación: 400")
            mock_error.assert_called_once_with(
                "Error en formato de token: {'error': 'Invalid token format'}"
            )

    @pytest.mark.asyncio
    async def test_validate_token_server_error(self):
        """Test que valida un token cuando el servidor devuelve error"""
        token = "valid.jwt.token"

        mock_response = MockResponse(500, text_data="Internal Server Error")
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "error"
        ) as mock_error, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is False
            assert data is None

            # Verificar logs
            mock_info.assert_any_call("Validando token con servicio de autenticación")
            mock_info.assert_any_call("Respuesta del servicio de autenticación: 500")
            mock_error.assert_called_once_with(
                "Error en validación de token: 500 - Internal Server Error"
            )

    @pytest.mark.asyncio
    async def test_validate_token_connection_error(self):
        """Test que valida un token cuando hay error de conexión"""
        token = "valid.jwt.token"

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "error"
        ) as mock_error, patch(
            "aiohttp.ClientSession"
        ) as mock_session_class:
            # Configurar mock para simular error de conexión
            mock_session = AsyncMock()
            mock_session.__aenter__.side_effect = aiohttp.ClientConnectorError(
                MagicMock(), MagicMock()
            )
            mock_session_class.return_value = mock_session

            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is False
            assert data is None

            # Verificar que se loggeó el error de conexión
            error_call = mock_error.call_args[0][0]
            assert "Error de conexión con servicio de autenticación" in error_call

    @pytest.mark.asyncio
    async def test_validate_token_timeout_error(self):
        """Test que valida un token cuando hay timeout"""
        token = "valid.jwt.token"

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "error"
        ) as mock_error, patch(
            "aiohttp.ClientSession"
        ) as mock_session_class:
            # Configurar mock para simular timeout
            mock_session = AsyncMock()
            mock_session.__aenter__.side_effect = aiohttp.ServerTimeoutError("Timeout")
            mock_session_class.return_value = mock_session

            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is False
            assert data is None

            # Verificar que se loggeó el error de timeout
            error_call = mock_error.call_args[0][0]
            assert "Timeout en comunicación con servicio de autenticación" in error_call

    @pytest.mark.asyncio
    async def test_validate_token_unexpected_error(self):
        """Test que valida el manejo de errores inesperados"""
        token = "test.token"

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "error"
        ) as mock_error, patch(
            "aiohttp.ClientSession"
        ) as mock_session_class:
            # Configurar mock de sesión para simular error inesperado
            mock_session = AsyncMock()
            mock_session.__aenter__.side_effect = Exception("Unexpected error")
            mock_session_class.return_value = mock_session

            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is False
            assert data is None

            # Verificar logs
            mock_info.assert_called_once_with(
                "Validando token con servicio de autenticación"
            )
            mock_error.assert_called_once()
            error_call = mock_error.call_args[0][0]
            assert "Error inesperado en validación de token" in error_call

    @pytest.mark.asyncio
    async def test_validate_token_empty_token(self):
        """Test que valida un token vacío"""
        token = ""

        mock_response = MockResponse(200, json_data={"valid": True})
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is True
            assert data == {"valid": True}

            # Verificar que se configuró el contexto con longitud 0
            mock_set_context.assert_called_once_with(
                "AuthClient.validate_token",
                {"token_length": 0, "auth_service_url": self.client.auth_service_url},
            )

    @pytest.mark.asyncio
    async def test_validate_token_none_token(self):
        """Test que valida un token None"""
        token = None

        mock_response = MockResponse(200, json_data={"valid": True})
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is True
            assert data == {"valid": True}

            # Verificar que se configuró el contexto con longitud 0
            mock_set_context.assert_called_once_with(
                "AuthClient.validate_token",
                {"token_length": 0, "auth_service_url": self.client.auth_service_url},
            )

    @pytest.mark.asyncio
    async def test_validate_token_very_long_token(self):
        """Test que valida un token muy largo"""
        token = "a" * 10000

        mock_response = MockResponse(200, json_data={"valid": True, "user": {"id": 1}})
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "success"
        ) as mock_success, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is True
            assert data == {"valid": True, "user": {"id": 1}}

            # Verificar que se configuró el contexto con la longitud correcta
            mock_set_context.assert_called_once_with(
                "AuthClient.validate_token",
                {
                    "token_length": 10000,
                    "auth_service_url": self.client.auth_service_url,
                },
            )

    @pytest.mark.asyncio
    async def test_validate_token_with_special_characters(self):
        """Test que valida un token con caracteres especiales"""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        mock_response = MockResponse(200, json_data={"valid": True, "user": {"name": "John Doe"}})
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "success"
        ) as mock_success, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is True
            assert data == {"valid": True, "user": {"name": "John Doe"}}

            # Verificar que se configuró el contexto con la longitud correcta
            mock_set_context.assert_called_once_with(
                "AuthClient.validate_token",
                {
                    "token_length": len(token),
                    "auth_service_url": self.client.auth_service_url,
                },
            )

    @pytest.mark.asyncio
    async def test_validate_token_with_unicode_characters(self):
        """Test que valida un token con caracteres Unicode"""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IsO6w7HDsSIsImlhdCI6MTUxNjIzOTAyMn0.ñáéíóú"

        mock_response = MockResponse(200, json_data={"valid": True, "user": {"name": "José"}})
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "success"
        ) as mock_success, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is True
            assert data == {"valid": True, "user": {"name": "José"}}

            # Verificar que se configuró el contexto con la longitud correcta
            mock_set_context.assert_called_once_with(
                "AuthClient.validate_token",
                {
                    "token_length": len(token),
                    "auth_service_url": self.client.auth_service_url,
                },
            )

    @pytest.mark.asyncio
    async def test_validate_token_response_without_valid_field(self):
        """Test que valida respuesta sin campo 'valid'"""
        token = "test.token"
        mock_response_data = {"user": {"id": 123}, "exp": 1234567890}

        mock_response = MockResponse(200, json_data=mock_response_data)
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "success"
        ) as mock_success, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados (debería ser False porque no hay campo 'valid')
            assert is_valid is False
            assert data == mock_response_data

            # Verificar logs
            mock_success.assert_called_once_with(
                "Token validado exitosamente",
                {"valid": False, "response_data": mock_response_data},
            )

    @pytest.mark.asyncio
    async def test_validate_token_response_with_false_valid_field(self):
        """Test que valida respuesta con campo 'valid' en False"""
        token = "test.token"
        mock_response_data = {"valid": False, "user": {"id": 123}}

        mock_response = MockResponse(200, json_data=mock_response_data)
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "success"
        ) as mock_success, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is False
            assert data == mock_response_data

            # Verificar logs
            mock_success.assert_called_once_with(
                "Token validado exitosamente",
                {"valid": False, "response_data": mock_response_data},
            )

    @pytest.mark.asyncio
    async def test_validate_token_with_custom_timeout(self):
        """Test que valida el uso del timeout personalizado"""
        token = "test.token"

        mock_response = MockResponse(200, json_data={"valid": True})
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "success"
        ) as mock_success, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ) as mock_session_class:
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar que se usó el timeout correcto
            mock_session_class.assert_called_once_with(timeout=self.client.timeout)

            # Verificar resultados
            assert is_valid is True
            assert data == {"valid": True}

    @pytest.mark.asyncio
    async def test_validate_token_with_custom_auth_service_url(self):
        """Test que valida el uso de URL personalizada del servicio de autenticación"""
        custom_url = "http://custom-auth-service:9000"
        self.client.auth_service_url = custom_url
        token = "test.token"

        mock_response = MockResponse(200, json_data={"valid": True})
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "success"
        ) as mock_success, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar que se usó la URL correcta
            assert len(mock_session.post_calls) == 1
            url, json_data = mock_session.post_calls[0]
            assert url == f"{custom_url}/validate"
            assert json_data == {"token": token}

            # Verificar resultados
            assert is_valid is True
            assert data == {"valid": True}

    @pytest.mark.asyncio
    async def test_validate_token_other_status_codes(self):
        """Test que valida otros códigos de estado HTTP"""
        token = "test.token"

        mock_response = MockResponse(403, text_data="Forbidden")
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "error"
        ) as mock_error, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is False
            assert data is None

            # Verificar logs
            mock_info.assert_any_call("Validando token con servicio de autenticación")
            mock_info.assert_any_call("Respuesta del servicio de autenticación: 403")
            mock_error.assert_called_once_with(
                "Error en validación de token: 403 - Forbidden"
            )

    @pytest.mark.asyncio
    async def test_validate_token_json_error_in_bad_request(self):
        """Test que valida error al parsear JSON en respuesta 400"""
        token = "test.token"

        mock_response = MockResponse(400, raise_json_error=True)
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "error"
        ) as mock_error, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is False
            assert data is None

            # Verificar que se loggeó el error
            error_call = mock_error.call_args[0][0]
            assert "Error inesperado en validación de token" in error_call

    @pytest.mark.asyncio
    async def test_validate_token_text_error_in_server_error(self):
        """Test que valida error al obtener texto en respuesta de servidor"""
        token = "test.token"

        mock_response = MockResponse(500, raise_text_error=True)
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "error"
        ) as mock_error, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is False
            assert data is None

            # Verificar que se loggeó el error
            error_call = mock_error.call_args[0][0]
            assert "Error inesperado en validación de token" in error_call

    @pytest.mark.asyncio
    async def test_validate_token_json_error_in_success_response(self):
        """Test que valida error al parsear JSON en respuesta exitosa"""
        token = "test.token"

        mock_response = MockResponse(200, raise_json_error=True)
        mock_session = MockSession(mock_response)

        with patch.object(
            self.client.logger, "set_context"
        ) as mock_set_context, patch.object(
            self.client.logger, "info"
        ) as mock_info, patch.object(
            self.client.logger, "error"
        ) as mock_error, patch(
            "aiohttp.ClientSession", return_value=mock_session
        ):
            # Llamar al método
            is_valid, data = await self.client.validate_token(token)

            # Verificar resultados
            assert is_valid is False
            assert data is None

            # Verificar que se loggeó el error
            error_call = mock_error.call_args[0][0]
            assert "Error inesperado en validación de token" in error_call
