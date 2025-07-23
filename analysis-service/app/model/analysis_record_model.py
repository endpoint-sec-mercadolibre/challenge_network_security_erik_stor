from mongoengine import Document, StringField, BooleanField, DateTimeField, DictField
from datetime import datetime, UTC
import uuid


class AnalysisRecord(Document):
    """
    Modelo para representar los registros de análisis en MongoDB
    """

    # Campos del documento
    uuid = StringField(required=True, unique=True, default=lambda: str(uuid.uuid4()))
    success = BooleanField(required=True)
    response = DictField(required=True)  # Marshal de la respuesta de Gemini
    user = StringField(required=True)  # Usuario extraído del token
    created_at = DateTimeField(default=lambda: datetime.now(UTC))
    updated_at = DateTimeField(default=lambda: datetime.now(UTC))

    # Configuración de la colección
    meta = {
        "collection": "analysis_records",
        "indexes": [
            "uuid",
            "user",
            "created_at",
            (
                "user",
                "created_at",
            ),  # Índice compuesto para consultas por usuario y fecha
        ],
    }

    def save(self, *args, **kwargs):
        """Sobrescribe el método save para actualizar updated_at"""
        self.updated_at = datetime.now(UTC)
        return super().save(*args, **kwargs)
