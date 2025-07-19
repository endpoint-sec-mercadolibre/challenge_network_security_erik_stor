
import { HTTP_STATUS_CODES } from "../exceptions/constants/ErrorMessages";
import { IResponse } from "../model/interfaces/IResponse";
import { SUCCESS_CODES, SUCCESS_MESSAGES } from "./consts/SuccessMessages";


export class SuccessResponse implements IResponse {

  constructor(
    public readonly data: any,
    public readonly name: string = 'SuccessResponse',
    public readonly title: string = 'Success',
    public readonly message: string = SUCCESS_MESSAGES.OK,
    public readonly code: string = SUCCESS_CODES.OK,
    public readonly statusCode: number = HTTP_STATUS_CODES.OK,
  ) { }



  public toResponse(): any {
    return {
      statusCode: this.statusCode,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
      body: JSON.stringify({
        message: this.message,
        ...this.data
      })
    };
  }

}
