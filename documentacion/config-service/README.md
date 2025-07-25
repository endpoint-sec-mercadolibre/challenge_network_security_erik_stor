# Servicio de Configuración (Config Service)

## Descripción General

El **Config Service** es un microservicio desarrollado en **Node.js** con **TypeScript** que implementa arquitectura hexagonal (Clean Architecture) para la lectura y gestión de archivos de configuración de dispositivos de red. Este servicio proporciona acceso seguro y encriptado a archivos de configuración mediante autenticación JWT.

## Características Principales

### 🔧 Arquitectura Hexagonal
- **Clean Architecture** con separación clara de capas
- **Inyección de Dependencias** para desacoplamiento
- **Patrón Repository** para acceso a datos
- **Command Pattern** para operaciones de negocio

### 🔐 Seguridad Avanzada
- **Autenticación JWT** con middleware integrado
- **Encriptación AES-256-CBC** compatible con Python
- **Helmet** para políticas de seguridad HTTP
- **Validación de entrada** robusta
- **CORS configurado** para comunicación entre servicios

### 📁 Gestión de Archivos
- **Lectura de archivos** de configuración encriptados
- **Encriptación/desencriptación** automática
- **Validación de formatos** de archivo
- **Manejo de errores** estructurado

### 🛠️ Tecnologías
- **Node.js** con **TypeScript**
- **Express.js** como servidor web
- **Webpack** para bundling
- **Jest** para testing
- **ESLint** y **Prettier** para calidad de código

## Estructura del Proyecto

```
config-service/
├── src/
│   ├── adapters/              # Adaptadores externos
│   │   ├── repository/        # Repositorios de datos
│   │   └── service/           # Servicios externos
│   │       ├── AuthService.ts
│   │       └── FileReaderService.ts
│   ├── config/               # Configuración
│   │   └── swagger.ts
│   ├── domain/               # Lógica de dominio
│   │   ├── command_handlers/ # Manejadores de comandos
│   │   │   └── GetConfigCommandHandler.ts
│   │   ├── commands/         # Comandos de dominio
│   │   │   └── GetConfigCommand.ts
│   │   ├── common/           # Utilidades comunes
│   │   │   ├── consts/
│   │   │   │   ├── Setup.ts
│   │   │   │   └── SuccessMessages.ts
│   │   │   └── SuccessResponse.ts
│   │   ├── exceptions/       # Excepciones personalizadas
│   │   │   ├── constants/
│   │   │   │   ├── ErrorMessages.ts
│   │   │   │   └── InputMessageException.ts
│   │   │   ├── core/
│   │   │   │   ├── BaseException.ts
│   │   │   │   ├── InvalidDataException.ts
│   │   │   │   ├── NotFoundException.ts
│   │   │   │   └── SystemException.ts
│   │   │   └── GetContentException.ts
│   │   ├── model/            # Modelos de dominio
│   │   │   ├── Input.ts
│   │   │   ├── interfaces/
│   │   │   │   ├── IOutput.ts
│   │   │   │   └── IResponse.ts
│   │   │   └── Output.ts
│   │   └── ports/            # Puertos (interfaces)
│   │       └── IFileReaderService.ts
│   ├── entrypoints/          # Puntos de entrada
│   │   └── api/              # Controladores HTTP
│   │       ├── GetConfigController.ts
│   │       └── middlewares/  # Middlewares
│   │           ├── authMiddleware.ts
│   │           ├── catchError.ts
│   │           ├── extractFilename.ts
│   │           └── initLogger.ts
│   ├── infra/               # Infraestructura
│   │   └── Logger.ts
│   ├── storage/             # Almacenamiento de archivos
│   │   └── show_running.txt
│   └── utils/               # Utilidades
│       ├── Encrypt.ts
│       ├── ErrorExtractor.ts
│       └── FileReaderUtil.ts
├── test/                   # Tests
│   └── unit/              # Tests unitarios
├── dist/                  # Código compilado
├── package.json           # Dependencias
├── tsconfig.json          # Configuración TypeScript
├── webpack.config.js      # Configuración Webpack
├── jest.config.js         # Configuración Jest
├── Dockerfile             # Configuración Docker
└── README.md              # Documentación
```

## Endpoints de la API

### 🏥 GET /health
Endpoint de salud del servicio.

**URL:** `GET http://localhost:8000/health`

**Headers:** No requeridos

**Response (200):**
```json
{
  "status": "OK",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "config-service"
}
```

### 📄 GET /config/{filename}
Obtiene el contenido de un archivo de configuración encriptado.

**URL:** `GET http://localhost:8000/config/{filename}`

**Headers requeridos:**
```
Authorization: Bearer <jwt_token>
```

