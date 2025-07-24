import { IFileReaderService } from '../../../../src/domain/ports/IFileReaderService';
import { InputFile } from '../../../../src/domain/model/Input';
import { NotFoundException } from '../../../../src/domain/exceptions/core/NotFoundException';
import { SystemException } from '../../../../src/domain/exceptions/core/SystemException';

describe('IFileReaderService Interface', () => {
  describe('estructura de la interfaz', () => {
    it('debe definir el método read', () => {
      // Crear un mock que implemente la interfaz
      const mockService: IFileReaderService = {
        read: jest.fn().mockResolvedValue('test content')
      };
      
      expect(mockService).toHaveProperty('read');
      expect(typeof mockService.read).toBe('function');
    });

    it('debe permitir llamar al método read', async () => {
      const mockService: IFileReaderService = {
        read: jest.fn().mockResolvedValue('test content')
      };
      
      const input = new InputFile('test.txt');
      const result = await mockService.read(input);
      
      expect(result).toBe('test content');
      expect(mockService.read).toHaveBeenCalledWith(input);
    });
  });

  describe('tipos de retorno', () => {
    it('debe permitir retorno de string', async () => {
      const mockService: IFileReaderService = {
        read: jest.fn().mockResolvedValue('file content')
      };
      
      const input = new InputFile('test.txt');
      const result = await mockService.read(input);
      
      expect(typeof result).toBe('string');
      expect(result).toBe('file content');
    });

    it('debe permitir retorno de NotFoundException', async () => {
      const notFoundException = new NotFoundException();
      const mockService: IFileReaderService = {
        read: jest.fn().mockResolvedValue(notFoundException)
      };
      
      const input = new InputFile('nonexistent.txt');
      const result = await mockService.read(input);
      
      expect(result).toBeInstanceOf(NotFoundException);
      expect(result).toBe(notFoundException);
    });

    it('debe permitir retorno de SystemException', async () => {
      const systemException = new SystemException('System error');
      const mockService: IFileReaderService = {
        read: jest.fn().mockResolvedValue(systemException)
      };
      
      const input = new InputFile('test.txt');
      const result = await mockService.read(input);
      
      expect(result).toBeInstanceOf(SystemException);
      expect(result).toBe(systemException);
    });
  });

  describe('parámetros de entrada', () => {
    it('debe aceptar InputFile como parámetro', async () => {
      const mockService: IFileReaderService = {
        read: jest.fn().mockResolvedValue('content')
      };
      
      const input = new InputFile('test.txt');
      await mockService.read(input);
      
      expect(mockService.read).toHaveBeenCalledWith(input);
    });

    it('debe manejar diferentes nombres de archivo', async () => {
      const mockService: IFileReaderService = {
        read: jest.fn().mockImplementation((input: InputFile) => {
          return Promise.resolve(`content of ${input.filename}`);
        })
      };
      
      const files = [
        new InputFile('file1.txt'),
        new InputFile('file2.json'),
        new InputFile('config.yaml')
      ];
      
      for (const file of files) {
        const result = await mockService.read(file);
        expect(result).toBe(`content of ${file.filename}`);
      }
    });
  });

  describe('comportamiento asíncrono', () => {
    it('debe retornar una Promise', () => {
      const mockService: IFileReaderService = {
        read: jest.fn().mockResolvedValue('content')
      };
      
      const input = new InputFile('test.txt');
      const result = mockService.read(input);
      
      expect(result).toBeInstanceOf(Promise);
    });

    it('debe resolver la Promise correctamente', async () => {
      const mockService: IFileReaderService = {
        read: jest.fn().mockResolvedValue('resolved content')
      };
      
      const input = new InputFile('test.txt');
      const result = await mockService.read(input);
      
      expect(result).toBe('resolved content');
    });

    it('debe manejar errores asíncronos', async () => {
      const mockService: IFileReaderService = {
        read: jest.fn().mockRejectedValue(new Error('Async error'))
      };
      
      const input = new InputFile('test.txt');
      
      await expect(mockService.read(input)).rejects.toThrow('Async error');
    });
  });

  describe('implementaciones específicas', () => {
    it('debe permitir implementación que siempre retorna string', async () => {
      const service: IFileReaderService = {
        read: async (input: InputFile) => {
          return `Content of ${input.filename}`;
        }
      };
      
      const input = new InputFile('test.txt');
      const result = await service.read(input);
      
      expect(result).toBe('Content of test.txt');
    });

    it('debe permitir implementación que retorna NotFoundException', async () => {
      const service: IFileReaderService = {
        read: async (input: InputFile) => {
          if (input.filename === 'nonexistent.txt') {
            return new NotFoundException();
          }
          return 'content';
        }
      };
      
      const input = new InputFile('nonexistent.txt');
      const result = await service.read(input);
      
      expect(result).toBeInstanceOf(NotFoundException);
    });

    it('debe permitir implementación que retorna SystemException', async () => {
      const service: IFileReaderService = {
        read: async (input: InputFile) => {
          if (input.filename === 'error.txt') {
            return new SystemException('System error occurred');
          }
          return 'content';
        }
      };
      
      const input = new InputFile('error.txt');
      const result = await service.read(input);
      
      expect(result).toBeInstanceOf(SystemException);
      expect((result as SystemException).message).toBe('System error occurred');
    });
  });

  describe('validación de tipos', () => {
    it('debe requerir que read sea una función asíncrona', () => {
      const mockService: IFileReaderService = {
        read: jest.fn().mockResolvedValue('content')
      };
      
      expect(typeof mockService.read).toBe('function');
    });

    it('debe permitir union types de retorno', async () => {
      const mockService: IFileReaderService = {
        read: jest.fn().mockImplementation((input: InputFile) => {
          if (input.filename === 'notfound.txt') {
            return Promise.resolve(new NotFoundException());
          } else if (input.filename === 'error.txt') {
            return Promise.resolve(new SystemException('Error'));
          } else {
            return Promise.resolve('content');
          }
        })
      };
      
      const notFoundInput = new InputFile('notfound.txt');
      const errorInput = new InputFile('error.txt');
      const successInput = new InputFile('success.txt');
      
      const notFoundResult = await mockService.read(notFoundInput);
      const errorResult = await mockService.read(errorInput);
      const successResult = await mockService.read(successInput);
      
      expect(notFoundResult).toBeInstanceOf(NotFoundException);
      expect(errorResult).toBeInstanceOf(SystemException);
      expect(successResult).toBe('content');
    });
  });
}); 
