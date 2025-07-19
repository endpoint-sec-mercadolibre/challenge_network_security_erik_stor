# Config Service

Microservicio de lectura de configuraciones implementando arquitectura hexagonal con Express y políticas de seguridad.

## Características

- ✅ Arquitectura hexagonal (Clean Architecture)
- ✅ Express.js como servidor web
- 🔒 Helmet para políticas de seguridad
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

### Recharge
```
POST /recharge
```

**Body:** JSON con los datos de recarga según la especificación del dominio.

## Variables de entorno

```bash
# Puerto del servidor
PORT=3000

# Entorno
NODE_ENV=development

# Tablas de DynamoDB
CUSTOMER_DYNAMO_TABLE=clients-table
TRANSACTIONS_TABLE_NAME=transactions-table
POCKET_TABLE_NAME=products-table
CARD_TOKENIZATION_TABLE_NAME=card-tokenization-table

# Servicios externos
CYBERSOURCE_SECRET_ARN=cybersource-secret-arn
```

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
