import path from 'path';

import { ERROR_MESSAGES } from '../../domain/exceptions/constants/ErrorMessages';
import { NotFoundException } from '../../domain/exceptions/core/NotFoundException';
import { SystemException } from '../../domain/exceptions/core/SystemException';
import { InputFile } from '../../domain/model/Input';
import { IFileReaderService } from '../../domain/ports/IFileReaderService';

import Logger from '../../infra/Logger';

import FileReader from '../../utils/FileReaderUtil';
import { Encrypt } from '../../utils/Encrypt';

/**
 * Ejemplo de uso de la clase FileReader
 */
class FileReaderService implements IFileReaderService {

  /**
   * Ejemplo de lectura básica de archivo
   */
  public async read(input: InputFile): Promise<string | NotFoundException | SystemException> {

    Logger.getInstance().info('Iniciando ejemplo de lectura básica de archivo', { input });

    try {

      const filePath = path.join(__dirname, `../../storage/${input.filename}`);

      // Verificar si el archivo existe
      const existe = await FileReader.fileExists(filePath);

      Logger.getInstance().info('Verificación de existencia', { filePath, existe });

      if (existe) {
        // Leer el contenido del archivo
        const contenido = await FileReader.readFile(filePath);
        Logger.getInstance().info('Contenido leído', {
          filePath,
          contenidoLength: contenido.length,
          preview: contenido.substring(0, 100) + '...'
        });

        return Encrypt.toBase64AndEncrypt(contenido);
      }

      return new NotFoundException();

    } catch (error) {
      Logger.error('Error en ejemplo de lectura básica', { error: error instanceof Error ? error.message : error });
      return new SystemException(ERROR_MESSAGES.INTERNAL_ERROR);
    }
  }

}

export default FileReaderService; 
