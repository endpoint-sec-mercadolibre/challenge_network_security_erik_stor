"""
Configuración específica para Swagger UI
"""

# Configuración personalizada para Swagger UI
SWAGGER_UI_CONFIG = {
    "swagger_ui_parameters": {
        "defaultModelsExpandDepth": -1,
        "defaultModelExpandDepth": 3,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "syntaxHighlight.theme": "monokai",
        "tryItOutEnabled": True,
        "persistAuthorization": True,
        "displayOperationId": True
    }
}

# Configuración de información adicional para la documentación
API_INFO = {
    "title": "Analysis Service API",
    "description": "API para Análisis de Archivos con Autenticación",
    "version": "1.0.0",
    "contact": {
        "name": "API Support",
        "email": "support@example.com"
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
} 