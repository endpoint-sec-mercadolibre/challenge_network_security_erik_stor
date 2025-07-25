package services

import (
	"auth-service/domain/entities"
	"auth-service/domain/services"
	"testing"
)

// MockUserRepository para testing
type MockUserRepository struct {
	users map[string]*entities.User
}

func NewMockUserRepository() *MockUserRepository {
	return &MockUserRepository{
		users: make(map[string]*entities.User),
	}
}

func (m *MockUserRepository) Save(user *entities.User) error {
	m.users[user.Username] = user
	return nil
}

func (m *MockUserRepository) FindByUsername(username string) (*entities.User, error) {
	if user, exists := m.users[username]; exists {
		return user, nil
	}
	return nil, &MockError{message: "user not found"}
}

func (m *MockUserRepository) Exists(username string) (bool, error) {
	_, exists := m.users[username]
	return exists, nil
}

type MockError struct {
	message string
}

func (e *MockError) Error() string {
	return e.message
}

func TestNewDefaultSeedService(t *testing.T) {
	// Arrange
	mockRepo := NewMockUserRepository()
	passwordService := services.NewDefaultPasswordService()

	// Act
	seedService := services.NewDefaultSeedService(mockRepo, passwordService)

	// Assert
	if seedService == nil {
		t.Fatal("Expected SeedService instance, got nil")
	}
}

func TestDefaultSeedService_SeedDefaultUser_NewUser(t *testing.T) {
	// Arrange
	mockRepo := NewMockUserRepository()
	passwordService := services.NewDefaultPasswordService()
	seedService := services.NewDefaultSeedService(mockRepo, passwordService)

	// Act
	err := seedService.SeedDefaultUser()

	// Assert
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}

	// Verificar que el usuario fue creado
	user, err := mockRepo.FindByUsername("admin")
	if err != nil {
		t.Errorf("Expected admin user to exist, got error: %v", err)
	}

	if user.Username != "admin" {
		t.Errorf("Expected username 'admin', got '%s'", user.Username)
	}

	if len(user.Password) < 50 {
		t.Error("Expected admin user to have encrypted password")
	}
}

func TestDefaultSeedService_SeedDefaultUser_UserAlreadyExists(t *testing.T) {
	// Arrange
	mockRepo := NewMockUserRepository()
	passwordService := services.NewDefaultPasswordService()
	seedService := services.NewDefaultSeedService(mockRepo, passwordService)

	// Crear usuario admin existente
	existingUser := entities.NewUser("admin", "oldpassword")
	mockRepo.Save(existingUser)

	// Act
	err := seedService.SeedDefaultUser()

	// Assert
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}

	// Verificar que el usuario sigue existiendo
	user, err := mockRepo.FindByUsername("admin")
	if err != nil {
		t.Errorf("Expected admin user to still exist, got error: %v", err)
	}

	if user.Username != "admin" {
		t.Errorf("Expected username 'admin', got '%s'", user.Username)
	}
}

func TestDefaultSeedService_SeedDefaultUser_UpdateExistingUserWithPlainPassword(t *testing.T) {
	// Arrange
	mockRepo := NewMockUserRepository()
	passwordService := services.NewDefaultPasswordService()
	seedService := services.NewDefaultSeedService(mockRepo, passwordService)

	// Crear usuario admin con contraseña sin encriptar
	plainPasswordUser := entities.NewUser("admin", "password")
	mockRepo.Save(plainPasswordUser)

	// Act
	err := seedService.SeedDefaultUser()

	// Assert
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}

	// Verificar que el usuario tiene contraseña encriptada ahora
	user, err := mockRepo.FindByUsername("admin")
	if err != nil {
		t.Errorf("Error finding admin user: %v", err)
	}

	if len(user.Password) < 50 {
		t.Error("Expected admin user to have encrypted password after update")
	}

	// Verificar que la contraseña funciona
	if !user.ValidateCredentials("Password123!", passwordService) {
		t.Error("Expected password validation to work after encryption")
	}
}

func TestDefaultSeedService_SeedDefaultUser_UserAlreadyExistsWithEncryptedPassword(t *testing.T) {
	// Arrange
	mockRepo := NewMockUserRepository()
	passwordService := services.NewDefaultPasswordService()
	seedService := services.NewDefaultSeedService(mockRepo, passwordService)

	// Crear usuario admin con contraseña encriptada
	hashedPassword, _ := passwordService.HashPassword("Password123!")
	encryptedUser := entities.NewUserWithHashedPassword("admin", hashedPassword)
	mockRepo.Save(encryptedUser)

	// Act
	err := seedService.SeedDefaultUser()

	// Assert
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}

	// Verificar que el usuario sigue existiendo
	exists, err := mockRepo.Exists("admin")
	if err != nil {
		t.Errorf("Error checking if user exists: %v", err)
	}

	if !exists {
		t.Error("Expected admin user to still exist")
	}
}
