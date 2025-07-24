import { ERROR_MESSAGES, HTTP_STATUS_CODES, ERROR_CODES } from '../../../../../src/domain/exceptions/constants/ErrorMessages';

describe('ErrorMessages Constants', () => {
  describe('ERROR_MESSAGES', () => {
    it('debe tener todos los mensajes de error definidos', () => {
      expect(ERROR_MESSAGES.REQUIRED_FIELD).toBe('El campo es obligatorio');
      expect(ERROR_MESSAGES.INVALID_FORMAT).toBe('El formato no es válido');
      expect(ERROR_MESSAGES.INVALID_LENGTH).toBe('La longitud no es válida');
      expect(ERROR_MESSAGES.INVALID_DATA).toBe('Los datos de entrada no son válidos');
      expect(ERROR_MESSAGES.INTERNAL_ERROR).toBe('Error interno del servidor');
      expect(ERROR_MESSAGES.NOT_FOUND).toBe('No se encontró el recurso');
    });

    it('debe tener las propiedades correctas', () => {
      const expectedKeys = [
        'REQUIRED_FIELD',
        'INVALID_FORMAT',
        'INVALID_LENGTH',
        'INVALID_DATA',
        'INTERNAL_ERROR',
        'NOT_FOUND'
      ];

      expectedKeys.forEach(key => {
        expect(ERROR_MESSAGES).toHaveProperty(key);
        expect(typeof ERROR_MESSAGES[key as keyof typeof ERROR_MESSAGES]).toBe('string');
      });
    });
  });

  describe('HTTP_STATUS_CODES', () => {
    it('debe tener todos los códigos de estado HTTP definidos', () => {
      expect(HTTP_STATUS_CODES.OK).toBe(200);
      expect(HTTP_STATUS_CODES.BAD_REQUEST).toBe(400);
      expect(HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR).toBe(500);
      expect(HTTP_STATUS_CODES.CREATED).toBe(201);
      expect(HTTP_STATUS_CODES.NOT_FOUND).toBe(404);
      expect(HTTP_STATUS_CODES.CONFLICT).toBe(409);
      expect(HTTP_STATUS_CODES.UNAUTHORIZED).toBe(401);
      expect(HTTP_STATUS_CODES.FORBIDDEN).toBe(403);
      expect(HTTP_STATUS_CODES.BAD_GATEWAY).toBe(502);
      expect(HTTP_STATUS_CODES.SERVICE_UNAVAILABLE).toBe(503);
      expect(HTTP_STATUS_CODES.GATEWAY_TIMEOUT).toBe(504);
    });

    it('debe tener las propiedades correctas', () => {
      const expectedKeys = [
        'OK',
        'BAD_REQUEST',
        'INTERNAL_SERVER_ERROR',
        'CREATED',
        'NOT_FOUND',
        'CONFLICT',
        'UNAUTHORIZED',
        'FORBIDDEN',
        'BAD_GATEWAY',
        'SERVICE_UNAVAILABLE',
        'GATEWAY_TIMEOUT'
      ];

      expectedKeys.forEach(key => {
        expect(HTTP_STATUS_CODES).toHaveProperty(key);
        expect(typeof HTTP_STATUS_CODES[key as keyof typeof HTTP_STATUS_CODES]).toBe('number');
      });
    });

    it('debe tener valores numéricos válidos', () => {
      Object.values(HTTP_STATUS_CODES).forEach(value => {
        expect(typeof value).toBe('number');
        expect(value).toBeGreaterThan(0);
        expect(Number.isInteger(value)).toBe(true);
      });
    });
  });

  describe('ERROR_CODES', () => {
    it('debe tener todos los códigos de error definidos', () => {
      expect(ERROR_CODES.VALIDATION_ERROR).toBe('VALIDATION_ERROR');
      expect(ERROR_CODES.INVALID_DATA).toBe('INVALID_DATA');
      expect(ERROR_CODES.INTERNAL_ERROR).toBe('INTERNAL_ERROR');
    });

    it('debe tener las propiedades correctas', () => {
      const expectedKeys = [
        'VALIDATION_ERROR',
        'INVALID_DATA',
        'INTERNAL_ERROR'
      ];

      expectedKeys.forEach(key => {
        expect(ERROR_CODES).toHaveProperty(key);
        expect(typeof ERROR_CODES[key as keyof typeof ERROR_CODES]).toBe('string');
      });
    });

    it('debe tener valores de string válidos', () => {
      Object.values(ERROR_CODES).forEach(value => {
        expect(typeof value).toBe('string');
        expect(value.length).toBeGreaterThan(0);
      });
    });
  });
}); 
