package api

import (
	"net/http"

	"auth-service/domain/services"
	"auth-service/infrastructure/logger"

	"github.com/gin-gonic/gin"
)

// TokenController maneja las peticiones HTTP relacionadas con tokens
type TokenController struct {
	tokenService services.TokenService
}

// NewTokenController crea una nueva instancia de TokenController
func NewTokenController(tokenService services.TokenService) *TokenController {
	return &TokenController{
		tokenService: tokenService,
	}
}

// GetPublicKey maneja la petición para obtener la llave pública
// @Summary Obtener llave pública
// @Description Obtiene la llave pública RSA para verificar tokens JWT
// @Tags tokens
// @Produce application/x-pem-file
// @Success 200 {string} string "Llave pública en formato PEM"
// @Failure 500 {object} map[string]interface{} "Error interno del servidor"
// @Router /public-key [get]
func (c *TokenController) GetPublicKey(ctx *gin.Context) {
	// Establecer contexto para logging
	logger.SetContext(logger.Context{
		FunctionName: "TokenController.GetPublicKey",
		Data: map[string]interface{}{
			"endpoint": "/public-key",
		},
	})

	logger.Info("Solicitud de llave pública recibida")

	publicKey, err := c.tokenService.GetPublicKey()
	if err != nil {
		logger.Error("Error al obtener llave pública", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Error serializando llave pública"})
		return
	}

	logger.Success("Llave pública enviada exitosamente", map[string]interface{}{
		"public_key_length": len(publicKey),
	})

	ctx.Data(http.StatusOK, "application/x-pem-file", []byte(publicKey))
}
