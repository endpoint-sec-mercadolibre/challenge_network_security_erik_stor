# Diagramas de Flujo - Analysis Service

## 1. Flujo Principal de Análisis

```mermaid
flowchart TD
    A[Cliente solicita análisis] --> B{¿Token JWT presente?}
    B -->|No| C[Retornar error 401 - Token requerido]
    B -->|Sí| D[Validar token con Auth Service]
    D --> E{¿Token válido?}
    E -->|No| F[Retornar error 401 - Token inválido]
    E -->|Sí| G{¿Parámetro filename presente?}
    G -->|No| H[Retornar error 400 - Filename requerido]
    G -->|Sí| I[Encriptar nombre de archivo]
    I --> J[Solicitar archivo al Config Service]
    J --> K{¿Archivo existe?}
    K -->|No| L[Retornar error 404 - Archivo no encontrado]
    K -->|Sí| M[Obtener contenido del archivo]
    M --> N[Analizar configuración]
    N --> O[Generar métricas de seguridad]
    O --> P[Identificar vulnerabilidades]
    P --> Q[Generar recomendaciones]
    Q --> R[Guardar análisis en MongoDB]
    R --> S[Retornar resultado del análisis]
```

## 2. Flujo de Health Check

```mermaid
flowchart TD
    A[Cliente solicita health check] --> B[Verificar conexión Auth Service]
    B --> C[Verificar conexión Config Service]
    C --> D[Verificar conexión MongoDB]
    D --> E{¿Todas las conexiones OK?}
    E -->|Sí| F[Retornar status: healthy]
    E -->|No| G[Retornar status: unhealthy]
```

## 3. Flujo de Autenticación

```mermaid
flowchart TD
    A[Request llega al middleware] --> B{¿Es ruta pública?}
    B -->|Sí| C[Continuar sin autenticación]
    B -->|No| D[Extraer token del header Authorization]
    D --> E{¿Token presente?}
    E -->|No| F[Retornar error 401 - Token requerido]
    E -->|Sí| G[Validar token con Auth Service]
    G --> H{¿Token válido?}
    H -->|No| I[Retornar error 401 - Token inválido]
    H -->|Sí| J[Agregar user info al request]
    J --> K[Continuar al endpoint]
```

## 4. Flujo de Análisis de Configuración

```mermaid
flowchart TD
    A[Iniciar análisis] --> B[Leer contenido del archivo]
    B --> C[Detectar tipo de configuración]
    C --> D{¿Tipo de archivo?}
    D -->|Router| E[Analizar configuración de router]
    D -->|Switch| F[Analizar configuración de switch]
    D -->|Firewall| G[Analizar configuración de firewall]
    D -->|Otro| H[Análisis genérico]
    E --> I[Verificar configuraciones de seguridad]
    F --> I
    G --> I
    H --> I
    I --> J[Calcular score de seguridad]
    J --> K[Identificar vulnerabilidades]
    K --> L[Generar recomendaciones]
    L --> M[Crear reporte de análisis]
    M --> N[Guardar en base de datos]
    N --> O[Retornar resultado]
```

## 5. Flujo de Manejo de Errores

```mermaid
flowchart TD
    A[Error ocurre] --> B{¿Tipo de error?}
    B -->|Autenticación| C[Log error de auth]
    B -->|Config Service| D[Log error de conexión]
    B -->|MongoDB| E[Log error de base de datos]
    B -->|Validación| F[Log error de validación]
    B -->|Otro| G[Log error general]
    C --> H[Retornar error 401]
    D --> I[Retornar error 404/500]
    E --> J[Retornar error 500]
    F --> K[Retornar error 400]
    G --> L[Retornar error 500]
```

## 6. Flujo de Inicialización del Servicio

