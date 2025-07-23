import pytest
from app.swagger_config import (
    SWAGGER_UI_PARAMETERS,
    OPENAPI_TAGS,
    SECURITY_SCHEMES,
    SERVERS,
    EXTRA_INFO
)


class TestSwaggerConfig:
    """Tests para la configuración de Swagger"""

    def test_swagger_ui_parameters_structure(self):
        """Test que valida la estructura de parámetros de Swagger UI"""
        assert isinstance(SWAGGER_UI_PARAMETERS, dict)
        assert "defaultModelsExpandDepth" in SWAGGER_UI_PARAMETERS
        assert "tryItOutEnabled" in SWAGGER_UI_PARAMETERS
        assert "persistAuthorization" in SWAGGER_UI_PARAMETERS
        assert SWAGGER_UI_PARAMETERS["defaultModelsExpandDepth"] == -1
        assert SWAGGER_UI_PARAMETERS["tryItOutEnabled"] is True

    def test_openapi_tags_structure(self):
        """Test que valida la estructura de tags de OpenAPI"""
        assert isinstance(OPENAPI_TAGS, list)
        assert len(OPENAPI_TAGS) == 2
        
        analysis_tag = next((tag for tag in OPENAPI_TAGS if tag["name"] == "analysis"), None)
        assert analysis_tag is not None
        assert "description" in analysis_tag
        assert "externalDocs" in analysis_tag
        
        health_tag = next((tag for tag in OPENAPI_TAGS if tag["name"] == "health"), None)
        assert health_tag is not None
        assert "description" in health_tag

    def test_security_schemes_structure(self):
        """Test que valida la estructura de esquemas de seguridad"""
        assert isinstance(SECURITY_SCHEMES, dict)
        assert "bearerAuth" in SECURITY_SCHEMES
        
        bearer_auth = SECURITY_SCHEMES["bearerAuth"]
        assert bearer_auth["type"] == "http"
        assert bearer_auth["scheme"] == "bearer"
        assert bearer_auth["bearerFormat"] == "JWT"
        assert "description" in bearer_auth

    def test_servers_structure(self):
        """Test que valida la estructura de servidores"""
        assert isinstance(SERVERS, list)
        assert len(SERVERS) == 1
        
        server = SERVERS[0]
        assert "url" in server
        assert "description" in server
        assert server["url"] == "http://localhost:8002"

    def test_extra_info_structure(self):
        """Test que valida la estructura de información extra"""
        assert isinstance(EXTRA_INFO, dict)
        assert "x-logo" in EXTRA_INFO
        assert "x-tagGroups" in EXTRA_INFO
        
        logo = EXTRA_INFO["x-logo"]
        assert "url" in logo
        assert "altText" in logo
        
        tag_groups = EXTRA_INFO["x-tagGroups"]
        assert isinstance(tag_groups, list)
        assert len(tag_groups) == 2 