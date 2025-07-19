import { BaseException } from "./BaseException";
import { ERROR_CODES, HTTP_STATUS_CODES } from "../constants/ErrorMessages";

export class SystemException extends BaseException {
  constructor(message: string) {
    super(message, ERROR_CODES.INTERNAL_ERROR, HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR);
    this.name = 'SystemException';
  }
} 
