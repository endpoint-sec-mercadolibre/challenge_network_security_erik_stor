// Mock de swagger-jsdoc
jest.mock('swagger-jsdoc');

// Mock de path
jest.mock('path', () => ({
  join: jest.fn()
}));

// Mock de process
const mockProcess = {
  env: {} as any,
  cwd: jest.fn()
};

// Mock de process.cwd
Object.defineProperty(global, 'process', {
  value: mockProcess,
  writable: true
});

// Importar después de configurar los mocks

describe('Swagger Configuration', () => {
  let mockSwaggerJsdoc: jest.MockedFunction<any>;
  let mockPathJoin: jest.MockedFunction<any>;
  let mockProcess: any;

  beforeEach(() => {
    // Configurar mocks antes de cada test
    jest.resetModules();

    // Mock de swagger-jsdoc
    mockSwaggerJsdoc = jest.fn().mockReturnValue({});
    jest.doMock('swagger-jsdoc', () => mockSwaggerJsdoc);

    // Mock de path
    mockPathJoin = jest.fn().mockImplementation((...args: any[]) => args.join('/'));
    jest.doMock('path', () => ({
      join: mockPathJoin
    }));

    // Mock de process
    mockProcess = {
      env: {},
      cwd: jest.fn().mockReturnValue('/test/working/directory')
    };

    // Mock de process global
    Object.defineProperty(global, 'process', {
      value: mockProcess,
      writable: true
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Configuración en entorno de desarrollo', () => {
    beforeEach(() => {
      mockProcess.env = {
        NODE_ENV: 'development',
        PORT: '3000'
      };
    });

    it('debería configurar swagger con archivos TypeScript en desarrollo', () => {
      // Importar después de configurar los mocks
      require('../../../src/config/swagger');

      expect(mockSwaggerJsdoc).toHaveBeenCalledWith({
        definition: {
          openapi: '3.0.0',
          info: {
            title: 'Config Service API',
            version: '1.0.0',
            description: 'API para el microservicio de configuración que implementa arquitectura hexagonal',
          },
          servers: [
            {
              url: 'http://localhost:3000',
              description: 'Servidor de desarrollo'
            }
          ],
          components: {
            securitySchemes: {
              bearerAuth: {
                type: 'http',
                scheme: 'bearer',
                bearerFormat: 'JWT',
                description: 'Token JWT obtenido del servicio de autenticación'
              }
            },
            schemas: {
              ConfigResponse: {
                type: 'object',
                properties: {
                  message: {
                    type: 'string',
                    example: 'Archivo leído exitosamente'
                  },
                  data: {
                    type: 'object',
                    properties: {
                      message: {
                        type: 'string',
                        example: 'Archivo leído exitosamente'
                      },
                      content: {
                        type: 'string',
                        example: 'Contenido del archivo de configuración...'
                      }
                    }
                  }
                }
              },
              ErrorResponse: {
                type: 'object',
                properties: {
                  error: {
                    type: 'string',
                    example: 'Error de validación'
                  },
                  message: {
                    type: 'string',
                    example: 'El archivo especificado no existe'
                  },
                  code: {
                    type: 'string',
                    example: 'AUTH_TOKEN_REQUIRED'
                  },
                  details: {
                    type: 'array',
                    items: {
                      type: 'string'
                    },
                    example: ['El campo filename es requerido']
                  }
                }
              },
              HealthResponse: {
                type: 'object',
                properties: {
                  status: {
                    type: 'string',
                    example: 'OK'
                  },
                  timestamp: {
                    type: 'string',
                    format: 'date-time',
                    example: '2024-01-15T10:30:00.000Z'
                  },
                  service: {
                    type: 'string',
                    example: 'config-service'
                  }
                }
              }
            }
          },
          tags: [
            {
              name: 'Configuración',
              description: 'Endpoints para la gestión de configuraciones'
            },
            {
              name: 'Salud',
              description: 'Endpoints para verificar el estado del servicio'
            }
          ]
        },
        apis: ['/test/working/directory/src/**/*.ts']
      });

      expect(mockPathJoin).toHaveBeenCalledWith('/test/working/directory', 'src', '**/*.ts');
    });

    it('debería usar puerto por defecto 8000 cuando PORT no está definido', () => {
      mockProcess.env = {
        NODE_ENV: 'development'
        // PORT no definido
      };

      require('../../../src/config/swagger');

      expect(mockSwaggerJsdoc).toHaveBeenCalledWith(
        expect.objectContaining({
          definition: expect.objectContaining({
            servers: [
              {
                url: 'http://localhost:8000',
                description: 'Servidor de desarrollo'
              }
            ]
          })
        })
      );
    });
  });

  describe('Configuración en entorno de producción', () => {
    beforeEach(() => {
      mockProcess.env = {
        NODE_ENV: 'production',
        PORT: '8080'
      };
    });

    it('debería configurar swagger con archivos JavaScript en producción', () => {
      require('../../../src/config/swagger');

      expect(mockSwaggerJsdoc).toHaveBeenCalledWith({
        definition: {
          openapi: '3.0.0',
          info: {
            title: 'Config Service API',
            version: '1.0.0',
            description: 'API para el microservicio de configuración que implementa arquitectura hexagonal',
          },
          servers: [
            {
              url: 'http://localhost:8080',
              description: 'Servidor de desarrollo'
            }
          ],
          components: {
            securitySchemes: {
              bearerAuth: {
                type: 'http',
                scheme: 'bearer',
                bearerFormat: 'JWT',
                description: 'Token JWT obtenido del servicio de autenticación'
              }
            },
            schemas: {
              ConfigResponse: {
                type: 'object',
                properties: {
                  message: {
                    type: 'string',
                    example: 'Archivo leído exitosamente'
                  },
                  data: {
                    type: 'object',
                    properties: {
                      message: {
                        type: 'string',
                        example: 'Archivo leído exitosamente'
                      },
                      content: {
                        type: 'string',
                        example: 'Contenido del archivo de configuración...'
                      }
                    }
                  }
                }
              },
              ErrorResponse: {
                type: 'object',
                properties: {
                  error: {
                    type: 'string',
                    example: 'Error de validación'
                  },
                  message: {
                    type: 'string',
                    example: 'El archivo especificado no existe'
                  },
                  code: {
                    type: 'string',
                    example: 'AUTH_TOKEN_REQUIRED'
                  },
                  details: {
                    type: 'array',
                    items: {
                      type: 'string'
                    },
                    example: ['El campo filename es requerido']
                  }
                }
              },
              HealthResponse: {
                type: 'object',
                properties: {
                  status: {
                    type: 'string',
                    example: 'OK'
                  },
                  timestamp: {
                    type: 'string',
                    format: 'date-time',
                    example: '2024-01-15T10:30:00.000Z'
                  },
                  service: {
                    type: 'string',
                    example: 'config-service'
                  }
                }
              }
            }
          },
          tags: [
            {
              name: 'Configuración',
              description: 'Endpoints para la gestión de configuraciones'
            },
            {
              name: 'Salud',
              description: 'Endpoints para verificar el estado del servicio'
            }
          ]
        },
        apis: ['/test/working/directory/dist/**/*.js']
      });

      expect(mockPathJoin).toHaveBeenCalledWith('/test/working/directory', 'dist', '**/*.js');
    });
  });

  describe('Configuración con NODE_ENV no definido', () => {
    beforeEach(() => {
      mockProcess.env = {
        PORT: '5000'
        // NODE_ENV no definido
      };
    });

    it('debería usar configuración de desarrollo cuando NODE_ENV no está definido', () => {
      require('../../../src/config/swagger');

      expect(mockSwaggerJsdoc).toHaveBeenCalledWith(
        expect.objectContaining({
          apis: ['/test/working/directory/src/**/*.ts']
        })
      );

      expect(mockPathJoin).toHaveBeenCalledWith('/test/working/directory', 'src', '**/*.ts');
    });
  });

  describe('Estructura de la configuración', () => {
    beforeEach(() => {
      mockProcess.env = {
        NODE_ENV: 'development',
        PORT: '3000'
      };
    });

    it('debería tener la estructura correcta de OpenAPI 3.0.0', () => {
      require('../../../src/config/swagger');

      const callArgs = mockSwaggerJsdoc.mock.calls[0][0]!;
      expect(callArgs).toBeDefined();
      expect(callArgs.definition).toBeDefined();

      expect(callArgs.definition!.openapi).toBe('3.0.0');
      expect(callArgs.definition!.info.title).toBe('Config Service API');
      expect(callArgs.definition!.info.version).toBe('1.0.0');
      expect(callArgs.definition!.info.description).toBe('API para el microservicio de configuración que implementa arquitectura hexagonal');
    });

    it('debería incluir el esquema de autenticación Bearer', () => {
      require('../../../src/config/swagger');

      const callArgs = mockSwaggerJsdoc.mock.calls[0][0]!;

      expect(callArgs.definition!.components.securitySchemes.bearerAuth).toEqual({
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
        description: 'Token JWT obtenido del servicio de autenticación'
      });
    });

    it('debería incluir todos los esquemas de respuesta definidos', () => {
      require('../../../src/config/swagger');

      const callArgs = mockSwaggerJsdoc.mock.calls[0][0]!;
      const schemas = callArgs.definition!.components.schemas;

      expect(schemas).toHaveProperty('ConfigResponse');
      expect(schemas).toHaveProperty('ErrorResponse');
      expect(schemas).toHaveProperty('HealthResponse');
    });

    it('debería incluir los tags correctos', () => {
      require('../../../src/config/swagger');

      const callArgs = mockSwaggerJsdoc.mock.calls[0][0]!;

      expect(callArgs.definition!.tags).toEqual([
        {
          name: 'Configuración',
          description: 'Endpoints para la gestión de configuraciones'
        },
        {
          name: 'Salud',
          description: 'Endpoints para verificar el estado del servicio'
        }
      ]);
    });

    it('debería exportar las especificaciones correctamente', () => {
      const { specs } = require('../../../src/config/swagger');

      expect(specs).toBeDefined();
      expect(mockSwaggerJsdoc).toHaveBeenCalledTimes(1);
    });
  });

  describe('Validación de rutas de archivos', () => {
    beforeEach(() => {
      mockProcess.env = {
        NODE_ENV: 'development',
        PORT: '3000'
      };
    });

    it('debería usar path.join correctamente para construir rutas', () => {
      require('../../../src/config/swagger');

      expect(mockPathJoin).toHaveBeenCalledWith('/test/working/directory', 'src', '**/*.ts');
    });

    it('debería usar path.join correctamente para rutas de producción', () => {
      mockProcess.env.NODE_ENV = 'production';

      require('../../../src/config/swagger');

      expect(mockPathJoin).toHaveBeenCalledWith('/test/working/directory', 'dist', '**/*.js');
    });
  });

  describe('Manejo de variables de entorno', () => {
    it('debería manejar PORT como string', () => {
      mockProcess.env = {
        NODE_ENV: 'development',
        PORT: '9999'
      };

      require('../../../src/config/swagger');

      const callArgs = mockSwaggerJsdoc.mock.calls[0][0]!;
      expect(callArgs.definition!.servers[0].url).toBe('http://localhost:9999');
    });

    it('debería manejar PORT como número', () => {
      mockProcess.env = {
        NODE_ENV: 'development',
        PORT: 1234
      };

      require('../../../src/config/swagger');

      const callArgs = mockSwaggerJsdoc.mock.calls[0][0]!;
      expect(callArgs.definition!.servers[0].url).toBe('http://localhost:1234');
    });
  });
}); 
