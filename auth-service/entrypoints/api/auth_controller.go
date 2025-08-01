package api

import (
	"net/http"

	"auth-service/infrastructure/logger"
	"auth-service/middlewares"
	"auth-service/usecases"

	"github.com/gin-gonic/gin"
)

// AuthController maneja las peticiones HTTP relacionadas con autenticación
type AuthController struct {
	loginUseCase         *usecases.LoginUseCase
	validateTokenUseCase *usecases.ValidateTokenUseCase
	validationMiddleware *middlewares.ValidationMiddleware
}

// NewAuthController crea una nueva instancia de AuthController
func NewAuthController(
	loginUseCase *usecases.LoginUseCase,
	validateTokenUseCase *usecases.ValidateTokenUseCase,
) *AuthController {
	return &AuthController{
		loginUseCase:         loginUseCase,
		validateTokenUseCase: validateTokenUseCase,
		validationMiddleware: middlewares.NewValidationMiddleware(),
	}
}

// Login maneja la petición de login
// @Summary Autenticar usuario
// @Description Autentica un usuario con credenciales y devuelve un token JWT
// @Tags auth
// @Accept json
// @Produce json
// @Param request body usecases.LoginRequest true "Credenciales de login"
// @Success 200 {object} usecases.LoginResponse "Login exitoso"
// @Failure 400 {object} map[string]interface{} "Datos de entrada inválidos"
// @Failure 401 {object} map[string]interface{} "Credenciales inválidas"
// @Router /login [post]
func (c *AuthController) Login(ctx *gin.Context) {
	// Establecer contexto para logging
	logger.SetContext(logger.Context{
		FunctionName: "AuthController.Login",
		Data: map[string]interface{}{
			"endpoint": "/login",
		},
	})

	logger.Info("Iniciando proceso de login")

	// Obtener la request validada del middleware
	validatedRequest, exists := ctx.Get("validated_request")
	if !exists {
		logger.Error("Request no validada encontrada", nil)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Error interno del servidor"})
		return
	}

	// Hacer type assertion correcta para el puntero
	requestPtr, ok := validatedRequest.(*usecases.LoginRequest)
	if !ok {
		logger.Error("Tipo de request inválido", nil)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Error interno del servidor"})
		return
	}
	request := *requestPtr

	logger.Info("Datos de login recibidos", map[string]interface{}{
		"username": request.Username,
	})

	response, err := c.loginUseCase.Execute(request)
	if err != nil {
		logger.Error("Error en proceso de login", err)
		ctx.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	logger.Success("Login exitoso", map[string]interface{}{
		"username": request.Username,
	})

	ctx.JSON(http.StatusOK, response)
}

// ValidateToken maneja la petición de validación de token
// @Summary Validar token JWT
// @Description Valida un token JWT y devuelve información sobre su validez
// @Tags auth
// @Accept json
// @Produce json
// @Param request body usecases.ValidateTokenRequest true "Token a validar"
// @Success 200 {object} usecases.ValidateTokenResponse "Validación completada"
// @Failure 400 {object} map[string]interface{} "Token requerido"
// @Router /validate [post]
func (c *AuthController) ValidateToken(ctx *gin.Context) {
	// Establecer contexto para logging
	logger.SetContext(logger.Context{
		FunctionName: "AuthController.ValidateToken",
		Data: map[string]interface{}{
			"endpoint": "/validate",
		},
	})

	logger.Info("Iniciando validación de token")

	// Obtener la request validada del middleware
	validatedRequest, exists := ctx.Get("validated_request")
	if !exists {
		logger.Error("Request no validada encontrada", nil)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Error interno del servidor"})
		return
	}

	// Hacer type assertion correcta para el puntero
	requestPtr, ok := validatedRequest.(*usecases.ValidateTokenRequest)
	if !ok {
		logger.Error("Tipo de request inválido", nil)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Error interno del servidor"})
		return
	}
	request := *requestPtr

	logger.Info("Token recibido para validación", map[string]interface{}{
		"token_length": len(request.Token),
	})

	response := c.validateTokenUseCase.Execute(request)

	logger.Success("Validación de token completada", map[string]interface{}{
		"valid": response.Valid,
	})

	ctx.JSON(http.StatusOK, response)
}
