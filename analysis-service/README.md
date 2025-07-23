# Analysis Service

Servicio de análisis de archivos construido con FastAPI que implementa arquitectura de capas y se integra con el servicio de autenticación.

## Características

- **Arquitectura de Capas**: Implementa el patrón de arquitectura con tres capas principales:
  - **Controller**: Maneja las peticiones HTTP y validaciones
  - **UseCase**: Contiene la lógica de negocio
  - **Model**: Define los modelos de datos

- **Autenticación JWT**: Protección completa de rutas con tokens JWT del servicio de autenticación
  - **Middleware de Autenticación**: Validación automática de tokens en todas las rutas protegidas
  - **Rutas Públicas**: Endpoints como `/health`, `/docs` accesibles sin autenticación
  - **Manejo de Errores**: Respuestas detalladas para tokens inválidos o faltantes
- **Encriptación**: Sistema de encriptación compatible con config-service
- **Logging**: Sistema de logs similar al config-service
- **Swagger**: Documentación automática de la API con esquemas de seguridad

## Estructura del Proyecto

```
analysis-service/
├── controller/           # Capa de controladores
│   ├── __init__.py
│   └── analysis_controller.py
├── usecase/             # Capa de casos de uso
│   ├── __init__.py
│   └── analysis_usecase.py
├── model/               # Capa de modelos
│   ├── __init__.py
│   └── analysis_model.py
├── utils/               # Utilidades
│   ├── __init__.py
│   ├── logger.py
│   ├── encrypt.py
│   ├── auth_client.py
│   └── auth_middleware.py
├── logs/                # Directorio de logs (se crea automáticamente)
├── main.py              # Punto de entrada de la aplicación
├── requirements.txt     # Dependencias de Python
├── env.example          # Variables de entorno de ejemplo
└── README.md           # Este archivo
```

## Instalación

1. **Clonar el repositorio** (si aplica)

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**:
   ```bash
   cp env.example .env
   # Editar .env con los valores apropiados
   ```

4. **Ejecutar el servicio**:
   ```bash
   python main.py
   ```

## Configuración

### Variables de Entorno

- `PORT`: Puerto del servicio (default: 8002)
- `AUTH_SERVICE_URL`: URL del servicio de autenticación (default: http://localhost:8001)
- `ENCRYPTION_KEY`: Clave de encriptación (debe ser la misma que config-service)
- `LOG_LEVEL`: Nivel de logging (default: INFO)

## API Endpoints

### GET /api/v1/analyze

Analiza un archivo especificado por nombre, encriptando el nombre para comunicación segura.

**Parámetros de Query:**
- `filename` (string, requerido): Nombre del archivo a analizar

**Headers:**
- `Authorization`: Bearer token JWT requerido

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "message": "Análisis completado exitosamente",
  "filename": "document.txt",
  "encrypted_filename": "U2FsdGVkX1...",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "file_size": 12288,
    "file_type": "text",
    "analysis_date": "2024-01-15T10:30:00",
    "security_level": "high",
    "encryption_algorithm": "AES-256-CBC + Base64"
  }
}
```

### GET /health

Endpoint de salud del servicio.

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "analysis-service"
}
```

## Documentación de la API

Una vez que el servicio esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

## Autenticación

### Sistema de Autenticación JWT

El servicio de análisis implementa un sistema completo de autenticación basado en tokens JWT:

#### Middleware de Autenticación
- **Validación Automática**: Todos los endpoints protegidos validan automáticamente el token JWT
- **Rutas Públicas**: Los siguientes endpoints no requieren autenticación:
  - `/health` - Estado del servicio
  - `/docs` - Documentación Swagger
  - `/redoc` - Documentación ReDoc
  - `/openapi.json` - Esquema OpenAPI

#### Headers Requeridos
Para acceder a endpoints protegidos, incluye el header:
```
Authorization: Bearer <token_jwt>
```

#### Respuestas de Error
El servicio devuelve respuestas detalladas para errores de autenticación:

**Token Faltante (401):**
```json
{
  "success": false,
  "message": "Token de autenticación requerido",
  "error_code": "TOKEN_REQUIRED",
  "detail": "Se requiere un token JWT Bearer para acceder a este recurso",
  "timestamp": "2024-01-15T10:30:00"
}
```

**Token Inválido (401):**
```json
{
  "success": false,
  "message": "Token de autenticación inválido",
  "error_code": "INVALID_TOKEN",
  "detail": "El token JWT proporcionado no es válido o ha expirado",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Pruebas de Autenticación

Ejecuta el script de pruebas para verificar que la autenticación funciona correctamente:

```bash
python test_auth.py
```

Este script prueba:
- ✅ Endpoint público (`/health`)
- ✅ Endpoint protegido sin token (debe fallar)
- ✅ Endpoint protegido con token inválido (debe fallar)
- ✅ Endpoint protegido con token válido (debe funcionar)

## Integración con Otros Servicios

### Servicio de Autenticación

El analysis-service se integra con el auth-service para validar tokens JWT. Asegúrate de que:

1. El auth-service esté ejecutándose en el puerto configurado
2. La variable `AUTH_SERVICE_URL` apunte al servicio correcto
3. Los tokens JWT sean válidos

### Config Service

El sistema de encriptación es compatible con config-service. Ambos servicios deben usar la misma `ENCRYPTION_KEY` para que la comunicación encriptada funcione correctamente.

## Logs

Los logs se almacenan en el directorio `logs/` con el nombre `analysis-service.log`. El sistema de logging incluye:

- Información de contexto (función, timestamp, datos adicionales)
- Colores en consola para diferentes niveles
- Formato JSON estructurado
- Niveles: INFO, ERROR, WARN, DEBUG, SUCCESS

## Desarrollo

### Agregar Nuevos Endpoints

1. Crear el modelo en `model/`
2. Implementar la lógica en `usecase/`
3. Crear el controlador en `controller/`
4. Registrar la ruta en `main.py`

### Ejecutar en Modo Desarrollo

```bash
python main.py
```

El servicio se ejecutará con recarga automática en http://localhost:8002

## Docker

Para ejecutar con Docker:

```bash
# Construir imagen
docker build -t analysis-service .

# Ejecutar contenedor
docker run -p 8002:8002 --env-file .env analysis-service
```

## Pruebas

### Script de Pruebas de Autenticación

Ejecuta el script automatizado para probar toda la funcionalidad de autenticación:

```bash
python test_auth.py
```

### Pruebas Manuales

Para probar manualmente:

1. **Obtener token del auth-service**:
   ```bash
   curl -X POST http://localhost:8001/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password123"}'
   ```

2. **Analizar archivo**:
   ```bash
   curl -X GET "http://localhost:8002/api/v1/analyze?filename=document.txt" \
     -H "Authorization: Bearer <token_jwt>"
   ```

3. **Probar endpoint público**:
   ```bash
   curl -X GET http://localhost:8002/health
   ```

4. **Probar endpoint protegido sin token** (debe fallar):
   ```bash
   curl -X GET "http://localhost:8002/api/v1/analyze?filename=document.txt"
   ``` 