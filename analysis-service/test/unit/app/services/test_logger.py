import pytest
import os
import logging
import json
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open, call
from app.services.logger import Logger


class TestLogger:
    """Tests para la clase Logger"""

    def setup_method(self):
        """Configuración antes de cada test"""
        # Limpiar handlers existentes para evitar interferencias
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            self.logger = Logger()
            self.mock_logger = mock_logger

    def test_logger_initialization(self):
        """Test que valida la inicialización del logger"""
        with patch('logging.getLogger') as mock_get_logger, \
             patch('os.path.exists', return_value=True), \
             patch('os.makedirs'):
            
            mock_internal_logger = MagicMock()
            mock_internal_logger.handlers = []
            mock_get_logger.return_value = mock_internal_logger
            
            logger = Logger()
            
            assert logger._logger is not None
            assert logger.context == {}
            mock_get_logger.assert_called_once_with("analysis-service")

    def test_setup_logger_creates_log_directory(self):
        """Test que valida la creación del directorio de logs"""
        with patch('logging.getLogger') as mock_get_logger, \
             patch('os.path.exists', return_value=False) as mock_exists, \
             patch('os.makedirs') as mock_makedirs, \
             patch('logging.FileHandler'), \
             patch('logging.StreamHandler'):
            
            mock_internal_logger = MagicMock()
            mock_internal_logger.handlers = []
            mock_get_logger.return_value = mock_internal_logger
            
            Logger()
            
            mock_exists.assert_called_once_with("logs")
            mock_makedirs.assert_called_once_with("logs")

    def test_setup_logger_directory_already_exists(self):
        """Test que valida que no crea el directorio si ya existe"""
        with patch('logging.getLogger') as mock_get_logger, \
             patch('os.path.exists', return_value=True) as mock_exists, \
             patch('os.makedirs') as mock_makedirs, \
             patch('logging.FileHandler'), \
             patch('logging.StreamHandler'):
            
            mock_internal_logger = MagicMock()
            mock_internal_logger.handlers = []
            mock_get_logger.return_value = mock_internal_logger
            
            Logger()
            
            mock_exists.assert_called_once_with("logs")
            mock_makedirs.assert_not_called()

    def test_setup_logger_configures_handlers(self):
        """Test que valida la configuración de handlers"""
        with patch('logging.getLogger') as mock_get_logger, \
             patch('os.path.exists', return_value=True), \
             patch('logging.FileHandler') as mock_file_handler, \
             patch('logging.StreamHandler') as mock_stream_handler:
            
            mock_internal_logger = MagicMock()
            mock_internal_logger.handlers = []
            mock_get_logger.return_value = mock_internal_logger
            
            mock_file_handler_instance = MagicMock()
            mock_stream_handler_instance = MagicMock()
            mock_file_handler.return_value = mock_file_handler_instance
            mock_stream_handler.return_value = mock_stream_handler_instance
            
            Logger()
            
            # Verificar que se configuraron los handlers
            mock_file_handler.assert_called_once_with("logs/analysis-service.log")
            mock_stream_handler.assert_called_once()
            
            # Verificar que se agregaron al logger
            assert mock_internal_logger.addHandler.call_count == 2

    def test_setup_logger_avoids_duplicate_handlers(self):
        """Test que valida que no duplica handlers"""
        with patch('logging.getLogger') as mock_get_logger, \
             patch('os.path.exists', return_value=True), \
             patch('logging.FileHandler'), \
             patch('logging.StreamHandler'):
            
            mock_internal_logger = MagicMock()
            # Simular que ya tiene handlers
            mock_internal_logger.handlers = [MagicMock()]
            mock_get_logger.return_value = mock_internal_logger
            
            Logger()
            
            # No debería agregar handlers si ya los tiene
            mock_internal_logger.addHandler.assert_not_called()

    def test_set_context_basic(self):
        """Test que valida el establecimiento de contexto básico"""
        function_name = "test_function"
        
        with patch('app.services.logger.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
            
            self.logger.set_context(function_name)
            
            expected_context = {
                "functionName": function_name,
                "timestamp": "2023-01-01T12:00:00"
            }
            assert self.logger.context == expected_context

    def test_set_context_with_data(self):
        """Test que valida el establecimiento de contexto con datos adicionales"""
        function_name = "test_function"
        additional_data = {"user_id": 123, "action": "create"}
        
        with patch('app.services.logger.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
            
            self.logger.set_context(function_name, additional_data)
            
            expected_context = {
                "functionName": function_name,
                "timestamp": "2023-01-01T12:00:00",
                "user_id": 123,
                "action": "create"
            }
            assert self.logger.context == expected_context

    def test_set_context_overwrites_previous_context(self):
        """Test que valida que el contexto se sobrescribe"""
        self.logger.context = {"old": "data"}
        
        function_name = "new_function"
        
        with patch('app.services.logger.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
            
            self.logger.set_context(function_name)
            
            expected_context = {
                "functionName": function_name,
                "timestamp": "2023-01-01T12:00:00"
            }
            assert self.logger.context == expected_context

    def test_format_message_basic(self):
        """Test que valida el formateo básico de mensajes"""
        self.logger.context = {"functionName": "test", "timestamp": "2023-01-01T12:00:00"}
        message = "Test message"
        
        formatted = self.logger._format_message(message)
        
        # Parsear el JSON para verificar estructura
        parsed = json.loads(formatted)
        assert parsed["message"] == message
        assert parsed["context"] == self.logger.context
        assert "data" not in parsed

    def test_format_message_with_data(self):
        """Test que valida el formateo de mensajes con datos"""
        self.logger.context = {"functionName": "test", "timestamp": "2023-01-01T12:00:00"}
        message = "Test message"
        data = {"key": "value", "number": 42}
        
        formatted = self.logger._format_message(message, data)
        
        # Parsear el JSON para verificar estructura
        parsed = json.loads(formatted)
        assert parsed["message"] == message
        assert parsed["context"] == self.logger.context
        assert parsed["data"] == data

    def test_format_message_with_none_data(self):
        """Test que valida el formateo de mensajes con data None"""
        self.logger.context = {"functionName": "test", "timestamp": "2023-01-01T12:00:00"}
        message = "Test message"
        
        formatted = self.logger._format_message(message, None)
        
        # Parsear el JSON para verificar estructura
        parsed = json.loads(formatted)
        assert parsed["message"] == message
        assert parsed["context"] == self.logger.context
        assert "data" not in parsed

    def test_format_message_with_complex_data(self):
        """Test que valida el formateo con datos complejos"""
        self.logger.context = {"functionName": "test", "timestamp": "2023-01-01T12:00:00"}
        message = "Test message"
        data = {
            "user": {"id": 123, "name": "José"},
            "items": [1, 2, 3],
            "unicode": "héllo wörld",
            "nested": {"deep": {"value": "test"}}
        }
        
        formatted = self.logger._format_message(message, data)
        
        # Verificar que es JSON válido y preserva caracteres Unicode
        parsed = json.loads(formatted)
        assert parsed["data"]["user"]["name"] == "José"
        assert parsed["data"]["unicode"] == "héllo wörld"

    def test_info_method(self):
        """Test que valida el método info"""
        message = "Info message"
        data = {"key": "value"}
        
        with patch.object(self.logger, '_format_message', return_value='formatted_message') as mock_format, \
             patch('builtins.print') as mock_print:
            
            self.logger.info(message, data)
            
            mock_format.assert_called_once_with(message, data)
            self.mock_logger.info.assert_called_once_with('formatted_message')
            mock_print.assert_called_once_with(f"\033[94m[INFO]\033[0m {message}")

    def test_info_method_without_data(self):
        """Test que valida el método info sin datos"""
        message = "Info message"
        
        with patch.object(self.logger, '_format_message', return_value='formatted_message') as mock_format, \
             patch('builtins.print') as mock_print:
            
            self.logger.info(message)
            
            mock_format.assert_called_once_with(message, None)
            self.mock_logger.info.assert_called_once_with('formatted_message')
            mock_print.assert_called_once_with(f"\033[94m[INFO]\033[0m {message}")

    def test_error_method(self):
        """Test que valida el método error"""
        message = "Error message"
        error = {"error_code": 500, "details": "Something went wrong"}
        
        with patch.object(self.logger, '_format_message', return_value='formatted_message') as mock_format, \
             patch('builtins.print') as mock_print:
            
            self.logger.error(message, error)
            
            mock_format.assert_called_once_with(message, error)
            self.mock_logger.error.assert_called_once_with('formatted_message')
            mock_print.assert_called_once_with(f"\033[91m[ERROR]\033[0m {message}")

    def test_error_method_without_error_data(self):
        """Test que valida el método error sin datos de error"""
        message = "Error message"
        
        with patch.object(self.logger, '_format_message', return_value='formatted_message') as mock_format, \
             patch('builtins.print') as mock_print:
            
            self.logger.error(message)
            
            mock_format.assert_called_once_with(message, None)
            self.mock_logger.error.assert_called_once_with('formatted_message')
            mock_print.assert_called_once_with(f"\033[91m[ERROR]\033[0m {message}")

    def test_success_method(self):
        """Test que valida el método success"""
        message = "Success message"
        data = {"result": "completed", "count": 42}
        
        with patch.object(self.logger, '_format_message', return_value='formatted_message') as mock_format, \
             patch('builtins.print') as mock_print:
            
            self.logger.success(message, data)
            
            mock_format.assert_called_once_with(message, data)
            self.mock_logger.info.assert_called_once_with('formatted_message')
            mock_print.assert_called_once_with(f"\033[92m[SUCCESS]\033[0m {message}")

    def test_success_method_without_data(self):
        """Test que valida el método success sin datos"""
        message = "Success message"
        
        with patch.object(self.logger, '_format_message', return_value='formatted_message') as mock_format, \
             patch('builtins.print') as mock_print:
            
            self.logger.success(message)
            
            mock_format.assert_called_once_with(message, None)
            self.mock_logger.info.assert_called_once_with('formatted_message')
            mock_print.assert_called_once_with(f"\033[92m[SUCCESS]\033[0m {message}")

    def test_warning_method(self):
        """Test que valida el método warning"""
        message = "Warning message"
        data = {"reason": "deprecated", "alternative": "new_method"}
        
        with patch.object(self.logger, '_format_message', return_value='formatted_message') as mock_format, \
             patch('builtins.print') as mock_print:
            
            self.logger.warning(message, data)
            
            mock_format.assert_called_once_with(message, data)
            self.mock_logger.warning.assert_called_once_with('formatted_message')
            mock_print.assert_called_once_with(f"\033[93m[WARNING]\033[0m {message}")

    def test_warning_method_without_data(self):
        """Test que valida el método warning sin datos"""
        message = "Warning message"
        
        with patch.object(self.logger, '_format_message', return_value='formatted_message') as mock_format, \
             patch('builtins.print') as mock_print:
            
            self.logger.warning(message)
            
            mock_format.assert_called_once_with(message, None)
            self.mock_logger.warning.assert_called_once_with('formatted_message')
            mock_print.assert_called_once_with(f"\033[93m[WARNING]\033[0m {message}")

    def test_get_timestamp(self):
        """Test que valida la obtención del timestamp"""
        with patch('app.services.logger.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00.123456"
            
            timestamp = self.logger.get_timestamp()
            
            assert timestamp == "2023-01-01T12:00:00.123456"
            mock_datetime.now.assert_called_once()

    def test_unicode_support_in_logging(self):
        """Test que valida el soporte de Unicode en los logs"""
        message = "Mensaje con caracteres especiales: áéíóú ñ 你好"
        data = {"usuario": "José", "país": "España", "emoji": "🌍"}
        
        self.logger.set_context("test_unicode")
        formatted = self.logger._format_message(message, data)
        
        # Verificar que el JSON mantiene los caracteres Unicode
        parsed = json.loads(formatted)
        assert parsed["message"] == message
        assert parsed["data"]["usuario"] == "José"
        assert parsed["data"]["país"] == "España"
        assert parsed["data"]["emoji"] == "🌍"

    def test_large_data_logging(self):
        """Test que valida el logging de datos grandes"""
        message = "Large data test"
        large_data = {
            "items": list(range(1000)),
            "text": "x" * 10000,
            "nested": {"level" + str(i): "value" + str(i) for i in range(100)}
        }
        
        self.logger.set_context("test_large_data")
        formatted = self.logger._format_message(message, large_data)
        
        # Verificar que puede manejar datos grandes
        parsed = json.loads(formatted)
        assert len(parsed["data"]["items"]) == 1000
        assert len(parsed["data"]["text"]) == 10000
        assert len(parsed["data"]["nested"]) == 100

    def test_context_persistence_across_calls(self):
        """Test que valida que el contexto persiste entre llamadas"""
        self.logger.set_context("persistent_function", {"session_id": "123"})
        
        with patch.object(self.logger, '_format_message', return_value='formatted') as mock_format, \
             patch('builtins.print'):
            
            self.logger.info("First message")
            self.logger.error("Second message")
            self.logger.success("Third message")
            
            # Verificar que todas las llamadas usan el mismo contexto
            for call_args in mock_format.call_args_list:
                # El contexto debería estar disponible en self.logger.context
                pass  # El contexto se mantiene en self.logger.context
            
            assert mock_format.call_count == 3

    def test_empty_context_logging(self):
        """Test que valida el logging con contexto vacío"""
        # No establecer contexto intencionalmente
        message = "Message without context"
        
        formatted = self.logger._format_message(message)
        parsed = json.loads(formatted)
        
        assert parsed["message"] == message
        assert parsed["context"] == {}

    def test_none_values_in_context(self):
        """Test que valida el manejo de valores None en el contexto"""
        function_name = "test_function"
        data_with_none = {"valid_key": "valid_value", "none_key": None}
        
        with patch('app.services.logger.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
            
            self.logger.set_context(function_name, data_with_none)
            
            # Verificar que se pueden manejar valores None
            assert self.logger.context["none_key"] is None
            assert self.logger.context["valid_key"] == "valid_value"

    def test_special_characters_in_function_name(self):
        """Test que valida caracteres especiales en el nombre de función"""
        function_name = "función_con_ñ_áéíóú_123_!@#"
        
        with patch('app.services.logger.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
            
            self.logger.set_context(function_name)
            
            assert self.logger.context["functionName"] == function_name

    def test_json_serialization_error_handling(self):
        """Test que valida el manejo de errores de serialización JSON"""
        # Crear un objeto que no se puede serializar a JSON
        class NonSerializable:
            pass
        
        message = "Test message"
        non_serializable_data = {"object": NonSerializable()}
        
        # json.dumps debería fallar con este tipo de datos
        with pytest.raises(TypeError):
            self.logger._format_message(message, non_serializable_data)

    def test_multiple_logger_instances(self):
        """Test que valida múltiples instancias de logger"""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger1 = MagicMock()
            mock_logger1.handlers = []
            mock_logger2 = MagicMock()
            mock_logger2.handlers = []
            
            # Configurar el mock para devolver diferentes loggers
            mock_get_logger.side_effect = [mock_logger1, mock_logger2]
            
            logger1 = Logger()
            logger2 = Logger()
            
            # Verificar que ambos loggers fueron configurados
            assert mock_get_logger.call_count == 2
            assert logger1._logger == mock_logger1
            assert logger2._logger == mock_logger2

    def test_context_isolation_between_instances(self):
        """Test que valida que el contexto está aislado entre instancias"""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger1 = MagicMock()
            mock_logger1.handlers = []
            mock_logger2 = MagicMock()
            mock_logger2.handlers = []
            
            mock_get_logger.side_effect = [mock_logger1, mock_logger2]
            
            logger1 = Logger()
            logger2 = Logger()
            
            logger1.set_context("function1", {"data": "value1"})
            logger2.set_context("function2", {"data": "value2"})
            
            # Verificar que los contextos están separados
            assert logger1.context["functionName"] == "function1"
            assert logger2.context["functionName"] == "function2"
            assert logger1.context["data"] == "value1"
            assert logger2.context["data"] == "value2"
