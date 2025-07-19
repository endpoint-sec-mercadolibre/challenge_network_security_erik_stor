import express, { Request, Response } from 'express';
import helmet from 'helmet';


import Logger from './infra/Logger';

import { AuditRepository } from './adapters/repository/AuditRepository';
import FileReaderService from './adapters/service/FileReaderService';

import { GetConfigCommandHandler } from './domain/command_handlers/GetConfigCommandHandler';


import { ConfigController } from './entrypoints/api/GetConfigController';
import { catchError } from './entrypoints/api/middlewares/catchError';
import { extractFilename } from './entrypoints/api/middlewares/extractFilename';
import { initLogger } from './entrypoints/api/middlewares/initLogger';


// Configuración del servidor Express
const app = express();
const PORT = process.env.PORT || 3000;

app.use(helmet({
  // TODO: Ajustar politicas de seguridad
  // contentSecurityPolicy: {
  //   directives: {
  //     defaultSrc: ["'self'"],
  //     styleSrc: ["'self'", "'unsafe-inline'"],
  //     scriptSrc: ["'self'"],
  //     imgSrc: ["'self'", "data:", "https:"],
  //     connectSrc: ["'self'"],
  //     fontSrc: ["'self'"],
  //     objectSrc: ["'none'"],
  //     mediaSrc: ["'self'"],
  //     frameSrc: ["'none'"],
  //   },
  // },
  // hsts: {
  //   maxAge: 31536000,
  //   includeSubDomains: true,
  //   preload: true
  // },
  // noSniff: true,
  // referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
  // frameguard: { action: 'deny' },
  // xssFilter: true,
  // hidePoweredBy: true
}));

// Middleware para parsing de JSON
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Middleware de logging
app.use(initLogger);

// Middleware de manejo de errores
app.use(catchError);

// Ruta de health check
app.get('/health', (_: Request, res: Response) => {
  res.status(200).json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    service: 'config-service'
  });
});

// Ruta principal para configuración
app.get(
  '/config/{:filename}',
  extractFilename,
  async (req: Request, res: Response) => {
    try {

      const controller = new ConfigController(
        new AuditRepository(),
        new GetConfigCommandHandler(new FileReaderService())
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

    Logger.success(`Servicio corriendo en el puerto ${PORT} en modo ${process.env.NODE_ENV}`);
  });
}

export default app; 
