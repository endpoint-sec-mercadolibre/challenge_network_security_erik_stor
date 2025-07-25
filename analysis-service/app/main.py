import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
import os
import time

from app.controller.analysis_controller import router as analysis_router
from app.services.auth_middleware import auth_middleware
from app.services.mongodb_service import mongodb_service

from app.swagger_config import SECURITY_SCHEMES, SERVERS, EXTRA_INFO
from app.swagger_ui_config import API_INFO, SWAGGER_UI_CONFIG

# Cargar variables de entorno
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title=API_INFO["title"],
    description=API_INFO["description"],
    version=API_INFO["version"],
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    servers=SERVERS,
    swagger_ui_parameters=SWAGGER_UI_CONFIG["swagger_ui_parameters"],
)

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    try:
        mongodb_service.connect()
        print("✅ Conexión a MongoDB establecida exitosamente")
    except Exception as e:
        print(f"❌ Error al conectar a MongoDB: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento que se ejecuta al cerrar la aplicación"""
    try:
        mongodb_service.disconnect()
        print("✅ Conexión a MongoDB cerrada exitosamente")
    except Exception as e:
        print(f"❌ Error al cerrar conexión a MongoDB: {str(e)}")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas con middleware de autenticación
app.include_router(
    analysis_router,
    prefix="/api/v1",
    tags=["analysis"],
    dependencies=[Depends(auth_middleware)],
)


@app.get(
    "/health",
    tags=["health"],
    summary="Verificar estado del servicio",
    description="Endpoint para verificar que el servicio esté funcionando correctamente",
    response_description="Estado del servicio",
    responses={
        200: {
            "description": "Servicio funcionando correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "service": "analysis-service",
                        "version": "1.0.0",
                        "timestamp": "2024-01-01T00:00:00Z",
                    }
                }
            },
        }
    },
)
async def health_check():
    """
    Verifica el estado de salud del servicio de análisis.

    Returns:
        dict: Información del estado del servicio
    """
    return {
        "status": "healthy",
        "service": "analysis-service",
        "version": "1.0.0",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def _add_basic_openapi_info(openapi_schema):
    """Agrega información básica al esquema OpenAPI"""
    openapi_schema["info"]["contact"] = API_INFO["contact"]
    openapi_schema["info"]["license"] = API_INFO["license"]
    openapi_schema["components"]["securitySchemes"] = SECURITY_SCHEMES
    
    # Agregar información extra al nivel raíz del esquema
    for key, value in EXTRA_INFO.items():
        openapi_schema[key] = value

def _is_public_path(path):
    """Determina si una ruta es pública (no requiere autenticación)"""
    public_paths = ["/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"]
    return path in public_paths

def _is_http_method(method):
    """Determina si un método es un método HTTP válido"""
    return method.lower() in ["get", "post", "put", "delete", "patch"]

def _add_security_to_method(path_method):
    """Agrega configuración de seguridad a un método específico"""
    if "security" not in path_method:
        path_method["security"] = [{"bearerAuth": []}]
    else:
        current_security = path_method["security"]
        if not any("bearerAuth" in sec for sec in current_security):
            path_method["security"].append({"bearerAuth": []})

def _apply_security_to_paths(openapi_schema):
    """Aplica configuración de seguridad a todas las rutas que la requieren"""
    for path in openapi_schema["paths"]:
        if _is_public_path(path):
            continue
            
        for method in openapi_schema["paths"][path]:
            if _is_http_method(method):
                _add_security_to_method(openapi_schema["paths"][path][method])

def custom_openapi():
    """Función personalizada para generar OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=SERVERS,
    )

    _add_basic_openapi_info(openapi_schema)
    openapi_schema["security"] = [{"bearerAuth": []}]
    _apply_security_to_paths(openapi_schema)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi



if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
