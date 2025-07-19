import { NotFoundException } from "../exceptions/core/NotFoundException";
import { SystemException } from "../exceptions/core/SystemException";
import { InputFile } from "../model/Input";

export interface IFileReaderService {
  read(input: InputFile): Promise<string | NotFoundException | SystemException>
} 
