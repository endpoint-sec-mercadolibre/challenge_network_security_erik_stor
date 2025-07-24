package entities

import (
	"testing"
	"time"
)

func TestNewToken(t *testing.T) {
	// Arrange
	value := "jwt.token.value"
	userID := "test-user-id"
	username := "testuser"
	expiresAt := time.Now().Add(1 * time.Hour)
	issuedAt := time.Now()

	// Act
	token := NewToken(value, userID, username, expiresAt, issuedAt)

	// Assert
	if token.Value != value {
		t.Errorf("Expected Value '%s', got '%s'", value, token.Value)
	}
	if token.UserID != userID {
		t.Errorf("Expected UserID '%s', got '%s'", userID, token.UserID)
	}
	if token.Username != username {
		t.Errorf("Expected Username '%s', got '%s'", username, token.Username)
	}
	if token.ExpiresAt != expiresAt {
		t.Errorf("Expected ExpiresAt, got different time")
	}
	if token.IssuedAt != issuedAt {
		t.Errorf("Expected IssuedAt, got different time")
	}
}

func TestToken_IsExpired_NotExpired(t *testing.T) {
	// Arrange
	expiresAt := time.Now().Add(1 * time.Hour)
	token := NewToken("jwt.token.value", "test-user-id", "testuser", expiresAt, time.Now())

	// Act
	isExpired := token.IsExpired()

	// Assert
	if isExpired {
		t.Error("Expected token to not be expired")
	}
}

func TestToken_IsExpired_Expired(t *testing.T) {
	// Arrange
	expiresAt := time.Now().Add(-1 * time.Hour)
	token := NewToken("jwt.token.value", "test-user-id", "testuser", expiresAt, time.Now())

	// Act
	isExpired := token.IsExpired()

	// Assert
	if !isExpired {
		t.Error("Expected token to be expired")
	}
}

func TestToken_IsExpired_JustExpired(t *testing.T) {
	// Arrange
	expiresAt := time.Now().Add(-1 * time.Millisecond) // Un milisegundo en el pasado
	token := NewToken("jwt.token.value", "test-user-id", "testuser", expiresAt, time.Now())

	// Act
	isExpired := token.IsExpired()

	// Assert
	if !isExpired {
		t.Error("Expected token to be expired when expiration time is in the past")
	}
}
