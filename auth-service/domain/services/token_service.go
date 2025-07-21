package services

import "auth-service/domain/entities"

// TokenService define las operaciones que debe implementar un servicio de tokens
type TokenService interface {
	// GenerateToken genera un nuevo token para un usuario
	GenerateToken(user *entities.User) (*entities.Token, error)
	
	// ValidateToken valida un token y retorna los claims
	ValidateToken(tokenString string) (*entities.TokenClaims, error)
	
	// GetPublicKey retorna la llave pública para validación
	GetPublicKey() (string, error)
} 