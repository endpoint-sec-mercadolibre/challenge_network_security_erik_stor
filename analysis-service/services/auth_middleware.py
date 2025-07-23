from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from services.auth_client import AuthClient
from services.logger import Logger

# Configurar logger
logger = Logger()


class AuthMiddleware:
    """Middleware para validar tokens JWT en todas las rutas protegidas"""

    def __init__(self):
        self.auth_client = AuthClient()
        self.security = HTTPBearer(auto_error=False)

    async def __call__(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(
            HTTPBearer(auto_error=False)
        ),
    ):
        """
        Valida el token JWT en cada petición

        Args:
            request: Petición HTTP
            credentials: Credenciales de autorización (opcional)

        Returns:
            dict: Información del usuario autenticado

        Raises:
            HTTPException: Si el token es inválido o no se proporciona
        """
        # Configurar contexto del logger
        logger.set_context(
            "AuthMiddleware", {"path": request.url.path, "method": request.method}
        )

        # Verificar si la ruta requiere autenticación
        if not self._requires_auth(request.url.path):
            logger.info("Ruta pública, saltando autenticación")
            return {"authenticated": False}

        # Verificar si se proporcionó token
        if not credentials:

            auth_header = request.headers.get("Authorization")

            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                logger.info("Token encontrado en header Authorization manual")
            else:
                logger.error("Token no proporcionado")
                logger.error(f"Headers disponibles: {dict(request.headers)}")
                raise HTTPException(
                    status_code=401,
                    detail={
                        "success": False,
                        "message": "Token de autenticación requerido",
                        "error_code": "TOKEN_REQUIRED",
                        "detail": "Se requiere un token JWT Bearer para acceder a este recurso. Asegúrate de usar el botón 'Authorize' en Swagger UI.",
                        "timestamp": logger.get_timestamp(),
                    },
                )

        else:
            token = credentials.credentials
            logger.info("Token obtenido de credentials")

        # Validar token con el servicio de autenticación
        try:
            logger.info("Validando token JWT")
            is_valid, data = await self.auth_client.validate_token(token)

            if not is_valid:
                logger.error("Token inválido")
                raise HTTPException(
                    status_code=401,
                    detail={
                        "success": False,
                        "message": "Token de autenticación inválido",
                        "error_code": "INVALID_TOKEN",
                        "detail": "El token JWT proporcionado no es válido o ha expirado. Obtén un nuevo token desde el servicio de autenticación.",
                        "timestamp": logger.get_timestamp(),
                    },
                )

            logger.success("Token validado correctamente")
            return {"authenticated": True, "token": token, "user": data.get("user")}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error inesperado en validación de token: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "message": "Error interno en validación de token",
                    "error_code": "AUTH_SERVICE_ERROR",
                    "detail": "Error al comunicarse con el servicio de autenticación",
                    "timestamp": logger.get_timestamp(),
                },
            )

    def _requires_auth(self, path: str) -> bool:
        """
        Determina si una ruta requiere autenticación

        Args:
            path: Ruta de la petición

        Returns:
            bool: True si requiere autenticación, False en caso contrario
        """
        # Rutas públicas que no requieren autenticación
        public_paths = ["/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"]

        # Verificar si la ruta es pública
        for public_path in public_paths:
            if path == public_path or path.startswith(public_path):
                return False

        # Todas las demás rutas requieren autenticación
        return True


# Instancia global del middleware
auth_middleware = AuthMiddleware()
