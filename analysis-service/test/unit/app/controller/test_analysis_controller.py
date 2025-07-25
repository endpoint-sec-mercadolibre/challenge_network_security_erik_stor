import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from fastapi import HTTPException, Request
from datetime import datetime

from app.controller.analysis_controller import analyze_file, router
from app.model.analysis_model import AnalysisResponse, AnalysisData


class TestAnalysisController:
    """Test cases para el controlador de análisis"""

    def setup_method(self):
        """Setup para cada test"""
        pass

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.services.auth_middleware.auth_middleware')
    @patch('app.controller.analysis_controller.logger')
    async def test_analyze_file_success(self, mock_logger, mock_auth_middleware, mock_usecase_class):
        """Test successful file analysis"""
        # Arrange
        mock_logger.set_context = MagicMock()
        mock_logger.info = MagicMock()
        mock_logger.success = MagicMock()
        
        expected_auth_result = {"token": "test_token", "user": "testuser"}
        mock_auth_middleware.return_value = expected_auth_result
        
        mock_usecase = AsyncMock()
        mock_usecase_class.return_value = mock_usecase
        
        expected_response = AnalysisResponse(
            success=True,
            message="Análisis completado exitosamente",
            data=AnalysisData(
                filename="test.txt",
                encrypted_filename="encrypted_test.txt",
                file_size=100,
                checksum="test_checksum",
                file_type="text/plain",
                content="test content",
                metadata={"analysis": "completed"},
                analysis_date=datetime.now().isoformat(),
                safe=True,
                problems=[],
                security_level="safe"
            )
        )
        
        mock_usecase.execute.return_value = expected_response
        
        # Crear mock request
        mock_request = Mock()
        mock_request.headers = {"authorization": "Bearer valid_token"}
        
        # Act - la función recibe request, auth_result y filename
        result = await analyze_file(mock_request, expected_auth_result, filename="test.txt", enable_ia=False)
        
        # Assert
        assert result == expected_response
        mock_usecase.execute.assert_called_once_with("test.txt", expected_auth_result, False)

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.services.auth_middleware.auth_middleware')
    @patch('app.controller.analysis_controller.logger')
    async def test_analyze_file_http_exception_passthrough(self, mock_logger, mock_auth_middleware, mock_usecase_class):
        """Test que valida que las HTTPException se pasan directamente"""
        # Configurar mocks
        mock_logger.set_context = MagicMock()
        mock_logger.info = MagicMock()
        mock_logger.error = MagicMock()
        
        mock_auth_middleware.return_value = {"token": "test_token"}
        
        mock_usecase = AsyncMock()
        # Simular HTTPException del usecase
        mock_usecase.execute.side_effect = HTTPException(status_code=404, detail="File not found")
        mock_usecase_class.return_value = mock_usecase
        
        mock_request = MagicMock(spec=Request)
        
        # Ejecutar y verificar que se lanza HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await analyze_file(mock_request, {"token": "test_token"}, filename="nonexistent.txt", enable_ia=False)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "File not found"

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.services.auth_middleware.auth_middleware')
    @patch('app.controller.analysis_controller.logger')
    async def test_analyze_file_mongodb_error(self, mock_logger, mock_auth_middleware, mock_usecase_class):
        """Test que valida el manejo de errores de MongoDB"""
        # Configurar mocks
        mock_logger.set_context = MagicMock()
        mock_logger.info = MagicMock()
        mock_logger.error = MagicMock()
        
        mock_auth_middleware.return_value = {"token": "test_token"}
        
        mock_usecase = AsyncMock()
        # Simular error de MongoDB
        mock_usecase.execute.side_effect = Exception("MongoDB connection failed")
        mock_usecase_class.return_value = mock_usecase
        
        mock_request = MagicMock(spec=Request)
        
        # Ejecutar y verificar que se lanza HTTPException 500
        with pytest.raises(HTTPException) as exc_info:
            await analyze_file(mock_request, {"token": "test_token"}, filename="test.txt", enable_ia=False)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Error en la base de datos"
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.services.auth_middleware.auth_middleware')
    @patch('app.controller.analysis_controller.logger')
    async def test_analyze_file_authentication_error(self, mock_logger, mock_auth_middleware, mock_usecase_class):
        """Test que valida el manejo de errores de autenticación"""
        # Configurar mocks
        mock_logger.set_context = MagicMock()
        mock_logger.info = MagicMock()
        mock_logger.error = MagicMock()
        
        mock_auth_middleware.return_value = {"token": "test_token"}
        
        mock_usecase = AsyncMock()
        # Simular error de autenticación
        mock_usecase.execute.side_effect = Exception("Authentication failed")
        mock_usecase_class.return_value = mock_usecase
        
        mock_request = MagicMock(spec=Request)
        
        # Ejecutar y verificar que se lanza HTTPException 500
        with pytest.raises(HTTPException) as exc_info:
            await analyze_file(mock_request, {"token": "test_token"}, filename="test.txt", enable_ia=False)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Error en la base de datos"

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.services.auth_middleware.auth_middleware')
    @patch('app.controller.analysis_controller.logger')
    async def test_analyze_file_general_error(self, mock_logger, mock_auth_middleware, mock_usecase_class):
        """Test que valida el manejo de errores generales"""
        # Configurar mocks
        mock_logger.set_context = MagicMock()
        mock_logger.info = MagicMock()
        mock_logger.error = MagicMock()
        
        mock_auth_middleware.return_value = {"token": "test_token"}
        
        mock_usecase = AsyncMock()
        # Simular error general
        mock_usecase.execute.side_effect = Exception("General error")
        mock_usecase_class.return_value = mock_usecase
        
        mock_request = MagicMock(spec=Request)
        
        # Ejecutar y verificar que se lanza HTTPException 500
        with pytest.raises(HTTPException) as exc_info:
            await analyze_file(mock_request, {"token": "test_token"}, filename="test.txt", enable_ia=False)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Error interno del servidor"

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.services.auth_middleware.auth_middleware')
    @patch('app.controller.analysis_controller.logger')
    async def test_analyze_file_logging_context(self, mock_logger, mock_auth_middleware, mock_usecase_class):
        """Test que valida el contexto de logging"""
        # Configurar mocks
        mock_logger.set_context = MagicMock()
        mock_logger.info = MagicMock()
        mock_logger.success = MagicMock()
        
        mock_auth_middleware.return_value = {"token": "test_token"}
        
        mock_usecase = AsyncMock()
        mock_analysis_data = AnalysisData(
            filename="document.pdf",
            encrypted_filename="encrypted_document",
            file_size=2048,
            checksum="sha256:def456",
            file_type="application/pdf",
            content="test content",
            metadata={"pages": 5},
            analysis_date="2024-01-01T12:00:00Z",
            safe=True,
            problems=[],
            security_level="safe"
        )
        mock_response = AnalysisResponse(
            success=True,
            message="PDF analizado correctamente",
            data=mock_analysis_data
        )
        mock_usecase.execute.return_value = mock_response
        mock_usecase_class.return_value = mock_usecase
        
        mock_request = MagicMock(spec=Request)
        
        # Ejecutar función
        result = await analyze_file(mock_request, {"token": "test_token"}, filename="document.pdf", enable_ia=False)
        
        # Verificar contexto de logging
        mock_logger.set_context.assert_called_once_with(
            "AnalysisController.analyze_file",
            {
                "filename": "document.pdf",
                "endpoint": "/analyze",
                "authenticated": True
            }
        )

    def test_router_configuration(self):
        """Test que valida la configuración del router"""
        assert router is not None
        
        # Verificar que tiene rutas
        routes = router.routes
        assert len(routes) > 0
        
        # Buscar la ruta de análisis
        analyze_route = None
        for route in routes:
            if hasattr(route, 'path') and route.path == "/analyze":
                analyze_route = route
                break
        
        assert analyze_route is not None
        assert "GET" in analyze_route.methods 