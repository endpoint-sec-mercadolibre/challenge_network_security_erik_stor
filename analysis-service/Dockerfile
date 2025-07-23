FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Instalar el paquete en modo desarrollo
RUN pip install -e .

# Crear directorio de logs
RUN mkdir -p logs

# Exponer puerto
EXPOSE 8002

# Comando para ejecutar la aplicación
CMD ["python", "run.py"] 