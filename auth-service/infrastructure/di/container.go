package di

import (
	domainRepos "auth-service/domain/repositories"
	domainServices "auth-service/domain/services"
	"auth-service/entrypoints/api"
	infraRepos "auth-service/infrastructure/repositories"
	infraServices "auth-service/infrastructure/services"
	"auth-service/usecases"
)

// Container maneja la inyección de dependencias
type Container struct {
	UserRepository       domainRepos.UserRepository
	TokenService         domainServices.TokenService
	LoginUseCase         *usecases.LoginUseCase
	ValidateTokenUseCase *usecases.ValidateTokenUseCase
	AuthController       *api.AuthController
	TokenController      *api.TokenController
	HealthController     *api.HealthController
}

// NewContainer crea una nueva instancia del contenedor de dependencias
func NewContainer() (*Container, error) {
	// Crear repositorios
	userRepo := infraRepos.NewInMemoryUserRepository()

	// Crear servicios
	tokenService, err := infraServices.NewJWTTokenService()
	if err != nil {
		return nil, err
	}

	// Crear casos de uso
	loginUseCase := usecases.NewLoginUseCase(userRepo, tokenService)
	validateTokenUseCase := usecases.NewValidateTokenUseCase(tokenService)

	// Crear controladores
	authController := api.NewAuthController(loginUseCase, validateTokenUseCase)
	tokenController := api.NewTokenController(tokenService)
	healthController := api.NewHealthController()

	return &Container{
		UserRepository:       userRepo,
		TokenService:         tokenService,
		LoginUseCase:         loginUseCase,
		ValidateTokenUseCase: validateTokenUseCase,
		AuthController:       authController,
		TokenController:      tokenController,
		HealthController:     healthController,
	}, nil
}
