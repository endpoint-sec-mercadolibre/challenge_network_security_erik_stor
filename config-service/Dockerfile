# Multi-stage build para optimizar el tamaño de la imagen
FROM node:22-alpine AS builder

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY package*.json ./ 
COPY tsconfig*.json ./
COPY webpack.config.js ./

# Instalar todas las dependencias (incluyendo devDependencies para build)
RUN npm ci --no-audit --no-fund --prefer-offline && npm cache clean --force

# Copiar código fuente
COPY src/ ./src/

# Construir la aplicación
RUN npm run build

# Imagen de producción
FROM node:22-alpine AS production

# Instalar dumb-init para manejo correcto de señales
RUN apk add --no-cache dumb-init

# Crear usuario no-root para seguridad
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de dependencias desde el builder
COPY --from=builder /app/package*.json ./

# Instalar solo dependencias de producción
RUN npm ci --only=production --no-audit --no-fund --prefer-offline && npm cache clean --force && \
    chown -R nodejs:nodejs /app

# Copiar archivos construidos desde el stage anterior
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist

# Cambiar al usuario no-root
USER nodejs

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8000/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Usar dumb-init para manejo correcto de señales
ENTRYPOINT ["dumb-init", "--"]

# Comando para iniciar la aplicación
CMD ["node", "dist/index.js"] 
