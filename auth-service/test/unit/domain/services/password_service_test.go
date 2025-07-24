package services

import (
	"strings"
	"testing"
)

func TestDefaultPasswordService_HashPassword(t *testing.T) {
	// Arrange
	passwordService := NewDefaultPasswordService()
	password := "Password123!"

	// Act
	hashedPassword, err := passwordService.HashPassword(password)

	// Assert
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if len(hashedPassword) < 50 {
		t.Error("Expected hashed password to be at least 50 characters long")
	}
	if !strings.HasPrefix(hashedPassword, "$2a$") {
		t.Error("Expected hashed password to start with $2a$")
	}
}

func TestDefaultPasswordService_HashPassword_EmptyPassword(t *testing.T) {
	// Arrange
	passwordService := NewDefaultPasswordService()
	password := ""

	// Act
	hashedPassword, err := passwordService.HashPassword(password)

	// Assert
	if err != nil {
		t.Errorf("Expected no error for empty password, got %v", err)
	}
	if len(hashedPassword) < 50 {
		t.Error("Expected hashed password to be at least 50 characters long")
	}
}

func TestDefaultPasswordService_HashPassword_LongPassword(t *testing.T) {
	// Arrange
	passwordService := NewDefaultPasswordService()
	password := strings.Repeat("a", 50) // Contraseña de 50 caracteres (dentro del límite de bcrypt)

	// Act
	hashedPassword, err := passwordService.HashPassword(password)

	// Assert
	if err != nil {
		t.Errorf("Expected no error for long password, got %v", err)
	}
	if len(hashedPassword) < 50 {
		t.Error("Expected hashed password to be at least 50 characters long")
	}
}

func TestDefaultPasswordService_HashPassword_TooLongPassword(t *testing.T) {
	// Arrange
	passwordService := NewDefaultPasswordService()
	password := strings.Repeat("a", 1000) // Password muy largo

	// Act
	_, err := passwordService.HashPassword(password)

	// Assert
	if err == nil {
		t.Error("Expected error for too long password")
	}
}

func TestDefaultPasswordService_ComparePassword(t *testing.T) {
	// Arrange
	passwordService := NewDefaultPasswordService()
	password := "Password123!"
	hashedPassword, _ := passwordService.HashPassword(password)

	// Act & Assert - Valid password
	err := passwordService.ComparePassword(hashedPassword, password)
	if err != nil {
		t.Errorf("Expected no error for valid password, got %v", err)
	}

	// Act & Assert - Invalid password
	err = passwordService.ComparePassword(hashedPassword, "WrongPassword")
	if err == nil {
		t.Error("Expected error for invalid password")
	}
}

func TestDefaultPasswordService_ConsistentHashing(t *testing.T) {
	// Arrange
	passwordService := NewDefaultPasswordService()
	password := "Password123!"

	// Act
	hash1, err1 := passwordService.HashPassword(password)
	hash2, err2 := passwordService.HashPassword(password)

	// Assert
	if err1 != nil || err2 != nil {
		t.Errorf("Expected no errors, got %v and %v", err1, err2)
	}

	// Los hashes deben ser diferentes (bcrypt usa salt)
	if hash1 == hash2 {
		t.Error("Expected different hashes for same password (due to salt)")
	}

	// Pero ambos deben validar correctamente
	err1 = passwordService.ComparePassword(hash1, password)
	err2 = passwordService.ComparePassword(hash2, password)
	if err1 != nil || err2 != nil {
		t.Errorf("Expected both hashes to validate correctly, got errors: %v and %v", err1, err2)
	}
}
