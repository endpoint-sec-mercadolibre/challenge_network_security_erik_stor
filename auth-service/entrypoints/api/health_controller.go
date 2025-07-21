package api

import (
	"auth-service/infrastructure/logger"
	"net/http"

	"github.com/gin-gonic/gin"
)

// HealthController maneja las peticiones HTTP relacionadas con health check
type HealthController struct{}

// NewHealthController crea una nueva instancia de HealthController
func NewHealthController() *HealthController {
	return &HealthController{}
}

// Health maneja la petición de health check
// @Summary Health check
// @Description Verifica el estado del servicio de autenticación
// @Tags health
// @Produce json
// @Success 200 {object} map[string]interface{} "Estado del servicio"
// @Router /health [get]
func (c *HealthController) Health(ctx *gin.Context) {
	// Establecer contexto para logging
	logger.SetContext(logger.Context{
		FunctionName: "HealthController.Health",
		Data: map[string]interface{}{
			"endpoint": "/health",
		},
	})

	logger.Info("Health check solicitado")

	ctx.JSON(http.StatusOK, gin.H{
		"status":  "ok",
		"service": "auth-service",
	})

	logger.Success("Health check completado exitosamente")
}
