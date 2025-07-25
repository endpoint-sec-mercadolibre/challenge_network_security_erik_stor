from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.utils.consts import EXAMPLE_TIMESTAMP


class AnalysisRequest(BaseModel):
    """Modelo para la solicitud de análisis"""

    file_name: str = Field(..., description="Nombre del archivo a analizar")
    file_content: str = Field(..., description="Contenido del archivo")
    analysis_type: str = Field(..., description="Tipo de análisis a realizar")
    user_id: Optional[str] = Field(
        None, description="ID del usuario que solicita el análisis"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "file_name": "config.txt",
                "file_content": "interface eth0\naddress 192.168.1.100",
                "analysis_type": "security",
                "user_id": "user123",
            }
        }
    }


class AnalysisRecord(BaseModel):
    """Modelo para el registro de análisis en la base de datos"""

    analysis_id: str = Field(..., description="ID único del análisis")
    file_name: str = Field(..., description="Nombre del archivo analizado")
    analysis_type: str = Field(..., description="Tipo de análisis realizado")
    status: str = Field(..., description="Estado del análisis")
    result: str = Field(..., description="Resultado del análisis")
    created_at: str = Field(..., description="Fecha de creación del análisis")
    user_id: str = Field(..., description="ID del usuario que solicitó el análisis")

    model_config = {
        "json_schema_extra": {
            "example": {
                "analysis_id": "analysis_123",
                "file_name": "config.txt",
                "analysis_type": "security",
                "status": "completed",
                "result": "Análisis de seguridad completado",
                "created_at": "2024-01-01T00:00:00Z",
                "user_id": "user123",
            }
        }
    }


class AnalysisData(BaseModel):
    """Modelo para los datos del análisis"""

    filename: str = Field(..., description="Nombre del archivo analizado")
    file_size: int = Field(..., ge=0, description="Tamaño del archivo en bytes")
    encrypted_filename: str = Field(..., description="Nombre del archivo encriptado")
    checksum: str = Field(..., description="Checksum del archivo")
    file_type: str = Field(..., description="Tipo de archivo")
    content: str | Dict[str, Any] = Field(..., description="Contenido del análisis (string para contenido básico, dict para análisis con IA)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales del archivo")
    analysis_date: Optional[str] = Field(None, description="Fecha del análisis")
    safe: Optional[bool] = Field(None, description="Indica si el archivo es seguro")
    problems: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de problemas encontrados")
    security_level: Optional[str] = Field(None, description="Nivel de seguridad del archivo")

    @validator('file_size')
    def validate_file_size(cls, v):
        if v < 0:
            raise ValueError('file_size debe ser un número positivo')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "config.txt",
                "file_size": 1024,
                "encrypted_filename": "encrypted_filename_123",
                "checksum": "sha256_hash_123",
                "file_type": "text/plain",
                "content": "Contenido del archivo o análisis estructurado",
                "metadata": {"encoding": "UTF-8", "line_count": 50},
                "analysis_date": "2024-01-01T12:00:00Z",
                "safe": True,
                "problems": [],
                "security_level": "safe"
            }
        }
    }


class AnalysisResponse(BaseModel):
    """Modelo para la respuesta del análisis"""

    success: bool = Field(..., description="Indica si el análisis fue exitoso")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    data: AnalysisData = Field(..., description="Datos del análisis del archivo")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Archivo analizado correctamente",
                "data": {
                    "filename": "config.txt",
                    "file_size": 1024,
                    "encrypted_filename": "encrypted_filename_123",
                    "checksum": "sha256_hash_123",
                    "file_type": "text/plain",
                    "content": "Contenido del archivo",
                    "metadata": {"encoding": "UTF-8", "line_count": 50},
                    "analysis_date": "2024-01-01T12:00:00Z",
                    "safe": True,
                    "problems": [],
                    "security_level": "safe"
                },
            }
        }
    }


class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""

    success: bool = Field(False, description="Indica que la operación no fue exitosa")
    message: str = Field(..., description="Descripción del error")
    error_code: Optional[str] = Field(None, description="Código de error específico")
    detail: Optional[str] = Field(None, description="Detalles adicionales del error")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp del error"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "message": "Token de autenticación inválido",
                "error_code": "UNAUTHORIZED",
                "detail": "El token JWT proporcionado no es válido o ha expirado",
                "timestamp": EXAMPLE_TIMESTAMP,
            }
        }
    }
