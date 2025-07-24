package usecases

import (
	"auth-service/domain/entities"
	"testing"
)

// MockValidateTokenService para testing
type MockValidateTokenService struct{}

func (m *MockValidateTokenService) GenerateToken(user *entities.User) (*entities.Token, error) {
	return nil, nil
}

func (m *MockValidateTokenService) ValidateToken(tokenString string) (*entities.TokenClaims, error) {
	if tokenString == "valid.token" {
		return &entities.TokenClaims{
			UserID:   "test-user-id",
			Username: "testuser",
		}, nil
	}
	return nil, &ValidateTokenMockError{message: "invalid token"}
}

func (m *MockValidateTokenService) GetPublicKey() (string, error) {
	return "mock-public-key", nil
}

type ValidateTokenMockError struct {
	message string
}

func (e *ValidateTokenMockError) Error() string {
	return e.message
}

func TestNewValidateTokenUseCase(t *testing.T) {
	// Arrange
	tokenService := &MockValidateTokenService{}

	// Act
	validateTokenUseCase := NewValidateTokenUseCase(tokenService)

	// Assert
	if validateTokenUseCase == nil {
		t.Fatal("Expected ValidateTokenUseCase instance, got nil")
	}
}

func TestValidateTokenUseCase_Execute_ValidToken(t *testing.T) {
	// Arrange
	tokenService := &MockValidateTokenService{}
	validateTokenUseCase := NewValidateTokenUseCase(tokenService)

	request := ValidateTokenRequest{
		Token: "valid.token",
	}

	// Act
	response := validateTokenUseCase.Execute(request)

	// Assert
	if response == nil {
		t.Fatal("Expected response, got nil")
	}
	if !response.Valid {
		t.Error("Expected token to be valid")
	}
	if response.User != "testuser" {
		t.Errorf("Expected User 'testuser', got '%s'", response.User)
	}
	if response.Error != "" {
		t.Errorf("Expected no error, got '%s'", response.Error)
	}
}

func TestValidateTokenUseCase_Execute_InvalidToken(t *testing.T) {
	// Arrange
	tokenService := &MockValidateTokenService{}
	validateTokenUseCase := NewValidateTokenUseCase(tokenService)

	request := ValidateTokenRequest{
		Token: "invalid.token",
	}

	// Act
	response := validateTokenUseCase.Execute(request)

	// Assert
	if response == nil {
		t.Fatal("Expected response, got nil")
	}
	if response.Valid {
		t.Error("Expected token to be invalid")
	}
	if response.Error == "" {
		t.Error("Expected error message")
	}
}

func TestValidateTokenUseCase_Execute_EmptyToken(t *testing.T) {
	// Arrange
	tokenService := &MockValidateTokenService{}
	validateTokenUseCase := NewValidateTokenUseCase(tokenService)

	request := ValidateTokenRequest{
		Token: "",
	}

	// Act
	response := validateTokenUseCase.Execute(request)

	// Assert
	if response == nil {
		t.Fatal("Expected response, got nil")
	}
	if response.Valid {
		t.Error("Expected token to be invalid")
	}
	if response.Error == "" {
		t.Error("Expected error message")
	}
} 