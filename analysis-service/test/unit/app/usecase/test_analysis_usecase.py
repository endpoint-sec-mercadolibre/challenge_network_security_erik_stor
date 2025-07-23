import pytest
import os
import json
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock

from app.usecase.analysis_usecase import AnalysisUseCase
from app.model.analysis_model import AnalysisResponse


class TestAnalysisUseCase:
    """Tests para el caso de uso de análisis"""

    def setup_method(self):
        """Configuración antes de cada test"""
        with patch("app.usecase.analysis_usecase.Logger") as mock_logger_class, patch(
            "app.usecase.analysis_usecase.Encrypt"
        ) as mock_encrypt_class, patch(
            "app.usecase.analysis_usecase.AnalysisRepository"
        ) as mock_repo_class:

            mock_logger = MagicMock()
            mock_encrypt = MagicMock()
            mock_repo = MagicMock()

            mock_logger_class.return_value = mock_logger
            mock_encrypt_class.return_value = mock_encrypt
            mock_repo_class.return_value = mock_repo

            self.usecase = AnalysisUseCase()
            self.usecase.logger = mock_logger
            self.usecase.encrypt = mock_encrypt
            self.usecase.repository = mock_repo

    def test_initialization(self):
        """Test de inicialización del usecase"""
        with patch("app.usecase.analysis_usecase.Logger") as mock_logger_class, patch(
            "app.usecase.analysis_usecase.Encrypt"
        ) as mock_encrypt_class, patch(
            "app.usecase.analysis_usecase.AnalysisRepository"
        ) as mock_repo_class:

            usecase = AnalysisUseCase()

            assert usecase.logger is not None
            assert usecase.encrypt is not None
            assert usecase.repository is not None
            assert usecase.config_service_url == "http://localhost:8000"

    def test_validate_filename_valid(self):
        """Test de validación de nombre de archivo válido"""
        self.usecase._validate_filename("test.txt")
        # No debe lanzar excepción

    def test_validate_filename_empty(self):
        """Test de validación de nombre de archivo vacío"""
        with pytest.raises(
            ValueError, match="El nombre del archivo no puede estar vacío"
        ):
            self.usecase._validate_filename("")

    def test_validate_filename_none(self):
        """Test de validación de nombre de archivo None"""
        with pytest.raises(
            ValueError, match="El nombre del archivo no puede estar vacío"
        ):
            self.usecase._validate_filename(None)

    def test_validate_filename_whitespace(self):
        """Test de validación de nombre de archivo solo espacios"""
        with pytest.raises(
            ValueError, match="El nombre del archivo no puede estar vacío"
        ):
            self.usecase._validate_filename("   ")

    def test_encrypt_filename(self):
        """Test de encriptación de nombre de archivo"""
        self.usecase.encrypt.encrypt.return_value = "encrypted_filename"
        self.usecase.encrypt.ofuscar_base64.return_value = "base64_filename"

        encrypted, base64 = self.usecase._encrypt_filename("test.txt")

        assert encrypted == "encrypted_filename"
        assert base64 == "base64_filename"
        self.usecase.encrypt.encrypt.assert_called_once_with("test.txt")
        self.usecase.encrypt.ofuscar_base64.assert_called_once_with(
            "encrypted_filename"
        )

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_get_file_content_success(self, mock_client_class):
        """Test exitoso de obtención de contenido de archivo"""
        # Configurar mocks
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"content": "encrypted_content"}}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        self.usecase.encrypt.desofuscar_base64.return_value = "desofuscated_content"
        self.usecase.encrypt.decrypt.return_value = "decrypted_content"

        # Ejecutar
        result = await self.usecase._get_file_content_from_config_service(
            "encrypted_filename", "token"
        )

        # Verificar
        assert result == "decrypted_content"
        mock_client.get.assert_called_once()
        self.usecase.encrypt.desofuscar_base64.assert_called_once_with(
            "encrypted_content"
        )
        self.usecase.encrypt.decrypt.assert_called_once_with("desofuscated_content")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_get_file_content_service_error(self, mock_client_class):
        """Test de error en servicio de configuración - usa contenido mock"""
        # Configurar mocks para simular error
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Service error")
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        # Ejecutar
        result = await self.usecase._get_file_content_from_config_service(
            "encrypted_filename"
        )

        # Verificar que retorna contenido mock
        assert "# Configuración de red de ejemplo" in result
        assert "interface eth0" in result

    def test_determine_security_level_safe(self):
        """Test de determinación de nivel de seguridad - seguro"""
        parsed_analysis = {"safe": True, "problems": []}

        result = self.usecase._determine_security_level_from_parsed(parsed_analysis)

        assert result == "safe"

    def test_determine_security_level_critical(self):
        """Test de determinación de nivel de seguridad - crítico"""
        parsed_analysis = {
            "safe": False,
            "problems": [
                {"severity": "crítica", "problem": "Test critical"},
                {"severity": "media", "problem": "Test medium"},
            ],
        }

        result = self.usecase._determine_security_level_from_parsed(parsed_analysis)

        assert result == "critical"

    def test_determine_security_level_high(self):
        """Test de determinación de nivel de seguridad - alto"""
        parsed_analysis = {
            "safe": False,
            "problems": [
                {"severity": "alta", "problem": "Test high"},
                {"severity": "baja", "problem": "Test low"},
            ],
        }

        result = self.usecase._determine_security_level_from_parsed(parsed_analysis)

        assert result == "high"

    def test_determine_security_level_no_problems(self):
        """Test de determinación de nivel de seguridad - sin problemas"""
        parsed_analysis = {"safe": False, "problems": []}

        result = self.usecase._determine_security_level_from_parsed(parsed_analysis)

        assert result == "safe"

    def test_create_analysis_prompt(self):
        """Test de creación de prompt para análisis"""
        file_content = "test configuration"

        prompt = self.usecase._create_analysis_prompt(file_content)

        assert "Analiza esta configuración de red" in prompt
        assert file_content in prompt
        assert "JSON" in prompt

    def test_parse_gemini_response_valid_json(self):
        """Test de parseo de respuesta de Gemini con JSON válido"""
        mock_response = MagicMock()
        mock_response.text = 'Some text {"analysis_date": "2024-01-01", "safe": true, "problems": []} more text'

        result = self.usecase._parse_gemini_response(mock_response)

        assert result["safe"] is True
        assert result["analysis_date"] == "2024-01-01"
        assert "problems" in result

    def test_parse_gemini_response_invalid_json(self):
        """Test de parseo de respuesta de Gemini con JSON inválido"""
        mock_response = MagicMock()
        mock_response.text = "This is not a JSON response"

        result = self.usecase._parse_gemini_response(mock_response)

        assert result["safe"] is False
        assert "problems" in result
        assert len(result["problems"]) > 0

    def test_ensure_required_fields(self):
        """Test de asegurar campos requeridos en análisis"""
        parsed_analysis = {}

        self.usecase._ensure_required_fields(parsed_analysis)

        assert "safe" in parsed_analysis
        assert "problems" in parsed_analysis
        assert "analysis_date" in parsed_analysis
        assert parsed_analysis["safe"] is False
        assert isinstance(parsed_analysis["problems"], list)

    def test_create_analysis_data(self):
        """Test de creación de datos de análisis"""
        parsed_analysis = {"safe": True, "problems": []}

        result = self.usecase._create_analysis_data(parsed_analysis)

        assert "analysis_date" in result
        assert "security_level" in result
        assert "gemini_analysis" in result
        assert "model_used" in result
        assert result["model_used"] == "gemini-1.5-flash"

    def test_create_fallback_analysis(self):
        """Test de creación de análisis de fallback"""
        error_message = "Test error"

        result = self.usecase._create_fallback_analysis(error_message)

        assert "analysis_date" in result
        assert result["security_level"] == "unknown"
        assert error_message in result["gemini_analysis"]
        assert result["model_used"] == "none"

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_configure_gemini_success(self, mock_model_class, mock_configure):
        """Test exitoso de configuración de Gemini"""
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model

        result = self.usecase._configure_gemini()

        mock_configure.assert_called_once_with(api_key="test_key")
        mock_model_class.assert_called_once_with("gemini-1.5-flash")
        assert result == mock_model

    def test_configure_gemini_no_api_key(self):
        """Test de configuración de Gemini sin API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key de Gemini no configurada"):
                self.usecase._configure_gemini()

    @pytest.mark.asyncio
    @patch("app.usecase.analysis_usecase.genai")
    async def test_perform_analysis_success(self, mock_genai):
        """Test exitoso de análisis con Gemini"""
        # Configurar mocks
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = (
            '{"safe": true, "problems": [], "analysis_date": "2024-01-01"}'
        )

        with patch.object(
            self.usecase, "_configure_gemini", return_value=mock_model
        ), patch.object(self.usecase, "_call_gemini_api", return_value=mock_response):

            result = await self.usecase._perform_analysis("test content")

            assert "analysis_date" in result
            assert "security_level" in result
            assert "gemini_analysis" in result

    @pytest.mark.asyncio
    async def test_perform_analysis_no_content(self):
        """Test de análisis sin contenido"""
        with pytest.raises(ValueError, match="No se proporcionó contenido del archivo"):
            await self.usecase._perform_analysis(None)

    def test_get_analysis_by_id(self):
        """Test de obtención de análisis por ID"""
        auth_result = {"user_id": "test_user"}

        result = self.usecase.get_analysis_by_id("test_id", auth_result)

        assert result["analysis_id"] == "test_id"
        assert result["user_id"] == "test_user"
        assert "status" in result

    def test_get_analyses_by_user(self):
        """Test de obtención de análisis por usuario"""
        auth_result = {"user_id": "test_user"}

        result = self.usecase.get_analyses_by_user(auth_result)

        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["user_id"] == "test_user"

    def test_save_analysis_record_success(self):
        """Test exitoso de guardado de registro de análisis"""
        analysis_data = {"test": "data"}
        auth_result = {"user": "test_user"}

        self.usecase._save_analysis_record(
            "test.txt", "encrypted", analysis_data, auth_result
        )

        self.usecase.repository.save_analysis_record.assert_called_once()

    def test_save_analysis_record_error(self):
        """Test de error en guardado de registro de análisis"""
        self.usecase.repository.save_analysis_record.side_effect = Exception(
            "MongoDB error"
        )
        analysis_data = {"test": "data"}
        auth_result = {"user": "test_user"}

        # En ambiente no test, debe lanzar excepción
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            with pytest.raises(
                RuntimeError, match="Error al guardar registro en base de datos"
            ):
                self.usecase._save_analysis_record(
                    "test.txt", "encrypted", analysis_data, auth_result
                )

    def test_create_success_response(self):
        """Test de creación de respuesta exitosa"""
        analysis_data = {"test": "data"}

        result = self.usecase._create_success_response(
            "test.txt", "encrypted", "file content", analysis_data
        )

        assert isinstance(result, AnalysisResponse)
        assert result.success is True
        assert result.data.filename == "test.txt"
        assert result.data.file_size == 12  # len("file content")

    def test_save_error_record_with_token(self):
        """Test de guardado de registro de error con token"""
        auth_result = {"token": "test_token", "user": "test_user"}

        self.usecase._save_error_record("test.txt", "Test error", auth_result)

        self.usecase.repository.save_analysis_record.assert_called_once()
        args, kwargs = self.usecase.repository.save_analysis_record.call_args
        assert kwargs["success"] is False
        assert "Test error" in kwargs["response"]["error"]

    def test_save_error_record_without_token(self):
        """Test de guardado de registro de error sin token"""
        auth_result = {}

        self.usecase._save_error_record("test.txt", "Test error", auth_result)

        # No debe llamar al repositorio si no hay token
        self.usecase.repository.save_analysis_record.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.usecase.analysis_usecase.httpx.AsyncClient")
    async def test_execute_full_flow_success(self, mock_client_class):
        """Test del flujo completo exitoso de execute"""
        # Configurar mocks para todo el flujo
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"content": "encrypted_content"}}
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        self.usecase.encrypt.encrypt.return_value = "encrypted_filename"
        self.usecase.encrypt.ofuscar_base64.return_value = "base64_filename"
        self.usecase.encrypt.desofuscar_base64.return_value = "desofuscated_content"
        self.usecase.encrypt.decrypt.return_value = "decrypted_content"

        # Mock los métodos de guardado para que no hagan await
        with patch.object(
            self.usecase, "_perform_analysis"
        ) as mock_analysis, patch.object(
            self.usecase, "_save_analysis_record"
        ) as mock_save_record, patch.object(
            self.usecase, "_save_error_record"
        ) as mock_save_error:

            mock_analysis.return_value = {"test": "analysis_data"}
            mock_save_record.return_value = None
            mock_save_error.return_value = None

            auth_result = {"token": "test_token", "user": "test_user"}

            result = await self.usecase.execute("test.txt", auth_result)

            assert isinstance(result, AnalysisResponse)
            assert result.success is True
            assert result.data.filename == "test.txt"

    @pytest.mark.asyncio
    async def test_execute_validation_error(self):
        """Test de error de validación en execute"""
        auth_result = {"token": "test_token"}

        # Mock _save_error_record para que no haga await
        with patch.object(self.usecase, "_save_error_record") as mock_save_error:
            mock_save_error.return_value = None

            with pytest.raises(ValueError):
                await self.usecase.execute("", auth_result)

    @pytest.mark.asyncio
    async def test_execute_general_error(self):
        """Test de error general en execute que se guarda"""
        auth_result = {"token": "test_token", "user": "test_user"}

        # Mock _save_error_record para que no haga await
        with patch.object(self.usecase, "_save_error_record") as mock_save_error:
            mock_save_error.return_value = None

            # Simular error en validación
            with patch.object(self.usecase, "_validate_filename") as mock_validate:
                mock_validate.side_effect = Exception("Test error")

                with pytest.raises(Exception, match="Test error"):
                    await self.usecase.execute("test.txt", auth_result)

                # Verificar que se llamó save_error_record
                mock_save_error.assert_called_once()
