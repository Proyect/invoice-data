# 📚 Manual del Desarrollador - Sistema OCR Universal

**Versión**: 1.0  
**Fecha**: Enero 2025  
**Autor**: Equipo de Desarrollo OCR  

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Componentes Principales](#componentes-principales)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Guía de Desarrollo](#guía-de-desarrollo)
6. [API y Servicios](#api-y-servicios)
7. [Base de Datos](#base-de-datos)
8. [Testing y Debugging](#testing-y-debugging)
9. [Despliegue](#despliegue)
10. [Mantenimiento](#mantenimiento)
11. [Troubleshooting](#troubleshooting)
12. [Roadmap](#roadmap)

---

## 🎯 Introducción

### ¿Qué es el Sistema OCR Universal?

El Sistema OCR Universal es una solución completa para el procesamiento automático de documentos mediante reconocimiento óptico de caracteres (OCR). El sistema puede procesar **cualquier tipo de documento** (facturas, DNI, recibos, tarjetas, contratos) y extraer datos estructurados de manera inteligente.

### Características Principales

- 🔄 **Procesamiento Universal**: Maneja cualquier tipo de documento
- 🤖 **Detección Automática**: Identifica el tipo de documento automáticamente
- 📈 **Alta Precisión**: Extracción confiable de datos estructurados
- ⚡ **Optimización Inteligente**: Preprocesamiento específico por tipo
- 🛡️ **Robusto**: Manejo de errores y validación de calidad
- 📊 **Escalable**: Arquitectura modular y extensible

### Casos de Uso

- **Facturación**: Procesamiento automático de facturas argentinas
- **Identificación**: Extracción de datos de DNI y documentos de identidad
- **Contabilidad**: Procesamiento de recibos y comprobantes
- **Finanzas**: Análisis de tarjetas de crédito y documentos bancarios
- **Legal**: Procesamiento de contratos y documentos legales

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA OCR UNIVERSAL                    │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React)                                          │
│  ├── Componentes de UI                                     │
│  ├── Gestión de Estado                                     │
│  └── Visualización de Resultados                           │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI)                                         │
│  ├── API REST                                              │
│  ├── Autenticación JWT                                     │
│  └── Gestión de Documentos                                 │
├─────────────────────────────────────────────────────────────┤
│  Servicios de Procesamiento                                │
│  ├── Universal Image Preprocessor                          │
│  ├── Universal OCR Service                                 │
│  ├── YOLO Detection Service                                │
│  └── Data Extraction Service                               │
├─────────────────────────────────────────────────────────────┤
│  Almacenamiento                                            │
│  ├── PostgreSQL (Metadatos)                               │
│  ├── Redis (Cache)                                         │
│  └── File System (Imágenes)                                │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Procesamiento

```mermaid
graph TD
    A[Imagen de Entrada] --> B[Preprocesamiento Universal]
    B --> C[Detección de Tipo de Documento]
    C --> D[Preprocesamiento Específico]
    D --> E[Detección YOLO de Campos]
    E --> F[Extracción OCR de Texto]
    F --> G[Extracción de Datos Estructurados]
    G --> H[Validación y Limpieza]
    H --> I[Cálculo de Confianza]
    I --> J[Resultado Final]
```

---

## 🔧 Componentes Principales

### 1. Universal Image Preprocessor

**Archivo**: `backend/services/universal_image_preprocessor.py`

#### Propósito
Preprocesa imágenes de documentos para optimizar el reconocimiento OCR.

#### Características
- Detección automática del tipo de documento
- Corrección de rotación y perspectiva
- Mejora de contraste y nitidez
- Reducción de ruido
- Evaluación de calidad de imagen

#### Uso
```python
from services.universal_image_preprocessor import UniversalImagePreprocessor

preprocessor = UniversalImagePreprocessor()
result = preprocessor.preprocess_image("documento.jpg", "FACTURA")
```

#### Métodos Principales

| Método | Descripción | Parámetros | Retorna |
|--------|-------------|------------|---------|
| `preprocess_image()` | Procesa una imagen completa | `image_path`, `document_type` | `Dict` con imagen procesada y metadatos |
| `_detect_document_type()` | Detecta el tipo de documento | `image` | `str` tipo de documento |
| `_auto_rotate()` | Corrige rotación automáticamente | `image` | `np.ndarray` imagen rotada |
| `_enhance_contrast()` | Mejora el contraste | `image`, `factor` | `np.ndarray` imagen mejorada |

### 2. Universal OCR Service

**Archivo**: `backend/services/universal_ocr_service.py`

#### Propósito
Servicio principal que coordina el procesamiento completo de documentos.

#### Características
- Procesamiento de cualquier tipo de documento
- Extracción de texto con Tesseract
- Extracción de datos estructurados
- Validación y limpieza de datos
- Cálculo de confianza

#### Uso
```python
from services.universal_ocr_service import UniversalOCRService

ocr_service = UniversalOCRService()
result = ocr_service.process_document("documento.jpg", "FACTURA")
```

#### Métodos Principales

| Método | Descripción | Parámetros | Retorna |
|--------|-------------|------------|---------|
| `process_document()` | Procesa un documento completo | `image_path`, `document_type` | `Dict` con datos extraídos |
| `_extract_text_with_ocr()` | Extrae texto con Tesseract | `image` | `str` texto extraído |
| `_extract_structured_data()` | Extrae datos estructurados | `text`, `document_type`, `fields` | `Dict` datos estructurados |
| `_validate_and_clean_data()` | Valida y limpia datos | `data`, `document_type` | `Dict` datos validados |

### 3. Universal Document Generator

**Archivo**: `backend/scripts/universal_document_generator.py`

#### Propósito
Genera datasets sintéticos para entrenamiento de modelos YOLO.

#### Características
- Generación de 5 tipos de documentos
- 1000+ imágenes de entrenamiento
- Múltiples clases por tipo de documento
- Datos realistas argentinos

#### Uso
```python
from scripts.universal_document_generator import UniversalDocumentGenerator

generator = UniversalDocumentGenerator()
generator.generate_universal_dataset(1000)
```

### 4. Process Any Document Script

**Archivo**: `backend/scripts/process_any_document.py`

#### Propósito
Script de línea de comandos para procesar documentos.

#### Uso
```bash
# Procesar cualquier documento
python scripts/process_any_document.py mi_documento.jpg

# Procesar con tipo específico
python scripts/process_any_document.py mi_factura.jpg --type FACTURA

# Exportar resultados
python scripts/process_any_document.py mi_documento.jpg --output resultado.json

# Ejecutar pruebas
python scripts/process_any_document.py --test
```

---

## ⚙️ Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- Tesseract OCR

### Instalación del Backend

```bash
# Clonar repositorio
git clone https://github.com/Proyect/invoice-data.git
cd invoice-data/src/backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
python setup_local.py

# Ejecutar migraciones
alembic upgrade head
```

### Instalación del Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con la URL del backend

# Ejecutar en desarrollo
npm start
```

### Configuración de Tesseract

#### Windows
1. Descargar Tesseract desde [GitHub](https://github.com/tesseract-ocr/tesseract)
2. Instalar en `C:\Program Files\Tesseract-OCR`
3. Agregar al PATH del sistema

#### Linux
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-spa
```

#### macOS
```bash
brew install tesseract tesseract-lang
```

### Variables de Entorno

#### Backend (.env)
```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/ocr_db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Tesseract
TESSERACT_PATH=/usr/bin/tesseract

# Almacenamiento
UPLOAD_DIR=uploaded_documents_local
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

---

## 💻 Guía de Desarrollo

### Estructura del Proyecto

```
backend/
├── api/                    # Endpoints de la API
│   └── v1/
│       ├── auth.py        # Autenticación
│       ├── documents.py   # Gestión de documentos
│       └── __init__.py
├── services/              # Servicios de negocio
│   ├── universal_image_preprocessor.py
│   ├── universal_ocr_service.py
│   ├── auth_service.py             # Autenticación
│   └── document_service.py
├── models/                # Modelos de datos
│   ├── auth.py
│   ├── documents.py
│   └── enums.py
├── scripts/               # Scripts de utilidad
│   ├── universal_document_generator.py
│   ├── process_any_document.py
│   └── ejecutar_sistema_completo.py
├── tests/                 # Tests unitarios
├── requirements.txt       # Dependencias Python
└── main.py               # Punto de entrada

frontend/
├── src/
│   ├── components/        # Componentes React
│   ├── pages/            # Páginas
│   ├── services/         # Servicios de API
│   ├── contexts/         # Contextos de React
│   └── types/            # Tipos TypeScript
├── package.json          # Dependencias Node.js
└── public/               # Archivos estáticos
```

### Convenciones de Código

#### Python
- **PEP 8**: Seguir estándares de Python
- **Type Hints**: Usar anotaciones de tipo
- **Docstrings**: Documentar todas las funciones
- **Logging**: Usar logging en lugar de print

```python
def process_document(self, image_path: str, document_type: str = "UNKNOWN") -> Dict[str, Any]:
    """
    Procesa un documento y extrae datos estructurados.
    
    Args:
        image_path: Ruta a la imagen del documento
        document_type: Tipo de documento (opcional)
        
    Returns:
        Dict con datos extraídos y metadatos
        
    Raises:
        ValueError: Si la imagen no se puede cargar
        OCRException: Si falla el procesamiento OCR
    """
    logger.info(f"Procesando documento: {image_path}")
    # ... implementación
```

#### TypeScript/React
- **ESLint**: Seguir reglas de ESLint
- **Prettier**: Formateo automático
- **Interfaces**: Definir interfaces para tipos
- **Hooks**: Usar hooks de React

```typescript
interface DocumentProcessingResult {
  success: boolean;
  documentType: string;
  qualityScore: number;
  confidenceScore: number;
  structuredData: Record<string, any>;
  recommendations: string[];
}

const useDocumentProcessing = () => {
  const [result, setResult] = useState<DocumentProcessingResult | null>(null);
  // ... implementación
};
```

### Patrones de Diseño

#### 1. Service Layer Pattern
```python
class UniversalOCRService:
    def __init__(self):
        self.preprocessor = UniversalImagePreprocessor()
        self.extractor = DataExtractor()
    
    def process_document(self, image_path: str) -> Dict[str, Any]:
        # Coordina diferentes servicios
        pass
```

#### 2. Strategy Pattern
```python
class DocumentProcessor:
    def __init__(self, strategy: ProcessingStrategy):
        self.strategy = strategy
    
    def process(self, document: Document) -> Result:
        return self.strategy.process(document)
```

#### 3. Factory Pattern
```python
class DocumentProcessorFactory:
    @staticmethod
    def create_processor(document_type: str) -> DocumentProcessor:
        if document_type == "FACTURA":
            return FacturaProcessor()
        elif document_type == "DNI":
            return DNIProcessor()
        # ...
```

---

## 🔌 API y Servicios

### Endpoints de la API

#### Autenticación
```http
POST /api/v1/token
Content-Type: application/x-www-form-urlencoded

username=usuario&password=contraseña
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Subida de Documentos
```http
POST /api/v1/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <archivo>
document_type: FACTURA
```

**Respuesta:**
```json
{
  "document_id": "uuid-1234",
  "filename": "factura.jpg",
  "status": "PROCESSING",
  "message": "Documento en procesamiento"
}
```

#### Estado del Documento
```http
GET /api/v1/documents/{document_id}/status
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "document_id": "uuid-1234",
  "status": "COMPLETED",
  "progress": 100,
  "message": "Procesamiento completado"
}
```

#### Datos Extraídos
```http
GET /api/v1/documents/{document_id}/extracted_data
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "document_id": "uuid-1234",
  "document_type": "FACTURA",
  "quality_score": 85.5,
  "confidence_score": 92.3,
  "structured_data": {
    "numero_factura": "0001-00012345",
    "fecha_emision": "15/01/2025",
    "proveedor": "TECHNOLOGY SOLUTIONS S.A.",
    "cuit_proveedor": "30-12345678-9",
    "total": "$15,750.00"
  },
  "raw_text": "FACTURA N° 0001-00012345...",
  "recommendations": [
    "Imagen de buena calidad para OCR"
  ]
}
```

### Servicios Internos

#### Universal Image Preprocessor
```python
class UniversalImagePreprocessor:
    def preprocess_image(self, image_path: str, document_type: str = "UNKNOWN") -> Dict[str, Any]:
        """
        Preprocesa una imagen para optimizar el OCR.
        
        Returns:
            {
                'processed_image': np.ndarray,
                'original_image': np.ndarray,
                'document_type': str,
                'quality_score': float,
                'preprocessing_applied': List[str],
                'recommendations': List[str]
            }
        """
```

#### Universal OCR Service
```python
class UniversalOCRService:
    def process_document(self, image_path: str, document_type: str = "UNKNOWN") -> Dict[str, Any]:
        """
        Procesa un documento completo.
        
        Returns:
            {
                'success': bool,
                'document_type': str,
                'quality_score': float,
                'confidence_score': float,
                'raw_text': str,
                'structured_data': Dict[str, Any],
                'detected_fields': List[Dict],
                'recommendations': List[str]
            }
        """
```

---

## 🗄️ Base de Datos

### Esquema de Base de Datos

#### Tabla: users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    disabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla: documents
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    quality_score FLOAT,
    confidence_score FLOAT,
    processing_error TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla: extracted_data
```sql
CREATE TABLE extracted_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_value TEXT,
    confidence FLOAT,
    extraction_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Migraciones

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

---

## 🧪 Testing y Debugging

### Tests Unitarios

#### Estructura de Tests
```
tests/
├── test_services/
│   ├── test_universal_image_preprocessor.py
│   ├── test_universal_ocr_service.py
│   └── test_document_service.py
├── test_api/
│   ├── test_auth.py
│   └── test_documents.py
├── test_models/
│   └── test_document_models.py
└── conftest.py
```

#### Ejemplo de Test
```python
import pytest
from services.universal_image_preprocessor import UniversalImagePreprocessor

class TestUniversalImagePreprocessor:
    def test_preprocess_image_success(self, sample_image_path):
        """Test successful image preprocessing"""
        preprocessor = UniversalImagePreprocessor()
        result = preprocessor.preprocess_image(sample_image_path)
        
        assert result['processed_image'] is not None
        assert result['quality_score'] > 0
        assert result['document_type'] in ['FACTURA', 'DNI', 'RECIBO', 'TARJETA', 'CONTRATO']
    
    def test_preprocess_image_invalid_path(self):
        """Test preprocessing with invalid image path"""
        preprocessor = UniversalImagePreprocessor()
        
        with pytest.raises(ValueError):
            preprocessor.preprocess_image("invalid_path.jpg")
```

### Tests de Integración

```python
def test_complete_document_processing_flow(client, auth_headers, sample_image):
    """Test complete document processing flow"""
    # 1. Upload document
    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": sample_image},
        data={"document_type": "FACTURA"}
    )
    assert response.status_code == 200
    document_id = response.json()["document_id"]
    
    # 2. Wait for processing
    time.sleep(5)
    
    # 3. Check status
    response = client.get(
        f"/api/v1/documents/{document_id}/status",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"
    
    # 4. Get extracted data
    response = client.get(
        f"/api/v1/documents/{document_id}/extracted_data",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "structured_data" in data
    assert data["confidence_score"] > 0
```

### Debugging

#### Logging
```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ocr_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usar en el código
logger.info(f"Procesando documento: {image_path}")
logger.error(f"Error en OCR: {error}")
```

#### Debug Mode
```python
# En desarrollo
DEBUG = True

# Logging detallado
if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
```

---

## 🚀 Despliegue

### Docker

#### Dockerfile Backend
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ocr_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./uploaded_documents:/app/uploaded_documents

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api/v1

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=ocr_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Producción

#### Variables de Entorno
```env
# Producción
DEBUG=False
DATABASE_URL=postgresql://user:password@prod-db:5432/ocr_db
REDIS_URL=redis://prod-redis:6379
SECRET_KEY=your-production-secret-key
UPLOAD_DIR=/app/uploads
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔧 Mantenimiento

### Monitoreo

#### Métricas de Sistema
- Tiempo de procesamiento por documento
- Tasa de éxito de extracción
- Calidad promedio de imágenes
- Uso de recursos (CPU, memoria)

#### Logs de Aplicación
```python
# Configurar logging estructurado
import structlog

logger = structlog.get_logger()

# Log con contexto
logger.info(
    "Document processed",
    document_id=document_id,
    processing_time=processing_time,
    confidence_score=confidence_score
)
```

### Backup

#### Base de Datos
```bash
# Backup diario
pg_dump -h localhost -U postgres ocr_db > backup_$(date +%Y%m%d).sql

# Restaurar
psql -h localhost -U postgres ocr_db < backup_20250101.sql
```

#### Archivos
```bash
# Backup de imágenes
tar -czf images_backup_$(date +%Y%m%d).tar.gz uploaded_documents/

# Sincronizar con S3
aws s3 sync uploaded_documents/ s3://your-bucket/documents/
```

### Actualizaciones

#### Actualización de Modelos
```python
# Script para actualizar modelos YOLO
def update_yolo_model():
    """Actualiza el modelo YOLO con nueva versión"""
    # 1. Descargar nuevo modelo
    # 2. Validar modelo
    # 3. Reemplazar modelo actual
    # 4. Reiniciar servicios
    pass
```

#### Migración de Datos
```python
# Script de migración
def migrate_document_types():
    """Migra tipos de documentos a nueva estructura"""
    # 1. Backup de datos actuales
    # 2. Transformar datos
    # 3. Actualizar base de datos
    # 4. Validar migración
    pass
```

---

## 🐛 Troubleshooting

### Problemas Comunes

#### 1. Error de Tesseract
```
Error: TesseractNotFoundError
```

**Solución:**
```bash
# Verificar instalación
tesseract --version

# Verificar PATH
echo $PATH

# Instalar dependencias
sudo apt-get install tesseract-ocr tesseract-ocr-spa
```

#### 2. Error de Memoria
```
Error: CUDA out of memory
```

**Solución:**
```python
# Reducir batch size
BATCH_SIZE = 1

# Usar CPU en lugar de GPU
device = "cpu"
```

#### 3. Error de Base de Datos
```
Error: connection to server at "localhost" (127.0.0.1), port 5432 failed
```

**Solución:**
```bash
# Verificar estado de PostgreSQL
sudo systemctl status postgresql

# Iniciar servicio
sudo systemctl start postgresql

# Verificar conexión
psql -h localhost -U postgres -d ocr_db
```

### Debugging Avanzado

#### Profiling de Rendimiento
```python
import cProfile
import pstats

def profile_ocr_processing():
    """Profile del procesamiento OCR"""
    pr = cProfile.Profile()
    pr.enable()
    
    # Código a perfilar
    result = ocr_service.process_document("test.jpg")
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

#### Análisis de Memoria
```python
import tracemalloc

def analyze_memory_usage():
    """Analiza el uso de memoria"""
    tracemalloc.start()
    
    # Código a analizar
    result = ocr_service.process_document("test.jpg")
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    
    tracemalloc.stop()
```

---

## 🗺️ Roadmap

### Versión 1.1 (Q2 2025)
- [ ] Integración completa con modelo YOLO
- [ ] Soporte para más tipos de documentos
- [ ] API de webhooks para notificaciones
- [ ] Dashboard de métricas en tiempo real

### Versión 1.2 (Q3 2025)
- [ ] Procesamiento por lotes
- [ ] Integración con servicios en la nube
- [ ] API de machine learning para mejoras
- [ ] Soporte para documentos escaneados

### Versión 2.0 (Q4 2025)
- [ ] Procesamiento en tiempo real
- [ ] Integración con sistemas ERP
- [ ] Análisis predictivo de calidad
- [ ] Soporte multiidioma

---

## 📞 Soporte

### Contacto
- **Email**: dev@ocr-system.com
- **Slack**: #ocr-development
- **GitHub**: [Repository Issues](https://github.com/your-org/ocr-system/issues)

### Documentación Adicional
- [API Documentation](http://localhost:8000/docs)
- [Frontend Storybook](http://localhost:3000/storybook)
- [Database Schema](docs/database-schema.md)
- [Deployment Guide](docs/deployment.md)

---

**Última actualización**: Enero 2025  
**Versión del manual**: 1.0  
**Mantenido por**: Equipo de Desarrollo OCR

