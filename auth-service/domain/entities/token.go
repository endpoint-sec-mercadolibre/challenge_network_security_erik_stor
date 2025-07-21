package entities

import (
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// TokenClaims representa los claims del token JWT
type TokenClaims struct {
	UserID   string `json:"user_id"`
	Username string `json:"username"`
	jwt.RegisteredClaims
}

// Token representa un token de autenticación
type Token struct {
	Value     string    `json:"token"`
	UserID    string    `json:"user_id"`
	Username  string    `json:"username"`
	ExpiresAt time.Time `json:"expires_at"`
	IssuedAt  time.Time `json:"issued_at"`
}

// NewToken crea una nueva instancia de Token
func NewToken(value, userID, username string, expiresAt, issuedAt time.Time) *Token {
	return &Token{
		Value:     value,
		UserID:    userID,
		Username:  username,
		ExpiresAt: expiresAt,
		IssuedAt:  issuedAt,
	}
}

// IsExpired verifica si el token ha expirado
func (t *Token) IsExpired() bool {
	return time.Now().After(t.ExpiresAt)
}
