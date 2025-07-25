package middlewares

import (
	"auth-service/domain/validators"
	"auth-service/infrastructure/logger"
	"net/http"
	"reflect"

	"github.com/gin-gonic/gin"
)

// ValidationMiddleware es un middleware que valida los datos de entrada
type ValidationMiddleware struct {
	validator *validators.CustomValidator
}

// NewValidationMiddleware crea una nueva instancia del middleware de validación
func NewValidationMiddleware() *ValidationMiddleware {
	return &ValidationMiddleware{
		validator: validators.NewCustomValidator(),
	}
}

// ValidateRequest es un middleware que valida automáticamente las estructuras de request
func (vm *ValidationMiddleware) ValidateRequest(requestType interface{}) gin.HandlerFunc {
	return func(c *gin.Context) {
		// No establecer contexto aquí para evitar conflictos con el middleware de logging
		logger.Info("Iniciando validación de datos de entrada")

		// Crear una nueva instancia del tipo de request usando reflexión
		requestTypeValue := reflect.ValueOf(requestType)
		if requestTypeValue.Kind() == reflect.Ptr {
			requestTypeValue = requestTypeValue.Elem()
		}
		request := reflect.New(requestTypeValue.Type()).Interface()

		// Parsear el JSON del body
		if err := c.ShouldBindJSON(&request); err != nil {
			logger.Error("Error al parsear JSON", err)
			c.JSON(http.StatusBadRequest, gin.H{
				"error":   "Formato JSON inválido",
				"details": err.Error(),
			})
			c.Abort()
			return
		}

		// Validar la estructura
		if err := vm.validator.Validate(request); err != nil {
			logger.Error("Error de validación", err)

			c.JSON(http.StatusBadRequest, gin.H{
				"error": "Credenciales inválidas",
			})
			c.Abort()
			return
		}

		// Guardar la request validada en el contexto para uso posterior
		c.Set("validated_request", request)

		logger.Success("Validación de datos completada exitosamente")

		c.Next()
	}
}

// ValidateQueryParams valida los parámetros de query
func (vm *ValidationMiddleware) ValidateQueryParams(requiredParams []string) gin.HandlerFunc {
	return func(c *gin.Context) {
		logger.Info("Validando parámetros de query")

		missingParams := []string{}
		for _, param := range requiredParams {
			if c.Query(param) == "" {
				missingParams = append(missingParams, param)
			}
		}

		if len(missingParams) > 0 {
			logger.Error("Parámetros de query faltantes", nil)
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "Parámetros de query requeridos",
				"details": map[string]interface{}{
					"missing_params": missingParams,
				},
			})
			c.Abort()
			return
		}

		logger.Success("Validación de parámetros de query completada")
		c.Next()
	}
}

// ValidateHeaders valida los headers requeridos
func (vm *ValidationMiddleware) ValidateHeaders(requiredHeaders []string) gin.HandlerFunc {
	return func(c *gin.Context) {
		logger.Info("Validando headers requeridos")

		missingHeaders := []string{}
		for _, header := range requiredHeaders {
			if c.GetHeader(header) == "" {
				missingHeaders = append(missingHeaders, header)
			}
		}

		if len(missingHeaders) > 0 {
			logger.Error("Headers requeridos faltantes", nil)
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "Headers requeridos",
				"details": map[string]interface{}{
					"missing_headers": missingHeaders,
				},
			})
			c.Abort()
			return
		}

		logger.Success("Validación de headers completada")
		c.Next()
	}
}
