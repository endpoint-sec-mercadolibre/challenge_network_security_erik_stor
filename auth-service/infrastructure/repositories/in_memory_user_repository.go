package repositories

import (
	"auth-service/domain/entities"
	"auth-service/domain/repositories"
	"errors"
	"sync"
)

// InMemoryUserRepository implementa UserRepository usando memoria
type InMemoryUserRepository struct {
	users map[string]*entities.User
	mutex sync.RWMutex
}

// NewInMemoryUserRepository crea una nueva instancia de InMemoryUserRepository
func NewInMemoryUserRepository() *InMemoryUserRepository {
	repo := &InMemoryUserRepository{
		users: make(map[string]*entities.User),
	}
	
	// Agregar usuario por defecto para pruebas
	defaultUser := entities.NewUser("admin", "password")
	repo.users[defaultUser.Username] = defaultUser
	
	return repo
}

// FindByUsername busca un usuario por su nombre de usuario
func (r *InMemoryUserRepository) FindByUsername(username string) (*entities.User, error) {
	r.mutex.RLock()
	defer r.mutex.RUnlock()
	
	user, exists := r.users[username]
	if !exists {
		return nil, errors.New("usuario no encontrado")
	}
	
	return user, nil
}

// Save guarda un usuario en el repositorio
func (r *InMemoryUserRepository) Save(user *entities.User) error {
	r.mutex.Lock()
	defer r.mutex.Unlock()
	
	r.users[user.Username] = user
	return nil
}

// Exists verifica si existe un usuario con el username dado
func (r *InMemoryUserRepository) Exists(username string) (bool, error) {
	r.mutex.RLock()
	defer r.mutex.RUnlock()
	
	_, exists := r.users[username]
	return exists, nil
}

// Ensure InMemoryUserRepository implementa UserRepository
var _ repositories.UserRepository = (*InMemoryUserRepository)(nil) 