import FileReaderService, { FileReadOptions, FileInfo } from '../../../src/utils/FileReaderUtil';
import * as fs from 'fs';
import Logger from '../../../src/infra/Logger';
import { FILE_DEFAULT_ENCODING } from '../../../src/domain/common/consts/Setup';

// Mock de fs
jest.mock('fs', () => ({
  existsSync: jest.fn(),
  promises: {
    readFile: jest.fn()
  }
}));
const mockFs = fs as jest.Mocked<typeof fs>;

// Mock de Logger
jest.mock('../../../src/infra/Logger');
const mockLogger = Logger as jest.Mocked<typeof Logger>;

describe('FileReaderService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Configurar mocks por defecto
    mockLogger.info = jest.fn();
    mockLogger.error = jest.fn();
    mockLogger.debug = jest.fn();
  });

  describe('readFile', () => {
    it('debería leer un archivo correctamente con encoding por defecto', async () => {
      const filePath = '/ruta/al/archivo.txt';
      const fileContent = 'Contenido del archivo';
      
      // Mock de existsSync
      mockFs.existsSync.mockReturnValue(true);
      
      // Mock de readFile
      mockFs.promises.readFile = jest.fn().mockResolvedValue(fileContent);

      const result = await FileReaderService.readFile(filePath);

      expect(result).toBe(fileContent);
      expect(mockFs.existsSync).toHaveBeenCalledWith(filePath);
      expect(mockFs.promises.readFile).toHaveBeenCalledWith(filePath, {
        encoding: FILE_DEFAULT_ENCODING,
        flag: undefined
      });
      expect(mockLogger.info).toHaveBeenCalledWith('Iniciando lectura de archivo', {
        filePath,
        options: undefined
      });
      expect(mockLogger.info).toHaveBeenCalledWith('Archivo leído exitosamente', {
        filePath,
        contentLength: fileContent.length,
        encoding: FILE_DEFAULT_ENCODING
      });
    });

    it('debería leer un archivo con opciones personalizadas', async () => {
      const filePath = '/ruta/al/archivo.txt';
      const fileContent = 'Contenido del archivo';
      const options: FileReadOptions = {
        encoding: 'utf8',
        flag: 'r'
      };
      
      mockFs.existsSync.mockReturnValue(true);
      mockFs.promises.readFile = jest.fn().mockResolvedValue(fileContent);

      const result = await FileReaderService.readFile(filePath, options);

      expect(result).toBe(fileContent);
      expect(mockFs.promises.readFile).toHaveBeenCalledWith(filePath, {
        encoding: 'utf8',
        flag: 'r'
      });
      expect(mockLogger.info).toHaveBeenCalledWith('Iniciando lectura de archivo', {
        filePath,
        options
      });
    });

    it('debería lanzar error si el archivo no existe', async () => {
      const filePath = '/ruta/al/archivo-inexistente.txt';
      
      mockFs.existsSync.mockReturnValue(false);

      await expect(FileReaderService.readFile(filePath)).rejects.toThrow(
        `El archivo no existe: ${filePath}`
      );

      expect(mockLogger.error).toHaveBeenCalledWith('El archivo no existe', { filePath });
      expect(mockFs.promises.readFile).not.toHaveBeenCalled();
    });

    it('debería lanzar error si la lectura del archivo falla', async () => {
      const filePath = '/ruta/al/archivo.txt';
      const readError = new Error('Error de lectura del archivo');
      
      mockFs.existsSync.mockReturnValue(true);
      mockFs.promises.readFile = jest.fn().mockRejectedValue(readError);

      await expect(FileReaderService.readFile(filePath)).rejects.toThrow('Error de lectura del archivo');

      expect(mockLogger.error).toHaveBeenCalledWith('Error al leer el archivo', {
        filePath,
        error: 'Error de lectura del archivo'
      });
    });

    it('debería manejar errores que no son instancias de Error', async () => {
      const filePath = '/ruta/al/archivo.txt';
      const readError = 'Error de string';
      
      mockFs.existsSync.mockReturnValue(true);
      mockFs.promises.readFile = jest.fn().mockRejectedValue(readError);

      await expect(FileReaderService.readFile(filePath)).rejects.toBe('Error de string');

      expect(mockLogger.error).toHaveBeenCalledWith('Error al leer el archivo', {
        filePath,
        error: 'Error de string'
      });
    });

    it('debería usar encoding por defecto cuando no se proporciona', async () => {
      const filePath = '/ruta/al/archivo.txt';
      const fileContent = 'Contenido del archivo';
      
      mockFs.existsSync.mockReturnValue(true);
      mockFs.promises.readFile = jest.fn().mockResolvedValue(fileContent);

      await FileReaderService.readFile(filePath);

      expect(mockFs.promises.readFile).toHaveBeenCalledWith(filePath, {
        encoding: FILE_DEFAULT_ENCODING,
        flag: undefined
      });
    });

    it('debería usar encoding personalizado cuando se proporciona', async () => {
      const filePath = '/ruta/al/archivo.txt';
      const fileContent = 'Contenido del archivo';
      const options: FileReadOptions = {
        encoding: 'latin1'
      };
      
      mockFs.existsSync.mockReturnValue(true);
      mockFs.promises.readFile = jest.fn().mockResolvedValue(fileContent);

      await FileReaderService.readFile(filePath, options);

      expect(mockFs.promises.readFile).toHaveBeenCalledWith(filePath, {
        encoding: 'latin1',
        flag: undefined
      });
    });
  });

  describe('fileExists', () => {
    it('debería retornar true si el archivo existe', async () => {
      const filePath = '/ruta/al/archivo.txt';
      
      mockFs.existsSync.mockReturnValue(true);

      const result = await FileReaderService.fileExists(filePath);

      expect(result).toBe(true);
      expect(mockFs.existsSync).toHaveBeenCalledWith(filePath);
      expect(mockLogger.debug).toHaveBeenCalledWith('Verificando existencia del archivo', { filePath });
      expect(mockLogger.debug).toHaveBeenCalledWith('Resultado de verificación de existencia', {
        filePath,
        exists: true
      });
    });

    it('debería retornar false si el archivo no existe', async () => {
      const filePath = '/ruta/al/archivo-inexistente.txt';
      
      mockFs.existsSync.mockReturnValue(false);

      const result = await FileReaderService.fileExists(filePath);

      expect(result).toBe(false);
      expect(mockFs.existsSync).toHaveBeenCalledWith(filePath);
      expect(mockLogger.debug).toHaveBeenCalledWith('Resultado de verificación de existencia', {
        filePath,
        exists: false
      });
    });

    it('debería retornar false si existeSync lanza un error', async () => {
      const filePath = '/ruta/al/archivo.txt';
      const existsError = new Error('Error al verificar existencia');
      
      mockFs.existsSync.mockImplementation(() => {
        throw existsError;
      });

      const result = await FileReaderService.fileExists(filePath);

      expect(result).toBe(false);
      expect(mockLogger.error).toHaveBeenCalledWith('Error al verificar existencia del archivo', {
        filePath,
        error: 'Error al verificar existencia'
      });
    });

    it('debería manejar errores que no son instancias de Error en fileExists', async () => {
      const filePath = '/ruta/al/archivo.txt';
      const existsError = 'Error de string';
      
      mockFs.existsSync.mockImplementation(() => {
        throw existsError;
      });

      const result = await FileReaderService.fileExists(filePath);

      expect(result).toBe(false);
      expect(mockLogger.error).toHaveBeenCalledWith('Error al verificar existencia del archivo', {
        filePath,
        error: 'Error de string'
      });
    });
  });

  describe('constantes y tipos', () => {
    it('debería tener el encoding por defecto configurado', () => {
      expect(FILE_DEFAULT_ENCODING).toBeDefined();
      expect(typeof FILE_DEFAULT_ENCODING).toBe('string');
    });

    it('debería exportar los tipos correctamente', () => {
      // Verificar que los tipos están disponibles
      const options: FileReadOptions = {
        encoding: 'utf8',
        flag: 'r'
      };
      
      const fileInfo: FileInfo = {
        name: 'archivo.txt',
        path: '/ruta/al/archivo.txt',
        size: 1024,
        extension: '.txt',
        lastModified: new Date()
      };

      expect(options.encoding).toBe('utf8');
      expect(options.flag).toBe('r');
      expect(fileInfo.name).toBe('archivo.txt');
      expect(fileInfo.size).toBe(1024);
    });
  });

  describe('integración', () => {
    it('debería manejar el flujo completo de verificación y lectura', async () => {
      const filePath = '/ruta/al/archivo.txt';
      const fileContent = 'Contenido del archivo';
      
      // Mock para verificación de existencia
      mockFs.existsSync.mockReturnValue(true);
      mockFs.promises.readFile = jest.fn().mockResolvedValue(fileContent);

      // Verificar que existe
      const exists = await FileReaderService.fileExists(filePath);
      expect(exists).toBe(true);

      // Leer el archivo
      const content = await FileReaderService.readFile(filePath);
      expect(content).toBe(fileContent);

      // Verificar que los logs se llamaron correctamente
      expect(mockLogger.debug).toHaveBeenCalledWith('Verificando existencia del archivo', { filePath });
      expect(mockLogger.info).toHaveBeenCalledWith('Iniciando lectura de archivo', {
        filePath,
        options: undefined
      });
    });

    it('debería manejar el caso donde el archivo no existe en el flujo completo', async () => {
      const filePath = '/ruta/al/archivo-inexistente.txt';
      
      mockFs.existsSync.mockReturnValue(false);

      // Verificar que no existe
      const exists = await FileReaderService.fileExists(filePath);
      expect(exists).toBe(false);

      // Intentar leer el archivo debería fallar
      await expect(FileReaderService.readFile(filePath)).rejects.toThrow(
        `El archivo no existe: ${filePath}`
      );
    });
  });

  describe('casos edge', () => {
    it('debería manejar archivo vacío', async () => {
      const filePath = '/ruta/al/archivo-vacio.txt';
      const fileContent = '';
      
      mockFs.existsSync.mockReturnValue(true);
      mockFs.promises.readFile = jest.fn().mockResolvedValue(fileContent);

      const result = await FileReaderService.readFile(filePath);

      expect(result).toBe('');
      expect(mockLogger.info).toHaveBeenCalledWith('Archivo leído exitosamente', {
        filePath,
        contentLength: 0,
        encoding: FILE_DEFAULT_ENCODING
      });
    });

    it('debería manejar archivo con contenido muy largo', async () => {
      const filePath = '/ruta/al/archivo-largo.txt';
      const fileContent = 'a'.repeat(10000); // 10KB de contenido
      
      mockFs.existsSync.mockReturnValue(true);
      mockFs.promises.readFile = jest.fn().mockResolvedValue(fileContent);

      const result = await FileReaderService.readFile(filePath);

      expect(result).toBe(fileContent);
      expect(result.length).toBe(10000);
      expect(mockLogger.info).toHaveBeenCalledWith('Archivo leído exitosamente', {
        filePath,
        contentLength: 10000,
        encoding: FILE_DEFAULT_ENCODING
      });
    });

    it('debería manejar rutas con caracteres especiales', async () => {
      const filePath = '/ruta/con/espacios y símbolos@#$%/archivo.txt';
      const fileContent = 'Contenido del archivo';
      
      mockFs.existsSync.mockReturnValue(true);
      mockFs.promises.readFile = jest.fn().mockResolvedValue(fileContent);

      const result = await FileReaderService.readFile(filePath);

      expect(result).toBe(fileContent);
      expect(mockFs.existsSync).toHaveBeenCalledWith(filePath);
      expect(mockFs.promises.readFile).toHaveBeenCalledWith(filePath, {
        encoding: FILE_DEFAULT_ENCODING,
        flag: undefined
      });
    });
  });
}); 
