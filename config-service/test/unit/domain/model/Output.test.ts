import { OutputFile } from '../../../../src/domain/model/Output';
import { File } from '../../../../src/domain/model/interfaces/IOutput';

describe('OutputFile', () => {
  describe('constructor', () => {
    it('debe crear una instancia con contenido válido', () => {
      const content = 'Contenido del archivo';
      const output = new OutputFile(content);
      
      expect(output.content).toBe(content);
    });

    it('debe crear una instancia con contenido vacío', () => {
      const content = '';
      const output = new OutputFile(content);
      
      expect(output.content).toBe(content);
    });

    it('debe crear una instancia con contenido JSON', () => {
      const content = '{"key": "value", "number": 123}';
      const output = new OutputFile(content);
      
      expect(output.content).toBe(content);
    });

    it('debe crear una instancia con contenido multilínea', () => {
      const content = 'Línea 1\nLínea 2\nLínea 3';
      const output = new OutputFile(content);
      
      expect(output.content).toBe(content);
    });
  });

  describe('propiedades', () => {
    it('debe tener la propiedad content readonly', () => {
      const output = new OutputFile('test content');
      
      expect(output).toHaveProperty('content');
      expect(typeof output.content).toBe('string');
    });

    it('debe permitir acceso a la propiedad content', () => {
      const content = 'test content';
      const output = new OutputFile(content);
      
      expect(output.content).toBe(content);
    });

    it('debe ser readonly', () => {
      const output = new OutputFile('test content');
      
      // Verificar que las propiedades existen y son accesibles
      expect(output.content).toBeDefined();
      expect(typeof output.content).toBe('string');
      expect(output.content).toBe('test content');
    });
  });

  describe('implementación de interfaz', () => {
    it('debe implementar la interfaz File', () => {
      const output = new OutputFile('test content');
      
      expect(output).toHaveProperty('content');
      expect(typeof output.content).toBe('string');
    });

    it('debe cumplir con el contrato de la interfaz File', () => {
      const content = 'test content';
      const output: File = new OutputFile(content);
      
      expect(output.content).toBe(content);
    });
  });

  describe('instanciación', () => {
    it('debe crear múltiples instancias independientes', () => {
      const output1 = new OutputFile('content1');
      const output2 = new OutputFile('content2');
      
      expect(output1.content).toBe('content1');
      expect(output2.content).toBe('content2');
      expect(output1).not.toBe(output2);
    });

    it('debe mantener el valor del content después de la instanciación', () => {
      const content = 'persistent content';
      const output = new OutputFile(content);
      
      // Verificar que el valor persiste
      expect(output.content).toBe(content);
      
      // Verificar que no cambia accidentalmente
      const currentContent = output.content;
      expect(currentContent).toBe(content);
    });
  });

  describe('tipos de contenido', () => {
    it('debe manejar contenido con caracteres especiales', () => {
      const content = 'áéíóú ñ ç @#$%^&*()';
      const output = new OutputFile(content);
      
      expect(output.content).toBe(content);
    });

    it('debe manejar contenido con números', () => {
      const content = '1234567890';
      const output = new OutputFile(content);
      
      expect(output.content).toBe(content);
    });

    it('debe manejar contenido con espacios', () => {
      const content = '   contenido con espacios   ';
      const output = new OutputFile(content);
      
      expect(output.content).toBe(content);
    });
  });
}); 
