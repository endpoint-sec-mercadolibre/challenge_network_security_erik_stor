import { plainToInstance } from 'class-transformer';
import { ValidationError } from 'class-validator';

import { GetConfigCommandHandler } from '../../../../src/domain/command_handlers/GetConfigCommandHandler';
import { SUCCESS_MESSAGES } from '../../../../src/domain/common/consts/SuccessMessages';
import { ERROR_MESSAGES } from '../../../../src/domain/exceptions/constants/ErrorMessages';
import { NotFoundException } from '../../../../src/domain/exceptions/core/NotFoundException';
import { SystemException } from '../../../../src/domain/exceptions/core/SystemException';
import { InputFile } from '../../../../src/domain/model/Input';
import { OutputFile } from '../../../../src/domain/model/Output';
import { ConfigController } from '../../../../src/entrypoints/api/GetConfigController';

// Mock de las dependencias
jest.mock('class-transformer');
jest.mock('class-validator');
jest.mock('../../../../src/infra/Logger', () => ({
  info: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn(),
  success: jest.fn()
}));
jest.mock('../../../../src/utils/ErrorExtractor');

const mockPlainToInstance = plainToInstance as jest.MockedFunction<typeof plainToInstance>;
const mockValidate = require('class-validator').validate as jest.MockedFunction<typeof import('class-validator').validate>;
const mockLogger = require('../../../../src/infra/Logger');
const mockErrorExtractor = require('../../../../src/utils/ErrorExtractor');

