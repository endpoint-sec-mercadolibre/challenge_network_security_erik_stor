# Diagrama de Secuencia - Auth Service

## 1. Secuencia de Login Exitoso

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as Middleware
    participant V as Validator
    participant A as AuthController
    participant L as LoginUseCase
    participant U as UserRepository
    participant P as PasswordService
    participant T as TokenService
    participant DB as MongoDB

    C->>M: POST /login {username, password}
    M->>V: Validar datos de entrada
    V-->>M: Datos válidos
    M->>A: Request validado
    A->>L: Execute(username, password)
    L->>U: FindByUsername(username)
    U->>DB: Query users collection
    DB-->>U: User document
    U-->>L: User entity
    L->>P: ComparePassword(password, user.password)
    P-->>L: Password válido
    L->>T: GenerateToken(user)
    T-->>L: JWT token
    L-->>A: LoginResponse{token, user}
    A-->>M: HTTP 200 + response
    M-->>C: JSON response
```

## 2. Secuencia de Login Fallido - Credenciales Inválidas

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as Middleware
    participant V as Validator
    participant A as AuthController
    participant L as LoginUseCase
    participant U as UserRepository
    participant P as PasswordService
    participant DB as MongoDB

    C->>M: POST /login {username, password}
    M->>V: Validar datos de entrada
    V-->>M: Datos válidos
    M->>A: Request validado
    A->>L: Execute(username, password)
    L->>U: FindByUsername(username)
    U->>DB: Query users collection
    DB-->>U: User not found
    U-->>L: nil
    L-->>A: Error: credenciales inválidas
    A-->>M: HTTP 401 + error
    M-->>C: JSON error response
```

## 3. Secuencia de Login Fallido - Validación

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as Middleware
    participant V as Validator
    participant A as AuthController

    C->>M: POST /login {username: "a", password: "123"}
    M->>V: Validar datos de entrada
    V->>V: Validar username (formato)
    V->>V: Validar password (formato)
    V-->>M: Error: datos inválidos
    M-->>C: HTTP 400 + detalles de validación
```

## 4. Secuencia de Validación de Token

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as Middleware
    participant V as Validator
    participant T as TokenController
    participant VT as ValidateTokenUseCase
    participant TS as TokenService

    C->>M: POST /validate {token}
    M->>V: Validar formato JSON
    V-->>M: JSON válido
    M->>T: Request validado
    T->>VT: Execute(token)
    VT->>TS: ValidateToken(token)
    TS->>TS: Parse JWT token
    TS->>TS: Verify RSA signature
    TS->>TS: Check expiration
    TS-->>VT: Token válido
    VT-->>T: ValidateResponse{valid: true, user}
    T-->>M: HTTP 200 + response
    M-->>C: JSON response
```

## 5. Secuencia de Validación de Token Expirado

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as Middleware
    participant V as Validator
    participant T as TokenController
    participant VT as ValidateTokenUseCase
    participant TS as TokenService

    C->>M: POST /validate {token}
    M->>V: Validar formato JSON
    V-->>M: JSON válido
    M->>T: Request validado
    T->>VT: Execute(token)
    VT->>TS: ValidateToken(token)
    TS->>TS: Parse JWT token
    TS->>TS: Verify RSA signature
    TS->>TS: Check expiration
    TS-->>VT: Token expirado
    VT-->>T: ValidateResponse{valid: false, error: "expirado"}
    T-->>M: HTTP 200 + response
    M-->>C: JSON response
```

## 6. Secuencia de Obtención de Llave Pública

```mermaid
sequenceDiagram
    participant C as Cliente
    participant T as TokenController
    participant TS as TokenService
    participant F as FileSystem

    C->>T: GET /public-key
    T->>TS: GetPublicKey()
    TS->>F: Read public.pem
    F-->>TS: Public key content
    TS-->>T: Public key PEM
    T-->>C: HTTP 200 + public key
```

## 7. Secuencia de Health Check

```mermaid
sequenceDiagram
    participant C as Cliente
    participant H as HealthController
    participant S as SeedService
    participant U as UserRepository
    participant DB as MongoDB

    C->>H: GET /health
    H->>H: Check MongoDB connection
    H->>S: EnsureDefaultUser()
    S->>U: FindByUsername("admin")
    U->>DB: Query users collection
    DB-->>U: User not found
    U-->>S: nil
    S->>S: Create default user
    S->>U: Create(user)
    U->>DB: Insert user document
    DB-->>U: Success
    U-->>S: User created
    S-->>H: Default user ensured
    H-->>C: HTTP 200 + health status
