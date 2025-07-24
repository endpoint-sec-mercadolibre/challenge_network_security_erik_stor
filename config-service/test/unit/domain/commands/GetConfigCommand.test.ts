import { GetConfigCommand } from '../../../../src/domain/commands/GetConfigCommand';
import { InputFile } from '../../../../src/domain/model/Input';

describe('GetConfigCommand', () => {
  describe('constructor', () => {
    it('debe crear una instancia con request válido', () => {
      const inputFile = new InputFile('test.txt');
      const command = new GetConfigCommand(inputFile);
      
      expect(command.request).toBe(inputFile);
    });

    it('debe crear una instancia con InputFile que tiene filename', () => {
      const inputFile = new InputFile('config.json');
      const command = new GetConfigCommand(inputFile);
      
      expect(command.request.filename).toBe('config.json');
    });

    it('debe crear múltiples instancias independientes', () => {
      const inputFile1 = new InputFile('file1.txt');
      const inputFile2 = new InputFile('file2.txt');
      
      const command1 = new GetConfigCommand(inputFile1);
      const command2 = new GetConfigCommand(inputFile2);
      
      expect(command1.request).toBe(inputFile1);
      expect(command2.request).toBe(inputFile2);
      expect(command1).not.toBe(command2);
    });
  });

  describe('propiedades', () => {
    it('debe tener la propiedad request readonly', () => {
      const inputFile = new InputFile('test.txt');
      const command = new GetConfigCommand(inputFile);
      
      expect(command).toHaveProperty('request');
      expect(command.request).toBe(inputFile);
    });

    it('debe permitir acceso a la propiedad request', () => {
      const inputFile = new InputFile('test.txt');
      const command = new GetConfigCommand(inputFile);
      
      expect(command.request).toBe(inputFile);
      expect(command.request.filename).toBe('test.txt');
    });

    it('debe ser readonly', () => {
      const inputFile = new InputFile('test.txt');
      const command = new GetConfigCommand(inputFile);
      
      // Verificar que la propiedad existe y es accesible
      expect(command.request).toBeDefined();
      expect(command.request).toBeInstanceOf(InputFile);
    });
  });

  describe('tipos de InputFile', () => {
    it('debe manejar InputFile con filename simple', () => {
      const inputFile = new InputFile('simple.txt');
      const command = new GetConfigCommand(inputFile);
      
      expect(command.request.filename).toBe('simple.txt');
    });

    it('debe manejar InputFile con filename con espacios', () => {
      const inputFile = new InputFile('file with spaces.txt');
      const command = new GetConfigCommand(inputFile);
      
      expect(command.request.filename).toBe('file with spaces.txt');
    });

    it('debe manejar InputFile con filename con caracteres especiales', () => {
      const inputFile = new InputFile('file-name_123.json');
      const command = new GetConfigCommand(inputFile);
      
      expect(command.request.filename).toBe('file-name_123.json');
    });

    it('debe manejar InputFile con filename vacío', () => {
      const inputFile = new InputFile('');
      const command = new GetConfigCommand(inputFile);
      
      expect(command.request.filename).toBe('');
    });
  });

  describe('instanciación', () => {
    it('debe mantener el valor del request después de la instanciación', () => {
      const inputFile = new InputFile('persistent.txt');
      const command = new GetConfigCommand(inputFile);
      
      // Verificar que el valor persiste
      expect(command.request).toBe(inputFile);
      
      // Verificar que no cambia accidentalmente
      const currentRequest = command.request;
      expect(currentRequest).toBe(inputFile);
    });

    it('debe crear instancias con diferentes tipos de archivo', () => {
      const fileTypes = [
        'config.json',
        'settings.yaml',
        'data.csv',
        'document.pdf',
        'script.js',
        'style.css'
      ];
      
      fileTypes.forEach(filename => {
        const inputFile = new InputFile(filename);
        const command = new GetConfigCommand(inputFile);
        
        expect(command.request.filename).toBe(filename);
      });
    });
  });

  describe('estructura de datos', () => {
    it('debe tener la estructura correcta', () => {
      const inputFile = new InputFile('test.txt');
      const command = new GetConfigCommand(inputFile);
      
      expect(command).toHaveProperty('request');
      expect(typeof command.request).toBe('object');
      expect(command.request).toBeInstanceOf(InputFile);
    });

    it('debe permitir acceso anidado a propiedades', () => {
      const inputFile = new InputFile('nested/file/path.txt');
      const command = new GetConfigCommand(inputFile);
      
      expect(command.request.filename).toBe('nested/file/path.txt');
    });
  });
}); 
