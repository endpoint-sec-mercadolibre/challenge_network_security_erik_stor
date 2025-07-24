FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema y wget para healthchecks
RUN apt-get update && apt-get install -y \
    gcc \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias de Python con optimizaciones
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Instalar el paquete en modo desarrollo
RUN pip install -e .

# Crear directorio de logs y usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    mkdir -p logs && \
    chown -R appuser:appuser /app

# Cambiar al usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8002

# Health check
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8002/health || exit 1

# Comando para ejecutar la aplicación
CMD ["python", "run.py"] 