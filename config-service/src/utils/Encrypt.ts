import * as CryptoJS from 'crypto-js';
import { SECRET_KEY } from '../domain/common/consts/Setup';

/**
 * Clase para manejar operaciones de encriptación y codificación
 */
export class Encrypt {
  private static readonly SECRET_KEY = SECRET_KEY;

  /**
   * Convierte un string a base64
   * @param text - Texto a convertir
   * @returns String codificado en base64
   */
  public static toBase64(text: string): string {
    try {
      return Buffer.from(text, 'utf8').toString('base64');
    } catch (error) {
      throw new Error(`Error al convertir a base64: ${error}`);
    }
  }

  /**
   * Decodifica un string desde base64
   * @param base64Text - Texto en base64
   * @returns String decodificado
   */
  public static fromBase64(base64Text: string): string {
    try {
      return Buffer.from(base64Text, 'base64').toString('utf8');
    } catch (error) {
      throw new Error(`Error al decodificar desde base64: ${error}`);
    }
  }

  /**
   * Encripta un string usando AES-256-CBC
   * @param text - Texto a encriptar
   * @returns String encriptado
   */
  public static encryptAES(text: string): string {
    try {
      const encrypted = CryptoJS.AES.encrypt(text, this.SECRET_KEY).toString();
      return encrypted;
    } catch (error) {
      throw new Error(`Error al encriptar con AES: ${error}`);
    }
  }

  /**
   * Desencripta un string usando AES-256-CBC
   * @param encryptedText - Texto encriptado
   * @returns String desencriptado
   */
  public static decryptAES(encryptedText: string): string {
    try {
      const decrypted = CryptoJS.AES.decrypt(encryptedText, this.SECRET_KEY);
      return decrypted.toString(CryptoJS.enc.Utf8);
    } catch (error) {
      throw new Error(`Error al desencriptar con AES: ${error}`);
    }
  }

  /**
   * Convierte un string a base64 y luego lo encripta con AES
   * @param text - Texto a procesar
   * @returns String convertido a base64 y encriptado
   */
  public static toBase64AndEncrypt(text: string): string {
    try {
      const encript = this.encryptAES(text);
      return this.toBase64(encript);
    } catch (error) {
      throw new Error(`Error al convertir a base64 y encriptar: ${error}`);
    }
  }

  /**
   * Desencripta un string y luego lo decodifica desde base64
   * @param encryptedText - Texto encriptado
   * @returns String desencriptado y decodificado desde base64
   */
  public static decryptAndFromBase64(encryptedText: string): string {
    try {
      const decryptedText =  this.fromBase64(encryptedText);
      return this.decryptAES(decryptedText);
    } catch (error) {
      throw new Error(`Error al desencriptar y decodificar desde base64: ${error}`);
    }
  }

  /**
   * Genera una clave secreta aleatoria de 32 caracteres
   * @returns Clave secreta generada
   */
  public static generateSecretKey(): string {
    return CryptoJS.lib.WordArray.random(32).toString();
  }

  /**
   * Valida si un string es válido en base64
   * @param text - Texto a validar
   * @returns true si es válido, false en caso contrario
   */
  public static isValidBase64(text: string): boolean {
    try {
      return Buffer.from(text, 'base64').toString('base64') === text;
    } catch {
      return false;
    }
  }
}
