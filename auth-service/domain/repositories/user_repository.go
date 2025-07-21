package repositories

import "auth-service/domain/entities"

// UserRepository define las operaciones que debe implementar un repositorio de usuarios
type UserRepository interface {
	// FindByUsername busca un usuario por su nombre de usuario
	FindByUsername(username string) (*entities.User, error)
	
	// Save guarda un usuario en el repositorio
	Save(user *entities.User) error
	
	// Exists verifica si existe un usuario con el username dado
	Exists(username string) (bool, error)
} 