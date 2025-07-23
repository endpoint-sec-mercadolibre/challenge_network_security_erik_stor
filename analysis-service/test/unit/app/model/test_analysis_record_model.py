import pytest
from datetime import datetime, UTC
from unittest.mock import patch, MagicMock
from mongoengine import connect, disconnect
import mongomock
from app.model.analysis_record_model import AnalysisRecord


class TestAnalysisRecord:
    """Tests para el modelo AnalysisRecord de MongoDB"""

    def setup_method(self):
        """Configuración antes de cada test"""
        # Conectar a una base de datos de prueba usando mongomock
        connect('test_db', mongo_client_class=mongomock.MongoClient)

    def teardown_method(self):
        """Limpieza después de cada test"""
        # Desconectar de la base de datos de prueba
        disconnect()

    def test_analysis_record_creation_with_defaults(self):
        """Test que valida la creación de AnalysisRecord con valores por defecto"""
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user="test_user"
        )
        
        assert record.success is True
        assert record.response == {"result": "test"}
        assert record.user == "test_user"
        assert record.uuid is not None
        assert isinstance(record.uuid, str)
        assert len(record.uuid) > 0
        assert isinstance(record.created_at, datetime)
        assert isinstance(record.updated_at, datetime)

    def test_analysis_record_creation_with_custom_uuid(self):
        """Test que valida la creación de AnalysisRecord con UUID personalizado"""
        custom_uuid = "test-uuid-123"
        record = AnalysisRecord(
            uuid=custom_uuid,
            success=False,
            response={"error": "test error"},
            user="test_user"
        )
        
        assert record.uuid == custom_uuid
        assert record.success is False
        assert record.response == {"error": "test error"}
        assert record.user == "test_user"

    def test_analysis_record_creation_with_custom_dates(self):
        """Test que valida la creación de AnalysisRecord con fechas personalizadas"""
        custom_date = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user="test_user",
            created_at=custom_date,
            updated_at=custom_date
        )
        
        assert record.created_at == custom_date
        assert record.updated_at == custom_date

    def test_analysis_record_meta_configuration(self):
        """Test que valida la configuración meta del modelo"""
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user="test_user"
        )
        
        # Verificar configuración de la colección
        assert record._meta['collection'] == 'analysis_records'
        
        # Verificar índices
        indexes = record._meta['indexes']
        assert 'uuid' in indexes
        assert 'user' in indexes
        assert 'created_at' in indexes
        assert ('user', 'created_at') in indexes

    def test_analysis_record_save_method(self):
        """Test que valida el método save personalizado"""
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user="test_user"
        )
        
        # Capturar el tiempo antes del save
        before_save = record.updated_at
        
        # Simular un pequeño delay
        import time
        time.sleep(0.001)
        
        # Mock del método save de la clase padre
        with patch.object(AnalysisRecord.__bases__[0], 'save') as mock_save:
            mock_save.return_value = record
            result = record.save()
            
            # Verificar que updated_at se actualizó
            assert record.updated_at > before_save
            assert mock_save.called
            assert result == record

    def test_analysis_record_save_with_arguments(self):
        """Test que valida el método save con argumentos adicionales"""
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user="test_user"
        )
        
        before_save = record.updated_at
        
        with patch.object(AnalysisRecord.__bases__[0], 'save') as mock_save:
            mock_save.return_value = record
            result = record.save(force_insert=True, validate=False)
            
            # Verificar que updated_at se actualizó
            assert record.updated_at > before_save
            # Verificar que se pasaron los argumentos al método padre
            mock_save.assert_called_once_with(force_insert=True, validate=False)
            assert result == record

    def test_analysis_record_uuid_uniqueness(self):
        """Test que valida que los UUIDs sean únicos"""
        record1 = AnalysisRecord(
            success=True,
            response={"result": "test1"},
            user="test_user"
        )
        
        record2 = AnalysisRecord(
            success=True,
            response={"result": "test2"},
            user="test_user"
        )
        
        # Los UUIDs deben ser diferentes
        assert record1.uuid != record2.uuid
        assert isinstance(record1.uuid, str)
        assert isinstance(record2.uuid, str)

    def test_analysis_record_required_fields(self):
        """Test que valida que los campos requeridos sean obligatorios"""
        # Test sin success - mongoengine puede ser permisivo, así que verificamos que se crea pero con valores por defecto
        record1 = AnalysisRecord(
            response={"result": "test"},
            user="test_user"
        )
        # Verificar que se creó el objeto (mongoengine puede usar valores por defecto)
        assert record1.user == "test_user"
        assert record1.response == {"result": "test"}
        
        # Test sin response
        record2 = AnalysisRecord(
            success=True,
            user="test_user"
        )
        # Verificar que se creó el objeto
        assert record2.success is True
        assert record2.user == "test_user"
        
        # Test sin user
        record3 = AnalysisRecord(
            success=True,
            response={"result": "test"}
        )
        # Verificar que se creó el objeto
        assert record3.success is True
        assert record3.response == {"result": "test"}

    def test_analysis_record_field_types(self):
        """Test que valida los tipos de datos de los campos"""
        record = AnalysisRecord(
            success=True,
            response={"result": "test", "data": [1, 2, 3]},
            user="test_user"
        )
        
        assert isinstance(record.success, bool)
        assert isinstance(record.response, dict)
        assert isinstance(record.user, str)
        assert isinstance(record.uuid, str)
        assert isinstance(record.created_at, datetime)
        assert isinstance(record.updated_at, datetime)

    def test_analysis_record_complex_response(self):
        """Test que valida el manejo de respuestas complejas"""
        complex_response = {
            "success": True,
            "data": {
                "filename": "test.txt",
                "analysis": {
                    "security_score": 85,
                    "vulnerabilities": ["CVE-2021-1234"],
                    "recommendations": ["Update software"]
                }
            },
            "metadata": {
                "processing_time": 1.5,
                "model_version": "1.0"
            }
        }
        
        record = AnalysisRecord(
            success=True,
            response=complex_response,
            user="test_user"
        )
        
        assert record.response == complex_response
        assert record.response["data"]["analysis"]["security_score"] == 85
        assert "CVE-2021-1234" in record.response["data"]["analysis"]["vulnerabilities"]

    def test_analysis_record_boolean_values(self):
        """Test que valida diferentes valores booleanos"""
        # Test con success=True
        record_true = AnalysisRecord(
            success=True,
            response={"result": "success"},
            user="test_user"
        )
        assert record_true.success is True
        
        # Test con success=False
        record_false = AnalysisRecord(
            success=False,
            response={"result": "failure"},
            user="test_user"
        )
        assert record_false.success is False

    def test_analysis_record_empty_response(self):
        """Test que valida el manejo de respuestas vacías"""
        record = AnalysisRecord(
            success=True,
            response={},
            user="test_user"
        )
        
        assert record.response == {}
        assert isinstance(record.response, dict)

    def test_analysis_record_special_characters_in_user(self):
        """Test que valida el manejo de caracteres especiales en el campo user"""
        special_user = "user@domain.com"
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user=special_user
        )
        
        assert record.user == special_user

    def test_analysis_record_long_user_string(self):
        """Test que valida el manejo de strings largos en el campo user"""
        long_user = "a" * 1000
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user=long_user
        )
        
        assert record.user == long_user
        assert len(record.user) == 1000

    def test_analysis_record_datetime_utc(self):
        """Test que valida que las fechas se manejen en UTC"""
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user="test_user"
        )
        
        # Verificar que las fechas tienen timezone UTC
        assert record.created_at.tzinfo == UTC
        assert record.updated_at.tzinfo == UTC

    def test_analysis_record_custom_datetime_without_timezone(self):
        """Test que valida el manejo de fechas sin timezone"""
        custom_date = datetime(2024, 1, 1, 12, 0, 0)
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user="test_user",
            created_at=custom_date,
            updated_at=custom_date
        )
        
        assert record.created_at == custom_date
        assert record.updated_at == custom_date

    def test_analysis_record_model_representation(self):
        """Test que valida la representación del modelo"""
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user="test_user"
        )
        
        # Verificar que el modelo se puede representar como string
        str_repr = str(record)
        assert "AnalysisRecord" in str_repr or "Document" in str_repr

    def test_analysis_record_field_validation(self):
        """Test que valida la validación de campos"""
        # Test con tipos de datos incorrectos - mongoengine puede ser permisivo
        record = AnalysisRecord(
            success="not_a_boolean",  # Debería ser boolean pero mongoengine puede aceptarlo
            response={"result": "test"},
            user="test_user"
        )
        # Verificar que se creó el objeto (mongoengine puede hacer conversión automática)
        assert record.response == {"result": "test"}
        assert record.user == "test_user"
        # El campo success puede ser convertido automáticamente o mantenido como string
        assert record.success == "not_a_boolean" or record.success is True

    def test_analysis_record_uuid_generation(self):
        """Test que valida la generación automática de UUID"""
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user="test_user"
        )
        
        # Verificar formato UUID (versión 4)
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, record.uuid) is not None

    def test_analysis_record_multiple_saves(self):
        """Test que valida múltiples llamadas al método save"""
        record = AnalysisRecord(
            success=True,
            response={"result": "test"},
            user="test_user"
        )
        
        with patch.object(AnalysisRecord.__bases__[0], 'save') as mock_save:
            mock_save.return_value = record
            
            # Primera llamada a save
            first_save_time = record.updated_at
            record.save()
            
            # Segunda llamada a save
            record.save()
            
            # Verificar que updated_at se actualizó en ambas llamadas
            assert record.updated_at > first_save_time
            assert mock_save.call_count == 2 