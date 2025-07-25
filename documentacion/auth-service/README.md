# Servicio de Autenticación (Auth Service)

## Descripción General

El **Auth Service** es un microservicio desarrollado en **Go** que proporciona autenticación basada en JWT usando llaves RSA (pública/privada) para la comunicación segura entre servicios. Este servicio es fundamental para la seguridad de toda la arquitectura de microservicios.

### Tecnologías Utilizadas
- **Go 1.23.0** - Lenguaje de programación principal
- **Gin v1.10.1** - Framework web para APIs REST
- **Swagger/OpenAPI** - Documentación automática de APIs

## Características Principales

###  Autenticación JWT con RSA
- Generación automática de llaves RSA de 2048 bits
- Tokens JWT firmados con llave privada RSA
- Validación de tokens con llave pública RSA
- Tiempo de expiración configurable

###  Carácteristicas Avanzadas
- **Sistema de validación robusto** con validaciones personalizadas para los campos de entrada
- **Validaciones de seguridad** para usernames, passwords y tokens JWT
- **CORS habilitado** para comunicación entre servicios

###  Persistencia de Datos
- **MongoDB** como base de datos principal
- **Semilla automática** de usuario por **defecto**

### 🔧 Arquitectura
- **Arquitectura Hexagonal** (Clean Architecture)
- **Inyección de Dependencias** con contenedor DI
- **Separación de capas**: Domain, Infrastructure, Entrypoints
- **Logging estructurado** con persistencia en un archivo de logs y mostrados consola

## Estructura del Proyecto

```
auth-service/
├── domain/                    # Lógica de dominio
│   ├── entities/             # Entidades del dominio
│   │   ├── token.go         # Entidad Token
│   │   └── user.go          # Entidad User
│   ├── repositories/        # Interfaces de repositorios
│   │   └── user_repository.go
│   ├── services/           # Servicios de dominio
│   │   ├── password_service.go
│   │   ├── seed_service.go
│   │   └── token_service.go
│   └── validators/         # Validadores
│       └── validators.go
├── entrypoints/            # Puntos de entrada
│   └── api/               # Controladores HTTP
│       ├── auth_controller.go
│       ├── health_controller.go
│       ├── token_controller.go
│       └── routes.go
├── infrastructure/         # Infraestructura
│   ├── di/               # Inyección de dependencias
│   │   └── container.go
│   ├── logger/           # Sistema de logging
│   │   └── logger.go
│   ├── repositories/     # Implementaciones de repositorios
│   │   └── mongodb_user_repository.go
│   └── services/         # Servicios de infraestructura
│       └── jwt_token_service.go
├── middlewares/          # Middlewares HTTP
│   ├── cors_middleware.go
│   ├── logging_middleware.go
│   └── validation_middleware.go
├── usecases/            # Casos de uso
│   ├── login_usecase.go
│   └── validate_token_usecase.go
├── test/               # Tests
│   ├── test_config.go
│   └── unit/          # Tests unitarios
├── main.go            # Punto de entrada
├── go.mod            # Dependencias Go
├── go.sum            # Checksums de dependencias
├── Dockerfile        # Configuración Docker
└── README.md         # Documentación
```

## Endpoints de la API

### 🔑 POST /login
Autentica un usuario y devuelve un token JWT.

**URL:** `POST http://localhost:8080/login`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "Password123!"
}
```

**Validaciones de Entrada:**
- **Username**: 3-50 caracteres, solo letras, números, guiones y guiones bajos
- **Password**: mínimo 8 caracteres con mayúsculas, minúsculas, números y caracteres especiales

**Response Exitosa (200):**
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNzA1NzQ5NjAwLCJleHAiOjE3MDU4MzYwMDB9.signature",
  "user": "admin"
}
```

**Response de Error (400 - Validación):**
```json
{
  "error": "Datos de entrada inválidos",
  "details": {
    "Username": "El campo Username debe tener entre 3 y 50 caracteres y solo puede contener letras, números, guiones y guiones bajos",
    "Password": "El campo Password debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales"
  }
}
```

