package middlewares

import (
	"bytes"
	"io"
	"time"

	"auth-service/infrastructure/logger"

	"github.com/gin-gonic/gin"
)

// responseWriter es un wrapper para capturar la respuesta
type responseWriter struct {
	gin.ResponseWriter
	body *bytes.Buffer
}

func (w responseWriter) Write(b []byte) (int, error) {
	w.body.Write(b)
	return w.ResponseWriter.Write(b)
}

// LoggingMiddleware registra todas las peticiones HTTP
func LoggingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()

		// Capturar el cuerpo de la petición
		var requestBody []byte
		if c.Request.Body != nil {
			requestBody, _ = io.ReadAll(c.Request.Body)
			c.Request.Body = io.NopCloser(bytes.NewBuffer(requestBody))
		}

		// Crear wrapper para capturar la respuesta
		blw := &responseWriter{
			ResponseWriter: c.Writer,
			body:           bytes.NewBufferString(""),
		}
		c.Writer = blw

		// Establecer contexto para el logger
		logger.SetContext(logger.Context{
			FunctionName: "HTTP_Request",
			Data: map[string]interface{}{
				"method":     c.Request.Method,
				"path":       c.Request.URL.Path,
				"user_agent": c.Request.UserAgent(),
				"ip":         c.ClientIP(),
			},
		})

		// Log de inicio de petición
		logger.Info("Iniciando petición HTTP", map[string]interface{}{
			"request_body": string(requestBody),
		})

		// Procesar la petición
		c.Next()

		// Calcular duración
		duration := time.Since(start)

		// Log de fin de petición
		statusCode := c.Writer.Status()

		logData := map[string]interface{}{
			"status_code":   statusCode,
			"duration":      duration.String(),
			"response_size": len(blw.body.String()),
		}

		if statusCode >= 400 {
			logger.Error("Petición HTTP completada con error", nil)
		} else {
			logger.Success("Petición HTTP completada exitosamente", logData)
		}

		// Log detallado de errores si los hay
		if len(c.Errors) > 0 {
			for _, err := range c.Errors {
				logger.Error("Error en petición HTTP", err.Err)
			}
		}
	}
}