```

## 8. Secuencia de Inicialización del Servicio

```mermaid
sequenceDiagram
    participant M as Main
    participant C as Container
    participant L as Logger
    participant R as Routes
    participant TS as TokenService
    participant F as FileSystem

    M->>M: Load environment variables
    M->>L: Initialize logger
    M->>C: Create dependency container
    C->>C: Register repositories
    C->>C: Register services
    C->>C: Register use cases
    C->>C: Register controllers
    M->>R: Setup routes
    M->>TS: Initialize token service
    TS->>F: Check if private.pem exists
    F-->>TS: File not found
    TS->>TS: Generate RSA key pair
    TS->>F: Write private.pem
    TS->>F: Write public.pem
    TS-->>M: Token service ready
    M->>M: Start HTTP server
    M-->>M: Service ready on port 8080
```

## 9. Secuencia de Error de Validación

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as Middleware
    participant V as Validator

    C->>M: POST /login {invalid_data}
    M->>V: Validar datos de entrada
    V->>V: Validate username format
    V->>V: Validate password requirements
    V-->>M: Validation errors
    M-->>C: HTTP 400 + error details
```

## 10. Secuencia de Error de Base de Datos

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as Middleware
    participant A as AuthController
    participant L as LoginUseCase
    participant U as UserRepository
    participant DB as MongoDB

    C->>M: POST /login {username, password}
    M->>A: Request validado
    A->>L: Execute(username, password)
    L->>U: FindByUsername(username)
    U->>DB: Query users collection
    DB-->>U: Connection error
    U-->>L: Database error
    L-->>A: Internal server error
    A-->>M: HTTP 503 + error
    M-->>C: JSON error response
```

## 11. Secuencia de Middleware de CORS

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as CORS Middleware
    participant H as Handler

    C->>M: HTTP Request
    M->>M: Check if OPTIONS request
    alt Preflight request
        M->>M: Add CORS headers
        M-->>C: HTTP 200 OK
    else Regular request
        M->>M: Add CORS headers
        M->>H: Forward request
        H-->>M: Response
        M-->>C: Response with CORS headers
    end
```

## 12. Secuencia de Middleware de Logging

```mermaid
sequenceDiagram
    participant C as Cliente
    participant L as Logging Middleware
    participant H as Handler
    participant LG as Logger

    C->>L: HTTP Request
    L->>LG: Log request start
    L->>H: Forward request
    H-->>L: Response
    L->>LG: Log request end + duration
    L-->>C: Response
```

## 13. Secuencia de Integración con Otros Servicios

```mermaid
sequenceDiagram
    participant AS as Analysis Service
    participant A as Auth Service
    participant C as Service

    AS->>A: POST /login {credentials}
    A-->>AS: JWT token
    AS->>C: GET /config/file + Authorization: Bearer token
    C->>A: POST /validate {token}
    A-->>C: {valid: true, user}
    C-->>AS: Service response
```

## 14. Secuencia de Creación de Usuario por Defecto

```mermaid
sequenceDiagram
    participant H as Health Controller
    participant S as Seed Service
    participant P as Password Service
    participant U as User Repository
    participant DB as MongoDB

    H->>S: EnsureDefaultUser()
    S->>U: FindByUsername("admin")
    U->>DB: Query users collection
    DB-->>U: No user found
    U-->>S: nil
    S->>P: HashPassword("Password123!")
    P-->>S: Hashed password
    S->>S: Create user entity
    S->>U: Create(user)
    U->>DB: Insert user document
    DB-->>U: Success
    U-->>S: User created
    S-->>H: Default user ensured
```

## 15. Secuencia de Manejo de Errores

```mermaid
sequenceDiagram
    participant C as Cliente
    participant M as Middleware
    participant H as Handler
    participant L as Logger

    C->>M: HTTP Request
    M->>H: Forward request
    H->>H: Process request
    H->>H: Error occurs
    H->>L: Log error with context
    H-->>M: Error response
    M->>M: Format error response
    M-->>C: HTTP error + details
``` 