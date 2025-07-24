import { SystemException } from '../../../../../src/domain/exceptions/core/SystemException';
import { ERROR_CODES, HTTP_STATUS_CODES } from '../../../../../src/domain/exceptions/constants/ErrorMessages';

describe('SystemException', () => {
  describe('constructor', () => {
    it('debe crear una instancia con el mensaje proporcionado', () => {
      const message = 'Error del sistema';
      const exception = new SystemException(message);
      
      expect(exception.message).toBe(message);
      expect(exception.code).toBe(ERROR_CODES.INTERNAL_ERROR);
      expect(exception.statusCode).toBe(HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR);
      expect(exception.name).toBe('SystemException');
    });

    it('debe heredar de BaseException', () => {
      const exception = new SystemException('Test message');
      expect(exception).toBeInstanceOf(Error);
    });

    it('debe tener los valores correctos por defecto', () => {
      const exception = new SystemException('Test message');
      
      expect(exception.code).toBe(ERROR_CODES.INTERNAL_ERROR);
      expect(exception.statusCode).toBe(HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR);
      expect(exception.data).toEqual({});
      expect(exception.title).toBe('Error');
    });
  });

  describe('toResponse', () => {
    it('debe retornar la respuesta correcta', () => {
      const message = 'Error del sistema crítico';
      const exception = new SystemException(message);
      const response = exception.toResponse();
      
      expect(response).toEqual({
        statusCode: HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
        body: JSON.stringify({
          title: 'Error',
          code: ERROR_CODES.INTERNAL_ERROR,
          message: message,
          statusCode: 500,
          error: {
            detail: {}
          }
        })
      });
    });

    it('debe retornar un JSON válido en el body', () => {
      const exception = new SystemException('Test message');
      const response = exception.toResponse();
      
      expect(() => JSON.parse(response.body)).not.toThrow();
      const parsedBody = JSON.parse(response.body);
      expect(parsedBody.code).toBe(ERROR_CODES.INTERNAL_ERROR);
      expect(parsedBody.statusCode).toBe(HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR);
    });
  });
}); 