```mermaid
flowchart TD
    A[Iniciar aplicación] --> B[Cargar variables de entorno]
    B --> C[Configurar logger]
    C --> D[Inicializar MongoDB connection]
    D --> E[Configurar FastAPI app]
    E --> F[Configurar middleware de auth]
    F --> G[Configurar CORS]
    G --> H[Configurar Swagger]
    H --> I[Registrar endpoints]
    I --> J[Iniciar servidor]
    J --> K[Servicio listo]
```

## 7. Flujo de Logging

```mermaid
flowchart TD
    A[Evento ocurre] --> B{¿Nivel de log?}
    B -->|DEBUG| C[Log detallado para desarrollo]
    B -->|INFO| D[Log informativo]
    B -->|WARN| E[Log de advertencia]
    B -->|ERROR| F[Log de error]
    B -->|SUCCESS| G[Log de éxito]
    C --> H[Escribir a archivo y consola]
    D --> H
    E --> H
    F --> H
    G --> H
    H --> I[Incluir timestamp y contexto]
```

## 8. Flujo de Integración con Config Service

```mermaid
flowchart TD
    A[Analysis Service] --> B[Solicitar archivo]
    B --> C[Encriptar nombre de archivo]
    C --> D[Enviar request a Config Service]
    D --> E{¿Config Service responde?}
    E -->|No| F[Error de conexión]
    E -->|Sí| G{¿Archivo encontrado?}
    G -->|No| H[Error 404 - Archivo no encontrado]
    G -->|Sí| I[Obtener contenido encriptado]
    I --> J[Desencriptar contenido]
    J --> K[Procesar contenido]
    K --> L[Retornar análisis]
```

## 9. Flujo de Validación de Datos

```mermaid
flowchart TD
    A[Recibir request] --> B{¿Método HTTP válido?}
    B -->|No| C[Error 405 - Método no permitido]
    B -->|Sí| D{¿Content-Type correcto?}
    D -->|No| E[Error 415 - Tipo de contenido no soportado]
    D -->|Sí| F{¿Parámetros requeridos presentes?}
    F -->|No| G[Error 400 - Parámetros faltantes]
    F -->|Sí| H{¿Parámetros válidos?}
    H -->|No| I[Error 400 - Parámetros inválidos]
    H -->|Sí| J[Continuar procesamiento]
```

## 10. Flujo de Almacenamiento en MongoDB

```mermaid
flowchart TD
    A[Análisis completado] --> B[Crear documento de análisis]
    B --> C[Agregar metadata]
    C --> D[Agregar resultados]
    D --> E[Agregar timestamp]
    E --> F[Conectar a MongoDB]
    F --> G{¿Conexión exitosa?}
    G -->|No| H[Error de conexión]
    G -->|Sí| I[Insertar documento]
    I --> J{¿Inserción exitosa?}
    J -->|No| K[Error de inserción]
    J -->|Sí| L[Confirmar guardado]
```

## 11. Flujo de Cálculo de Score de Seguridad

```mermaid
flowchart TD
    A[Analizar configuración] --> B[Verificar autenticación AAA]
    B --> C[Verificar logging de seguridad]
    C --> D[Verificar configuración SNMP]
    D --> E[Verificar políticas de acceso]
    E --> F[Verificar configuración de red]
    F --> G[Calcular puntuación base]
    G --> H[Restar puntos por vulnerabilidades]
    H --> I[Sumar puntos por buenas prácticas]
    I --> J[Normalizar score (0-100)]
    J --> K[Asignar nivel de seguridad]
    K --> L[Retornar score final]
```

## 12. Flujo de Generación de Recomendaciones

```mermaid
flowchart TD
    A[Análisis de configuración] --> B[Identificar configuraciones faltantes]
    B --> C[Identificar configuraciones inseguras]
    C --> D[Identificar mejores prácticas]
    D --> E[Generar recomendaciones de seguridad]
    E --> F[Generar recomendaciones de rendimiento]
    F --> G[Generar recomendaciones de compliance]
    G --> H[Priorizar recomendaciones]
    H --> I[Formatear recomendaciones]
    I --> J[Incluir en respuesta]
``` 