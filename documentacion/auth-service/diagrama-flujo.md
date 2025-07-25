# Diagrama de Flujo - Auth Service

## 1. Flujo Principal de Autenticación (Login)

```mermaid
flowchart TD
    A[Cliente envía POST /login] --> B{Validar formato JSON}
    B -->|Inválido| C[Retornar Error 400 - JSON inválido]
    B -->|Válido| D{Validar campos requeridos}
    D -->|Faltantes| E[Retornar Error 400 - Campos requeridos]
    D -->|Completos| F{Validar username}
    F -->|Inválido| G[Retornar Error 400 - Username inválido]
    F -->|Válido| H{Validar password}
    H -->|Inválido| I[Retornar Error 400 - Password inválido]
    H -->|Válido| J[Buscar usuario en MongoDB]
    J --> K{Usuario existe?}
    K -->|No| L[Retornar Error 401 - Credenciales inválidas]
    K -->|Sí| M{Verificar password con bcrypt}
    M -->|Incorrecto| L
    M -->|Correcto| N[Generar token JWT con RSA]
    N --> O[Retornar 200 - Token + Usuario]
```

## 2. Flujo de Validación de Token

```mermaid
flowchart TD
    A[Cliente envía POST /validate] --> B{Validar formato JSON}
    B -->|Inválido| C[Retornar Error 400 - JSON inválido]
    B -->|Válido| D{Validar campo token}
    D -->|Faltante| E[Retornar Error 400 - Token requerido]
    D -->|Presente| F{Validar formato JWT}
    F -->|Inválido| G[Retornar 200 - valid: false, error: formato]
    F -->|Válido| H[Verificar firma con llave pública RSA]
    H -->|Firma inválida| I[Retornar 200 - valid: false, error: firma]
    H -->|Firma válida| J{Token expirado?}
    J -->|Sí| K[Retornar 200 - valid: false, error: expirado]
    J -->|No| L[Extraer claims del token]
    L --> M[Retornar 200 - valid: true, user: username]
```

## 3. Flujo de Obtención de Llave Pública

```mermaid
flowchart TD
    A[Cliente envía GET /public-key] --> B[Verificar existencia de llave pública]
    B --> C{¿Existe public.pem?}
    C -->|No| D[Generar par de llaves RSA 2048 bits]
    D --> E[Guardar private.pem]
    D --> F[Guardar public.pem]
    C -->|Sí| G[Leer archivo public.pem]
    F --> G
    G --> H[Retornar 200 - Llave pública en formato PEM]
```

## 4. Flujo de Health Check

```mermaid
flowchart TD
    A[Cliente envía GET /health] --> B[Verificar conexión a MongoDB]
    B --> C{¿MongoDB conectado?}
    C -->|No| D[Retornar Error 503 - Servicio no disponible]
    C -->|Sí| E[Verificar existencia de usuario por defecto]
    E --> F{¿Existe usuario admin?}
    F -->|No| G[Crear usuario admin con password encriptado]
    F -->|Sí| H[Retornar 200 - Status healthy]
    G --> H
```

## 5. Flujo de Inicialización del Servicio

```mermaid
flowchart TD
    A[Iniciar aplicación] --> B[Cargar variables de entorno]
    B --> C[Inicializar logger]
    C --> D[Configurar CORS middleware]
    D --> E[Configurar logging middleware]
    E --> F[Configurar validation middleware]
    F --> G[Inicializar contenedor de dependencias]
    G --> H[Configurar repositorio MongoDB]
    H --> I[Configurar servicios de dominio]
    I --> J[Configurar casos de uso]
    J --> K[Configurar controladores]
    K --> L[Configurar rutas]
    L --> M[Verificar/generar llaves RSA]
    M --> N[Iniciar servidor HTTP]
    N --> O[Servicio listo en puerto 8080]
```

## 6. Flujo de Manejo de Errores

```mermaid
flowchart TD
    A[Request llega] --> B{¿Error de validación?}
    B -->|Sí| C[Retornar Error 400 con detalles]
    B -->|No| D{¿Error de autenticación?}
    D -->|Sí| E[Retornar Error 401]
    D -->|No| F{¿Error de base de datos?}
    F -->|Sí| G[Retornar Error 503]
    F -->|No| H{¿Error interno?}
    H -->|Sí| I[Log error y retornar Error 500]
    H -->|No| J[Procesar request normalmente]
```

## 7. Flujo de Validación de Datos

