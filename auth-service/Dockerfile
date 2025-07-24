FROM golang:1.23-alpine AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY go.mod go.sum ./

# Descargar dependencias
RUN go mod download

# Copiar código fuente
COPY . .

# Compilar la aplicación con optimizaciones
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -ldflags="-w -s" -o main .

# Imagen final optimizada
FROM alpine:latest

# Instalar dependencias necesarias
RUN apk --no-cache add ca-certificates wget

# Crear usuario no-root y directorio de trabajo
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001 -h /home/appuser && \
    mkdir -p /home/appuser/logs && \
    chown -R appuser:appuser /home/appuser

WORKDIR /home/appuser

# Copiar el binario compilado
COPY --from=builder /app/main .
RUN chown appuser:appuser main

# Cambiar al usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8080

# Health check
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Comando para ejecutar la aplicación
CMD ["./main"] 