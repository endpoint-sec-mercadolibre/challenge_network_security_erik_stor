import mongoose from 'mongoose';

import { MONGODB_CONNECTION_STRING } from '../domain/common/consts/Setup';
import { SystemException } from '../domain/exceptions/core/SystemException';

import Logger from './Logger';

export class MongoConfig {
  private static isConnected: boolean = false;
  private static readonly connectionString: string = MONGODB_CONNECTION_STRING;

  static async connect(): Promise<void> {
    if (!MongoConfig.isConnected) {
      try {
        await mongoose.connect(MongoConfig.connectionString);
        MongoConfig.isConnected = true;
        Logger.info('Conexión a MongoDB establecida exitosamente con Mongoose');
      } catch (error) {
        Logger.error('Error al conectar con MongoDB:', error);
        throw new SystemException(`Error al conectar con MongoDB: ${error}`);
      }
    }
  }

  static async disconnect(): Promise<void> {
    if (MongoConfig.isConnected) {
      try {
        await mongoose.disconnect();
        MongoConfig.isConnected = false;
        Logger.info('Conexión a MongoDB cerrada');
      } catch (error) {
        Logger.error('Error al cerrar la conexión con MongoDB:', error);
        throw new SystemException(`Error al cerrar la conexión con MongoDB: ${error}`);
      }
    }
  }

  static getConnection(): typeof mongoose {
    return mongoose;
  }

  static isConnectionActive(): boolean {
    return MongoConfig.isConnected && mongoose.connection.readyState === 1;
  }

  static getConnectionStatus(): string {
    const states = {
      0: 'disconnected',
      1: 'connected',
      2: 'connecting',
      3: 'disconnecting'
    };
    return states[mongoose.connection.readyState as keyof typeof states] || 'unknown';
  }
} 
