# Objetivo del challenge:
Se debe desarrollar una solución que tenga 2 servicios para poder analizar el estado de seguridad de un dispositivo de red.
- Un servicio orientado a disponibilizar la configuración de un dispositivo de red. Para este challenge vamos a otorgarles un archivo de texto que simule ser la configuración real.
- Un servicio que tenga la responsabilidad de analizar el archivo de configuración. Este servicio debe comunicarse con el primero mencionado y utilizar la configuración obtenida como input a analizar. A su vez, debe contar con una interfaz (API) que disponibilice los resultados del analisis, los cuales deben estar perisistidos para poder ser accedidos en cualquier momento.

# Estructura Esperada del Challenge
## Contenedores Docker:
- **config-service**: solo puede tener conectividad con `analysis-service`.
- **analysis-service**: debe poder ser accedido desde el host y tener conectividad con `config-service`.

## Desarrollo:
- Definir APIs funcionales para cada servicio (`config-service`, `analysis-service`).
- La aplicación debe estar escrita en un lenguaje backend como Python, Go, Javascript o el que desee.
- `analysis-service` debe tener una comunicación con `config-service` y retornar un analisis de seguridad basado en la configuración recibida.
- **Docker Compose**: El candidato debe incluir un archivo `docker-compose.yml` que defina los contenedores y las redes.
- **Seguridad**: Todos los servicios deben estar autenticados.

## Documentación:
- **Documentación de los endpoints**: Debe incluir la documentación de cada endpoint desarrollado y sus funcionalidades.
- **Manual**: Incluir un manual en formato PDF o Markdown que explique cómo utilizar la solución, incluyendo ejemplos de uso de las APIs y configuración de las redes Docker. Es válido el uso de diagramas.

# Extras:
- **Swagger**: Se debe proporcionar una especificación de Swagger que describa todos los endpoints y su uso.
- **Logs y Monitoreo Avanzado**: Implementar una solución para monitorear y visualizar los logs en tiempo real.
- **Tests Automatizados**: Incluir pruebas unitarias y de integración para los servicios, utilizando herramientas como JUnit, PyTest. (Se puede proponer otra biblioteca).
- **Seguridad**: Autorización, cifrado de tráfico, entre otras oportunidades de hardening que aumenten la seguridad de la solución.

# Entrega del Proyecto
El candidato debe entregar los siguientes elementos:
- **Código Fuente**: Todo el código fuente del proyecto debe estar disponible en este repositorio.
- **Docker Compose**: El archivo `docker-compose.yml` debe estar correctamente configurado.
- **Documentación**: Swagger y un manual detallado en formato PDF o Markdown.
- **Base de Datos**: El esquema de base de datos debe estar claramente definido, y los logs deben ser almacenados de forma eficiente.
- **Instrucciones de Ejecución**: El candidato debe proporcionar instrucciones claras sobre cómo ejecutar los contenedores, acceder a las APIs y probar la solución.
