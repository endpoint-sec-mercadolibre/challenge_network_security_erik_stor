import { NextFunction, Request, Response } from 'express';
import { AuthService } from '../../../adapters/service/AuthService';
import Logger from '../../../infra/Logger';

export const authMiddleware = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  const authService = new AuthService();

  // Log del inicio de validación
  Logger.info('Iniciando validación de autenticación', {
    method: req.method,
    path: req.path,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
  });

  try {
    // Extraer el token del header Authorization
    const authHeader = req.headers.authorization;
    
    if (!authHeader) {
      Logger.warn('Header de autorización no encontrado', {
        method: req.method,
        path: req.path,
        ip: req.ip,
      });
      
      res.status(401).json({
        error: 'Token de autorización requerido',
        message: 'Debe proporcionar un token JWT en el header Authorization',
        code: 'AUTH_TOKEN_REQUIRED'
      });
      return;
    }

    // Verificar que el header tenga el formato correcto: "Bearer <token>"
    const tokenParts = authHeader.split(' ');
    
    if (tokenParts.length !== 2 || tokenParts[0] !== 'Bearer') {
      Logger.warn('Formato de token inválido', {
        method: req.method,
        path: req.path,
        ip: req.ip,
        authHeaderFormat: tokenParts.length,
      });
      
      res.status(401).json({
        error: 'Formato de token inválido',
        message: 'El token debe tener el formato: Bearer <token>',
        code: 'AUTH_TOKEN_INVALID_FORMAT'
      });
      return;
    }

    const token = tokenParts[1];

    if (!token || token.trim() === '') {
      Logger.warn('Token vacío', {
        method: req.method,
        path: req.path,
        ip: req.ip,
      });
      
      res.status(401).json({
        error: 'Token vacío',
        message: 'El token no puede estar vacío',
        code: 'AUTH_TOKEN_EMPTY'
      });
      return;
    }

    Logger.info('Token extraído correctamente', {
      method: req.method,
      path: req.path,
      tokenLength: token.length,
    });

    // Validar el token contra el servicio de autenticación
    const validationResult = await authService.validateToken(token);

    if (!validationResult.valid) {
      Logger.warn('Token inválido', {
        method: req.method,
        path: req.path,
        ip: req.ip,
        error: validationResult.error,
      });
      
      res.status(401).json({
        error: 'Token inválido',
        message: validationResult.error || 'El token proporcionado no es válido',
        code: 'AUTH_TOKEN_INVALID'
      });
      return;
    }

    // Token válido, agregar información del usuario al request
    req.user = {
      username: validationResult.user || 'unknown',
      token: token,
    };

    Logger.info('Autenticación exitosa', {
      method: req.method,
      path: req.path,
      ip: req.ip,
      username: validationResult.user,
    });

    next();
  } catch (error) {
    Logger.error('Error en middleware de autenticación', {
      error: error instanceof Error ? error.message : String(error),
      method: req.method,
      path: req.path,
      ip: req.ip,
    });

    res.status(500).json({
      error: 'Error interno de autenticación',
      message: 'Error al procesar la autenticación',
      code: 'AUTH_INTERNAL_ERROR'
    });
    return;
  }
};

// Extender la interfaz Request para incluir información del usuario
declare global {
  namespace Express {
    interface Request {
      user?: {
        username: string;
        token: string;
      };
    }
  }
} 
