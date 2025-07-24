package repositories

import (
	"auth-service/domain/entities"
	"auth-service/domain/repositories"
	"auth-service/infrastructure/logger"
	"context"
	"errors"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// MongoDBUserRepository implementa UserRepository usando MongoDB
type MongoDBUserRepository struct {
	client     *mongo.Client
	database   *mongo.Database
	collection *mongo.Collection
}

// UserDocument representa el documento de usuario en MongoDB
type UserDocument struct {
	ID        primitive.ObjectID `bson:"_id,omitempty"`
	Username  string             `bson:"username"`
	Password  string             `bson:"password"`
	CreatedAt time.Time          `bson:"created_at"`
	UpdatedAt time.Time          `bson:"updated_at"`
}

// NewMongoDBUserRepository crea una nueva instancia de MongoDBUserRepository
func NewMongoDBUserRepository(mongoURI, databaseName string) (*MongoDBUserRepository, error) {
	// Establecer contexto para logging
	logger.SetContext(logger.Context{
		FunctionName: "NewMongoDBUserRepository",
		Data: map[string]interface{}{
			"mongoURI":     mongoURI,
			"databaseName": databaseName,
		},
	})

	logger.Info("Conectando a MongoDB")

	// Conectar a MongoDB
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		logger.Error("Error conectando a MongoDB", err)
		return nil, err
	}

	// Verificar conexión
	err = client.Ping(ctx, nil)
	if err != nil {
		logger.Error("Error verificando conexión a MongoDB", err)
		return nil, err
	}

	database := client.Database(databaseName)
	collection := database.Collection("users")

	// Crear índice único en username
	indexModel := mongo.IndexModel{
		Keys:    bson.D{{Key: "username", Value: 1}},
		Options: options.Index().SetUnique(true),
	}

	_, err = collection.Indexes().CreateOne(ctx, indexModel)
	if err != nil {
		logger.Error("Error creando índice en MongoDB", err)
		return nil, err
	}

	logger.Success("Conexión a MongoDB establecida correctamente")

	return &MongoDBUserRepository{
		client:     client,
		database:   database,
		collection: collection,
	}, nil
}

// Close cierra la conexión a MongoDB
func (r *MongoDBUserRepository) Close() error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	return r.client.Disconnect(ctx)
}

// FindByUsername busca un usuario por su nombre de usuario
func (r *MongoDBUserRepository) FindByUsername(username string) (*entities.User, error) {
	// Establecer contexto para logging
	logger.SetContext(logger.Context{
		FunctionName: "MongoDBUserRepository.FindByUsername",
		Data: map[string]interface{}{
			"username": username,
		},
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var userDoc UserDocument
	err := r.collection.FindOne(ctx, bson.M{"username": username}).Decode(&userDoc)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			logger.Info("Usuario no encontrado en MongoDB")
			return nil, errors.New("usuario no encontrado")
		}
		logger.Error("Error buscando usuario en MongoDB", err)
		return nil, err
	}

	user := &entities.User{
		ID:        userDoc.ID.Hex(),
		Username:  userDoc.Username,
		Password:  userDoc.Password,
		CreatedAt: userDoc.CreatedAt,
		UpdatedAt: userDoc.UpdatedAt,
	}

	logger.Success("Usuario encontrado en MongoDB")
	return user, nil
}

// Save guarda un usuario en el repositorio
func (r *MongoDBUserRepository) Save(user *entities.User) error {
	// Establecer contexto para logging
	logger.SetContext(logger.Context{
		FunctionName: "MongoDBUserRepository.Save",
		Data: map[string]interface{}{
			"username": user.Username,
		},
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Verificar si el usuario ya existe
	existingUser, err := r.FindByUsername(user.Username)
	if err == nil && existingUser != nil {
		// Usuario existe, actualizar
		objectID, err := primitive.ObjectIDFromHex(existingUser.ID)
		if err != nil {
			logger.Error("Error convirtiendo ID a ObjectID", err)
			return err
		}

		userDoc := UserDocument{
			ID:        objectID,
			Username:  user.Username,
			Password:  user.Password,
			CreatedAt: existingUser.CreatedAt,
			UpdatedAt: time.Now(),
		}

		_, err = r.collection.ReplaceOne(ctx, bson.M{"_id": objectID}, userDoc)
		if err != nil {
			logger.Error("Error actualizando usuario en MongoDB", err)
			return err
		}

		logger.Success("Usuario actualizado en MongoDB")
		return nil
	}

	// Usuario no existe, crear nuevo
	userDoc := UserDocument{
		Username:  user.Username,
		Password:  user.Password,
		CreatedAt: user.CreatedAt,
		UpdatedAt: user.UpdatedAt,
	}

	result, err := r.collection.InsertOne(ctx, userDoc)
	if err != nil {
		logger.Error("Error guardando usuario en MongoDB", err)
		return err
	}

	// Actualizar el ID del usuario con el ObjectID generado por MongoDB
	if oid, ok := result.InsertedID.(primitive.ObjectID); ok {
		user.ID = oid.Hex()
	}

	logger.Success("Usuario guardado en MongoDB")
	return nil
}

// Exists verifica si existe un usuario con el username dado
func (r *MongoDBUserRepository) Exists(username string) (bool, error) {
	// Establecer contexto para logging
	logger.SetContext(logger.Context{
		FunctionName: "MongoDBUserRepository.Exists",
		Data: map[string]interface{}{
			"username": username,
		},
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	count, err := r.collection.CountDocuments(ctx, bson.M{"username": username})
	if err != nil {
		logger.Error("Error verificando existencia de usuario en MongoDB", err)
		return false, err
	}

	exists := count > 0
	logger.Info("Verificación de existencia de usuario completada", map[string]interface{}{
		"exists": exists,
	})

	return exists, nil
}

// Ensure MongoDBUserRepository implementa UserRepository
var _ repositories.UserRepository = (*MongoDBUserRepository)(nil) 