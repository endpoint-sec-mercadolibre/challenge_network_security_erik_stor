import { SuccessResponse } from '../../../../src/domain/common/SuccessResponse';
import { HTTP_STATUS_CODES } from '../../../../src/domain/exceptions/constants/ErrorMessages';
import { SUCCESS_CODES, SUCCESS_MESSAGES } from '../../../../src/domain/common/consts/SuccessMessages';

describe('SuccessResponse', () => {
  describe('constructor', () => {
    it('debe crear una instancia con valores por defecto', () => {
      const data = { key: 'value' };
      const response = new SuccessResponse(data);
      
      expect(response.data).toBe(data);
      expect(response.name).toBe('SuccessResponse');
      expect(response.title).toBe('Success');
      expect(response.message).toBe(SUCCESS_MESSAGES.OK);
      expect(response.code).toBe(SUCCESS_CODES.OK);
      expect(response.statusCode).toBe(HTTP_STATUS_CODES.OK);
    });

    it('debe crear una instancia con valores personalizados', () => {
      const data = { custom: 'data' };
      const response = new SuccessResponse(
        data,
        'CustomName',
        'CustomTitle',
        'Custom message',
        'CUSTOM_CODE',
        201
      );
      
      expect(response.data).toBe(data);
      expect(response.name).toBe('CustomName');
      expect(response.title).toBe('CustomTitle');
      expect(response.message).toBe('Custom message');
      expect(response.code).toBe('CUSTOM_CODE');
      expect(response.statusCode).toBe(201);
    });

    it('debe crear una instancia con data null', () => {
      const response = new SuccessResponse(null);
      
      expect(response.data).toBeNull();
      expect(response.name).toBe('SuccessResponse');
      expect(response.message).toBe(SUCCESS_MESSAGES.OK);
    });

    it('debe crear una instancia con data undefined', () => {
      const response = new SuccessResponse(undefined);
      
      expect(response.data).toBeUndefined();
      expect(response.name).toBe('SuccessResponse');
      expect(response.message).toBe(SUCCESS_MESSAGES.OK);
    });
  });

  describe('propiedades', () => {
    it('debe tener todas las propiedades readonly', () => {
      const data = { test: 'data' };
      const response = new SuccessResponse(data);
      
      expect(response).toHaveProperty('data');
      expect(response).toHaveProperty('name');
      expect(response).toHaveProperty('title');
      expect(response).toHaveProperty('message');
      expect(response).toHaveProperty('code');
      expect(response).toHaveProperty('statusCode');
    });

    it('debe permitir acceso a todas las propiedades', () => {
      const data = { test: 'data' };
      const response = new SuccessResponse(data);
      
      expect(response.data).toBe(data);
      expect(response.name).toBe('SuccessResponse');
      expect(response.title).toBe('Success');
      expect(response.message).toBe(SUCCESS_MESSAGES.OK);
      expect(response.code).toBe(SUCCESS_CODES.OK);
      expect(response.statusCode).toBe(HTTP_STATUS_CODES.OK);
    });
  });

  describe('toResponse', () => {
    it('debe retornar la respuesta correcta con valores por defecto', () => {
      const data = { key: 'value', number: 123 };
      const response = new SuccessResponse(data);
      const result = response.toResponse();
      
      expect(result).toEqual({
        statusCode: HTTP_STATUS_CODES.OK,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
        body: JSON.stringify({
          message: SUCCESS_MESSAGES.OK,
          ...data
        })
      });
    });

    it('debe retornar la respuesta correcta con valores personalizados', () => {
      const data = { custom: 'data' };
      const response = new SuccessResponse(
        data,
        'CustomName',
        'CustomTitle',
        'Custom message',
        'CUSTOM_CODE',
        201
      );
      const result = response.toResponse();
      
      expect(result).toEqual({
        statusCode: 201,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
        body: JSON.stringify({
          message: 'Custom message',
          ...data
        })
      });
    });

    it('debe retornar un JSON válido en el body', () => {
      const data = { key: 'value' };
      const response = new SuccessResponse(data);
      const result = response.toResponse();
      
      expect(() => JSON.parse(result.body)).not.toThrow();
      const parsedBody = JSON.parse(result.body);
      expect(parsedBody.message).toBe(SUCCESS_MESSAGES.OK);
      expect(parsedBody.key).toBe('value');
    });

    it('debe manejar data con objetos anidados', () => {
      const data = {
        user: {
          id: 1,
          name: 'John',
          profile: {
            email: 'john@example.com',
            active: true
          }
        }
      };
      const response = new SuccessResponse(data);
      const result = response.toResponse();
      
      const parsedBody = JSON.parse(result.body);
      expect(parsedBody.user.id).toBe(1);
      expect(parsedBody.user.name).toBe('John');
      expect(parsedBody.user.profile.email).toBe('john@example.com');
      expect(parsedBody.user.profile.active).toBe(true);
    });

    it('debe manejar data con arrays', () => {
      const data = {
        items: ['item1', 'item2', 'item3'],
        numbers: [1, 2, 3, 4, 5]
      };
      const response = new SuccessResponse(data);
      const result = response.toResponse();
      
      const parsedBody = JSON.parse(result.body);
      expect(parsedBody.items).toEqual(['item1', 'item2', 'item3']);
      expect(parsedBody.numbers).toEqual([1, 2, 3, 4, 5]);
    });

    it('debe manejar data null', () => {
      const response = new SuccessResponse(null);
      const result = response.toResponse();
      
      const parsedBody = JSON.parse(result.body);
      expect(parsedBody.message).toBe(SUCCESS_MESSAGES.OK);
      expect(parsedBody).not.toHaveProperty('null');
    });

    it('debe manejar data undefined', () => {
      const response = new SuccessResponse(undefined);
      const result = response.toResponse();
      
      const parsedBody = JSON.parse(result.body);
      expect(parsedBody.message).toBe(SUCCESS_MESSAGES.OK);
      expect(parsedBody).not.toHaveProperty('undefined');
    });
  });

  describe('implementación de IResponse', () => {
    it('debe implementar la interfaz IResponse', () => {
      const data = { test: 'data' };
      const response = new SuccessResponse(data);
      
      expect(typeof response.toResponse).toBe('function');
      const result = response.toResponse();
      expect(result).toHaveProperty('statusCode');
      expect(result).toHaveProperty('headers');
      expect(result).toHaveProperty('body');
    });

    it('debe cumplir con el contrato de IResponse', () => {
      const data = { test: 'data' };
      const response = new SuccessResponse(data);
      
      const result = response.toResponse();
      expect(typeof result.statusCode).toBe('number');
      expect(typeof result.headers).toBe('object');
      expect(typeof result.body).toBe('string');
    });
  });

  describe('tipos de data', () => {
    it('debe manejar data de tipo string', () => {
      const data = 'simple string';
      const response = new SuccessResponse(data);
      const result = response.toResponse();
      
      const parsedBody = JSON.parse(result.body);
      expect(parsedBody.message).toBe(SUCCESS_MESSAGES.OK);
      // El string se expande como propiedades del objeto debido al spread operator
      expect(parsedBody['0']).toBe('s');
      expect(parsedBody['1']).toBe('i');
    });

    it('debe manejar data de tipo number', () => {
      const data = 42;
      const response = new SuccessResponse(data);
      const result = response.toResponse();
      
      const parsedBody = JSON.parse(result.body);
      expect(parsedBody.message).toBe(SUCCESS_MESSAGES.OK);
      // Los números no se expanden como propiedades del objeto
      expect(parsedBody).toHaveProperty('message');
    });

    it('debe manejar data de tipo boolean', () => {
      const data = true;
      const response = new SuccessResponse(data);
      const result = response.toResponse();
      
      const parsedBody = JSON.parse(result.body);
      expect(parsedBody.message).toBe(SUCCESS_MESSAGES.OK);
      // Los booleanos no se expanden como propiedades del objeto
      expect(parsedBody).toHaveProperty('message');
    });

    it('debe manejar data de tipo array', () => {
      const data = [1, 2, 3, 'test'];
      const response = new SuccessResponse(data);
      const result = response.toResponse();
      
      const parsedBody = JSON.parse(result.body);
      expect(parsedBody.message).toBe(SUCCESS_MESSAGES.OK);
      // El array se expande como propiedades del objeto debido al spread operator
      expect(parsedBody['0']).toBe(1);
      expect(parsedBody['1']).toBe(2);
      expect(parsedBody['2']).toBe(3);
      expect(parsedBody['3']).toBe('test');
    });
  });

  describe('headers', () => {
    it('debe tener los headers correctos', () => {
      const data = { test: 'data' };
      const response = new SuccessResponse(data);
      const result = response.toResponse();
      
      expect(result.headers).toEqual({
        'Content-Type': 'application/json',
        'Access-Control-Allow-Headers': 'Content-Type',
      });
    });

    it('debe mantener los headers consistentes', () => {
      const data1 = { test1: 'data1' };
      const data2 = { test2: 'data2' };
      
      const response1 = new SuccessResponse(data1);
      const response2 = new SuccessResponse(data2);
      
      const result1 = response1.toResponse();
      const result2 = response2.toResponse();
      
      expect(result1.headers).toEqual(result2.headers);
    });
  });
}); 
