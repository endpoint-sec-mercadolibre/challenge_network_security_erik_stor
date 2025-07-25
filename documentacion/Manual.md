# Manual de Usuario - Sistema de Análisis de Seguridad de Red

## Descripción General

Este sistema está compuesto por tres microservicios que trabajan en conjunto para proporcionar análisis de seguridad de configuraciones de dispositivos de red:

1. **Auth Service** - Servicio de autenticación y autorización
2. **Config Service** - Servicio de gestión de archivos de configuración
3. **Analysis Service** - Servicio de análisis de seguridad

## Arquitectura del Sistema

```mermaid
graph TB
    Client[Cliente] --> Auth[Auth Service]
    Client --> Config[Config Service]
    Client --> Analysis[Analysis Service]
    
    Analysis --> Auth
    Analysis --> Config
    Config --> Auth
    
    Auth --> MongoDB[(MongoDB)]
    Analysis --> MongoDB
    
    subgraph "Docker Network"
        Auth
        Config
        Analysis
        MongoDB
    end
```

## Componentes del Sistema

### Auth Service (Puerto 8080)
- **Propósito**: Autenticación y autorización centralizada
- **Tecnología**: Go con Gin framework
- **Base de Datos**: MongoDB
- **Características**: JWT tokens, RSA keys, validación de usuarios

### Config Service (Puerto 8000)
- **Propósito**: Gestión segura de archivos de configuración
- **Tecnología**: Node.js con TypeScript
- **Almacenamiento**: Sistema de archivos con encriptación AES-256-CBC
- **Características**: Encriptación de archivos, arquitectura hexagonal

### Analysis Service (Puerto 8002)
- **Propósito**: Análisis de seguridad de configuraciones
- **Tecnología**: Python con FastAPI
- **Base de Datos**: MongoDB
- **Características**: Análisis de configuraciones, scoring de seguridad

## Instalación y Configuración

### Prerrequisitos

- **Docker**: Versión 20.10 o superior
- **Docker Compose**: Versión 2.0 o superior
- **Git**: Para clonar el repositorio
- **Mínimo 4GB RAM** disponible para los contenedores

### Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd challenge_network_security_erik_stor
   ```

2. **Configurar variables de entorno**:
   ```bash
   # Crear archivo .env en la raíz del proyecto
   cp env.example .env
   ```

3. **Editar variables de entorno**:
   ```bash
   # Variables principales
   ENCRYPTION_KEY=tu_clave_secreta_aqui
   MONGO_PORT=27017
   AUTH_SERVICE_PORT=8080
   CONFIG_SERVICE_PORT=8000
   ANALYSIS_SERVICE_PORT=8002
   DOCKER_NETWORK_SUBNET=172.25.0.0/16
   ```

4. **Levantar los servicios**:
   ```bash
   docker-compose up -d
   ```

5. **Verificar que todos los servicios estén funcionando**:
   ```bash
   docker-compose ps
   ```

## Uso del Sistema

### 1. Autenticación

#### Obtener Token de Acceso

```bash
curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Login exitoso",
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "admin",
    "username": "admin"
  }
}
```

#### Validar Token

```bash
curl -X POST http://localhost:8080/validate \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

### 2. Gestión de Configuraciones

#### Obtener Archivo de Configuración