```mermaid
flowchart TD
    A[Datos de entrada] --> B{¿Username presente?}
    B -->|No| C[Error: Username requerido]
    B -->|Sí| D{¿Username con formato invalido?}
    D -->|No| E[Error: Credenciales inválidas]
    D -->|Sí| F{¿Username formato válido?}
    F -->|No| G[Error: Credenciales inválidas]
    F -->|Sí| H{¿Password presente?}
    H -->|No| I[Error: Password requerido]
    H -->|Sí| J{¿Password 8+ caracteres?}
    J -->|No| K[Error: Credenciales inválidas]
    J -->|Sí| L{¿Password tiene mayúscula?}
    L -->|No| M[Error: Credenciales inválidas]
    L -->|Sí| N{¿Password tiene minúscula?}
    N -->|No| O[Error: Credenciales inválidas]
    N -->|Sí| P{¿Password tiene número?}
    P -->|No| Q[Error: Credenciales inválidas]
    P -->|Sí| R{¿Password tiene especial?}
    R -->|No| S[Error: Credenciales inválidas]
    R -->|Sí| T[Datos válidos]
```

## 8. Flujo de Generación de Token JWT

```mermaid
flowchart TD
    A[Usuario autenticado] --> B[Crear claims del token]
    B --> C[Establecer issuer: auth-service]
    C --> D[Establecer subject: username]
    D --> E[Establecer issued at: now]
    E --> F[Establecer expiration: now + 24h]
    F --> G[Cargar llave privada RSA]
    G --> H[Firmar token con algoritmo RS256]
    H --> I[Codificar token en base64]
    I --> J[Retornar token JWT completo]
```

## 9. Flujo de Verificación de Password

```mermaid
flowchart TD
    A[Password recibido] --> B[Obtener hash almacenado]
    B --> C[Usar bcrypt.CompareHashAndPassword]
    C --> D{¿Password coincide?}
    D -->|Sí| E[Autenticación exitosa]
    D -->|No| F[Autenticación fallida]
```

## 10. Flujo de Creación de Usuario por Defecto

```mermaid
flowchart TD
    A[Health check ejecutado] --> B{¿Usuario admin existe?}
    B -->|Sí| C[Continuar normalmente]
    B -->|No| D[Crear password: Password123!]
    D --> E[Encriptar password con bcrypt]
    E --> F[Crear documento de usuario]
    F --> G[Guardar en colección users]
    G --> H[Log: Usuario admin creado]
    H --> C
```

## 11. Flujo de Middleware de CORS

```mermaid
flowchart TD
    A[Request llega] --> B{¿Es preflight OPTIONS?}
    B -->|Sí| C[Agregar headers CORS]
    C --> D[Retornar 200 OK]
    B -->|No| E[Agregar headers CORS]
    E --> F[Continuar al siguiente middleware]
```

## 12. Flujo de Middleware de Logging

```mermaid
flowchart TD
    A[Request llega] --> B[Log inicio de request]
    B --> C[Procesar request]
    C --> D[Log fin de request]
    D --> E[Log duración del request]
    E --> F[Log status code]
    F --> G[Log tamaño de respuesta]
```

## 13. Flujo de Middleware de Validación

```mermaid
flowchart TD
    A[Request llega] --> B{¿Endpoint requiere validación?}
    B -->|No| C[Continuar sin validación]
    B -->|Sí| D[Extraer datos del request]
    D --> E[Ejecutar validadores]
    E --> F{¿Datos válidos?}
    F -->|Sí| G[Continuar al controlador]
    F -->|No| H[Retornar error de validación]
```

## 14. Flujo de Integración con Otros Servicios

```mermaid
flowchart TD
    A[Servicio cliente] --> B[Obtener token via /login]
    B --> C[Almacenar token]
    C --> D[Incluir token en requests]
    D --> E[Servicio protegido recibe request]
    E --> F[Extraer token del header]
    F --> G[Validar token via /validate]
    G --> H{¿Token válido?}
    H -->|Sí| I[Procesar request]
    H -->|No| J[Retornar 401 Unauthorized]
```

## 15. Flujo de Recuperación de Errores

```mermaid
flowchart TD
    A[Error ocurre] --> B{¿Es error de red?}
    B -->|Sí| C[Reintentar conexión]
    C --> D{¿Reintento exitoso?}
    D -->|Sí| E[Continuar operación]
    D -->|No| F[Log error y fallar]
    B -->|No| G{¿Es error de validación?}
    G -->|Sí| H[Retornar error al cliente]
    G -->|No| I{¿Es error de base de datos?}
    I -->|Sí| J[Log error y retornar 503]
    I -->|No| K[Log error y retornar 500]
``` 