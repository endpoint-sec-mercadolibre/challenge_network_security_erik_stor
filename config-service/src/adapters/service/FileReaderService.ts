import path from 'path';

import { ERROR_MESSAGES } from '../../domain/exceptions/constants/ErrorMessages';
import { NotFoundException } from '../../domain/exceptions/core/NotFoundException';
import { SystemException } from '../../domain/exceptions/core/SystemException';
import { InputFile } from '../../domain/model/Input';
import { IFileReaderService } from '../../domain/ports/IFileReaderService';

import Logger from '../../infra/Logger';

import FileReader from '../../utils/FileReaderUtil';
import { Encrypt } from '../../utils/Encrypt';
import { STORAGE_PATH } from '../../domain/common/consts/Setup';


class FileReaderService implements IFileReaderService {

  constructor(private readonly encrypt: Encrypt) {
    this.encrypt = new Encrypt();
  }


  public async read(input: InputFile): Promise<string | NotFoundException | SystemException> {

    Logger.info('Iniciando la lectura de archivo', { input });

    try {

      const filePath = path.join(__dirname, `${STORAGE_PATH}/${input.filename}`);
      const absolutePath = path.resolve(filePath);

      // Verificar si el archivo existe
      const existe = await FileReader.fileExists(filePath);

      Logger.info('Verificación de existencia', {
        filePath,
        absolutePath,
        filename: input.filename,
        existe
      });

      if (existe) {
        // Leer el contenido del archivo
        const contenido = await FileReader.readFile(filePath);
        Logger.info('Contenido leído', {
          filePath,
          contenidoLength: contenido.length,
          preview: contenido.substring(0, 10) + '...'
        });

        const textEncrypted = await this.encrypt.encrypt(contenido);
        return this.encrypt.ofuscarBase64(textEncrypted);
      }

      return new NotFoundException();

    } catch (error) {
      Logger.error('Error en lectura del archivo', { error: error instanceof Error ? error.message : error });
      return new SystemException(ERROR_MESSAGES.INTERNAL_ERROR);
    }
  }

}

export default FileReaderService; 
