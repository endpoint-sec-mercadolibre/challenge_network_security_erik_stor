import * as logger from 'logger';
import chalk from 'chalk';

interface Context {
  functionName: string;
  [key: string]: any;
}

class Logger {
  private static instance: logger.Logger;
  private static context: Context;
  private static readonly LOG_FILE_NAME = 'config-service.log';

  public static getInstance(): logger.Logger {
    if (!Logger.instance) {
      Logger.instance = logger.createLogger(Logger.LOG_FILE_NAME);
    }
    return Logger.instance;
  }

  public static setInstance(context: Context) {
    // Solo actualizar el contexto, no recrear la instancia
    Logger.context = context;
    // No crear nueva instancia del logger
  }

  public static addContext(context: Context) {
    Logger.context = { ...Logger.context, ...context };
  }

  public static info(message: string, data?: any) {
    const logData = data ? { ...data, context: Logger.context } : { context: Logger.context };
    console.log(chalk.blue(message), logData);
    Logger.getInstance().info(message, logData);
  }

  public static error(message: string, error?: any) {
    const logData = error ? { error, context: Logger.context } : { context: Logger.context };
    console.log(chalk.red(message), logData);
    Logger.getInstance().error(message, logData);
  }

  public static warn(message: string, data?: any) {
    const logData = data ? { ...data, context: Logger.context } : { context: Logger.context };
    console.log(chalk.yellow(message), logData);
    Logger.getInstance().warn(message, logData);
  }

  public static debug(message: string, data?: any) {
    const logData = data ? { ...data, context: Logger.context } : { context: Logger.context };
    console.log(chalk.gray(message), logData);
    Logger.getInstance().debug(message, logData);
  }

  public static success(message: string, data?: any) {
    const logData = data ? { ...data, context: Logger.context } : { context: Logger.context };
    console.log(chalk.green(message), logData);
    Logger.getInstance().info(message, logData);
  }
}

export default Logger;
