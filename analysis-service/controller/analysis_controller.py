from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from model.analysis_model import AnalysisResponse, ErrorResponse
from usecase.analysis_usecase import AnalysisUseCase
from utils.logger import Logger
from utils.auth_client import AuthClient

# Configurar router
router = APIRouter()
security = HTTPBearer()

# Configurar logger
logger = Logger()

@router.get(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        200: {"description": "Análisis exitoso"},
        400: {"model": ErrorResponse, "description": "Parámetros inválidos"},
        401: {"model": ErrorResponse, "description": "No autorizado"},
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    },
    summary="Analizar archivo",
    description="Analiza un archivo especificado por nombre, encriptando el nombre para comunicación segura"
)
async def analyze_file(
    filename: str = Query(..., description="Nombre del archivo a analizar", example="document.txt"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analiza un archivo especificado por nombre.
    
    - **filename**: Nombre del archivo a analizar
    - **Authorization**: Token JWT Bearer requerido
    
    Retorna información del análisis incluyendo el nombre encriptado del archivo.
    """
    try:
        # Configurar contexto del logger
        logger.set_context("AnalysisController.analyze_file", {
            "filename": filename,
            "endpoint": "/analyze"
        })
        
        logger.info("Iniciando análisis de archivo")
        
        # Validar token
        auth_client = AuthClient()
        is_valid = await auth_client.validate_token(credentials.credentials)
        
        if not is_valid:
            logger.error("Token inválido")
            raise HTTPException(
                status_code=401,
                detail="Token de autenticación inválido"
            )
        
        logger.info("Token validado correctamente")
        
        # Ejecutar caso de uso
        use_case = AnalysisUseCase()
        result = await use_case.execute(filename)
        
        logger.success("Análisis completado exitosamente")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en análisis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        ) 