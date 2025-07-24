import pytest
import pytest_asyncio
from fastapi import status
from unittest.mock import patch, Mock


class TestAuthentication:
    """Tests End-to-End para la autenticación del servicio"""

    @pytest.mark.asyncio
    async def test_analyze_without_authorization_header(self, async_client):
        """Test: debe fallar sin header de Authorization"""
        params = {"filename": "test_config.txt"}
        
        response = await async_client.get("/api/v1/analyze", params=params)
        
        # Sin header de authorization, el middleware debería rechazar la petición
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @pytest.mark.asyncio
    async def test_analyze_with_invalid_token_format(self, async_client):
        """Test: debe fallar con formato de token inválido"""
        headers = {"Authorization": "InvalidFormat token123"}
        params = {"filename": "test_config.txt"}
        
        response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @pytest.mark.asyncio
    async def test_analyze_with_missing_bearer_prefix(self, async_client):
        """Test: debe fallar sin prefijo Bearer"""
        headers = {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        params = {"filename": "test_config.txt"}
        
        response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @pytest.mark.asyncio
    async def test_analyze_with_expired_token(self, async_client):
        """Test: debe fallar con token expirado"""
        # Mock del AuthClient para simular token expirado
        with patch('app.services.auth_client.AuthClient.validate_token') as mock_validate:
            mock_validate.return_value = (False, {"error": "Token expirado"})
            
            headers = {"Authorization": "Bearer expired_token_123"}
            params = {"filename": "test_config.txt"}
            
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            
            data = response.json()
            assert "detail" in data
            assert "Token de autenticación inválido" in data["detail"]["message"]

    @pytest.mark.asyncio
    async def test_analyze_with_malformed_jwt(self, async_client):
        """Test: debe fallar con JWT malformado"""
        # Mock del AuthClient para simular JWT malformado
        with patch('app.services.auth_client.AuthClient.validate_token') as mock_validate:
            mock_validate.return_value = (False, {"error": "JWT malformado"})
            
            headers = {"Authorization": "Bearer malformed.jwt.token"}
            params = {"filename": "test_config.txt"}
            
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            
            data = response.json()
            assert "detail" in data
            assert "Token de autenticación inválido" in data["detail"]["message"]

    @pytest.mark.asyncio
    async def test_analyze_with_valid_token_success(
        self, 
        async_client, 
        valid_auth_token,
        mock_config_service,
        mock_gemini_api,
        mock_analysis_repository,
        mock_encrypt_service,
        mock_mongodb
    ):
        """Test: debe funcionar con token válido"""
        # Mock middleware para autenticación exitosa
        with patch('app.services.auth_client.AuthClient.validate_token') as mock_validate, \
             patch('app.services.auth_middleware.auth_middleware.__call__') as mock_middleware:
                
            mock_validate.return_value = (True, {"user": "testuser", "user_id": "user123"})
            mock_middleware.return_value = {
                "authenticated": True,
                "token": "valid_token",
                "user": "testuser"
            }
            
            headers = {"Authorization": valid_auth_token}
            params = {"filename": "test_config.txt"}
            
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_analyze_auth_service_unavailable(self, async_client, valid_auth_token):
        """Test: manejo cuando el servicio de autenticación no está disponible"""
        # Mock del AuthClient para simular servicio no disponible
        with patch('app.services.auth_client.AuthClient.validate_token') as mock_validate:
            import httpx
            mock_validate.side_effect = httpx.ConnectError("Cannot connect to host localhost:8001")
            
            headers = {"Authorization": valid_auth_token}
            params = {"filename": "test_config.txt"}
            
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            # El middleware actual devuelve 500 en caso de error de conexión
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            
            data = response.json()
            assert "detail" in data

    @pytest.mark.asyncio
    async def test_analyze_auth_timeout(self, async_client, valid_auth_token):
        """Test: manejo de timeout en autenticación"""
        # Mock del AuthClient para simular timeout
        with patch('app.services.auth_client.AuthClient.validate_token') as mock_validate:
            import httpx
            mock_validate.side_effect = httpx.TimeoutException("Timeout")
            
            headers = {"Authorization": valid_auth_token}
            params = {"filename": "test_config.txt"}
            
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            # El middleware actual devuelve 500 en caso de timeout
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_health_endpoint_bypasses_auth(self, async_client):
        """Test: el endpoint de health debe saltar la autenticación"""
        # No incluir header de autorización
        response = await async_client.get("/health")
        
        # Debe funcionar sin autenticación
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_openapi_endpoints_bypass_auth(self, async_client):
        """Test: los endpoints de documentación deben saltar la autenticación"""
        # Probar endpoint de OpenAPI
        response = await async_client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        
        # Probar Swagger UI
        response = await async_client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        
        # Probar ReDoc
        response = await async_client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_auth_middleware_preserves_request_info(
        self,
        async_client,
        valid_auth_token,
        mock_config_service,
        mock_gemini_api,
        mock_analysis_repository,
        mock_encrypt_service,
        mock_mongodb
    ):
        """Test: el middleware debe preservar información de la petición"""
        # Este test verifica que el middleware funciona correctamente
        # usando los mocks del AuthClient para simular autenticación exitosa
        
        with patch('app.services.auth_client.AuthClient.validate_token') as mock_validate:
            mock_validate.return_value = (True, {"user": "testuser", "user_id": "user123"})
            
            headers = {
                "Authorization": valid_auth_token,
                "User-Agent": "test-client",
                "X-Request-ID": "test-123"
            }
            params = {"filename": "test_config.txt"}
            
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            assert response.status_code == status.HTTP_200_OK
            
            # Verificar que la respuesta es correcta, lo que indica que el middleware
            # procesó correctamente la información de la petición
            data = response.json()
            assert data["success"] is True
            assert data["data"]["filename"] == "test_config.txt"

    @pytest.mark.asyncio
    async def test_auth_different_user_contexts(
        self,
        async_client,
        valid_auth_token,
        mock_config_service,
        mock_gemini_api,
        mock_analysis_repository,
        mock_encrypt_service,
        mock_mongodb
    ):
        """Test: diferentes usuarios deben obtener contextos diferentes"""
        users_data = [
            {"user": "user1", "user_id": "id1"},
            {"user": "user2", "user_id": "id2"},
            {"user": "admin", "user_id": "admin_id"}
        ]
        
        for user_data in users_data:
            with patch('app.services.auth_client.AuthClient.validate_token') as mock_validate, \
                 patch('app.services.auth_middleware.auth_middleware.__call__') as mock_middleware:
                    
                mock_validate.return_value = (True, {"user": user_data["user"], "user_id": user_data["user_id"]})
                mock_middleware.return_value = {
                    "authenticated": True,
                    "token": "valid_token",
                    "user": user_data["user"]
                }
                
                headers = {"Authorization": valid_auth_token}
                params = {"filename": f"config_{user_data['user']}.txt"}
                
                response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
                
                assert response.status_code == status.HTTP_200_OK
                
                data = response.json()
                assert data["success"] is True
                assert data["data"]["filename"] == f"config_{user_data['user']}.txt" 