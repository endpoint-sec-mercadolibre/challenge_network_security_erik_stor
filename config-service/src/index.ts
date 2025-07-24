import cors from 'cors';
import express, { Request, Response } from 'express';
import helmet from 'helmet';
import swaggerUi from 'swagger-ui-express';

import Logger from './infra/Logger';

import FileReaderService from './adapters/service/FileReaderService';

import { GetConfigCommandHandler } from './domain/command_handlers/GetConfigCommandHandler';

import { specs } from './config/swagger';

import { ConfigController } from './entrypoints/api/GetConfigController';
import { catchError } from './entrypoints/api/middlewares/catchError';
import { extractFilename } from './entrypoints/api/middlewares/extractFilename';
import { initLogger } from './entrypoints/api/middlewares/initLogger';
import { authMiddleware } from './entrypoints/api/middlewares/authMiddleware';
import { Encrypt } from './utils/Encrypt';


// Configuración del servidor Express
const app = express();
const PORT = process.env.PORT || 3000;

app.use(helmet());

// Middleware de CORS
app.use(cors());

// Middleware para parsing de JSON
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Middleware de logging
app.use(initLogger);

// Middleware de manejo de errores
app.use(catchError);

// Configuración de Swagger
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs));

// Ruta de health check
/**
 * @swagger
 * /health:
 *   get:
 *     summary: Verificar estado del servicio
 *     description: Endpoint para verificar que el servicio esté funcionando correctamente
 *     tags: [Salud]
 *     responses:
 *       200:
 *         description: Servicio funcionando correctamente
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/HealthResponse'
 */
app.get('/health', (_: Request, res: Response) => {
  res.status(200).json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    service: 'config-service'
  });
});

/**
 * @swagger
 * /config/{filename}:
 *   get:
 *     summary: Obtener configuración de un archivo
 *     description: Lee y retorna el contenido de un archivo de configuración específico. Requiere autenticación JWT.
 *     tags: [Configuración]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: filename
 *         required: true
 *         schema:
 *           type: string
 *         description: 'Nombre del archivo de configuración encriptado y en base64'
 *         example: VTJGc2RHVmtYMStwTjRMaTZsK0RobEg0WkpBR29VbmZYM3lQSmF5Z01ZSTZqTG1xWFV3eDFIbDVudVdCTzVMZg==
 *     responses:
 *       200:
 *         description: Configuración obtenida exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ConfigResponse'
 *       401:
 *         description: No autorizado - Token JWT requerido o inválido
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       400:
 *         description: Error de validación en los parámetros
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       404:
 *         description: Archivo de configuración no encontrado
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       500:
 *         description: Error interno del servidor
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.get(
  '/config/:filename',
  authMiddleware,
  extractFilename,
  async (req: Request, res: Response) => {
    try {

      const encrypt = new Encrypt();
      const fileReaderService = new FileReaderService(encrypt);

      const controller = new ConfigController(
        new GetConfigCommandHandler(fileReaderService)
      );

      // Log solo información relevante del request para evitar referencias circulares
      Logger.getInstance().info('Request recibido:', {
        method: req.method,
        path: req.path,
        ip: req.ip,
        userAgent: req.get('User-Agent')
      });

      const result = await controller.handle(req);

      res.status(result.statusCode).json(JSON.parse(result.body));
    } catch (error) {
      Logger.error('Error en el endpoint /config:', error instanceof Error ? error.message : String(error));
      res.status(500).json({
        error: 'Error interno del servidor',
        message: 'Error procesando la configuración'
      });
    }
  });

// Iniciar el servidor
if (require.main === module) {
  app.listen(PORT, () => {
    Logger.info(`Servidor config-service iniciado en el puerto ${PORT}`);
    Logger.info(`Health check disponible en: http://localhost:${PORT}/health`);
    Logger.info(`Endpoint de configuración disponible en: http://localhost:${PORT}/config`);
    Logger.info(`Documentación Swagger disponible en: http://localhost:${PORT}/api-docs`);
    Logger.success(`Servicio corriendo en el puerto ${PORT} en modo ${process.env.NODE_ENV}`);
  });
}

export default app; 
