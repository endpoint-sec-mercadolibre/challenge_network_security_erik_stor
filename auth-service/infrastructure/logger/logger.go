package logger

import (
	"os"
	"path/filepath"
	"runtime"
	"time"

	"github.com/fatih/color"
	"github.com/sirupsen/logrus"
)

// Context representa el contexto de la operación
type Context struct {
	FunctionName string                 `json:"functionName"`
	Data         map[string]interface{} `json:"data,omitempty"`
}

// Logger es la estructura principal del logger
type Logger struct {
	logger *logrus.Logger
	file   *os.File
}

var (
	instance *Logger
	context  Context
)

// GetInstance retorna la instancia singleton del logger
func GetInstance() *Logger {
	if instance == nil {
		instance = &Logger{
			logger: logrus.New(),
		}
		instance.setupLogger()
	}
	return instance
}

// setupLogger configura el logger con formato JSON y archivo de salida
func (l *Logger) setupLogger() {
	// Crear directorio de logs si no existe
	logDir := "logs"
	if err := os.MkdirAll(logDir, 0755); err != nil {
		panic("No se pudo crear el directorio de logs: " + err.Error())
	}

	// Abrir archivo de log
	logFile := filepath.Join(logDir, "auth-service.log")
	file, err := os.OpenFile(logFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		panic("No se pudo abrir el archivo de log: " + err.Error())
	}

	l.file = file
	l.logger.SetOutput(file)
	l.logger.SetFormatter(&logrus.JSONFormatter{
		TimestampFormat: time.RFC3339,
		FieldMap: logrus.FieldMap{
			logrus.FieldKeyTime:  "timestamp",
			logrus.FieldKeyLevel: "level",
			logrus.FieldKeyMsg:   "message",
		},
	})
	l.logger.SetLevel(logrus.InfoLevel)
}

// SetContext establece el contexto para los logs
func SetContext(ctx Context) {
	context = ctx
}

// AddContext agrega datos adicionales al contexto existente
func AddContext(data map[string]interface{}) {
	if context.Data == nil {
		context.Data = make(map[string]interface{})
	}
	for k, v := range data {
		context.Data[k] = v
	}
}

// getCallerInfo obtiene información de la función que llama al logger
func getCallerInfo() string {
	pc, _, _, ok := runtime.Caller(2)
	if ok {
		fn := runtime.FuncForPC(pc)
		if fn != nil {
			return fn.Name()
		}
	}
	return "unknown"
}

// Info registra un mensaje de información
func Info(message string, data ...map[string]interface{}) {
	logger := GetInstance()
	fields := logrus.Fields{
		"context": context,
		"caller":  getCallerInfo(),
	}

	if len(data) > 0 {
		for k, v := range data[0] {
			fields[k] = v
		}
	}

	// Log a archivo
	logger.logger.WithFields(fields).Info(message)

	// Log a consola con color
	color.Blue("[INFO] %s", message)
	if len(data) > 0 {
		color.Cyan("  Data: %+v", data[0])
	}
}

// Error registra un mensaje de error
func Error(message string, err error) {
	logger := GetInstance()
	fields := logrus.Fields{
		"context": context,
		"caller":  getCallerInfo(),
	}

	if err != nil {
		fields["error"] = err.Error()
	}

	// Log a archivo
	logger.logger.WithFields(fields).Error(message)

	// Log a consola con color
	color.Red("[ERROR] %s", message)
	if err != nil {
		color.Red("  Error: %v", err)
	}
}

// Warn registra un mensaje de advertencia
func Warn(message string, data ...map[string]interface{}) {
	logger := GetInstance()
	fields := logrus.Fields{
		"context": context,
		"caller":  getCallerInfo(),
	}

	if len(data) > 0 {
		for k, v := range data[0] {
			fields[k] = v
		}
	}

	// Log a archivo
	logger.logger.WithFields(fields).Warn(message)

	// Log a consola con color
	color.Yellow("[WARN] %s", message)
	if len(data) > 0 {
		color.Yellow("  Data: %+v", data[0])
	}
}

// Debug registra un mensaje de debug
func Debug(message string, data ...map[string]interface{}) {
	logger := GetInstance()
	fields := logrus.Fields{
		"context": context,
		"caller":  getCallerInfo(),
	}

	if len(data) > 0 {
		for k, v := range data[0] {
			fields[k] = v
		}
	}

	// Log a archivo
	logger.logger.WithFields(fields).Debug(message)

	// Log a consola con color
	color.White("[DEBUG] %s", message)
	if len(data) > 0 {
		color.White("  Data: %+v", data[0])
	}
}

// Success registra un mensaje de éxito
func Success(message string, data ...map[string]interface{}) {
	logger := GetInstance()
	fields := logrus.Fields{
		"context": context,
		"caller":  getCallerInfo(),
	}

	if len(data) > 0 {
		for k, v := range data[0] {
			fields[k] = v
		}
	}

	// Log a archivo como info
	logger.logger.WithFields(fields).Info(message)

	// Log a consola con color verde
	color.Green("[SUCCESS] %s", message)
	if len(data) > 0 {
		color.Green("  Data: %+v", data[0])
	}
}

// Close cierra el archivo de log
func (l *Logger) Close() error {
	if l.file != nil {
		return l.file.Close()
	}
	return nil
}