**Parámetros de Path:**
- `filename`: Nombre del archivo de configuración encriptado en base64

**Ejemplo de Request:**
```bash
curl -X GET "http://localhost:8000/config/U2FsdGVkX1..." \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response Exitosa (200):**
```json
{
  "message": "Archivo leído exitosamente",
  "data": {
    "message": "Archivo leído exitosamente",
    "content": "Contenido del archivo de configuración..."
  }
}
```

**Response de Error (401 - No autorizado):**
```json
{
  "error": "Token de autorización requerido",
  "message": "Debe proporcionar un token JWT en el header Authorization",
  "code": "AUTH_TOKEN_REQUIRED"
}
```

**Response de Error (400 - Token inválido):**
```json
{
  "error": "Token de autorización inválido",
  "message": "El token JWT proporcionado no es válido o ha expirado",
  "code": "AUTH_TOKEN_INVALID"
}
```

**Response de Error (404 - Archivo no encontrado):**
```json
{
  "error": "Archivo no encontrado",
  "message": "El archivo de configuración solicitado no existe",
  "code": "FILE_NOT_FOUND"
}
```

## Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `PORT` | Puerto del servicio | `8000` | No |
| `NODE_ENV` | Entorno de ejecución | `production` | No |
| `AUTH_SERVICE_URL` | URL del servicio de autenticación | `http://auth-service:8080` | Sí |
| `FILE_DEFAULT_ENCODING` | Codificación de archivos | `utf8` | No |
| `ENCRYPTION_KEY` | Clave de encriptación | `mi_contraseña_secreta_super_segura_2024` | Sí |
| `MONGO_HOST` | Host de MongoDB | `mongodb_meli_db` | No |
| `MONGO_PORT` | Puerto de MongoDB | `27017` | No |
| `MONGO_DATABASE` | Base de datos MongoDB | `analysis_service` | No |

### Archivo de Configuración (.env)
```bash
# Configuración del Servicio
PORT=8000
NODE_ENV=production

# Servicio de Autenticación
AUTH_SERVICE_URL=http://auth-service:8080

# Configuración de Archivos
FILE_DEFAULT_ENCODING=utf8
ENCRYPTION_KEY=mi_contraseña_secreta_super_segura_2024

# Base de Datos MongoDB
MONGO_HOST=mongodb_meli_db
MONGO_PORT=27017
MONGO_DATABASE=analysis_service
```

## Autenticación

### Sistema de Autenticación JWT

El servicio implementa autenticación JWT mediante un middleware que valida tokens contra el servicio de autenticación.

#### Middleware de Autenticación

El middleware `authMiddleware` se encarga de:

1. **Extraer el token** del header `Authorization: Bearer <token>`
2. **Validar el formato** del token
3. **Comunicarse con el auth-service** para validar el token
4. **Agregar información del usuario** al request si es válido
5. **Rechazar requests** con tokens inválidos o faltantes

#### Headers Requeridos
Para acceder a endpoints protegidos, incluye el header:
```
Authorization: Bearer <token_jwt>
```

#### Códigos de Error de Autenticación

- `AUTH_TOKEN_REQUIRED`: No se proporcionó header de autorización
- `AUTH_TOKEN_INVALID_FORMAT`: Formato de token incorrecto
- `AUTH_TOKEN_EMPTY`: Token vacío
- `AUTH_TOKEN_INVALID`: Token inválido o expirado
- `AUTH_INTERNAL_ERROR`: Error interno del middleware

## Políticas de Seguridad (Helmet)

El servicio incluye las siguientes políticas de seguridad configuradas con Helmet:

### Configuraciones Implementadas

- **Content Security Policy (CSP)**: Restringe recursos permitidos
- **HTTP Strict Transport Security (HSTS)**: Fuerza conexiones HTTPS
- **X-Content-Type-Options**: Previene MIME type sniffing
- **X-Frame-Options**: Previene clickjacking
- **X-XSS-Protection**: Protección básica contra XSS
- **Referrer Policy**: Controla información del referrer
- **Hide Powered-By**: Oculta el header X-Powered-By

### Configuración de Helmet
```typescript
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

## Sistema de Encriptación

### Algoritmo AES-256-CBC

El servicio utiliza encriptación AES-256-CBC compatible con Python para asegurar la comunicación de archivos de configuración.

#### Características
- **Algoritmo**: AES-256-CBC
- **Compatibilidad**: Python y Node.js
- **Codificación**: Base64 para transmisión
- **Clave**: Configurable mediante variable de entorno

#### Funciones de Encriptación
```typescript
// Encriptar texto
const encrypted = encrypt(text, encryptionKey);

