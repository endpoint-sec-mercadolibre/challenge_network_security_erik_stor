package test

import (
	"auth-service/domain/entities"
	"auth-service/domain/repositories"
	"auth-service/domain/services"
	"auth-service/usecases"
	"errors"
)

// TestConfig proporciona configuración y mocks para los tests
type TestConfig struct {
	UserRepository  repositories.UserRepository
	TokenService    services.TokenService
	PasswordService services.PasswordService
	SeedService     services.SeedService
	LoginUseCase    *usecases.LoginUseCase
}

// NewTestConfig crea una nueva configuración de test con mocks
func NewTestConfig() *TestConfig {
	userRepo := NewMockUserRepository()
	tokenService := NewMockTokenService()
	passwordService := services.NewDefaultPasswordService()
	seedService := services.NewDefaultSeedService(userRepo, passwordService)
	loginUseCase := usecases.NewLoginUseCase(userRepo, tokenService, passwordService)

	return &TestConfig{
		UserRepository:  userRepo,
		TokenService:    tokenService,
		PasswordService: passwordService,
		SeedService:     seedService,
		LoginUseCase:    loginUseCase,
	}
}

// MockUserRepository implementa UserRepository para testing
type MockUserRepository struct {
	users map[string]*entities.User
}

func NewMockUserRepository() *MockUserRepository {
	return &MockUserRepository{
		users: make(map[string]*entities.User),
	}
}

func (m *MockUserRepository) Save(user *entities.User) error {
	m.users[user.Username] = user
	return nil
}

func (m *MockUserRepository) FindByUsername(username string) (*entities.User, error) {
	user, exists := m.users[username]
	if !exists {
		return nil, errors.New("user not found")
	}
	return user, nil
}

func (m *MockUserRepository) Exists(username string) (bool, error) {
	_, exists := m.users[username]
	return exists, nil
}

// MockTokenService implementa TokenService para testing
type MockTokenService struct {
	tokens map[string]*entities.Token
}

func NewMockTokenService() *MockTokenService {
	return &MockTokenService{
		tokens: make(map[string]*entities.Token),
	}
}

func (m *MockTokenService) GenerateToken(user *entities.User) (*entities.Token, error) {
	token := &entities.Token{
		Value:    "mock-jwt-token-" + user.ID,
		UserID:   user.ID,
		Username: user.Username,
	}
	m.tokens[user.ID] = token
	return token, nil
}

func (m *MockTokenService) ValidateToken(tokenValue string) (*entities.TokenClaims, error) {
	for _, token := range m.tokens {
		if token.Value == tokenValue {
			return &entities.TokenClaims{
				UserID:   token.UserID,
				Username: token.Username,
			}, nil
		}
	}
	return nil, errors.New("invalid token")
}

func (m *MockTokenService) GetPublicKey() (string, error) {
	return "mock-public-key", nil
}
