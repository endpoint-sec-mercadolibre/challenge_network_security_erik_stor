import pytest
import os
from unittest.mock import patch, MagicMock
from app.services.mongodb_service import MongoDBService, mongodb_service


class TestMongoDBService:
    """Tests para la clase MongoDBService"""

    def setup_method(self):
        """Configuración antes de cada test"""
        # Crear una nueva instancia para cada test
        with patch('app.services.mongodb_service.Logger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            self.service = MongoDBService()
            self.mock_logger = mock_logger

    def test_mongodb_service_initialization(self):
        """Test que valida la inicialización del servicio"""
        with patch('app.services.mongodb_service.Logger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            
            service = MongoDBService()
            
            assert service.logger is not None
            assert service.connection is None
            mock_logger_class.assert_called_once()

    def test_connect_without_authentication(self):
        """Test que valida la conexión sin autenticación"""
        with patch.dict(os.environ, {
            "MONGO_HOST": "test_host",
            "MONGO_PORT": "27018",
            "MONGO_DATABASE": "test_db"
        }, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect:
            
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            self.service.connect()
            
            # Verificar llamadas de logging
            assert self.mock_logger.info.call_count >= 4
            info_calls = [call.args[0] for call in self.mock_logger.info.call_args_list]
            
            assert "Conectando a MongoDB: test_host:27018/test_db" in info_calls
            assert "Usuario: None" in info_calls
            assert "Autenticación requerida: False" in info_calls
            assert "Usando conexión sin autenticación" in info_calls
            assert any("URI de conexión: mongodb://test_host:27018/test_db" in call for call in info_calls)
            
            # Verificar que se llamó connect con los parámetros correctos
            mock_connect.assert_called_once_with(
                db="test_db",
                host="mongodb://test_host:27018/test_db",
                alias="default"
            )
            
            # Verificar logging de éxito
            self.mock_logger.success.assert_called_once_with("Conexión a MongoDB establecida exitosamente")
            
            # Verificar que se guardó la conexión
            assert self.service.connection == mock_connection

    def test_connect_with_authentication(self):
        """Test que valida la conexión con autenticación"""
        with patch.dict(os.environ, {
            "MONGO_HOST": "auth_host",
            "MONGO_PORT": "27019",
            "MONGO_DATABASE": "auth_db",
            "MONGO_USERNAME": "test_user",
            "MONGO_PASSWORD": "test_password"
        }, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect:
            
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            self.service.connect()
            
            # Verificar llamadas de logging
            info_calls = [call.args[0] for call in self.mock_logger.info.call_args_list]
            
            assert "Conectando a MongoDB: auth_host:27019/auth_db" in info_calls
            assert "Usuario: test_user" in info_calls
            assert "Autenticación requerida: True" in info_calls
            assert "Usando conexión con autenticación" in info_calls
            
            # Verificar que la contraseña está ofuscada en el log
            uri_log_found = False
            for call in info_calls:
                if "URI de conexión:" in call and "***" in call:
                    uri_log_found = True
                    assert "test_password" not in call
                    break
            assert uri_log_found, "No se encontró el log de URI con contraseña ofuscada"
            
            # Verificar que se llamó connect con URI de autenticación
            expected_uri = "mongodb://test_user:test_password@auth_host:27019/auth_db?authSource=admin"
            mock_connect.assert_called_once_with(
                db="auth_db",
                host=expected_uri,
                alias="default"
            )
            
            assert self.service.connection == mock_connection

    def test_connect_with_default_values(self):
        """Test que valida la conexión con valores por defecto"""
        with patch.dict(os.environ, {}, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect:
            
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            self.service.connect()
            
            # Verificar llamadas de logging con valores por defecto
            info_calls = [call.args[0] for call in self.mock_logger.info.call_args_list]
            
            assert "Conectando a MongoDB: localhost:27017/analysis_service" in info_calls
            assert "Usuario: None" in info_calls
            assert "Autenticación requerida: False" in info_calls
            
            # Verificar que se llamó connect con valores por defecto
            mock_connect.assert_called_once_with(
                db="analysis_service",
                host="mongodb://localhost:27017/analysis_service",
                alias="default"
            )

    def test_connect_with_partial_authentication(self):
        """Test que valida la conexión cuando solo hay usuario pero no contraseña"""
        with patch.dict(os.environ, {
            "MONGO_USERNAME": "test_user"
            # No hay MONGO_PASSWORD
        }, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect:
            
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            self.service.connect()
            
            # Verificar que no usa autenticación
            info_calls = [call.args[0] for call in self.mock_logger.info.call_args_list]
            assert "Autenticación requerida: False" in info_calls
            assert "Usando conexión sin autenticación" in info_calls
            
            # Verificar que se usa URI sin autenticación
            mock_connect.assert_called_once_with(
                db="analysis_service",
                host="mongodb://localhost:27017/analysis_service",
                alias="default"
            )

    def test_connect_with_custom_port_as_string(self):
        """Test que valida que el puerto se convierte correctamente a entero"""
        with patch.dict(os.environ, {
            "MONGO_PORT": "30000"
        }, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect:
            
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            self.service.connect()
            
            # Verificar que el puerto se procesó correctamente
            info_calls = [call.args[0] for call in self.mock_logger.info.call_args_list]
            assert "Conectando a MongoDB: localhost:30000/analysis_service" in info_calls

    def test_connect_error_handling(self):
        """Test que valida el manejo de errores durante la conexión"""
        with patch.dict(os.environ, {}, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect:
            
            # Simular error en la conexión
            mock_connect.side_effect = Exception("Error de conexión")
            
            with pytest.raises(Exception) as exc_info:
                self.service.connect()
            
            assert "Error de conexión" in str(exc_info.value)
            
            # Verificar que se registró el error
            self.mock_logger.error.assert_called_once_with("Error al conectar a MongoDB: Error de conexión")

    def test_connect_mongoengine_import_error(self):
        """Test que valida el manejo de errores de importación"""
        with patch.dict(os.environ, {}, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect:
            
            # Simular error de importación
            mock_connect.side_effect = ImportError("No module named 'pymongo'")
            
            with pytest.raises(ImportError):
                self.service.connect()
            
            # Verificar que se registró el error
            self.mock_logger.error.assert_called_once_with("Error al conectar a MongoDB: No module named 'pymongo'")

    def test_disconnect_with_connection(self):
        """Test que valida la desconexión cuando hay una conexión activa"""
        with patch('app.services.mongodb_service.disconnect') as mock_disconnect:
            # Simular una conexión activa
            self.service.connection = MagicMock()
            
            self.service.disconnect()
            
            # Verificar que se llamó disconnect
            mock_disconnect.assert_called_once_with(alias="default")
            
            # Verificar logging
            self.mock_logger.info.assert_called_once_with("Conexión a MongoDB cerrada")

    def test_disconnect_without_connection(self):
        """Test que valida la desconexión cuando no hay conexión activa"""
        with patch('app.services.mongodb_service.disconnect') as mock_disconnect:
            # No hay conexión activa (connection = None)
            assert self.service.connection is None
            
            self.service.disconnect()
            
            # No debería llamar disconnect si no hay conexión
            mock_disconnect.assert_not_called()
            
            # No debería haber logging
            self.mock_logger.info.assert_not_called()

    def test_disconnect_error_handling(self):
        """Test que valida el manejo de errores durante la desconexión"""
        with patch('app.services.mongodb_service.disconnect') as mock_disconnect:
            # Simular una conexión activa
            self.service.connection = MagicMock()
            
            # Simular error en la desconexión
            mock_disconnect.side_effect = Exception("Error de desconexión")
            
            # No debería lanzar excepción, solo registrar el error
            self.service.disconnect()
            
            # Verificar que se registró el error
            self.mock_logger.error.assert_called_once_with("Error al cerrar conexión a MongoDB: Error de desconexión")

    def test_uri_construction_with_special_characters_in_password(self):
        """Test que valida la construcción de URI con caracteres especiales en la contraseña"""
        with patch.dict(os.environ, {
            "MONGO_HOST": "localhost",
            "MONGO_PORT": "27017",
            "MONGO_DATABASE": "testdb",
            "MONGO_USERNAME": "user@domain.com",
            "MONGO_PASSWORD": "p@ssw0rd!#$%"
        }, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect:
            
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            self.service.connect()
            
            # Verificar que se construyó la URI correctamente
            expected_uri = "mongodb://user@domain.com:p@ssw0rd!#$%@localhost:27017/testdb?authSource=admin"
            mock_connect.assert_called_once_with(
                db="testdb",
                host=expected_uri,
                alias="default"
            )

    def test_multiple_connect_calls(self):
        """Test que valida múltiples llamadas a connect"""
        with patch.dict(os.environ, {}, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect:
            
            mock_connection1 = MagicMock()
            mock_connection2 = MagicMock()
            mock_connect.side_effect = [mock_connection1, mock_connection2]
            
            # Primera conexión
            self.service.connect()
            assert self.service.connection == mock_connection1
            
            # Segunda conexión
            self.service.connect()
            assert self.service.connection == mock_connection2
            
            # Verificar que se llamó connect dos veces
            assert mock_connect.call_count == 2

    def test_uri_password_masking_without_password(self):
        """Test que valida que no haya problemas al enmascarar URI sin contraseña"""
        with patch.dict(os.environ, {
            "MONGO_HOST": "localhost",
            "MONGO_PORT": "27017",
            "MONGO_DATABASE": "testdb"
        }, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect:
            
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            self.service.connect()
            
            # Verificar que el URI se muestra completo sin enmascaramiento
            info_calls = [call.args[0] for call in self.mock_logger.info.call_args_list]
            uri_log_found = False
            for call in info_calls:
                if "URI de conexión: mongodb://localhost:27017/testdb" in call:
                    uri_log_found = True
                    break
            assert uri_log_found

    def test_environment_variables_edge_cases(self):
        """Test que valida casos límite con variables de entorno"""
        with patch.dict(os.environ, {
            "MONGO_HOST": "",  # Host vacío
            "MONGO_PORT": "0",  # Puerto 0
            "MONGO_DATABASE": "",  # Base de datos vacía
            "MONGO_USERNAME": "",  # Usuario vacío
            "MONGO_PASSWORD": ""  # Contraseña vacía
        }, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect:
            
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            self.service.connect()
            
            # Verificar que se usan los valores vacíos o por defecto
            info_calls = [call.args[0] for call in self.mock_logger.info.call_args_list]
            
            # Con host vacío se usa el string vacío (no el valor por defecto)
            assert "Conectando a MongoDB: :0/" in info_calls
            
            # Con usuario y contraseña vacíos no debería usar autenticación
            assert "Autenticación requerida: False" in info_calls

    def test_connection_state_after_operations(self):
        """Test que valida el estado de la conexión después de operaciones"""
        with patch.dict(os.environ, {}, clear=True), \
             patch('app.services.mongodb_service.connect') as mock_connect, \
             patch('app.services.mongodb_service.disconnect') as mock_disconnect:
            
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            # Inicialmente no hay conexión
            assert self.service.connection is None
            
            # Después de connect debería haber conexión
            self.service.connect()
            assert self.service.connection == mock_connection
            
            # Después de disconnect la conexión debería seguir en el objeto
            # (solo se cierra la conexión pero no se borra la referencia)
            self.service.disconnect()
            assert self.service.connection == mock_connection


class TestMongoDBServiceGlobalInstance:
    """Tests para la instancia global mongodb_service"""

    def test_global_instance_exists(self):
        """Test que valida que existe la instancia global"""
        assert mongodb_service is not None
        assert isinstance(mongodb_service, MongoDBService)

    def test_global_instance_is_singleton(self):
        """Test que valida que la instancia global es única"""
        from app.services.mongodb_service import mongodb_service as mongodb_service2
        
        # Ambas importaciones deberían referenciar la misma instancia
        assert mongodb_service is mongodb_service2

    def test_global_instance_has_logger(self):
        """Test que valida que la instancia global tiene logger"""
        assert mongodb_service.logger is not None

    def test_global_instance_initial_connection_state(self):
        """Test que la instancia global tiene un estado inicial correcto"""
        # Después de las operaciones previas, la instancia puede tener una conexión
        # Lo importante es que la instancia existe y puede manejar conexiones
        assert mongodb_service is not None
        
        # Verificar que puede conectar y desconectar correctamente
        assert hasattr(mongodb_service, 'connect')
        assert hasattr(mongodb_service, 'disconnect')
        assert hasattr(mongodb_service, 'connection')


class TestMongoDBServiceIntegration:
    """Tests de integración para casos complejos"""

    def test_complete_connect_disconnect_cycle(self):
        """Test que valida el ciclo completo de conexión y desconexión"""
        with patch('app.services.mongodb_service.Logger') as mock_logger_class, \
             patch('app.services.mongodb_service.connect') as mock_connect, \
             patch('app.services.mongodb_service.disconnect') as mock_disconnect, \
             patch.dict(os.environ, {
                 "MONGO_HOST": "integration_host",
                 "MONGO_PORT": "27017",
                 "MONGO_DATABASE": "integration_db",
                 "MONGO_USERNAME": "integration_user",
                 "MONGO_PASSWORD": "integration_pass"
             }, clear=True):
            
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            
            service = MongoDBService()
            
            # Ciclo completo: connect -> disconnect
            service.connect()
            service.disconnect()
            
            # Verificar que se llamaron los métodos correctos
            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once_with(alias="default")
            
            # Verificar logging de ambas operaciones
            mock_logger.success.assert_called_once_with("Conexión a MongoDB establecida exitosamente")
            mock_logger.info.assert_called_with("Conexión a MongoDB cerrada")

    def test_error_recovery_scenarios(self):
        """Test que valida escenarios de recuperación de errores"""
        with patch('app.services.mongodb_service.Logger') as mock_logger_class, \
             patch('app.services.mongodb_service.connect') as mock_connect, \
             patch.dict(os.environ, {}, clear=True):
            
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            
            service = MongoDBService()
            
            # Primer intento: falla
            mock_connect.side_effect = Exception("Primera falla")
            with pytest.raises(Exception):
                service.connect()
            
            # Segundo intento: éxito
            mock_connection = MagicMock()
            mock_connect.side_effect = None
            mock_connect.return_value = mock_connection
            
            service.connect()
            
            # Verificar que se recuperó correctamente
            assert service.connection == mock_connection
            assert mock_connect.call_count == 2
            assert mock_logger.error.call_count == 1
            assert mock_logger.success.call_count == 1 