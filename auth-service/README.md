# Servicio de Autenticación

Este servicio proporciona autenticación basada en JWT usando llaves RSA (pública/privada) para la comunicación segura entre servicios.

## Características

- Autenticación con JWT usando llaves RSA
- Generación automática de llaves pública/privada
- Validación de tokens
- Endpoint para obtener la llave pública
- CORS habilitado para comunicación entre servicios
- **Sistema de validación robusto** con validaciones personalizadas
- **Middleware de validación automática** para todos los endpoints
- **Mensajes de error en español** para mejor experiencia de usuario
- **Validaciones de seguridad** para usernames, passwords y tokens JWT

## Endpoints

### POST /login
Autentica un usuario y devuelve un token JWT.

**Request:**
```json
{
  "username": "admin",
  "password": "Password123!"
}
```

**Nota:** El sistema de validación requiere:
- Username: 3-50 caracteres, solo letras, números, guiones y guiones bajos
- Password: mínimo 8 caracteres con mayúsculas, minúsculas, números y caracteres especiales

**Response:**
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": "admin"
}
```

### POST /validate
Valida un token JWT.

**Request:**
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (válido):**
```json
{
  "valid": true,
  "user": "admin"
}
```

**Response (inválido):**
```json
{
  "valid": false,
  "error": "token expirado"
}
```

### GET /public-key
Obtiene la llave pública RSA en formato PEM.

### GET /health
Endpoint de salud del servicio que también ejecuta la semilla de datos para crear el usuario por defecto si no existe.

## Configuración

### Variables de entorno
- `PORT`: Puerto del servicio (default: 8080)
- `MONGO_URI`: URI de conexión a MongoDB (default: mongodb://localhost:27017)
- `MONGO_DATABASE`: Nombre de la base de datos (default: auth_service)
- `JWT_SECRET`: Clave secreta para JWT (opcional, se genera automáticamente)
- `JWT_EXPIRATION`: Tiempo de expiración del token (default: 24h)

### Credenciales de prueba
- Usuario: `admin`
- Contraseña: `Password123!`

**Importante:** Las credenciales deben cumplir con las reglas de validación implementadas.

### Base de datos
El servicio utiliza MongoDB para almacenar usuarios. Al hacer la primera petición al endpoint `/health`, se creará automáticamente el usuario por defecto si no existe.

## Ejecución

### Local
```bash
go mod tidy
go run main.go
```

### Docker
```bash
docker build -t auth-service .
docker run -p 8080:8080 auth-service
```

### Docker Compose (recomendado para desarrollo)
```bash
# Iniciar todos los servicios (MongoDB + Auth Service)
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

## Llaves RSA

El servicio genera automáticamente un par de llaves RSA (2048 bits) en los archivos:
- `private.pem`: Llave privada (solo para el servicio de autenticación)
- `public.pem`: Llave pública (puede ser compartida con otros servicios)

## Sistema de Validación

El servicio incluye un sistema de validación robusto que valida automáticamente todos los datos de entrada:

### Validaciones Implementadas
- **Username**: 3-50 caracteres, solo letras, números, guiones y guiones bajos
- **Password**: Mínimo 8 caracteres con mayúsculas, minúsculas, números y caracteres especiales
- **JWT Token**: Formato válido de token JWT (3 partes separadas por puntos)
- **Campos requeridos**: Validación de campos obligatorios
- **Strings no vacíos**: Validación de strings después de trim

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

Para más detalles sobre el sistema de validación, consulta [docs/VALIDATION.md](docs/VALIDATION.md).

## Testing

### Ejecutar Tests
```bash
# Todos los tests
go test ./...

# Solo tests de validación
go test ./test/unit/domain/validators/

# Tests con coverage
go test -cover ./test/unit/domain/validators/
```

## Integración con otros servicios

Para integrar este servicio con otros servicios:

1. Obtener la llave pública desde `/public-key`
2. Usar la llave pública para validar tokens JWT
3. Enviar tokens en el header `Authorization: Bearer <token>` 