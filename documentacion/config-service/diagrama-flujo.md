# Diagrama de Flujo - Config Service

## 1. Flujo Principal de Lectura de Configuración

```mermaid
flowchart TD
    A[Cliente envía GET /config/{filename}] --> B{¿Header Authorization presente?}
    B -->|No| C[Retornar Error 401 - Token requerido]
    B -->|Sí| D[Extraer token del header]
    D --> E{¿Formato de token válido?}
    E -->|No| F[Retornar Error 401 - Formato inválido]
    E -->|Sí| G[Validar token con Auth Service]
    G --> H{¿Token válido?}
    H -->|No| I[Retornar Error 401 - Token inválido]
    H -->|Sí| J[Desencriptar nombre de archivo]
    J --> K{¿Desencriptación exitosa?}
    K -->|No| L[Retornar Error 400 - Nombre inválido]
    K -->|Sí| M[Verificar existencia de archivo]
    M --> N{¿Archivo existe?}
    N -->|No| O[Retornar Error 404 - Archivo no encontrado]
    N -->|Sí| P[Leer contenido del archivo]
    P --> Q{¿Lectura exitosa?}
    Q -->|No| R[Retornar Error 500 - Error de lectura]
    Q -->|Sí| S[Retornar 200 - Contenido del archivo]
```

## 2. Flujo de Health Check

```mermaid
flowchart TD
    A[Cliente envía GET /health] --> B[Verificar estado del servicio]
    B --> C[Obtener información del sistema]
    C --> D[Verificar conexión a Auth Service]
    D --> E{¿Auth Service disponible?}
    E -->|No| F[Log warning: Auth Service no disponible]
    E -->|Sí| G[Log info: Auth Service disponible]
    F --> H[Retornar 200 - Status OK]
    G --> H
```

## 3. Flujo de Middleware de Autenticación

```mermaid
flowchart TD
    A[Request llega] --> B{¿Endpoint requiere autenticación?}
    B -->|No| C[Continuar sin autenticación]
    B -->|Sí| D[Extraer token del header Authorization]
    D --> E{¿Header Authorization presente?}
    E -->|No| F[Retornar Error 401 - Token requerido]
    E -->|Sí| G{¿Formato Bearer válido?}
    G -->|No| H[Retornar Error 401 - Formato inválido]
    G -->|Sí| I[Extraer token JWT]
    I --> J{¿Token no está vacío?}
    J -->|No| K[Retornar Error 401 - Token vacío]
    J -->|Sí| L[Validar token con Auth Service]
    L --> M{¿Validación exitosa?}
    M -->|No| N[Retornar Error 401 - Token inválido]
    M -->|Sí| O[Agregar información de usuario al request]
    O --> P[Continuar al siguiente middleware]
```

## 4. Flujo de Desencriptación de Nombre de Archivo

```mermaid
flowchart TD
    A[Nombre encriptado recibido] --> B{¿String no está vacío?}
    B -->|No| C[Error: Nombre de archivo vacío]
    B -->|Sí| D[Decodificar base64]
    D --> E{¿Decodificación exitosa?}
    E -->|No| F[Error: Formato base64 inválido]
    E -->|Sí| G[Desencriptar con AES-256-CBC]
    G --> H{¿Desencriptación exitosa?}
    H -->|No| I[Error: Clave de encriptación inválida]
    H -->|Sí| J[Nombre de archivo desencriptado]
```

## 5. Flujo de Lectura de Archivo

```mermaid
flowchart TD
    A[Nombre de archivo desencriptado] --> B[Construir ruta completa]
    B --> C[Verificar permisos de lectura]
    C --> D{¿Permisos válidos?}
    D -->|No| E[Error: Permisos insuficientes]
    D -->|Sí| F[Verificar existencia de archivo]
    F --> G{¿Archivo existe?}
    G -->|No| H[Error: Archivo no encontrado]
    G -->|Sí| I[Leer contenido del archivo]
    I --> J{¿Lectura exitosa?}
    J -->|No| K[Error: Error de lectura]
    J -->|Sí| L[Validar codificación UTF-8]
    L --> M{¿Codificación válida?}
    M -->|No| N[Error: Codificación inválida]
    M -->|Sí| O[Contenido del archivo]
```

## 6. Flujo de Manejo de Errores

```mermaid
flowchart TD
    A[Error ocurre] --> B{¿Es error de autenticación?}
    B -->|Sí| C[Retornar Error 401 con detalles]
    B -->|No| D{¿Es error de validación?}
    D -->|Sí| E[Retornar Error 400 con detalles]
    D -->|No| F{¿Es error de archivo no encontrado?}
    F -->|Sí| G[Retornar Error 404]
    F -->|No| H{¿Es error de encriptación?}
    H -->|Sí| I[Retornar Error 500 - Error de encriptación]
    H -->|No| J{¿Es error interno?}
    J -->|Sí| K[Log error y retornar Error 500]
    J -->|No| L[Retornar Error 500 genérico]
```

## 7. Flujo de Inicialización del Servicio

