# Diagramas de Secuencia - Analysis Service

## 1. Secuencia de Análisis Exitoso

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant AS as Analysis Service
    participant Auth as Auth Service
    participant Config as Config Service
    participant DB as MongoDB

    Client->>AS: GET /api/v1/analyze?filename=show_running.txt
    Note over Client,AS: Authorization: Bearer <token>
    
    AS->>AS: Validar token JWT
    AS->>Auth: POST /validate {token}
    Auth-->>AS: {valid: true, user: admin}
    
    AS->>AS: Encriptar nombre de archivo
    AS->>Config: GET /config/{encrypted_filename}
    Note over AS,Config: Authorization: Bearer <token>
    
    Config->>Config: Desencriptar nombre
    Config->>Config: Buscar archivo
    Config-->>AS: {content: "config content", encrypted: true}
    
    AS->>AS: Desencriptar contenido
    AS->>AS: Analizar configuración
    AS->>AS: Calcular score de seguridad
    AS->>AS: Identificar vulnerabilidades
    AS->>AS: Generar recomendaciones
    
    AS->>DB: Insertar análisis
    DB-->>AS: {_id: "analysis_id"}
    
    AS-->>Client: {success: true, data: {...}}
```

## 2. Secuencia de Error de Autenticación

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant AS as Analysis Service
    participant Auth as Auth Service

    Client->>AS: GET /api/v1/analyze?filename=show_running.txt
    Note over Client,AS: Sin Authorization header
    
    AS->>AS: Extraer token del header
    AS->>AS: Token no encontrado
    AS-->>Client: {error: "Token de autenticación requerido", code: 401}
```

## 3. Secuencia de Token Inválido

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant AS as Analysis Service
    participant Auth as Auth Service

    Client->>AS: GET /api/v1/analyze?filename=show_running.txt
    Note over Client,AS: Authorization: Bearer invalid_token
    
    AS->>AS: Extraer token del header
    AS->>Auth: POST /validate {token: "invalid_token"}
    Auth-->>AS: {valid: false, error: "Token inválido"}
    
    AS-->>Client: {error: "Token de autenticación inválido", code: 401}
```

## 4. Secuencia de Archivo No Encontrado

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant AS as Analysis Service
    participant Auth as Auth Service
    participant Config as Config Service

    Client->>AS: GET /api/v1/analyze?filename=nonexistent.txt
    Note over Client,AS: Authorization: Bearer <token>
    
    AS->>Auth: POST /validate {token}
    Auth-->>AS: {valid: true, user: admin}
    
    AS->>AS: Encriptar nombre de archivo
    AS->>Config: GET /config/{encrypted_filename}
    Note over AS,Config: Authorization: Bearer <token>
    
    Config->>Config: Desencriptar nombre
    Config->>Config: Buscar archivo
    Config-->>AS: {error: "Archivo no encontrado", code: 404}
    
    AS-->>Client: {error: "Archivo no encontrado", code: 404}
```

## 5. Secuencia de Health Check

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant AS as Analysis Service
    participant Auth as Auth Service
    participant Config as Config Service
    participant DB as MongoDB

    Client->>AS: GET /health
    
    AS->>Auth: GET /health
    Auth-->>AS: {status: "healthy"}
    
    AS->>Config: GET /health
    Config-->>AS: {status: "healthy"}
    
    AS->>DB: Ping connection
    DB-->>AS: {status: "connected"}
    
    AS-->>Client: {status: "healthy", dependencies: {...}}
```

## 6. Secuencia de Inicialización del Servicio

```mermaid
sequenceDiagram
    participant App as Application
    participant Env as Environment
    participant Logger as Logger Service
    participant DB as MongoDB
    participant FastAPI as FastAPI App

    App->>Env: Cargar variables de entorno
    Env-->>App: Configuración cargada
    
    App->>Logger: Inicializar logger
    Logger-->>App: Logger configurado
    
    App->>DB: Conectar a MongoDB
    DB-->>App: Conexión establecida
    
    App->>FastAPI: Configurar aplicación
    FastAPI->>FastAPI: Configurar middleware
    FastAPI->>FastAPI: Configurar CORS
    FastAPI->>FastAPI: Configurar Swagger
    FastAPI->>FastAPI: Registrar endpoints
    FastAPI-->>App: Aplicación configurada
    
    App->>App: Iniciar servidor
    App-->>App: Servicio listo en puerto 8002
```

## 7. Secuencia de Error de Conexión a Config Service

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant AS as Analysis Service
    participant Auth as Auth Service
    participant Config as Config Service

    Client->>AS: GET /api/v1/analyze?filename=show_running.txt
    Note over Client,AS: Authorization: Bearer <token>
    
    AS->>Auth: POST /validate {token}
    Auth-->>AS: {valid: true, user: admin}
    
    AS->>AS: Encriptar nombre de archivo
    AS->>Config: GET /config/{encrypted_filename}
    Note over AS,Config: Config Service no disponible
    
    Config-->>AS: Connection timeout
    
    AS->>AS: Log error de conexión
    AS-->>Client: {error: "Error interno del servidor", code: 500}
```

