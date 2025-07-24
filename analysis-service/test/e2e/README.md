# Tests End-to-End (E2E) - Analysis Service

Este directorio contiene tests end-to-end comprensivos para el servicio de análisis de archivos de configuración de red.

## 📋 Descripción

Los tests E2E validan el flujo completo del servicio desde la petición HTTP hasta la respuesta, incluyendo:

- ✅ Autenticación y autorización
- ✅ Validación de parámetros  
- ✅ Encriptación/desencriptación de archivos
- ✅ Integración con servicios externos (Config Service, Gemini API)
- ✅ Persistencia en MongoDB
- ✅ Manejo de errores y casos límite
- ✅ Performance y logging

## 🗂️ Estructura de Archivos

```
test/e2e/
├── __init__.py                    # Marcador de paquete Python
├── conftest.py                    # Configuración y fixtures compartidas
├── test_health_endpoint.py        # Tests del endpoint de health
├── test_analysis_endpoint.py      # Tests del endpoint principal de análisis
├── test_authentication.py         # Tests de autenticación y autorización
├── test_error_scenarios.py        # Tests de manejo de errores
├── test_integration_flow.py       # Tests de flujo completo de integración
├── pytest.ini                     # Configuración de pytest
└── README.md                      # Esta documentación
```

## 🚀 Ejecución de Tests

### Prerrequisitos

1. **Python 3.8+** instalado
2. **Dependencias** instaladas:
   ```bash
   pip install -r requirements-test.txt
   ```

### Métodos de Ejecución

#### 1. Script Automatizado (Recomendado)

```bash
# Desde el directorio raíz del analysis-service
python run_e2e_tests.py
```

**Opciones disponibles:**
```bash
# Ejecutar todos los tests
python run_e2e_tests.py

# Con reporte de cobertura
python run_e2e_tests.py --coverage

# Solo tests rápidos
python run_e2e_tests.py --fast

# Solo tests de autenticación
python run_e2e_tests.py --auth

# Tests específicos
python run_e2e_tests.py --specific "health"

# Salida detallada
python run_e2e_tests.py --verbose
```

#### 2. Pytest Directo

```bash
# Cambiar al directorio de tests e2e
cd test/e2e

# Ejecutar todos los tests
pytest -v

# Con cobertura
pytest --cov=../../app --cov-report=html

# Tests específicos
pytest test_health_endpoint.py -v
pytest -k "test_auth" -v
```

## 📊 Tipos de Tests

### 1. Health Endpoint (`test_health_endpoint.py`)
- ✅ Verificación de estado del servicio
- ✅ Acceso sin autenticación
- ✅ Formato de respuesta
- ✅ Headers CORS

### 2. Analysis Endpoint (`test_analysis_endpoint.py`)
- ✅ Flujo completo de análisis exitoso
- ✅ Integración con Gemini API
- ✅ Proceso de encriptación/desencriptación
- ✅ Validación de parámetros
- ✅ Manejo de errores de servicios externos

### 3. Authentication (`test_authentication.py`)
- ✅ Autenticación con token válido/inválido
- ✅ Tokens expirados y malformados
- ✅ Middleware de autenticación
- ✅ Endpoints públicos vs protegidos
- ✅ Diferentes contextos de usuario

### 4. Error Scenarios (`test_error_scenarios.py`)
- ✅ Nombres de archivo inválidos
- ✅ Timeouts de servicios externos
- ✅ Fallos de MongoDB
- ✅ Rate limits de Gemini API
- ✅ Fallos múltiples simultáneos

### 5. Integration Flow (`test_integration_flow.py`)
- ✅ Flujo completo con configuración insegura
- ✅ Flujo completo con configuración segura
- ✅ Performance y logging del sistema

## 🔧 Configuración

### Variables de Entorno

Los tests configuran automáticamente estas variables:

```bash
ENVIRONMENT=test
ENCRYPTION_KEY=test_encryption_key_for_e2e
CONFIG_SERVICE_URL=http://localhost:8000
GEMINI_API_KEY=test_gemini_api_key
MONGODB_URL=mongodb://localhost:27017/test_db
PORT=8002
```

### Fixtures Disponibles

