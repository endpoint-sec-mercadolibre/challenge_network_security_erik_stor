import pytest
from datetime import datetime
from pydantic import ValidationError
from app.model.analysis_model import (
    AnalysisRequest,
    AnalysisRecord,
    AnalysisData,
    AnalysisResponse,
    ErrorResponse,
)
from app.utils.consts import EXAMPLE_TIMESTAMP


class TestAnalysisRequest:
    """Tests para el modelo AnalysisRequest"""

    def test_analysis_request_valid_data(self):
        """Test que valida la creación de AnalysisRequest con datos válidos"""
        data = {
            "file_name": "test.txt",
            "file_content": "contenido del archivo",
            "analysis_type": "security",
            "user_id": "user123"
        }
        
        request = AnalysisRequest(**data)
        
        assert request.file_name == "test.txt"
        assert request.file_content == "contenido del archivo"
        assert request.analysis_type == "security"
        assert request.user_id == "user123"

    def test_analysis_request_without_user_id(self):
        """Test que valida la creación de AnalysisRequest sin user_id"""
        data = {
            "file_name": "test.txt",
            "file_content": "contenido del archivo",
            "analysis_type": "security"
        }
        
        request = AnalysisRequest(**data)
        
        assert request.file_name == "test.txt"
        assert request.file_content == "contenido del archivo"
        assert request.analysis_type == "security"
        assert request.user_id is None

    def test_analysis_request_missing_required_fields(self):
        """Test que valida que se lance error cuando faltan campos requeridos"""
        data = {
            "file_name": "test.txt",
            "analysis_type": "security"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AnalysisRequest(**data)
        
        assert "file_content" in str(exc_info.value)

    def test_analysis_request_empty_strings(self):
        """Test que valida que se acepten strings vacíos"""
        data = {
            "file_name": "",
            "file_content": "",
            "analysis_type": "",
            "user_id": ""
        }
        
        request = AnalysisRequest(**data)
        
        assert request.file_name == ""
        assert request.file_content == ""
        assert request.analysis_type == ""
        assert request.user_id == ""

    def test_analysis_request_model_config(self):
        """Test que valida la configuración del modelo"""
        request = AnalysisRequest(
            file_name="config.txt",
            file_content="interface eth0\naddress 192.168.1.100",
            analysis_type="security",
            user_id="user123"
        )
        
        # Verificar que el modelo se puede serializar
        json_data = request.model_dump()
        assert json_data["file_name"] == "config.txt"
        assert json_data["file_content"] == "interface eth0\naddress 192.168.1.100"
        assert json_data["analysis_type"] == "security"
        assert json_data["user_id"] == "user123"


class TestAnalysisRecord:
    """Tests para el modelo AnalysisRecord"""

    def test_analysis_record_valid_data(self):
        """Test que valida la creación de AnalysisRecord con datos válidos"""
        data = {
            "analysis_id": "analysis_123",
            "file_name": "config.txt",
            "analysis_type": "security",
            "status": "completed",
            "result": "Análisis de seguridad completado",
            "created_at": "2024-01-01T00:00:00Z",
            "user_id": "user123"
        }
        
        record = AnalysisRecord(**data)
        
        assert record.analysis_id == "analysis_123"
        assert record.file_name == "config.txt"
        assert record.analysis_type == "security"
        assert record.status == "completed"
        assert record.result == "Análisis de seguridad completado"
        assert record.created_at == "2024-01-01T00:00:00Z"
        assert record.user_id == "user123"

    def test_analysis_record_missing_required_fields(self):
        """Test que valida que se lance error cuando faltan campos requeridos"""
        data = {
            "analysis_id": "analysis_123",
            "file_name": "config.txt",
            "analysis_type": "security"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AnalysisRecord(**data)
        
        assert "status" in str(exc_info.value)

    def test_analysis_record_model_config(self):
        """Test que valida la configuración del modelo"""
        record = AnalysisRecord(
            analysis_id="analysis_123",
            file_name="config.txt",
            analysis_type="security",
            status="completed",
            result="Análisis de seguridad completado",
            created_at="2024-01-01T00:00:00Z",
            user_id="user123"
        )
        
        # Verificar que el modelo se puede serializar
        json_data = record.model_dump()
        assert json_data["analysis_id"] == "analysis_123"
        assert json_data["file_name"] == "config.txt"
        assert json_data["analysis_type"] == "security"
        assert json_data["status"] == "completed"
        assert json_data["result"] == "Análisis de seguridad completado"
        assert json_data["created_at"] == "2024-01-01T00:00:00Z"
        assert json_data["user_id"] == "user123"


class TestAnalysisData:
    """Tests para el modelo AnalysisData"""

    def test_analysis_data_valid_data(self):
        """Test que valida la creación de AnalysisData con datos válidos"""
        analysis_date = datetime(2024, 1, 1, 12, 0, 0)
        data = {
            "filename": "document.txt",
            "encrypted_filename": "encrypted_abc123",
            "file_size": 1024,
            "analysis_date": analysis_date,
            "file_type": "text/plain",
            "checksum": "sha256:abc123...",
            "metadata": {"encoding": "UTF-8", "line_count": 50}
        }
        
        analysis_data = AnalysisData(**data)
        
        assert analysis_data.filename == "document.txt"
        assert analysis_data.encrypted_filename == "encrypted_abc123"
        assert analysis_data.file_size == 1024
        assert analysis_data.analysis_date == analysis_date
        assert analysis_data.file_type == "text/plain"
        assert analysis_data.checksum == "sha256:abc123..."
        assert analysis_data.metadata == {"encoding": "UTF-8", "line_count": 50}

    def test_analysis_data_without_optional_fields(self):
        """Test que valida la creación de AnalysisData sin campos opcionales"""
        analysis_date = datetime(2024, 1, 1, 12, 0, 0)
        data = {
            "filename": "document.txt",
            "encrypted_filename": "encrypted_abc123",
            "file_size": 1024,
            "analysis_date": analysis_date,
            "file_type": "text/plain"
        }
        
        analysis_data = AnalysisData(**data)
        
        assert analysis_data.filename == "document.txt"
        assert analysis_data.encrypted_filename == "encrypted_abc123"
        assert analysis_data.file_size == 1024
        assert analysis_data.analysis_date == analysis_date
        assert analysis_data.file_type == "text/plain"
        assert analysis_data.checksum is None
        assert analysis_data.metadata is None

    def test_analysis_data_negative_file_size(self):
        """Test que valida que se lance error con file_size negativo"""
        analysis_date = datetime(2024, 1, 1, 12, 0, 0)
        data = {
            "filename": "document.txt",
            "encrypted_filename": "encrypted_abc123",
            "file_size": -1,
            "analysis_date": analysis_date,
            "file_type": "text/plain"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AnalysisData(**data)
        
        assert "file_size" in str(exc_info.value)

    def test_analysis_data_zero_file_size(self):
        """Test que valida que se acepte file_size cero"""
        analysis_date = datetime(2024, 1, 1, 12, 0, 0)
        data = {
            "filename": "document.txt",
            "encrypted_filename": "encrypted_abc123",
            "file_size": 0,
            "analysis_date": analysis_date,
            "file_type": "text/plain"
        }
        
        analysis_data = AnalysisData(**data)
        assert analysis_data.file_size == 0

    def test_analysis_data_missing_required_fields(self):
        """Test que valida que se lance error cuando faltan campos requeridos"""
        data = {
            "filename": "document.txt",
            "file_size": 1024
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AnalysisData(**data)
        
        assert "encrypted_filename" in str(exc_info.value)

    def test_analysis_data_model_config(self):
        """Test que valida la configuración del modelo"""
        analysis_date = datetime(2024, 1, 1, 12, 0, 0)
        analysis_data = AnalysisData(
            filename="document.txt",
            encrypted_filename="encrypted_abc123",
            file_size=1024,
            analysis_date=analysis_date,
            file_type="text/plain",
            checksum="sha256:abc123...",
            metadata={"encoding": "UTF-8", "line_count": 50}
        )
        
        # Verificar que el modelo se puede serializar
        json_data = analysis_data.model_dump()
        assert json_data["filename"] == "document.txt"
        assert json_data["encrypted_filename"] == "encrypted_abc123"
        assert json_data["file_size"] == 1024
        assert json_data["file_type"] == "text/plain"
        assert json_data["checksum"] == "sha256:abc123..."
        assert json_data["metadata"] == {"encoding": "UTF-8", "line_count": 50}


class TestAnalysisResponse:
    """Tests para el modelo AnalysisResponse"""

    def test_analysis_response_valid_data(self):
        """Test que valida la creación de AnalysisResponse con datos válidos"""
        analysis_date = datetime(2024, 1, 1, 12, 0, 0)
        analysis_data = AnalysisData(
            filename="document.txt",
            encrypted_filename="encrypted_abc123",
            file_size=1024,
            analysis_date=analysis_date,
            file_type="text/plain",
            checksum="sha256:abc123...",
            metadata={"encoding": "UTF-8", "line_count": 50}
        )
        
        response = AnalysisResponse(
            success=True,
            message="Archivo analizado correctamente",
            data=analysis_data
        )
        
        assert response.success is True
        assert response.message == "Archivo analizado correctamente"
        assert response.data == analysis_data

    def test_analysis_response_failure(self):
        """Test que valida la creación de AnalysisResponse con success=False"""
        analysis_date = datetime(2024, 1, 1, 12, 0, 0)
        analysis_data = AnalysisData(
            filename="document.txt",
            encrypted_filename="encrypted_abc123",
            file_size=1024,
            analysis_date=analysis_date,
            file_type="text/plain"
        )
        
        response = AnalysisResponse(
            success=False,
            message="Error en el análisis",
            data=analysis_data
        )
        
        assert response.success is False
        assert response.message == "Error en el análisis"
        assert response.data == analysis_data

    def test_analysis_response_missing_required_fields(self):
        """Test que valida que se lance error cuando faltan campos requeridos"""
        with pytest.raises(ValidationError) as exc_info:
            AnalysisResponse(success=True)
        
        assert "message" in str(exc_info.value)

    def test_analysis_response_model_config(self):
        """Test que valida la configuración del modelo"""
        analysis_date = datetime(2024, 1, 1, 12, 0, 0)
        analysis_data = AnalysisData(
            filename="document.txt",
            encrypted_filename="encrypted_abc123",
            file_size=1024,
            analysis_date=analysis_date,
            file_type="text/plain",
            checksum="sha256:abc123...",
            metadata={"encoding": "UTF-8", "line_count": 50}
        )
        
        response = AnalysisResponse(
            success=True,
            message="Archivo analizado correctamente",
            data=analysis_data
        )
        
        # Verificar que el modelo se puede serializar
        json_data = response.model_dump()
        assert json_data["success"] is True
        assert json_data["message"] == "Archivo analizado correctamente"
        assert "data" in json_data


class TestErrorResponse:
    """Tests para el modelo ErrorResponse"""

    def test_error_response_valid_data(self):
        """Test que valida la creación de ErrorResponse con datos válidos"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        error = ErrorResponse(
            message="Token de autenticación inválido",
            error_code="UNAUTHORIZED",
            detail="El token JWT proporcionado no es válido o ha expirado",
            timestamp=timestamp
        )
        
        assert error.success is False
        assert error.message == "Token de autenticación inválido"
        assert error.error_code == "UNAUTHORIZED"
        assert error.detail == "El token JWT proporcionado no es válido o ha expirado"
        assert error.timestamp == timestamp

    def test_error_response_minimal_data(self):
        """Test que valida la creación de ErrorResponse con datos mínimos"""
        error = ErrorResponse(message="Error simple")
        
        assert error.success is False
        assert error.message == "Error simple"
        assert error.error_code is None
        assert error.detail is None
        assert isinstance(error.timestamp, datetime)

    def test_error_response_without_timestamp(self):
        """Test que valida la creación de ErrorResponse sin timestamp explícito"""
        error = ErrorResponse(
            message="Error sin timestamp",
            error_code="TEST_ERROR"
        )
        
        assert error.success is False
        assert error.message == "Error sin timestamp"
        assert error.error_code == "TEST_ERROR"
        assert error.detail is None
        assert isinstance(error.timestamp, datetime)

    def test_error_response_missing_required_fields(self):
        """Test que valida que se lance error cuando faltan campos requeridos"""
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse()
        
        assert "message" in str(exc_info.value)

    def test_error_response_model_config(self):
        """Test que valida la configuración del modelo"""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        error = ErrorResponse(
            message="Token de autenticación inválido",
            error_code="UNAUTHORIZED",
            detail="El token JWT proporcionado no es válido o ha expirado",
            timestamp=timestamp
        )
        
        # Verificar que el modelo se puede serializar
        json_data = error.model_dump()
        assert json_data["success"] is False
        assert json_data["message"] == "Token de autenticación inválido"
        assert json_data["error_code"] == "UNAUTHORIZED"
        assert json_data["detail"] == "El token JWT proporcionado no es válido o ha expirado"
        assert json_data["timestamp"] == timestamp

    def test_error_response_timestamp_default_factory(self):
        """Test que valida que el timestamp se genere automáticamente"""
        error1 = ErrorResponse(message="Error 1")
        error2 = ErrorResponse(message="Error 2")
        
        # Los timestamps deben ser diferentes
        assert error1.timestamp != error2.timestamp
        assert isinstance(error1.timestamp, datetime)
        assert isinstance(error2.timestamp, datetime)


class TestModelIntegration:
    """Tests de integración entre modelos"""

    def test_analysis_request_to_analysis_record(self):
        """Test que valida la conversión de AnalysisRequest a AnalysisRecord"""
        request = AnalysisRequest(
            file_name="test.txt",
            file_content="contenido",
            analysis_type="security",
            user_id="user123"
        )
        
        record = AnalysisRecord(
            analysis_id="analysis_123",
            file_name=request.file_name,
            analysis_type=request.analysis_type,
            status="completed",
            result="Análisis completado",
            created_at="2024-01-01T00:00:00Z",
            user_id=request.user_id
        )
        
        assert record.file_name == request.file_name
        assert record.analysis_type == request.analysis_type
        assert record.user_id == request.user_id

    def test_analysis_data_to_analysis_response(self):
        """Test que valida la integración de AnalysisData en AnalysisResponse"""
        analysis_date = datetime(2024, 1, 1, 12, 0, 0)
        analysis_data = AnalysisData(
            filename="document.txt",
            encrypted_filename="encrypted_abc123",
            file_size=1024,
            analysis_date=analysis_date,
            file_type="text/plain"
        )
        
        response = AnalysisResponse(
            success=True,
            message="Archivo analizado correctamente",
            data=analysis_data
        )
        
        assert response.data.filename == "document.txt"
        assert response.data.file_size == 1024
        assert response.data.analysis_date == analysis_date

    def test_error_response_in_error_scenario(self):
        """Test que valida el uso de ErrorResponse en un escenario de error"""
        try:
            # Simular un error
            raise ValueError("Error de validación")
        except ValueError as e:
            error_response = ErrorResponse(
                message="Error en el procesamiento",
                error_code="VALIDATION_ERROR",
                detail=str(e)
            )
        
        assert error_response.success is False
        assert error_response.message == "Error en el procesamiento"
        assert error_response.error_code == "VALIDATION_ERROR"
        assert error_response.detail == "Error de validación"


class TestModelValidation:
    """Tests adicionales de validación de modelos"""

    def test_analysis_request_field_descriptions(self):
        """Test que valida las descripciones de los campos"""
        request = AnalysisRequest(
            file_name="test.txt",
            file_content="contenido",
            analysis_type="security"
        )
        
        # Verificar que los campos tienen las descripciones correctas
        schema = request.model_json_schema()
        assert "file_name" in schema["properties"]
        assert "file_content" in schema["properties"]
        assert "analysis_type" in schema["properties"]
        assert "user_id" in schema["properties"]

    def test_analysis_data_field_constraints(self):
        """Test que valida las restricciones de los campos"""
        analysis_date = datetime(2024, 1, 1, 12, 0, 0)
        
        # Test con file_size válido
        data = AnalysisData(
            filename="test.txt",
            encrypted_filename="encrypted_123",
            file_size=0,
            analysis_date=analysis_date,
            file_type="text/plain"
        )
        assert data.file_size >= 0

    def test_model_serialization(self):
        """Test que valida la serialización de todos los modelos"""
        # AnalysisRequest
        request = AnalysisRequest(
            file_name="test.txt",
            file_content="contenido",
            analysis_type="security"
        )
        request_json = request.model_dump_json()
        assert isinstance(request_json, str)
        
        # AnalysisRecord
        record = AnalysisRecord(
            analysis_id="analysis_123",
            file_name="test.txt",
            analysis_type="security",
            status="completed",
            result="Análisis completado",
            created_at="2024-01-01T00:00:00Z",
            user_id="user123"
        )
        record_json = record.model_dump_json()
        assert isinstance(record_json, str)
        
        # AnalysisData
        analysis_date = datetime(2024, 1, 1, 12, 0, 0)
        data = AnalysisData(
            filename="test.txt",
            encrypted_filename="encrypted_123",
            file_size=1024,
            analysis_date=analysis_date,
            file_type="text/plain"
        )
        data_json = data.model_dump_json()
        assert isinstance(data_json, str)
        
        # AnalysisResponse
        response = AnalysisResponse(
            success=True,
            message="Éxito",
            data=data
        )
        response_json = response.model_dump_json()
        assert isinstance(response_json, str)
        
        # ErrorResponse
        error = ErrorResponse(message="Error")
        error_json = error.model_dump_json()
        assert isinstance(error_json, str) 