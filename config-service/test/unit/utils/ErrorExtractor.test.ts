import { 
  extractValidationErrors, 
  flattenErrorMessages, 
  errorsToObject, 
  createSummaryMessage,
  ExtractedError,
  ErrorExtractionResult
} from '../../../src/utils/ErrorExtractor';
import { ValidationError } from 'class-validator';

describe('ErrorExtractor', () => {
  describe('extractValidationErrors', () => {
    it('debería retornar resultado vacío cuando no hay errores', () => {
      const result = extractValidationErrors([]);

      expect(result).toEqual({
        errors: [],
        hasErrors: false,
        errorCount: 0
      });
    });

    it('debería retornar resultado vacío cuando validationErrors es null', () => {
      const result = extractValidationErrors(null as any);

      expect(result).toEqual({
        errors: [],
        hasErrors: false,
        errorCount: 0
      });
    });

    it('debería retornar resultado vacío cuando validationErrors es undefined', () => {
      const result = extractValidationErrors(undefined as any);

      expect(result).toEqual({
        errors: [],
        hasErrors: false,
        errorCount: 0
      });
    });

    it('debería extraer errores simples correctamente', () => {
      const validationErrors: ValidationError[] = [
        {
          target: { name: '', email: 'invalid' },
          value: '',
          property: 'name',
          children: [],
          constraints: {
            isNotEmpty: 'El nombre no puede estar vacío',
            minLength: 'El nombre debe tener al menos 2 caracteres'
          }
        },
        {
          target: { name: '', email: 'invalid' },
          value: 'invalid',
          property: 'email',
          children: [],
          constraints: {
            isEmail: 'El email debe ser válido'
          }
        }
      ];

      const result = extractValidationErrors(validationErrors);

      expect(result.hasErrors).toBe(true);
      expect(result.errorCount).toBe(3);
      expect(result.errors).toHaveLength(2);
      expect(result.errors[0]).toEqual({
        field: 'name',
        messages: ['El nombre no puede estar vacío', 'El nombre debe tener al menos 2 caracteres']
      });
      expect(result.errors[1]).toEqual({
        field: 'email',
        messages: ['El email debe ser válido']
      });
    });

    it('debería manejar errores con constraints vacíos', () => {
      const validationErrors: ValidationError[] = [
        {
          target: { name: '' },
          value: '',
          property: 'name',
          children: [],
          constraints: {}
        }
      ];

      const result = extractValidationErrors(validationErrors);

      expect(result.hasErrors).toBe(false);
      expect(result.errorCount).toBe(0);
      expect(result.errors).toHaveLength(0);
    });

    it('debería manejar errores con constraints que contienen valores no string', () => {
      const validationErrors: ValidationError[] = [
        {
          target: { name: '' },
          value: '',
          property: 'name',
          children: [],
          constraints: {
            isNotEmpty: 'El nombre no puede estar vacío',
            minLength: null as any,
            maxLength: undefined as any,
            pattern: 123 as any
          }
        }
      ];

      const result = extractValidationErrors(validationErrors);

      expect(result.hasErrors).toBe(true);
      expect(result.errorCount).toBe(1);
      expect(result.errors[0].messages).toEqual(['El nombre no puede estar vacío']);
    });

    it('debería extraer errores anidados correctamente', () => {
      const validationErrors: ValidationError[] = [
        {
          target: { address: { street: '', city: '' } },
          value: { street: '', city: '' },
          property: 'address',
          children: [
            {
              target: { street: '', city: '' },
              value: '',
              property: 'street',
              children: [],
              constraints: {
                isNotEmpty: 'La calle no puede estar vacía'
              }
            },
            {
              target: { street: '', city: '' },
              value: '',
              property: 'city',
              children: [],
              constraints: {
                isNotEmpty: 'La ciudad no puede estar vacía'
              }
            }
          ],
          constraints: {}
        }
      ];

      const result = extractValidationErrors(validationErrors);

      expect(result.hasErrors).toBe(true);
      expect(result.errorCount).toBe(2);
      expect(result.errors).toHaveLength(2);
      expect(result.errors[0]).toEqual({
        field: 'address.street',
        messages: ['La calle no puede estar vacía']
      });
      expect(result.errors[1]).toEqual({
        field: 'address.city',
        messages: ['La ciudad no puede estar vacía']
      });
    });

    it('debería manejar errores anidados múltiples niveles', () => {
      const validationErrors: ValidationError[] = [
        {
          target: { user: { profile: { personal: { name: '' } } } },
          value: { profile: { personal: { name: '' } } },
          property: 'user',
          children: [
            {
              target: { profile: { personal: { name: '' } } },
              value: { personal: { name: '' } },
              property: 'profile',
              children: [
                {
                  target: { personal: { name: '' } },
                  value: { name: '' },
                  property: 'personal',
                  children: [
                    {
                      target: { name: '' },
                      value: '',
                      property: 'name',
                      children: [],
                      constraints: {
                        isNotEmpty: 'El nombre no puede estar vacío'
                      }
                    }
                  ],
                  constraints: {}
                }
              ],
              constraints: {}
            }
          ],
          constraints: {}
        }
      ];

      const result = extractValidationErrors(validationErrors);

      expect(result.hasErrors).toBe(true);
      expect(result.errorCount).toBe(1);
      expect(result.errors[0]).toEqual({
        field: 'user.profile.personal.name',
        messages: ['El nombre no puede estar vacío']
      });
    });

    it('debería combinar errores del mismo campo', () => {
      const validationErrors: ValidationError[] = [
        {
          target: { name: '' },
          value: '',
          property: 'name',
          children: [],
          constraints: {
            isNotEmpty: 'El nombre no puede estar vacío'
          }
        },
        {
          target: { name: '' },
          value: '',
          property: 'name',
          children: [],
          constraints: {
            minLength: 'El nombre debe tener al menos 2 caracteres'
          }
        }
      ];

      const result = extractValidationErrors(validationErrors);

      expect(result.hasErrors).toBe(true);
      expect(result.errorCount).toBe(2);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0]).toEqual({
        field: 'name',
        messages: ['El nombre no puede estar vacío', 'El nombre debe tener al menos 2 caracteres']
      });
    });

    it('debería manejar errores anidados con errores del campo padre', () => {
      const validationErrors: ValidationError[] = [
        {
          target: { address: { street: '' } },
          value: { street: '' },
          property: 'address',
          children: [
            {
              target: { street: '' },
              value: '',
              property: 'street',
              children: [],
              constraints: {
                isNotEmpty: 'La calle no puede estar vacía'
              }
            }
          ],
          constraints: {
            isNotEmpty: 'La dirección no puede estar vacía'
          }
        }
      ];

      const result = extractValidationErrors(validationErrors);

      expect(result.hasErrors).toBe(true);
      expect(result.errorCount).toBe(2);
      expect(result.errors).toHaveLength(2);
      expect(result.errors.find(e => e.field === 'address')).toEqual({
        field: 'address',
        messages: ['La dirección no puede estar vacía']
      });
      expect(result.errors.find(e => e.field === 'address.street')).toEqual({
        field: 'address.street',
        messages: ['La calle no puede estar vacía']
      });
    });
  });

  describe('flattenErrorMessages', () => {
    it('debería convertir errores extraídos a array plano de mensajes', () => {
      const extractedErrors: ErrorExtractionResult = {
        errors: [
          {
            field: 'name',
            messages: ['El nombre no puede estar vacío', 'El nombre debe tener al menos 2 caracteres']
          },
          {
            field: 'email',
            messages: ['El email debe ser válido']
          }
        ],
        hasErrors: true,
        errorCount: 3
      };

      const result = flattenErrorMessages(extractedErrors);

      expect(result).toEqual([
        'El nombre no puede estar vacío',
        'El nombre debe tener al menos 2 caracteres',
        'El email debe ser válido'
      ]);
    });

    it('debería retornar array vacío cuando no hay errores', () => {
      const extractedErrors: ErrorExtractionResult = {
        errors: [],
        hasErrors: false,
        errorCount: 0
      };

      const result = flattenErrorMessages(extractedErrors);

      expect(result).toEqual([]);
    });

    it('debería manejar errores con un solo mensaje', () => {
      const extractedErrors: ErrorExtractionResult = {
        errors: [
          {
            field: 'name',
            messages: ['El nombre no puede estar vacío']
          }
        ],
        hasErrors: true,
        errorCount: 1
      };

      const result = flattenErrorMessages(extractedErrors);

      expect(result).toEqual(['El nombre no puede estar vacío']);
    });
  });

  describe('errorsToObject', () => {
    it('debería convertir errores extraídos a objeto plano', () => {
      const extractedErrors: ErrorExtractionResult = {
        errors: [
          {
            field: 'name',
            messages: ['El nombre no puede estar vacío', 'El nombre debe tener al menos 2 caracteres']
          },
          {
            field: 'email',
            messages: ['El email debe ser válido']
          }
        ],
        hasErrors: true,
        errorCount: 3
      };

      const result = errorsToObject(extractedErrors);

      expect(result).toEqual({
        name: ['El nombre no puede estar vacío', 'El nombre debe tener al menos 2 caracteres'],
        email: ['El email debe ser válido']
      });
    });

    it('debería retornar objeto vacío cuando no hay errores', () => {
      const extractedErrors: ErrorExtractionResult = {
        errors: [],
        hasErrors: false,
        errorCount: 0
      };

      const result = errorsToObject(extractedErrors);

      expect(result).toEqual({});
    });

    it('debería manejar errores con un solo mensaje', () => {
      const extractedErrors: ErrorExtractionResult = {
        errors: [
          {
            field: 'name',
            messages: ['El nombre no puede estar vacío']
          }
        ],
        hasErrors: true,
        errorCount: 1
      };

      const result = errorsToObject(extractedErrors);

      expect(result).toEqual({
        name: ['El nombre no puede estar vacío']
      });
    });

    it('debería manejar campos anidados en el objeto', () => {
      const extractedErrors: ErrorExtractionResult = {
        errors: [
          {
            field: 'address.street',
            messages: ['La calle no puede estar vacía']
          },
          {
            field: 'address.city',
            messages: ['La ciudad no puede estar vacía']
          }
        ],
        hasErrors: true,
        errorCount: 2
      };

      const result = errorsToObject(extractedErrors);

      expect(result).toEqual({
        'address.street': ['La calle no puede estar vacía'],
        'address.city': ['La ciudad no puede estar vacía']
      });
    });
  });

  describe('createSummaryMessage', () => {
    it('debería crear mensaje resumido cuando hay errores', () => {
      const extractedErrors: ErrorExtractionResult = {
        errors: [
          {
            field: 'name',
            messages: ['El nombre no puede estar vacío', 'El nombre debe tener al menos 2 caracteres']
          },
          {
            field: 'email',
            messages: ['El email debe ser válido']
          }
        ],
        hasErrors: true,
        errorCount: 3
      };

      const result = createSummaryMessage(extractedErrors);

      expect(result).toBe('Se encontraron 3 error(es) de validación en 2 campo(s)');
    });

    it('debería crear mensaje resumido con un solo error', () => {
      const extractedErrors: ErrorExtractionResult = {
        errors: [
          {
            field: 'name',
            messages: ['El nombre no puede estar vacío']
          }
        ],
        hasErrors: true,
        errorCount: 1
      };

      const result = createSummaryMessage(extractedErrors);

      expect(result).toBe('Se encontraron 1 error(es) de validación en 1 campo(s)');
    });

    it('debería crear mensaje cuando no hay errores', () => {
      const extractedErrors: ErrorExtractionResult = {
        errors: [],
        hasErrors: false,
        errorCount: 0
      };

      const result = createSummaryMessage(extractedErrors);

      expect(result).toBe('No hay errores de validación');
    });

    it('debería manejar múltiples errores en un solo campo', () => {
      const extractedErrors: ErrorExtractionResult = {
        errors: [
          {
            field: 'name',
            messages: ['El nombre no puede estar vacío', 'El nombre debe tener al menos 2 caracteres', 'El nombre debe tener máximo 50 caracteres']
          }
        ],
        hasErrors: true,
        errorCount: 3
      };

      const result = createSummaryMessage(extractedErrors);

      expect(result).toBe('Se encontraron 3 error(es) de validación en 1 campo(s)');
    });
  });

  describe('integración completa', () => {
    it('debería manejar un flujo completo de extracción y procesamiento', () => {
      const validationErrors: ValidationError[] = [
        {
          target: { name: '', email: 'invalid', age: -5 },
          value: '',
          property: 'name',
          children: [],
          constraints: {
            isNotEmpty: 'El nombre no puede estar vacío',
            minLength: 'El nombre debe tener al menos 2 caracteres'
          }
        },
        {
          target: { name: '', email: 'invalid', age: -5 },
          value: 'invalid',
          property: 'email',
          children: [],
          constraints: {
            isEmail: 'El email debe ser válido'
          }
        },
        {
          target: { name: '', email: 'invalid', age: -5 },
          value: -5,
          property: 'age',
          children: [],
          constraints: {
            min: 'La edad debe ser mayor a 0'
          }
        }
      ];

      // Extraer errores
      const extractedErrors = extractValidationErrors(validationErrors);

      expect(extractedErrors.hasErrors).toBe(true);
      expect(extractedErrors.errorCount).toBe(4);
      expect(extractedErrors.errors).toHaveLength(3);

      // Aplanar mensajes
      const flatMessages = flattenErrorMessages(extractedErrors);
      expect(flatMessages).toHaveLength(4);
      expect(flatMessages).toContain('El nombre no puede estar vacío');
      expect(flatMessages).toContain('El email debe ser válido');
      expect(flatMessages).toContain('La edad debe ser mayor a 0');

      // Convertir a objeto
      const errorObject = errorsToObject(extractedErrors);
      expect(errorObject.name).toHaveLength(2);
      expect(errorObject.email).toHaveLength(1);
      expect(errorObject.age).toHaveLength(1);

      // Crear mensaje resumido
      const summary = createSummaryMessage(extractedErrors);
      expect(summary).toBe('Se encontraron 4 error(es) de validación en 3 campo(s)');
    });
  });

  describe('casos edge', () => {
    it('debería manejar errores con campos vacíos', () => {
      const validationErrors: ValidationError[] = [
        {
          target: { '': 'value' },
          value: 'value',
          property: '',
          children: [],
          constraints: {
            isNotEmpty: 'El campo no puede estar vacío'
          }
        }
      ];

      const result = extractValidationErrors(validationErrors);

      expect(result.hasErrors).toBe(true);
      expect(result.errors[0].field).toBe('');
    });

    it('debería manejar errores con mensajes muy largos', () => {
      const longMessage = 'a'.repeat(1000);
      const validationErrors: ValidationError[] = [
        {
          target: { name: '' },
          value: '',
          property: 'name',
          children: [],
          constraints: {
            isNotEmpty: longMessage
          }
        }
      ];

      const result = extractValidationErrors(validationErrors);

      expect(result.hasErrors).toBe(true);
      expect(result.errors[0].messages[0]).toBe(longMessage);
    });

    it('debería manejar errores con caracteres especiales en los campos', () => {
      const validationErrors: ValidationError[] = [
        {
          target: { 'field-with-dashes': '', 'field_with_underscores': '' },
          value: '',
          property: 'field-with-dashes',
          children: [],
          constraints: {
            isNotEmpty: 'El campo no puede estar vacío'
          }
        },
        {
          target: { 'field-with-dashes': '', 'field_with_underscores': '' },
          value: '',
          property: 'field_with_underscores',
          children: [],
          constraints: {
            isNotEmpty: 'El campo no puede estar vacío'
          }
        }
      ];

      const result = extractValidationErrors(validationErrors);

      expect(result.hasErrors).toBe(true);
      expect(result.errors).toHaveLength(2);
      expect(result.errors[0].field).toBe('field-with-dashes');
      expect(result.errors[1].field).toBe('field_with_underscores');
    });

    it('debería manejar errores anidados con campos duplicados', () => {
      const validationErrors: ValidationError[] = [
        {
          target: { address: { street: '' } },
          value: { street: '' },
          property: 'address',
          children: [
            {
              target: { street: '' },
              value: '',
              property: 'street',
              children: [],
              constraints: {
                isNotEmpty: 'La calle no puede estar vacía'
              }
            }
          ],
          constraints: {}
        },
        {
          target: { address: { street: '' } },
          value: { street: '' },
          property: 'address',
          children: [
            {
              target: { street: '' },
              value: '',
              property: 'street',
              children: [],
              constraints: {
                minLength: 'La calle debe tener al menos 3 caracteres'
              }
            }
          ],
          constraints: {}
        }
      ];

      const result = extractValidationErrors(validationErrors);

      expect(result.hasErrors).toBe(true);
      expect(result.errorCount).toBe(2);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].field).toBe('address.street');
      expect(result.errors[0].messages).toContain('La calle no puede estar vacía');
      expect(result.errors[0].messages).toContain('La calle debe tener al menos 3 caracteres');
    });
  });
}); 
