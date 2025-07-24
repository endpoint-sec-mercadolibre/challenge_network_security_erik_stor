package entities

import (
	"time"

	"auth-service/infrastructure/logger"

	"github.com/google/uuid"
)

// User representa la entidad de usuario en el dominio
type User struct {
	ID        string    `json:"id"`
	Username  string    `json:"username"`
	Password  string    `json:"-"` // No se serializa en JSON
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// NewUser crea una nueva instancia de User
func NewUser(username, password string) *User {
	now := time.Now()
	return &User{
		ID:        uuid.New().String(),
		Username:  username,
		Password:  password,
		CreatedAt: now,
		UpdatedAt: now,
	}
}

// NewUserWithHashedPassword crea una nueva instancia de User con contraseña encriptada
func NewUserWithHashedPassword(username, hashedPassword string) *User {
	now := time.Now()
	return &User{
		ID:        uuid.New().String(),
		Username:  username,
		Password:  hashedPassword,
		CreatedAt: now,
		UpdatedAt: now,
	}
}

// ValidateCredentials valida las credenciales del usuario usando bcrypt
func (u *User) ValidateCredentials(password string, passwordService interface {
	ComparePassword(hashedPassword, password string) error
}) bool {
	// Agregar logging de debug
	logger.Info("Validando credenciales", map[string]interface{}{
		"username":                u.Username,
		"password_length":         len(password),
		"hashed_password_length":  len(u.Password),
		"hashed_password_preview": u.Password[:10] + "...",
	})

	err := passwordService.ComparePassword(u.Password, password)

	if err != nil {
		logger.Error("Error comparando contraseñas", err)
	} else {
		logger.Success("Contraseñas coinciden correctamente")
	}

	return err == nil
}
