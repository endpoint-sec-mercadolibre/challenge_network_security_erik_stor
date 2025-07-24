import { File } from '../../../../../src/domain/model/interfaces/IOutput';

describe('File Interface', () => {
  describe('estructura de la interfaz', () => {
    it('debe definir la propiedad content', () => {
      // Crear un objeto que implemente la interfaz
      const file: File = {
        content: 'test content'
      };
      
      expect(file).toHaveProperty('content');
      expect(typeof file.content).toBe('string');
    });

    it('debe permitir acceso a la propiedad content', () => {
      const content = 'test content';
      const file: File = {
        content: content
      };
      
      expect(file.content).toBe(content);
    });
  });

  describe('implementación de la interfaz', () => {
    it('debe permitir implementación con string simple', () => {
      const file: File = {
        content: 'simple content'
      };
      
      expect(file.content).toBe('simple content');
    });

    it('debe permitir implementación con string vacío', () => {
      const file: File = {
        content: ''
      };
      
      expect(file.content).toBe('');
    });

    it('debe permitir implementación con JSON string', () => {
      const jsonContent = '{"key": "value", "number": 123}';
      const file: File = {
        content: jsonContent
      };
      
      expect(file.content).toBe(jsonContent);
    });

    it('debe permitir implementación con contenido multilínea', () => {
      const multilineContent = 'Línea 1\nLínea 2\nLínea 3';
      const file: File = {
        content: multilineContent
      };
      
      expect(file.content).toBe(multilineContent);
    });
  });

  describe('tipos de contenido', () => {
    it('debe manejar contenido con caracteres especiales', () => {
      const specialContent = 'áéíóú ñ ç @#$%^&*()';
      const file: File = {
        content: specialContent
      };
      
      expect(file.content).toBe(specialContent);
    });

    it('debe manejar contenido con números', () => {
      const numericContent = '1234567890';
      const file: File = {
        content: numericContent
      };
      
      expect(file.content).toBe(numericContent);
    });

    it('debe manejar contenido con espacios', () => {
      const spacedContent = '   contenido con espacios   ';
      const file: File = {
        content: spacedContent
      };
      
      expect(file.content).toBe(spacedContent);
    });
  });

  describe('validación de tipos', () => {
    it('debe requerir que content sea string', () => {
      // Verificar que TypeScript valida el tipo
      const file: File = {
        content: 'valid string'
      };
      
      expect(typeof file.content).toBe('string');
    });

    it('debe permitir cualquier string válido', () => {
      const validStrings = [
        'simple',
        '',
        'con espacios',
        'con\nsaltos\nde\nlínea',
        'con caracteres especiales: áéíóú ñ ç @#$%^&*()',
        '{"json": "content"}'
      ];

      validStrings.forEach(str => {
        const file: File = {
          content: str
        };
        expect(file.content).toBe(str);
      });
    });
  });
}); 
