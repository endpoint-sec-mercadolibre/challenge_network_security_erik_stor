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

3. **Editar variables de entorno**: Las variables ya se encuentran dentro del archivo ".env" en la raíz de este proyecto, sin embargo, pueden ser editadas.
   ```bash
      # ===========================================
      # CONFIGURACIÓN DE SEGURIDAD Y VARIABLES DE ENTORNO
      # ===========================================

      # Configuración de la red Docker
      DOCKER_NETWORK_SUBNET=192.25.0.0/16
      DOCKER_NETWORK_NAME=custom_net

      # ===========================================
      # CONFIGURACIÓN DE MONGODB
      # ===========================================
      MONGO_ROOT_USERNAME=admin
      MONGO_ROOT_PASSWORD=password
      MONGO_DATABASE=analysis_service
      MONGO_AUTH_DATABASE=admin
      MONGO_PORT=27017

      # ===========================================
      # CONFIGURACIÓN DE SERVICIOS
      # ===========================================

      # Config Service
      CONFIG_SERVICE_PORT=8000
      CONFIG_SERVICE_NODE_ENV=production
      CONFIG_SERVICE_FILE_ENCODING=utf8
      CONFIG_SERVICE_ENCRYPTION_KEY=mi_contraseña_secreta_super_segura_2024

      # Auth Service
      AUTH_SERVICE_PORT=8080
      AUTH_SERVICE_DATABASE=auth_service

      # Analysis Service
      ANALYSIS_SERVICE_PORT=8002
      ANALYSIS_SERVICE_LOG_LEVEL=INFO
      ANALYSIS_SERVICE_ENCRYPTION_KEY=mi_contraseña_secreta_super_segura_2024
      ANALYSIS_SERVICE_GEMINI_API_KEY=AIzaSyBw1lahxUngAHg8jHn2XvfHE-d9JUpnAp4

      # ===========================================
      # URLs DE COMUNICACIÓN INTERNA
      # ===========================================
      INTERNAL_AUTH_SERVICE_URL=http://auth-service:8080
      INTERNAL_CONFIG_SERVICE_URL=http://config-service:8000

      # ===========================================
      # CONFIGURACIÓN DE SEGURIDAD ADICIONAL
      # ===========================================
      # Tiempo de espera para health checks (segundos)
      HEALTH_CHECK_INTERVAL=30
      HEALTH_CHECK_TIMEOUT=10
      HEALTH_CHECK_RETRIES=3
      HEALTH_CHECK_START_PERIOD=40

      # Configuración de reinicio de contenedores
      RESTART_POLICY=unless-stopped 
   ```

4. **Levantar los servicios**:
   ```bash
   docker-compose up -d
   ```

5. **Verificar que todos los servicios estén funcionando**:
   ```bash
   docker-compose ps
   ```

6. **Verificar si el usuario semilla fue registrado con éxito**

Usando el siguiente comando podras acceder a la base datos de usuarios donde estara nuestro usuario "semilla".

```bash
  docker exec -it mongodb_meli_db mongosh auth_service --eval "db.users.find().pretty()"
```

Deberias encontrar un registro como el siguiente:

```bash
  [
    {
      _id: ObjectId('688395db4765510467302dec'),
      username: 'admin',
      password: '$2a$12$3kRgh0H6gNUmYtN3u.RcNODNR4e6H/ntPRoe6ef2OZpHaW2J54CIm',
      created_at: ISODate('2025-07-25T14:34:03.619Z'),
      updated_at: ISODate('2025-07-25T14:34:03.619Z')
    }
  ]
```

## Flujo de Trabajo Completo

### Paso 1: Obtener el token de autenticación

Puedes copiar este curl y usarlo en tu herramienta de peticiones Http como Postman o Insomnia:

```bash
# Obtener token con el usuario por defecto
curl -s -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Password123!"}' | \
  jq -r '.token'
```

También te adjunto la [colección de Postman del servicio de autenticación](./auth-service/auth-service-postman-collection.json) para que la uses importandola en la herramienta.

El resultado de este pequeño servicio nos permitira acceder al siguiente paso.

**Respuesta**

```json
{
    "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9....",
    "user": "admin"
}
```

### Paso 2: Realizar Análisis

En el cuerpo de la respuesta del paso anterior, debemos encontrar la clave "token", el valor de esta lo utilizaremos para poder acceder al servicio de análisis, continuando con la dinámica puedes hacer uso de este curl en tu herramienta para obtener el analisis de la configuración o 
puedes utilizar la [colección de Postman del servicio de análisis](./analysis-service/analysis-service-postman-collection.json). *Recuerda utilizar en token generado en el paso anterior*

