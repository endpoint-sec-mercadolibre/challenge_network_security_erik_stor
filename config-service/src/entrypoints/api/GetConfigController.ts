
import { plainToInstance } from 'class-transformer';
import { validate } from 'class-validator';

import { SuccessResponse } from '../../domain/common/SuccessResponse';
import { SUCCESS_MESSAGES } from '../../domain/common/consts/SuccessMessages';
import { ERROR_MESSAGES } from '../../domain/exceptions/constants/ErrorMessages';
import { BaseException } from '../../domain/exceptions/core/BaseException';
import { InvalidDataException } from '../../domain/exceptions/core/InvalidDataException';
import { SystemException } from '../../domain/exceptions/core/SystemException';
import { InputFile } from '../../domain/model/Input';

import { AuditRepository } from '../../adapters/repository/AuditRepository';
import Logger from '../../infra/Logger';

import { extractValidationErrors, flattenErrorMessages } from '../../utils/ErrorExtractor';

import { RechargeConfirmResponse } from './model/GetConfigRequest';

import { GetConfigCommandHandler } from '../../domain/command_handlers/GetConfigCommandHandler';
import { GetConfigCommand } from '../../domain/commands/GetConfigCommand';
import { OutputFile } from '../../domain/model/Output';


export class ConfigController {

  constructor(
    private readonly auditRepository: AuditRepository,
    private readonly getConfigCommandHandler: GetConfigCommandHandler
  ) { }

  async handle(req: any): Promise<any> {
    try {

      // Log solo información relevante del request para evitar referencias circulares
      Logger.info('Inicio de proceso de validación de datos', {
        method: req.method,
        path: req.path,
        ip: req.ip,
        userAgent: req.get('User-Agent'),
        pathParameters: req.params
      });


      const request = plainToInstance(InputFile, { ...req.params }) as unknown as InputFile;

      const validationErrors = await validate(request);

      if (validationErrors.length > 0) {

        Logger.error('Errores de validación:', JSON.stringify(validationErrors));

        const extractedErrors = extractValidationErrors(validationErrors);
        const errorMessages = flattenErrorMessages(extractedErrors);

        Logger.error('Mensajes de error:', JSON.stringify(errorMessages));

        const errorResponse = new InvalidDataException(errorMessages)

        this.auditRepository.createAuditLog('', req.path, false);

        return errorResponse.toResponse();

      }

      Logger.info('Datos validados correctamente', {
        path: request.filename
      });

      const getConfigCommand = new GetConfigCommand(request);

      Logger.info('Ejecutando comando:', {
        path: getConfigCommand.request.filename
      });

      const result = await this.getConfigCommandHandler.handle(getConfigCommand);

      if (result instanceof OutputFile) {
        const response: RechargeConfirmResponse = {
          message: SUCCESS_MESSAGES.READ_FILE,
          data: { ...result }
        };

        return new SuccessResponse(response).toResponse();
      }

      return result.toResponse();

    } catch (error: any) {
      Logger.error('Error en el controlador:', {
        error: error.message,
        stack: error.stack
      });

      if (error instanceof BaseException) {
        return error.toResponse();
      }

      return new SystemException(ERROR_MESSAGES.INTERNAL_ERROR).toResponse();
    }
  }
} 
