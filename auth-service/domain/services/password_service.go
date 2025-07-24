package services

import (
	"golang.org/x/crypto/bcrypt"
)

// PasswordService define las operaciones para el manejo seguro de contraseñas
type PasswordService interface {
	// HashPassword encripta una contraseña usando bcrypt
	HashPassword(password string) (string, error)
	// ComparePassword compara una contraseña en texto plano con su hash
	ComparePassword(hashedPassword, password string) error
}

// DefaultPasswordService implementa PasswordService
type DefaultPasswordService struct{}

// NewDefaultPasswordService crea una nueva instancia de DefaultPasswordService
func NewDefaultPasswordService() *DefaultPasswordService {
	return &DefaultPasswordService{}
}

// HashPassword encripta una contraseña usando bcrypt con costo 12
func (s *DefaultPasswordService) HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), 12)
	if err != nil {
		return "", err
	}
	return string(bytes), nil
}

// ComparePassword compara una contraseña en texto plano con su hash
func (s *DefaultPasswordService) ComparePassword(hashedPassword, password string) error {
	return bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password))
} 