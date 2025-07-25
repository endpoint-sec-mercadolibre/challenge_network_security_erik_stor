# Analysis Service

Servicio de análisis de archivos construido con FastAPI que implementa arquitectura de capas y se integra con el servicio de autenticación para proporcionar análisis de seguridad de configuraciones de red.

## Propósito

El Analysis Service es un microservicio especializado en el análisis de archivos de configuración de red, proporcionando evaluaciones de seguridad, validaciones de configuración y métricas de calidad. Se integra con el Config Service para acceder a archivos encriptados y con el Auth Service para autenticación segura.

## Características Principales

### 🏗️ Arquitectura de Capas
- **Controller Layer**: Maneja las peticiones HTTP, validaciones y respuestas
- **UseCase Layer**: Contiene la lógica de negocio y orquestación
- **Model Layer**: Define los modelos de datos y entidades
- **Repository Layer**: Gestiona la persistencia de datos y análisis

### 🔐 Autenticación y Seguridad
- **JWT Authentication**: Protección completa con tokens JWT del Auth Service
- **Middleware de Autenticación**: Validación automática en rutas protegidas
- **Encriptación AES-256-CBC**: Compatible con Config Service
- **Rutas Públicas**: Endpoints de salud y documentación sin autenticación

### 📊 Análisis de Configuraciones
- **Análisis de Seguridad**: Evaluación de configuraciones de red
- **Validación de Configuraciones**: Verificación de sintaxis y mejores prácticas
- **Métricas de Calidad**: Indicadores de configuración óptima
- **Logging Estructurado**: Trazabilidad completa de análisis

### 🛠️ Tecnologías
- **FastAPI**: Framework web moderno y rápido
- **Python 3.9+**: Lenguaje de programación
- **MongoDB**: Base de datos para almacenar análisis
- **JWT**: Autenticación basada en tokens
- **AES-256-CBC**: Encriptación de datos
- **Swagger/OpenAPI**: Documentación automática de API

## Estructura del Proyecto

```
analysis-service/
├── app/
│   ├── controller/           # Capa de controladores
│   │   ├── __init__.py
│   │   └── analysis_controller.py
│   ├── usecase/             # Capa de casos de uso
│   │   ├── __init__.py
│   │   └── analysis_usecase.py
│   ├── model/               # Capa de modelos
│   │   ├── __init__.py
│   │   ├── analysis_model.py
│   │   ├── analysis_record_model.py
│   │   └── analysis_repository.py
│   ├── services/            # Servicios auxiliares
│   │   ├── __init__.py
│   │   ├── auth_client.py
│   │   ├── auth_middleware.py
│   │   ├── encrypt.py
│   │   ├── logger.py
│   │   └── mongodb_service.py
│   ├── utils/               # Utilidades
│   │   ├── __init__.py
│   │   └── consts.py
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── swagger_config.py    # Configuración de Swagger
│   └── swagger_ui_config.py # Configuración de UI de Swagger
├── test/                    # Pruebas unitarias y e2e
│   ├── e2e/
│   │   ├── test_analysis_endpoint.py
│   │   ├── test_authentication.py
│   │   ├── test_health_endpoint.py
│   │   └── test_working_analysis.py
│   └── unit/
│       └── app/
│           ├── controller/
│           ├── model/
│           ├── services/
│           └── usecase/
├── Dockerfile               # Configuración de Docker
├── requirements.txt         # Dependencias de Python
├── requirements-test.txt    # Dependencias de pruebas
├── pyproject.toml          # Configuración del proyecto
├── setup.py               # Script de instalación
└── run.py                 # Script de ejecución
```

## Instalación y Configuración

### Prerrequisitos
- Python 3.9 o superior
- MongoDB 6.0 o superior
- Docker (opcional)

### Instalación Local

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd analysis-service
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   ```bash
   cp env.example .env
   # Editar .env con los valores apropiados
   ```

5. **Ejecutar el servicio**:
   ```bash
   python run.py
   ```

### Instalación con Docker

1. **Construir imagen**:
   ```bash
   docker build -t analysis-service .
   ```

2. **Ejecutar contenedor**:
   ```bash
   docker run -p 8002:8002 --env-file .env analysis-service
   ```

## Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `PORT` | Puerto del servicio | 8002 | No |
| `AUTH_SERVICE_URL` | URL del Auth Service | http://localhost:8080 | Sí |
| `CONFIG_SERVICE_URL` | URL del Config Service | http://localhost:8000 | Sí |
| `ENCRYPTION_KEY` | Clave de encriptación AES | - | Sí |
| `LOG_LEVEL` | Nivel de logging | INFO | No |
| `MONGODB_URI` | URI de conexión a MongoDB | mongodb://localhost:27017 | Sí |
| `MONGODB_DATABASE` | Nombre de la base de datos | analysis_service | No |

### Configuración de MongoDB

El servicio utiliza MongoDB para almacenar los registros de análisis. Asegúrate de que MongoDB esté ejecutándose y accesible desde la URL configurada.

## API Endpoints

### GET /api/v1/analyze

Analiza un archivo de configuración especificado por nombre, proporcionando evaluaciones de seguridad y métricas de calidad.

**Parámetros de Query:**
- `filename` (string, requerido): Nombre del archivo a analizar

