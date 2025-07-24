import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { AuthService, ValidateTokenRequest, ValidateTokenResponse } from '../../../../src/adapters/service/AuthService';
import Logger from '../../../../src/infra/Logger';

// Mock de axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock de Logger
jest.mock('../../../../src/infra/Logger');

describe('AuthService', () => {
  let authService: AuthService;
  let mockAxiosInstance: jest.Mocked<AxiosInstance>;

  beforeEach(() => {
    // Limpiar todos los mocks
    jest.clearAllMocks();
    
    // Configurar variables de entorno
    process.env.AUTH_SERVICE_URL = 'http://test-auth-service:8080';
    
    // Crear mock del cliente axios
    mockAxiosInstance = {
      post: jest.fn(),
      get: jest.fn(),
      interceptors: {
        request: {
          use: jest.fn(),
        },
        response: {
          use: jest.fn(),
        },
      },
    } as any;

    // Mock de axios.create
    mockedAxios.create.mockReturnValue(mockAxiosInstance);
    
    // Crear instancia del servicio
    authService = new AuthService();
  });

  afterEach(() => {
    delete process.env.AUTH_SERVICE_URL;
  });

  describe('constructor', () => {
    it('debería crear una instancia con URL por defecto cuando no hay AUTH_SERVICE_URL', () => {
      delete process.env.AUTH_SERVICE_URL;
      const service = new AuthService();
      
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: 'http://auth-service:8080',
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('debería crear una instancia con URL personalizada cuando hay AUTH_SERVICE_URL', () => {
      process.env.AUTH_SERVICE_URL = 'http://custom-auth:9090';
      const service = new AuthService();
      
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: 'http://custom-auth:9090',
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('debería configurar interceptores de request y response', () => {
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });
  });

  describe('validateToken', () => {
    const mockToken = 'test-jwt-token';
    const mockRequest: ValidateTokenRequest = { token: mockToken };
    const mockValidResponse: ValidateTokenResponse = {
      valid: true,
      user: 'test-user',
    };
    const mockInvalidResponse: ValidateTokenResponse = {
      valid: false,
      error: 'Token expirado',
    };

    it('debería validar un token exitosamente', async () => {
      const mockAxiosResponse: AxiosResponse<ValidateTokenResponse> = {
        data: mockValidResponse,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      };

      mockAxiosInstance.post.mockResolvedValue(mockAxiosResponse);

      const result = await authService.validateToken(mockToken);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/validate', mockRequest);
      expect(result).toEqual(mockValidResponse);
      expect(Logger.info).toHaveBeenCalledWith('Iniciando validación de token', {
        tokenLength: mockToken.length,
        authServiceUrl: 'http://test-auth-service:8080',
      });
      expect(Logger.info).toHaveBeenCalledWith('Token validado exitosamente', {
        valid: true,
        user: 'test-user',
      });
    });

    it('debería manejar token inválido', async () => {
      const mockAxiosResponse: AxiosResponse<ValidateTokenResponse> = {
        data: mockInvalidResponse,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      };

      mockAxiosInstance.post.mockResolvedValue(mockAxiosResponse);

      const result = await authService.validateToken(mockToken);

      expect(result).toEqual(mockInvalidResponse);
      expect(Logger.info).toHaveBeenCalledWith('Token validado exitosamente', {
        valid: false,
        user: undefined,
      });
    });

    it('debería manejar error de red y retornar token inválido', async () => {
      const networkError = new Error('Network error');
      mockAxiosInstance.post.mockRejectedValue(networkError);

      const result = await authService.validateToken(mockToken);

      expect(result).toEqual({
        valid: false,
        error: 'Error de comunicación con el servicio de autenticación',
      });
      expect(Logger.error).toHaveBeenCalledWith('Error al validar token:', {
        error: 'Network error',
        tokenLength: mockToken.length,
      });
    });

    it('debería manejar error de axios con response', async () => {
      const axiosError = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' },
        },
        message: 'Request failed with status code 401',
      };
      mockAxiosInstance.post.mockRejectedValue(axiosError);

      const result = await authService.validateToken(mockToken);

      expect(result).toEqual({
        valid: false,
        error: 'Error de comunicación con el servicio de autenticación',
      });
      expect(Logger.error).toHaveBeenCalledWith('Error al validar token:', {
        error: expect.any(String),
        tokenLength: mockToken.length,
      });
    });

    it('debería manejar error sin mensaje', async () => {
      const errorWithoutMessage = {};
      mockAxiosInstance.post.mockRejectedValue(errorWithoutMessage);

      const result = await authService.validateToken(mockToken);

      expect(result).toEqual({
        valid: false,
        error: 'Error de comunicación con el servicio de autenticación',
      });
      expect(Logger.error).toHaveBeenCalledWith('Error al validar token:', {
        error: '[object Object]',
        tokenLength: mockToken.length,
      });
    });
  });

  describe('isHealthy', () => {
    it('debería retornar true cuando el servicio está saludable', async () => {
      const mockAxiosResponse: AxiosResponse = {
        data: {},
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {} as any,
      };

      mockAxiosInstance.get.mockResolvedValue(mockAxiosResponse);

      const result = await authService.isHealthy();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health');
      expect(result).toBe(true);
    });

    it('debería retornar false cuando el servicio no está saludable', async () => {
      const mockAxiosResponse: AxiosResponse = {
        data: {},
        status: 503,
        statusText: 'Service Unavailable',
        headers: {},
        config: {} as any,
      };

      mockAxiosInstance.get.mockResolvedValue(mockAxiosResponse);

      const result = await authService.isHealthy();

      expect(result).toBe(false);
    });

    it('debería retornar false cuando hay error de red', async () => {
      const networkError = new Error('Connection refused');
      mockAxiosInstance.get.mockRejectedValue(networkError);

      const result = await authService.isHealthy();

      expect(result).toBe(false);
      expect(Logger.error).toHaveBeenCalledWith('Auth service no está disponible:', {
        error: 'Connection refused',
      });
    });

    it('debería retornar false cuando hay error sin mensaje', async () => {
      const errorWithoutMessage = {};
      mockAxiosInstance.get.mockRejectedValue(errorWithoutMessage);

      const result = await authService.isHealthy();

      expect(result).toBe(false);
      expect(Logger.error).toHaveBeenCalledWith('Auth service no está disponible:', {
        error: '[object Object]',
      });
    });
  });

  describe('interceptors', () => {
    let requestInterceptor: any;
    let requestErrorInterceptor: any;
    let responseInterceptor: any;
    let responseErrorInterceptor: any;

    beforeEach(() => {
      // Capturar las funciones de los interceptores
      (mockAxiosInstance.interceptors.request.use as jest.Mock).mockImplementation((success: any, error: any) => {
        requestInterceptor = success;
        requestErrorInterceptor = error;
      });

      (mockAxiosInstance.interceptors.response.use as jest.Mock).mockImplementation((success: any, error: any) => {
        responseInterceptor = success;
        responseErrorInterceptor = error;
      });
    });

    it('debería configurar interceptor de request correctamente', () => {
      const requestUseSpy = jest.spyOn(mockAxiosInstance.interceptors.request, 'use');
      
      new AuthService();
      
      expect(requestUseSpy).toHaveBeenCalledWith(
        expect.any(Function),
        expect.any(Function)
      );
    });

    it('debería configurar interceptor de response correctamente', () => {
      const responseUseSpy = jest.spyOn(mockAxiosInstance.interceptors.response, 'use');
      
      new AuthService();
      
      expect(responseUseSpy).toHaveBeenCalledWith(
        expect.any(Function),
        expect.any(Function)
      );
    });

    it('debería ejecutar interceptor de request exitosamente', () => {
      new AuthService();
      
      const mockConfig = {
        method: 'post',
        url: '/validate',
        baseURL: 'http://test-auth-service:8080',
      };

      const result = requestInterceptor(mockConfig);

      expect(result).toEqual(mockConfig);
      expect(Logger.info).toHaveBeenCalledWith('Request a auth-service:', {
        method: 'POST',
        url: '/validate',
        baseURL: 'http://test-auth-service:8080',
      });
    });

    it('debería ejecutar interceptor de request con método undefined', () => {
      new AuthService();
      
      const mockConfig = {
        method: undefined,
        url: '/validate',
        baseURL: 'http://test-auth-service:8080',
      };

      const result = requestInterceptor(mockConfig);

      expect(result).toEqual(mockConfig);
      expect(Logger.info).toHaveBeenCalledWith('Request a auth-service:', {
        method: undefined,
        url: '/validate',
        baseURL: 'http://test-auth-service:8080',
      });
    });

    it('debería manejar error en interceptor de request', () => {
      new AuthService();
      
      const mockError = { message: 'Request error' };

      const result = requestErrorInterceptor(mockError);

      expect(Logger.error).toHaveBeenCalledWith('Error en request a auth-service:', 'Request error');
      expect(result).rejects.toEqual(mockError);
    });

    it('debería ejecutar interceptor de response exitosamente', () => {
      new AuthService();
      
      const mockResponse = {
        status: 200,
        statusText: 'OK',
      };

      const result = responseInterceptor(mockResponse);

      expect(result).toEqual(mockResponse);
      expect(Logger.info).toHaveBeenCalledWith('Response de auth-service:', {
        status: 200,
        statusText: 'OK',
      });
    });

    it('debería manejar error en interceptor de response', () => {
      new AuthService();
      
      const mockError = {
        response: {
          status: 500,
          data: { error: 'Internal server error' },
        },
        message: 'Request failed',
      };

      const result = responseErrorInterceptor(mockError);

      expect(Logger.error).toHaveBeenCalledWith('Error en response de auth-service:', {
        status: 500,
        message: 'Request failed',
        data: { error: 'Internal server error' },
      });
      expect(result).rejects.toEqual(mockError);
    });

    it('debería manejar error en interceptor de response sin response', () => {
      new AuthService();
      
      const mockError = {
        message: 'Network error',
      };

      const result = responseErrorInterceptor(mockError);

      expect(Logger.error).toHaveBeenCalledWith('Error en response de auth-service:', {
        status: undefined,
        message: 'Network error',
        data: undefined,
      });
      expect(result).rejects.toEqual(mockError);
    });
  });
}); 
