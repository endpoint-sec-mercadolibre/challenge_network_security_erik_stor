import pytest
import pytest_asyncio
from fastapi import status
from unittest.mock import patch, Mock
import json


class TestAnalysisEndpoint:
    """Tests End-to-End para el endpoint de análisis de archivos"""

    @pytest.mark.asyncio
    async def test_analyze_file_success_complete_flow(
        self, 
        async_client, 
        valid_auth_token,
        mock_config_service,
        mock_gemini_api,
        mock_analysis_repository,
        mock_encrypt_service,
        mock_mongodb
    ):
        """Test completo: flujo exitoso de análisis de archivo"""
        # Mock del middleware a nivel de aplicación  
        with patch('app.services.auth_client.AuthClient.validate_token') as mock_validate:
            mock_validate.return_value = (True, {"user": "testuser", "user_id": "test_user_id_123"})
            
            # Realizar petición
            headers = {"Authorization": valid_auth_token}
            params = {"filename": "test_config.txt"}
            
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            # DEBUG: Imprimir respuesta para entender qué está pasando
            print(f"Status code: {response.status_code}")
            print(f"Response text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response JSON keys: {list(data.keys())}")
                print(f"Response JSON: {data}")
            
            # Validar respuesta exitosa
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            
            # DEBUG: Imprimir info antes de los asserts
            print(f"DEBUG: Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            print(f"DEBUG: Response data: {data}")
            
            # Verificar estructura básica de la respuesta
            assert isinstance(data, dict)
            assert "success" in data
            assert data["success"] is True
            
            # Verificar el mensaje (debe estar presente según el modelo AnalysisResponse)
            assert "message" in data
            assert data["message"] == "Análisis completado exitosamente"
            
            # Verificar que existe el campo data
            assert "data" in data
            
            # Validar estructura de datos
            analysis_data = data["data"]
            assert analysis_data["filename"] == "test_config.txt"
            assert "encrypted_filename" in analysis_data
            assert "file_size" in analysis_data
            assert "analysis_date" in analysis_data
            assert "file_type" in analysis_data
            assert "metadata" in analysis_data

    @pytest.mark.asyncio
    async def test_analyze_file_with_gemini_analysis(
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
        """Test: verificar que el análisis incluye respuesta de Gemini"""
        headers = {"Authorization": valid_auth_token}
        params = {"filename": "network_config.txt"}
        
        response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        metadata = data["data"]["metadata"]
        
        # Verificar que contiene datos del análisis de Gemini
        assert "gemini_analysis" in metadata
        assert "security_level" in metadata
        assert "analysis_date" in metadata
        assert "model_used" in metadata

    @pytest.mark.asyncio
    async def test_analyze_file_encryption_flow(
        self,
        async_client,
        valid_auth_token,
        mock_auth_middleware,
        mock_config_service,
        mock_gemini_api,
        mock_analysis_repository,
        mock_mongodb
    ):
        """Test: verificar que el flujo de encriptación funciona correctamente"""
        # Usar el mock global del servicio de encriptación para verificar las llamadas
        with patch('app.usecase.analysis_usecase.AnalysisUseCase._encrypt_filename') as mock_encrypt_filename:
            mock_encrypt_filename.return_value = ("encrypted_network_config", "base64_encrypted_filename")
            
            headers = {"Authorization": valid_auth_token}
            params = {"filename": "network_config.txt"}
            
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            assert response.status_code == status.HTTP_200_OK
            
            # Verificar que se llamó al método de encriptación del filename
            mock_encrypt_filename.assert_called_once_with("network_config.txt")
            
            # Verificar que la respuesta contiene los datos encriptados
            data = response.json()
            assert data["success"] is True
            assert data["data"]["filename"] == "network_config.txt"
            assert "encrypted_filename" in data["data"]

    @pytest.mark.asyncio
    async def test_analyze_file_missing_filename(self, async_client, valid_auth_token, mock_auth_middleware):
        """Test: error cuando no se proporciona filename"""
        headers = {"Authorization": valid_auth_token}
        
        response = await async_client.get("/api/v1/analyze", headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_analyze_file_empty_filename(self, async_client, valid_auth_token, mock_auth_middleware):
        """Test: error cuando el filename está vacío"""
        headers = {"Authorization": valid_auth_token}
        params = {"filename": ""}
        
        response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
        
        # FastAPI debería rechazar esto en la validación de parámetros
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_analyze_file_config_service_error(
        self,
        async_client,
        valid_auth_token,
        mock_auth_middleware,
        mock_analysis_repository,
        mock_encrypt_service,
        mock_gemini_api,
        mock_mongodb
    ):
        """Test: manejo de errores cuando el servicio de configuración falla"""
        # Mock para simular error en el servicio de configuración
        async def _mock_get_file_content_error(encrypted_filename, token=None):
            raise Exception("Config service unavailable")
        
        with patch('app.usecase.analysis_usecase.AnalysisUseCase._get_file_content_from_config_service', side_effect=_mock_get_file_content_error):
            headers = {"Authorization": valid_auth_token}
            params = {"filename": "missing_file.txt"}
            
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            # Debería fallar con error 500 debido al error del servicio
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_analyze_file_gemini_api_error(
        self,
        async_client,
        valid_auth_token,
        mock_auth_middleware,
        mock_config_service,
        mock_analysis_repository,
        mock_encrypt_service,
        mock_mongodb
    ):
        """Test: manejo de errores cuando Gemini API falla"""
        # Mock para simular error en Gemini API
        def _mock_generate_content_error(prompt, generation_config=None):
            raise Exception("Gemini API error")
        
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content.side_effect = _mock_generate_content_error
            mock_model_class.return_value = mock_model
            
            with patch('google.generativeai.configure'):
                headers = {"Authorization": valid_auth_token}
                params = {"filename": "test_config.txt"}
                
                response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
                
                assert response.status_code == status.HTTP_200_OK
                
                data = response.json()
                metadata = data["data"]["metadata"]
                
                # Debería incluir análisis de fallback
                assert metadata["security_level"] == "unknown"
                assert "Error en análisis" in str(metadata["gemini_analysis"])

    @pytest.mark.asyncio
    async def test_analyze_file_mongodb_save_error(
        self,
        async_client,
        valid_auth_token,
        mock_auth_middleware,
        mock_config_service,
        mock_gemini_api,
        mock_encrypt_service,
        mock_mongodb
    ):
        """Test: manejo de errores cuando MongoDB falla al guardar"""
        # Mock del repositorio que falla
        with patch('app.model.analysis_repository.AnalysisRepository') as mock_repo:
            mock_instance = Mock()
            mock_instance.save_analysis_record.side_effect = Exception("MongoDB connection error")
            mock_repo.return_value = mock_instance

            headers = {"Authorization": valid_auth_token}
            params = {"filename": "test_config.txt"}
            
            response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
            
            # En entorno de test debería continuar sin guardar
            # En entorno de producción debería fallar
            # El comportamiento está controlado por ENVIRONMENT variable
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_analyze_file_response_format(
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
        """Test: validar formato exacto de la respuesta"""
        headers = {"Authorization": valid_auth_token}
        params = {"filename": "format_test.txt"}
        
        response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
        
        assert response.status_code == status.HTTP_200_OK
        assert "application/json" in response.headers.get("content-type", "")
        
        data = response.json()
        
        # Validar estructura raíz
        assert isinstance(data, dict)
        assert set(data.keys()) == {"success", "message", "data"}
        
        # Validar tipos
        assert isinstance(data["success"], bool)
        assert isinstance(data["message"], str)
        assert isinstance(data["data"], dict)
        
        # Validar estructura de data
        analysis_data = data["data"]
        expected_data_keys = {
            "filename", "encrypted_filename", "file_size", 
            "analysis_date", "file_type", "checksum", "metadata"
        }
        assert set(analysis_data.keys()) == expected_data_keys 