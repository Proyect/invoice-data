# 🚀 Manual del Desarrollador - OCR Document Processor

## 📋 Tabla de Contenidos
1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Configuración del Entorno](#configuración-del-entorno)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [APIs y Endpoints](#apis-y-endpoints)
6. [Base de Datos](#base-de-datos)
7. [Autenticación y Seguridad](#autenticación-y-seguridad)
8. [Procesamiento de Documentos](#procesamiento-de-documentos)
9. [Modelos YOLO](#modelos-yolo)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

El **OCR Document Processor** es un sistema completo para el procesamiento de documentos oficiales y facturas utilizando tecnologías de vanguardia como YOLO (You Only Look Once) para detección de objetos y Tesseract para OCR.

### 🛠️ Tecnologías Principales
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + TypeScript + Material-UI
- **Base de Datos**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Procesamiento**: Celery + Redis
- **IA/ML**: YOLO v8, Tesseract OCR
- **Containerización**: Docker + Docker Compose

---

## 🏗️ Arquitectura del Sistema

### 📊 Diagrama de Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   React + TS    │◄──►│   FastAPI       │◄──►│   PostgreSQL    │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis Queue   │    │   OCR Worker    │
                       │   Port: 6379    │◄──►│   Celery        │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   YOLO Models   │
                       │   Tesseract     │
                       └─────────────────┘
```

### 🔄 Flujo de Procesamiento

1. **Upload**: Usuario sube documento vía Frontend
2. **API**: Backend recibe archivo y crea registro en DB
3. **Queue**: Documento se encola para procesamiento
4. **Worker**: Celery worker procesa el documento
5. **YOLO**: Detección de campos usando YOLO
6. **OCR**: Extracción de texto usando Tesseract
7. **Response**: Resultados almacenados en DB
8. **Frontend**: Usuario ve resultados procesados

---

## ⚙️ Configuración del Entorno

### 📦 Prerrequisitos

```bash
# Docker y Docker Compose
Docker Desktop >= 4.20
Docker Compose >= 2.0

# Para desarrollo local (opcional)
Node.js >= 18
Python >= 3.11
```

### 🔧 Variables de Entorno

#### Backend (.env)
```env
# Base de Datos
POSTGRES_DB=ocr_database
POSTGRES_USER=ocr_user
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://ocr_user:your_secure_password_here@db:5432/ocr_database

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT
SECRET_KEY_JWT=your_super_secret_jwt_key_here_make_it_long_and_random
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Almacenamiento
LOCAL_STORAGE_PATH=/app/uploaded_documents_local
YOLO_MODELS_PATH=/app/models/yolo_models
```

#### Frontend (.env.local)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
GENERATE_SOURCEMAP=false
```

---

## 📁 Estructura del Proyecto

```
src/
├── backend/                    # Backend FastAPI
│   ├── api/                   # API Routes
│   │   └── v1/
│   │       ├── auth.py        # Autenticación
│   │       └── documents.py   # Documentos
│   ├── models/                # Modelos SQLAlchemy
│   ├── services/              # Lógica de negocio
│   ├── ocr_worker/            # Worker Celery
│   ├── scripts/               # Scripts de entrenamiento
│   ├── requirements.txt       # Dependencias Python
│   └── Dockerfile            # Imagen Docker
│
├── frontend/                  # Frontend React
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   ├── pages/            # Páginas
│   │   ├── contexts/         # Context API
│   │   ├── services/         # Servicios API
│   │   └── types/            # TypeScript types
│   ├── package.json          # Dependencias Node
│   └── Dockerfile            # Imagen Docker
│
└── docker-compose.full.yml   # Orquestación completa
```

---

## 🌐 APIs y Endpoints

### 🔐 Autenticación

#### POST `/api/v1/token`
Obtener token JWT de acceso

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 📄 Documentos

#### GET `/api/v1/documents/`
Listar todos los documentos

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "documents": [
    {
      "id": "uuid",
      "original_filename": "invoice.jpg",
      "document_type": "INVOICE",
      "status": "COMPLETED",
      "created_at": "2025-01-22T12:42:41.979Z",
      "updated_at": "2025-01-22T12:42:41.979Z"
    }
  ]
}
```

#### POST `/api/v1/documents/upload`
Subir nuevo documento

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer {token}" \
  -F "file=@document.jpg" \
  -F "document_type=INVOICE"
```

#### GET `/api/v1/documents/{id}/status`
Obtener estado del documento

#### GET `/api/v1/documents/{id}/extracted`
Obtener datos extraídos

#### GET `/api/v1/documents/{id}/structured`
Obtener datos estructurados

#### DELETE `/api/v1/documents/{id}`
Eliminar documento

#### GET `/api/v1/documents/{id}/download`
Descargar documento original

---

## 🗄️ Base de Datos

### 📊 Esquema Principal

#### Tabla: `users`
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

#### Tabla: `documents`
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    original_filename VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',
    file_path VARCHAR(500),
    extracted_data JSONB,
    structured_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 🔄 Migraciones

```bash
# Ejecutar migraciones
docker exec -it src-backend-1 python -m alembic upgrade head

# Crear nueva migración
docker exec -it src-backend-1 python -m alembic revision --autogenerate -m "description"
```

---

## 🔐 Autenticación y Seguridad

### 🎫 JWT Tokens

```python
# Crear token
access_token = create_access_token(
    data={"sub": user.username, "user_id": str(user.id)},
    expires_delta=timedelta(minutes=30)
)

# Verificar token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
```

### 🛡️ CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📄 Procesamiento de Documentos

### 🔄 Flujo de Procesamiento

```python
@celery_app.task
def process_document(document_id: str):
    """Procesa un documento usando YOLO + Tesseract"""
    
    # 1. Cargar documento
    document = get_document_by_id(document_id)
    image = cv2.imread(document.file_path)
    
    # 2. Detección YOLO
    results = yolo_model(image)
    detections = results[0].boxes
    
    # 3. Extracción OCR por región
    extracted_text = {}
    for box in detections:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        roi = image[int(y1):int(y2), int(x1):int(x2)]
        
        # OCR con Tesseract
        text = pytesseract.image_to_string(roi, lang='spa')
        extracted_text[box.cls.item()] = text.strip()
    
    # 4. Estructuración de datos
    structured_data = structure_extracted_data(extracted_text)
    
    # 5. Actualizar base de datos
    update_document_data(document_id, extracted_text, structured_data)
```

### 🎯 Tipos de Documentos Soportados

- **INVOICE**: Facturas comerciales
- **DNI**: Documentos de identidad
- **RECEIPT**: Recibos y comprobantes
- **CONTRACT**: Contratos
- **OTHER**: Otros documentos

---

## 🤖 Modelos YOLO

### 📊 Configuración de Entrenamiento

```yaml
# configs/invoice_dataset.yaml
path: /app/datasets/invoices
train: images/train
val: images/val
test: images/test

nc: 10  # Número de clases
names: ['total', 'date', 'invoice_number', 'vendor', 'customer', 'item', 'quantity', 'price', 'tax', 'subtotal']
```

### 🚀 Scripts de Entrenamiento

#### Entrenamiento Básico
```bash
# Activar entorno de entrenamiento
cd backend
source yolo_training_env/bin/activate  # Linux/Mac
# o
yolo_training_env\Scripts\activate     # Windows

# Ejecutar entrenamiento
python scripts/quick_train_example.py
```

#### Entrenamiento Avanzado
```bash
# Sistema completo de entrenamiento
python scripts/setup_advanced_training.py
python scripts/complete_training_workflow.py
```

### 📈 Monitoreo de Entrenamiento

```bash
# TensorBoard
tensorboard --logdir=runs

# Weights & Biases
wandb login
python scripts/advanced_training_system.py
```

---

## 🚀 Deployment

### 🐳 Docker Compose

#### Levantar Sistema Completo
```bash
# Crear red Docker
docker network create ocr-network

# Levantar todos los servicios
docker-compose -f docker-compose.full.yml up -d

# Verificar estado
docker ps
```

#### Servicios Individuales
```bash
# Solo backend
docker-compose -f docker-compose.full.yml up -d backend db redis

# Solo frontend
docker-compose -f docker-compose.full.yml up -d frontend
```

### 🔧 Comandos Útiles

```bash
# Ver logs
docker-compose -f docker-compose.full.yml logs -f backend

# Reiniciar servicio
docker-compose -f docker-compose.full.yml restart backend

# Ejecutar comando en contenedor
docker exec -it src-backend-1 python create_user_in_container.py

# Backup de base de datos
docker exec src-db-1 pg_dump -U ocr_user ocr_database > backup.sql

# Restore de base de datos
docker exec -i src-db-1 psql -U ocr_user ocr_database < backup.sql
```

### 🌐 URLs de Acceso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Celery Flower**: http://localhost:5555
- **PgAdmin**: http://localhost:5050

---

## 🔧 Troubleshooting

### ❌ Problemas Comunes

#### 1. Error de Puerto Ocupado
```bash
# Verificar puertos en uso
netstat -an | findstr :3000
netstat -an | findstr :8000

# Detener servicios conflictivos
docker-compose -f docker-compose.full.yml down
```

#### 2. Error de Conexión a Base de Datos
```bash
# Verificar logs de base de datos
docker logs src-db-1

# Reiniciar base de datos
docker-compose -f docker-compose.full.yml restart db
```

#### 3. Error de Autenticación
```bash
# Crear usuario de prueba
docker exec -it src-backend-1 python create_user_in_container.py

# Verificar token
curl -X POST "http://localhost:8000/api/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword"
```

#### 4. Error de Nginx (Frontend)
```bash
# Verificar configuración
docker exec -it src-frontend-1 cat /etc/nginx/conf.d/default.conf

# Rebuild frontend
docker-compose -f docker-compose.full.yml build frontend
docker-compose -f docker-compose.full.yml up -d frontend
```

#### 5. Error de OCR Worker
```bash
# Verificar logs del worker
docker logs src-ocr-worker-1

# Reiniciar worker
docker-compose -f docker-compose.full.yml restart ocr-worker
```

### 📊 Monitoreo del Sistema

#### Métricas de Performance
```bash
# Uso de recursos
docker stats

# Logs en tiempo real
docker-compose -f docker-compose.full.yml logs -f

# Estado de servicios
docker-compose -f docker-compose.full.yml ps
```

#### Health Checks
```bash
# API Health
curl http://localhost:8000/health

# Database Health
docker exec src-db-1 pg_isready -U ocr_user

# Redis Health
docker exec src-redis-1 redis-cli ping
```

---

## 🎯 Mejores Prácticas

### 💻 Desarrollo

1. **Usar entornos virtuales** para desarrollo local
2. **Versionar modelos** YOLO entrenados
3. **Implementar tests** unitarios y de integración
4. **Documentar APIs** con OpenAPI/Swagger
5. **Usar linting** (ESLint, Black, isort)

### 🔒 Seguridad

1. **Rotar secrets** JWT regularmente
2. **Validar inputs** en todas las APIs
3. **Usar HTTPS** en producción
4. **Implementar rate limiting**
5. **Auditar logs** de acceso

### 🚀 Performance

1. **Cachear resultados** de OCR
2. **Optimizar imágenes** antes del procesamiento
3. **Usar índices** en base de datos
4. **Implementar paginación** en listas
5. **Monitorear memoria** del worker

---

## 📞 Soporte

Para soporte técnico o reportar bugs:

1. **Issues**: Crear issue en el repositorio
2. **Logs**: Incluir logs relevantes
3. **Configuración**: Especificar entorno y versiones
4. **Reproducción**: Describir pasos para reproducir

---

**Versión**: 1.0.0  
**Última actualización**: Enero 2025  
**Mantenido por**: Equipo de Desarrollo OCR

