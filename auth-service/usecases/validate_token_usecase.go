package usecases

import (
	"auth-service/domain/services"
	"auth-service/infrastructure/logger"
)

// ValidateTokenRequest representa la solicitud de validación de token
// @Description Token JWT a validar
type ValidateTokenRequest struct {
	// @Description Token JWT a validar
	// @example eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
	Token string `json:"token" validate:"required,jwt_token"`
}

// ValidateTokenResponse representa la respuesta de validación de token
// @Description Resultado de la validación del token JWT
type ValidateTokenResponse struct {
	// @Description Indica si el token es válido
	// @example true
	Valid bool `json:"valid"`
	// @Description Nombre de usuario del token (solo si es válido)
	// @example admin
	User string `json:"user,omitempty"`
	// @Description Mensaje de error (solo si el token es inválido)
	// @example token expired
	Error string `json:"error,omitempty"`
}

// ValidateTokenUseCase maneja la lógica de negocio para validar tokens
type ValidateTokenUseCase struct {
	tokenService services.TokenService
}

// NewValidateTokenUseCase crea una nueva instancia de ValidateTokenUseCase
func NewValidateTokenUseCase(tokenService services.TokenService) *ValidateTokenUseCase {
	return &ValidateTokenUseCase{
		tokenService: tokenService,
	}
}

// Execute ejecuta el caso de uso de validación de token
func (uc *ValidateTokenUseCase) Execute(request ValidateTokenRequest) *ValidateTokenResponse {
	// Establecer contexto para logging
	logger.SetContext(logger.Context{
		FunctionName: "ValidateTokenUseCase.Execute",
		Data: map[string]interface{}{
			"token_length": len(request.Token),
		},
	})

	logger.Info("Ejecutando validación de token")

	// Validar token
	logger.Info("Validando token JWT")
	claims, err := uc.tokenService.ValidateToken(request.Token)
	if err != nil {
		logger.Error("Token inválido", err)
		return &ValidateTokenResponse{
			Valid: false,
			Error: err.Error(),
		}
	}

	logger.Success("Token validado exitosamente", map[string]interface{}{
		"username": claims.Username,
		"user_id":  claims.UserID,
	})

	return &ValidateTokenResponse{
		Valid: true,
		User:  claims.Username,
	}
}
