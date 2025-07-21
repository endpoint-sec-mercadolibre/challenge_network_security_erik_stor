# Servicio de Autenticación

Este servicio proporciona autenticación basada en JWT usando llaves RSA (pública/privada) para la comunicación segura entre servicios.

## Características

- Autenticación con JWT usando llaves RSA
- Generación automática de llaves pública/privada
- Validación de tokens
- Endpoint para obtener la llave pública
- CORS habilitado para comunicación entre servicios

## Endpoints

### POST /login
Autentica un usuario y devuelve un token JWT.

**Request:**
```json
{
  "username": "admin",
  "password": "password"
}
```

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
Endpoint de salud del servicio.

## Configuración

### Variables de entorno
- `PORT`: Puerto del servicio (default: 8080)

### Credenciales de prueba
- Usuario: `admin`
- Contraseña: `password`

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

## Llaves RSA

El servicio genera automáticamente un par de llaves RSA (2048 bits) en los archivos:
- `private.pem`: Llave privada (solo para el servicio de autenticación)
- `public.pem`: Llave pública (puede ser compartida con otros servicios)

## Integración con otros servicios

Para integrar este servicio con otros servicios:

1. Obtener la llave pública desde `/public-key`
2. Usar la llave pública para validar tokens JWT
3. Enviar tokens en el header `Authorization: Bearer <token>` 