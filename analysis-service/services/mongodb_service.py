import os
from mongoengine import connect, disconnect
from services.logger import Logger


class MongoDBService:
    """
    Servicio para manejar la conexión a MongoDB
    """
    
    def __init__(self):
        self.logger = Logger()
        self.connection = None
    
    def connect(self):
        """
        Establece la conexión a MongoDB
        """
        try:
            # Obtener configuración desde variables de entorno
            mongo_host = os.getenv("MONGO_HOST", "localhost")
            mongo_port = int(os.getenv("MONGO_PORT", "27017"))
            mongo_database = os.getenv("MONGO_DATABASE", "analysis_service")
            mongo_username = os.getenv("MONGO_USERNAME")
            mongo_password = os.getenv("MONGO_PASSWORD")
            
            self.logger.info(f"Conectando a MongoDB: {mongo_host}:{mongo_port}/{mongo_database}")
            self.logger.info(f"Usuario: {mongo_username}")
            self.logger.info(f"Autenticación requerida: {bool(mongo_username and mongo_password)}")
            
            # Construir URI de conexión
            if mongo_username and mongo_password:
                # Conexión con autenticación - usar authSource=admin para el usuario root
                mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_database}?authSource=admin"
                self.logger.info("Usando conexión con autenticación")
            else:
                # Conexión sin autenticación
                mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/{mongo_database}"
                self.logger.info("Usando conexión sin autenticación")
            
            self.logger.info(f"URI de conexión: {mongo_uri.replace(mongo_password, '***') if mongo_password else mongo_uri}")
            
            # Establecer conexión
            self.connection = connect(
                db=mongo_database,
                host=mongo_uri,
                alias='default'
            )
            
            self.logger.success("Conexión a MongoDB establecida exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error al conectar a MongoDB: {str(e)}")
            raise
    
    def disconnect(self):
        """
        Cierra la conexión a MongoDB
        """
        try:
            if self.connection:
                disconnect(alias='default')
                self.logger.info("Conexión a MongoDB cerrada")
        except Exception as e:
            self.logger.error(f"Error al cerrar conexión a MongoDB: {str(e)}")
    

# Instancia global del servicio
mongodb_service = MongoDBService() 