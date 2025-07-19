import { NextFunction, Request, Response } from "express";

import { Encrypt } from "../../../utils/Encrypt";

export const extractFilename = (req: Request, _: Response, next: NextFunction) => {

  req.params.filename = Encrypt.decryptAndFromBase64(req.params?.filename ?? '');

  next();
}