## 8. Secuencia de Error de Base de Datos

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant AS as Analysis Service
    participant Auth as Auth Service
    participant Config as Config Service
    participant DB as MongoDB

    Client->>AS: GET /api/v1/analyze?filename=show_running.txt
    Note over Client,AS: Authorization: Bearer <token>
    
    AS->>Auth: POST /validate {token}
    Auth-->>AS: {valid: true, user: admin}
    
    AS->>Config: GET /config/{encrypted_filename}
    Config-->>AS: {content: "config content"}
    
    AS->>AS: Analizar configuración
    AS->>DB: Insertar análisis
    Note over AS,DB: MongoDB no disponible
    
    DB-->>AS: Connection error
    
    AS->>AS: Log error de base de datos
    AS-->>Client: {error: "Error interno del servidor", code: 500}
```

## 9. Secuencia de Validación de Parámetros

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant AS as Analysis Service

    Client->>AS: GET /api/v1/analyze
    Note over Client,AS: Sin parámetro filename
    
    AS->>AS: Validar parámetros
    AS->>AS: Filename requerido no presente
    AS-->>Client: {error: "Nombre de archivo requerido", code: 400}
```

## 10. Secuencia de Análisis de Configuración de Router

```mermaid
sequenceDiagram
    participant AS as Analysis Service
    participant Analyzer as Config Analyzer
    participant Security as Security Engine
    participant Score as Score Calculator

    AS->>Analyzer: Analizar configuración de router
    Analyzer->>Analyzer: Detectar comandos de router
    Analyzer->>Analyzer: Extraer configuraciones de seguridad
    Analyzer-->>AS: Configuraciones extraídas
    
    AS->>Security: Verificar configuraciones de seguridad
    Security->>Security: Verificar AAA
    Security->>Security: Verificar logging
    Security->>Security: Verificar SNMP
    Security->>Security: Verificar políticas de acceso
    Security-->>AS: Vulnerabilidades identificadas
    
    AS->>Score: Calcular score de seguridad
    Score->>Score: Aplicar métricas
    Score->>Score: Normalizar score
    Score-->>AS: Score calculado
    
    AS->>AS: Generar recomendaciones
    AS->>AS: Crear reporte final
```

## 11. Secuencia de Middleware de Autenticación

```mermaid
sequenceDiagram
    participant Request as HTTP Request
    participant Middleware as Auth Middleware
    participant Auth as Auth Service
    participant Endpoint as Protected Endpoint

    Request->>Middleware: Request con Authorization header
    
    Middleware->>Middleware: Extraer token
    Middleware->>Middleware: Verificar formato Bearer
    
    Middleware->>Auth: Validar token
    Auth-->>Middleware: {valid: true, user: admin}
    
    Middleware->>Middleware: Agregar user info al request
    Middleware->>Endpoint: Pasar request al endpoint
    
    Endpoint->>Endpoint: Procesar request
    Endpoint-->>Request: Response
```

## 12. Secuencia de Logging Estructurado

```mermaid
sequenceDiagram
    participant Event as Event
    participant Logger as Logger Service
    participant File as Log File
    participant Console as Console

    Event->>Logger: Log event con nivel y mensaje
    
    Logger->>Logger: Crear timestamp
    Logger->>Logger: Agregar contexto
    Logger->>Logger: Formatear como JSON
    
    Logger->>File: Escribir log a archivo
    File-->>Logger: Confirmación
    
    Logger->>Console: Mostrar log en consola
    Console-->>Logger: Confirmación
    
    Logger-->>Event: Log completado
```

## 13. Secuencia de Integración con Analysis Service

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant AS as Analysis Service
    participant Config as Config Service
    participant Auth as Auth Service

    Note over Client,Auth: Flujo completo de análisis
    
    Client->>AS: Solicitar análisis
    AS->>Auth: Validar autenticación
    Auth-->>AS: Usuario autenticado
    
    AS->>Config: Solicitar archivo
    Config-->>AS: Contenido del archivo
    
    AS->>AS: Procesar análisis
    AS->>AS: Generar reporte
    AS-->>Client: Resultado del análisis
```

## 14. Secuencia de Manejo de Errores

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant AS as Analysis Service
    participant Logger as Logger Service

    Client->>AS: Request que genera error
    
    AS->>AS: Capturar excepción
    AS->>Logger: Log error con contexto
    Logger-->>AS: Error registrado
    
    AS->>AS: Determinar tipo de error
    AS->>AS: Formatear respuesta de error
    AS-->>Client: Respuesta de error apropiada
``` 