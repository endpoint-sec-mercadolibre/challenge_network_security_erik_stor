import pytest
from unittest.mock import patch, MagicMock
from app.model.analysis_repository import AnalysisRepository
from app.model.analysis_record_model import AnalysisRecord


class TestAnalysisRepository:
    """Tests para el repositorio AnalysisRepository"""

    def setup_method(self):
        """Configuración antes de cada test"""
        self.repository = AnalysisRepository()

    def test_analysis_repository_initialization(self):
        """Test que valida la inicialización del repositorio"""
        repository = AnalysisRepository()

        assert repository.logger is not None
        assert hasattr(repository.logger, "info")
        assert hasattr(repository.logger, "success")
        assert hasattr(repository.logger, "error")

    def test_save_analysis_record_success(self):
        """Test que valida el guardado exitoso de un registro de análisis"""
        success = True
        response = {"result": "Análisis completado", "score": 85}
        user = "test_user"

        # Mock del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "success"
        ) as mock_success, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_record.uuid = "test-uuid-123"
            mock_analysis_record_class.return_value = mock_record
            mock_record.save.return_value = mock_record

            # Llamar al método
            result = self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar que se llamaron los métodos del logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_success.assert_called_once_with(
                f"Registro guardado exitosamente con UUID: {mock_record.uuid}"
            )

            # Verificar que se llamó el método save
            mock_record.save.assert_called_once()

            # Verificar el resultado
            assert result == mock_record

    def test_save_analysis_record_failure(self):
        """Test que valida el guardado de un registro de análisis fallido"""
        success = False
        response = {"error": "Error en el análisis", "details": "Timeout"}
        user = "test_user"

        # Mock del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "success"
        ) as mock_success, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_record.uuid = "test-uuid-456"
            mock_analysis_record_class.return_value = mock_record
            mock_record.save.return_value = mock_record

            # Llamar al método
            result = self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar que se llamaron los métodos del logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_success.assert_called_once_with(
                f"Registro guardado exitosamente con UUID: {mock_record.uuid}"
            )

            # Verificar que se llamó el método save
            mock_record.save.assert_called_once()

            # Verificar el resultado
            assert result == mock_record

    def test_save_analysis_record_with_complex_response(self):
        """Test que valida el guardado con una respuesta compleja"""
        success = True
        complex_response = {
            "success": True,
            "data": {
                "filename": "config.txt",
                "analysis": {
                    "security_score": 92,
                    "vulnerabilities": [
                        {"id": "CVE-2021-1234", "severity": "HIGH"},
                        {"id": "CVE-2021-5678", "severity": "MEDIUM"},
                    ],
                    "recommendations": [
                        "Update OpenSSL to version 1.1.1k",
                        "Enable HTTPS for all connections",
                    ],
                },
            },
            "metadata": {
                "processing_time": 2.5,
                "model_version": "2.1.0",
                "timestamp": "2024-01-01T12:00:00Z",
            },
        }
        user = "admin@company.com"

        # Mock del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "success"
        ) as mock_success, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_record.uuid = "complex-uuid-789"
            mock_analysis_record_class.return_value = mock_record
            mock_record.save.return_value = mock_record

            # Llamar al método
            result = self.repository.save_analysis_record(
                success, complex_response, user
            )

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=complex_response, user=user
            )

            # Verificar que se llamaron los métodos del logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_success.assert_called_once_with(
                f"Registro guardado exitosamente con UUID: {mock_record.uuid}"
            )

            # Verificar que se llamó el método save
            mock_record.save.assert_called_once()

            # Verificar el resultado
            assert result == mock_record

    def test_save_analysis_record_with_empty_response(self):
        """Test que valida el guardado con una respuesta vacía"""
        success = True
        response = {}
        user = "test_user"

        # Mock del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "success"
        ) as mock_success, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_record.uuid = "empty-uuid-000"
            mock_analysis_record_class.return_value = mock_record
            mock_record.save.return_value = mock_record

            # Llamar al método
            result = self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar que se llamaron los métodos del logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_success.assert_called_once_with(
                f"Registro guardado exitosamente con UUID: {mock_record.uuid}"
            )

            # Verificar que se llamó el método save
            mock_record.save.assert_called_once()

            # Verificar el resultado
            assert result == mock_record

    def test_save_analysis_record_with_special_characters_in_user(self):
        """Test que valida el guardado con caracteres especiales en el usuario"""
        success = True
        response = {"result": "test"}
        user = "user@domain.com+test"

        # Mock del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "success"
        ) as mock_success, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_record.uuid = "special-uuid-111"
            mock_analysis_record_class.return_value = mock_record
            mock_record.save.return_value = mock_record

            # Llamar al método
            result = self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar que se llamaron los métodos del logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_success.assert_called_once_with(
                f"Registro guardado exitosamente con UUID: {mock_record.uuid}"
            )

            # Verificar que se llamó el método save
            mock_record.save.assert_called_once()

            # Verificar el resultado
            assert result == mock_record

    def test_save_analysis_record_mongodb_error(self):
        """Test que valida el manejo de errores de MongoDB"""
        success = True
        response = {"result": "test"}
        user = "test_user"

        # Mock del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "error"
        ) as mock_error, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_analysis_record_class.return_value = mock_record

            # Simular un error de MongoDB
            mongodb_error = Exception("Connection timeout")
            mock_record.save.side_effect = mongodb_error

            # Llamar al método y verificar que se lanza la excepción
            with pytest.raises(RuntimeError) as exc_info:
                self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar que se llamaron los métodos del logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_error.assert_called_once_with(
                f"Error al guardar registro de análisis: {str(mongodb_error)}"
            )

            # Verificar el mensaje de error
            assert "Error de MongoDB: Connection timeout" in str(exc_info.value)

    def test_save_analysis_record_validation_error(self):
        """Test que valida el manejo de errores de validación"""
        success = True
        response = {"result": "test"}
        user = "test_user"

        # Mock del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "error"
        ) as mock_error, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_analysis_record_class.return_value = mock_record

            # Simular un error de validación
            validation_error = ValueError("Invalid field value")
            mock_record.save.side_effect = validation_error

            # Llamar al método y verificar que se lanza la excepción
            with pytest.raises(RuntimeError) as exc_info:
                self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar que se llamaron los métodos del logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_error.assert_called_once_with(
                f"Error al guardar registro de análisis: {str(validation_error)}"
            )

            # Verificar el mensaje de error
            assert "Error de MongoDB: Invalid field value" in str(exc_info.value)

    def test_save_analysis_record_connection_error(self):
        """Test que valida el manejo de errores de conexión"""
        success = True
        response = {"result": "test"}
        user = "test_user"

        # Mock del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "error"
        ) as mock_error, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_analysis_record_class.return_value = mock_record

            # Simular un error de conexión
            connection_error = ConnectionError("Database connection failed")
            mock_record.save.side_effect = connection_error

            # Llamar al método y verificar que se lanza la excepción
            with pytest.raises(RuntimeError) as exc_info:
                self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar que se llamaron los métodos del logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_error.assert_called_once_with(
                f"Error al guardar registro de análisis: {str(connection_error)}"
            )

            # Verificar el mensaje de error
            assert "Error de MongoDB: Database connection failed" in str(exc_info.value)

    def test_save_analysis_record_analysis_record_creation(self):
        """Test que valida la creación correcta del objeto AnalysisRecord"""
        success = False
        response = {"error": "Analysis failed"}
        user = "test_user"

        # Mock del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "success"
        ) as mock_success, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_record.uuid = "test-uuid-999"
            mock_analysis_record_class.return_value = mock_record
            mock_record.save.return_value = mock_record

            # Llamar al método
            result = self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar que se llamaron los métodos del logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_success.assert_called_once_with(
                f"Registro guardado exitosamente con UUID: {mock_record.uuid}"
            )

            # Verificar el resultado
            assert result == mock_record

    def test_save_analysis_record_logger_integration(self):
        """Test que valida la integración completa con el logger"""
        success = True
        response = {"result": "successful analysis"}
        user = "integration_test_user"

        # Mock completo del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "success"
        ) as mock_success, patch.object(
            self.repository.logger, "error"
        ) as mock_error, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_record.uuid = "integration-uuid-123"
            mock_analysis_record_class.return_value = mock_record
            mock_record.save.return_value = mock_record

            # Llamar al método
            result = self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar la secuencia de llamadas al logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_success.assert_called_once_with(
                f"Registro guardado exitosamente con UUID: {mock_record.uuid}"
            )
            mock_error.assert_not_called()  # No debería llamarse en caso de éxito

            # Verificar el resultado
            assert result == mock_record

    def test_save_analysis_record_error_logger_integration(self):
        """Test que valida la integración del logger en caso de error"""
        success = True
        response = {"result": "test"}
        user = "error_test_user"

        # Mock completo del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "success"
        ) as mock_success, patch.object(
            self.repository.logger, "error"
        ) as mock_error, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_analysis_record_class.return_value = mock_record

            # Simular un error
            test_error = Exception("Test error message")
            mock_record.save.side_effect = test_error

            # Llamar al método y verificar que se lanza la excepción
            with pytest.raises(RuntimeError):
                self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar la secuencia de llamadas al logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_error.assert_called_once_with(
                f"Error al guardar registro de análisis: {str(test_error)}"
            )
            mock_success.assert_not_called()  # No debería llamarse en caso de error

    def test_save_analysis_record_boolean_values(self):
        """Test que valida diferentes valores booleanos para success"""
        response = {"result": "test"}
        user = "test_user"

        # Test con success=True
        with patch.object(self.repository.logger, "info"), patch.object(
            self.repository.logger, "success"
        ), patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            mock_record = MagicMock()
            mock_record.uuid = "bool-true-uuid"
            mock_analysis_record_class.return_value = mock_record
            mock_record.save.return_value = mock_record

            result = self.repository.save_analysis_record(True, response, user)
            assert result == mock_record
            mock_analysis_record_class.assert_called_once_with(
                success=True, response=response, user=user
            )

        # Test con success=False
        with patch.object(self.repository.logger, "info"), patch.object(
            self.repository.logger, "success"
        ), patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            mock_record = MagicMock()
            mock_record.uuid = "bool-false-uuid"
            mock_analysis_record_class.return_value = mock_record
            mock_record.save.return_value = mock_record

            result = self.repository.save_analysis_record(False, response, user)
            assert result == mock_record
            mock_analysis_record_class.assert_called_once_with(
                success=False, response=response, user=user
            )

    def test_save_analysis_record_empty_user(self):
        """Test que valida el manejo de usuarios vacíos"""
        success = True
        response = {"result": "test"}
        user = ""

        # Mock del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "success"
        ) as mock_success, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_record.uuid = "empty-user-uuid"
            mock_analysis_record_class.return_value = mock_record
            mock_record.save.return_value = mock_record

            # Llamar al método
            result = self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar que se llamaron los métodos del logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_success.assert_called_once_with(
                f"Registro guardado exitosamente con UUID: {mock_record.uuid}"
            )

            # Verificar el resultado
            assert result == mock_record

    def test_save_analysis_record_none_values(self):
        """Test que valida el manejo de valores None"""
        success = True
        response = None
        user = "test_user"

        # Mock del logger y AnalysisRecord
        with patch.object(self.repository.logger, "info") as mock_info, patch.object(
            self.repository.logger, "success"
        ) as mock_success, patch(
            "app.model.analysis_repository.AnalysisRecord"
        ) as mock_analysis_record_class:

            # Configurar el mock de AnalysisRecord
            mock_record = MagicMock()
            mock_record.uuid = "none-values-uuid"
            mock_analysis_record_class.return_value = mock_record
            mock_record.save.return_value = mock_record

            # Llamar al método
            result = self.repository.save_analysis_record(success, response, user)

            # Verificar que se creó el AnalysisRecord con los parámetros correctos
            mock_analysis_record_class.assert_called_once_with(
                success=success, response=response, user=user
            )

            # Verificar que se llamaron los métodos del logger
            mock_info.assert_called_once_with(
                f"Guardando registro de análisis para usuario: {user}"
            )
            mock_success.assert_called_once_with(
                f"Registro guardado exitosamente con UUID: {mock_record.uuid}"
            )

            # Verificar el resultado
            assert result == mock_record
