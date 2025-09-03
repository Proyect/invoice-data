# OCR Document Processor API

API para procesar documentos oficiales y facturas usando YOLO + OCR con FastAPI.

## 🚀 Características

- **Procesamiento de Documentos**: DNI, Facturas tipo A, B y C
- **OCR Inteligente**: YOLO + Tesseract para detección y extracción de campos
- **Procesamiento Asíncrono**: Cola de tareas con Redis + RQ
- **Autenticación JWT**: Sistema de usuarios con tokens seguros
- **Almacenamiento Local**: Sistema de archivos para documentos subidos
- **Base de Datos PostgreSQL**: Almacenamiento persistente de metadatos y resultados

## 📋 Requisitos Previos

- Docker y Docker Compose
- Python 3.11+ (para desarrollo local)
- PostgreSQL 15+
- Redis 7+

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd invoice-data/src/backend
```

### 2. Configurar variables de entorno
```bash
cp env.example .env
# Editar .env con tus valores
```

### 3. Ejecutar con Docker Compose
```bash
docker-compose up --build
```

## 🔧 Configuración

### Variables de Entorno (.env)

```bash
# Base de datos
POSTGRES_DB=ocr_database
POSTGRES_USER=ocr_user
POSTGRES_PASSWORD=your_password
DATABASE_URL=postgresql://ocr_user:your_password@db:5432/ocr_database

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT
SECRET_KEY_JWT=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Almacenamiento
LOCAL_STORAGE_PATH=/app/uploaded_documents_local
```

## 📚 Uso de la API

### 1. Autenticación
```bash
# Obtener token
curl -X POST "http://localhost:8000/api/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword"
```

### 2. Subir documento
```bash
# Subir documento para OCR
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@documento.jpg" \
  -F "document_type=DNI_FRONT"
```

### 3. Consultar estado
```bash
# Ver estado del documento
curl "http://localhost:8000/api/v1/documents/{document_id}/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Obtener datos extraídos
```bash
# Obtener resultados del OCR
curl "http://localhost:8000/api/v1/documents/{document_id}/extracted_data" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🏗️ Arquitectura

```
├── api/v1/           # Endpoints de la API
├── models/           # Modelos Pydantic
├── services/         # Lógica de negocio
├── workers/          # Workers de procesamiento
├── database.py       # Configuración de BD
├── config.py         # Configuración general
└── main.py          # Punto de entrada
```

## 🔍 Servicios

- **Auth Service**: Autenticación JWT y gestión de usuarios
- **Document Service**: Gestión de documentos en BD
- **OCR Service**: Procesamiento YOLO + Tesseract
- **Storage Service**: Almacenamiento de archivos
- **Task Queue Service**: Cola de tareas asíncronas

## 🚨 Solución de Problemas

### Error de conexión a BD
- Verificar que PostgreSQL esté ejecutándose
- Comprobar variables de entorno en .env

### Error de Redis
- Verificar que Redis esté ejecutándose
- Comprobar puerto 6379

### Error de modelos YOLO
- Crear directorio `models/yolo_models/`
- Colocar modelos entrenados (.pt files)

### Error de permisos
- Verificar permisos en directorio de almacenamiento
- Asegurar que el usuario del contenedor tenga acceso

## 📝 Desarrollo

### Ejecutar tests
```bash
# Próximamente
pytest
```

### Linting
```bash
# Próximamente
flake8
black
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Para soporte, email: [tu-email@ejemplo.com](mailto:tu-email@ejemplo.com)
