import { File } from "./interfaces/IOutput";


export class OutputFile implements File {

  constructor(
    public readonly content: string
  ) {
  }
}



