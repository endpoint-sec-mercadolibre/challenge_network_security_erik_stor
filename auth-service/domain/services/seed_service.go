package services

import (
	"auth-service/domain/entities"
	"auth-service/domain/repositories"
	"auth-service/infrastructure/logger"
	"time"
)

// SeedService define las operaciones para inicializar datos en la base de datos
type SeedService interface {
	// SeedDefaultUser crea el usuario por defecto si no existe
	SeedDefaultUser() error
}

// DefaultSeedService implementa SeedService
type DefaultSeedService struct {
	userRepository  repositories.UserRepository
	passwordService PasswordService
}

// NewDefaultSeedService crea una nueva instancia de DefaultSeedService
func NewDefaultSeedService(userRepository repositories.UserRepository, passwordService PasswordService) *DefaultSeedService {
	return &DefaultSeedService{
		userRepository:  userRepository,
		passwordService: passwordService,
	}
}

// SeedDefaultUser crea el usuario por defecto si no existe
func (s *DefaultSeedService) SeedDefaultUser() error {
	// Establecer contexto para logging
	logger.SetContext(logger.Context{
		FunctionName: "DefaultSeedService.SeedDefaultUser",
		Data: map[string]interface{}{
			"username": "admin",
		},
	})

	logger.Info("Verificando si existe usuario por defecto")

	// Verificar si el usuario admin ya existe
	exists, err := s.userRepository.Exists("admin")
	if err != nil {
		logger.Error("Error verificando existencia de usuario admin", err)
		return err
	}

	if exists {
		logger.Info("Usuario admin ya existe, verificando si necesita actualización de contraseña")

		// Obtener el usuario existente
		existingUser, err := s.userRepository.FindByUsername("admin")
		if err != nil {
			logger.Error("Error obteniendo usuario admin existente", err)
			return err
		}

		// Verificar si la contraseña ya está encriptada (bcrypt genera hashes de ~60 caracteres)
		if len(existingUser.Password) < 50 {
			logger.Info("Usuario admin existe pero con contraseña sin encriptar, actualizando...")

			// Encriptar la contraseña por defecto (debe cumplir con las validaciones)
			hashedPassword, err := s.passwordService.HashPassword("Password123!")
			if err != nil {
				logger.Error("Error encriptando contraseña por defecto", err)
				return err
			}

			// Actualizar el usuario con la contraseña encriptada
			existingUser.Password = hashedPassword
			existingUser.UpdatedAt = time.Now()

			err = s.userRepository.Save(existingUser)
			if err != nil {
				logger.Error("Error actualizando usuario admin con contraseña encriptada", err)
				return err
			}

			logger.Success("Usuario admin actualizado exitosamente con contraseña encriptada")
		} else {
			logger.Info("Usuario admin ya existe con contraseña encriptada")
		}

		return nil
	}

	// Encriptar la contraseña por defecto (debe cumplir con las validaciones)
	hashedPassword, err := s.passwordService.HashPassword("Password123!")
	if err != nil {
		logger.Error("Error encriptando contraseña por defecto", err)
		return err
	}

	// Crear usuario por defecto con contraseña encriptada
	defaultUser := entities.NewUserWithHashedPassword("admin", hashedPassword)
	err = s.userRepository.Save(defaultUser)
	if err != nil {
		logger.Error("Error creando usuario admin", err)
		return err
	}

	logger.Success("Usuario admin creado exitosamente con contraseña encriptada")
	return nil
}