```bash
curl -X GET "http://localhost:8000/config/:nombre_archivo_base64_encryptado_con_aes_256_cbc" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Respuesta**:
```json
{
  "message": "Archivo obtenido exitosamente",  
  "content": "! Cisco Router Configuration\nhostname Router1\n...",  
}
```

#### Verificar Estado del Config Service

```bash
curl -X GET http://localhost:8000/health
```

### 3. Análisis de Seguridad

#### Analizar Configuración

```bash
curl -X GET "http://localhost:8002/api/v1/analyze?filename=show_running.txt" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Análisis completado exitosamente",
  "data": {
    "filename": "show_running.txt",
    "encrypted_filename": "o7cpDpoWexPhI7sUZK0dg3cVRIfNlawrmqKfz2KTSKhdtOYJxm+GJwiUicEs6Nlf2RBxc8UIYKU/jPKj",
    "file_size": 1662,
    "analysis_date": "2025-07-25T14:09:36.227017",
    "file_type": "text/plain",
    "checksum": null,
    "metadata": {
      "analysis_date": "2025-07-25T14:09:36.128888",
      "security_level": "critical",
      "gemini_analysis": {
        "analysis_date": "2023-10-27 16:30:00",
        "safe": false,
        "problems": [
          {
            "problem": "Contraseñas débiles para el acceso al switch y usuarios.",
            "severity": "Crítica",
            "recommendation": "Cambiar inmediatamente todas las contraseñas por contraseñas fuertes y únicas, utilizando una longitud mínima de 16 caracteres, con mayúsculas, minúsculas, números y símbolos.  Implementar un sistema de gestión de contraseñas para evitar la reutilización de credenciales.  Considerar el uso de la autenticación multifactor (MFA) para mayor seguridad."
          },
          ...
        ]
      },
      "model_used": "gemini-1.5-flash",
      "tokens_used": "unknown"
    }
  }
}
```

#### Verificar Estado del Analysis Service

```bash
curl -X GET http://localhost:8002/health
```

## Flujo de Trabajo Completo

### Paso 1: Autenticación
```bash
# Obtener token con el usuario por defecto
TOKEN=$(curl -s -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Password123!"}' | \
  jq -r '.token')
```


### Paso 2: Realizar Análisis
```bash
# Analizar configuración
curl -X GET "http://localhost:8002/api/v1/analyze?filename=show_running.txt" \
  -H "Authorization: Bearer $TOKEN"
```

## Archivos de Configuración Disponibles

El sistema incluye el siguiente archivo de configuración de ejemplo:

- `show_running.txt` - Configuración de router Cisco

## Documentación de APIs

### Swagger UI

Cada servicio proporciona documentación interactiva:

- **Auth Service**: http://localhost:8080/swagger/index.html
- **Config Service**: http://localhost:8000/api-docs/
- **Analysis Service**: http://localhost:8002/docs

### Colecciones de Postman

Se incluyen colecciones de Postman para cada servicio:

- [Auth Service Collection](auth-service/auth-service-postman-collection.json)
- [Config Service Collection](config-service/config-service-postman-collection.json)
- [Analysis Service Collection](analysis-service/analysis-service-postman-collection.json)

## Monitoreo y Logs

### Verificar Estado de Servicios

```bash
# Estado general
docker-compose ps

# Logs en tiempo real
docker-compose logs -f

# Logs de servicio específico
docker-compose logs -f auth-service
docker-compose logs -f config-service
docker-compose logs -f analysis-service
```

Además también se incluye un archivo de logs por cada servicio donde se persisten para lecturas e inspecciones posteriores a un reinicio:

```bash

docker exec -it config-service-container cat ./config-service.log
docker exec -it auth-service-container cat ./logs/auth-service.log
docker exec -it analysis-service-container cat ./logs/analysis-service.log

```

### Endpoints de Health Check

```bash
# Verificar salud de todos los servicios
curl http://localhost:8080/health  # Auth Service
curl http://localhost:8000/health  # Config Service
curl http://localhost:8002/health  # Analysis Service
```

## Configuración de Red

### Red Docker

El sistema utiliza una red Docker personalizada:

```yaml
networks:
  custom_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16
```

### Asignación de IPs

- **MongoDB**: 172.25.0.2
- **Config Service**: 172.25.0.3
- **Auth Service**: 172.25.0.4
- **Analysis Service**: 172.25.0.5

## Seguridad

### Autenticación JWT

- **Algoritmo**: RS256 (RSA + SHA256)
- **Expiración**: Configurable
- **Validación**: Automática en todos los endpoints protegidos

### Encriptación

- **Algoritmo**: AES-256-CBC
- **Aplicación**: Nombres de archivos y contenido
- **Compatibilidad**: Entre todos los servicios

### Headers de Seguridad

El Config Service implementa headers de seguridad adicionales:
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security

## Troubleshooting

### Problemas Comunes

#### 1. Servicios No Inician

```bash
# Verificar logs
docker-compose logs

# Reiniciar servicios
docker-compose restart

# Reconstruir imágenes
docker-compose build --no-cache
```

#### 2. Error de Conexión a MongoDB

```bash
# Verificar que MongoDB esté ejecutándose
docker-compose ps mongodb_meli_db

# Verificar logs de MongoDB
docker-compose logs mongodb_meli_db
```

#### 3. Error de Autenticación

```bash
# Verificar que el Auth Service esté funcionando
curl http://localhost:8080/health

# Verificar formato del token
echo $TOKEN | cut -d'.' -f1 | base64 -d
```

#### 4. Error de Encriptación

```bash
# Verificar variable ENCRYPTION_KEY
echo $ENCRYPTION_KEY

# Verificar que todos los servicios usen la misma clave
docker-compose exec config-service env | grep ENCRYPTION_KEY
docker-compose exec analysis-service env | grep ENCRYPTION_KEY
```

### Comandos Útiles

```bash
# Limpiar contenedores y volúmenes
docker-compose down -v

# Ver uso de recursos
docker stats

# Acceder a MongoDB
docker-compose exec mongodb_meli_db mongosh

# Ver logs de un servicio específico
docker-compose logs -f --tail=100 auth-service
```

## Desarrollo

### Estructura del Proyecto

```
challenge_network_security_erik_stor/
├── auth-service/          # Servicio de autenticación
├── config-service/        # Servicio de configuración
├── analysis-service/      # Servicio de análisis
├── config/               # Configuración de MongoDB
├── documentacion/        # Documentación completa
├── docker-compose.yml    # Orquestación de servicios
└── README.md            # Este archivo
```

### Modo Desarrollo

```bash
# Ejecutar en modo desarrollo con logs
docker-compose up

# Ejecutar servicios específicos
docker-compose up auth-service config-service

# Ejecutar con rebuild
docker-compose up --build
```


## Escalabilidad

### Configuración de Recursos

```yaml
# En docker-compose.yml
services:
  auth-service:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

### Monitoreo de Rendimiento

```bash
# Ver estadísticas de contenedores
docker stats

# Ver uso de red
docker network ls
docker network inspect challenge_network_security_erik_stor_custom_net
```

## Backup y Recuperación

### Backup de Base de Datos

```bash
# Backup de MongoDB
docker-compose exec mongodb_meli_db mongodump --out /backup

# Restaurar backup
docker-compose exec mongodb_meli_db mongorestore /backup
```

### Logs y Debugging

- **Logs estructurados**: Todos los servicios implementan logging JSON
- **Niveles de log**: DEBUG, INFO, WARN, ERROR, SUCCESS
- **Rotación de logs**: Automática para evitar llenado de disco

