import axios, { AxiosInstance, AxiosResponse } from 'axios';
import Logger from '../../infra/Logger';

export interface ValidateTokenRequest {
  token: string;
}

export interface ValidateTokenResponse {
  valid: boolean;
  user?: string;
  error?: string;
}

export class AuthService {
  private client: AxiosInstance;
  private authServiceUrl: string;

  constructor() {
    this.authServiceUrl = process.env.AUTH_SERVICE_URL || 'http://auth-service:8080';
    
    this.client = axios.create({
      baseURL: this.authServiceUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para logging
    this.client.interceptors.request.use(
      (config) => {
        Logger.info('Request a auth-service:', {
          method: config.method?.toUpperCase(),
          url: config.url,
          baseURL: config.baseURL,
        });
        return config;
      },
      (error) => {
        Logger.error('Error en request a auth-service:', error.message);
        return Promise.reject(error);
      }
    );

    this.client.interceptors.response.use(
      (response) => {
        Logger.info('Response de auth-service:', {
          status: response.status,
          statusText: response.statusText,
        });
        return response;
      },
      (error) => {
        Logger.error('Error en response de auth-service:', {
          status: error.response?.status,
          message: error.message,
          data: error.response?.data,
        });
        return Promise.reject(error);
      }
    );
  }

  /**
   * Valida un token JWT contra el servicio de autenticación
   * @param token - Token JWT a validar
   * @returns Promise<ValidateTokenResponse> - Resultado de la validación
   */
  async validateToken(token: string): Promise<ValidateTokenResponse> {
    try {
      Logger.info('Iniciando validación de token', {
        tokenLength: token.length,
        authServiceUrl: this.authServiceUrl,
      });

      const request: ValidateTokenRequest = { token };
      
      const response: AxiosResponse<ValidateTokenResponse> = await this.client.post(
        '/validate',
        request
      );

      Logger.info('Token validado exitosamente', {
        valid: response.data.valid,
        user: response.data.user,
      });

      return response.data;
    } catch (error) {
      Logger.error('Error al validar token:', {
        error: error instanceof Error ? error.message : String(error),
        tokenLength: token.length,
      });

      // Si hay un error de red o del servicio, consideramos el token como inválido
      return {
        valid: false,
        error: 'Error de comunicación con el servicio de autenticación',
      };
    }
  }

  /**
   * Verifica si el servicio de autenticación está disponible
   * @returns Promise<boolean> - true si está disponible, false en caso contrario
   */
  async isHealthy(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      Logger.error('Auth service no está disponible:', {
        error: error instanceof Error ? error.message : String(error),
      });
      return false;
    }
  }
} 
