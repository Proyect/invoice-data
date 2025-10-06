# 🔧 Manual Técnico - Deployment y Configuración

**Versión**: 1.0  
**Fecha**: Enero 2025  
**Para**: Administradores de sistema y DevOps  

---

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación Local](#instalación-local)
3. [Configuración de Producción](#configuración-de-producción)
4. [Docker Deployment](#docker-deployment)
5. [Configuración de Base de Datos](#configuración-de-base-de-datos)
6. [Configuración de Redis](#configuración-de-redis)
7. [Configuración de Tesseract](#configuración-de-tesseract)
8. [Configuración de Nginx](#configuración-de-nginx)
9. [Monitoreo y Logs](#monitoreo-y-logs)
10. [Backup y Recuperación](#backup-y-recuperación)
11. [Escalabilidad](#escalabilidad)
12. [Seguridad](#seguridad)

---

## 💻 Requisitos del Sistema

### Requisitos Mínimos

#### Servidor de Aplicación
- **CPU**: 4 cores (2.4 GHz)
- **RAM**: 8 GB
- **Almacenamiento**: 100 GB SSD
- **Sistema Operativo**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+

#### Base de Datos
- **PostgreSQL**: 12+
- **RAM**: 4 GB
- **Almacenamiento**: 50 GB SSD

#### Cache
- **Redis**: 6+
- **RAM**: 2 GB

### Requisitos Recomendados

#### Servidor de Aplicación
- **CPU**: 8 cores (3.0 GHz)
- **RAM**: 16 GB
- **Almacenamiento**: 500 GB SSD
- **GPU**: NVIDIA GTX 1060+ (opcional, para YOLO)

#### Base de Datos
- **PostgreSQL**: 13+
- **RAM**: 8 GB
- **Almacenamiento**: 200 GB SSD

#### Cache
- **Redis**: 6+
- **RAM**: 4 GB

---

## 🏠 Instalación Local

### 1. Preparar el Entorno

#### Ubuntu/Debian
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3.9 python3.9-pip python3.9-venv \
    postgresql postgresql-contrib redis-server \
    tesseract-ocr tesseract-ocr-spa \
    libgl1-mesa-glx libglib2.0-0 \
    nginx git curl

# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs
```

#### CentOS/RHEL
```bash
# Actualizar sistema
sudo yum update -y

# Instalar EPEL
sudo yum install -y epel-release

# Instalar dependencias
sudo yum install -y python39 python39-pip postgresql-server \
    redis tesseract tesseract-langpack-spa \
    nginx git curl

# Instalar Node.js
curl -fsSL https://rpm.nodesource.com/setup_16.x | sudo bash -
sudo yum install -y nodejs
```

#### Windows
```powershell
# Instalar Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Instalar dependencias
choco install python postgresql redis nginx nodejs git -y

# Instalar Tesseract
choco install tesseract -y
```

### 2. Configurar Base de Datos

```bash
# Inicializar PostgreSQL
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Crear usuario y base de datos
sudo -u postgres psql
```

```sql
-- En psql
CREATE USER ocr_user WITH PASSWORD 'secure_password';
CREATE DATABASE ocr_db OWNER ocr_user;
GRANT ALL PRIVILEGES ON DATABASE ocr_db TO ocr_user;
\q
```

### 3. Configurar Redis

```bash
# Configurar Redis
sudo systemctl enable redis
sudo systemctl start redis

# Verificar que funciona
redis-cli ping
# Debe responder: PONG
```

### 4. Instalar Aplicación

```bash
# Clonar repositorio
git clone https://github.com/your-org/ocr-system.git
cd ocr-system

# Configurar backend
cd backend
python3.9 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
python setup_local.py
```

```bash
# Configurar frontend
cd ../frontend
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con la URL del backend

# Construir para producción
npm run build
```

### 5. Ejecutar Aplicación

```bash
# Backend
cd backend
source venv/bin/activate
python main.py

# Frontend (en otra terminal)
cd frontend
npm start
```

---

## 🚀 Configuración de Producción

### 1. Configuración del Servidor

#### Variables de Entorno de Producción
```env
# .env.production
DEBUG=False
ENVIRONMENT=production

# Base de datos
DATABASE_URL=postgresql://ocr_user:secure_password@localhost:5432/ocr_db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-super-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Tesseract
TESSERACT_PATH=/usr/bin/tesseract

# Almacenamiento
UPLOAD_DIR=/var/www/ocr-system/uploads
MAX_FILE_SIZE=10485760  # 10MB

# CORS
ALLOWED_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ocr-system/app.log
```

#### Configuración de Sistema
```bash
# Crear usuario para la aplicación
sudo useradd -r -s /bin/false ocr-app
sudo mkdir -p /var/www/ocr-system
sudo chown -R ocr-app:ocr-app /var/www/ocr-system

# Crear directorios necesarios
sudo mkdir -p /var/log/ocr-system
sudo mkdir -p /var/www/ocr-system/uploads
sudo chown -R ocr-app:ocr-app /var/log/ocr-system
sudo chown -R ocr-app:ocr-app /var/www/ocr-system/uploads
```

### 2. Configuración de Nginx

```nginx
# /etc/nginx/sites-available/ocr-system
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Frontend
    location / {
        root /var/www/ocr-system/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # File upload size
        client_max_body_size 10M;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/ocr-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Configuración de Systemd

#### Servicio Backend
```ini
# /etc/systemd/system/ocr-backend.service
[Unit]
Description=OCR System Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=ocr-app
Group=ocr-app
WorkingDirectory=/var/www/ocr-system/backend
Environment=PATH=/var/www/ocr-system/backend/venv/bin
ExecStart=/var/www/ocr-system/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable ocr-backend
sudo systemctl start ocr-backend
```

---

## 🐳 Docker Deployment

### 1. Docker Compose para Producción

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://ocr_user:${DB_PASSWORD}@db:5432/ocr_db
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
    depends_on:
      - db
      - redis
    volumes:
      - uploads:/app/uploads
      - logs:/app/logs
    restart: unless-stopped
    networks:
      - ocr-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - ocr-network

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=ocr_db
      - POSTGRES_USER=ocr_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backup:/backup
    restart: unless-stopped
    networks:
      - ocr-network

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - ocr-network

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    networks:
      - ocr-network

volumes:
  postgres_data:
  redis_data:
  uploads:
  logs:

networks:
  ocr-network:
    driver: bridge
```

### 2. Dockerfile de Producción

#### Backend
```dockerfile
# backend/Dockerfile.prod
FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear usuario no-root
RUN useradd -r -s /bin/false ocr-app && \
    chown -R ocr-app:ocr-app /app
USER ocr-app

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend
```dockerfile
# frontend/Dockerfile.prod
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. Despliegue con Docker

```bash
# Crear archivo de variables de entorno
cat > .env.prod << EOF
DB_PASSWORD=your_secure_password
SECRET_KEY=your_super_secret_key
EOF

# Desplegar
docker-compose -f docker-compose.prod.yml up -d

# Verificar estado
docker-compose -f docker-compose.prod.yml ps
```

---

## 🗄️ Configuración de Base de Datos

### 1. Optimización de PostgreSQL

```sql
-- /etc/postgresql/13/main/postgresql.conf
# Memoria
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Conexiones
max_connections = 100
shared_preload_libraries = 'pg_stat_statements'

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# WAL
wal_level = replica
max_wal_size = 1GB
min_wal_size = 80MB
checkpoint_completion_target = 0.9
```

### 2. Índices de Base de Datos

```sql
-- Índices para optimizar consultas
CREATE INDEX CONCURRENTLY idx_documents_user_id ON documents(user_id);
CREATE INDEX CONCURRENTLY idx_documents_status ON documents(status);
CREATE INDEX CONCURRENTLY idx_documents_type ON documents(document_type);
CREATE INDEX CONCURRENTLY idx_documents_uploaded_at ON documents(uploaded_at);
CREATE INDEX CONCURRENTLY idx_extracted_data_document_id ON extracted_data(document_id);
CREATE INDEX CONCURRENTLY idx_extracted_data_field_name ON extracted_data(field_name);

-- Índice compuesto para consultas frecuentes
CREATE INDEX CONCURRENTLY idx_documents_user_status_type 
ON documents(user_id, status, document_type);
```

### 3. Backup Automático

```bash
#!/bin/bash
# /usr/local/bin/backup_ocr_db.sh

# Configuración
DB_NAME="ocr_db"
DB_USER="ocr_user"
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Crear backup
pg_dump -h localhost -U $DB_USER -d $DB_NAME \
    --format=custom \
    --compress=9 \
    --file="$BACKUP_DIR/ocr_db_$DATE.backup"

# Limpiar backups antiguos
find $BACKUP_DIR -name "ocr_db_*.backup" -mtime +$RETENTION_DAYS -delete

# Log
echo "$(date): Backup completed - ocr_db_$DATE.backup" >> /var/log/backup.log
```

```bash
# Agregar a crontab
# 0 2 * * * /usr/local/bin/backup_ocr_db.sh
```

---

## 🔴 Configuración de Redis

### 1. Configuración de Producción

```conf
# /etc/redis/redis.conf
# Memoria
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistencia
save 900 1
save 300 10
save 60 10000

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Seguridad
requirepass your_redis_password
bind 127.0.0.1

# Performance
tcp-keepalive 300
timeout 0
```

### 2. Monitoreo de Redis

```bash
# Instalar redis-tools
sudo apt install redis-tools

# Monitorear en tiempo real
redis-cli monitor

# Ver estadísticas
redis-cli info stats
```

---

## 🔍 Configuración de Tesseract

### 1. Instalación Completa

```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng

# CentOS/RHEL
sudo yum install tesseract tesseract-langpack-spa tesseract-langpack-eng

# Verificar instalación
tesseract --version
tesseract --list-langs
```

### 2. Configuración de Tesseract

```bash
# Crear directorio de configuración
sudo mkdir -p /etc/tesseract

# Configuración personalizada
cat > /etc/tesseract/tessdata_config << EOF
# Configuración Tesseract para OCR System
tessdata_dir_config = /usr/share/tesseract-ocr/4.00/tessdata
user_words_suffix = user-words
user_patterns_suffix = user-patterns
EOF
```

---

## 🌐 Configuración de Nginx

### 1. Configuración de Producción

```nginx
# /etc/nginx/nginx.conf
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # Configuración básica
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;

    # MIME types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=1r/s;

    # Include site configurations
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

### 2. Configuración de SSL

```bash
# Generar certificado SSL con Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 Monitoreo y Logs

### 1. Configuración de Logs

```python
# backend/config/logging.py
import logging
import logging.handlers
from pathlib import Path

def setup_logging():
    """Configura el sistema de logging"""
    
    # Crear directorio de logs
    log_dir = Path("/var/log/ocr-system")
    log_dir.mkdir(exist_ok=True)
    
    # Configuración del logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Handler para archivo
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
```

### 2. Monitoreo con Prometheus

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ocr-system'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
```

### 3. Alertas con Grafana

```yaml
# monitoring/grafana/alerts.yml
groups:
  - name: ocr-system
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
```

---

## 💾 Backup y Recuperación

### 1. Script de Backup Completo

```bash
#!/bin/bash
# /usr/local/bin/backup_ocr_system.sh

# Configuración
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Crear directorio de backup
mkdir -p $BACKUP_DIR/$DATE

# Backup de base de datos
pg_dump -h localhost -U ocr_user -d ocr_db \
    --format=custom \
    --compress=9 \
    --file="$BACKUP_DIR/$DATE/database.backup"

# Backup de archivos
tar -czf "$BACKUP_DIR/$DATE/uploads.tar.gz" /var/www/ocr-system/uploads

# Backup de configuración
tar -czf "$BACKUP_DIR/$DATE/config.tar.gz" \
    /etc/nginx/sites-available/ocr-system \
    /etc/systemd/system/ocr-backend.service \
    /var/www/ocr-system/backend/.env

# Backup de logs
tar -czf "$BACKUP_DIR/$DATE/logs.tar.gz" /var/log/ocr-system

# Limpiar backups antiguos
find $BACKUP_DIR -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;

# Log
echo "$(date): Full backup completed - $DATE" >> /var/log/backup.log
```

### 2. Script de Recuperación

```bash
#!/bin/bash
# /usr/local/bin/restore_ocr_system.sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_date>"
    echo "Available backups:"
    ls -la /backup/
    exit 1
fi

BACKUP_DATE=$1
BACKUP_DIR="/backup/$BACKUP_DATE"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "Restoring OCR System from backup: $BACKUP_DATE"

# Detener servicios
sudo systemctl stop ocr-backend
sudo systemctl stop nginx

# Restaurar base de datos
pg_restore -h localhost -U ocr_user -d ocr_db \
    --clean --if-exists \
    "$BACKUP_DIR/database.backup"

# Restaurar archivos
tar -xzf "$BACKUP_DIR/uploads.tar.gz" -C /

# Restaurar configuración
tar -xzf "$BACKUP_DIR/config.tar.gz" -C /

# Iniciar servicios
sudo systemctl start ocr-backend
sudo systemctl start nginx

echo "Restore completed successfully"
```

---

## 📈 Escalabilidad

### 1. Load Balancer con Nginx

```nginx
# /etc/nginx/conf.d/load-balancer.conf
upstream ocr_backend {
    least_conn;
    server 127.0.0.1:8000 weight=3;
    server 127.0.0.1:8001 weight=3;
    server 127.0.0.1:8002 weight=2;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://ocr_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 2. Horizontal Scaling con Docker Swarm

```yaml
# docker-stack.yml
version: '3.8'

services:
  backend:
    image: ocr-system/backend:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
    networks:
      - ocr-network

  frontend:
    image: ocr-system/frontend:latest
    deploy:
      replicas: 2
    networks:
      - ocr-network

  db:
    image: postgres:13
    deploy:
      replicas: 1
      placement:
        constraints: [node.role == manager]
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ocr-network

networks:
  ocr-network:
    driver: overlay

volumes:
  postgres_data:
```

### 3. Auto-scaling con Kubernetes

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ocr-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ocr-backend
  template:
    metadata:
      labels:
        app: ocr-backend
    spec:
      containers:
      - name: backend
        image: ocr-system/backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ocr-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ocr-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 🔒 Seguridad

### 1. Configuración de Firewall

```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH
sudo ufw allow ssh

# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir PostgreSQL (solo desde localhost)
sudo ufw allow from 127.0.0.1 to any port 5432

# Permitir Redis (solo desde localhost)
sudo ufw allow from 127.0.0.1 to any port 6379
```

### 2. Configuración de SSL/TLS

```nginx
# Configuración SSL avanzada
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/ssl/certs/ca-certificates.crt;
```

### 3. Configuración de Seguridad de Base de Datos

```sql
-- Configuración de seguridad PostgreSQL
-- /etc/postgresql/13/main/pg_hba.conf

# Solo conexiones locales
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5

# Denegar conexiones externas
host    all             all             0.0.0.0/0               reject
```

### 4. Monitoreo de Seguridad

```bash
# Instalar fail2ban
sudo apt install fail2ban

# Configurar fail2ban para Nginx
cat > /etc/fail2ban/jail.local << EOF
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📞 Soporte Técnico

### Contacto
- **Email**: devops@ocr-system.com
- **Slack**: #devops-support
- **GitHub**: [Repository Issues](https://github.com/your-org/ocr-system/issues)

### Documentación Adicional
- [API Documentation](http://localhost:8000/docs)
- [Database Schema](docs/database-schema.md)
- [Security Guidelines](docs/security.md)
- [Performance Tuning](docs/performance.md)

---

**Última actualización**: Enero 2025  
**Versión del manual**: 1.0  
**Mantenido por**: Equipo de DevOps

