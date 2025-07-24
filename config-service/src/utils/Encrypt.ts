import * as crypto from 'crypto';
import { SECRET_KEY } from '../domain/common/consts/Setup';
import { SystemException } from '../domain/exceptions/core/SystemException';

/**
 * Clase para manejar operaciones de encriptación AES-256-GCM y ofuscación base64
 * Basada en la implementación de encript.js
 * 
 * Esta clase implementa:
 * - AES-256-GCM para encriptación segura
 * - PBKDF2 para derivación de claves
 * - Ofuscación base64 con rotación de caracteres
 * - Compatibilidad con Web Crypto API
 */
export class Encrypt {

  private readonly password: string;

  constructor(password: string = SECRET_KEY) {
    /**
     * Inicializa el cifrador AES con una contraseña.
     * 
     * @param {string} password - Contraseña para derivar la clave de cifrado
     */
    this.password = password;
  }

  /**
   * Deriva una clave de 256 bits usando PBKDF2.
   * 
   * @param {Uint8Array} salt - Salt para la derivación de clave
   * @returns {Promise<CryptoKey>} Clave derivada
   */
  async _deriveKey(salt: Uint8Array) {
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(this.password),
      'PBKDF2',
      false,
      ['deriveKey']
    );

    return await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: salt,
        iterations: 100000,
        hash: 'SHA-256'
      },
      keyMaterial,
      {
        name: 'AES-GCM',
        length: 256
      },
      false,
      ['encrypt', 'decrypt']
    );
  }

  /**
   * Encripta el texto usando AES-256-GCM.
   * 
   * @param {string} plaintext - Texto a encriptar
   * @returns {Promise<string>} Texto encriptado codificado en base64
   */
  async encrypt(plaintext: string) {
    // Generar salt e IV aleatorios
    const salt = crypto.getRandomValues(new Uint8Array(16)); // 128 bits
    const iv = crypto.getRandomValues(new Uint8Array(12));   // 96 bits para GCM

    // Derivar clave
    const key = await this._deriveKey(salt);

    // Convertir texto a bytes
    const plaintextBytes = new TextEncoder().encode(plaintext);

    // Encriptar
    const encryptedData = await crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv: iv
      },
      key,
      plaintextBytes
    );

    // El resultado de AES-GCM incluye el tag al final
    const ciphertext = new Uint8Array(encryptedData);

    // Extraer ciphertext y tag (los últimos 16 bytes son el tag)
    const actualCiphertext = ciphertext.slice(0, -16);
    const tag = ciphertext.slice(-16);

    // Combinar: salt (16) + iv (12) + tag (16) + ciphertext
    const combined = new Uint8Array(salt.length + iv.length + tag.length + actualCiphertext.length);
    combined.set(salt, 0);
    combined.set(iv, 16);
    combined.set(tag, 28);
    combined.set(actualCiphertext, 44);

    // Codificar en base64
    return this._arrayBufferToBase64(combined);
  }

  /**
   * Desencripta el texto usando AES-256-GCM.
   * 
   * @param {string} encryptedData - Texto encriptado codificado en base64
   * @returns {Promise<string>} Texto desencriptado
   * @throws {Error} Si la desencriptación falla
   */
  async decrypt(encryptedData: string) {
    try {
      // Decodificar base64
      const data = this._base64ToArrayBuffer(encryptedData);

      // Extraer componentes
      const salt = data.slice(0, 16);           // Primeros 16 bytes
      const iv = data.slice(16, 28);           // Siguientes 12 bytes
      const tag = data.slice(28, 44);          // Siguientes 16 bytes
      const ciphertext = data.slice(44);       // Resto

      // Derivar clave
      const key = await this._deriveKey(salt);

      // Combinar ciphertext y tag para el formato que espera Web Crypto API
      const ciphertextWithTag = new Uint8Array(ciphertext.length + tag.length);
      ciphertextWithTag.set(ciphertext);
      ciphertextWithTag.set(tag, ciphertext.length);

      // Desencriptar
      const decryptedData = await crypto.subtle.decrypt(
        {
          name: 'AES-GCM',
          iv: iv
        },
        key,
        ciphertextWithTag
      );

      // Convertir bytes a texto
      return new TextDecoder().decode(decryptedData);

    } catch (error: any) {
      return new SystemException(`Error al desencriptar: ${error.message}`);
    }
  }

  /**
   * Convierte ArrayBuffer a string base64.
   * 
   * @param {Uint8Array} buffer - Buffer a convertir
   * @returns {string} String en base64
   */
  private _arrayBufferToBase64(buffer: Uint8Array) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * Convierte string base64 a Uint8Array.
   * 
   * @param {string} base64 - String en base64
   * @returns {Uint8Array} Array de bytes
   */
  private _base64ToArrayBuffer(base64: string) {
    const binaryString = atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
  }

  /**
   * Ofusca un string convirtiéndolo a base64 y aplicando una transformación adicional.
   * 
   * @param {string} texto - Texto a ofuscar
   * @returns {string} Texto ofuscado
   */
  ofuscarBase64(texto: string) {
    try {
      // Convertir a base64
      const textoBytes = new TextEncoder().encode(texto);
      const base64Texto = this._arrayBufferToBase64(textoBytes);

      // Aplicar transformación adicional: rotar caracteres
      const caracteres = base64Texto.split('');
      for (let i = 0; i < caracteres.length; i++) {
        if (/[a-zA-Z]/.test(caracteres[i])) {
          // Rotar letras: A->B, B->C, ..., Z->A
          if (caracteres[i] === caracteres[i].toUpperCase()) {
            caracteres[i] = String.fromCharCode(
              ((caracteres[i].charCodeAt(0) - 'A'.charCodeAt(0) + 1) % 26) + 'A'.charCodeAt(0)
            );
          } else {
            caracteres[i] = String.fromCharCode(
              ((caracteres[i].charCodeAt(0) - 'a'.charCodeAt(0) + 1) % 26) + 'a'.charCodeAt(0)
            );
          }
        } else if (/\d/.test(caracteres[i])) {
          // Rotar números: 0->1, 1->2, ..., 9->0
          caracteres[i] = ((parseInt(caracteres[i]) + 1) % 10).toString();
        }
      }

      return caracteres.join('');

    } catch (error: any) {
      throw new Error(`Error al ofuscar: ${error.message}`);
    }
  }

  /**
   * Desofusca un string que fue ofuscado con ofuscarBase64().
   * 
   * @param {string} textoOfuscado - Texto ofuscado a desofuscar
   * @returns {string} Texto original desofuscado
   * @throws {Error} Si la desofuscación falla
   */
  desofuscarBase64(textoOfuscado: string) {
    try {
      // Revertir la transformación: rotar caracteres en dirección opuesta
      const caracteres = textoOfuscado.split('');
      for (let i = 0; i < caracteres.length; i++) {
        if (/[a-zA-Z]/.test(caracteres[i])) {
          // Rotar letras en dirección opuesta: B->A, C->B, ..., A->Z
          if (caracteres[i] === caracteres[i].toUpperCase()) {
            caracteres[i] = String.fromCharCode(
              ((caracteres[i].charCodeAt(0) - 'A'.charCodeAt(0) - 1 + 26) % 26) + 'A'.charCodeAt(0)
            );
          } else {
            caracteres[i] = String.fromCharCode(
              ((caracteres[i].charCodeAt(0) - 'a'.charCodeAt(0) - 1 + 26) % 26) + 'a'.charCodeAt(0)
            );
          }
        } else if (/\d/.test(caracteres[i])) {
          // Rotar números en dirección opuesta: 1->0, 2->1, ..., 0->9
          caracteres[i] = ((parseInt(caracteres[i]) - 1 + 10) % 10).toString();
        }
      }

      const textoBase64 = caracteres.join('');

      // Decodificar base64
      const textoBytes = this._base64ToArrayBuffer(textoBase64);
      return new TextDecoder().decode(textoBytes);

    } catch (error: any) {
      throw new Error(`Error al desofuscar: ${error.message}`);
    }
  }



}
