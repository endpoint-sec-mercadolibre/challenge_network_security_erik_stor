package services

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"log"
	"os"
	"time"

	"auth-service/domain/entities"
	"auth-service/domain/services"

	"github.com/golang-jwt/jwt/v5"
)

// JWTTokenService implementa TokenService usando JWT
type JWTTokenService struct {
	privateKey *rsa.PrivateKey
	publicKey  *rsa.PublicKey
}

// NewJWTTokenService crea una nueva instancia de JWTTokenService
func NewJWTTokenService() (*JWTTokenService, error) {
	privateKey, publicKey, err := generateOrLoadKeys()
	if err != nil {
		return nil, err
	}

	return &JWTTokenService{
		privateKey: privateKey,
		publicKey:  publicKey,
	}, nil
}

// GenerateToken genera un nuevo token para un usuario
func (s *JWTTokenService) GenerateToken(user *entities.User) (*entities.Token, error) {
	now := time.Now()
	expiresAt := now.Add(24 * time.Hour)

	claims := entities.TokenClaims{
		UserID:   user.ID,
		Username: user.Username,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(expiresAt),
			IssuedAt:  jwt.NewNumericDate(now),
			NotBefore: jwt.NewNumericDate(now),
			Issuer:    "auth-service",
			Subject:   user.ID,
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodRS256, claims)
	tokenString, err := token.SignedString(s.privateKey)
	if err != nil {
		return nil, err
	}

	return entities.NewToken(tokenString, user.ID, user.Username, expiresAt, now), nil
}

// ValidateToken valida un token y retorna los claims
func (s *JWTTokenService) ValidateToken(tokenString string) (*entities.TokenClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &entities.TokenClaims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
			return nil, fmt.Errorf("método de firma inesperado: %v", token.Header["alg"])
		}
		return s.publicKey, nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(*entities.TokenClaims); ok && token.Valid {
		return claims, nil
	}

	return nil, fmt.Errorf("token inválido")
}

// GetPublicKey retorna la llave pública para validación
func (s *JWTTokenService) GetPublicKey() (string, error) {
	publicKeyBytes, err := x509.MarshalPKIXPublicKey(s.publicKey)
	if err != nil {
		return "", err
	}
	
	publicKeyPEM := pem.EncodeToMemory(&pem.Block{
		Type:  "PUBLIC KEY",
		Bytes: publicKeyBytes,
	})
	
	return string(publicKeyPEM), nil
}

// generateOrLoadKeys genera o carga las llaves RSA
func generateOrLoadKeys() (*rsa.PrivateKey, *rsa.PublicKey, error) {
	// Intentar cargar llaves existentes
	privateKeyBytes, err := os.ReadFile("private.pem")
	if err == nil {
		publicKeyBytes, err := os.ReadFile("public.pem")
		if err == nil {
			// Decodificar llave privada
			block, _ := pem.Decode(privateKeyBytes)
			privateKey, err := x509.ParsePKCS1PrivateKey(block.Bytes)
			if err != nil {
				return nil, nil, err
			}

			// Decodificar llave pública
			block, _ = pem.Decode(publicKeyBytes)
			publicKey, err := x509.ParsePKIXPublicKey(block.Bytes)
			if err != nil {
				return nil, nil, err
			}

			return privateKey, publicKey.(*rsa.PublicKey), nil
		}
	}

	// Generar nuevas llaves
	log.Println("Generando nuevas llaves RSA...")
	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		return nil, nil, err
	}

	publicKey := &privateKey.PublicKey

	// Guardar llave privada
	privateKeyPEM := &pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: x509.MarshalPKCS1PrivateKey(privateKey),
	}
	err = os.WriteFile("private.pem", pem.EncodeToMemory(privateKeyPEM), 0600)
	if err != nil {
		return nil, nil, err
	}

	// Guardar llave pública
	publicKeyBytes, err := x509.MarshalPKIXPublicKey(publicKey)
	if err != nil {
		return nil, nil, err
	}
	publicKeyPEM := &pem.Block{
		Type:  "PUBLIC KEY",
		Bytes: publicKeyBytes,
	}
	err = os.WriteFile("public.pem", pem.EncodeToMemory(publicKeyPEM), 0644)
	if err != nil {
		return nil, nil, err
	}

	log.Println("Llaves RSA generadas y guardadas")
	return privateKey, publicKey, nil
}

// Ensure JWTTokenService implementa TokenService
var _ services.TokenService = (*JWTTokenService)(nil) 