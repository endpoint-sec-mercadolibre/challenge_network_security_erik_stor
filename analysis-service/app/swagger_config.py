"""
Configuración personalizada para Swagger UI
"""

# Configuración de colores para Swagger UI
SWAGGER_UI_PARAMETERS = {
    "defaultModelsExpandDepth": -1,  # Ocultar modelos por defecto
    "defaultModelExpandDepth": 3,  # Profundidad de expansión de modelos
    "displayRequestDuration": True,  # Mostrar duración de requests
    "docExpansion": "list",  # Expandir documentación en lista
    "filter": True,  # Habilitar filtro de endpoints
    "showExtensions": True,  # Mostrar extensiones
    "showCommonExtensions": True,  # Mostrar extensiones comunes
    "syntaxHighlight.theme": "monokai",  # Tema de resaltado de sintaxis
    "tryItOutEnabled": True,  # Habilitar "Try it out" por defecto
    "persistAuthorization": True,  # Persistir autorización entre sesiones
    "displayOperationId": True,  # Mostrar ID de operación
    "deepLinking": True,  # Habilitar deep linking
    "showMutatedRequest": True,  # Mostrar request modificado
}

# Configuración de OpenAPI personalizada
OPENAPI_TAGS = [
    {
        "name": "analysis",
        "description": "Operaciones de análisis de archivos",
        "externalDocs": {
            "description": "Documentación adicional",
            "url": "https://github.com/your-repo/analysis-service",
        },
    },
    {"name": "health", "description": "Endpoints de monitoreo y salud del servicio"},
]

# Configuración de seguridad
SECURITY_SCHEMES = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": """
        Para usar esta API, necesitas obtener un token JWT del servicio de autenticación:

        1. **Obtener Token**: Haz una petición POST a http://localhost:8080/login con:
        ```json
        {
            "username": "username",
            "password": "password"
        }
        ```

        2. **Usar Token**: Copia el token de la respuesta y pégalo aquí (sin 'Bearer')

        3. **Formato**: El token se enviará automáticamente como 'Bearer <token>' en el header Authorization
        """,
    }
}

# Configuración de servidores
SERVERS = [
    {"url": "http://localhost:8002", "description": "Servidor de desarrollo"},
]

# Configuración de metadatos adicionales
EXTRA_INFO = {
    "x-logo": {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
        "altText": "Analysis Service Logo",
    },
    "x-tagGroups": [
        {"name": "Core Operations", "tags": ["analysis"]},
        {"name": "Monitoring", "tags": ["health"]},
    ],
}
