import Logger from '../../../src/infra/Logger';

// Mock del módulo logger
jest.mock('logger', () => ({
  createLogger: jest.fn().mockReturnValue({
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
  })
}));

// Mock de console.log para verificar las salidas
const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

describe('Logger', () => {
  beforeEach(() => {
    // Limpiar todos los mocks antes de cada test
    jest.clearAllMocks();
    // Resetear la instancia singleton
    (Logger as any).instance = undefined;
    (Logger as any).context = undefined;
  });

  afterAll(() => {
    consoleSpy.mockRestore();
  });

  describe('getInstance', () => {
    it('debería crear una nueva instancia del logger si no existe', () => {
      const logger = require('logger');

      const result = Logger.getInstance();

      expect(logger.createLogger).toHaveBeenCalledWith('config-service.log');
      expect(result).toBeDefined();
    });

    it('debería retornar la misma instancia si ya existe', () => {
      const logger = require('logger');

      const firstCall = Logger.getInstance();
      const secondCall = Logger.getInstance();

      expect(logger.createLogger).toHaveBeenCalledTimes(1);
      expect(firstCall).toBe(secondCall);
    });
  });

  describe('setInstance', () => {
    it('debería actualizar el contexto sin recrear la instancia', () => {
      const context = { functionName: 'testFunction', userId: '123' };
      
      Logger.setInstance(context);

      expect((Logger as any).context).toEqual(context);
    });

    it('debería sobrescribir el contexto existente', () => {
      const initialContext = { functionName: 'initialFunction' };
      const newContext = { functionName: 'newFunction', userId: '456' };

      Logger.setInstance(initialContext);
      Logger.setInstance(newContext);

      expect((Logger as any).context).toEqual(newContext);
    });
  });

  describe('addContext', () => {
    it('debería agregar contexto adicional al existente', () => {
      const initialContext = { functionName: 'testFunction' };
      const additionalContext = { functionName: 'newFunction', userId: '123', requestId: 'req-456' };

      Logger.setInstance(initialContext);
      Logger.addContext(additionalContext);

      expect((Logger as any).context).toEqual({
        functionName: 'newFunction',
        userId: '123',
        requestId: 'req-456'
      });
    });

    it('debería crear contexto si no existe', () => {
      const newContext = { functionName: 'newFunction', userId: '123' };

      Logger.addContext(newContext);

      expect((Logger as any).context).toEqual(newContext);
    });

    it('debería sobrescribir propiedades existentes', () => {
      const initialContext = { functionName: 'oldFunction', userId: '123' };
      const additionalContext = { functionName: 'newFunction', requestId: 'req-456' };

      Logger.setInstance(initialContext);
      Logger.addContext(additionalContext);

      expect((Logger as any).context).toEqual({
        functionName: 'newFunction',
        userId: '123',
        requestId: 'req-456'
      });
    });
  });

  describe('info', () => {
    it('debería loggear mensaje info con contexto', () => {
      const logger = require('logger');
      const context = { functionName: 'testFunction' };
      const message = 'Test info message';
      const data = { key: 'value' };

      Logger.setInstance(context);
      Logger.info(message, data);

      const expectedLogData = { key: 'value', context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().info).toHaveBeenCalledWith(message, expectedLogData);
    });

    it('debería loggear mensaje info sin datos adicionales', () => {
      const logger = require('logger');
      const context = { functionName: 'testFunction' };
      const message = 'Test info message';

      Logger.setInstance(context);
      Logger.info(message);

      const expectedLogData = { context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().info).toHaveBeenCalledWith(message, expectedLogData);
    });

    it('debería loggear mensaje info sin contexto', () => {
      const logger = require('logger');
      const message = 'Test info message';

      Logger.info(message);

      const expectedLogData = { context: undefined };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().info).toHaveBeenCalledWith(message, expectedLogData);
    });
  });

  describe('error', () => {
    it('debería loggear mensaje error con contexto y error', () => {
      const logger = require('logger');
      const context = { functionName: 'testFunction' };
      const message = 'Test error message';
      const error = new Error('Test error');

      Logger.setInstance(context);
      Logger.error(message, error);

      const expectedLogData = { error, context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().error).toHaveBeenCalledWith(message, expectedLogData);
    });

    it('debería loggear mensaje error sin error adicional', () => {
      const logger = require('logger');
      const context = { functionName: 'testFunction' };
      const message = 'Test error message';

      Logger.setInstance(context);
      Logger.error(message);

      const expectedLogData = { context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().error).toHaveBeenCalledWith(message, expectedLogData);
    });
  });

  describe('warn', () => {
    it('debería loggear mensaje warning con contexto y datos', () => {
      const logger = require('logger');
      const context = { functionName: 'testFunction' };
      const message = 'Test warning message';
      const data = { warningType: 'deprecation' };

      Logger.setInstance(context);
      Logger.warn(message, data);

      const expectedLogData = { warningType: 'deprecation', context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().warn).toHaveBeenCalledWith(message, expectedLogData);
    });

    it('debería loggear mensaje warning sin datos adicionales', () => {
      const logger = require('logger');
      const context = { functionName: 'testFunction' };
      const message = 'Test warning message';

      Logger.setInstance(context);
      Logger.warn(message);

      const expectedLogData = { context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().warn).toHaveBeenCalledWith(message, expectedLogData);
    });
  });

  describe('debug', () => {
    it('debería loggear mensaje debug con contexto y datos', () => {
      const logger = require('logger');
      const context = { functionName: 'testFunction' };
      const message = 'Test debug message';
      const data = { debugInfo: 'detailed info' };

      Logger.setInstance(context);
      Logger.debug(message, data);

      const expectedLogData = { debugInfo: 'detailed info', context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().debug).toHaveBeenCalledWith(message, expectedLogData);
    });

    it('debería loggear mensaje debug sin datos adicionales', () => {
      const logger = require('logger');
      const context = { functionName: 'testFunction' };
      const message = 'Test debug message';

      Logger.setInstance(context);
      Logger.debug(message);

      const expectedLogData = { context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().debug).toHaveBeenCalledWith(message, expectedLogData);
    });
  });

  describe('success', () => {
    it('debería loggear mensaje success con contexto y datos', () => {
      const logger = require('logger');
      const context = { functionName: 'testFunction' };
      const message = 'Test success message';
      const data = { result: 'success' };

      Logger.setInstance(context);
      Logger.success(message, data);

      const expectedLogData = { result: 'success', context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().info).toHaveBeenCalledWith(message, expectedLogData);
    });

    it('debería loggear mensaje success sin datos adicionales', () => {
      const logger = require('logger');
      const context = { functionName: 'testFunction' };
      const message = 'Test success message';

      Logger.setInstance(context);
      Logger.success(message);

      const expectedLogData = { context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().info).toHaveBeenCalledWith(message, expectedLogData);
    });
  });

  describe('Casos edge y integración', () => {
    it('debería manejar contexto con propiedades dinámicas', () => {
      const logger = require('logger');
      const context = { 
        functionName: 'testFunction',
        dynamicProp: 'dynamicValue',
        nested: { key: 'value' }
      };
      const message = 'Test message';

      Logger.setInstance(context);
      Logger.info(message);

      const expectedLogData = { context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().info).toHaveBeenCalledWith(message, expectedLogData);
    });

    it('debería manejar datos complejos en los logs', () => {
      const logger = require('logger');
      const context = { functionName: 'testFunction' };
      const message = 'Test message';
      const complexData = {
        array: [1, 2, 3],
        object: { nested: { value: 'test' } },
        nullValue: null,
        undefinedValue: undefined,
        booleanValue: true
      };

      Logger.setInstance(context);
      Logger.info(message, complexData);

      const expectedLogData = { ...complexData, context };
      expect(consoleSpy).toHaveBeenCalledWith(message, expectedLogData);
      expect(logger.createLogger().info).toHaveBeenCalledWith(message, expectedLogData);
    });

    it('debería mantener la instancia singleton a través de múltiples llamadas', () => {
      const logger = require('logger');

      const instance1 = Logger.getInstance();
      const instance2 = Logger.getInstance();

      expect(instance1).toBe(instance2);
      expect(logger.createLogger).toHaveBeenCalledTimes(1);
    });
  });
}); 
