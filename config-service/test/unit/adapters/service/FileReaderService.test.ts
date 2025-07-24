import path from 'path';
import FileReaderService from '../../../../src/adapters/service/FileReaderService';
import { STORAGE_PATH } from '../../../../src/domain/common/consts/Setup';
import { ERROR_MESSAGES } from '../../../../src/domain/exceptions/constants/ErrorMessages';
import { NotFoundException } from '../../../../src/domain/exceptions/core/NotFoundException';
import { SystemException } from '../../../../src/domain/exceptions/core/SystemException';
import { InputFile } from '../../../../src/domain/model/Input';
import Logger from '../../../../src/infra/Logger';
import { Encrypt } from '../../../../src/utils/Encrypt';
import FileReader from '../../../../src/utils/FileReaderUtil';

// Mock de las dependencias
jest.mock('../../../../src/utils/FileReaderUtil'); 
jest.mock('../../../../src/utils/Encrypt');
jest.mock('../../../../src/infra/Logger');
jest.mock('path');
jest.mock('../../../../src/domain/common/consts/Setup', () => ({
  STORAGE_PATH: '../storage',
}));

const mockedFileReader = FileReader as jest.Mocked<typeof FileReader>;
const mockedEncrypt = Encrypt as jest.MockedClass<typeof Encrypt>;
const mockedPath = path as jest.Mocked<typeof path>;
const mockedLogger = Logger as jest.Mocked<typeof Logger>;

