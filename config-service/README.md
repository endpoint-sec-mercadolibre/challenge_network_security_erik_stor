# Config Service

Microservicio de lectura de configuraciones implementando arquitectura hexagonal con Express y políticas de seguridad.

## Características

- ✅ Arquitectura hexagonal (Clean Architecture)
- ✅ Express.js como servidor web
- 🔒 Helmet para políticas de seguridad
- 🔐 Encriptación AES-256-CBC compatible con Python
- 🔑 Autenticación JWT con middleware
- 📝 Logging estructurado
- 🧪 Tests con Jest
- 🔧 TypeScript
- 📦 Webpack para bundling

## Instalación

```bash
npm install
```

## Scripts disponibles

### Desarrollo
```bash
# Ejecutar en modo desarrollo
npm run dev

# Ejecutar con hot reload
npm run dev:watch
```

### Producción
```bash
# Construir para producción
npm run build

# Ejecutar en producción
npm start
```

### Testing
```bash
# Ejecutar tests
npm test

# Ejecutar tests en modo watch
npm run test:watch

# Generar reporte de cobertura
npm run test:coverage
```

### Linting
```bash
# Verificar código
npm run lint

# Corregir errores automáticamente
npm run lint:fix

# Verificar tipos TypeScript
npm run type-check
```

### Utilidades de Encriptación
```bash
# Probar compatibilidad de encriptación
npm run encrypt:test

# Ver ayuda de utilidad de encriptación
npm run encrypt:help

# Encriptar texto manualmente
npm run build && node encrypt-utility.js encrypt "archivo.txt"

# Desencriptar texto manualmente
npm run build && node encrypt-utility.js decrypt "texto_encriptado"
```

## Endpoints

### Health Check
```
GET /health
```

**Respuesta:**
```json
{
  "status": "OK",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "service": "config-service"
}
```

### Configuración (Requiere Autenticación)
```
GET /config/{filename}
```

**Headers requeridos:**
```
Authorization: Bearer <jwt_token>
```

**Parámetros:**
- `filename`: Nombre del archivo de configuración encriptado en base64

**Respuesta exitosa:**
```json
{
  "message": "Archivo leído exitosamente",
  "data": {
    "message": "Archivo leído exitosamente",
    "content": "Contenido del archivo de configuración..."
  }
}
```

**Respuesta de error (401 - No autorizado):**
```json
{
  "error": "Token de autorización requerido",
  "message": "Debe proporcionar un token JWT en el header Authorization",
  "code": "AUTH_TOKEN_REQUIRED"
}
```

## Variables de entorno

```bash
# Puerto del servidor
PORT=3000

# Entorno
NODE_ENV=development

# Servicio de autenticación
AUTH_SERVICE_URL=http://auth-service:8080

# Configuración de archivos
FILE_DEFAULT_ENCODING=utf8
ENCRYPTION_KEY=mi_contraseña_secreta

# Base de datos MongoDB
MONGO_HOST=mongodb_meli_db
MONGO_PORT=27017
MONGO_DATABASE=analysis_service
MONGO_USERNAME=admin
MONGO_PASSWORD=password
```

## Autenticación

El servicio implementa autenticación JWT mediante un middleware que valida tokens contra el servicio de autenticación.

### Middleware de Autenticación

El middleware `authMiddleware` se encarga de:

1. **Extraer el token** del header `Authorization: Bearer <token>`
2. **Validar el formato** del token
3. **Comunicarse con el auth-service** para validar el token
4. **Agregar información del usuario** al request si es válido
5. **Rechazar requests** con tokens inválidos o faltantes

### Códigos de Error

- `AUTH_TOKEN_REQUIRED`: No se proporcionó header de autorización
- `AUTH_TOKEN_INVALID_FORMAT`: Formato de token incorrecto
- `AUTH_TOKEN_EMPTY`: Token vacío
- `AUTH_TOKEN_INVALID`: Token inválido o expirado
- `AUTH_INTERNAL_ERROR`: Error interno del middleware

## Políticas de seguridad (Helmet)

El servicio incluye las siguientes políticas de seguridad configuradas con Helmet:

- **Content Security Policy (CSP)**: Restringe recursos permitidos
- **HTTP Strict Transport Security (HSTS)**: Fuerza conexiones HTTPS
- **X-Content-Type-Options**: Previene MIME type sniffing
- **X-Frame-Options**: Previene clickjacking
- **X-XSS-Protection**: Protección básica contra XSS
- **Referrer Policy**: Controla información del referrer
- **Hide Powered-By**: Oculta el header X-Powered-By

## Estructura del proyecto

```
src/
├── adapters/          # Adaptadores externos
│   ├── repository/    # Repositorios de datos
│   └── service/       # Servicios externos
├── domain/            # Lógica de dominio
│   ├── command_handlers/
│   ├── commands/
│   ├── exceptions/
│   ├── model/
│   └── ports/
├── entrypoints/       # Puntos de entrada
│   └── api/
├── infra/             # Infraestructura
└── utils/             # Utilidades
```

## Desarrollo

### Ejecutar en modo desarrollo
```bash
npm run dev
```

El servidor estará disponible en `http://localhost:3000`

### Ejecutar con hot reload
```bash
npm run dev:watch
```

### Ejecutar tests
```bash
npm test
```

## Despliegue

### AWS Lambda
El servicio mantiene compatibilidad con AWS Lambda a través de la función `handler` exportada.

### Servidor Express
Para despliegue como servidor web tradicional, usar:
```bash
npm run build
npm start
```

## Logs

El servicio utiliza un sistema de logging estructurado que registra:
- Requests HTTP
- Errores de aplicación
- Información de auditoría
- Métricas de rendimiento 
