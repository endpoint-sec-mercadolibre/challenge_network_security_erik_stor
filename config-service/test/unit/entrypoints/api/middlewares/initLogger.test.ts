import { Request, Response, NextFunction } from 'express';
import { initLogger } from '../../../../../src/entrypoints/api/middlewares/initLogger';
import Logger from '../../../../../src/infra/Logger';

// Mock dependencies
jest.mock('../../../../../src/infra/Logger');

const MockedLogger = Logger as jest.Mocked<typeof Logger>;

describe('initLogger', () => {
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
      info: jest.fn(),
    };

    // Setup Logger mocks
    MockedLogger.setInstance = jest.fn();
    MockedLogger.getInstance = jest.fn().mockReturnValue(mockLoggerInstance);
  });

  describe('cuando se inicializa el logger', () => {
    it('debe configurar la instancia del logger con el contexto correcto', () => {
      initLogger(mockRequest as Request, mockResponse as Response, mockNext);

      expect(MockedLogger.setInstance).toHaveBeenCalledWith({
        functionName: 'config-service',
      });
    });

    it('debe registrar la información del request', () => {
      initLogger(mockRequest as Request, mockResponse as Response, mockNext);

      expect(MockedLogger.getInstance).toHaveBeenCalled();
      expect(mockLoggerInstance.info).toHaveBeenCalledWith('GET /config/test - 127.0.0.1');
    });

    it('debe llamar next() después de configurar el logger', () => {
      initLogger(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockNext).toHaveBeenCalled();
    });
  });

  describe('cuando se usan diferentes métodos HTTP', () => {
    it('debe registrar correctamente el método POST', () => {
      mockRequest = {
        ...mockRequest,
        method: 'POST',
        path: '/config/create',
        ip: '192.168.1.1',
      };

      initLogger(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockLoggerInstance.info).toHaveBeenCalledWith('POST /config/create - 192.168.1.1');
    });

    it('debe registrar correctamente el método PUT', () => {
      mockRequest = {
        ...mockRequest,
        method: 'PUT',
        path: '/config/update',
        ip: '10.0.0.1',
      };

      initLogger(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockLoggerInstance.info).toHaveBeenCalledWith('PUT /config/update - 10.0.0.1');
    });

    it('debe registrar correctamente el método DELETE', () => {
      mockRequest = {
        ...mockRequest,
        method: 'DELETE',
        path: '/config/remove',
        ip: '172.16.0.1',
      };

      initLogger(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockLoggerInstance.info).toHaveBeenCalledWith('DELETE /config/remove - 172.16.0.1');
    });
  });

  describe('cuando hay valores undefined o null', () => {
    it('debe manejar method undefined', () => {
      mockRequest = {
        ...mockRequest,
        method: undefined,
      };

      initLogger(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockLoggerInstance.info).toHaveBeenCalledWith('undefined /config/test - 127.0.0.1');
    });

    it('debe manejar path undefined', () => {
      mockRequest = {
        ...mockRequest,
        path: undefined,
      };

      initLogger(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockLoggerInstance.info).toHaveBeenCalledWith('GET undefined - 127.0.0.1');
    });

    it('debe manejar ip undefined', () => {
      mockRequest = {
        ...mockRequest,
        ip: undefined,
      };

      initLogger(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockLoggerInstance.info).toHaveBeenCalledWith('GET /config/test - undefined');
    });

    it('debe manejar todos los valores undefined', () => {
      mockRequest = {
        ...mockRequest,
        method: undefined,
        path: undefined,
        ip: undefined,
      };

      initLogger(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockLoggerInstance.info).toHaveBeenCalledWith('undefined undefined - undefined');
    });
  });

  describe('orden de ejecución', () => {
    it('debe ejecutar las operaciones en el orden correcto', () => {
      const executionOrder: string[] = [];

      MockedLogger.setInstance.mockImplementation(() => {
        executionOrder.push('setInstance');
      });

      MockedLogger.getInstance.mockImplementation(() => {
        executionOrder.push('getInstance');
        return mockLoggerInstance;
      });

      mockLoggerInstance.info.mockImplementation(() => {
        executionOrder.push('info');
      });

      (mockNext as jest.Mock).mockImplementation(() => {
        executionOrder.push('next');
      });

      initLogger(mockRequest as Request, mockResponse as Response, mockNext);

      expect(executionOrder).toEqual(['setInstance', 'getInstance', 'info', 'next']);
    });
  });
}); 