describe('FileReaderService', () => {
  let fileReaderService: FileReaderService;
  let mockEncryptInstance: jest.Mocked<Encrypt>;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Crear mock de la instancia de Encrypt
    mockEncryptInstance = {
      encrypt: jest.fn(),
      ofuscarBase64: jest.fn(),
    } as any;

    // Mock del constructor de Encrypt
    mockedEncrypt.mockImplementation(() => mockEncryptInstance);
    
    // Mock de path.join y path.resolve
    mockedPath.join.mockReturnValue('/mock/path/file.txt');
    mockedPath.resolve.mockReturnValue('/absolute/mock/path/file.txt');
    
    // Crear instancia del servicio
    fileReaderService = new FileReaderService(mockEncryptInstance);
  });

  describe('constructor', () => {
    it('debería crear una instancia con Encrypt', () => {
      expect(mockedEncrypt).toHaveBeenCalled();
      expect(fileReaderService).toBeInstanceOf(FileReaderService);
    });

    it('debería usar la instancia de Encrypt proporcionada', () => {
      const customEncrypt = new Encrypt();
      const service = new FileReaderService(customEncrypt);
      expect(service).toBeInstanceOf(FileReaderService);
    });
  });

  describe('read', () => {
    const mockInput: InputFile = new InputFile('test-file.txt');
    const mockContent = 'contenido del archivo de prueba';
    const mockEncryptedContent = 'contenido-encriptado';
    const mockOfuscatedContent = 'contenido-ofuscado';

    it('debería leer un archivo exitosamente y retornar contenido ofuscado', async () => {
      // Configurar mocks
      mockedFileReader.fileExists.mockResolvedValue(true);
      mockedFileReader.readFile.mockResolvedValue(mockContent);
      mockEncryptInstance.encrypt.mockResolvedValue(mockEncryptedContent);
      mockEncryptInstance.ofuscarBase64.mockReturnValue(mockOfuscatedContent);

      // Ejecutar método
      const result = await fileReaderService.read(mockInput);

      // Verificar llamadas
      expect(mockedPath.join).toHaveBeenCalledWith(expect.any(String), `${STORAGE_PATH}/${mockInput.filename}`);
      expect(mockedPath.resolve).toHaveBeenCalledWith('/mock/path/file.txt');
      expect(mockedFileReader.fileExists).toHaveBeenCalledWith('/mock/path/file.txt');
      expect(mockedFileReader.readFile).toHaveBeenCalledWith('/mock/path/file.txt');
      expect(mockEncryptInstance.encrypt).toHaveBeenCalledWith(mockContent);
      expect(mockEncryptInstance.ofuscarBase64).toHaveBeenCalledWith(mockEncryptedContent);

      // Verificar resultado
      expect(result).toBe(mockOfuscatedContent);

      // Verificar logs
      expect(mockedLogger.info).toHaveBeenCalledWith('Iniciando la lectura de archivo', { input: mockInput });
      expect(mockedLogger.info).toHaveBeenCalledWith('Verificación de existencia', {
        filePath: '/mock/path/file.txt',
        absolutePath: '/absolute/mock/path/file.txt',
        filename: mockInput.filename,
        existe: true,
      });
      expect(mockedLogger.info).toHaveBeenCalledWith('Contenido leído', {
        filePath: '/mock/path/file.txt',
        contenidoLength: mockContent.length,
        preview: mockContent.substring(0, 10) + '...',
      });
    });

    it('debería retornar NotFoundException cuando el archivo no existe', async () => {
      // Configurar mock para archivo inexistente
      mockedFileReader.fileExists.mockResolvedValue(false);

      // Ejecutar método
      const result = await fileReaderService.read(mockInput);

      // Verificar que se verificó la existencia
      expect(mockedFileReader.fileExists).toHaveBeenCalledWith('/mock/path/file.txt');
      
      // Verificar que NO se leyó el archivo
      expect(mockedFileReader.readFile).not.toHaveBeenCalled();
      expect(mockEncryptInstance.encrypt).not.toHaveBeenCalled();
      expect(mockEncryptInstance.ofuscarBase64).not.toHaveBeenCalled();

      // Verificar resultado
      expect(result).toBeInstanceOf(NotFoundException);

      // Verificar logs
      expect(mockedLogger.info).toHaveBeenCalledWith('Verificación de existencia', {
        filePath: '/mock/path/file.txt',
        absolutePath: '/absolute/mock/path/file.txt',
        filename: mockInput.filename,
        existe: false,
      });
    });

    it('debería retornar SystemException cuando hay error al verificar existencia', async () => {
      // Configurar mock para error en verificación
      mockedFileReader.fileExists.mockRejectedValue(new Error('Error de sistema'));

      // Ejecutar método
      const result = await fileReaderService.read(mockInput);

      // Verificar resultado
      expect(result).toBeInstanceOf(SystemException);
      expect((result as SystemException).message).toBe(ERROR_MESSAGES.INTERNAL_ERROR);

      // Verificar logs
      expect(mockedLogger.error).toHaveBeenCalledWith('Error en lectura del archivo', {
        error: 'Error de sistema',
      });
    });

    it('debería retornar SystemException cuando hay error al leer el archivo', async () => {
      // Configurar mocks
      mockedFileReader.fileExists.mockResolvedValue(true);
      mockedFileReader.readFile.mockRejectedValue(new Error('Error de lectura'));

      // Ejecutar método
      const result = await fileReaderService.read(mockInput);

      // Verificar resultado
      expect(result).toBeInstanceOf(SystemException);
      expect((result as SystemException).message).toBe(ERROR_MESSAGES.INTERNAL_ERROR);

      // Verificar que se intentó leer el archivo
      expect(mockedFileReader.readFile).toHaveBeenCalledWith('/mock/path/file.txt');

      // Verificar logs
      expect(mockedLogger.error).toHaveBeenCalledWith('Error en lectura del archivo', {
        error: 'Error de lectura',
      });
    });

    it('debería retornar SystemException cuando hay error en encriptación', async () => {
      // Configurar mocks
      mockedFileReader.fileExists.mockResolvedValue(true);
      mockedFileReader.readFile.mockResolvedValue(mockContent);
      mockEncryptInstance.encrypt.mockRejectedValue(new Error('Error de encriptación'));

      // Ejecutar método
      const result = await fileReaderService.read(mockInput);

      // Verificar resultado
      expect(result).toBeInstanceOf(SystemException);
      expect((result as SystemException).message).toBe(ERROR_MESSAGES.INTERNAL_ERROR);

      // Verificar que se intentó encriptar
      expect(mockEncryptInstance.encrypt).toHaveBeenCalledWith(mockContent);

      // Verificar logs
      expect(mockedLogger.error).toHaveBeenCalledWith('Error en lectura del archivo', {
        error: 'Error de encriptación',
      });
    });

    it('debería retornar SystemException cuando hay error en ofuscación', async () => {
      // Configurar mocks
      mockedFileReader.fileExists.mockResolvedValue(true);
      mockedFileReader.readFile.mockResolvedValue(mockContent);
      mockEncryptInstance.encrypt.mockResolvedValue(mockEncryptedContent);
      mockEncryptInstance.ofuscarBase64.mockImplementation(() => {
        throw new Error('Error de ofuscación');
      });

      // Ejecutar método
      const result = await fileReaderService.read(mockInput);

      // Verificar resultado
      expect(result).toBeInstanceOf(SystemException);
      expect((result as SystemException).message).toBe(ERROR_MESSAGES.INTERNAL_ERROR);

      // Verificar que se intentó ofuscar
      expect(mockEncryptInstance.ofuscarBase64).toHaveBeenCalledWith(mockEncryptedContent);

      // Verificar logs
      expect(mockedLogger.error).toHaveBeenCalledWith('Error en lectura del archivo', {
        error: 'Error de ofuscación',
      });
    });

    it('debería manejar error sin mensaje', async () => {
      // Configurar mocks
      mockedFileReader.fileExists.mockResolvedValue(true);
      mockedFileReader.readFile.mockRejectedValue({});

      // Ejecutar método
      const result = await fileReaderService.read(mockInput);

      // Verificar resultado
      expect(result).toBeInstanceOf(SystemException);
      expect((result as SystemException).message).toBe(ERROR_MESSAGES.INTERNAL_ERROR);

      // Verificar logs
      expect(mockedLogger.error).toHaveBeenCalledWith('Error en lectura del archivo', {
        error: expect.any(Object),
      });
    });

    it('debería manejar error con string', async () => {
      // Configurar mocks
      mockedFileReader.fileExists.mockResolvedValue(true);
      mockedFileReader.readFile.mockRejectedValue('Error string');

      // Ejecutar método
      const result = await fileReaderService.read(mockInput);

      // Verificar resultado
      expect(result).toBeInstanceOf(SystemException);
      expect((result as SystemException).message).toBe(ERROR_MESSAGES.INTERNAL_ERROR);

      // Verificar logs
      expect(mockedLogger.error).toHaveBeenCalledWith('Error en lectura del archivo', {
        error: 'Error string',
      });
    });

    it('debería manejar archivo con contenido vacío', async () => {
      // Configurar mocks
      const emptyContent = '';
      mockedFileReader.fileExists.mockResolvedValue(true);
      mockedFileReader.readFile.mockResolvedValue(emptyContent);
      mockEncryptInstance.encrypt.mockResolvedValue(mockEncryptedContent);
      mockEncryptInstance.ofuscarBase64.mockReturnValue(mockOfuscatedContent);

      // Ejecutar método
      const result = await fileReaderService.read(mockInput);

      // Verificar resultado
      expect(result).toBe(mockOfuscatedContent);

      // Verificar logs con contenido vacío
      expect(mockedLogger.info).toHaveBeenCalledWith('Contenido leído', {
        filePath: '/mock/path/file.txt',
        contenidoLength: 0,
        preview: '...',
      });
    });

    it('debería manejar archivo con contenido muy corto', async () => {
      // Configurar mocks
      const shortContent = 'abc';
      mockedFileReader.fileExists.mockResolvedValue(true);
      mockedFileReader.readFile.mockResolvedValue(shortContent);
      mockEncryptInstance.encrypt.mockResolvedValue(mockEncryptedContent);
      mockEncryptInstance.ofuscarBase64.mockReturnValue(mockOfuscatedContent);

      // Ejecutar método
      const result = await fileReaderService.read(mockInput);

      // Verificar resultado
      expect(result).toBe(mockOfuscatedContent);

      // Verificar logs con contenido corto
      expect(mockedLogger.info).toHaveBeenCalledWith('Contenido leído', {
        filePath: '/mock/path/file.txt',
        contenidoLength: 3,
        preview: 'abc...',
      });
    });
  });
}); 
