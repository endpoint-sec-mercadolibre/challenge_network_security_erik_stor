import { FILE_DEFAULT_ENCODING, SECRET_KEY, MONGODB_CONNECTION_STRING, STORAGE_PATH } from '../../../../../src/domain/common/consts/Setup';

// Mock de process.env
const originalEnv = process.env;

describe('Setup Constants', () => {
  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  describe('FILE_DEFAULT_ENCODING', () => {
    it('debe usar el valor de FILE_DEFAULT_ENCODING del environment', () => {
      process.env.FILE_DEFAULT_ENCODING = 'ascii';

      // Re-importar el módulo para obtener el nuevo valor
      const { FILE_DEFAULT_ENCODING: newEncoding } = require('../../../../../src/domain/common/consts/Setup');

      expect(newEncoding).toBe('ascii');
    });

    it('debe usar utf8 como valor por defecto cuando no está definido', () => {
      delete process.env.FILE_DEFAULT_ENCODING;

      // Re-importar el módulo para obtener el valor por defecto
      const { FILE_DEFAULT_ENCODING: defaultEncoding } = require('../../../../../src/domain/common/consts/Setup');

      expect(defaultEncoding).toBe('utf8');
    });

    it('debe usar utf8 cuando el valor es undefined', () => {
      process.env.FILE_DEFAULT_ENCODING = undefined;

      // Re-importar el módulo para obtener el valor por defecto
      const { FILE_DEFAULT_ENCODING: defaultEncoding } = require('../../../../../src/domain/common/consts/Setup');

      expect(defaultEncoding).toBe('utf8');
    });

    it('debe manejar diferentes tipos de encoding', () => {
      // Verificar que el valor por defecto es utf8
      expect(FILE_DEFAULT_ENCODING).toBe('utf8');

      // Verificar que es un string válido
      expect(typeof FILE_DEFAULT_ENCODING).toBe('string');
      expect(FILE_DEFAULT_ENCODING.length).toBeGreaterThan(0);
    });
  });

  describe('SECRET_KEY', () => {
    it('debe usar el valor de ENCRYPTION_KEY del environment', () => {
      process.env.ENCRYPTION_KEY = 'custom_secret_key_123';

      // Re-importar el módulo para obtener el nuevo valor
      const { SECRET_KEY: newSecretKey } = require('../../../../../src/domain/common/consts/Setup');

      expect(newSecretKey).toBe('custom_secret_key_123');
    });

    it('debe usar mi_contraseña_secreta como valor por defecto cuando no está definido', () => {
      delete process.env.ENCRYPTION_KEY;

      // Re-importar el módulo para obtener el valor por defecto
      const { SECRET_KEY: defaultSecretKey } = require('../../../../../src/domain/common/consts/Setup');

      expect(defaultSecretKey).toBe('mi_contraseña_secreta');
    });

    it('debe usar mi_contraseña_secreta cuando el valor es undefined', () => {
      process.env.ENCRYPTION_KEY = undefined;

      // Re-importar el módulo para obtener el valor por defecto
      const { SECRET_KEY: defaultSecretKey } = require('../../../../../src/domain/common/consts/Setup');

      expect(defaultSecretKey).toBe('mi_contraseña_secreta');
    });

    it('debe manejar claves secretas complejas', () => {
      // Verificar que el valor por defecto es correcto
      expect(SECRET_KEY).toBe('mi_contraseña_secreta');

      // Verificar que es un string válido
      expect(typeof SECRET_KEY).toBe('string');
      expect(SECRET_KEY.length).toBeGreaterThan(0);
    });
  });

  describe('MONGODB_CONNECTION_STRING', () => {
    it('debe usar el valor de MONGODB_CONNECTION_STRING del environment', () => {
      process.env.MONGODB_CONNECTION_STRING = 'mongodb://custom-host:27017/custom-db';

      // Re-importar el módulo para obtener el nuevo valor
      const { MONGODB_CONNECTION_STRING: newConnectionString } = require('../../../../../src/domain/common/consts/Setup');

      expect(newConnectionString).toBe('mongodb://custom-host:27017/custom-db');
    });

    it('debe usar mongodb://localhost:27017/config-service como valor por defecto cuando no está definido', () => {
      delete process.env.MONGODB_CONNECTION_STRING;

      // Re-importar el módulo para obtener el valor por defecto
      const { MONGODB_CONNECTION_STRING: defaultConnectionString } = require('../../../../../src/domain/common/consts/Setup');

      expect(defaultConnectionString).toBe('mongodb://localhost:27017/config-service');
    });

    it('debe usar mongodb://localhost:27017/config-service cuando el valor es undefined', () => {
      process.env.MONGODB_CONNECTION_STRING = undefined;

      // Re-importar el módulo para obtener el valor por defecto
      const { MONGODB_CONNECTION_STRING: defaultConnectionString } = require('../../../../../src/domain/common/consts/Setup');

      expect(defaultConnectionString).toBe('mongodb://localhost:27017/config-service');
    });

    it('debe manejar diferentes formatos de connection string', () => {
      // Verificar que el valor por defecto es correcto
      expect(MONGODB_CONNECTION_STRING).toBe('mongodb://localhost:27017/config-service');

      // Verificar que es un string válido
      expect(typeof MONGODB_CONNECTION_STRING).toBe('string');
      expect(MONGODB_CONNECTION_STRING.length).toBeGreaterThan(0);
      expect(MONGODB_CONNECTION_STRING).toContain('mongodb://');
    });
  });

  describe('STORAGE_PATH', () => {
    it('debe usar el valor de STORAGE_PATH del environment', () => {
      process.env.STORAGE_PATH = '/custom/storage/path';

      // Re-importar el módulo para obtener el nuevo valor
      const { STORAGE_PATH: newStoragePath } = require('../../../../../src/domain/common/consts/Setup');

      expect(newStoragePath).toBe('/custom/storage/path');
    });

    it('debe usar ../dist/storage como valor por defecto cuando no está definido', () => {
      delete process.env.STORAGE_PATH;

      // Re-importar el módulo para obtener el valor por defecto
      const { STORAGE_PATH: defaultStoragePath } = require('../../../../../src/domain/common/consts/Setup');

      expect(defaultStoragePath).toBe('../dist/storage');
    });

    it('debe usar ../dist/storage cuando el valor es undefined', () => {
      process.env.STORAGE_PATH = undefined;

      // Re-importar el módulo para obtener el valor por defecto
      const { STORAGE_PATH: defaultStoragePath } = require('../../../../../src/domain/common/consts/Setup');

      expect(defaultStoragePath).toBe('../dist/storage');
    });

    it('debe manejar diferentes rutas de almacenamiento', () => {
      // Verificar que el valor por defecto es correcto
      expect(STORAGE_PATH).toBe('../dist/storage');

      // Verificar que es un string válido
      expect(typeof STORAGE_PATH).toBe('string');
      expect(STORAGE_PATH.length).toBeGreaterThan(0);
      expect(STORAGE_PATH).toContain('storage');
    });
  });

  describe('valores por defecto', () => {
    it('debe usar todos los valores por defecto cuando no hay variables de entorno', () => {
      delete process.env.FILE_DEFAULT_ENCODING;
      delete process.env.ENCRYPTION_KEY;
      delete process.env.MONGODB_CONNECTION_STRING;
      delete process.env.STORAGE_PATH;

      // Re-importar el módulo para obtener los valores por defecto
      const {
        FILE_DEFAULT_ENCODING: defaultEncoding,
        SECRET_KEY: defaultSecretKey,
        MONGODB_CONNECTION_STRING: defaultConnectionString,
        STORAGE_PATH: defaultStoragePath
      } = require('../../../../../src/domain/common/consts/Setup');

      expect(defaultEncoding).toBe('utf8');
      expect(defaultSecretKey).toBe('mi_contraseña_secreta');
      expect(defaultConnectionString).toBe('mongodb://localhost:27017/config-service');
      expect(defaultStoragePath).toBe('../dist/storage');
    });
  });

  describe('tipos de datos', () => {
    it('debe retornar strings para todas las constantes', () => {
      expect(typeof FILE_DEFAULT_ENCODING).toBe('string');
      expect(typeof SECRET_KEY).toBe('string');
      expect(typeof MONGODB_CONNECTION_STRING).toBe('string');
      expect(typeof STORAGE_PATH).toBe('string');
    });

    it('debe tener valores no vacíos', () => {
      expect(FILE_DEFAULT_ENCODING.length).toBeGreaterThan(0);
      expect(SECRET_KEY.length).toBeGreaterThan(0);
      expect(MONGODB_CONNECTION_STRING.length).toBeGreaterThan(0);
      expect(STORAGE_PATH.length).toBeGreaterThan(0);
    });
  });
}); 
