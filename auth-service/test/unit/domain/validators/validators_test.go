package validators

import (
	"testing"
)

// TestStruct para probar las validaciones
type TestStruct struct {
	Username string `validate:"username"`
	Password string `validate:"password"`
	Token    string `validate:"jwt_token"`
	Field    string `validate:"not_empty_string"`
}

// TestStructUsername para probar solo validación de username
type TestStructUsername struct {
	Username string `validate:"username"`
}

// TestStructPassword para probar solo validación de password
type TestStructPassword struct {
	Password string `validate:"password"`
}

// TestStructToken para probar solo validación de token
type TestStructToken struct {
	Token string `validate:"jwt_token"`
}

// TestStructField para probar solo validación de campo
type TestStructField struct {
	Field string `validate:"not_empty_string"`
}

func TestCustomValidator_ValidateUsername(t *testing.T) {
	tests := []struct {
		name     string
		username string
		want     bool
	}{
		{"username válido", "testuser", true},
		{"username con guión", "test-user", true},
		{"username con guión bajo", "test_user", true},
		{"username con números", "testuser123", true},
		{"username muy corto", "ab", false},
		{"username muy largo", "thisusernameiswaytoolongandshouldfailvalidationbecauseitisover50characters", false},
		{"username con espacios", "test user", false},
		{"username con caracteres especiales", "test@user", false},
		{"username vacío", "", false},
	}

	validator := NewCustomValidator()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			testStruct := TestStructUsername{Username: tt.username}
			err := validator.Validate(testStruct)

			if tt.want && err != nil {
				t.Errorf("Expected validation to pass, got error: %v", err)
			}
			if !tt.want && err == nil {
				t.Errorf("Expected validation to fail, but it passed")
			}
		})
	}
}

func TestCustomValidator_ValidatePassword(t *testing.T) {
	tests := []struct {
		name     string
		password string
		want     bool
	}{
		{"password válido", "Password123!", true},
		{"password sin mayúscula", "password123!", false},
		{"password sin minúscula", "PASSWORD123!", false},
		{"password sin número", "Password!", false},
		{"password sin carácter especial", "Password123", false},
		{"password muy corto", "Pass1!", false},
		{"password vacío", "", false},
	}

	validator := NewCustomValidator()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			testStruct := TestStructPassword{Password: tt.password}
			err := validator.Validate(testStruct)

			if tt.want && err != nil {
				t.Errorf("Expected validation to pass, got error: %v", err)
			}
			if !tt.want && err == nil {
				t.Errorf("Expected validation to fail, but it passed")
			}
		})
	}
}

func TestCustomValidator_ValidateJWTToken(t *testing.T) {
	tests := []struct {
		name  string
		token string
		want  bool
	}{
		{"token JWT válido", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c", true},
		{"token con solo 2 partes", "part1.part2", false},
		{"token con 4 partes", "part1.part2.part3.part4", false},
		{"token con parte vacía", "part1..part3", false},
		{"token vacío", "", false},
	}

	validator := NewCustomValidator()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			testStruct := TestStructToken{Token: tt.token}
			err := validator.Validate(testStruct)

			if tt.want && err != nil {
				t.Errorf("Expected validation to pass, got error: %v", err)
			}
			if !tt.want && err == nil {
				t.Errorf("Expected validation to fail, but it passed")
			}
		})
	}
}

func TestCustomValidator_ValidateNotEmptyString(t *testing.T) {
	tests := []struct {
		name  string
		value string
		want  bool
	}{
		{"string válido", "test", true},
		{"string con espacios", " test ", true},
		{"string vacío", "", false},
		{"solo espacios", "   ", false},
		{"solo tabs", "\t\t\t", false},
	}

	validator := NewCustomValidator()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			testStruct := TestStructField{Field: tt.value}
			err := validator.Validate(testStruct)

			if tt.want && err != nil {
				t.Errorf("Expected validation to pass, got error: %v", err)
			}
			if !tt.want && err == nil {
				t.Errorf("Expected validation to fail, but it passed")
			}
		})
	}
}

func TestGetValidationErrors(t *testing.T) {
	validator := NewCustomValidator()

	// Test con errores de validación
	testStruct := TestStruct{
		Username: "ab",      // muy corto
		Password: "pass",    // muy corto
		Token:    "invalid", // no es JWT
		Field:    "",        // vacío
	}

	err := validator.Validate(testStruct)
	if err == nil {
		t.Fatal("Expected validation to fail")
	}

	errors := GetValidationErrors(err)
	if len(errors) == 0 {
		t.Error("Expected validation errors, got none")
	}

	// Verificar que tenemos errores para los campos esperados
	expectedFields := []string{"Username", "Password", "Token", "Field"}
	for _, field := range expectedFields {
		if _, exists := errors[field]; !exists {
			t.Errorf("Expected error for field %s", field)
		}
	}
}

func TestNewCustomValidator(t *testing.T) {
	validator := NewCustomValidator()
	if validator == nil {
		t.Fatal("Expected validator instance, got nil")
	}
	if validator.validator == nil {
		t.Fatal("Expected internal validator, got nil")
	}
}
