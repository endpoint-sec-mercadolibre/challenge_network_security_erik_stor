import aiohttp
import os
from app.services.logger import Logger


class AuthClient:
    """Cliente para consumir el servicio de autenticación"""

    def __init__(self):
        self.logger = Logger()
        # URL del servicio de autenticación
        self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
        self.timeout = aiohttp.ClientTimeout(total=10)

    async def validate_token(self, token: str) -> tuple[bool, dict]:
        """
        Valida un token JWT con el servicio de autenticación

        Args:
            token: Token JWT a validar

        Returns:
            bool: True si el token es válido, False en caso contrario
        """
        self.logger.set_context(
            "AuthClient.validate_token",
            {
                "token_length": len(token) if token else 0,
                "auth_service_url": self.auth_service_url,
            },
        )

        try:
            self.logger.info("Validando token con servicio de autenticación")

            # URL del endpoint de validación
            url = f"{self.auth_service_url}/validate"

            # Datos de la petición
            payload = {"token": token}

            # Realizar petición HTTP
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    self.logger.info(
                        f"Respuesta del servicio de autenticación: {response.status}"
                    )

                    if response.status == 200:
                        data = await response.json()
                        is_valid = data.get("valid", False)

                        self.logger.success(
                            "Token validado exitosamente",
                            {"valid": is_valid, "response_data": data},
                        )

                        return is_valid, data
                    elif response.status == 401:
                        self.logger.error(
                            "Token inválido según el servicio de autenticación"
                        )
                        return False, None
                    elif response.status == 400:
                        response_data = await response.json()
                        self.logger.error(f"Error en formato de token: {response_data}")
                        return False, None
                    else:
                        response_text = await response.text()
                        self.logger.error(
                            f"Error en validación de token: {response.status} - {response_text}"
                        )
                        return False, None

        except aiohttp.ClientConnectorError as e:
            self.logger.error(
                f"Error de conexión con servicio de autenticación: {str(e)}"
            )
            return False, None
        except aiohttp.ServerTimeoutError as e:
            self.logger.error(
                f"Timeout en comunicación con servicio de autenticación: {str(e)}"
            )
            return False, None
        except Exception as e:
            self.logger.error(f"Error inesperado en validación de token: {str(e)}")
            return False, None
