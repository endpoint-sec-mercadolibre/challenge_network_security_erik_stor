package di

import (
	domainRepos "auth-service/domain/repositories"
	domainServices "auth-service/domain/services"
	"auth-service/entrypoints/api"
	infraRepos "auth-service/infrastructure/repositories"
	infraServices "auth-service/infrastructure/services"
	"auth-service/usecases"
	"os"
)

// Container maneja la inyección de dependencias
type Container struct {
	UserRepository       domainRepos.UserRepository
	TokenService         domainServices.TokenService
	PasswordService      domainServices.PasswordService
	SeedService          domainServices.SeedService
	LoginUseCase         *usecases.LoginUseCase
	ValidateTokenUseCase *usecases.ValidateTokenUseCase
	AuthController       *api.AuthController
	TokenController      *api.TokenController
	HealthController     *api.HealthController
}

// NewContainer crea una nueva instancia del contenedor de dependencias
func NewContainer() (*Container, error) {
	// Obtener configuración de MongoDB desde variables de entorno
	mongoURI := os.Getenv("MONGO_URI")
	if mongoURI == "" {
		mongoURI = "mongodb://localhost:27017"
	}

	databaseName := os.Getenv("MONGO_DATABASE")
	if databaseName == "" {
		databaseName = "auth_service"
	}

	// Crear repositorio de MongoDB
	userRepo, err := infraRepos.NewMongoDBUserRepository(mongoURI, databaseName)
	if err != nil {
		return nil, err
	}

	// Crear servicios
	tokenService, err := infraServices.NewJWTTokenService()
	if err != nil {
		return nil, err
	}

	passwordService := domainServices.NewDefaultPasswordService()
	seedService := domainServices.NewDefaultSeedService(userRepo, passwordService)

	// Crear casos de uso
	loginUseCase := usecases.NewLoginUseCase(userRepo, tokenService, passwordService)
	validateTokenUseCase := usecases.NewValidateTokenUseCase(tokenService)

	// Crear controladores
	authController := api.NewAuthController(loginUseCase, validateTokenUseCase)
	tokenController := api.NewTokenController(tokenService)
	healthController := api.NewHealthController(seedService)

	return &Container{
		UserRepository:       userRepo,
		TokenService:         tokenService,
		PasswordService:      passwordService,
		SeedService:          seedService,
		LoginUseCase:         loginUseCase,
		ValidateTokenUseCase: validateTokenUseCase,
		AuthController:       authController,
		TokenController:      tokenController,
		HealthController:     healthController,
	}, nil
}
