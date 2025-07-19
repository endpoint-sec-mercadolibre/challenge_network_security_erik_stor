import { NextFunction, Request, Response } from "express";

import Logger from "../../../infra/Logger";

export const initLogger = (req: Request, _: Response, next: NextFunction) => {
  Logger.setInstance({
    functionName: 'config-service',
  });
  Logger.getInstance().info(`${req.method} ${req.path} - ${req.ip}`);
  next();
}
