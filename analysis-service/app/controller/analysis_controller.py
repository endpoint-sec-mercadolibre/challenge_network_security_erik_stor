from fastapi import APIRouter, Query, HTTPException, Request, Depends

from app.model.analysis_model import AnalysisResponse, ErrorResponse
from app.usecase.analysis_usecase import AnalysisUseCase
from app.services.logger import Logger
from app.services.auth_middleware import auth_middleware

# Configurar router
router = APIRouter()

# Configurar logger
logger = Logger()


@router.get(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        200: {
            "description": "Análisis exitoso",
            "content": {
                "application/json": {
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
                            "metadata": {"encoding": "UTF-8", "line_count": 50},
                        },
                    }
                }
            },
        },
        400: {
            "model": ErrorResponse,
            "description": "Parámetros inválidos",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Nombre de archivo requerido",
                        "error_code": "INVALID_PARAMETER",
                        "detail": "El nombre del archivo no puede estar vacío",
                        "timestamp": "2024-01-01T12:00:00Z",
                    }
                }
            },
        },
        401: {
            "model": ErrorResponse,
            "description": "No autorizado",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Token de autenticación inválido",
                        "error_code": "UNAUTHORIZED",
                        "detail": "El token JWT proporcionado no es válido o ha expirado",
                        "timestamp": "2024-01-01T12:00:00Z",
                    }
                }
            },
        },
        500: {
            "model": ErrorResponse,
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Error interno del servidor",
                        "error_code": "INTERNAL_ERROR",
                        "detail": "Ocurrió un error inesperado durante el procesamiento",
                        "timestamp": "2024-01-01T12:00:00Z",
                    }
                }
            },
        },
    },
    summary="Analizar archivo",
    description="""Analiza un archivo especificado por nombre, encriptando el nombre para comunicación segura.""",
    operation_id="analyze_file",
)
async def analyze_file(
    request: Request,
    auth_result: dict = Depends(auth_middleware),
    filename: str = Query(
        ...,
        description="Nombre del archivo a analizar (debe existir en el servidor)",
        example="document.txt",
        min_length=1,
        max_length=255,
    ),
):
    """
    Analiza un archivo especificado por nombre.

    Args:
        request (Request): Objeto de petición HTTP
        filename (str): Nombre del archivo a analizar

    Returns:
        AnalysisResponse: Información del análisis incluyendo el nombre encriptado del archivo

    Raises:
        HTTPException: Si el archivo no existe o hay un error interno
    """
    try:
        # Configurar contexto del logger
        logger.set_context(
            "AnalysisController.analyze_file",
            {
                "filename": filename,
                "endpoint": "/analyze",
                "authenticated": True,  # La autenticación ya fue validada por el middleware global
            },
        )

        logger.info("Iniciando análisis de archivo")

        # La autenticación ya fue validada por el middleware global
        logger.info("Usuario autenticado correctamente")
        logger.info(f"Token recibido del middleware: {auth_result.get('token', 'No token')[:20]}...")

        # Ejecutar caso de uso con el resultado de autenticación
        use_case = AnalysisUseCase()
        result = await use_case.execute(filename, auth_result)

        logger.success("Análisis completado exitosamente")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en análisis: {str(e)}")

        # Determinar el código de estado apropiado basado en el tipo de error
        if (
            "MongoDB" in str(e)
            or "base de datos" in str(e)
            or "Authentication failed" in str(e)
        ):
            status_code = 500
            detail = "Error en la base de datos"
        else:
            status_code = 500
            detail = "Error interno del servidor"

        raise HTTPException(status_code=status_code, detail=detail)