- `client`: Cliente síncrono de FastAPI
- `async_client`: Cliente asíncrono de FastAPI
- `valid_auth_token`: Token de autenticación válido
- `mock_auth_middleware`: Mock del middleware de autenticación
- `mock_config_service`: Mock del servicio de configuración
- `mock_gemini_api`: Mock de Google Gemini API
- `mock_mongodb`: Mock de MongoDB
- `mock_encrypt_service`: Mock del servicio de encriptación

## 📈 Reportes y Cobertura

### Reporte de Cobertura HTML
```bash
python run_e2e_tests.py --coverage
# Genera: htmlcov/index.html
```

### Reporte en Terminal
```bash
pytest --cov=../../app --cov-report=term-missing
```

### Métricas Objetivo
- **Cobertura mínima**: 80%
- **Tiempo de ejecución**: < 30 segundos
- **Tasa de éxito**: 100%

## 🧪 Casos de Prueba Cubiertos

### Escenarios Exitosos
- ✅ Análisis de archivo con problemas de seguridad críticos
- ✅ Análisis de archivo con configuración segura
- ✅ Autenticación exitosa con diferentes usuarios
- ✅ Recuperación ante fallos de servicios externos

### Escenarios de Error
- ✅ Autenticación fallida (token inválido/expirado)
- ✅ Parámetros de entrada inválidos
- ✅ Servicios externos no disponibles
- ✅ Fallos de encriptación/desencriptación
- ✅ Errores de base de datos

### Casos Límite
- ✅ Nombres de archivo con caracteres especiales
- ✅ Archivos extremadamente largos
- ✅ Timeouts de red
- ✅ Respuestas malformadas de APIs externas

## 🔍 Debugging

### Logs Detallados
```bash
pytest -v -s --log-cli-level=DEBUG
```

### Tests Específicos
```bash
# Un test específico
pytest test_health_endpoint.py::TestHealthEndpoint::test_health_check_sync -v

# Tests que fallan
pytest --lf

# Tests más lentos
pytest --durations=10
```

### Modo Debugging
```bash
# Con breakpoints
pytest --pdb

# Con coverage y debugging
pytest --cov=../../app --pdb-trace
```

## 🏗️ Arquitectura de Tests

### Patrón de Diseño
- **Arrange**: Configuración de mocks y datos
- **Act**: Ejecución de la petición HTTP
- **Assert**: Validación de respuesta y efectos

### Estrategia de Mocking
- **Servicios externos**: Completamente mockeados
- **Base de datos**: Mock en memoria
- **Autenticación**: Mock configurable
- **APIs externas**: Respuestas controladas

### Aislamiento
- Cada test es independiente
- Estado limpio entre tests
- Mocks específicos por test

## 📝 Contribuir

### Agregar Nuevos Tests

1. **Identificar el escenario** a probar
2. **Elegir el archivo apropiado** o crear uno nuevo
3. **Seguir el patrón AAA** (Arrange, Act, Assert)
4. **Usar fixtures existentes** cuando sea posible
5. **Documentar el propósito** del test

### Ejemplo de Test
```python
@pytest_asyncio.async_test
async def test_nuevo_escenario(
    self, 
    async_client, 
    valid_auth_token,
    mock_auth_middleware,
    # ... otros fixtures necesarios
):
    """Test: descripción clara del escenario"""
    # Arrange
    headers = {"Authorization": valid_auth_token}
    params = {"filename": "test.txt"}
    
    # Act
    response = await async_client.get("/api/v1/analyze", headers=headers, params=params)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
```

## 🚨 Troubleshooting

### Problemas Comunes

1. **Tests lentos**: Verificar que los mocks estén configurados correctamente
2. **Fallos de importación**: Asegurar que `PYTHONPATH` incluya el directorio raíz
3. **Errores de fixtures**: Verificar que `conftest.py` esté en el directorio correcto
4. **Fallos de async**: Usar `@pytest_asyncio.async_test` para tests asíncronos

### Verificación Rápida
```bash
# Verificar que pytest encuentra los tests
pytest --collect-only

# Verificar fixtures disponibles
pytest --fixtures

# Test de conectividad básica
pytest test_health_endpoint.py::TestHealthEndpoint::test_health_check_sync -v
```

## 📞 Soporte

Para problemas con los tests E2E:

1. **Verificar logs** de ejecución
2. **Revisar configuración** de entorno
3. **Validar dependencias** instaladas
4. **Consultar documentación** del proyecto principal

---

**Nota**: Estos tests están diseñados para ejecutarse en un entorno aislado con mocks. No requieren servicios externos reales funcionando. 