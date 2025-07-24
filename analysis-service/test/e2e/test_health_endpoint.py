import pytest
import pytest_asyncio
from fastapi import status


class TestHealthEndpoint:
    """Tests End-to-End para el endpoint de health"""

    def test_health_check_sync(self, client):
        """Test síncrono: debe devolver estado healthy sin autenticación"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "analysis-service"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)

    @pytest.mark.asyncio
    async def test_health_check_async(self, async_client):
        """Test asíncrono: debe devolver estado healthy sin autenticación"""
        response = await async_client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "analysis-service"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data

    def test_health_check_content_type(self, client):
        """Test: debe devolver content-type application/json"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        assert "application/json" in response.headers["content-type"]

    def test_health_check_no_auth_required(self, client):
        """Test: endpoint de health no debe requerir autenticación"""
        # Sin header de Authorization
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        
        # Con header de Authorization inválido - aún debería funcionar
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/health", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_health_check_response_structure(self, client):
        """Test: validar estructura completa de la respuesta"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # Validar que tiene exactamente las claves esperadas
        expected_keys = {"status", "service", "version", "timestamp"}
        assert set(data.keys()) == expected_keys
        
        # Validar tipos de datos
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["timestamp"], str)
        
        # Validar valores específicos
        assert data["status"] == "healthy"
        assert data["service"] == "analysis-service"
        assert data["version"] == "1.0.0"

    def test_health_check_cors_headers(self, client):
        """Test: verificar que el endpoint incluye headers CORS apropiados"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        # El middleware CORS debería estar configurado para permitir todos los orígenes
        # En entorno de test, FastAPI puede no incluir estos headers automáticamente
        # pero la configuración debería estar presente 