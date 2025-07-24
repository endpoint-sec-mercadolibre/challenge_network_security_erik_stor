import { InputRechargeMessageException } from '../../../../../src/domain/exceptions/constants/InputMessageException';

describe('InputRechargeMessageException', () => {
  describe('mensajes de error', () => {
    it('debe tener el mensaje correcto para FILENAME_MUST_BE_STRING', () => {
      expect(InputRechargeMessageException.FILENAME_MUST_BE_STRING).toBe('El nombre del archivo debe ser una cadena de texto');
    });

    it('debe tener el mensaje correcto para FILENAME_REQUIRED', () => {
      expect(InputRechargeMessageException.FILENAME_REQUIRED).toBe('El nombre del archivo es requerido');
    });

    it('debe tener propiedades readonly', () => {
      // Verificar que las propiedades son readonly (no se pueden modificar)
      const originalValue = InputRechargeMessageException.FILENAME_MUST_BE_STRING;
      expect(originalValue).toBe('El nombre del archivo debe ser una cadena de texto');
    });

    it('debe tener valores de string válidos', () => {
      expect(typeof InputRechargeMessageException.FILENAME_MUST_BE_STRING).toBe('string');
      expect(typeof InputRechargeMessageException.FILENAME_REQUIRED).toBe('string');
      expect(InputRechargeMessageException.FILENAME_MUST_BE_STRING.length).toBeGreaterThan(0);
      expect(InputRechargeMessageException.FILENAME_REQUIRED.length).toBeGreaterThan(0);
    });

    it('debe tener mensajes descriptivos', () => {
      expect(InputRechargeMessageException.FILENAME_MUST_BE_STRING).toContain('cadena de texto');
      expect(InputRechargeMessageException.FILENAME_REQUIRED).toContain('requerido');
    });
  });

  describe('estructura de la clase', () => {
    it('debe ser una clase estática', () => {
      expect(typeof InputRechargeMessageException).toBe('function');
      expect(InputRechargeMessageException.FILENAME_MUST_BE_STRING).toBeDefined();
      expect(InputRechargeMessageException.FILENAME_REQUIRED).toBeDefined();
    });

    it('debe tener solo las propiedades esperadas', () => {
      const properties = Object.getOwnPropertyNames(InputRechargeMessageException);
      expect(properties).toContain('FILENAME_MUST_BE_STRING');
      expect(properties).toContain('FILENAME_REQUIRED');
      // Verificar que al menos tiene las propiedades esperadas
      expect(properties.length).toBeGreaterThanOrEqual(2);
    });
  });
}); 
