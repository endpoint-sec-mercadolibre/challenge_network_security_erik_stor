// Package main Auth Service API
//
// Servicio de autenticación que proporciona funcionalidades de login, validación de tokens y gestión de claves públicas.
//
//	Schemes: http, https
//	Host: localhost:8080
//	BasePath: /
//	Version: 1.0.0
//
//	Consumes:
//	- application/json
//
//	Produces:
//	- application/json
//	- application/x-pem-file
//
//	Security:
//	- bearer
//
// swagger:meta
package main

import (
	"log"
	"net/http"
	"os"

	"auth-service/entrypoints/api"
	"auth-service/infrastructure/di"
	"auth-service/infrastructure/logger"
	infraRepos "auth-service/infrastructure/repositories"

	_ "auth-service/docs" // Importar documentación generada por swag
)

// @title Auth Service API
// @version 1.0
// @description Servicio de autenticación que proporciona funcionalidades de login, validación de tokens y gestión de claves públicas.

// @host localhost:8080
// @BasePath /

// @securityDefinitions.apikey BearerAuth
// @in header
// @name Authorization
// @description Type "Bearer" followed by a space and JWT token.

func main() {
	// Inicializar logger
	loggerInstance := logger.GetInstance()
	defer loggerInstance.Close()

	// Establecer contexto inicial
	logger.SetContext(logger.Context{
		FunctionName: "main",
		Data: map[string]interface{}{
			"service": "auth-service",
		},
	})

	logger.Info("Iniciando servicio de autenticación")

	// Crear contenedor de dependencias
	container, err := di.NewContainer()
	if err != nil {
		logger.Error("Error inicializando contenedor de dependencias", err)
		log.Fatal("Error inicializando contenedor de dependencias:", err)
	}

	// Cerrar conexión de MongoDB al finalizar
	defer func() {
		if mongoRepo, ok := container.UserRepository.(*infraRepos.MongoDBUserRepository); ok {
			if err := mongoRepo.Close(); err != nil {
				logger.Error("Error cerrando conexión de MongoDB", err)
			} else {
				logger.Success("Conexión de MongoDB cerrada correctamente")
			}
		}
	}()

	logger.Success("Contenedor de dependencias inicializado correctamente")

	// Configurar rutas
	router := api.SetupRoutes(
		container.AuthController,
		container.TokenController,
		container.HealthController,
	)

	logger.Success("Rutas configuradas correctamente")

	// Obtener puerto del entorno
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	logger.Info("Servicio listo para recibir peticiones", map[string]interface{}{
		"port": port,
	})

	logger.Success("Servicio de autenticación iniciando en puerto " + port)
	log.Fatal(http.ListenAndServe(":"+port, router))
}