**Response de Error (401 - Credenciales inválidas):**
```json
{
  "error": "Credenciales inválidas",
  "message": "El usuario o contraseña proporcionados son incorrectos"
}
```

### ✅ POST /validate
Valida un token JWT.

**URL:** `POST http://localhost:8080/validate`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNzA1NzQ5NjAwLCJleHAiOjE3MDU4MzYwMDB9.signature"
}
```

**Response (Token Válido - 200):**
```json
{
  "valid": true,
  "user": "admin"
}
```

**Response (Token Inválido - 400):**
```json
{
  "valid": false,
  "error": "token expirado"
}
```

### 🔓 GET /public-key
Obtiene la llave pública RSA en formato PEM.

**URL:** `GET http://localhost:8080/public-key`

**Response (200):**
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----
```

### 🏥 GET /health
Endpoint de salud del servicio que también ejecuta la semilla de datos para crear el usuario por defecto si no existe.

**URL:** `GET http://localhost:8080/health`

**Response (200):**
```json
{
  "status": "healthy",
  "service": "auth-service",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

## Configuración del Entorno

### Variables de Entorno

| Variable | Descripción | Valor por Defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `PORT` | Puerto del servicio | `8080` | Si |
| `MONGO_URI` | URI de conexión a MongoDB | `mongodb://localhost:27017` | Si |
| `MONGO_DATABASE` | Nombre de la base de datos | `auth_service` | Si |
| `JWT_SECRET` | Clave secreta para JWT | Auto-generada | Si |
| `JWT_EXPIRATION` | Tiempo de expiración del token | `24h` | Si |

### Archivo de Configuración (.env)
```bash
# Configuración del Servicio
PORT=8080

# Base de Datos MongoDB
MONGO_URI=mongodb://mongodb_meli_db:27017
MONGO_DATABASE=auth_service

# JWT Configuration
JWT_EXPIRATION=24h

# Logging
LOG_LEVEL=INFO
```

### Credenciales de Prueba
- **Usuario:** `admin`
- **Contraseña:** `Password123!`

**Importante:** Estas credenciales son del usuario por defecto. 

## Base de Datos

### Esquema de MongoDB

**Colección: `users`**

```json
{
  "_id": "ObjectId",
  "username": "string (único)",
  "password": "string (encriptado)",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Configuración de MongoDB
El servicio utiliza MongoDB para almacenar usuarios. Al hacer la primera petición al endpoint `/health`, se creará automáticamente el usuario por defecto si no existe.

## Llaves RSA

### Generación Automática
El servicio genera automáticamente un par de llaves RSA (2048 bits) en los archivos:
- `private.pem`: Llave privada (solo para el servicio de autenticación)
- `public.pem`: Llave pública (puede ser compartida con otros servicios)

### Ubicación de Archivos
```
auth-service/
├── private.pem    # Llave privada RSA
└── public.pem     # Llave pública RSA
```

## Sistema de Validación

### Validaciones Implementadas

#### Username
- **Longitud**: 3-50 caracteres
- **Caracteres permitidos**: Letras, números, guiones y guiones bajos
- **Regex**: `^[a-zA-Z0-9_-]{3,50}$`

#### Password
- **Longitud mínima**: 8 caracteres
- **Requisitos**:
  - Al menos una mayúscula
  - Al menos una minúscula
  - Al menos un número
  - Al menos un carácter especial
- **Regex**: `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$`

#### JWT Token
- **Formato**: 3 partes separadas por puntos
- **Validación**: Estructura base64 válida
- **Firma**: Verificación con llave pública RSA

### Ejemplos de Respuestas de Error
```json
{
  "error": "Datos de entrada inválidos",
  "details": {
    "Username": "El campo Username debe tener entre 3 y 50 caracteres y solo puede contener letras, números, guiones y guiones bajos",
    "Password": "El campo Password debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales"
  }
}
```

## Ejecución

### Desarrollo Local

#### Prerrequisitos
- Go 1.21 o superior
- MongoDB 6.0 o superior

#### Pasos de Instalación
```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd auth-service