**Headers:**
- `Authorization`: Bearer token JWT requerido

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "message": "Análisis completado exitosamente",
  "filename": "show_running.txt",
  "encrypted_filename": "U2FsdGVkX1...",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "file_size": 12288,
    "file_type": "network_config",
    "analysis_date": "2024-01-15T10:30:00Z",
    "security_level": "high",
    "encryption_algorithm": "AES-256-CBC + Base64",
    "security_score": 85,
    "recommendations": [
      "Configurar autenticación AAA",
      "Habilitar logging de seguridad",
      "Revisar configuración de SNMP"
    ],
    "vulnerabilities": [
      {
        "severity": "medium",
        "description": "SNMP community string por defecto",
        "recommendation": "Cambiar community string por defecto"
      }
    ],
    "compliance": {
      "cisco_best_practices": true,
      "security_standards": true,
      "network_policies": false
    }
  }
}
```

**Respuesta de Error (400):**
```json
{
  "success": false,
  "message": "Nombre de archivo requerido",
  "error_code": "FILENAME_REQUIRED",
  "detail": "El parámetro filename es obligatorio",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Respuesta de Error (404):**
```json
{
  "success": false,
  "message": "Archivo no encontrado",
  "error_code": "FILE_NOT_FOUND",
  "detail": "El archivo especificado no existe en el Config Service",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /health

Endpoint de salud del servicio.

**Respuesta (200):**
```json
{
  "status": "healthy",
  "service": "analysis-service",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "dependencies": {
    "auth_service": "connected",
    "config_service": "connected",
    "mongodb": "connected"
  }
}
```

## Documentación de la API

Una vez que el servicio esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **OpenAPI Schema**: http://localhost:8002/openapi.json

## Sistema de Autenticación

### Middleware de Autenticación JWT

El servicio implementa un middleware completo de autenticación:

#### Rutas Protegidas
- `/api/v1/analyze` - Requiere token JWT válido

#### Rutas Públicas
- `/health` - Estado del servicio
- `/docs` - Documentación Swagger
- `/redoc` - Documentación ReDoc
- `/openapi.json` - Esquema OpenAPI

#### Headers Requeridos
```http
Authorization: Bearer <token_jwt>
```

#### Respuestas de Error de Autenticación

**Token Faltante (401):**
```json
{
  "success": false,
  "message": "Token de autenticación requerido",
  "error_code": "TOKEN_REQUIRED",
  "detail": "Se requiere un token JWT Bearer para acceder a este recurso",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Token Inválido (401):**
```json
{
  "success": false,
  "message": "Token de autenticación inválido",
  "error_code": "INVALID_TOKEN",
  "detail": "El token JWT proporcionado no es válido o ha expirado",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Integración con Otros Servicios

### Auth Service
- **Propósito**: Validación de tokens JWT
- **Endpoint**: `/validate` del Auth Service
- **Configuración**: `AUTH_SERVICE_URL`

### Config Service
- **Propósito**: Obtención de archivos de configuración encriptados
- **Endpoint**: `/config/{filename}` del Config Service
- **Configuración**: `CONFIG_SERVICE_URL`

### MongoDB
- **Propósito**: Almacenamiento de registros de análisis
- **Configuración**: `MONGODB_URI` y `MONGODB_DATABASE`

## Sistema de Logging

### Configuración
- **Archivo**: `logs/analysis-service.log`
- **Formato**: JSON estructurado
- **Niveles**: DEBUG, INFO, WARN, ERROR, SUCCESS

### Ejemplo de Log
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "analysis-service",
  "function": "analyze_file",
  "message": "Análisis iniciado para archivo: show_running.txt",
  "data": {
    "filename": "show_running.txt",
    "user_id": "admin"
  }
}
```

## Pruebas

### Ejecutar Todas las Pruebas
```bash
# Pruebas unitarias
pytest test/unit/

# Pruebas e2e
pytest test/e2e/

# Cobertura de código
pytest --cov=app test/
```

### Pruebas de Autenticación
```bash
python test/e2e/test_authentication.py
```

### Pruebas de Análisis
```bash
python test/e2e/test_analysis_endpoint.py
```

## Desarrollo

### Estructura de Desarrollo
1. **Modelos**: Definir en `app/model/`
2. **Casos de Uso**: Implementar en `app/usecase/`
3. **Controladores**: Crear en `app/controller/`
4. **Servicios**: Agregar en `app/services/`

### Ejecutar en Modo Desarrollo
```bash
python run.py
```

El servicio se ejecutará con recarga automática en http://localhost:8002

## Despliegue

### Docker Compose
```yaml
analysis-service:
  build: ./analysis-service
  ports:
    - "8002:8002"
  environment:
    - AUTH_SERVICE_URL=http://auth-service:8080
    - CONFIG_SERVICE_URL=http://config-service:8000
  depends_on:
    - mongodb_meli_db
```

### Variables de Producción
- Configurar `ENCRYPTION_KEY` segura
- Establecer `LOG_LEVEL` apropiado
- Configurar URLs de servicios en producción

## Monitoreo y Troubleshooting

### Métricas de Salud
- Endpoint `/health` para verificación de estado
- Logs estructurados para debugging
- Conexiones a servicios dependientes

### Problemas Comunes

**Error de Conexión a Auth Service:**
```
ERROR: No se pudo conectar al Auth Service
SOLUCIÓN: Verificar AUTH_SERVICE_URL y estado del Auth Service
```

**Error de Conexión a Config Service:**
```
ERROR: No se pudo obtener archivo del Config Service
SOLUCIÓN: Verificar CONFIG_SERVICE_URL y estado del Config Service
```

**Error de MongoDB:**
```
ERROR: No se pudo conectar a MongoDB
SOLUCIÓN: Verificar MONGODB_URI y estado de MongoDB
```

## Documentación Adicional

- [Colección de Postman](auth-service-postman-collection.json)
- [Diagrama de Flujo](diagrama-flujo.md)
- [Diagrama de Secuencia](diagrama-secuencia.md)
- [Diagrama de Base de Datos](diagrama-base-datos.md)

## Contribución

1. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
2. Implementar cambios
3. Ejecutar pruebas: `pytest`
4. Crear pull request

## Licencia

Este proyecto está bajo la licencia MIT. 