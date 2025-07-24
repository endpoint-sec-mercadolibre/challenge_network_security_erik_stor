package services

import (
	"auth-service/domain/entities"
	"testing"
	"time"
)

// MockTokenService para testing
type MockTokenService struct{}

func (m *MockTokenService) GenerateToken(user *entities.User) (*entities.Token, error) {
	now := time.Now()
	return entities.NewToken("mock.token.value", user.ID, user.Username, now.Add(1*time.Hour), now), nil
}

func (m *MockTokenService) ValidateToken(tokenString string) (*entities.TokenClaims, error) {
	if tokenString == "valid.token" {
		return &entities.TokenClaims{
			UserID:   "test-user-id",
			Username: "testuser",
		}, nil
	}
	return nil, &TokenMockError{message: "invalid token"}
}

func (m *MockTokenService) GetPublicKey() (string, error) {
	return "mock-public-key", nil
}

type TokenMockError struct {
	message string
}

func (e *TokenMockError) Error() string {
	return e.message
}

func TestMockTokenService_GenerateToken(t *testing.T) {
	// Arrange
	tokenService := &MockTokenService{}
	user := entities.NewUser("testuser", "password123")

	// Act
	token, err := tokenService.GenerateToken(user)

	// Assert
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if token == nil {
		t.Fatal("Expected token instance, got nil")
	}
	if token.UserID != user.ID {
		t.Errorf("Expected UserID '%s', got '%s'", user.ID, token.UserID)
	}
	if token.Username != user.Username {
		t.Errorf("Expected Username '%s', got '%s'", user.Username, token.Username)
	}
	if token.Value == "" {
		t.Error("Expected token value to be generated")
	}
}

func TestMockTokenService_ValidateToken(t *testing.T) {
	// Arrange
	tokenService := &MockTokenService{}

	// Act & Assert - Valid token
	claims, err := tokenService.ValidateToken("valid.token")
	if err != nil {
		t.Errorf("Expected no error for valid token, got %v", err)
	}
	if claims == nil {
		t.Fatal("Expected claims, got nil")
	}
	if claims.UserID != "test-user-id" {
		t.Errorf("Expected UserID 'test-user-id', got '%s'", claims.UserID)
	}

	// Act & Assert - Invalid token
	_, err = tokenService.ValidateToken("invalid.token")
	if err == nil {
		t.Error("Expected error for invalid token")
	}
}

func TestMockTokenService_GetPublicKey(t *testing.T) {
	// Arrange
	tokenService := &MockTokenService{}

	// Act
	publicKey, err := tokenService.GetPublicKey()

	// Assert
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if publicKey != "mock-public-key" {
		t.Errorf("Expected public key 'mock-public-key', got '%s'", publicKey)
	}
}
