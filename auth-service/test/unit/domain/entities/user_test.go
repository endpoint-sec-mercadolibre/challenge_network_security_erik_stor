package entities

import (
	"auth-service/domain/entities"
	"testing"
	"time"
)

// MockPasswordService para evitar ciclos de importación
type MockPasswordService struct{}

func (m *MockPasswordService) HashPassword(password string) (string, error) {
	return "$2a$12$mockhash", nil
}

func (m *MockPasswordService) ComparePassword(hashedPassword, password string) error {
	if password == "password123" {
		return nil
	}
	return &MockError{message: "password incorrecto"}
}

type MockError struct {
	message string
}

func (e *MockError) Error() string {
	return e.message
}

func TestNewUser(t *testing.T) {
	// Arrange & Act
	user := entities.NewUser("testuser", "password123")

	// Assert
	if user.Username != "testuser" {
		t.Errorf("Expected username 'testuser', got '%s'", user.Username)
	}
	if user.Password != "password123" {
		t.Errorf("Expected password 'password123', got '%s'", user.Password)
	}
	if user.ID == "" {
		t.Error("Expected user ID to be generated")
	}
	if user.CreatedAt.IsZero() {
		t.Error("Expected CreatedAt to be set")
	}
	if user.UpdatedAt.IsZero() {
		t.Error("Expected UpdatedAt to be set")
	}
}

func TestNewUserWithHashedPassword(t *testing.T) {
	// Arrange
	hashedPassword := "$2a$12$hashedpassword"

	// Act
	user := entities.NewUserWithHashedPassword("testuser", hashedPassword)

	// Assert
	if user.Username != "testuser" {
		t.Errorf("Expected username 'testuser', got '%s'", user.Username)
	}
	if user.Password != hashedPassword {
		t.Errorf("Expected hashed password, got '%s'", user.Password)
	}
	if user.ID == "" {
		t.Error("Expected user ID to be generated")
	}
	if user.CreatedAt.IsZero() {
		t.Error("Expected CreatedAt to be set")
	}
	if user.UpdatedAt.IsZero() {
		t.Error("Expected UpdatedAt to be set")
	}
}

func TestValidateCredentials(t *testing.T) {
	// Arrange
	passwordService := &MockPasswordService{}
	user := entities.NewUserWithHashedPassword("testuser", "$2a$12$mockhash")

	// Act & Assert - Valid credentials
	if !user.ValidateCredentials("password123", passwordService) {
		t.Error("Expected valid credentials to pass validation")
	}

	// Act & Assert - Invalid credentials
	if user.ValidateCredentials("wrongpassword", passwordService) {
		t.Error("Expected invalid credentials to fail validation")
	}
}

func TestUserTimestamps(t *testing.T) {
	// Arrange
	user := entities.NewUser("testuser", "password123")
	originalCreatedAt := user.CreatedAt
	originalUpdatedAt := user.UpdatedAt

	// Act - Simulate some time passing
	time.Sleep(1 * time.Millisecond)
	user.UpdatedAt = time.Now()

	// Assert
	if user.CreatedAt != originalCreatedAt {
		t.Error("Expected CreatedAt to remain unchanged")
	}
	if user.UpdatedAt == originalUpdatedAt {
		t.Error("Expected UpdatedAt to be updated")
	}
}
