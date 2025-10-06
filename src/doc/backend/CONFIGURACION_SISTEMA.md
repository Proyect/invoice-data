# ⚙️ Configuración del Sistema - OCR Document Processor

## 📋 Tabla de Contenidos
1. [Configuración General](#configuración-general)
2. [Variables de Entorno](#variables-de-entorno)
3. [Configuración de Base de Datos](#configuración-de-base-de-datos)
4. [Configuración de Redis](#configuración-de-redis)
5. [Configuración JWT](#configuración-jwt)
6. [Configuración de Almacenamiento](#configuración-de-almacenamiento)
7. [Configuración de Modelos YOLO](#configuración-de-modelos-yolo)
8. [Configuración de CORS](#configuración-de-cors)
9. [Configuración de Nginx](#configuración-de-nginx)
10. [Monitoreo y Logs](#monitoreo-y-logs)

---

## 🔧 Configuración General

### 🌐 URLs del Sistema

```yaml
# URLs principales
FRONTEND_URL: "http://localhost:3000"
BACKEND_URL: "http://localhost:8000"
API_DOCS_URL: "http://localhost:8000/docs"
FLOWER_URL: "http://localhost:5555"

# URLs de desarrollo
FRONTEND_DEV_URL: "http://localhost:3000"
BACKEND_DEV_URL: "http://localhost:8000"
```

### 🐳 Configuración Docker

```yaml
# docker-compose.full.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ocr_database
      POSTGRES_USER: ocr_user
      POSTGRES_PASSWORD: your_secure_password_here
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://ocr_user:your_secure_password_here@db:5432/ocr_database
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
```

---

## 🔑 Variables de Entorno

### 🐍 Backend (.env)

```env
# Base de Datos PostgreSQL
POSTGRES_DB=ocr_database
POSTGRES_USER=ocr_user
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://ocr_user:your_secure_password_here@db:5432/ocr_database

# Redis Cache/Queue
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://redis:6379/0

# JWT Authentication
SECRET_KEY_JWT=your_super_secret_jwt_key_here_make_it_long_and_random
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Almacenamiento
LOCAL_STORAGE_PATH=/app/uploaded_documents_local
YOLO_MODELS_PATH=/app/models/yolo_models

# Configuración de la aplicación
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Configuración de archivos
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=[".jpg", ".jpeg", ".png", ".pdf"]

# Configuración de procesamiento
OCR_LANGUAGE=spa
YOLO_CONFIDENCE_THRESHOLD=0.5
YOLO_IOU_THRESHOLD=0.45
```

### ⚛️ Frontend (.env.local)

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws

# Build Configuration
GENERATE_SOURCEMAP=false
REACT_APP_VERSION=1.0.0

# Feature Flags
REACT_APP_ENABLE_DEBUG=false
REACT_APP_ENABLE_ANALYTICS=false

# External Services
REACT_APP_GOOGLE_ANALYTICS_ID=
REACT_APP_SENTRY_DSN=
```

---

## 🗄️ Configuración de Base de Datos

### 📊 PostgreSQL

```sql
-- Configuración de base de datos
CREATE DATABASE ocr_database;
CREATE USER ocr_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE ocr_database TO ocr_user;

-- Configuraciones de rendimiento
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### 🔄 Migraciones

```python
# alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://ocr_user:your_secure_password_here@localhost:5432/ocr_database

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 88 REVISION_SCRIPT_FILENAME
```

---

## 🔴 Configuración de Redis

### ⚙️ Redis Configuration

```conf
# redis.conf
port 6379
bind 0.0.0.0
protected-mode no
save 900 1
save 300 10
save 60 10000

# Memory configuration
maxmemory 256mb
maxmemory-policy allkeys-lru

# Logging
loglevel notice
logfile ""

# Persistence
appendonly yes
appendfsync everysec
```

### 🔄 Celery Configuration

```python
# celery_config.py
from celery import Celery

celery_app = Celery(
    "ocr_worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["ocr_worker.worker"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)
```

---

## 🔐 Configuración JWT

### 🎫 JWT Settings

```python
# config.py
import os
from datetime import timedelta

# JWT Configuration
SECRET_KEY_JWT = os.getenv("SECRET_KEY_JWT", "your_super_secret_jwt_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Token expiration
ACCESS_TOKEN_EXPIRE_DELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE_DELTA = timedelta(days=7)

# Password hashing
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

### 🛡️ Security Middleware

```python
# security.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

---

## 💾 Configuración de Almacenamiento

### 📁 File Storage

```python
# storage_config.py
import os
from pathlib import Path

# Storage paths
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "/app/uploaded_documents_local")
YOLO_MODELS_PATH = os.getenv("YOLO_MODELS_PATH", "/app/models/yolo_models")

# Create directories
Path(LOCAL_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
Path(YOLO_MODELS_PATH).mkdir(parents=True, exist_ok=True)

# File upload configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
```

### 🔒 File Permissions

```bash
# Set proper permissions
chmod 755 /app/uploaded_documents_local
chmod 755 /app/models/yolo_models
chown -R app:app /app/uploaded_documents_local
chown -R app:app /app/models/yolo_models
```

---

## 🤖 Configuración de Modelos YOLO

### 📊 Model Configuration

```yaml
# configs/invoice_dataset.yaml
path: /app/datasets/invoices
train: images/train
val: images/val
test: images/test

nc: 10  # number of classes
names: ['total', 'date', 'invoice_number', 'vendor', 'customer', 'item', 'quantity', 'price', 'tax', 'subtotal']

# Training parameters
epochs: 100
batch: 16
imgsz: 640
device: 0  # GPU device
workers: 8

# Optimization
optimizer: AdamW
lr0: 0.01
weight_decay: 0.0005
momentum: 0.937

# Data augmentation
hsv_h: 0.015
hsv_s: 0.7
hsv_v: 0.4
degrees: 0.0
translate: 0.1
scale: 0.5
shear: 0.0
perspective: 0.0
flipud: 0.0
fliplr: 0.5
mosaic: 1.0
mixup: 0.0
copy_paste: 0.0
```

### 🎯 Model Loading

```python
# model_loader.py
from ultralytics import YOLO
import torch

class ModelLoader:
    def __init__(self):
        self.model_path = "/app/models/yolo_models/best.pt"
        self.model = None
        
    def load_model(self):
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
            
        self.model = YOLO(self.model_path)
        self.model.to(device)
        return self.model
```

---

## 🌐 Configuración de CORS

### ⚙️ CORS Settings

```python
# cors_config.py
from fastapi.middleware.cors import CORSMiddleware

# CORS configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # Development
]

CORS_METHODS = [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
    "PATCH",
]

CORS_HEADERS = [
    "Accept",
    "Accept-Language",
    "Content-Language",
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "Origin",
    "Access-Control-Request-Method",
    "Access-Control-Request-Headers",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
    expose_headers=["*"],
    max_age=3600,
)
```

---

## 🌐 Configuración de Nginx

### 📄 Nginx Config

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Static files
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

---

## 📊 Monitoreo y Logs

### 📝 Logging Configuration

```python
# logging_config.py
import logging
import sys
from pathlib import Path

# Create logs directory
logs_dir = Path("/app/logs")
logs_dir.mkdir(exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(logs_dir / "app.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# Specific loggers
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

# Celery logging
celery_logger = logging.getLogger("celery")
celery_logger.setLevel(logging.INFO)
```

### 📈 Health Checks

```python
# health_check.py
from fastapi import FastAPI
import psycopg2
import redis

app = FastAPI()

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Database check
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        status["services"]["database"] = "healthy"
    except Exception as e:
        status["services"]["database"] = f"unhealthy: {str(e)}"
        status["status"] = "unhealthy"
    
    # Redis check
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        r.ping()
        status["services"]["redis"] = "healthy"
    except Exception as e:
        status["services"]["redis"] = f"unhealthy: {str(e)}"
        status["status"] = "unhealthy"
    
    return status
```

---

## 🔧 Comandos de Configuración

### 🚀 Startup Commands

```bash
# Create Docker network
docker network create ocr-network

# Start all services
docker-compose -f docker-compose.full.yml up -d

# Check service status
docker-compose -f docker-compose.full.yml ps

# View logs
docker-compose -f docker-compose.full.yml logs -f
```

### 🔄 Maintenance Commands

```bash
# Database backup
docker exec src-db-1 pg_dump -U ocr_user ocr_database > backup_$(date +%Y%m%d).sql

# Database restore
docker exec -i src-db-1 psql -U ocr_user ocr_database < backup.sql

# Clear Redis cache
docker exec src-redis-1 redis-cli FLUSHALL

# Restart services
docker-compose -f docker-compose.full.yml restart backend
docker-compose -f docker-compose.full.yml restart frontend
```

### 🧹 Cleanup Commands

```bash
# Remove unused containers
docker container prune -f

# Remove unused images
docker image prune -f

# Remove unused volumes
docker volume prune -f

# Complete cleanup
docker system prune -af
```

---

**Versión**: 1.0.0  
**Última actualización**: Enero 2025  
**Mantenido por**: Equipo de Desarrollo OCR

