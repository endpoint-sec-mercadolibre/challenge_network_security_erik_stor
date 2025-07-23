package middlewares

import (
	"github.com/gin-gonic/gin"
	"github.com/rs/cors"
)

// CORSMiddleware configura CORS para la aplicación
func CORSMiddleware() gin.HandlerFunc {
	config := cors.New(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowedMethods:   []string{"GET", "POST"},
		AllowedHeaders:   []string{"*"},
		AllowCredentials: true,
	})

	return func(c *gin.Context) {
		config.HandlerFunc(c.Writer, c.Request)
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	}
} 