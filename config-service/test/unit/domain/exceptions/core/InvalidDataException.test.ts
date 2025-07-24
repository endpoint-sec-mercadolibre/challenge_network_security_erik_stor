import { InvalidDataException } from '../../../../../src/domain/exceptions/core/InvalidDataException';
import { ERROR_CODES, ERROR_MESSAGES, HTTP_STATUS_CODES } from '../../../../../src/domain/exceptions/constants/ErrorMessages';

describe('InvalidDataException', () => {
  describe('constructor', () => {
    it('debe crear una instancia con mensajes de error', () => {
      const errorMessages = ['Campo requerido', 'Formato inválido'];
      const exception = new InvalidDataException(errorMessages);
      
      expect(exception.message).toBe(ERROR_MESSAGES.INVALID_DATA);
      expect(exception.code).toBe(ERROR_CODES.INVALID_DATA);
      expect(exception.statusCode).toBe(HTTP_STATUS_CODES.BAD_REQUEST);
      expect(exception.data).toEqual(errorMessages);
      expect(exception.name).toBe('InvalidDataException');
    });

    it('debe crear una instancia con un solo mensaje de error', () => {
      const errorMessages = ['Solo un error'];
      const exception = new InvalidDataException(errorMessages);
      
      expect(exception.message).toBe(ERROR_MESSAGES.INVALID_DATA);
      expect(exception.code).toBe(ERROR_CODES.INVALID_DATA);
      expect(exception.statusCode).toBe(HTTP_STATUS_CODES.BAD_REQUEST);
      expect(exception.data).toEqual(errorMessages);
    });

    it('debe crear una instancia con array vacío de errores', () => {
      const errorMessages: string[] = [];
      const exception = new InvalidDataException(errorMessages);
      
      expect(exception.message).toBe(ERROR_MESSAGES.INVALID_DATA);
      expect(exception.code).toBe(ERROR_CODES.INVALID_DATA);
      expect(exception.statusCode).toBe(HTTP_STATUS_CODES.BAD_REQUEST);
      expect(exception.data).toEqual([]);
    });

    it('debe heredar de BaseException', () => {
      const exception = new InvalidDataException(['Test error']);
      expect(exception).toBeInstanceOf(Error);
    });
  });

  describe('toResponse', () => {
    it('debe retornar la respuesta correcta con mensajes de error', () => {
      const errorMessages = ['Error 1', 'Error 2', 'Error 3'];
      const exception = new InvalidDataException(errorMessages);
      const response = exception.toResponse();
      
      expect(response).toEqual({
        statusCode: HTTP_STATUS_CODES.BAD_REQUEST,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
        body: JSON.stringify({
          title: 'Error',
          code: ERROR_CODES.INVALID_DATA,
          message: ERROR_MESSAGES.INVALID_DATA,
          statusCode: 400,
          error: {
            detail: errorMessages
          }
        })
      });
    });

    it('debe retornar un JSON válido en el body', () => {
      const errorMessages = ['Campo requerido'];
      const exception = new InvalidDataException(errorMessages);
      const response = exception.toResponse();
      
      expect(() => JSON.parse(response.body)).not.toThrow();
      const parsedBody = JSON.parse(response.body);
      expect(parsedBody.code).toBe(ERROR_CODES.INVALID_DATA);
      expect(parsedBody.message).toBe(ERROR_MESSAGES.INVALID_DATA);
      expect(parsedBody.error.detail).toEqual(errorMessages);
    });
  });
}); 
