// import mongoose, { Model } from 'mongoose';
// import { MongoConfig } from '../../infra/MongoDb';
// import { AuditSchema, IAuditDocument } from '../../domain/model/Audit';
import { IAuditDocument } from '../../domain/model/Audit';
import Logger from '../../infra/Logger';
import { SystemException } from '../../domain/exceptions/core/SystemException';


export class AuditRepository {


  constructor(
    // private readonly auditModel: Model<IAuditDocument> = mongoose.model<IAuditDocument>('Audit', AuditSchema)
  ) { }

  /**
   * Escribe un registro de auditoría en MongoDB
   * @param user - Identificador del usuario
   * @param path - Ruta del archivo
   * @param managedRead - Indica si la lectura fue gestionada
   * @returns Promise con el documento creado
   */
  async createAuditLog(user: string, path: string, managedRead: boolean): Promise<IAuditDocument | SystemException> {
    try {

      Logger.getInstance().info('Inicio de proceso de creación de registro de auditoría', { user, path, managedRead });
      // Asegurar que la conexión esté establecida
      // await MongoConfig.connect();

      // const auditLog = new this.auditModel({
      //   user,
      //   path,
      //   managedRead
      // });

      // const savedLog = await auditLog.save();
      // Logger.getInstance().info(`Registro de auditoría creado: ${savedLog._id}`);

      // await MongoConfig.disconnect();

      return {
        _id: '123',
        user,
        path,
        managedRead,
        createdAt: new Date(),
        updatedAt: new Date()
      } as IAuditDocument;
    } catch (error) {
      Logger.getInstance().error('Error al crear registro de auditoría:', error);
      return new SystemException(`Error al crear registro de auditoría: ${error}`);
    }
  }

}
