import { BaseException } from '../../../../../src/domain/exceptions/core/BaseException';
import { HTTP_STATUS_CODES } from '../../../../../src/domain/exceptions/constants/ErrorMessages';

describe('BaseException', () => {
  describe('constructor', () => {
    it('debe crear una instancia con valores por defecto', () => {
      const exception = new BaseException('Test message', 'TEST_CODE');
      
      expect(exception.message).toBe('Test message');
      expect(exception.code).toBe('TEST_CODE');
      expect(exception.statusCode).toBe(HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR);
      expect(exception.data).toEqual({});
      expect(exception.title).toBe('Error');
      expect(exception.name).toBe('BaseException');
    });

    it('debe crear una instancia con valores personalizados', () => {
      const customData = { key: 'value' };
      const exception = new BaseException(
        'Custom message',
        'CUSTOM_CODE',
        400,
        customData,
        'Custom Title'
      );
      
      expect(exception.message).toBe('Custom message');
      expect(exception.code).toBe('CUSTOM_CODE');
      expect(exception.statusCode).toBe(400);
      expect(exception.data).toEqual(customData);
      expect(exception.title).toBe('Custom Title');
      expect(exception.name).toBe('BaseException');
    });
  });

  describe('toResponse', () => {
    it('debe retornar la respuesta correcta con valores por defecto', () => {
      const exception = new BaseException('Test message', 'TEST_CODE');
      const response = exception.toResponse();
      
      expect(response).toEqual({
        statusCode: HTTP_STATUS_CODES.INTERNAL_SERVER_ERROR,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
        body: JSON.stringify({
          title: 'Error',
          code: 'TEST_CODE',
          message: 'Test message',
          statusCode: 500,
          error: {
            detail: {}
          }
        })
      });
    });

    it('debe retornar la respuesta correcta con valores personalizados', () => {
      const customData = { key: 'value', nested: { prop: 'test' } };
      const exception = new BaseException(
        'Custom message',
        'CUSTOM_CODE',
        400,
        customData,
        'Custom Title'
      );
      const response = exception.toResponse();
      
      expect(response).toEqual({
        statusCode: 400,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
        body: JSON.stringify({
          title: 'Custom Title',
          code: 'CUSTOM_CODE',
          message: 'Custom message',
          statusCode: 400,
          error: {
            detail: customData
          }
        })
      });
    });

    it('debe retornar un JSON válido en el body', () => {
      const exception = new BaseException('Test message', 'TEST_CODE');
      const response = exception.toResponse();
      
      expect(() => JSON.parse(response.body)).not.toThrow();
      const parsedBody = JSON.parse(response.body);
      expect(parsedBody.title).toBe('Error');
      expect(parsedBody.code).toBe('TEST_CODE');
      expect(parsedBody.message).toBe('Test message');
    });
  });

  describe('herencia de Error', () => {
    it('debe ser una instancia de Error', () => {
      const exception = new BaseException('Test message', 'TEST_CODE');
      expect(exception).toBeInstanceOf(Error);
    });

    it('debe tener la propiedad name correcta', () => {
      const exception = new BaseException('Test message', 'TEST_CODE');
      expect(exception.name).toBe('BaseException');
    });
  });
}); 
