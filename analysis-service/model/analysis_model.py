from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AnalysisRequest(BaseModel):
    """Modelo para la solicitud de análisis"""
    filename: str = Field(..., description="Nombre del archivo a analizar", example="document.txt")
    
class AnalysisResponse(BaseModel):
    """Modelo para la respuesta del análisis"""
    success: bool = Field(..., description="Indica si el análisis fue exitoso")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    filename: str = Field(..., description="Nombre del archivo analizado")
    encrypted_filename: str = Field(..., description="Nombre del archivo encriptado")
    timestamp: datetime = Field(..., description="Timestamp del análisis")
    data: Optional[dict] = Field(None, description="Datos adicionales del análisis")

class AuthRequest(BaseModel):
    """Modelo para la solicitud de autenticación"""
    username: str = Field(..., description="Nombre de usuario", example="admin")
    password: str = Field(..., description="Contraseña del usuario", example="password123")

class AuthResponse(BaseModel):
    """Modelo para la respuesta de autenticación"""
    token: str = Field(..., description="Token JWT generado")
    user: str = Field(..., description="Nombre de usuario autenticado")

class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    error: str = Field(..., description="Descripción del error")
    detail: Optional[str] = Field(None, description="Detalles adicionales del error") 