// Desencriptar texto
const decrypted = decrypt(encryptedText, encryptionKey);
```

#### Ejemplo de Uso
```typescript
import { encrypt, decrypt } from './utils/Encrypt';

// Encriptar nombre de archivo
const filename = "config.txt";
const encryptedFilename = encrypt(filename, process.env.ENCRYPTION_KEY);

// Desencriptar nombre de archivo
const decryptedFilename = decrypt(encryptedFilename, process.env.ENCRYPTION_KEY);
```

## Gestión de Archivos

### Estructura de Almacenamiento

```
config-service/
└── storage/
    ├── show_running.txt          # Archivo de configuración de ejemplo
    ├── router_config.txt         # Configuración de router
    ├── switch_config.txt         # Configuración de switch
    └── firewall_config.txt       # Configuración de firewall
```

### Operaciones de Archivo

#### Lectura de Archivos
```typescript
// Leer archivo de configuración
const content = await fileReaderService.readFile(filename);

// Validar existencia de archivo
const exists = await fileReaderService.fileExists(filename);
```

#### Validación de Archivos
- **Existencia**: Verificar que el archivo existe
- **Permisos**: Verificar permisos de lectura
- **Tamaño**: Validar tamaño máximo permitido
- **Formato**: Verificar formato de archivo

## Manejo de Errores

### Sistema de Excepciones

El servicio implementa un sistema de excepciones personalizado con códigos de error específicos.

#### Tipos de Excepciones

- **BaseException**: Excepción base para todas las excepciones
- **InvalidDataException**: Datos de entrada inválidos
- **NotFoundException**: Recurso no encontrado
- **SystemException**: Error interno del sistema
- **GetContentException**: Error al obtener contenido de archivo

#### Códigos de Error

| Código | Descripción | HTTP Status |
|--------|-------------|-------------|
| `AUTH_TOKEN_REQUIRED` | Token de autorización requerido | 401 |
| `AUTH_TOKEN_INVALID` | Token de autorización inválido | 401 |
| `FILE_NOT_FOUND` | Archivo no encontrado | 404 |
| `INVALID_FILENAME` | Nombre de archivo inválido | 400 |
| `ENCRYPTION_ERROR` | Error de encriptación/desencriptación | 500 |
| `READ_FILE_ERROR` | Error al leer archivo | 500 |

#### Ejemplo de Manejo de Errores
```typescript
try {
  const content = await fileReaderService.readFile(filename);
  return new SuccessResponse(content);
} catch (error) {
  if (error instanceof NotFoundException) {
    throw new GetContentException('Archivo no encontrado');
  }
  throw new SystemException('Error interno del sistema');
}
```

## Logging

### Sistema de Logging Estructurado

El servicio utiliza un sistema de logging estructurado que registra:
- Requests HTTP
- Errores de aplicación
- Información de auditoría
- Métricas de rendimiento

#### Niveles de Log
- **INFO**: Información general
- **ERROR**: Errores de aplicación
- **WARN**: Advertencias
- **DEBUG**: Información detallada

#### Formato de Logs
```json
{
  "level": "INFO",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "config-service",
  "message": "Archivo leído exitosamente",
  "filename": "config.txt",
  "user": "admin",
  "ip": "192.168.1.100"
}
```

## Testing

### Configuración de Tests

El servicio incluye una suite completa de tests unitarios con Jest.

#### Ejecutar Tests
```bash
# Todos los tests
npm test

# Tests en modo watch
npm run test:watch

# Tests con coverage
npm run test:coverage

# Tests específicos
npm test -- --testNamePattern="GetConfigCommandHandler"
```

#### Cobertura de Tests
```bash
# Generar reporte de cobertura
npm run test:coverage

# Ver reporte en navegador
open coverage/lcov-report/index.html
```

#### Estructura de Tests
```
test/
└── unit/
    ├── adapters/
    │   ├── repository/
    │   └── service/
    │       ├── AuthService.test.ts
    │       └── FileReaderService.test.ts
    ├── domain/
    │   ├── command_handlers/
    │   │   └── GetConfigCommandHandler.test.ts
    │   ├── commands/
    │   │   └── GetConfigCommand.test.ts
    │   ├── exceptions/
    │   │   ├── constants/
    │   │   │   ├── ErrorMessages.test.ts
    │   │   │   └── InputMessageException.test.ts
    │   │   └── core/
    │   │       ├── BaseException.test.ts
    │   │       ├── InvalidDataException.test.ts
    │   │       ├── NotFoundException.test.ts
    │   │       └── SystemException.test.ts
    │   └── model/
    │       ├── Input.test.ts
    │       ├── interfaces/
    │       │   ├── IOutput.test.ts
    │       │   └── IResponse.test.ts
    │       └── Output.test.ts
    ├── entrypoints/
    │   └── api/
    │       ├── GetConfigController.test.ts
    │       └── middlewares/
    │           ├── authMiddleware.test.ts
    │           ├── catchError.test.ts
    │           ├── extractFilename.test.ts
    │           └── initLogger.test.ts
    ├── infra/
    │   └── Logger.test.ts
    └── utils/
        ├── Encrypt.test.ts
        ├── ErrorExtractor.test.ts
        └── FileReaderUtil.test.ts
