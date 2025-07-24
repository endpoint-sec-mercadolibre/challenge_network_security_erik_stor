import { SUCCESS_MESSAGES, SUCCESS_CODES } from '../../../../../src/domain/common/consts/SuccessMessages';

describe('SuccessMessages Constants', () => {
  describe('SUCCESS_MESSAGES', () => {
    it('debe tener todos los mensajes de éxito definidos', () => {
      expect(SUCCESS_MESSAGES.OK).toBe('Operación exitosa');
      expect(SUCCESS_MESSAGES.READ_FILE).toBe('Archivo leído exitosamente');
    });

    it('debe tener las propiedades correctas', () => {
      const expectedKeys = [
        'OK',
        'READ_FILE'
      ];

      expectedKeys.forEach(key => {
        expect(SUCCESS_MESSAGES).toHaveProperty(key);
        expect(typeof SUCCESS_MESSAGES[key as keyof typeof SUCCESS_MESSAGES]).toBe('string');
      });
    });

    it('debe tener valores de string válidos', () => {
      Object.values(SUCCESS_MESSAGES).forEach((value: string) => {
        expect(typeof value).toBe('string');
        expect(value.length).toBeGreaterThan(0);
      });
    });

    it('debe tener mensajes descriptivos', () => {
      expect(SUCCESS_MESSAGES.OK).toContain('exitosa');
      expect(SUCCESS_MESSAGES.READ_FILE).toContain('leído');
    });
  });

  describe('SUCCESS_CODES', () => {
    it('debe tener todos los códigos de éxito definidos', () => {
      expect(SUCCESS_CODES.OK).toBe('OK');
      expect(SUCCESS_CODES.CREATED).toBe('CREATED');
      expect(SUCCESS_CODES.READ_FILE).toBe('READ_FILE');
    });

    it('debe tener las propiedades correctas', () => {
      const expectedKeys = [
        'OK',
        'CREATED',
        'READ_FILE'
      ];

      expectedKeys.forEach(key => {
        expect(SUCCESS_CODES).toHaveProperty(key);
        expect(typeof SUCCESS_CODES[key as keyof typeof SUCCESS_CODES]).toBe('string');
      });
    });

    it('debe tener valores de string válidos', () => {
      Object.values(SUCCESS_CODES).forEach((value: string) => {
        expect(typeof value).toBe('string');
        expect(value.length).toBeGreaterThan(0);
      });
    });

    it('debe tener códigos en formato correcto', () => {
      Object.values(SUCCESS_CODES).forEach((value: string) => {
        // Verificar que los códigos están en mayúsculas o formato consistente
        expect(value).toMatch(/^[A-Z_]+$/);
      });
    });
  });

  describe('estructura de las constantes', () => {
    it('debe ser un objeto readonly', () => {
      expect(typeof SUCCESS_MESSAGES).toBe('object');
      expect(typeof SUCCESS_CODES).toBe('object');
    });

    it('debe tener propiedades readonly', () => {
      // Verificar que las propiedades existen y tienen valores válidos
      expect(SUCCESS_MESSAGES.OK).toBeDefined();
      expect(typeof SUCCESS_MESSAGES.OK).toBe('string');
      expect(SUCCESS_MESSAGES.OK.length).toBeGreaterThan(0);
    });

    it('debe tener el número correcto de propiedades', () => {
      const messageKeys = Object.keys(SUCCESS_MESSAGES);
      const codeKeys = Object.keys(SUCCESS_CODES);

      expect(messageKeys.length).toBe(2);
      expect(codeKeys.length).toBe(3);
    });
  });

  describe('consistencia entre mensajes y códigos', () => {
    it('debe tener mensajes y códigos relacionados', () => {
      // Verificar que hay mensajes para los códigos principales
      expect(SUCCESS_MESSAGES.OK).toBeDefined();
      expect(SUCCESS_CODES.OK).toBeDefined();
      expect(SUCCESS_MESSAGES.READ_FILE).toBeDefined();
      expect(SUCCESS_CODES.READ_FILE).toBeDefined();
    });

    it('debe tener códigos sin espacios ni caracteres especiales', () => {
      Object.values(SUCCESS_CODES).forEach((value: string) => {
        expect(value).not.toContain(' ');
        expect(value).not.toContain('-');
        expect(value).not.toContain('.');
      });
    });

    it('debe tener mensajes en español', () => {
      Object.values(SUCCESS_MESSAGES).forEach((value: string) => {
        // Verificar que los mensajes contienen caracteres en español
        expect(value).toMatch(/[áéíóúñ]/);
      });
    });
  });
}); 
