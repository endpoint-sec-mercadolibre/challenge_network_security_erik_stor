import aiohttp
import os
from typing import Optional
from utils.logger import Logger

class AuthClient:
    """Cliente para consumir el servicio de autenticación"""
    
    def __init__(self):
        self.logger = Logger()
        # URL del servicio de autenticación
        self.auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8001')
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    async def validate_token(self, token: str) -> bool:
        """
        Valida un token JWT con el servicio de autenticación
        
        Args:
            token: Token JWT a validar
            
        Returns:
            bool: True si el token es válido, False en caso contrario
        """
        self.logger.set_context("AuthClient.validate_token", {
            "token_length": len(token) if token else 0
        })
        
        try:
            self.logger.info("Validando token con servicio de autenticación")
            
            # URL del endpoint de validación
            url = f"{self.auth_service_url}/validate"
            
            # Datos de la petición
            payload = {
                "token": token
            }
            
            # Realizar petición HTTP
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        is_valid = data.get('valid', False)
                        
                        self.logger.success("Token validado exitosamente", {
                            "valid": is_valid
                        })
                        
                        return is_valid
                    else:
                        self.logger.error(f"Error en validación de token: {response.status}")
                        return False
                        
        except aiohttp.ClientError as e:
            self.logger.error(f"Error de conexión con servicio de autenticación: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado en validación de token: {str(e)}")
            return False
    
    async def login(self, username: str, password: str) -> Optional[str]:
        """
        Realiza login con el servicio de autenticación
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Optional[str]: Token JWT si el login es exitoso, None en caso contrario
        """
        self.logger.set_context("AuthClient.login", {
            "username": username
        })
        
        try:
            self.logger.info("Realizando login con servicio de autenticación")
            
            # URL del endpoint de login
            url = f"{self.auth_service_url}/login"
            
            # Datos de la petición
            payload = {
                "username": username,
                "password": password
            }
            
            # Realizar petición HTTP
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        token = data.get('token')
                        
                        self.logger.success("Login exitoso", {
                            "username": username
                        })
                        
                        return token
                    else:
                        self.logger.error(f"Error en login: {response.status}")
                        return None
                        
        except aiohttp.ClientError as e:
            self.logger.error(f"Error de conexión con servicio de autenticación: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error inesperado en login: {str(e)}")
            return None 