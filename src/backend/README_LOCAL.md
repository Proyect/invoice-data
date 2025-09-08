# 🚀 Guía de Ejecución Local - Backend OCR

## 📋 Prerrequisitos

### 1. Python y Dependencias
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### 2. Tesseract OCR
- **Windows**: Descargar desde [GitHub Tesseract](https://github.com/tesseract-ocr/tesseract)
- **Agregar al PATH**: `C:\Program Files\Tesseract-OCR`

### 3. Configuración Inicial
```bash
# Ejecutar script de configuración
python setup_local.py
```

## 🔧 Configuración

### Variables de Entorno
El archivo `.env.local` ya está configurado con:
- SQLite como base de datos
- Almacenamiento local de archivos
- Configuración JWT para desarrollo

### Credenciales de Prueba
- **Usuario**: `testuser`
- **Contraseña**: `testpassword`

## 🚀 Ejecución

### Iniciar el Servidor
```bash
python run_local.py
```

El servidor estará disponible en:
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs

## 🧪 Pruebas

### 1. Autenticación
```bash
curl -X POST "http://localhost:8000/api/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword"
```

### 2. Subir Documento
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_image.jpg" \
  -F "document_type=DNI_FRONT"
```

## 🔍 Estructura del Proyecto

```
backend/
├── api/v1/           # Endpoints de la API
├── models/           # Modelos Pydantic y Enums
├── services/         # Lógica de negocio
├── workers/          # Procesamiento asíncrono
├── uploaded_documents_local/  # Archivos subidos
├── models/yolo_models/       # Modelos YOLO
└── test.db          # Base de datos SQLite
```

## ⚠️ Limitaciones Actuales

1. **Modelos YOLO**: Solo modelo genérico (yolov8n.pt)
2. **Redis**: No configurado (procesamiento síncrono)
3. **OCR**: Tesseract básico sin optimizaciones

## 🐛 Solución de Problemas

### Error: "Modelo YOLO no encontrado"
```bash
# El script setup_local.py descarga automáticamente yolov8n.pt
python setup_local.py
```

### Error: "Tesseract not found"
- Verificar instalación de Tesseract
- Agregar al PATH del sistema

### Error: "Database locked"
- Cerrar todas las conexiones a test.db
- Reiniciar el servidor

## 📚 Próximos Pasos

1. Entrenar modelos YOLO específicos
2. Configurar Redis para mejor rendimiento
3. Implementar logging y monitoreo
4. Agregar validaciones adicionales
