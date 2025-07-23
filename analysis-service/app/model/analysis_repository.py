from typing import Dict, Any
from app.model.analysis_record_model import AnalysisRecord
from app.services.logger import Logger


class AnalysisRepository:
    """
    Repositorio para manejar las operaciones de MongoDB con los registros de análisis
    """

    def __init__(self):
        self.logger = Logger()

    def save_analysis_record(
        self, success: bool, response: Dict[str, Any], user: str
    ) -> AnalysisRecord:
        """
        Guarda un nuevo registro de análisis en MongoDB

        Args:
            success: Indica si el análisis fue exitoso
            response: Respuesta de Gemini (marshal)
            user: Usuario que realizó el análisis

        Returns:
            AnalysisRecord: Registro guardado
        """
        try:
            self.logger.info(f"Guardando registro de análisis para usuario: {user}")

            # Crear nuevo registro
            record = AnalysisRecord(success=success, response=response, user=user)

            # Guardar en MongoDB (mongoengine.save() no es asíncrono)
            record.save()

            self.logger.success(
                f"Registro guardado exitosamente con UUID: {record.uuid}"
            )
            return record

        except Exception as e:
            self.logger.error(f"Error al guardar registro de análisis: {str(e)}")
            # Re-lanzar como una excepción más específica para MongoDB
            raise RuntimeError(f"Error de MongoDB: {str(e)}")
