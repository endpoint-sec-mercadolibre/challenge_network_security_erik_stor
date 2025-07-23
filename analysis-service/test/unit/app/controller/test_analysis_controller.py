import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

from app.controller.analysis_controller import router, analyze_file
from app.model.analysis_model import AnalysisResponse, AnalysisData


class TestAnalysisController:
    """Tests para el controller de análisis"""

    def setup_method(self):
        """Configuración antes de cada test"""
        self.client = TestClient(router)

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.controller.analysis_controller.auth_middleware')
    @patch('app.controller.analysis_controller.logger')
    async def test_analyze_file_success(self, mock_logger, mock_auth_middleware, mock_usecase_class):
        """Test exitoso del endpoint analyze_file"""
        # Configurar mocks
        mock_logger.set_context = MagicMock()
        mock_logger.info = MagicMock()
        mock_logger.success = MagicMock()
        
        mock_auth_middleware.return_value = {"token": "test_token", "user": {"id": 1}}
        
        mock_usecase = AsyncMock()
        mock_analysis_data = AnalysisData(
            filename="test.txt",
            encrypted_filename="encrypted_test",
            file_size=1024,
            analysis_date="2024-01-01T12:00:00Z",
            file_type="text/plain",
            checksum="sha256:abc123",
            metadata={"encoding": "UTF-8"}
        )
        mock_response = AnalysisResponse(
            success=True,
            message="Archivo analizado correctamente",
            data=mock_analysis_data
        )
        mock_usecase.execute.return_value = mock_response
        mock_usecase_class.return_value = mock_usecase
        
        # Crear mock request
        mock_request = MagicMock(spec=Request)
        
        # Ejecutar función
        result = await analyze_file(mock_request, filename="test.txt")
        
        # Verificaciones
        assert result is not None
        assert result.success is True
        assert result.message == "Archivo analizado correctamente"
        assert result.data.filename == "test.txt"
        
        # Verificar que se llamaron los métodos correctos
        mock_logger.set_context.assert_called_once()
        mock_logger.info.assert_any_call("Iniciando análisis de archivo")
        mock_logger.info.assert_any_call("Usuario autenticado correctamente")
        mock_logger.success.assert_called_once_with("Análisis completado exitosamente")
        mock_auth_middleware.assert_called_once_with(mock_request)
        mock_usecase.execute.assert_called_once_with("test.txt", {"token": "test_token", "user": {"id": 1}})

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.controller.analysis_controller.auth_middleware')
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
            await analyze_file(mock_request, filename="nonexistent.txt")
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "File not found"

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.controller.analysis_controller.auth_middleware')
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
            await analyze_file(mock_request, filename="test.txt")
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Error en la base de datos"
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.controller.analysis_controller.auth_middleware')
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
            await analyze_file(mock_request, filename="test.txt")
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Error en la base de datos"

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.controller.analysis_controller.auth_middleware')
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
            await analyze_file(mock_request, filename="test.txt")
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Error interno del servidor"

    @pytest.mark.asyncio
    @patch('app.controller.analysis_controller.AnalysisUseCase')
    @patch('app.controller.analysis_controller.auth_middleware')
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
            analysis_date="2024-01-01T12:00:00Z",
            file_type="application/pdf",
            checksum="sha256:def456",
            metadata={"pages": 5}
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
        result = await analyze_file(mock_request, filename="document.pdf")
        
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