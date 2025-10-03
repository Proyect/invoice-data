# 🔐 CREDENCIALES DE CONEXIÓN A LA BASE DE DATOS

## 📊 **POSTGRESQL - Base de Datos Principal**

### **Configuración de Conexión:**
```bash
# Host y Puerto
HOST: localhost
PUERTO: 5432

# Credenciales de Acceso
USUARIO: ocr_user
CONTRASEÑA: dev_password_123
BASE_DE_DATOS: ocr_database
```

### **URL de Conexión Completa:**
```
postgresql://ocr_user:dev_password_123@localhost:5432/ocr_database
```

### **Conexión desde Aplicaciones:**
```python
# Python (psycopg2)
DATABASE_URL = "postgresql://ocr_user:dev_password_123@localhost:5432/ocr_database"

# SQLAlchemy
engine = create_engine("postgresql://ocr_user:dev_password_123@localhost:5432/ocr_database")
```

## 🔴 **REDIS - Cola de Tareas**

### **Configuración de Conexión:**
```bash
# Host y Puerto
HOST: localhost
PUERTO: 6379
BASE_DE_DATOS: 0
```

### **URL de Conexión:**
```
redis://localhost:6379/0
```

## 🐳 **DOCKER - Configuración de Contenedores**

### **Variables de Entorno para Docker:**
```bash
# Base de Datos
POSTGRES_DB=ocr_database
POSTGRES_USER=ocr_user
POSTGRES_PASSWORD=dev_password_123
DATABASE_URL=postgresql://ocr_user:dev_password_123@db:5432/ocr_database

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY_JWT=ocr_super_secret_jwt_key_2024_make_it_long_and_random_for_development
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Almacenamiento
LOCAL_STORAGE_PATH=/app/uploaded_documents_local
YOLO_MODELS_PATH=/app/models/yolo_models
```

## 🚀 **INSTRUCCIONES DE CONEXIÓN**

### **1. Crear archivo .env en backend:**
```bash
# Copiar el contenido de env.example y actualizar las credenciales
cp env.example .env
```

### **2. Actualizar las credenciales en .env:**
```bash
POSTGRES_PASSWORD=ocr_secure_password_2024
DATABASE_URL=postgresql://ocr_user:ocr_secure_password_2024@localhost:5432/ocr_database
SECRET_KEY_JWT=ocr_super_secret_jwt_key_2024_make_it_long_and_random_for_development
```

### **3. Iniciar la base de datos:**
```bash
# Con Docker
docker-compose up -d db redis

# O instalar PostgreSQL localmente
# Usuario: ocr_user
# Contraseña: dev_password_123
# Base de datos: ocr_database
```

## 🔧 **HERRAMIENTAS DE CONEXIÓN**

### **pgAdmin (Interfaz Gráfica):**
- Host: localhost
- Puerto: 5432
- Usuario: ocr_user
- Contraseña: ocr_secure_password_2024
- Base de datos: ocr_database

### **psql (Línea de Comandos):**
```bash
psql -h localhost -p 5432 -U ocr_user -d ocr_database
# Contraseña: dev_password_123
```

### **DBeaver/DataGrip:**
- Driver: PostgreSQL
- Host: localhost
- Puerto: 5432
- Usuario: ocr_user
- Contraseña: ocr_secure_password_2024
- Base de datos: ocr_database

## ⚠️ **NOTAS IMPORTANTES**

1. **Seguridad**: Cambia las contraseñas en producción
2. **Puertos**: Asegúrate de que 5432 (PostgreSQL) y 6379 (Redis) estén disponibles
3. **Firewall**: Configura el firewall para permitir conexiones a estos puertos
4. **Backup**: Configura respaldos regulares de la base de datos

## 🎯 **CREDENCIALES DE PRUEBA DEL SISTEMA**

### **Login en la Aplicación:**
- Usuario: `testuser`
- Contraseña: `testpassword`

### **Base de Datos:**
- Usuario: `ocr_user`
- Contraseña: `ocr_secure_password_2024`
