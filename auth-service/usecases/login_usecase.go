package usecases

import (
	"auth-service/domain/repositories"
	"auth-service/domain/services"
	"auth-service/infrastructure/logger"
	"errors"
)

// LoginRequest representa la solicitud de login
// @Description Credenciales de autenticación del usuario
type LoginRequest struct {
	// @Description Nombre de usuario
	// @example admin
	Username string `json:"username" validate:"required,username"`
	// @Description Contraseña del usuario
	// @example Password123!
	Password string `json:"password" validate:"required,password"`
}

// LoginResponse representa la respuesta del login
// @Description Respuesta exitosa del login con token JWT
type LoginResponse struct {
	// @Description Token JWT generado para el usuario
	// @example eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
	Token string `json:"token"`
	// @Description Nombre de usuario autenticado
	// @example admin
	User string `json:"user"`
}

// LoginUseCase maneja la lógica de negocio para el login
type LoginUseCase struct {
	userRepo        repositories.UserRepository
	tokenService    services.TokenService
	passwordService services.PasswordService
}

// NewLoginUseCase crea una nueva instancia de LoginUseCase
func NewLoginUseCase(userRepo repositories.UserRepository, tokenService services.TokenService, passwordService services.PasswordService) *LoginUseCase {
	return &LoginUseCase{
		userRepo:        userRepo,
		tokenService:    tokenService,
		passwordService: passwordService,
	}
}

// Execute ejecuta el caso de uso de login
func (uc *LoginUseCase) Execute(request LoginRequest) (*LoginResponse, error) {
	// Establecer contexto para logging
	logger.SetContext(logger.Context{
		FunctionName: "LoginUseCase.Execute",
		Data: map[string]interface{}{
			"username": request.Username,
		},
	})

	logger.Info("Ejecutando caso de uso de login")

	// Buscar usuario por username
	logger.Info("Buscando usuario en repositorio")
	user, err := uc.userRepo.FindByUsername(request.Username)
	if err != nil {
		logger.Error("Usuario no encontrado", err)
		return nil, errors.New("credenciales inválidas")
	}

	logger.Info("Usuario encontrado", map[string]interface{}{
		"user_id": user.ID,
	})

	// Validar credenciales
	logger.Info("Validando credenciales del usuario")
	if !user.ValidateCredentials(request.Password, uc.passwordService) {
		logger.Error("Credenciales inválidas", errors.New("password incorrecto"))
		return nil, errors.New("credenciales inválidas")
	}

	logger.Success("Credenciales validadas correctamente")

	// Generar token
	logger.Info("Generando token JWT")
	token, err := uc.tokenService.GenerateToken(user)
	if err != nil {
		logger.Error("Error al generar token", err)
		return nil, errors.New("error generando token")
	}

	logger.Success("Token generado exitosamente", map[string]interface{}{
		"user_id":  token.UserID,
		"username": token.Username,
	})

	return &LoginResponse{
		Token: token.Value,
		User:  user.Username,
	}, nil
}
