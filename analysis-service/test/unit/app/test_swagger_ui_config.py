import pytest
from app.swagger_ui_config import SWAGGER_UI_CONFIG, API_INFO


class TestSwaggerUIConfig:
    """Tests para la configuración de Swagger UI"""

    def test_swagger_ui_config_structure(self):
        """Test que valida la estructura de configuración de Swagger UI"""
        assert isinstance(SWAGGER_UI_CONFIG, dict)
        assert "swagger_ui_parameters" in SWAGGER_UI_CONFIG
        
        ui_params = SWAGGER_UI_CONFIG["swagger_ui_parameters"]
        assert isinstance(ui_params, dict)
        assert "defaultModelsExpandDepth" in ui_params
        assert "tryItOutEnabled" in ui_params
        assert "persistAuthorization" in ui_params
        assert ui_params["defaultModelsExpandDepth"] == -1
        assert ui_params["tryItOutEnabled"] is True
        assert ui_params["persistAuthorization"] is True

    def test_api_info_structure(self):
        """Test que valida la estructura de información de la API"""
        assert isinstance(API_INFO, dict)
        assert "title" in API_INFO
        assert "description" in API_INFO
        assert "version" in API_INFO
        
        assert API_INFO["title"] == "Analysis Service API"
        assert API_INFO["version"] == "1.0.0"
        assert "Análisis de Archivos" in API_INFO["description"]

    def test_config_values(self):
        """Test que valida valores específicos de configuración"""
        ui_params = SWAGGER_UI_CONFIG["swagger_ui_parameters"]
        
        assert ui_params["defaultModelExpandDepth"] == 3
        assert ui_params["displayRequestDuration"] is True
        assert ui_params["docExpansion"] == "list"
        assert ui_params["filter"] is True
        assert ui_params["syntaxHighlight.theme"] == "monokai"
        assert ui_params["displayOperationId"] is True 