```mermaid
flowchart TD
    A[Iniciar aplicación] --> B[Cargar variables de entorno]
    B --> C[Validar configuración requerida]
    C --> D{¿Configuración válida?}
    D -->|No| E[Error: Configuración inválida]
    D -->|Sí| F[Inicializar logger]
    F --> G[Configurar Express app]
    G --> H[Configurar middlewares de seguridad]
    H --> I[Configurar middlewares de autenticación]
    I --> J[Configurar rutas]
    J --> K[Configurar manejo de errores]
    K --> L[Iniciar servidor HTTP]
    L --> M[Servicio listo en puerto 8000]
```

## 8. Flujo de Validación de Token con Auth Service

```mermaid
flowchart TD
    A[Token JWT recibido] --> B[Preparar request a Auth Service]
    B --> C[Enviar POST /validate a Auth Service]
    C --> D{¿Request exitoso?}
    D -->|No| E[Error: Auth Service no disponible]
    D -->|Sí| F[Procesar respuesta]
    F --> G{¿Response válido?}
    G -->|No| H[Error: Respuesta inválida]
    G -->|Sí| I{¿Token válido?}
    I -->|No| J[Error: Token inválido o expirado]
    I -->|Sí| K[Token válido - continuar]
```

## 9. Flujo de Middleware de Seguridad (Helmet)

```mermaid
flowchart TD
    A[Request llega] --> B[Agregar headers de seguridad]
    B --> C[Content Security Policy]
    C --> D[HTTP Strict Transport Security]
    D --> E[X-Content-Type-Options]
    E --> F[X-Frame-Options]
    F --> G[X-XSS-Protection]
    G --> H[Referrer Policy]
    H --> I[Hide Powered-By]
    I --> J[Continuar al siguiente middleware]
```

## 10. Flujo de Logging

```mermaid
flowchart TD
    A[Request llega] --> B[Log inicio de request]
    B --> C[Procesar request]
    C --> D[Log fin de request]
    D --> E[Log duración del request]
    E --> F[Log status code]
    F --> G[Log tamaño de respuesta]
    G --> H[Log información de usuario]
    H --> I[Log nombre de archivo solicitado]
```

## 11. Flujo de Encriptación (Utilidad)

```mermaid
flowchart TD
    A[Texto a encriptar] --> B[Generar IV aleatorio]
    B --> C[Cifrar con AES-256-CBC]
    C --> D[Concatenar IV + texto cifrado]
    D --> E[Codificar en base64]
    E --> F[Texto encriptado listo]
```

## 12. Flujo de Desencriptación (Utilidad)

```mermaid
flowchart TD
    A[Texto encriptado] --> B[Decodificar base64]
    B --> C[Separar IV y texto cifrado]
    C --> D[Descifrar con AES-256-CBC]
    D --> E{¿Descifrado exitoso?}
    E -->|No| F[Error: Descifrado fallido]
    E -->|Sí| G[Texto desencriptado]
```

## 13. Flujo de Validación de Configuración

```mermaid
flowchart TD
    A[Configuración cargada] --> B{¿PORT definido?}
    B -->|No| C[Usar puerto por defecto: 8000]
    B -->|Sí| D[Validar rango de puerto]
    C --> E{¿AUTH_SERVICE_URL definido?}
    D --> E
    E -->|No| F[Error: AUTH_SERVICE_URL requerido]
    E -->|Sí| G[Validar formato de URL]
    F --> H[Terminar aplicación]
    G --> I{¿ENCRYPTION_KEY definido?}
    I -->|No| J[Error: ENCRYPTION_KEY requerido]
    I -->|Sí| K[Validar longitud de clave]
    J --> H
    K --> L[Configuración válida]
```

## 14. Flujo de Manejo de Archivos de Configuración

```mermaid
flowchart TD
    A[Solicitud de archivo] --> B[Desencriptar nombre]
    B --> C[Construir ruta en storage/]
    C --> D[Verificar archivos disponibles]
    D --> E{¿Archivo solicitado existe?}
    E -->|No| F[Retornar lista de archivos disponibles]
    E -->|Sí| G[Leer contenido]
    F --> H[Error: Archivo no encontrado]
    G --> I[Validar contenido]
    I --> J{¿Contenido válido?}
    J -->|No| K[Error: Contenido corrupto]
    J -->|Sí| L[Retornar contenido]
```

## 15. Flujo de Integración con Analysis Service

```mermaid
flowchart TD
    A[Analysis Service solicita archivo] --> B[Enviar GET /config/{filename}]
    B --> C[Validar token JWT]
    C --> D{¿Token válido?}
    D -->|No| E[Retornar Error 401]
    D -->|Sí| F[Leer archivo de configuración]
    E --> G[Analysis Service maneja error]
    F --> H{¿Lectura exitosa?}
    H -->|No| I[Retornar Error 500]
    H -->|Sí| J[Retornar contenido del archivo]
    I --> G
    J --> K[Analysis Service procesa configuración]
``` 