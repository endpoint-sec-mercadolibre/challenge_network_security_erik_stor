import { Request, Response, NextFunction } from 'express';
import { authMiddleware } from '../../../../../src/entrypoints/api/middlewares/authMiddleware';
import { AuthService } from '../../../../../src/adapters/service/AuthService';

// Mock del AuthService
jest.mock('../../../../../src/adapters/service/AuthService');
const MockedAuthService = AuthService as jest.MockedClass<typeof AuthService>;

describe('authMiddleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;

  beforeEach(() => {
    mockRequest = {
      method: 'GET',
      path: '/config/test',
      ip: '127.0.0.1',
      headers: {},
      user: undefined,
      get: jest.fn().mockReturnValue('test-user-agent'),
    };
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn().mockReturnThis(),
    };
    mockNext = jest.fn();
    
    // Limpiar todos los mocks
    jest.clearAllMocks();
  });

  describe('cuando no se proporciona header de autorización', () => {
    it('debe retornar error 401', async () => {
      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Token de autorización requerido',
        message: 'Debe proporcionar un token JWT en el header Authorization',
        code: 'AUTH_TOKEN_REQUIRED'
      });
      expect(mockNext).not.toHaveBeenCalled();
    });
  });

  describe('cuando el formato del header es incorrecto', () => {
    it('debe retornar error 401 para formato inválido', async () => {
      mockRequest.headers = {
        authorization: 'InvalidFormat token123'
      };

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Formato de token inválido',
        message: 'El token debe tener el formato: Bearer <token>',
        code: 'AUTH_TOKEN_INVALID_FORMAT'
      });
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('debe retornar error 401 para header sin Bearer', async () => {
      mockRequest.headers = {
        authorization: 'token123'
      };

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Formato de token inválido',
        message: 'El token debe tener el formato: Bearer <token>',
        code: 'AUTH_TOKEN_INVALID_FORMAT'
      });
      expect(mockNext).not.toHaveBeenCalled();
    });
  });

  describe('cuando el token está vacío', () => {
    it('debe retornar error 401', async () => {
      mockRequest.headers = {
        authorization: 'Bearer '
      };

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Token vacío',
        message: 'El token no puede estar vacío',
        code: 'AUTH_TOKEN_EMPTY'
      });
      expect(mockNext).not.toHaveBeenCalled();
    });
  });

  describe('cuando el token es válido', () => {
    it('debe llamar next() y agregar información del usuario', async () => {
      const validToken = 'valid.jwt.token';
      mockRequest.headers = {
        authorization: `Bearer ${validToken}`
      };

      // Mock del AuthService para retornar token válido
      const mockValidateToken = jest.fn().mockResolvedValue({
        valid: true,
        user: 'testuser'
      });
      
      MockedAuthService.prototype.validateToken = mockValidateToken;

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockValidateToken).toHaveBeenCalledWith(validToken);
      expect(mockRequest.user).toEqual({
        username: 'testuser',
        token: validToken
      });
      expect(mockNext).toHaveBeenCalled();
      expect(mockResponse.status).not.toHaveBeenCalled();
      expect(mockResponse.json).not.toHaveBeenCalled();
    });
  });

  describe('cuando el token es inválido', () => {
    it('debe retornar error 401', async () => {
      const invalidToken = 'invalid.jwt.token';
      mockRequest.headers = {
        authorization: `Bearer ${invalidToken}`
      };

      // Mock del AuthService para retornar token inválido
      const mockValidateToken = jest.fn().mockResolvedValue({
        valid: false,
        error: 'Token expirado'
      });
      
      MockedAuthService.prototype.validateToken = mockValidateToken;

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockValidateToken).toHaveBeenCalledWith(invalidToken);
      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Token inválido',
        message: 'Token expirado',
        code: 'AUTH_TOKEN_INVALID'
      });
      expect(mockNext).not.toHaveBeenCalled();
    });
  });

  describe('cuando hay un error en la validación', () => {
    it('debe retornar error 500', async () => {
      const token = 'test.jwt.token';
      mockRequest.headers = {
        authorization: `Bearer ${token}`
      };

      // Mock del AuthService para lanzar error
      const mockValidateToken = jest.fn().mockRejectedValue(new Error('Error de red'));
      
      MockedAuthService.prototype.validateToken = mockValidateToken;

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockValidateToken).toHaveBeenCalledWith(token);
      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Error interno de autenticación',
        message: 'Error al procesar la autenticación',
        code: 'AUTH_INTERNAL_ERROR'
      });
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('debe manejar errores no-Error objects', async () => {
      const token = 'test.jwt.token';
      mockRequest.headers = {
        authorization: `Bearer ${token}`
      };

      // Mock del AuthService para lanzar error no-Error
      const mockValidateToken = jest.fn().mockRejectedValue('String error');
      
      MockedAuthService.prototype.validateToken = mockValidateToken;

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockValidateToken).toHaveBeenCalledWith(token);
      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Error interno de autenticación',
        message: 'Error al procesar la autenticación',
        code: 'AUTH_INTERNAL_ERROR'
      });
      expect(mockNext).not.toHaveBeenCalled();
    });
  });

  describe('casos edge y adicionales', () => {
    it('debe manejar token con espacios en blanco', async () => {
      mockRequest.headers = {
        authorization: 'Bearer   token123  '
      };

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Formato de token inválido',
        message: 'El token debe tener el formato: Bearer <token>',
        code: 'AUTH_TOKEN_INVALID_FORMAT'
      });
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('debe manejar header authorization undefined', async () => {
      mockRequest.headers = {
        authorization: undefined
      };

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Token de autorización requerido',
        message: 'Debe proporcionar un token JWT en el header Authorization',
        code: 'AUTH_TOKEN_REQUIRED'
      });
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('debe manejar header authorization null', async () => {
      mockRequest.headers = {
        authorization: null as any
      };

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Token de autorización requerido',
        message: 'Debe proporcionar un token JWT en el header Authorization',
        code: 'AUTH_TOKEN_REQUIRED'
      });
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('debe manejar cuando validateToken retorna valid false sin error', async () => {
      const token = 'test.jwt.token';
      mockRequest.headers = {
        authorization: `Bearer ${token}`
      };

      const mockValidateToken = jest.fn().mockResolvedValue({
        valid: false,
        error: undefined
      });
      
      MockedAuthService.prototype.validateToken = mockValidateToken;

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockValidateToken).toHaveBeenCalledWith(token);
      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Token inválido',
        message: 'El token proporcionado no es válido',
        code: 'AUTH_TOKEN_INVALID'
      });
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('debe manejar cuando validateToken retorna user undefined', async () => {
      const token = 'test.jwt.token';
      mockRequest.headers = {
        authorization: `Bearer ${token}`
      };

      const mockValidateToken = jest.fn().mockResolvedValue({
        valid: true,
        user: undefined
      });
      
      MockedAuthService.prototype.validateToken = mockValidateToken;

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockValidateToken).toHaveBeenCalledWith(token);
      expect(mockRequest.user).toEqual({
        username: 'unknown',
        token: token
      });
      expect(mockNext).toHaveBeenCalled();
    });

    it('debe manejar cuando validateToken retorna user null', async () => {
      const token = 'test.jwt.token';
      mockRequest.headers = {
        authorization: `Bearer ${token}`
      };

      const mockValidateToken = jest.fn().mockResolvedValue({
        valid: true,
        user: null
      });
      
      MockedAuthService.prototype.validateToken = mockValidateToken;

      await authMiddleware(mockRequest as Request, mockResponse as Response, mockNext);

      expect(mockValidateToken).toHaveBeenCalledWith(token);
      expect(mockRequest.user).toEqual({
        username: 'unknown',
        token: token
      });
      expect(mockNext).toHaveBeenCalled();
    });
  });
}); 
