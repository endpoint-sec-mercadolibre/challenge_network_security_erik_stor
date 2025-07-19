import { NextFunction, Request, Response } from "express";

import Logger from "../../../infra/Logger";

export const catchError = (error: Error, _: Request, res: Response, __: NextFunction) => {
  Logger.getInstance().error('Error en el servidor:', error.message);
  res.status(500).json({
    error: 'Error interno del servidor',
    message: process.env.NODE_ENV === 'development' ? error.message : 'Algo salió mal'
  });
}
