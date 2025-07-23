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
    "description": """
    ## API para Análisis de Archivos con Autenticación
    
    Este servicio proporciona funcionalidades para analizar archivos de manera segura.
    
    ### Autenticación
    
    Para usar esta API, necesitas obtener un token JWT del servicio de autenticación:
    
    1. **Obtener Token**: Haz una petición POST a `http://localhost:8080/login` con:
       ```json
       {
         "username": "tu_usuario",
         "password": "tu_password"
       }
       ```
    
    2. **Usar Token**: Copia el token de la respuesta y úsalo en el botón "Authorize" de Swagger UI
    
    3. **Formato**: El token debe incluirse como `Bearer <token>` en el header Authorization
    
    ### Endpoints Protegidos
    
    - `/api/v1/analyze` - Requiere autenticación JWT
    
    ### Endpoints Públicos
    
    - `/health` - Verificación de estado del servicio
    - `/docs` - Esta documentación
    - `/redoc` - Documentación alternativa
    """,
    "version": "1.0.0",
    "contact": {
        "name": "Analysis Service Team",
        "email": "support@analysisservice.com",
        "url": "https://github.com/your-repo/analysis-service"
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
} 