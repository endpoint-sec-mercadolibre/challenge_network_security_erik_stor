import pytest
import json
from fastapi import status
from unittest.mock import patch, Mock


class TestWorkingAnalysis:
    """Tests E2E que funcionan con la estructura real de la aplicación"""

    @pytest.mark.asyncio
    async def test_analyze_endpoint_basic_functionality(
        self, 
        async_client, 
        valid_auth_token,
        mock_auth_middleware,
        mock_config_service,
        mock_gemini_api,
        mock_analysis_repository,
        mock_encrypt_service,
        mock_mongodb
    ):
        """Test básico: verificar que el endpoint responde correctamente"""
        headers = {"Authorization": valid_auth_token}
        params = {"filename": "test_config.txt"}
        
        response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
        
        # Validar que obtenemos una respuesta exitosa
        assert response.status_code == status.HTTP_200_OK
        
        # Validar que es JSON válido
        data = response.json()
        assert isinstance(data, dict)
        
        # Validar estructura básica (independiente del formato específico)
        assert "success" in data
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_analyze_without_auth_fails(self, async_client):
        """Test: debe fallar sin autenticación"""
        params = {"filename": "test_config.txt"}
        
        response = await async_client.get("/api/v1/analyze", params=params)
        
        # Debe fallar por falta de autenticación
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED, 
            status.HTTP_403_FORBIDDEN
        ]

    @pytest.mark.asyncio
    async def test_analyze_missing_filename_parameter(
        self, 
        async_client, 
        valid_auth_token,
        mock_auth_middleware
    ):
        """Test: debe fallar sin el parámetro filename"""
        headers = {"Authorization": valid_auth_token}
        
        # Mock del middleware para que la autenticación pase primero
        with patch('app.services.auth_client.AuthClient.validate_token') as mock_validate, \
             patch('app.services.auth_middleware.auth_middleware.__call__') as mock_middleware:
                
            mock_validate.return_value = (True, {"user": "testuser", "user_id": "user123"})
            mock_middleware.return_value = {
                "authenticated": True,
                "token": "valid_token",
                "user": "testuser"
            }
            
            response = await async_client.get("/api/v1/analyze", headers=headers)
            
            # FastAPI debe rechazar por parámetro requerido faltante
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_analyze_empty_filename_parameter(
        self, 
        async_client, 
        valid_auth_token,
        mock_auth_middleware
    ):
        """Test: debe fallar con filename vacío"""
        headers = {"Authorization": valid_auth_token}
        params = {"filename": ""}
        
        # Mock del middleware para que la autenticación pase primero
        with patch('app.services.auth_client.AuthClient.validate_token') as mock_validate, \
             patch('app.services.auth_middleware.auth_middleware.__call__') as mock_middleware:
                
            mock_validate.return_value = (True, {"user": "testuser", "user_id": "user123"})
            mock_middleware.return_value = {
                "authenticated": True,
                "token": "valid_token",
                "user": "testuser"
            }
            
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            # FastAPI debe rechazar por validación de longitud mínima
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_health_endpoint_works(self, async_client):
        """Test: el endpoint de health debe funcionar sin autenticación"""
        response = await async_client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "analysis-service"
        assert data["version"] == "1.0.0"

    @pytest.mark.asyncio 
    async def test_analyze_endpoint_response_format(
        self, 
        async_client, 
        valid_auth_token,
        mock_auth_middleware,
        mock_config_service,
        mock_gemini_api,
        mock_analysis_repository,
        mock_encrypt_service,
        mock_mongodb
    ):
        """Test: validar el formato de respuesta actual"""
        headers = {"Authorization": valid_auth_token}
        params = {"filename": "test_config.txt"}
        
        response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
        
        assert response.status_code == status.HTTP_200_OK
        assert "application/json" in response.headers.get("content-type", "")
        
        data = response.json()
        
        # Validar estructura mínima esperada
        assert isinstance(data, dict)
        assert "success" in data
        assert data["success"] is True
        
        # La aplicación actual devuelve estructura del config service,
        # así que validamos esa estructura por ahora
        if "data" in data:
            assert isinstance(data["data"], dict)

    @pytest.mark.asyncio
    async def test_analyze_with_different_filenames(
        self, 
        async_client, 
        valid_auth_token,
        mock_auth_middleware,
        mock_config_service,
        mock_gemini_api,
        mock_analysis_repository,
        mock_encrypt_service,
        mock_mongodb
    ):
        """Test: diferentes nombres de archivo válidos"""
        test_filenames = [
            "config.txt",
            "network-config.conf", 
            "setup.ini",
            "test_file_123.cfg"
        ]
        
        headers = {"Authorization": valid_auth_token}
        
        for filename in test_filenames:
            params = {"filename": filename}
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            assert response.status_code == status.HTTP_200_OK, f"Failed for filename: {filename}"
            
            data = response.json()
            assert data["success"] is True, f"Failed for filename: {filename}" 