describe('ConfigController', () => {
  let configController: ConfigController;
  let mockGetConfigCommandHandler: jest.Mocked<GetConfigCommandHandler>;

  beforeEach(() => {
    // Limpiar todos los mocks
    jest.clearAllMocks();

    // Mock del command handler
    mockGetConfigCommandHandler = {
      handle: jest.fn()
    } as any;

    // Mock del logger
    mockLogger.info = jest.fn();
    mockLogger.error = jest.fn();

    // Mock de ErrorExtractor
    mockErrorExtractor.extractValidationErrors = jest.fn();
    mockErrorExtractor.flattenErrorMessages = jest.fn();

    // Crear instancia del controlador
    configController = new ConfigController(mockGetConfigCommandHandler);
  });

  describe('handle', () => {
    const mockRequest = {
      method: 'GET',
      path: '/config/test.txt',
      ip: '127.0.0.1',
      get: jest.fn().mockReturnValue('Mozilla/5.0'),
      params: { filename: 'test.txt' }
    };

    describe('caso exitoso', () => {
      it('debe procesar correctamente una solicitud válida y retornar respuesta exitosa', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const mockOutputFile = new OutputFile('contenido del archivo');
        const expectedResponse = {
          statusCode: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
          },
          body: JSON.stringify({
            message: SUCCESS_MESSAGES.READ_FILE,
            data: { content: 'contenido del archivo' }
          })
        };

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue([]);
        mockGetConfigCommandHandler.handle.mockResolvedValue(mockOutputFile);

        // Act
        const result = await configController.handle(mockRequest);

        // Assert
        expect(mockPlainToInstance).toHaveBeenCalledWith(InputFile, { filename: 'test.txt' });
        expect(mockValidate).toHaveBeenCalledWith(mockInputFile);
        expect(mockGetConfigCommandHandler.handle).toHaveBeenCalledWith(
          expect.objectContaining({
            request: mockInputFile
          })
        );
        expect(result).toEqual(expectedResponse);
        expect(mockLogger.info).toHaveBeenCalledWith('Inicio de proceso de validación de datos', {
          method: 'GET',
          path: '/config/test.txt',
          ip: '127.0.0.1',
          userAgent: 'Mozilla/5.0',
          pathParameters: { filename: 'test.txt' }
        });
        expect(mockLogger.info).toHaveBeenCalledWith('Datos validados correctamente', {
          path: 'test.txt'
        });
        expect(mockLogger.info).toHaveBeenCalledWith('Ejecutando comando:', {
          path: 'test.txt'
        });
      });
    });

    describe('errores de validación', () => {
      it('debe retornar InvalidDataException cuando hay errores de validación', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const validationErrors: ValidationError[] = [
          {
            property: 'filename',
            constraints: {
              isNotEmpty: 'El nombre del archivo es requerido'
            },
            children: []
          }
        ];

        const extractedErrors = {
          errors: [{ field: 'filename', messages: ['El nombre del archivo es requerido'] }],
          hasErrors: true,
          errorCount: 1
        };

        const flattenedErrors = ['El nombre del archivo es requerido'];

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue(validationErrors);
        mockErrorExtractor.extractValidationErrors.mockReturnValue(extractedErrors);
        mockErrorExtractor.flattenErrorMessages.mockReturnValue(flattenedErrors);

        // Act
        const result = await configController.handle(mockRequest);

        // Assert
        expect(mockValidate).toHaveBeenCalledWith(mockInputFile);
        expect(mockErrorExtractor.extractValidationErrors).toHaveBeenCalledWith(validationErrors);
        expect(mockErrorExtractor.flattenErrorMessages).toHaveBeenCalledWith(extractedErrors);
        expect(mockLogger.error).toHaveBeenCalledWith('Errores de validación:', JSON.stringify(validationErrors));
        expect(mockLogger.error).toHaveBeenCalledWith('Mensajes de error:', JSON.stringify(flattenedErrors));
        expect(result).toEqual(expect.objectContaining({
          statusCode: 400,
          body: expect.stringContaining('Los datos de entrada no son válidos')
        }));
      });

      it('debe manejar múltiples errores de validación', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const validationErrors: ValidationError[] = [
          {
            property: 'filename',
            constraints: {
              isNotEmpty: 'El nombre del archivo es requerido',
              isString: 'El nombre del archivo debe ser una cadena'
            },
            children: []
          }
        ];

        const extractedErrors = {
          errors: [{
            field: 'filename',
            messages: ['El nombre del archivo es requerido', 'El nombre del archivo debe ser una cadena']
          }],
          hasErrors: true,
          errorCount: 2
        };

        const flattenedErrors = ['El nombre del archivo es requerido', 'El nombre del archivo debe ser una cadena'];

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue(validationErrors);
        mockErrorExtractor.extractValidationErrors.mockReturnValue(extractedErrors);
        mockErrorExtractor.flattenErrorMessages.mockReturnValue(flattenedErrors);

        // Act
        const result = await configController.handle(mockRequest);

        // Assert
        expect(result).toEqual(expect.objectContaining({
          statusCode: 400,
          body: expect.stringContaining('Los datos de entrada no son válidos')
        }));
      });
    });

    describe('errores del command handler', () => {
      it('debe retornar NotFoundException cuando el command handler retorna NotFoundException', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const notFoundException = new NotFoundException();

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue([]);
        mockGetConfigCommandHandler.handle.mockResolvedValue(notFoundException);

        // Act
        const result = await configController.handle(mockRequest);

        // Assert
        expect(result).toEqual(notFoundException.toResponse());
      });

      it('debe retornar SystemException cuando el command handler retorna SystemException', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const systemException = new SystemException('Error del sistema');

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue([]);
        mockGetConfigCommandHandler.handle.mockResolvedValue(systemException);

        // Act
        const result = await configController.handle(mockRequest);

        // Assert
        expect(result).toEqual(systemException.toResponse());
      });

             it('debe retornar cualquier otro resultado que no sea OutputFile', async () => {
         // Arrange
         const mockInputFile = new InputFile('test.txt');
         const mockOtherResult = {
           toResponse: jest.fn().mockReturnValue({
             statusCode: 418,
             body: JSON.stringify({ message: 'I\'m a teapot' })
           })
         } as any;

         mockPlainToInstance.mockReturnValue(mockInputFile as any);
         mockValidate.mockResolvedValue([]);
         mockGetConfigCommandHandler.handle.mockResolvedValue(mockOtherResult);

         // Act
         const result = await configController.handle(mockRequest);

         // Assert
         expect(mockOtherResult.toResponse).toHaveBeenCalled();
         expect(result).toEqual({
           statusCode: 418,
           body: JSON.stringify({ message: 'I\'m a teapot' })
         });
       });

       it('debe retornar resultado cuando el command handler retorna un objeto que no es OutputFile', async () => {
         // Arrange
         const mockInputFile = new InputFile('test.txt');
         const mockOtherResult = {
           toResponse: jest.fn().mockReturnValue({
             statusCode: 200,
             body: JSON.stringify({ message: 'Otro tipo de respuesta' })
           })
         };

         mockPlainToInstance.mockReturnValue(mockInputFile as any);
         mockValidate.mockResolvedValue([]);
         mockGetConfigCommandHandler.handle.mockResolvedValue(mockOtherResult as any);

         // Act
         const result = await configController.handle(mockRequest);

         // Assert
         expect(mockOtherResult.toResponse).toHaveBeenCalled();
         expect(result).toEqual({
           statusCode: 200,
           body: JSON.stringify({ message: 'Otro tipo de respuesta' })
         });
       });

       it('debe retornar resultado cuando el command handler retorna una clase personalizada', async () => {
         // Arrange
         class CustomResponse {
           toResponse() {
             return {
               statusCode: 201,
               body: JSON.stringify({ message: 'Respuesta personalizada' })
             };
           }
         }

         const mockInputFile = new InputFile('test.txt');
         const customResult = new CustomResponse();

         mockPlainToInstance.mockReturnValue(mockInputFile as any);
         mockValidate.mockResolvedValue([]);
         mockGetConfigCommandHandler.handle.mockResolvedValue(customResult as any);

         // Act
         const result = await configController.handle(mockRequest);

         // Assert
         expect(result).toEqual({
           statusCode: 201,
           body: JSON.stringify({ message: 'Respuesta personalizada' })
         });
       });


    });

    describe('errores del sistema', () => {
      it('debe manejar errores inesperados y retornar SystemException', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const unexpectedError = new Error('Error inesperado');

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue([]);
        mockGetConfigCommandHandler.handle.mockRejectedValue(unexpectedError);

        // Act
        const result = await configController.handle(mockRequest);

        // Assert
        expect(mockLogger.error).toHaveBeenCalledWith('Error en el controlador:', {
          error: 'Error inesperado',
          stack: unexpectedError.stack
        });
        expect(result).toEqual(expect.objectContaining({
          statusCode: 500,
          body: expect.stringContaining(ERROR_MESSAGES.INTERNAL_ERROR)
        }));
      });

      it('debe manejar errores que no son instancias de BaseException', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const stringError = 'Error como string';

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue([]);
        mockGetConfigCommandHandler.handle.mockRejectedValue(stringError);

        // Act
        const result = await configController.handle(mockRequest);

        // Assert
        expect(mockLogger.error).toHaveBeenCalledWith('Error en el controlador:', {
          error: undefined,
          stack: undefined
        });
        expect(result).toEqual(expect.objectContaining({
          statusCode: 500,
          body: expect.stringContaining(ERROR_MESSAGES.INTERNAL_ERROR)
        }));
      });

      it('debe manejar errores durante la validación', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const validationError = new Error('Error en validación');

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockRejectedValue(validationError);

        // Act
        const result = await configController.handle(mockRequest);

        // Assert
        expect(mockLogger.error).toHaveBeenCalledWith('Error en el controlador:', {
          error: 'Error en validación',
          stack: validationError.stack
        });
        expect(result).toEqual(expect.objectContaining({
          statusCode: 500,
          body: expect.stringContaining(ERROR_MESSAGES.INTERNAL_ERROR)
        }));
      });

      it('debe manejar errores durante la transformación de datos', async () => {
        // Arrange
        const transformationError = new Error('Error en transformación');

        mockPlainToInstance.mockImplementation(() => {
          throw transformationError;
        });

        // Act
        const result = await configController.handle(mockRequest);

        // Assert
        expect(mockLogger.error).toHaveBeenCalledWith('Error en el controlador:', {
          error: 'Error en transformación',
          stack: transformationError.stack
        });
        expect(result).toEqual(expect.objectContaining({
          statusCode: 500,
          body: expect.stringContaining(ERROR_MESSAGES.INTERNAL_ERROR)
        }));
      });

      it('debe manejar errores que son instancias de BaseException', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const baseException = new NotFoundException();

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue([]);
        mockGetConfigCommandHandler.handle.mockRejectedValue(baseException);

        // Act
        const result = await configController.handle(mockRequest);

        // Assert
        expect(mockLogger.error).toHaveBeenCalledWith('Error en el controlador:', {
          error: baseException.message,
          stack: baseException.stack
        });
        expect(result).toEqual(baseException.toResponse());
      });
    });

    describe('logging', () => {
      it('debe registrar información del request correctamente', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const mockOutputFile = new OutputFile('contenido');

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue([]);
        mockGetConfigCommandHandler.handle.mockResolvedValue(mockOutputFile);

        // Act
        await configController.handle(mockRequest);

        // Assert
        expect(mockLogger.info).toHaveBeenCalledWith('Inicio de proceso de validación de datos', {
          method: 'GET',
          path: '/config/test.txt',
          ip: '127.0.0.1',
          userAgent: 'Mozilla/5.0',
          pathParameters: { filename: 'test.txt' }
        });
      });

      it('debe registrar cuando los datos son validados correctamente', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const mockOutputFile = new OutputFile('contenido');

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue([]);
        mockGetConfigCommandHandler.handle.mockResolvedValue(mockOutputFile);

        // Act
        await configController.handle(mockRequest);

        // Assert
        expect(mockLogger.info).toHaveBeenCalledWith('Datos validados correctamente', {
          path: 'test.txt'
        });
      });

      it('debe registrar cuando se ejecuta el comando', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const mockOutputFile = new OutputFile('contenido');

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue([]);
        mockGetConfigCommandHandler.handle.mockResolvedValue(mockOutputFile);

        // Act
        await configController.handle(mockRequest);

        // Assert
        expect(mockLogger.info).toHaveBeenCalledWith('Ejecutando comando:', {
          path: 'test.txt'
        });
      });
    });

    describe('estructura de respuesta', () => {
      it('debe retornar la estructura correcta de RechargeConfirmResponse cuando es exitoso', async () => {
        // Arrange
        const mockInputFile = new InputFile('test.txt');
        const mockOutputFile = new OutputFile('contenido del archivo');

        mockPlainToInstance.mockReturnValue(mockInputFile as any);
        mockValidate.mockResolvedValue([]);
        mockGetConfigCommandHandler.handle.mockResolvedValue(mockOutputFile);

        // Act
        const result = await configController.handle(mockRequest);

        // Assert
        const responseBody = JSON.parse(result.body);
        expect(responseBody).toEqual({
          message: SUCCESS_MESSAGES.READ_FILE,
          data: { content: 'contenido del archivo' }
        });
        expect(result.statusCode).toBe(200);
        expect(result.headers).toEqual({
          'Content-Type': 'application/json',
          'Access-Control-Allow-Headers': 'Content-Type',
        });
      });
    });
  });
}); 
