import * as fs from 'fs';
import Logger from '../infra/Logger';
import { FILE_DEFAULT_ENCODING } from '../domain/common/consts/Setup';

interface FileReadOptions {
  encoding?: BufferEncoding;
  flag?: string;
}

interface FileInfo {
  name: string;
  path: string;
  size: number;
  extension: string;
  lastModified: Date;
}

class FileReaderService {
  private static readonly DEFAULT_ENCODING: BufferEncoding = FILE_DEFAULT_ENCODING as BufferEncoding;

  /**
   * Lee el contenido completo de un archivo
   * @param filePath - Ruta del archivo a leer
   * @param options - Opciones de lectura (encoding, flag)
   * @returns Promise<string> - Contenido del archivo
   */
  public static async readFile(filePath: string, options?: FileReadOptions): Promise<string> {

    Logger.getInstance().info('Iniciando lectura de archivo', { filePath, options });

    try {
      // Validar que el archivo existe
      if (!fs.existsSync(filePath)) {
        Logger.error('El archivo no existe', { filePath });
        throw new Error(`El archivo no existe: ${filePath}`);
      }

      // Leer el contenido del archivo
      const encoding = options?.encoding || this.DEFAULT_ENCODING;
      const content = await fs.promises.readFile(filePath, { encoding, flag: options?.flag });

      Logger.getInstance().info('Archivo leído exitosamente', {
        filePath,
        contentLength: content.length,
        encoding
      });

      return content;

    } catch (error) {
      Logger.getInstance().error('Error al leer el archivo', { filePath, error: error instanceof Error ? error.message : error });
      throw error;
    }
  }

  /**
   * Verifica si un archivo existe
   * @param filePath - Ruta del archivo
   * @returns Promise<boolean> - true si existe, false en caso contrario
   */
  public static async fileExists(filePath: string): Promise<boolean> {

    Logger.getInstance().debug('Verificando existencia del archivo', { filePath });

    try {
      const exists = fs.existsSync(filePath);
      Logger.getInstance().debug('Resultado de verificación de existencia', { filePath, exists });
      return exists;
    } catch (error) {
      Logger.getInstance().error('Error al verificar existencia del archivo', { filePath, error: error instanceof Error ? error.message : error });
      return false;
    }
  }


}

export default FileReaderService;
export { FileReadOptions, FileInfo }; 
