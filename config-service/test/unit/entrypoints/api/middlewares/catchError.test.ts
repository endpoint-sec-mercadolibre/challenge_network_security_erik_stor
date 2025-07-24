import { Request, Response, NextFunction } from 'express';
import { catchError } from '../../../../../src/entrypoints/api/middlewares/catchError';
import Logger from '../../../../../src/infra/Logger';

// Mock dependencies
jest.mock('../../../../../src/infra/Logger');

const MockedLogger = Logger as jest.Mocked<typeof Logger>;

describe('catchError', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;
  let mockLoggerInstance: jest.Mocked<any>;

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Setup mock request
    mockRequest = {
      method: 'GET',
      path: '/config/test',
      ip: '127.0.0.1',
    };

    // Setup mock response
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn().mockReturnThis(),
    };

    // Setup mock next function
    mockNext = jest.fn();

    // Setup mock logger instance
    mockLoggerInstance = {
      error: jest.fn(),
    };

    // Setup Logger mocks
    MockedLogger.getInstance = jest.fn().mockReturnValue(mockLoggerInstance);

    // Reset environment variables
    delete process.env.NODE_ENV;
  });

  describe('cuando se maneja un error', () => {
    it('debe registrar el error en el logger', () => {
      const testError = new Error('Test error message');

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(MockedLogger.getInstance).toHaveBeenCalled();
      expect(mockLoggerInstance.error).toHaveBeenCalledWith('Error en el servidor:', 'Test error message');
    });

    it('debe retornar status 500', () => {
      const testError = new Error('Test error message');

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
    });
  });

  describe('cuando NODE_ENV es development', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'development';
    });

    it('debe incluir el mensaje de error en la respuesta', () => {
      const testError = new Error('Test error message');

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Error interno del servidor',
        message: 'Test error message'
      });
    });

    it('debe manejar errores con mensajes largos', () => {
      const longErrorMessage = 'A'.repeat(1000);
      const testError = new Error(longErrorMessage);

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Error interno del servidor',
        message: longErrorMessage
      });
    });

    it('debe manejar errores con caracteres especiales', () => {
      const specialCharMessage = 'Error con caracteres: áéíóú ñ ç € $ % &';
      const testError = new Error(specialCharMessage);

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Error interno del servidor',
        message: specialCharMessage
      });
    });
  });

  describe('cuando NODE_ENV no es development', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'production';
    });

    it('debe ocultar el mensaje de error en la respuesta', () => {
      const testError = new Error('Test error message');

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Error interno del servidor',
        message: 'Algo salió mal'
      });
    });

    it('debe ocultar el mensaje incluso con errores críticos', () => {
      const criticalError = new Error('Database connection failed: password is incorrect');
      criticalError.name = 'DatabaseError';

      catchError(criticalError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Error interno del servidor',
        message: 'Algo salió mal'
      });
    });
  });

  describe('cuando NODE_ENV no está definido', () => {
    it('debe ocultar el mensaje de error por defecto', () => {
      const testError = new Error('Test error message');

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Error interno del servidor',
        message: 'Algo salió mal'
      });
    });
  });

  describe('cuando NODE_ENV es test', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'test';
    });

    it('debe ocultar el mensaje de error', () => {
      const testError = new Error('Test error message');

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Error interno del servidor',
        message: 'Algo salió mal'
      });
    });
  });

  describe('cuando NODE_ENV es staging', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'staging';
    });

    it('debe ocultar el mensaje de error', () => {
      const testError = new Error('Test error message');

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Error interno del servidor',
        message: 'Algo salió mal'
      });
    });
  });

  describe('manejo de diferentes tipos de errores', () => {
    it('debe manejar errores con mensaje vacío', () => {
      const testError = new Error('');

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockLoggerInstance.error).toHaveBeenCalledWith('Error en el servidor:', '');
    });

    it('debe manejar errores con mensaje undefined', () => {
      const testError = new Error();
      testError.message = undefined as any;

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockLoggerInstance.error).toHaveBeenCalledWith('Error en el servidor:', undefined);
    });

    it('debe manejar errores con mensaje null', () => {
      const testError = new Error();
      testError.message = null as any;

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockLoggerInstance.error).toHaveBeenCalledWith('Error en el servidor:', null);
    });

    it('debe manejar errores personalizados', () => {
      class CustomError extends Error {
        constructor(message: string) {
          super(message);
          this.name = 'CustomError';
        }
      }

      const customError = new CustomError('Custom error message');

      catchError(customError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockLoggerInstance.error).toHaveBeenCalledWith('Error en el servidor:', 'Custom error message');
    });
  });

  describe('orden de ejecución', () => {
    it('debe ejecutar las operaciones en el orden correcto', () => {
      const executionOrder: string[] = [];
      const testError = new Error('Test error');

      MockedLogger.getInstance.mockImplementation(() => {
        executionOrder.push('getInstance');
        return mockLoggerInstance;
      });

      mockLoggerInstance.error.mockImplementation(() => {
        executionOrder.push('logger.error');
      });

      (mockResponse.status as jest.Mock).mockImplementation(() => {
        executionOrder.push('response.status');
        return mockResponse;
      });

      (mockResponse.json as jest.Mock).mockImplementation(() => {
        executionOrder.push('response.json');
        return mockResponse;
      });

      catchError(testError, mockRequest as Request, mockResponse as Response, mockNext);

      expect(executionOrder).toEqual(['getInstance', 'logger.error', 'response.status', 'response.json']);
    });
  });


}); 
