import { BaseException } from './core/BaseException';
import { HTTP_STATUS_CODES } from './constants/ErrorMessages';

export class GetContentException extends BaseException {
  constructor(message: string, code: string, statusCode: number = HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR
  ) {
    super(message, code, statusCode);
    this.name = 'GetContentException';
  }
}




