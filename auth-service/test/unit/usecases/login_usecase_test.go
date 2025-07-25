package usecases

import (
	"auth-service/domain/entities"
	"auth-service/usecases"
	"testing"
	"time"
)

// MockUserRepository para testing
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
	if user, exists := m.users[username]; exists {
		return user, nil
	}
	return nil, &MockError{message: "user not found"}
}

func (m *MockUserRepository) Exists(username string) (bool, error) {
	_, exists := m.users[username]
	return exists, nil
}

// MockPasswordService para testing
type MockPasswordService struct{}

func (m *MockPasswordService) HashPassword(password string) (string, error) {
	return "$2a$12$mockhash", nil
}

func (m *MockPasswordService) ComparePassword(hashedPassword, password string) error {
	if password == "Password123!" {
		return nil
	}
	return &MockError{message: "password incorrecto"}
}

// MockTokenService para testing
type MockTokenService struct{}

func (m *MockTokenService) GenerateToken(user *entities.User) (*entities.Token, error) {
	now := time.Now()
	return entities.NewToken("mock.token.value", user.ID, user.Username, now.Add(1*time.Hour), now), nil
}

func (m *MockTokenService) ValidateToken(tokenString string) (*entities.TokenClaims, error) {
	return nil, nil
}

func (m *MockTokenService) GetPublicKey() (string, error) {
	return "mock-public-key", nil
}

type MockError struct {
	message string
}

func (e *MockError) Error() string {
	return e.message
}

func TestNewLoginUseCase(t *testing.T) {
	// Arrange
	mockRepo := NewMockUserRepository()
	passwordService := &MockPasswordService{}
	tokenService := &MockTokenService{}

	// Act
	loginUseCase := usecases.NewLoginUseCase(mockRepo, tokenService, passwordService)

	// Assert
	if loginUseCase == nil {
		t.Fatal("Expected LoginUseCase instance, got nil")
	}
}

func TestLoginUseCase_Execute_Success(t *testing.T) {
	// Arrange
	mockRepo := NewMockUserRepository()
	passwordService := &MockPasswordService{}
	tokenService := &MockTokenService{}
	loginUseCase := usecases.NewLoginUseCase(mockRepo, tokenService, passwordService)

	// Crear usuario de prueba
	user := entities.NewUser("admin", "Password123!")
	hashedPassword, _ := passwordService.HashPassword("Password123!")
	user.Password = hashedPassword
	mockRepo.Save(user)

	request := usecases.LoginRequest{
		Username: "admin",
		Password: "Password123!",
	}

	// Act
	response, err := loginUseCase.Execute(request)

	// Assert
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if response == nil {
		t.Fatal("Expected response, got nil")
	}
	if response.Token == "" {
		t.Error("Expected token in response")
	}
	if response.User != user.Username {
		t.Errorf("Expected User '%s', got '%s'", user.Username, response.User)
	}
}

func TestLoginUseCase_Execute_InvalidCredentials(t *testing.T) {
	// Arrange
	mockRepo := NewMockUserRepository()
	passwordService := &MockPasswordService{}
	tokenService := &MockTokenService{}
	loginUseCase := usecases.NewLoginUseCase(mockRepo, tokenService, passwordService)

	// Crear usuario de prueba
	user := entities.NewUser("admin", "Password123!")
	hashedPassword, _ := passwordService.HashPassword("Password123!")
	user.Password = hashedPassword
	mockRepo.Save(user)

	request := usecases.LoginRequest{
		Username: "admin",
		Password: "WrongPassword",
	}

	// Act
	response, err := loginUseCase.Execute(request)

	// Assert
	if err == nil {
		t.Error("Expected error for invalid credentials")
	}
	if response != nil {
		t.Error("Expected nil response for invalid credentials")
	}
}

func TestLoginUseCase_Execute_UserNotFound(t *testing.T) {
	// Arrange
	mockRepo := NewMockUserRepository()
	passwordService := &MockPasswordService{}
	tokenService := &MockTokenService{}
	loginUseCase := usecases.NewLoginUseCase(mockRepo, tokenService, passwordService)

	request := usecases.LoginRequest{
		Username: "nonexistent",
		Password: "Password123!",
	}

	// Act
	response, err := loginUseCase.Execute(request)

	// Assert
	if err == nil {
		t.Error("Expected error for user not found")
	}
	if response != nil {
		t.Error("Expected nil response for user not found")
	}
}

func TestLoginUseCase_Execute_EmptyRequest(t *testing.T) {
	// Arrange
	mockRepo := NewMockUserRepository()
	passwordService := &MockPasswordService{}
	tokenService := &MockTokenService{}
	loginUseCase := usecases.NewLoginUseCase(mockRepo, tokenService, passwordService)

	request := usecases.LoginRequest{
		Username: "",
		Password: "",
	}

	// Act
	response, err := loginUseCase.Execute(request)

	// Assert
	if err == nil {
		t.Error("Expected error for empty request")
	}
	if response != nil {
		t.Error("Expected nil response for empty request")
	}
}
