from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
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

    filename: str = Field(..., description="Nombre original del archivo")
    encrypted_filename: str = Field(..., description="Nombre del archivo encriptado")
    file_size: int = Field(..., description="Tamaño del archivo en bytes", ge=0)
    analysis_date: datetime = Field(..., description="Fecha y hora del análisis")
    file_type: str = Field(..., description="Tipo MIME del archivo")
    checksum: Optional[str] = Field(None, description="Checksum del archivo")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Metadatos adicionales del archivo"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "document.txt",
                "encrypted_filename": "encrypted_abc123",
                "file_size": 1024,
                "analysis_date": EXAMPLE_TIMESTAMP,
                "file_type": "text/plain",
                "checksum": "sha256:abc123...",
                "metadata": {"encoding": "UTF-8", "line_count": 50},
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
                    "filename": "document.txt",
                    "encrypted_filename": "encrypted_abc123",
                    "file_size": 1024,
                    "analysis_date": EXAMPLE_TIMESTAMP,
                    "file_type": "text/plain",
                    "checksum": "sha256:abc123...",
                    "metadata": {"encoding": "UTF-8", "line_count": 50},
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
