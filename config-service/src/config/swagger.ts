import swaggerJsdoc from 'swagger-jsdoc';
import path from 'path';

// Determinar el entorno y las rutas apropiadas
const isProduction = process.env.NODE_ENV === 'production';
const cwd = process.cwd();

// Configurar las rutas de APIs según el entorno
let apiPaths: string[] = [];

if (isProduction) {
  // En producción, usar solo archivos JavaScript compilados
  apiPaths = [
    path.join(cwd, 'dist', '**/*.js')
  ];
} else {
  // En desarrollo, usar archivos TypeScript
  apiPaths = [
    path.join(cwd, 'src', '**/*.ts')
  ];
}

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Config Service API',
      version: '1.0.0',
      description: 'API para el microservicio de configuración que implementa arquitectura hexagonal',
    },
    servers: [
      {
        url: `http://localhost:${process.env.PORT || 8000}`,
        description: 'Servidor de desarrollo'
      }
    ],
    components: {
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
  apis: apiPaths
};

export const specs = swaggerJsdoc(options);
