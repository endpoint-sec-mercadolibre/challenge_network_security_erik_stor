package api

import (
	"auth-service/middlewares"

	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

// SetupRoutes configura las rutas de la aplicación
func SetupRoutes(
	authController *AuthController,
	tokenController *TokenController,
	healthController *HealthController,
) *gin.Engine {
	router := gin.Default()

	// Aplicar middleware de logging primero
	router.Use(middlewares.LoggingMiddleware())

	// Aplicar middleware CORS
	router.Use(middlewares.CORSMiddleware())

	// Ruta de documentación Swagger
	router.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// Rutas de autenticación
	router.POST("/login", authController.Login)
	router.POST("/validate", authController.ValidateToken)

	// Rutas de tokens
	router.GET("/public-key", tokenController.GetPublicKey)

	// Rutas de health
	router.GET("/health", healthController.Health)

	return router
}
