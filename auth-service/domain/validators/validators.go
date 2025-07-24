package validators

import (
	"fmt"
	"regexp"
	"strings"

	"github.com/go-playground/validator/v10"
)

// CustomValidator contiene las validaciones personalizadas
type CustomValidator struct {
	validator *validator.Validate
}

// NewCustomValidator crea una nueva instancia del validador personalizado
func NewCustomValidator() *CustomValidator {
	v := validator.New()

	// Registrar validaciones personalizadas
	if err := v.RegisterValidation("username", validateUsername); err != nil {
		panic(fmt.Sprintf("Error registrando validación username: %v", err))
	}
	if err := v.RegisterValidation("password", validatePassword); err != nil {
		panic(fmt.Sprintf("Error registrando validación password: %v", err))
	}
	if err := v.RegisterValidation("jwt_token", validateJWTToken); err != nil {
		panic(fmt.Sprintf("Error registrando validación jwt_token: %v", err))
	}
	if err := v.RegisterValidation("not_empty_string", validateNotEmptyString); err != nil {
		panic(fmt.Sprintf("Error registrando validación not_empty_string: %v", err))
	}

	return &CustomValidator{
		validator: v,
	}
}

// Validate valida una estructura usando las reglas definidas
func (cv *CustomValidator) Validate(i interface{}) error {
	return cv.validator.Struct(i)
}

// validateUsername valida el formato del nombre de usuario
func validateUsername(fl validator.FieldLevel) bool {
	username := fl.Field().String()

	// Debe tener entre 3 y 50 caracteres
	if len(username) < 3 || len(username) > 50 {
		return false
	}

	// Solo puede contener letras, números, guiones y guiones bajos
	usernameRegex := regexp.MustCompile(`^[a-zA-Z0-9_-]+$`)
	return usernameRegex.MatchString(username)
}

// validatePassword valida el formato de la contraseña
func validatePassword(fl validator.FieldLevel) bool {
	password := fl.Field().String()

	// Debe tener al menos 8 caracteres
	if len(password) < 8 {
		return false
	}

	// Debe tener al menos una letra mayúscula
	hasUpper := regexp.MustCompile(`[A-Z]`).MatchString(password)
	if !hasUpper {
		return false
	}

	// Debe tener al menos una letra minúscula
	hasLower := regexp.MustCompile(`[a-z]`).MatchString(password)
	if !hasLower {
		return false
	}

	// Debe tener al menos un número
	hasNumber := regexp.MustCompile(`[0-9]`).MatchString(password)
	if !hasNumber {
		return false
	}

	// Debe tener al menos un carácter especial
	hasSpecial := regexp.MustCompile(`[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]`).MatchString(password)
	if !hasSpecial {
		return false
	}

	return true
}

// validateJWTToken valida el formato básico de un token JWT
func validateJWTToken(fl validator.FieldLevel) bool {
	token := fl.Field().String()

	// Un token JWT debe tener 3 partes separadas por puntos
	parts := strings.Split(token, ".")
	if len(parts) != 3 {
		return false
	}

	// Cada parte debe tener contenido
	for _, part := range parts {
		if len(strings.TrimSpace(part)) == 0 {
			return false
		}
	}

	return true
}

// validateNotEmptyString valida que el string no esté vacío después de trim
func validateNotEmptyString(fl validator.FieldLevel) bool {
	value := strings.TrimSpace(fl.Field().String())
	return len(value) > 0
}

// GetValidationErrors traduce los errores de validación a mensajes en español
func GetValidationErrors(err error) map[string]string {
	errors := make(map[string]string)

	if validationErrors, ok := err.(validator.ValidationErrors); ok {
		for _, e := range validationErrors {
			field := e.Field()
			tag := e.Tag()
			param := e.Param()

			message := getErrorMessage(field, tag, param)
			errors[field] = message
		}
	}

	return errors
}

// getErrorMessage devuelve el mensaje de error en español para cada tipo de validación
func getErrorMessage(field, tag, param string) string {
	switch tag {
	case "required":
		return fmt.Sprintf("El campo %s es obligatorio", field)
	case "username":
		return fmt.Sprintf("El campo %s debe tener entre 3 y 50 caracteres y solo puede contener letras, números, guiones y guiones bajos", field)
	case "password":
		return fmt.Sprintf("El campo %s debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales", field)
	case "jwt_token":
		return fmt.Sprintf("El campo %s debe ser un token JWT válido", field)
	case "not_empty_string":
		return fmt.Sprintf("El campo %s no puede estar vacío", field)
	case "min":
		return fmt.Sprintf("El campo %s debe tener al menos %s caracteres", field, param)
	case "max":
		return fmt.Sprintf("El campo %s debe tener máximo %s caracteres", field, param)
	case "email":
		return fmt.Sprintf("El campo %s debe ser un email válido", field)
	default:
		return fmt.Sprintf("El campo %s no cumple con la validación requerida", field)
	}
}
