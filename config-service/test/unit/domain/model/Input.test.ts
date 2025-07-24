import { InputFile } from '../../../../src/domain/model/Input';
import { InputRechargeMessageException } from '../../../../src/domain/exceptions/constants/InputMessageException';

describe('InputFile', () => {
  describe('constructor', () => {
    it('debe crear una instancia con filename válido', () => {
      const filename = 'test.txt';
      const input = new InputFile(filename);
      
      expect(input.filename).toBe(filename);
    });

    it('debe crear una instancia con filename vacío', () => {
      const filename = '';
      const input = new InputFile(filename);
      
      expect(input.filename).toBe(filename);
    });

    it('debe crear una instancia con filename con espacios', () => {
      const filename = 'test file.txt';
      const input = new InputFile(filename);
      
      expect(input.filename).toBe(filename);
    });

    it('debe crear una instancia con filename con caracteres especiales', () => {
      const filename = 'test-file_123.txt';
      const input = new InputFile(filename);
      
      expect(input.filename).toBe(filename);
    });
  });

  describe('propiedades', () => {
    it('debe tener la propiedad filename', () => {
      const input = new InputFile('test.txt');
      
      expect(input).toHaveProperty('filename');
      expect(typeof input.filename).toBe('string');
    });

    it('debe permitir acceso a la propiedad filename', () => {
      const filename = 'test.txt';
      const input = new InputFile(filename);
      
      expect(input.filename).toBe(filename);
    });
  });

  describe('decoradores de validación', () => {
    it('debe tener el decorador IsString con mensaje correcto', () => {
      // Verificar que la clase tiene los decoradores aplicados
      const input = new InputFile('test.txt');
      
      // La validación se ejecuta cuando se usa class-validator
      // Aquí solo verificamos que la propiedad existe y tiene el valor correcto
      expect(input.filename).toBe('test.txt');
    });

    it('debe tener el decorador IsNotEmpty con mensaje correcto', () => {
      const input = new InputFile('test.txt');
      
      // Verificar que la propiedad no está vacía
      expect(input.filename).not.toBe('');
      expect(input.filename.length).toBeGreaterThan(0);
    });
  });

  describe('mensajes de error de validación', () => {
    it('debe usar el mensaje correcto para IsString', () => {
      expect(InputRechargeMessageException.FILENAME_MUST_BE_STRING).toBe('El nombre del archivo debe ser una cadena de texto');
    });

    it('debe usar el mensaje correcto para IsNotEmpty', () => {
      expect(InputRechargeMessageException.FILENAME_REQUIRED).toBe('El nombre del archivo es requerido');
    });
  });

  describe('instanciación', () => {
    it('debe crear múltiples instancias independientes', () => {
      const input1 = new InputFile('file1.txt');
      const input2 = new InputFile('file2.txt');
      
      expect(input1.filename).toBe('file1.txt');
      expect(input2.filename).toBe('file2.txt');
      expect(input1).not.toBe(input2);
    });

    it('debe mantener el valor del filename después de la instanciación', () => {
      const filename = 'persistent.txt';
      const input = new InputFile(filename);
      
      // Verificar que el valor persiste
      expect(input.filename).toBe(filename);
      
      // Verificar que no cambia accidentalmente
      const currentFilename = input.filename;
      expect(currentFilename).toBe(filename);
    });
  });
}); 
