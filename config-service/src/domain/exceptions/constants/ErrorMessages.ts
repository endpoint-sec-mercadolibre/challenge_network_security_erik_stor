export const ERROR_MESSAGES = {
  // Validaciones generales
  REQUIRED_FIELD: 'El campo es obligatorio',
  INVALID_FORMAT: 'El formato no es válido',
  INVALID_LENGTH: 'La longitud no es válida',
  INVALID_DATA: 'Los datos de entrada no son válidos',
  INTERNAL_ERROR: 'Error interno del servidor',
  NOT_FOUND: 'No se encontró el recurso',

}

export type ErrorMessageKey = keyof typeof ERROR_MESSAGES;

export const HTTP_STATUS_CODES = {
  OK: 200,
  BAD_REQUEST: 400,
  INTERNAL_SERVER_ERROR: 500,
  CREATED: 201,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

export type HttpStatusCodeKey = keyof typeof HTTP_STATUS_CODES;


export const ERROR_CODES = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_DATA: 'INVALID_DATA',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
} as const;

export type ErrorCodeKey = keyof typeof ERROR_CODES;
