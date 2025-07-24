import { GetContentException } from '../../../../src/domain/exceptions/GetContentException';
import { HTTP_STATUS_CODES } from '../../../../src/domain/exceptions/constants/ErrorMessages';

describe('GetContentException', () => {
  describe('constructor', () => {
    it('debe crear una instancia con valores por defecto', () => {
      const message = 'Error al obtener contenido';
      const code = 'GET_CONTENT_ERROR';
      const exception = new GetContentException(message, code);
      
      expect(exception.message).toBe(message);
      expect(exception.code).toBe(code);
      expect(exception.statusCode).toBe(HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR);
      expect(exception.name).toBe('GetContentException');
    });

    it('debe crear una instancia con statusCode personalizado', () => {
      const message = 'Error al obtener contenido';
      const code = 'GET_CONTENT_ERROR';
      const customStatusCode = 404;
      const exception = new GetContentException(message, code, customStatusCode);
      
      expect(exception.message).toBe(message);
      expect(exception.code).toBe(code);
      expect(exception.statusCode).toBe(customStatusCode);
      expect(exception.name).toBe('GetContentException');
    });

    it('debe heredar de BaseException', () => {
      const exception = new GetContentException('Test message', 'TEST_CODE');
      expect(exception).toBeInstanceOf(Error);
    });

    it('debe tener los valores correctos por defecto', () => {
      const exception = new GetContentException('Test message', 'TEST_CODE');
      
      expect(exception.statusCode).toBe(HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR);
      expect(exception.data).toEqual({});
      expect(exception.title).toBe('Error');
    });
  });

  describe('toResponse', () => {
    it('debe retornar la respuesta correcta con valores por defecto', () => {
      const message = 'Error al obtener contenido';
      const code = 'GET_CONTENT_ERROR';
      const exception = new GetContentException(message, code);
      const response = exception.toResponse();
      
      expect(response).toEqual({
        statusCode: HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
        body: JSON.stringify({
          title: 'Error',
          code: code,
          message: message,
          statusCode: 500,
          error: {
            detail: {}
          }
        })
      });
    });

    it('debe retornar la respuesta correcta con statusCode personalizado', () => {
      const message = 'Error al obtener contenido';
      const code = 'GET_CONTENT_ERROR';
      const customStatusCode = 400;
      const exception = new GetContentException(message, code, customStatusCode);
      const response = exception.toResponse();
      
      expect(response).toEqual({
        statusCode: customStatusCode,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
        body: JSON.stringify({
          title: 'Error',
          code: code,
          message: message,
          statusCode: 400,
          error: {
            detail: {}
          }
        })
      });
    });

    it('debe retornar un JSON válido en el body', () => {
      const exception = new GetContentException('Test message', 'TEST_CODE');
      const response = exception.toResponse();
      
      expect(() => JSON.parse(response.body)).not.toThrow();
      const parsedBody = JSON.parse(response.body);
      expect(parsedBody.code).toBe('TEST_CODE');
      expect(parsedBody.message).toBe('Test message');
      expect(parsedBody.statusCode).toBe(HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR);
    });
  });
}); 
