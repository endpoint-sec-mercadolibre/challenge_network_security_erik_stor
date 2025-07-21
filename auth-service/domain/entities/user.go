package entities

import (
	"time"

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

// ValidateCredentials valida las credenciales del usuario
func (u *User) ValidateCredentials(password string) bool {
	return u.Password == password
}
