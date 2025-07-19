import { BaseException } from "./BaseException";
import { ERROR_CODES, ERROR_MESSAGES, HTTP_STATUS_CODES } from "../constants/ErrorMessages";


export class InvalidDataException extends BaseException {

  constructor(errorMessages: string[]) {
    super(ERROR_MESSAGES.INVALID_DATA, ERROR_CODES.INVALID_DATA, HTTP_STATUS_CODES.BAD_REQUEST, errorMessages);
    this.name = 'InvalidDataException';
  }

}
