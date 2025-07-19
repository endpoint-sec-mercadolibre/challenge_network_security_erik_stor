
export const FILE_DEFAULT_ENCODING = process.env.FILE_DEFAULT_ENCODING ?? 'utf8';

export const SECRET_KEY = process.env.ENCRYPTION_KEY || 'default-secret-key-32-chars-long';

export const MONGODB_CONNECTION_STRING = process.env.MONGODB_CONNECTION_STRING || 'mongodb://localhost:27017/config-service';
