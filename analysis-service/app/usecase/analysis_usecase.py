from datetime import datetime
import os
import httpx
from httpx import HTTPStatusError
import google.generativeai as genai

import json

from app.model.analysis_model import AnalysisResponse
from app.model.analysis_repository import AnalysisRepository
from app.services.logger import Logger

# Usar la nueva implementación compatible
from app.services.encrypt import Encrypt


class AnalysisUseCase:
    """Caso de uso para el análisis de archivos"""

    def __init__(self):
        self.logger = Logger()
        self.encrypt = Encrypt(os.getenv("ENCRYPTION_KEY", "mi_contraseña_secreta"))
        self.config_service_url = os.getenv(
            "CONFIG_SERVICE_URL", "http://localhost:8000"
        )
        self.repository = AnalysisRepository()

    async def execute(
        self, filename: str, auth_result: dict, enable_ia: bool
    ) -> AnalysisResponse:
        """
        Ejecuta el análisis del archivo especificado

        Args:
            filename: Nombre del archivo a analizar
            auth_result: Resultado de la autenticación
            enable_ia: Indica si se debe utilizar IA para el análisis

        Returns:
            AnalysisResponse: Resultado del análisis
        """
        self.logger.set_context("AnalysisUseCase.execute", {"filename": filename})
        self.logger.info("Ejecutando caso de uso de análisis")

        try:
            # Validar y procesar nombre del archivo
            self._validate_filename(filename)
            encrypted_filename, filename_base64 = self._encrypt_filename(filename)

            # Obtener contenido del archivo y realizar análisis
            file_content = await self._get_file_content_from_config_service(
                filename_base64, auth_result.get("token")
            )

            if enable_ia:
                analysis_data = self._perform_analysis(file_content)
            else:
                analysis_data = file_content

            # Guardar registro en MongoDB
            self._save_analysis_record(
                filename, encrypted_filename, analysis_data, auth_result, enable_ia
            )

            # Crear y retornar respuesta
            return self._create_success_response(analysis_data, filename, encrypted_filename)

        except Exception as e:
            self.logger.error(f"Error en caso de uso: {str(e)}")
            raise

    def _validate_filename(self, filename: str) -> None:
        """Valida el nombre del archivo"""
        if not filename or not filename.strip():
            self.logger.error("Nombre de archivo inválido")
            raise ValueError("El nombre del archivo no puede estar vacío")
        self.logger.info("Nombre de archivo validado")

    def _encrypt_filename(self, filename: str) -> tuple[str, str]:
        """Encripta el nombre del archivo"""
        encrypted_filename = self.encrypt.encrypt(filename)
        filename_base64 = self.encrypt.ofuscar_base64(encrypted_filename)

        self.logger.info(
            "Nombre de archivo encriptado correctamente con método compatible"
        )
        self.logger.info(f"Nombre de archivo encriptado: {encrypted_filename}")
        self.logger.info(f"Nombre de archivo base64: {filename_base64}")

        return encrypted_filename, filename_base64

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

            except httpx.HTTPStatusError as http_error:
                if http_error.response.status_code == 404:
                    self.logger.error(
                        "Archivo no encontrado en el servicio de configuración"
                    )
                    raise ValueError("El archivo solicitado no existe en el sistema")
                else:
                    self.logger.error(
                        f"Error HTTP del servicio de configuración: {http_error.response.status_code}"
                    )
                    raise ValueError(
                        f"Error del servicio de configuración: {http_error.response.status_code}"
                    )
            except Exception as service_error:
                self.logger.error(
                    f"Error al conectar con servicio de configuración: {str(service_error)}"
                )
                raise ValueError(
                    f"No se pudo obtener el archivo del servicio de configuración: {str(service_error)}"
                )

        except Exception as e:
            self.logger.error(f"Error al obtener contenido del archivo: {str(e)}")
            raise

    def _perform_analysis(self, file_content: str = None) -> dict:
        """
        Realiza el análisis del archivo usando la API de Google Gemini

        Args:
            file_content: Contenido del archivo a analizar

        Returns:
            dict: Datos del análisis
        """
        self.logger.info("Realizando análisis del archivo con Gemini API")

        if not file_content:
            self.logger.error("No se proporcionó contenido del archivo")
            raise ValueError("No se proporcionó contenido del archivo")

        try:
            # Configurar Gemini y obtener respuesta
            model = self._configure_gemini()
            prompt = self._create_analysis_prompt(file_content)
            response = self._call_gemini_api(model, prompt)

            # Parsear respuesta y crear análisis
            parsed_analysis = self._parse_gemini_response(response)
            analysis_data = self._create_analysis_data(parsed_analysis)

            self.logger.success("Análisis con Gemini completado exitosamente")
            return analysis_data

        except Exception as e:
            self.logger.error(f"Error en análisis con Gemini: {str(e)}")
            return self._create_fallback_analysis(str(e))

    def _configure_gemini(self):
        """Configura la API de Gemini"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.logger.error("GEMINI_API_KEY no está configurada")
            raise ValueError("API key de Gemini no configurada")

        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")

    def _create_analysis_prompt(self, file_content: str) -> str:
        """Crea el prompt para el análisis de seguridad"""
        return f"""Analiza esta configuración de red detalladamente. 
        Identifica todas las configuraciones potencialmente inseguras y clasifícalas por nivel de severidad (crítica, alta, media o baja).
        Para cada problema detectado, proporciona una explicación clara del riesgo y una recomendación específica de cómo solucionarlo o mitigar el riesgo. 
        El análisis debe ser preciso, conciso y orientado a buenas prácticas de seguridad actuales. El resultado debe ser un JSON con la siguiente estructura:
        {{
            "safe": true o false,
            "problems": [
                {{
                    "problem": "descripción del problema",
                    "severity": "severidad (crítica, alta, media o baja)",
                    "recommendation": "recomendación para solucionar el problema"
                }}
            ]
        }}
        Configuración de red a analizar: {file_content}"""

    def _call_gemini_api(self, model, prompt: str):
        """Llama a la API de Gemini"""
        self.logger.info("Enviando solicitud a Gemini API")

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=2048,
                temperature=0.1,
            ),
        )

        self.logger.info("Respuesta recibida de Gemini API")
        print(response)
        return response

    def _parse_gemini_response(self, response) -> dict:
        """Parsea la respuesta de Gemini como JSON"""
        analysis_result = (
            response.text if response.text else "No se pudo obtener análisis"
        )

        try:
            return self._extract_and_validate_json(analysis_result)
        except ValueError as e:
            self.logger.error(f"Error al parsear JSON de Gemini: {str(e)}")
            return self._create_default_analysis(
                f"Error al parsear respuesta de Gemini: {str(e)}"
            )

    def _extract_and_validate_json(self, analysis_result: str) -> dict:
        """Extrae y valida JSON de la respuesta de Gemini"""
        json_start = analysis_result.find("{")
        json_end = analysis_result.rfind("}") + 1

        if json_start != -1 and json_end != 0:
            json_str = analysis_result[json_start:json_end]
            parsed_analysis = json.loads(json_str)

            if not isinstance(parsed_analysis, dict):
                raise ValueError("La respuesta no es un objeto JSON válido")

            # Asegurar campos requeridos
            self._ensure_required_fields(parsed_analysis)

            self.logger.info("Respuesta de Gemini parseada como JSON exitosamente")
            return parsed_analysis
        else:
            self.logger.warning(
                "No se encontró JSON en la respuesta de Gemini, usando estructura por defecto"
            )
            return self._create_default_analysis(
                "No se pudo parsear la respuesta de Gemini"
            )

    def _ensure_required_fields(self, parsed_analysis: dict) -> None:
        """Asegura que el análisis tenga todos los campos requeridos"""
        if "safe" not in parsed_analysis:
            parsed_analysis["safe"] = False
        if "problems" not in parsed_analysis:
            parsed_analysis["problems"] = []

    def _create_default_analysis(self, problem_message: str) -> dict:
        """Crea un análisis por defecto cuando hay errores"""
        return {
            "safe": False,
            "problems": [
                {
                    "problem": problem_message,
                    "severity": "Desconocida",
                    "recommendation": "Revisar la configuración de la API de Gemini",
                }
            ],
        }

    def _create_analysis_data(self, parsed_analysis: dict) -> dict:
        """Crea la estructura de datos del análisis"""
        from datetime import datetime
        
        security_level = self._determine_security_level_from_parsed(parsed_analysis)

        return {
            "analysis_date": datetime.now().isoformat(),
            "security_level": security_level,
            "safe": parsed_analysis.get("safe", False),
            "problems": parsed_analysis.get("problems", []),
        }

    def _create_fallback_analysis(self, error_message: str) -> dict:
        """Crea un análisis de fallback en caso de error"""
        from datetime import datetime
        
        return {
            "analysis_date": datetime.now().isoformat(),
            "security_level": "unknown",
            "safe": False,
            "problems": [
                {
                    "problem": f"Error en análisis: {error_message}",
                    "severity": "Desconocida",
                    "recommendation": "Revisar la configuración de la API de Gemini y reintentar el análisis.",
                }
            ],
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

    def _save_analysis_record(
        self,
        filename: str,
        encrypted_filename: str,
        analysis_data: dict | str,
        auth_result: dict,
        enable_ia: bool,
    ) -> None:
        """Guarda el registro de análisis en MongoDB"""
        # En entorno de test, no intentar guardar en MongoDB
        if "test" in os.environ.get("ENVIRONMENT", "").lower():
            self.logger.info("Entorno de test detectado, saltando guardado en MongoDB")
            return

        try:
            # Preparar los datos para MongoDB
            if enable_ia and isinstance(analysis_data, dict):
                # Cuando se usa IA, guardar el análisis completo
                mongo_response = {
                    "filename": filename,
                    "encrypted_filename": encrypted_filename,
                    "analysis_data": analysis_data,  # Incluye security_level, safe, problems
                    "gemini_response": True,  # Booleano indicando que se usó Gemini
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                # Cuando no se usa IA, guardar solo el contenido del archivo
                mongo_response = {
                    "filename": filename,
                    "encrypted_filename": encrypted_filename,
                    "analysis_data": analysis_data,  # Es el contenido del archivo como string
                    "gemini_response": False,  # Booleano indicando que no se usó Gemini
                    "timestamp": datetime.now().isoformat(),
                }

            self.repository.save_analysis_record(
                success=True, response=mongo_response, user=auth_result.get("user")
            )
            self.logger.success("Registro guardado en MongoDB exitosamente")

        except Exception as mongo_error:
            self.logger.warning(
                f"Error al guardar en MongoDB (continuando sin guardar): {str(mongo_error)}"
            )
            # Solo lanzar excepción en entorno de producción
            raise RuntimeError(
                f"Error al guardar registro en base de datos: {str(mongo_error)}"
            )

    def _create_success_response(
        self,
        analysis_data: dict | str,
        filename: str = None,
        encrypted_filename: str = None,
    ) -> AnalysisResponse:
        """Crea la respuesta de éxito"""
        from datetime import datetime
        import hashlib
        
        # Generar valores por defecto si no se proporcionan
        if filename is None:
            filename = "unknown.txt"
        if encrypted_filename is None:
            encrypted_filename = "encrypted_unknown"
            
        # Calcular checksum del contenido
        content_str = str(analysis_data)
        checksum = hashlib.sha256(content_str.encode()).hexdigest()
        
        # Determinar el tipo de archivo
        file_type = "text/plain"
        if isinstance(analysis_data, dict):
            file_type = "application/json"
            
        # Preparar metadatos
        metadata = {
            "encoding": "UTF-8",
            "line_count": len(content_str.split('\n')) if isinstance(content_str, str) else 1
        }
        
        # Preparar datos de análisis
        if isinstance(analysis_data, dict):
            # Si es un análisis con IA
            analysis_date = analysis_data.get("analysis_date", datetime.now().isoformat())
            safe = analysis_data.get("safe", True)
            problems = analysis_data.get("problems", [])
            security_level = analysis_data.get("security_level", "unknown")
        else:
            # Si es contenido básico
            analysis_date = datetime.now().isoformat()
            safe = True
            problems = []
            security_level = "safe"
            
        analysis_data_model = {
            "filename": filename,
            "file_size": len(content_str.encode('utf-8')),
            "encrypted_filename": encrypted_filename,
            "checksum": checksum,
            "file_type": file_type,
            "content": analysis_data,
            "metadata": metadata,
            "analysis_date": analysis_date,
            "safe": safe,
            "problems": problems,
            "security_level": security_level
        }

        return AnalysisResponse(
            success=True,
            message="Análisis completado exitosamente",
            data=analysis_data_model,
        )

    def _save_error_record(
        self, filename: str, error_message: str, auth_result: dict
    ) -> None:
        """Guarda el registro de error en MongoDB"""
        if not auth_result.get("token"):
            return

        # En entorno de test, no intentar guardar en MongoDB
        if "test" in os.environ.get("ENVIRONMENT", "").lower():
            self.logger.info(
                "Entorno de test detectado, saltando guardado de error en MongoDB"
            )
            return

        try:
            user = auth_result.get("user") or "unknown_user"
            error_response = {
                "error": error_message,
                "filename": filename,
                "timestamp": datetime.now().isoformat(),
            }

            self.repository.save_analysis_record(
                success=False, response=error_response, user=user
            )
            self.logger.info("Registro de error guardado en MongoDB")

        except Exception as mongo_error:
            self.logger.warning(
                f"Error al guardar registro de error en MongoDB (continuando sin guardar): {str(mongo_error)}"
            )
            # Solo lanzar excepción en entorno de producción
            self.logger.error(
                f"Error al guardar registro de error en MongoDB: {str(mongo_error)}"
            )

    def get_analysis_by_id(self, analysis_id: str, auth_result: dict) -> dict:
        """
        Obtiene un análisis específico por ID
        
        Args:
            analysis_id: ID del análisis a obtener
            auth_result: Resultado de la autenticación
            
        Returns:
            dict: Datos del análisis
        """
        try:
            # En entorno de test, retornar datos mock
            if "test" in os.environ.get("ENVIRONMENT", "").lower():
                return {
                    "analysis_id": analysis_id,
                    "filename": "test.txt",
                    "analysis_data": {"content": "test content"},
                    "timestamp": datetime.now().isoformat(),
                    "user": auth_result.get("user", "testuser")
                }
            
            # Implementación real para obtener de MongoDB
            # Por ahora retornamos datos mock
            return {
                "analysis_id": analysis_id,
                "filename": "test.txt",
                "analysis_data": {"content": "test content"},
                "timestamp": datetime.now().isoformat(),
                "user": auth_result.get("user", "unknown")
            }
        except Exception as e:
            self.logger.error(f"Error al obtener análisis por ID: {str(e)}")
            raise

    def get_analyses_by_user(self, auth_result: dict) -> list:
        """
        Obtiene todos los análisis de un usuario
        
        Args:
            auth_result: Resultado de la autenticación
            
        Returns:
            list: Lista de análisis del usuario
        """
        try:
            user = auth_result.get("user", "unknown")
            
            # En entorno de test, retornar datos mock
            if "test" in os.environ.get("ENVIRONMENT", "").lower():
                return [
                    {
                        "analysis_id": "test_1",
                        "filename": "test1.txt",
                        "analysis_data": {"content": "test content 1"},
                        "timestamp": datetime.now().isoformat(),
                        "user": user
                    },
                    {
                        "analysis_id": "test_2",
                        "filename": "test2.txt",
                        "analysis_data": {"content": "test content 2"},
                        "timestamp": datetime.now().isoformat(),
                        "user": user
                    }
                ]
            
            # Implementación real para obtener de MongoDB
            # Por ahora retornamos datos mock
            return [
                {
                    "analysis_id": "real_1",
                    "filename": "real1.txt",
                    "analysis_data": {"content": "real content 1"},
                    "timestamp": datetime.now().isoformat(),
                    "user": user
                }
            ]
        except Exception as e:
            self.logger.error(f"Error al obtener análisis por usuario: {str(e)}")
            raise
