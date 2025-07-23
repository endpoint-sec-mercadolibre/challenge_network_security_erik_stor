import { NextFunction, Request, Response } from "express";

import Logger from "../../../infra/Logger";
import { Encrypt } from "../../../utils/Encrypt";

export const extractFilename = async (req: Request, _: Response, next: NextFunction) => {

  const encrypt = new Encrypt();
  // Log solo información relevante del request para evitar referencias circulares
  Logger.info('Inicio de proceso de extracción de nombre de archivo', {
    method: req.method,
    path: req.path,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    pathParameters: req.params,
    originalFilename: req.params?.filename
  });

  try {

    const originalFilename = req.params?.filename || '';
    Logger.info('Procesando filename:', { originalFilename });

    if (!originalFilename) {
      Logger.error('Filename está vacío o no definido');
      req.params.filename = '';
      next();
      return;
    }

    // Decodificar URL encoding primero
    const urlDecoded = decodeURIComponent(originalFilename);
    Logger.info('Después de URL decode:', { urlDecoded });

    try {
      // NUEVO: Usar CompatibleEncrypt que maneja múltiples métodos de desencriptación
      const base64Decoded = encrypt.desofuscarBase64(urlDecoded);
      const decryptedFilename = await encrypt.decrypt(base64Decoded);
      Logger.info('Filename desencriptado exitosamente con CompatibleEncrypt:', { decryptedFilename });

      req.params.filename = decryptedFilename;

    } catch (compatibleError) {
      Logger.info('CompatibleEncrypt falló, intentando método clásico como fallback', {
        error: compatibleError instanceof Error ? compatibleError.message : String(compatibleError)
      });

      try {
        // FALLBACK: Usar el método original como último recurso
        const base64Decoded = encrypt.desofuscarBase64(urlDecoded);
        Logger.info('Base64 decodificado con método clásico:', { base64Decoded });

        const finalDecryptedFilename = await encrypt.decrypt(base64Decoded);
        Logger.info('Filename desencriptado exitosamente con método clásico:', { finalDecryptedFilename });

        req.params.filename = finalDecryptedFilename;

      } catch (classicError) {
        Logger.error('Error al desencriptar el nombre de archivo con ambos métodos', {
          compatibleError: compatibleError instanceof Error ? compatibleError.message : String(compatibleError),
          classicError: classicError instanceof Error ? classicError.message : String(classicError),
          urlDecoded
        });

        // En caso de error de desencriptación con ambos métodos, usar el nombre original
        req.params.filename = originalFilename;
      }
    }

  } catch (error) {
    Logger.error('Error general al desencriptar el nombre de archivo', {
      error: error instanceof Error ? error.message : String(error),
      originalFilename: req.params?.filename
    });
    // En caso de error, mantener el filename original para que el controlador pueda manejarlo
    req.params.filename = req.params?.filename || '';
  }

  next();
}
