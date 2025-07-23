import FileReaderService from '../../adapters/service/FileReaderService';
import Logger from '../../infra/Logger';
import { GetConfigCommand } from '../commands/GetConfigCommand';
import { ERROR_MESSAGES } from '../exceptions/constants/ErrorMessages';
import { NotFoundException } from '../exceptions/core/NotFoundException';
import { SystemException } from '../exceptions/core/SystemException';
import { OutputFile } from '../model/Output';


export class GetConfigCommandHandler {
  constructor(
    private readonly fileReaderService: FileReaderService
  ) { }

  async handle(command: GetConfigCommand): Promise<OutputFile | NotFoundException | SystemException> {
    Logger.info('Inicio de lectura de archivo', {
      path: command.request.filename
    });

    try {
      const response = await this.fileReaderService.read(command.request);

      if (typeof response === 'string') {
        Logger.info('Lectura de archivo exitosa', {
          path: command.request.filename,
          content: response
        });
        return new OutputFile(response);
      }

      return response;

    } catch (error) {
      Logger.error('Error en lectura de archivo', {
        error: error instanceof Error ? error.message : String(error),
      });

      return new SystemException(ERROR_MESSAGES.INTERNAL_ERROR);
    }
  }
} 
