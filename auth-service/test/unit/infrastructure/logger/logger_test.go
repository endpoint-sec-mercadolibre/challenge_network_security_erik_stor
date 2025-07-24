package logger

import (
	"testing"
)

func TestSetContext(t *testing.T) {
	// Arrange
	context := Context{
		FunctionName: "TestFunction",
		Data: map[string]interface{}{
			"key": "value",
		},
	}

	// Act
	SetContext(context)

	// Assert - Verificar que el contexto se estableció correctamente
	// (No hay forma directa de verificar el contexto, pero podemos verificar que no hay error)
}

func TestInfo(t *testing.T) {
	// Arrange
	message := "Test info message"

	// Act & Assert - No debería fallar
	Info(message)
}

func TestInfoWithData(t *testing.T) {
	// Arrange
	message := "Test info message with data"
	data := map[string]interface{}{
		"key1": "value1",
		"key2": 123,
	}

	// Act & Assert - No debería fallar
	Info(message, data)
}

func TestSuccess(t *testing.T) {
	// Arrange
	message := "Test success message"

	// Act & Assert - No debería fallar
	Success(message)
}

func TestSuccessWithData(t *testing.T) {
	// Arrange
	message := "Test success message with data"
	data := map[string]interface{}{
		"key1": "value1",
		"key2": 123,
	}

	// Act & Assert - No debería fallar
	Success(message, data)
}

func TestError(t *testing.T) {
	// Arrange
	message := "Test error message"
	err := &MockError{message: "test error"}

	// Act & Assert - No debería fallar
	Error(message, err)
}

func TestErrorWithoutError(t *testing.T) {
	// Arrange
	message := "Test error message without error"

	// Act & Assert - No debería fallar
	Error(message, nil)
}

func TestWarn(t *testing.T) {
	// Arrange
	message := "Test warning message"

	// Act & Assert - No debería fallar
	Warn(message)
}

func TestWarnWithData(t *testing.T) {
	// Arrange
	message := "Test warning message with data"
	data := map[string]interface{}{
		"key1": "value1",
		"key2": 123,
	}

	// Act & Assert - No debería fallar
	Warn(message, data)
}

func TestDebug(t *testing.T) {
	// Arrange
	message := "Test debug message"

	// Act & Assert - No debería fallar
	Debug(message)
}

func TestDebugWithData(t *testing.T) {
	// Arrange
	message := "Test debug message with data"
	data := map[string]interface{}{
		"key1": "value1",
		"key2": 123,
	}

	// Act & Assert - No debería fallar
	Debug(message, data)
}

type MockError struct {
	message string
}

func (e *MockError) Error() string {
	return e.message
}
