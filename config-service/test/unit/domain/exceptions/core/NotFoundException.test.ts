import { NotFoundException } from '../../../../../src/domain/exceptions/core/NotFoundException';
import { ERROR_CODES, ERROR_MESSAGES, HTTP_STATUS_CODES } from '../../../../../src/domain/exceptions/constants/ErrorMessages';

describe('NotFoundException', () => {
  describe('constructor', () => {
    it('debe crear una instancia con valores por defecto', () => {
      const exception = new NotFoundException();
      
      expect(exception.message).toBe(ERROR_MESSAGES.NOT_FOUND);
      expect(exception.code).toBe(ERROR_CODES.INVALID_DATA);
      expect(exception.statusCode).toBe(HTTP_STATUS_CODES.NOT_FOUND);
      expect(exception.name).toBe('NotFoundException');
    });

    it('debe heredar de BaseException', () => {
      const exception = new NotFoundException();
      expect(exception).toBeInstanceOf(Error);
    });

    it('debe tener los valores correctos por defecto', () => {
      const exception = new NotFoundException();
      
      expect(exception.message).toBe(ERROR_MESSAGES.NOT_FOUND);
      expect(exception.code).toBe(ERROR_CODES.INVALID_DATA);
      expect(exception.statusCode).toBe(HTTP_STATUS_CODES.NOT_FOUND);
      expect(exception.data).toEqual({});
      expect(exception.title).toBe('Error');
    });
  });

  describe('toResponse', () => {
    it('debe retornar la respuesta correcta', () => {
      const exception = new NotFoundException();
      const response = exception.toResponse();
      
      expect(response).toEqual({
        statusCode: HTTP_STATUS_CODES.NOT_FOUND,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
        body: JSON.stringify({
          title: 'Error',
          code: ERROR_CODES.INVALID_DATA,
          message: ERROR_MESSAGES.NOT_FOUND,
          statusCode: 404,
          error: {
            detail: {}
          }
        })
      });
    });

    it('debe retornar un JSON válido en el body', () => {
      const exception = new NotFoundException();
      const response = exception.toResponse();
      
      expect(() => JSON.parse(response.body)).not.toThrow();
      const parsedBody = JSON.parse(response.body);
      expect(parsedBody.code).toBe(ERROR_CODES.INVALID_DATA);
      expect(parsedBody.message).toBe(ERROR_MESSAGES.NOT_FOUND);
      expect(parsedBody.statusCode).toBe(HTTP_STATUS_CODES.NOT_FOUND);
    });
  });
}); 
