import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
import json

class Logger:
    """Sistema de logging similar al config-service"""
    
    def __init__(self):
        self.logger = logging.getLogger("analysis-service")
        self.context: Dict[str, Any] = {}
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura el logger"""
        # Crear directorio de logs si no existe
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configurar nivel de logging
        self.logger.setLevel(logging.INFO)
        
        # Evitar duplicación de handlers
        if not self.logger.handlers:
            # Handler para archivo
            file_handler = logging.FileHandler(f"{log_dir}/analysis-service.log")
            file_handler.setLevel(logging.INFO)
            
            # Handler para consola
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formato del log
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def set_context(self, function_name: str, data: Optional[Dict[str, Any]] = None):
        """
        Establece el contexto para el logging
        
        Args:
            function_name: Nombre de la función
            data: Datos adicionales del contexto
        """
        self.context = {
            "functionName": function_name,
            "timestamp": datetime.now().isoformat()
        }
        
        if data:
            self.context.update(data)
    
    def _format_message(self, message: str, data: Optional[Any] = None) -> str:
        """
        Formatea el mensaje de log con contexto
        
        Args:
            message: Mensaje principal
            data: Datos adicionales
            
        Returns:
            str: Mensaje formateado
        """
        log_data = {
            "message": message,
            "context": self.context
        }
        
        if data:
            log_data["data"] = data
        
        return json.dumps(log_data, ensure_ascii=False, indent=2)
    
    def info(self, message: str, data: Optional[Any] = None):
        """
        Registra un mensaje de información
        
        Args:
            message: Mensaje a registrar
            data: Datos adicionales
        """
        formatted_message = self._format_message(message, data)
        self.logger.info(formatted_message)
        print(f"\033[94m[INFO]\033[0m {message}")
    
    def error(self, message: str, error: Optional[Any] = None):
        """
        Registra un mensaje de error
        
        Args:
            message: Mensaje de error
            error: Detalles del error
        """
        formatted_message = self._format_message(message, error)
        self.logger.error(formatted_message)
        print(f"\033[91m[ERROR]\033[0m {message}")
    
    def success(self, message: str, data: Optional[Any] = None):
        """
        Registra un mensaje de éxito
        
        Args:
            message: Mensaje de éxito
            data: Datos adicionales
        """
        formatted_message = self._format_message(message, data)
        self.logger.info(formatted_message)
        print(f"\033[92m[SUCCESS]\033[0m {message}")
    
    def get_timestamp(self) -> str:
        """
        Obtiene el timestamp actual en formato ISO
        
        Returns:
            str: Timestamp en formato ISO
        """
        return datetime.now().isoformat() 