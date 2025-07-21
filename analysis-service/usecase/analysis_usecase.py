from datetime import datetime
from typing import Optional

from model.analysis_model import AnalysisResponse
from utils.logger import Logger
from utils.encrypt import Encrypt

class AnalysisUseCase:
    """Caso de uso para el análisis de archivos"""
    
    def __init__(self):
        self.logger = Logger()
        self.encrypt = Encrypt()
    
    async def execute(self, filename: str) -> AnalysisResponse:
        """
        Ejecuta el análisis del archivo especificado
        
        Args:
            filename: Nombre del archivo a analizar
            
        Returns:
            AnalysisResponse: Resultado del análisis
        """
        # Configurar contexto del logger
        self.logger.set_context("AnalysisUseCase.execute", {
            "filename": filename
        })
        
        self.logger.info("Ejecutando caso de uso de análisis")
        
        try:
            # Validar nombre del archivo
            if not filename or not filename.strip():
                self.logger.error("Nombre de archivo inválido")
                raise ValueError("El nombre del archivo no puede estar vacío")
            
            self.logger.info("Nombre de archivo validado")
            
            # Encriptar nombre del archivo usando el mismo algoritmo que config-service
            encrypted_filename = self.encrypt.to_base64_and_encrypt(filename)
            
            self.logger.info("Nombre de archivo encriptado correctamente")
            
            # Simular análisis del archivo (aquí se podría agregar lógica real de análisis)
            analysis_data = await self._perform_analysis(filename)
            
            self.logger.success("Análisis completado exitosamente")
            
            # Crear respuesta
            response = AnalysisResponse(
                success=True,
                message="Análisis completado exitosamente",
                filename=filename,
                encrypted_filename=encrypted_filename,
                timestamp=datetime.now(),
                data=analysis_data
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error en caso de uso: {str(e)}")
            raise
    
    async def _perform_analysis(self, filename: str) -> dict:
        """
        Realiza el análisis del archivo (simulado)
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            dict: Datos del análisis
        """
        self.logger.info("Realizando análisis del archivo")
        
        # Simular análisis
        analysis_data = {
            "file_size": len(filename) * 1024,  # Simular tamaño
            "file_type": self._get_file_type(filename),
            "analysis_date": datetime.now().isoformat(),
            "security_level": "high",
            "encryption_algorithm": "AES-256-CBC + Base64"
        }
        
        self.logger.info("Análisis simulado completado")
        
        return analysis_data
    
    def _get_file_type(self, filename: str) -> str:
        """
        Determina el tipo de archivo basado en la extensión
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            str: Tipo de archivo
        """
        if '.' not in filename:
            return "unknown"
        
        extension = filename.split('.')[-1].lower()
        
        file_types = {
            'txt': 'text',
            'pdf': 'document',
            'doc': 'document',
            'docx': 'document',
            'jpg': 'image',
            'jpeg': 'image',
            'png': 'image',
            'gif': 'image',
            'mp4': 'video',
            'avi': 'video',
            'mp3': 'audio',
            'wav': 'audio',
            'zip': 'archive',
            'rar': 'archive',
            'json': 'data',
            'xml': 'data',
            'csv': 'data'
        }
        
        return file_types.get(extension, 'unknown') 