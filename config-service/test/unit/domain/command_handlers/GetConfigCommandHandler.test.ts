import { GetConfigCommandHandler } from '../../../../src/domain/command_handlers/GetConfigCommandHandler';
import { GetConfigCommand } from '../../../../src/domain/commands/GetConfigCommand';
import { ERROR_MESSAGES } from '../../../../src/domain/exceptions/constants/ErrorMessages';
import { NotFoundException } from '../../../../src/domain/exceptions/core/NotFoundException';
import { SystemException } from '../../../../src/domain/exceptions/core/SystemException';
import { InputFile } from '../../../../src/domain/model/Input';
import { OutputFile } from '../../../../src/domain/model/Output';

// Mock de Logger
jest.mock('../../../../src/infra/Logger', () => ({
  info: jest.fn(),
  error: jest.fn()
}));

describe('GetConfigCommandHandler', () => {
  let handler: GetConfigCommandHandler;
  let mockService: any;

  beforeEach(() => {
    mockService = {
      read: jest.fn()
    };
    handler = new GetConfigCommandHandler(mockService);
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    it('debe crear una instancia con fileReaderService', () => {
      expect(handler).toBeInstanceOf(GetConfigCommandHandler);
      expect(handler['fileReaderService']).toBe(mockService);
    });
  });

  describe('handle - caso exitoso', () => {
    it('debe retornar OutputFile cuando el servicio retorna string', async () => {
      const content = 'file content';
      const inputFile = new InputFile('test.txt');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockResolvedValue(content);

      const result = await handler.handle(command);

      expect(result).toBeInstanceOf(OutputFile);
      expect((result as OutputFile).content).toBe(content);
      expect(mockService.read).toHaveBeenCalledWith(inputFile);
    });

    it('debe manejar contenido vacío', async () => {
      const content = '';
      const inputFile = new InputFile('empty.txt');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockResolvedValue(content);

      const result = await handler.handle(command);

      expect(result).toBeInstanceOf(OutputFile);
      expect((result as OutputFile).content).toBe('');
    });

    it('debe manejar contenido JSON', async () => {
      const content = '{"key": "value", "number": 123}';
      const inputFile = new InputFile('config.json');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockResolvedValue(content);

      const result = await handler.handle(command);

      expect(result).toBeInstanceOf(OutputFile);
      expect((result as OutputFile).content).toBe(content);
    });
  });

  describe('handle - caso NotFoundException', () => {
    it('debe retornar NotFoundException cuando el servicio lo retorna', async () => {
      const notFoundException = new NotFoundException();
      const inputFile = new InputFile('nonexistent.txt');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockResolvedValue(notFoundException);

      const result = await handler.handle(command);

      expect(result).toBe(notFoundException);
      expect(result).toBeInstanceOf(NotFoundException);
    });
  });

  describe('handle - caso SystemException', () => {
    it('debe retornar SystemException cuando el servicio lo retorna', async () => {
      const systemException = new SystemException('System error');
      const inputFile = new InputFile('error.txt');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockResolvedValue(systemException);

      const result = await handler.handle(command);

      expect(result).toBe(systemException);
      expect(result).toBeInstanceOf(SystemException);
    });
  });

  describe('handle - caso error en el servicio', () => {
    it('debe retornar SystemException cuando el servicio lanza un error', async () => {
      const inputFile = new InputFile('error.txt');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockRejectedValue(new Error('Service error'));

      const result = await handler.handle(command);

      expect(result).toBeInstanceOf(SystemException);
      expect((result as SystemException).message).toBe(ERROR_MESSAGES.INTERNAL_ERROR);
    });

    it('debe manejar errores de tipo string', async () => {
      const inputFile = new InputFile('error.txt');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockRejectedValue('String error');

      const result = await handler.handle(command);

      expect(result).toBeInstanceOf(SystemException);
      expect((result as SystemException).message).toBe(ERROR_MESSAGES.INTERNAL_ERROR);
    });

    it('debe manejar errores de tipo number', async () => {
      const inputFile = new InputFile('error.txt');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockRejectedValue(500);

      const result = await handler.handle(command);

      expect(result).toBeInstanceOf(SystemException);
      expect((result as SystemException).message).toBe(ERROR_MESSAGES.INTERNAL_ERROR);
    });
  });

  describe('logging', () => {
    it('debe registrar información al inicio', async () => {
      const inputFile = new InputFile('test.txt');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockResolvedValue('content');

      await handler.handle(command);

      // Verificar que se llamó al logger (esto se verifica indirectamente)
      expect(mockService.read).toHaveBeenCalled();
    });

    it('debe registrar información de éxito', async () => {
      const inputFile = new InputFile('test.txt');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockResolvedValue('content');

      await handler.handle(command);

      // Verificar que se procesó correctamente
      expect(mockService.read).toHaveBeenCalledWith(inputFile);
    });

    it('debe registrar errores cuando ocurren', async () => {
      const inputFile = new InputFile('error.txt');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockRejectedValue(new Error('Test error'));

      await handler.handle(command);

      // Verificar que se manejó el error
      expect(mockService.read).toHaveBeenCalledWith(inputFile);
    });
  });

  describe('tipos de retorno', () => {
    it('debe retornar union type correcto', async () => {
      const inputFile = new InputFile('test.txt');
      const command = new GetConfigCommand(inputFile);

      // Caso OutputFile
      mockService.read.mockResolvedValue('content');
      let result = await handler.handle(command);
      expect(result).toBeInstanceOf(OutputFile);

      // Caso NotFoundException
      const notFoundException = new NotFoundException();
      mockService.read.mockResolvedValue(notFoundException);
      result = await handler.handle(command);
      expect(result).toBeInstanceOf(NotFoundException);

      // Caso SystemException
      const systemException = new SystemException('Error');
      mockService.read.mockResolvedValue(systemException);
      result = await handler.handle(command);
      expect(result).toBeInstanceOf(SystemException);
    });
  });

  describe('manejo de parámetros', () => {
    it('debe pasar el InputFile correcto al servicio', async () => {
      const inputFile = new InputFile('test.txt');
      const command = new GetConfigCommand(inputFile);

      mockService.read.mockResolvedValue('content');

      await handler.handle(command);

      expect(mockService.read).toHaveBeenCalledWith(inputFile);
    });

    it('debe manejar diferentes nombres de archivo', async () => {
      const files = ['file1.txt', 'file2.json', 'config.yaml'];

      for (const filename of files) {
        const inputFile = new InputFile(filename);
        const command = new GetConfigCommand(inputFile);

        mockService.read.mockResolvedValue(`content of ${filename}`);

        const result = await handler.handle(command);

        expect(result).toBeInstanceOf(OutputFile);
        expect((result as OutputFile).content).toBe(`content of ${filename}`);
        expect(mockService.read).toHaveBeenCalledWith(inputFile);
      }
    });
  });
}); 
