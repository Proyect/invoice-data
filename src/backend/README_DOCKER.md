# 🐳 Despliegue con Docker - Backend OCR

## 📋 Requisitos Previos

- **Docker Desktop** instalado y funcionando
- **Git** (para clonar el repositorio)
- Al menos **4GB de RAM** disponible
- **10GB de espacio en disco** libre

## 🚀 Inicio Rápido

### 1. Preparar el entorno
```bash
# Navegar al directorio del backend
cd src/backend

# Copiar configuración de Docker
copy .env.docker .env

# (Opcional) Editar .env para personalizar configuración
```

### 2. Iniciar con Docker Compose
```bash
# Opción 1: Usar el script automatizado (Windows)
start_docker.bat

# Opción 2: Comandos manuales
docker compose up --build -d
```

### 3. Verificar que todo funciona
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Celery Flower**: http://localhost:5555
- **Base de datos**: localhost:5432
- **Redis**: localhost:6379

## 🏗️ Arquitectura Docker

### Servicios Incluidos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `api` | 8000 | FastAPI backend principal |
| `celery_worker` | - | Worker para procesamiento OCR |
| `celery_flower` | 5555 | Monitoreo de tareas Celery |
| `db` | 5432 | PostgreSQL database |
| `redis` | 6379 | Cola de mensajes y cache |

### Volúmenes Persistentes

- `postgres_data`: Datos de la base de datos
- `shared_storage`: Documentos subidos
- `model_storage`: Modelos YOLO entrenados

## 🔧 Comandos Útiles

### Gestión de Contenedores
```bash
# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f api
docker compose logs -f celery_worker

# Reiniciar un servicio
docker compose restart api

# Detener todos los servicios
docker compose down

# Detener y eliminar volúmenes
docker compose down -v
```

### Desarrollo
```bash
# Reconstruir después de cambios en código
docker compose up --build

# Ejecutar comandos dentro del contenedor
docker compose exec api bash
docker compose exec api python manage.py shell

# Ver estado de los contenedores
docker compose ps
```

### Base de Datos
```bash
# Conectar a PostgreSQL
docker compose exec db psql -U postgres -d invoice_db

# Backup de la base de datos
docker compose exec db pg_dump -U postgres invoice_db > backup.sql

# Restaurar backup
docker compose exec -T db psql -U postgres invoice_db < backup.sql
```

## 🎯 Entrenamiento de Modelos YOLO

### Preparar datos de entrenamiento
```bash
# Ejecutar dentro del contenedor API
docker compose exec api python scripts/train_detector.py --type invoice --setup
docker compose exec api python scripts/train_detector.py --type dni --setup
```

### Entrenar modelos (requiere dataset)
```bash
# Entrenar modelo para facturas
docker compose exec api python scripts/train_detector.py --type invoice --epochs 50

# Entrenar modelo para DNI
docker compose exec api python scripts/train_detector.py --type dni --epochs 50
```

## 🐛 Solución de Problemas

### Error: Puerto ya en uso
```bash
# Verificar qué está usando el puerto
netstat -ano | findstr :8000

# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar 8000 por 8001
```

### Error: Memoria insuficiente
```bash
# Reducir workers de Celery en docker-compose.yml
command: celery -A ocr_worker.celery_app worker --loglevel=info --concurrency=1
```

### Error: Modelos YOLO no encontrados
```bash
# Verificar que los modelos estén en la carpeta correcta
ls models/yolo_models/

# Copiar modelo genérico si es necesario
docker compose exec api cp models/yolo_models/yolov8n.pt models/yolo_models/invoice_yolov8.pt
```

### Logs útiles para debugging
```bash
# Ver logs de todos los servicios
docker compose logs

# Ver logs con timestamps
docker compose logs -t

# Seguir logs en tiempo real
docker compose logs -f --tail=100
```

## 🔒 Configuración de Producción

### Variables de entorno importantes
```env
# Cambiar en producción
SECRET_KEY_JWT=tu_clave_super_secreta_aqui
POSTGRES_PASSWORD=password_seguro_aqui

# Configurar dominio
ALLOWED_HOSTS=tu-dominio.com,localhost

# Configurar CORS si es necesario
CORS_ORIGINS=https://tu-frontend.com
```

### Optimizaciones para producción
```yaml
# En docker-compose.yml
api:
  command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
  
celery_worker:
  command: celery -A ocr_worker.celery_app worker --loglevel=warning --concurrency=4
```

## 📊 Monitoreo

### Celery Flower Dashboard
- URL: http://localhost:5555
- Monitorea tareas en tiempo real
- Ve estadísticas de workers
- Administra tareas pendientes

### Health Checks
```bash
# Verificar salud de la API
curl http://localhost:8000/

# Verificar salud de Redis
docker compose exec redis redis-cli ping

# Verificar salud de PostgreSQL
docker compose exec db pg_isready -U postgres
```

## 🚨 Backup y Restauración

### Backup completo
```bash
# Crear backup de datos
docker compose exec db pg_dump -U postgres invoice_db > db_backup.sql
docker compose exec api tar -czf storage_backup.tar.gz /app/uploaded_documents_local
```

### Restauración
```bash
# Restaurar base de datos
docker compose exec -T db psql -U postgres invoice_db < db_backup.sql

# Restaurar archivos
docker compose exec api tar -xzf storage_backup.tar.gz -C /app/
```

## 🎉 ¡Listo!

Tu backend OCR está ahora funcionando completamente en Docker con:
- ✅ API FastAPI con documentación automática
- ✅ Base de datos PostgreSQL
- ✅ Cola de tareas con Celery y Redis
- ✅ Procesamiento OCR con YOLO + Tesseract
- ✅ Monitoreo con Flower
- ✅ Volúmenes persistentes
- ✅ Health checks y restart automático

Para entrenar modelos YOLO específicos, necesitarás agregar datasets etiquetados a las carpetas correspondientes.
