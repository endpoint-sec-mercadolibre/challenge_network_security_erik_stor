import { Request, Response, NextFunction } from 'express';
import Logger from '../../../../../src/infra/Logger';

// Mock de las dependencias
jest.mock('../../../../../src/infra/Logger');

// Mock de la clase Encrypt usando __mocks__
jest.mock('../../../../../src/utils/Encrypt', () => {
  return {
    Encrypt: jest.fn().mockImplementation(() => ({
      desofuscarBase64: jest.fn(),
      decrypt: jest.fn(),
    }))
  };
});

// Importar después del mock para evitar conflictos
const { extractFilename } = require('../../../../../src/entrypoints/api/middlewares/extractFilename');
const { Encrypt } = require('../../../../../src/utils/Encrypt');

describe('extractFilename Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;
  let mockLogger: jest.Mocked<typeof Logger>;
  let encryptInstance: any;

  beforeAll(() => {
    // Asegurar que los mocks están configurados correctamente
    jest.clearAllMocks();
  });

  beforeEach(() => {
    // Limpiar todos los mocks
    jest.clearAllMocks();

    // Crear una nueva instancia mockeada para cada test
    encryptInstance = {
      desofuscarBase64: jest.fn(),
      decrypt: jest.fn(),
    };

    // Mockear el constructor para que retorne nuestra instancia
    (Encrypt as jest.MockedClass<typeof Encrypt>).mockImplementation(() => encryptInstance);

    // Configurar mock de Logger
    mockLogger = Logger as jest.Mocked<typeof Logger>;

    // Configurar request mock
    mockRequest = {
      method: 'GET',
      path: '/config/test-file',
      ip: '127.0.0.1',
      get: jest.fn().mockReturnValue('Mozilla/5.0'),
      params: {},
    };

    // Configurar response mock
    mockResponse = {};

    // Configurar next function mock
    mockNext = jest.fn();
  });

  describe('Casos exitosos', () => {
    it('debería extraer y desencriptar correctamente un filename válido', async () => {
      // Arrange
      const originalFilename = 'test-encrypted-filename';
      // Crear un base64 válido que simule el formato esperado por decrypt
      const base64Decoded = 'dGVzdC1iYXNlNjQtZGVjb2RlZA=='; // "test-base64-decoded" en base64
      const decryptedFilename = 'test-file.txt';

      mockRequest.params = { filename: originalFilename };
      
      encryptInstance.desofuscarBase64.mockReturnValue(base64Decoded);
      encryptInstance.decrypt.mockResolvedValue(decryptedFilename);

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockLogger.info).toHaveBeenCalledWith('Inicio de proceso de extracción de nombre de archivo', {
        method: 'GET',
        path: '/config/test-file',
        ip: '127.0.0.1',
        userAgent: 'Mozilla/5.0',
        pathParameters: { filename: decryptedFilename },
        originalFilename: originalFilename
      });

      expect(mockLogger.info).toHaveBeenCalledWith('Procesando filename:', { originalFilename });
      expect(mockLogger.info).toHaveBeenCalledWith('Después de URL decode:', { urlDecoded: originalFilename });
      expect(mockLogger.info).toHaveBeenCalledWith('Filename desencriptado:', { decryptedFilename });

      expect(encryptInstance.desofuscarBase64).toHaveBeenCalledWith(originalFilename);
      expect(encryptInstance.decrypt).toHaveBeenCalledWith(base64Decoded);
      expect(mockRequest.params!.filename).toBe(decryptedFilename);
      expect(mockNext).toHaveBeenCalled();
    });

    it('debería manejar filename con caracteres especiales en URL encoding', async () => {
      // Arrange
      const originalFilename = 'test%20file%2Bwith%20spaces.txt';
      const urlDecoded = 'test file+with spaces.txt';
      const base64Decoded = 'dGVzdC1iYXNlNjQtZGVjb2RlZA=='; // "test-base64-decoded" en base64
      const decryptedFilename = 'test file with spaces.txt';

      mockRequest.params = { filename: originalFilename };
      
      encryptInstance.desofuscarBase64.mockReturnValue(base64Decoded);
      encryptInstance.decrypt.mockResolvedValue(decryptedFilename);

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockLogger.info).toHaveBeenCalledWith('Después de URL decode:', { urlDecoded });
      expect(encryptInstance.desofuscarBase64).toHaveBeenCalledWith(urlDecoded);
      expect(mockRequest.params!.filename).toBe(decryptedFilename);
      expect(mockNext).toHaveBeenCalled();
    });
  });

  describe('Casos de filename vacío o no definido', () => {
    it('debería manejar filename vacío', async () => {
      // Arrange
      mockRequest.params = { filename: '' };

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockLogger.error).toHaveBeenCalledWith('Filename está vacío o no definido');
      expect(mockRequest.params!.filename).toBe('');
      expect(mockNext).toHaveBeenCalled();
      expect(encryptInstance.desofuscarBase64).not.toHaveBeenCalled();
      expect(encryptInstance.decrypt).not.toHaveBeenCalled();
    });

    it('debería manejar filename undefined', async () => {
      // Arrange
      mockRequest.params = { filename: undefined as any };

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockLogger.error).toHaveBeenCalledWith('Filename está vacío o no definido');
      expect(mockRequest.params!.filename).toBe('');
      expect(mockNext).toHaveBeenCalled();
      expect(encryptInstance.desofuscarBase64).not.toHaveBeenCalled();
      expect(encryptInstance.decrypt).not.toHaveBeenCalled();
    });

    it('debería manejar params sin filename', async () => {
      // Arrange
      mockRequest.params = {};

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockLogger.error).toHaveBeenCalledWith('Filename está vacío o no definido');
      expect(mockRequest.params!.filename).toBe('');
      expect(mockNext).toHaveBeenCalled();
      expect(encryptInstance.desofuscarBase64).not.toHaveBeenCalled();
      expect(encryptInstance.decrypt).not.toHaveBeenCalled();
    });

    it('debería manejar params undefined', async () => {
      // Arrange
      mockRequest.params = undefined as any;

      // Act & Assert
      // Este caso debería fallar porque el middleware asume que req.params existe
      await expect(extractFilename(mockRequest as Request, mockResponse as Response, mockNext))
        .rejects.toThrow();
    });
  });

  describe('Manejo de errores', () => {
    it('debería manejar error en desofuscarBase64', async () => {
      // Arrange
      const originalFilename = 'test-filename';
      const error = new Error('Error en desofuscarBase64');

      mockRequest.params = { filename: originalFilename };
      encryptInstance.desofuscarBase64.mockImplementation(() => {
        throw error;
      });

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockLogger.error).toHaveBeenCalledWith('Error general al desencriptar el nombre de archivo', {
        error: 'Error en desofuscarBase64',
        originalFilename: originalFilename
      });
      expect(mockRequest.params!.filename).toBe(originalFilename);
      expect(mockNext).toHaveBeenCalled();
      expect(encryptInstance.decrypt).not.toHaveBeenCalled();
    });

    it('debería manejar error en decrypt', async () => {
      // Arrange
      const originalFilename = 'test-filename';
      const base64Decoded = 'test-base64-decoded';
      const error = new Error('Error en decrypt');

      mockRequest.params = { filename: originalFilename };
      
      encryptInstance.desofuscarBase64.mockReturnValue(base64Decoded);
      encryptInstance.decrypt.mockRejectedValue(error);

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockLogger.error).toHaveBeenCalledWith('Error general al desencriptar el nombre de archivo', {
        error: 'Error en decrypt',
        originalFilename: originalFilename
      });
      expect(mockRequest.params!.filename).toBe(originalFilename);
      expect(mockNext).toHaveBeenCalled();
    });

    it('debería manejar error no-Error object', async () => {
      // Arrange
      const originalFilename = 'test-filename';
      const error = 'String error';

      mockRequest.params = { filename: originalFilename };
      encryptInstance.desofuscarBase64.mockImplementation(() => {
        throw error;
      });

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockLogger.error).toHaveBeenCalledWith('Error general al desencriptar el nombre de archivo', {
        error: 'String error',
        originalFilename: originalFilename
      });
      expect(mockRequest.params!.filename).toBe(originalFilename);
      expect(mockNext).toHaveBeenCalled();
    });

    it('debería manejar error con filename undefined en catch', async () => {
      // Arrange
      const error = new Error('Test error');

      mockRequest.params = undefined as any;
      encryptInstance.desofuscarBase64.mockImplementation(() => {
        throw error;
      });

      // Act & Assert
      // Este caso debería fallar porque el middleware asume que req.params existe
      await expect(extractFilename(mockRequest as Request, mockResponse as Response, mockNext))
        .rejects.toThrow();
    });
  });

  describe('Logging completo', () => {
    it('debería registrar toda la información del request correctamente', async () => {
      // Arrange
      const originalFilename = 'test-filename';
      const decryptedFilename = 'test-file.txt';

      mockRequest = {
        ...mockRequest,
        params: { filename: originalFilename },
        method: 'POST',
        path: '/api/config/special-file',
        ip: '192.168.1.100',
        get: jest.fn().mockReturnValue('Custom-Agent/1.0'),
      };
      
      encryptInstance.desofuscarBase64.mockReturnValue('ZGVjb2RlZA=='); // "decoded" en base64
      encryptInstance.decrypt.mockResolvedValue(decryptedFilename);

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockLogger.info).toHaveBeenCalledWith('Inicio de proceso de extracción de nombre de archivo', {
        method: 'POST',
        path: '/api/config/special-file',
        ip: '192.168.1.100',
        userAgent: 'Custom-Agent/1.0',
        pathParameters: { filename: decryptedFilename },
        originalFilename: originalFilename
      });
    });

    it('debería registrar el proceso paso a paso', async () => {
      // Arrange
      const originalFilename = 'test-filename';
      const base64Decoded = 'dGVzdC1iYXNlNjQtZGVjb2RlZA=='; // "test-base64-decoded" en base64
      const decryptedFilename = 'test-file.txt';

      mockRequest.params = { filename: originalFilename };
      
      encryptInstance.desofuscarBase64.mockReturnValue(base64Decoded);
      encryptInstance.decrypt.mockResolvedValue(decryptedFilename);

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      // Verificar que se llamaron todos los logs esperados, sin importar el orden exacto
      expect(mockLogger.info).toHaveBeenCalledWith('Inicio de proceso de extracción de nombre de archivo', expect.any(Object));
      expect(mockLogger.info).toHaveBeenCalledWith('Procesando filename:', { originalFilename });
      expect(mockLogger.info).toHaveBeenCalledWith('Después de URL decode:', { urlDecoded: originalFilename });
      expect(mockLogger.info).toHaveBeenCalledWith('Filename desencriptado:', { decryptedFilename });
    });
  });

  describe('Integración con Express', () => {
    it('debería llamar a next() en todos los casos', async () => {
      // Arrange
      mockRequest.params = { filename: 'test' };
      encryptInstance.desofuscarBase64.mockReturnValue('ZGVjb2RlZA=='); // "decoded" en base64
      encryptInstance.decrypt.mockResolvedValue('decrypted');

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockNext).toHaveBeenCalledTimes(1);
    });

    it('debería llamar a next() incluso con error', async () => {
      // Arrange
      mockRequest.params = { filename: 'test' };
      encryptInstance.desofuscarBase64.mockImplementation(() => {
        throw new Error('Test error');
      });

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockNext).toHaveBeenCalledTimes(1);
    });

    it('debería llamar a next() con filename vacío', async () => {
      // Arrange
      mockRequest.params = { filename: '' };

      // Act
      await extractFilename(mockRequest as Request, mockResponse as Response, mockNext);

      // Assert
      expect(mockNext).toHaveBeenCalledTimes(1);
    });
  });
});
