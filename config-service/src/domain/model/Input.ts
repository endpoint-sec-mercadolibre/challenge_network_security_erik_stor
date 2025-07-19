import { IsNotEmpty, IsString } from "class-validator";
import { InputRechargeMessageException } from "../exceptions/constants/InputMessageException";

export class InputFile {

  @IsString({ message: InputRechargeMessageException.FILENAME_MUST_BE_STRING })
  @IsNotEmpty({ message: InputRechargeMessageException.FILENAME_REQUIRED })
  filename: string;

  constructor(
    filename: string
  ) {
    this.filename = filename;
  }
} 
