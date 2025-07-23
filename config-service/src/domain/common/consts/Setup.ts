
export const FILE_DEFAULT_ENCODING = process.env.FILE_DEFAULT_ENCODING ?? 'utf8';

export const SECRET_KEY = process.env.ENCRYPTION_KEY || 'mi_contraseña_secreta';

export const MONGODB_CONNECTION_STRING = process.env.MONGODB_CONNECTION_STRING || 'mongodb://localhost:27017/config-service';

export const STORAGE_PATH = process.env.STORAGE_PATH || '../dist/storage';
