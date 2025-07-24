import { IResponse } from '../../../../../src/domain/model/interfaces/IResponse';

describe('IResponse Interface', () => {
  describe('estructura de la interfaz', () => {
    it('debe definir el método toResponse', () => {
      // Crear un objeto que implemente la interfaz
      const response: IResponse = {
        toResponse: () => ({ statusCode: 200, body: 'test' })
      };
      
      expect(response).toHaveProperty('toResponse');
      expect(typeof response.toResponse).toBe('function');
    });

    it('debe permitir llamar al método toResponse', () => {
      const mockResponse = { statusCode: 200, body: 'test' };
      const response: IResponse = {
        toResponse: () => mockResponse
      };
      
      const result = response.toResponse();
      expect(result).toBe(mockResponse);
    });
  });

  describe('implementación de la interfaz', () => {
    it('debe permitir implementación con retorno simple', () => {
      const response: IResponse = {
        toResponse: () => ({ statusCode: 200, body: 'simple response' })
      };
      
      const result = response.toResponse();
      expect(result.statusCode).toBe(200);
      expect(result.body).toBe('simple response');
    });

    it('debe permitir implementación con retorno complejo', () => {
      const complexResponse = {
        statusCode: 201,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'success' })
      };
      
      const response: IResponse = {
        toResponse: () => complexResponse
      };
      
      const result = response.toResponse();
      expect(result).toEqual(complexResponse);
    });

    it('debe permitir implementación con retorno vacío', () => {
      const response: IResponse = {
        toResponse: () => ({})
      };
      
      const result = response.toResponse();
      expect(result).toEqual({});
    });
  });

  describe('tipos de retorno', () => {
    it('debe permitir retorno con statusCode numérico', () => {
      const response: IResponse = {
        toResponse: () => ({ statusCode: 404 })
      };
      
      const result = response.toResponse();
      expect(typeof result.statusCode).toBe('number');
      expect(result.statusCode).toBe(404);
    });

    it('debe permitir retorno con body string', () => {
      const response: IResponse = {
        toResponse: () => ({ body: 'response body' })
      };
      
      const result = response.toResponse();
      expect(typeof result.body).toBe('string');
      expect(result.body).toBe('response body');
    });

    it('debe permitir retorno con headers objeto', () => {
      const headers = { 'Content-Type': 'application/json', 'Authorization': 'Bearer token' };
      const response: IResponse = {
        toResponse: () => ({ headers })
      };
      
      const result = response.toResponse();
      expect(result.headers).toEqual(headers);
    });
  });

  describe('validación de tipos', () => {
    it('debe requerir que toResponse sea una función', () => {
      const response: IResponse = {
        toResponse: () => ({})
      };
      
      expect(typeof response.toResponse).toBe('function');
    });

    it('debe permitir cualquier tipo de retorno', () => {
      const validReturns = [
        { statusCode: 200 },
        { body: 'test' },
        { headers: {} },
        { statusCode: 500, body: 'error', headers: { 'Content-Type': 'text/plain' } },
        null,
        undefined,
        'string return',
        123
      ];

      validReturns.forEach(returnValue => {
        const response: IResponse = {
          toResponse: () => returnValue as any
        };
        
        const result = response.toResponse();
        expect(result).toBe(returnValue);
      });
    });
  });

  describe('comportamiento del método', () => {
    it('debe ejecutar la función cada vez que se llama', () => {
      let callCount = 0;
      const response: IResponse = {
        toResponse: () => {
          callCount++;
          return { callCount };
        }
      };
      
      expect(callCount).toBe(0);
      
      const result1 = response.toResponse();
      expect(callCount).toBe(1);
      expect(result1.callCount).toBe(1);
      
      const result2 = response.toResponse();
      expect(callCount).toBe(2);
      expect(result2.callCount).toBe(2);
    });

    it('debe permitir acceso a variables externas', () => {
      let externalValue = 'initial';
      const response: IResponse = {
        toResponse: () => ({ value: externalValue })
      };
      
      let result = response.toResponse();
      expect(result.value).toBe('initial');
      
      externalValue = 'updated';
      result = response.toResponse();
      expect(result.value).toBe('updated');
    });
  });
}); 
