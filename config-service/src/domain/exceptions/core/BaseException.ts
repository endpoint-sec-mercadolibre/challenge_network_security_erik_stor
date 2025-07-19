

import { IResponse } from "../../model/interfaces/IResponse";
import { HTTP_STATUS_CODES } from "../constants/ErrorMessages";

export class BaseException extends Error implements IResponse {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR,
    public readonly data: any = {},
    public readonly title: string = 'Error'
  ) {
    super(message);
    this.name = this.constructor.name;
  }

  public toResponse(): any {
    return {
      statusCode: this.statusCode,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
      body: JSON.stringify({
        title: this.title,
        code: this.code,
        message: this.message,
        error: {
          detail: this.data
        }
      })
    };
  }
}