```

## Desarrollo

### Scripts Disponibles

#### Desarrollo
```bash
# Ejecutar en modo desarrollo
npm run dev

# Ejecutar con hot reload
npm run dev:watch
```

#### Producción
```bash
# Construir para producción
npm run build

# Ejecutar en producción
npm start
```

#### Testing
```bash
# Ejecutar tests
npm test

# Ejecutar tests en modo watch
npm run test:watch

# Generar reporte de cobertura
npm run test:coverage
```

#### Linting
```bash
# Verificar código
npm run lint

# Corregir errores automáticamente
npm run lint:fix

# Verificar tipos TypeScript
npm run type-check
```

#### Utilidades de Encriptación
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

### Configuración de TypeScript

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "test"]
}
```

### Configuración de Webpack

```javascript
const path = require('path');

module.exports = {
  entry: './src/index.ts',
  target: 'node',
  mode: 'production',
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
  },
};
```

## Despliegue

### Docker

#### Construir Imagen
```bash
docker build -t config-service .
```

#### Ejecutar Contenedor
```bash
docker run -p 8000:8000 \
  -e AUTH_SERVICE_URL=http://auth-service:8080 \
  -e ENCRYPTION_KEY=mi_contraseña_secreta_super_segura_2024 \
  config-service
```

### Docker Compose

#### Iniciar Servicios
```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f config-service

# Detener servicios
docker-compose down
```

### AWS Lambda

El servicio mantiene compatibilidad con AWS Lambda a través de la función `handler` exportada.

```typescript
// Función Lambda handler
export const handler = async (event: any, context: any) => {
  // Lógica del handler
  return {
    statusCode: 200,
    body: JSON.stringify({ message: 'Config service running' })
  };
};
```

## Integración con Otros Servicios

### Flujo de Integración

1. **Analysis Service** solicita archivo de configuración
2. **Config Service** valida token JWT con **Auth Service**
3. **Config Service** lee y desencripta archivo
4. **Config Service** retorna contenido al **Analysis Service**

### Ejemplo de Integración
```bash
# 1. Obtener token del auth-service
curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Password123!"}'

# 2. Usar token para obtener configuración
curl -X GET "http://localhost:8000/config/U2FsdGVkX1..." \
  -H "Authorization: Bearer <token_jwt>"
```

## Monitoreo y Métricas

### Health Checks

#### Endpoint de Salud
```bash
curl http://localhost:8000/health
```

#### Respuesta de Salud
```json
{
  "status": "OK",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "config-service",
  "version": "1.0.0",
  "uptime": "3600",
  "memory": {
    "used": "45.2 MB",
    "total": "512 MB"
  }
}
```

### Métricas de Rendimiento

- **Tiempo de respuesta** de endpoints
- **Tasa de errores** por tipo
- **Uso de memoria** y CPU
- **Conexiones activas**
- **Archivos leídos** por minuto

## Troubleshooting

### Problemas Comunes

#### Error de Conexión al Auth Service
```
Error: connect ECONNREFUSED auth-service:8080
```
**Solución:** Verificar que el auth-service esté ejecutándose y accesible.

#### Error de Encriptación
```
Error: Invalid key length
```
**Solución:** Verificar que `ENCRYPTION_KEY` tenga la longitud correcta.

#### Error de Archivo No Encontrado
```
Error: ENOENT: no such file or directory
```
**Solución:** Verificar que el archivo existe en el directorio `storage/`.

#### Error de Token Inválido
```
Error: AUTH_TOKEN_INVALID
```
**Solución:** Obtener un nuevo token del auth-service.

### Logs de Debug
```bash
# Habilitar logs de debug
export NODE_ENV=development
export DEBUG=config-service:*
npm run dev
```

## Documentación Adicional

Para información más detallada, consulta:
- 📋 **Colección de Postman** - `config-service-postman-collection.json`
- 🔄 **Diagrama de Flujo** - `diagrama-flujo.md`
- ⏱️ **Diagrama de Secuencia** - `diagrama-secuencia.md`
- 🗄️ **Diagrama de Base de Datos** - `diagrama-base-datos.md` 