# 2. Instalar dependencias
go mod tidy

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con los valores apropiados

# 4. Ejecutar el servicio
go run main.go
```

### Docker

#### Construir Imagen
```bash
docker build -t auth-service .
```

#### Ejecutar Contenedor
```bash
docker run -p 8080:8080 \
  -e MONGO_URI=mongodb://host.docker.internal:27017 \
  -e MONGO_DATABASE=auth_service \
  auth-service
```

### Docker Compose (Recomendado)

#### Iniciar Servicios
```bash
# Iniciar todos los servicios (MongoDB + Auth Service)
docker-compose up -d

# Ver logs
docker-compose logs -f auth-service

# Detener servicios
docker-compose down
```

#### Verificar Estado
```bash
# Verificar que el servicio esté funcionando
curl http://localhost:8080/health

# Verificar logs
docker-compose logs auth-service
```

## Testing

### Ejecutar Tests
```bash
# Todos los tests
go test ./...

# Tests con coverage
go test -cover ./...

# Tests específicos
go test ./test/unit/domain/validators/
go test ./test/unit/domain/entities/
go test ./test/unit/infrastructure/
```

### Cobertura de Tests
```bash
# Generar reporte de cobertura
go test -coverprofile=coverage.out ./...

# Ver reporte en navegador
go tool cover -html=coverage.out
```

## Integración con Otros Servicios

### Flujo de Integración
1. **Obtener llave pública** desde `/public-key`
2. **Usar la llave pública** para validar tokens JWT
3. **Enviar tokens** en el header `Authorization: Bearer <token>`

### Ejemplo de Integración
```bash
# 1. Obtener token
curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Password123!"}'

# 2. Usar token en otros servicios
curl -X GET http://localhost:8000/config/archivo.txt \
  -H "Authorization: Bearer <token_jwt>"
```

## Logs y Monitoreo

### Niveles de Log
- **INFO**: Información general del servicio
- **ERROR**: Errores de aplicación
- **DEBUG**: Información detallada para debugging
- **WARN**: Advertencias del sistema

### Formato de Logs
```json
{
  "level": "INFO",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "auth-service",
  "message": "Usuario autenticado exitosamente",
  "user": "admin",
  "ip": "192.168.1.100"
}
```

## Seguridad

### Medidas Implementadas
- **Validación de entrada** robusta
- **Encriptación de contraseñas** con bcrypt
- **Tokens JWT** con firma RSA
- **CORS configurado** para comunicación entre servicios
- **Logging** para todas las operaciones
- **Rate limiting** implícito en validaciones

### Recomendaciones de Seguridad
1. **Cambiar credenciales por defecto** en producción
2. **Configurar HTTPS** en producción
3. **Implementar rate limiting** adicional si es necesario
4. **Monitorear logs** de autenticación
5. **Rotar llaves RSA** periódicamente

## Troubleshooting

### Problemas Comunes

#### Error de Conexión a MongoDB
```
Error: no reachable servers
```
**Solución:** Verificar que MongoDB esté ejecutándose y accesible.

#### Error de Validación de Token
```
Error: token expirado
```
**Solución:** Obtener un nuevo token con `/login`.

#### Error de CORS
```
Error: CORS policy
```
**Solución:** Verificar configuración de CORS en el middleware.

### Logs de Debug
```bash
# Habilitar logs de debug
export LOG_LEVEL=DEBUG
go run main.go
```

## Documentación Adicional

Para información más detallada, puedes buscar en la carpeta de documentación en la carpeta de este proyecto
los siguientes artefactos:

- 📋 **Colección de Postman** - `auth-service-postman-collection.json`
- 🔄 **Diagrama de Flujo** - `diagrama-flujo.md`
- ⏱️ **Diagrama de Secuencia** - `diagrama-secuencia.md`
- 🗄️ **Diagrama de Base de Datos** - `diagrama-base-datos.md` 