```bash
# Analizar configuración
curl -X GET "http://localhost:8002/api/v1/analyze?filename=show_running.txt" \
  -H "Authorization: Bearer $TOKEN"
```


### Paso 3: Verificar que los registros del análisis son guardados en la base de datos

Para verificar que los registros son almacenados correctamente en la base de datos mongoDB, debes ejecutar el siguiente comando:

```bash
  docker exec -it mongodb_meli_db mongosh analysis_service --eval "db.analysis_records.find().pretty()"
```

## Servicios del Sistema

En esta seccion te indico que servicios existen en el sistema. Todos los servicios cuentan con un verificador de salud que nos muestra si el api esta trabajando y disponible para su uso. 

### 1. Autenticación

Este servicio es el encargado de generar y validar nuestro Json Web Token (JWT) utilizando una llave publica y llave privada en el proceso.

#### Obtener Token de Acceso

```bash
curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Password123!"
  }'
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Login exitoso",
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": "string"
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

**Respuesta**

```json
  {
    "valid": true,
    "user": "admin"
  }
```

#### Verificar Estado del Auth Service

```bash
curl -X GET http://localhost:8080/health
```

**Respuesta**
```json
{
  "message": "Servicio funcionando correctamente y semilla ejecutada",
  "service": "auth-service",
  "status": "ok"
}

```

### 2. Gestión de Configuraciones

Este servicio es el encargado de leer y extraer el contenido del archivo que solicitemos.
*Debido a la configuración de docker (que se encuentra en el archivo docker-compose.yml) el servicio de configuración no esta expuesto por defecto, para hacer uso de este servicio utilizando algun agente externo al servicio de análisis deberás habilitar el puerto de entrada*.

#### Obtener Archivo de Configuración

```bash
curl -X GET "http://localhost:8000/config/:nombre_archivo_base64_encryptado_con_aes_256_cbc" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Respuesta**:
```json
{
  "message": "Archivo obtenido exitosamente",  
  "content": "contenido del archivo en base64 y encriptado con aes_256_cbc...",  
}
```

#### Verificar Estado del Config Service

```bash
curl -X GET http://localhost:8000/health
```

**Respuesta**
```json
  { 
    "status": "OK",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "service": "config-service"
  }
```


### 3. Análisis de Seguridad

Este servicio es el encargado de generar un análisis utilizando Gemini para entregar un reporte de las fallas de seguridad o en caso 
de que el parametro de la intelegencia artificial este apagado retornara el contenido del archivo

#### Analizar Configuración

```bash
curl -X GET "http://localhost:8002/api/v1/analyze?filename=show_running.txt&enable_ia=true" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Respuesta con el parametro enable_ia con el valor true**:
```json
{
  "success": true,
  "message": "Análisis completado exitosamente",
  "data": {
    "content": {
      "security_level": "critical",
      "safe": false,
      "problems": [
        {
          "problem": "Contraseñas débiles para el acceso al switch y usuarios.",
          "severity": "Crítica",
          "recommendation": "Cambiar inmediatamente todas las contraseñas por contraseñas fuertes y únicas, utilizando una longitud mínima de 16 caracteres, con mayúsculas, minúsculas, números y símbolos.  Implementar un sistema de gestión de contraseñas para evitar la reutilización de credenciales.  Considerar el uso de la autenticación multifactor (MFA) para mayor seguridad."
        }
      ]
    }
  }
}
```

**Respuesta con el parametro enable_ia con el valor true**:
```json
{
  "success": true,
  "message": "Análisis completado exitosamente",
  "data": {
    "content": "contenido del archivo..."
  }
}
```

#### Verificar Estado del Analysis Service

```bash
curl -X GET http://localhost:8002/health
```


**Respuesta**
```json
{
  "status": "healthy",
  "service": "analysis-service",
  "version": "1.0.0",
  "timestamp": "2025-07-25 19:08:40"
}
```


## Archivos de Configuración Disponibles

El sistema incluye el siguiente archivo de configuración de ejemplo:

- `show_running.txt` - Configuración de router Cisco

## Documentación de APIs

### Swagger UI

Cada servicio proporciona documentación interactiva:

- **Auth Service**: http://localhost:8080/swagger/index.html
- **Analysis Service**: http://localhost:8002/docs

### Colecciones de Postman

Se incluyen colecciones de Postman para cada servicio:

- [Auth Service Collection](auth-service/auth-service-postman-collection.json)
- [Analysis Service Collection](analysis-service/analysis-service-postman-collection.json)

**Debido a la configuración de docker nuestro servicio de configuración no esta disponible por defecto y deberás habilitar el puerto de entrada en el archivo docker compose**

- [Config Service Collection](config-service/config-service-postman-collection.json)
  
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

