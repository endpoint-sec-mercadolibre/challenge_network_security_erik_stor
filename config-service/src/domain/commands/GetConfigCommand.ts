import { InputFile } from "../model/Input";


export class GetConfigCommand {
  constructor(
    public readonly request: InputFile
  ) { }
} 
