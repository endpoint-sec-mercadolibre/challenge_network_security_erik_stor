package api

import (
	"auth-service/domain/services"
	"auth-service/infrastructure/logger"
	"net/http"

	"github.com/gin-gonic/gin"
)

// HealthController maneja las peticiones HTTP relacionadas con health check
type HealthController struct {
	seedService services.SeedService
}

// NewHealthController crea una nueva instancia de HealthController
func NewHealthController(seedService services.SeedService) *HealthController {
	return &HealthController{
		seedService: seedService,
	}
}

// Health maneja la petición de health check
// @Summary Health check
// @Description Verifica el estado del servicio de autenticación y ejecuta semilla de datos
// @Tags health
// @Produce json
// @Success 200 {object} map[string]interface{} "Estado del servicio"
// @Failure 500 {object} map[string]interface{} "Error interno del servidor"
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

	// Ejecutar semilla de datos
	err := c.seedService.SeedDefaultUser()
	if err != nil {
		logger.Error("Error ejecutando semilla de datos", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"service": "auth-service",
			"message": "Error ejecutando semilla de datos",
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"status":  "ok",
		"service": "auth-service",
		"message": "Servicio funcionando correctamente y semilla ejecutada",
	})

	logger.Success("Health check completado exitosamente")
}
