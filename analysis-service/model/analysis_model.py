from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AnalysisData(BaseModel):
    """Modelo para los datos del análisis"""
    filename: str = Field(..., description="Nombre original del archivo")
    encrypted_filename: str = Field(..., description="Nombre del archivo encriptado")
    file_size: int = Field(..., description="Tamaño del archivo en bytes", ge=0)
    analysis_date: datetime = Field(..., description="Fecha y hora del análisis")
    file_type: str = Field(..., description="Tipo MIME del archivo")
    checksum: Optional[str] = Field(None, description="Checksum del archivo")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales del archivo")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "document.txt",
                "encrypted_filename": "encrypted_abc123",
                "file_size": 1024,
                "analysis_date": "2024-01-01T12:00:00Z",
                "file_type": "text/plain",
                "checksum": "sha256:abc123...",
                "metadata": {
                    "encoding": "UTF-8",
                    "line_count": 50
                }
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
                    "analysis_date": "2024-01-01T12:00:00Z",
                    "file_type": "text/plain",
                    "checksum": "sha256:abc123...",
                    "metadata": {
                        "encoding": "UTF-8",
                        "line_count": 50
                    }
                }
            }
        }
    }

class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    success: bool = Field(False, description="Indica que la operación no fue exitosa")
    message: str = Field(..., description="Descripción del error")
    error_code: Optional[str] = Field(None, description="Código de error específico")
    detail: Optional[str] = Field(None, description="Detalles adicionales del error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "message": "Token de autenticación inválido",
                "error_code": "UNAUTHORIZED",
                "detail": "El token JWT proporcionado no es válido o ha expirado",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    } 