from datetime import datetime
import os
import httpx
import google.generativeai as genai

import json

from model.analysis_model import AnalysisResponse
from model.analysis_repository import AnalysisRepository
from services.logger import Logger

# Usar la nueva implementación compatible
from services.encrypt import Encrypt


class AnalysisUseCase:
    """Caso de uso para el análisis de archivos"""

    def __init__(self):
        self.logger = Logger()
        self.encrypt = Encrypt(os.getenv("ENCRYPTION_KEY", "mi_contraseña_secreta"))
        self.config_service_url = os.getenv(
            "CONFIG_SERVICE_URL", "http://localhost:8000"
        )
        self.repository = AnalysisRepository()

    async def execute(self, filename: str, auth_result: dict) -> AnalysisResponse:
        """
        Ejecuta el análisis del archivo especificado

        Args:
            filename: Nombre del archivo a analizar
            token: Token de autorización

        Returns:
            AnalysisResponse: Resultado del análisis
        """
        # Configurar contexto del logger
        self.logger.set_context("AnalysisUseCase.execute", {"filename": filename})

        self.logger.info("Ejecutando caso de uso de análisis")

        try:
            # Validar nombre del archivo
            if not filename or not filename.strip():
                self.logger.error("Nombre de archivo inválido")
                raise ValueError("El nombre del archivo no puede estar vacío")

            self.logger.info("Nombre de archivo validado")

            # Encriptar nombre del archivo usando el método compatible
            encrypted_filename = self.encrypt.encrypt(filename)
            filename_base64 = self.encrypt.ofuscar_base64(encrypted_filename)

            self.logger.info(
                "Nombre de archivo encriptado correctamente con método compatible"
            )
            self.logger.info(f"Nombre de archivo encriptado: {encrypted_filename}")
            self.logger.info(f"Nombre de archivo base64: {filename_base64}")

            # Obtener contenido del archivo desde el servicio de configuración
            file_content = await self._get_file_content_from_config_service(
                filename_base64, auth_result.get("token")
            )

            self.logger.info(
                "Contenido del archivo obtenido, iniciando análisis con Gemini"
            )

            analysis_data = await self._perform_analysis(filename, file_content)

            self.logger.success("Análisis completado exitosamente")

            # Guardar registro en MongoDB
            try:
                # Preparar respuesta para guardar en MongoDB
                mongo_response = {
                    "filename": filename,
                    "encrypted_filename": encrypted_filename,
                    "analysis_data": analysis_data,
                    "gemini_response": analysis_data.get(
                        "gemini_analysis", {}
                    ),  # Ahora es un objeto JSON
                    "timestamp": datetime.now().isoformat(),
                }

                # Guardar en MongoDB
                self.repository.save_analysis_record(
                    success=True, response=mongo_response, user=auth_result.get("user")
                )

                self.logger.success("Registro guardado en MongoDB exitosamente")

            except Exception as e:
                self.logger.error(f"Error al guardar en MongoDB: {str(e)}")
                # Si falla MongoDB, el análisis no se considera exitoso
                raise Exception(f"Error al guardar registro en base de datos: {str(e)}")

            # Crear datos del análisis con la estructura correcta
            analysis_data_model = {
                "filename": filename,
                "encrypted_filename": encrypted_filename,
                "file_size": len(file_content) if file_content else 0,
                "analysis_date": datetime.now(),
                "file_type": "text/plain",  # Por defecto, se puede mejorar detectando el tipo real
                "checksum": None,
                "metadata": analysis_data,
            }

            # Crear respuesta
            response = AnalysisResponse(
                success=True,
                message="Análisis completado exitosamente",
                data=analysis_data_model,
            )

            return response

        except Exception as e:
            self.logger.error(f"Error en caso de uso: {str(e)}")

            # Guardar registro de error en MongoDB si tenemos token
            if auth_result.get("token"):
                try:
                    user = auth_result.get("user") or "unknown_user"
                    error_response = {
                        "error": str(e),
                        "filename": filename,
                        "timestamp": datetime.now().isoformat(),
                    }

                    self.repository.save_analysis_record(
                        success=False, response=error_response, user=user
                    )

                    self.logger.info("Registro de error guardado en MongoDB")

                except Exception as mongo_error:
                    self.logger.error(
                        f"Error al guardar registro de error en MongoDB: {str(mongo_error)}"
                    )
                    # No re-lanzar el error aquí para evitar enmascarar el error original

            raise

    async def _get_file_content_from_config_service(
        self, encrypted_filename: str, token: str = None
    ) -> str:
        """
        Obtiene el contenido del archivo desde el servicio de configuración

        Args:
            encrypted_filename: Nombre del archivo encriptado

        Returns:
            str: Contenido del archivo desencriptado
        """
        self.logger.info(
            "Obteniendo contenido del archivo desde el servicio de configuración"
        )

        try:
            # Construir URL del servicio de configuración
            url = f"{self.config_service_url}/config/{encrypted_filename}"

            self.logger.info(f"Realizando petición a: {url}")

            # Configurar headers con el token de autorización
            headers = {"accept": "application/json"}

            if token:
                headers["Authorization"] = f"Bearer {token}"

            # Intentar obtener contenido del servicio de configuración
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    mock_response = response.json()

                self.logger.info("Respuesta del servicio de configuración obtenida")

                # Extraer el contenido encriptado
                encrypted_content = mock_response.get("data", {}).get("content")

                if not encrypted_content:
                    raise ValueError(
                        "No se encontró el contenido en la respuesta del servicio"
                    )

                self.logger.info("Contenido encriptado extraído de la respuesta")

                # Desofuscar el contenido (convertir de base64 a texto normal)
                desofuscated_content = self.encrypt.desofuscar_base64(encrypted_content)
                self.logger.info("Contenido desofuscado correctamente")

                # Desencriptar el contenido
                decrypted_content = self.encrypt.decrypt(desofuscated_content)
                self.logger.info("Contenido desencriptado correctamente")

                return decrypted_content

            except Exception as service_error:
                self.logger.warning(
                    f"Error al conectar con servicio de configuración: {str(service_error)}"
                )
                self.logger.info("Usando contenido mock para desarrollo")

                # Contenido mock para desarrollo
                mock_content = """# Configuración de red de ejemplo
interface eth0
    address 192.168.1.100
    netmask 255.255.255.0
    gateway 192.168.1.1

# Configuración de firewall básica
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Configuración de DNS
nameserver 8.8.8.8
nameserver 8.8.4.4"""

                return mock_content

        except Exception as e:
            self.logger.error(f"Error al obtener contenido del archivo: {str(e)}")
            raise

    async def _perform_analysis(self, filename: str, file_content: str = None) -> dict:
        """
        Realiza el análisis del archivo usando la API de Google Gemini

        Args:
            filename: Nombre del archivo
            file_content: Contenido del archivo a analizar

        Returns:
            dict: Datos del análisis
        """
        self.logger.info("Realizando análisis del archivo con Gemini API")

        if not file_content:
            self.logger.error("No se proporcionó contenido del archivo")
            raise ValueError("No se proporcionó contenido del archivo")

        try:
            # Obtener la API key de Gemini desde variables de entorno
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                self.logger.error("GEMINI_API_KEY no está configurada")
                raise ValueError("API key de Gemini no configurada")

            # Configurar Gemini
            genai.configure(api_key=api_key)

            # Preparar el prompt para el análisis de seguridad
            prompt = f"""Analiza esta configuración de red detalladamente. 
            Identifica todas las configuraciones potencialmente inseguras y clasifícalas por nivel de severidad (crítica, alta, media o baja).
            Para cada problema detectado, proporciona una explicación clara del riesgo y una recomendación específica de cómo solucionarlo o mitigar el riesgo. 
            El análisis debe ser preciso, conciso y orientado a buenas prácticas de seguridad actuales. El resultado debe ser un JSON con la siguiente estructura:
            {{
                "analysis_date": "fecha y hora del análisis",
                "safe": "true o false",
                "problems": [
                    {{
                        "problem": "descripción del problema",
                        "severity": "severidad (crítica, alta, media o baja)",
                        "recommendation": "recomendación para solucionar el problema"
                    }}
                ]
            }}
            Configuración de red a analizar: {file_content}"""

            self.logger.info("Enviando solicitud a Gemini API")

            # Configurar el modelo Gemini
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Realizar la solicitud a la API de Gemini
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2048,
                    temperature=0.1,  # Temperatura baja para respuestas más estandarizadas
                ),
            )

            self.logger.info("Respuesta recibida de Gemini API")
            print(response)

            # Extraer el contenido de la respuesta
            analysis_result = (
                response.text if response.text else "No se pudo obtener análisis"
            )

            # Intentar parsear la respuesta de Gemini como JSON
            try:
                # Buscar el JSON en la respuesta (puede estar rodeado de texto)
                json_start = analysis_result.find("{")
                json_end = analysis_result.rfind("}") + 1

                if json_start != -1 and json_end != 0:
                    json_str = analysis_result[json_start:json_end]
                    parsed_analysis = json.loads(json_str)

                    # Validar que tenga la estructura esperada
                    if not isinstance(parsed_analysis, dict):
                        raise ValueError("La respuesta no es un objeto JSON válido")

                    # Asegurar que tenga los campos requeridos
                    if "safe" not in parsed_analysis:
                        parsed_analysis["safe"] = False
                    if "problems" not in parsed_analysis:
                        parsed_analysis["problems"] = []
                    if "analysis_date" not in parsed_analysis:
                        parsed_analysis["analysis_date"] = datetime.now().isoformat()

                    self.logger.info(
                        "Respuesta de Gemini parseada como JSON exitosamente"
                    )

                else:
                    # Si no se encuentra JSON, crear estructura por defecto
                    self.logger.warning(
                        "No se encontró JSON en la respuesta de Gemini, usando estructura por defecto"
                    )
                    parsed_analysis = {
                        "analysis_date": datetime.now().isoformat(),
                        "safe": False,
                        "problems": [
                            {
                                "problem": "No se pudo parsear la respuesta de Gemini",
                                "severity": "Desconocida",
                                "recommendation": "Revisar la configuración de la API de Gemini",
                            }
                        ],
                    }

            except (json.JSONDecodeError, ValueError) as e:
                self.logger.error(f"Error al parsear JSON de Gemini: {str(e)}")
                # Crear estructura por defecto en caso de error
                parsed_analysis = {
                    "analysis_date": datetime.now().isoformat(),
                    "safe": False,
                    "problems": [
                        {
                            "problem": f"Error al parsear respuesta de Gemini: {str(e)}",
                            "severity": "Desconocida",
                            "recommendation": "Revisar la configuración de la API de Gemini",
                        }
                    ],
                }

            # Crear estructura de datos del análisis
            analysis_data = {
                "analysis_date": datetime.now().isoformat(),
                "security_level": self._determine_security_level_from_parsed(
                    parsed_analysis
                ),
                "gemini_analysis": parsed_analysis,  # Ahora es un objeto JSON, no un string
                "model_used": "gemini-1.5-flash",
                "tokens_used": "unknown",
            }

            self.logger.success("Análisis con Gemini completado exitosamente")

            return analysis_data

        except Exception as e:
            self.logger.error(f"Error en análisis con Gemini: {str(e)}")
            # Fallback a análisis básico en caso de error
            return {
                "analysis_date": datetime.now().isoformat(),
                "security_level": "unknown",
                "gemini_analysis": f"Error en análisis: {str(e)}",
                "model_used": "none",
                "tokens_used": "",
            }

    def _determine_security_level_from_parsed(self, parsed_analysis: dict) -> str:
        """
        Determina el nivel de seguridad basado en el análisis parseado de Gemini

        Args:
            parsed_analysis: Análisis parseado como diccionario

        Returns:
            str: Nivel de seguridad (critical, high, medium, low, safe)
        """
        try:
            # Si el análisis indica que es seguro, retornar safe
            if parsed_analysis.get("safe", False):
                return "safe"

            # Revisar los problemas para determinar el nivel más alto
            problems = parsed_analysis.get("problems", [])

            if not problems:
                return "safe"

            # Contar problemas por severidad
            severity_counts = {
                "crítica": 0,
                "critical": 0,
                "alta": 0,
                "high": 0,
                "media": 0,
                "medium": 0,
                "baja": 0,
                "low": 0,
            }

            for problem in problems:
                severity = problem.get("severity", "").lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1

            # Determinar el nivel más alto de severidad
            if severity_counts["crítica"] > 0 or severity_counts["critical"] > 0:
                return "critical"
            elif severity_counts["alta"] > 0 or severity_counts["high"] > 0:
                return "high"
            elif severity_counts["media"] > 0 or severity_counts["medium"] > 0:
                return "medium"
            elif severity_counts["baja"] > 0 or severity_counts["low"] > 0:
                return "low"
            else:
                return "safe"

        except Exception as e:
            self.logger.warning(f"Error al determinar nivel de seguridad: {str(e)}")
            return "unknown"
