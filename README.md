# Objetivo del Challenge

Desarrollar una solución compuesta por 2 servicios que permitan analizar el estado de seguridad de un dispositivo de red.

- **Servicio de Configuración**: Este servicio proporcionará la configuración de un dispositivo de red. Para los fines de este challenge, se entregará un archivo de texto que simulará ser la configuración real.
- **Servicio de Análisis**: Responsable de analizar el archivo de configuración suministrado. El análisis debe realizarse mediante un modelo LLM, identificando configuraciones inseguras, clasificándolas según su severidad (_baja, media, alta y crítica_) y generando un resumen en lenguaje natural que incluya posibles soluciones a los hallazgos.

---

# Estructura Esperada del Challenge

## Contenedores Docker

- **config-service**: Debe tener conectividad únicamente con `analysis-service`.
- **analysis-service**: Debe ser accesible desde el host y tener comunicación exclusiva con `config-service`.

## Desarrollo

- Definir endpoints funcionales para cada servicio (`config-service` y `analysis-service`).
- La solución debe implementarse en un lenguaje backend como **Python**, **Go**, **JavaScript**, entre otros.
- `analysis-service` debe comunicarse con `config-service` y retornar un análisis de seguridad basado en la configuración recibida.
- **Docker Compose**: Incluir un archivo `docker-compose.yml` que defina los contenedores y redes necesarias.
- **Seguridad**: Todos los servicios deben implementar mecanismos de autenticación.

## Documentación

- **APIs**: Documentar detalladamente todos los endpoints desarrollados y sus funcionalidades.
- **Manual de Usuario**: Incluir un manual en formato PDF o Markdown con instrucciones de uso, ejemplos de llamadas a las APIs y detalles sobre la configuración de redes en Docker. Se recomienda adjuntar diagramas para mayor claridad.

---

# Requisitos Adicionales

- **Swagger**: Proveer una especificación en Swagger que describa todos los endpoints y su uso.
- **Logs y Monitoreo**: Implementar una solución para el monitoreo y visualización de logs en tiempo real.
- **Pruebas Automatizadas**: Incluir pruebas unitarias y de integración para los servicios (por ejemplo, utilizando **JUnit**, **PyTest** u otras herramientas afines).
- **Seguridad Avanzada**: Implementar características de autorización, cifrado de tráfico y otras medidas de hardening que refuercen la seguridad de la solución.
- **Persistencia de Datos**: Guardar en una base de datos los resultados generados por el modelo LLM.
- **Optimización del LLM**: Garantizar un uso eficiente y determinístico del LLM, explotando todas sus capacidades de integración.
- **Control del Análisis IA**: Incorporar una funcionalidad que permita habilitar o deshabilitar dinámicamente el análisis basado en inteligencia artificial, según los requerimientos del usuario.

---

# Entregables

El candidato debe entregar los siguientes elementos:

- **Código Fuente**: Todo el código del proyecto debe estar alojado en este repositorio.
- **Docker Compose**: Archivo `docker-compose.yml` completamente funcional.
- **Documentación**: Especificación Swagger y manual detallado (PDF o Markdown).
- **Base de Datos**: Esquema de base de datos definido y logs almacenados de manera eficiente.
- **Instrucciones de Ejecución**: Guía clara para ejecutar los contenedores, acceder a las APIs y probar la solución.
