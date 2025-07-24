import { NextFunction, Request, Response } from "express";

import Logger from "../../../infra/Logger";
import { Encrypt } from "../../../utils/Encrypt";
import { SystemException } from "../../../domain/exceptions/core/SystemException";

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

    const base64Decoded = encrypt.desofuscarBase64(urlDecoded);
    const decryptedFilename = await encrypt.decrypt(base64Decoded);
    Logger.info('Filename desencriptado:', { decryptedFilename });

    if (decryptedFilename instanceof SystemException) {
      req.params.filename = ''
    } else {
      req.params.filename = decryptedFilename;
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
