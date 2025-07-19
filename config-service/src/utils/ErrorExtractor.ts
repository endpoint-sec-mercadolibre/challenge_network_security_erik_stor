import { ValidationError } from 'class-validator';

export interface ExtractedError {
  field: string;
  messages: string[];
}

export interface ErrorExtractionResult {
  errors: ExtractedError[];
  hasErrors: boolean;
  errorCount: number;
}

/**
 * Extrae y formatea los mensajes de error de validación
 * @param validationErrors - Array de errores de validación de class-validator
 * @returns Objeto con los errores extraídos y metadatos
 */
export function extractValidationErrors(validationErrors: ValidationError[]): ErrorExtractionResult {
  if (!validationErrors || validationErrors.length === 0) {
    return {
      errors: [],
      hasErrors: false,
      errorCount: 0
    };
  }

  const extractedErrors: ExtractedError[] = [];

  validationErrors.forEach(error => {
    const field = error.property;
    const messages: string[] = [];

    // Extraer mensajes de las restricciones
    if (error.constraints) {
      Object.values(error.constraints).forEach(message => {
        if (message && typeof message === 'string') {
          messages.push(message);
        }
      });
    }

    // Procesar errores anidados (para objetos complejos)
    if (error.children && error.children.length > 0) {
      const nestedErrors = extractValidationErrors(error.children);
      nestedErrors.errors.forEach(nestedError => {
        const nestedField = `${field}.${nestedError.field}`;
        const existingError = extractedErrors.find(e => e.field === nestedField);
        
        if (existingError) {
          existingError.messages.push(...nestedError.messages);
        } else {
          extractedErrors.push({
            field: nestedField,
            messages: [...nestedError.messages]
          });
        }
      });
    }

    // Agregar errores del campo actual si tiene mensajes
    if (messages.length > 0) {
      const existingError = extractedErrors.find(e => e.field === field);
      if (existingError) {
        existingError.messages.push(...messages);
      } else {
        extractedErrors.push({
          field,
          messages
        });
      }
    }
  });

  return {
    errors: extractedErrors,
    hasErrors: extractedErrors.length > 0,
    errorCount: extractedErrors.reduce((total, error) => total + error.messages.length, 0)
  };
}

/**
 * Convierte los errores extraídos a un formato plano de mensajes
 * @param extractedErrors - Resultado de extractValidationErrors
 * @returns Array de mensajes de error
 */
export function flattenErrorMessages(extractedErrors: ErrorExtractionResult): string[] {
  const messages: string[] = [];
  
  extractedErrors.errors.forEach(error => {
    messages.push(...error.messages);
  });
  
  return messages;
}

/**
 * Convierte los errores extraídos a un formato de objeto plano
 * @param extractedErrors - Resultado de extractValidationErrors
 * @returns Objeto con campo como clave y mensajes como valor
 */
export function errorsToObject(extractedErrors: ErrorExtractionResult): Record<string, string[]> {
  const result: Record<string, string[]> = {};
  
  extractedErrors.errors.forEach(error => {
    result[error.field] = error.messages;
  });
  
  return result;
}

/**
 * Crea un mensaje de error resumido
 * @param extractedErrors - Resultado de extractValidationErrors
 * @returns Mensaje resumido de los errores
 */
export function createSummaryMessage(extractedErrors: ErrorExtractionResult): string {
  if (!extractedErrors.hasErrors) {
    return 'No hay errores de validación';
  }

  const errorCount = extractedErrors.errorCount;
  const fieldCount = extractedErrors.errors.length;
  
  return `Se encontraron ${errorCount} error(es) de validación en ${fieldCount} campo(s)`;
} 
