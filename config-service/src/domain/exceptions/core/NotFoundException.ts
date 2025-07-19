import { BaseException } from "./BaseException";
import { ERROR_MESSAGES, ERROR_CODES, HTTP_STATUS_CODES } from "../constants/ErrorMessages";


export class NotFoundException extends BaseException {
  constructor() {
    super(ERROR_MESSAGES.NOT_FOUND, ERROR_CODES.INVALID_DATA, HTTP_STATUS_CODES.NOT_FOUND);
    this.name = 'NotFoundException';
  }
}
