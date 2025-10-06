# Guía de Pruebas del Sistema OCR

Este documento describe cómo ejecutar las pruebas del sistema OCR tanto en entorno local como con contenedores Docker.

## 📋 Resumen de Pruebas

El sistema incluye pruebas completas para:

- **Frontend**: Compilación, componentes, integración
- **Backend Local**: API, base de datos, modelos, servicios
- **Backend Docker**: Contenedores, redes, volúmenes, servicios
- **Integración**: Comunicación frontend-backend, CORS, autenticación

## 🚀 Ejecución Rápida

### Todas las Pruebas (Recomendado)
```bash
run_all_tests.bat all
```

### Pruebas Específicas
```bash
# Solo pruebas locales
run_all_tests.bat local

# Solo pruebas Docker
run_all_tests.bat docker

# Solo pruebas frontend
run_all_tests.bat frontend
```

## 🏠 Pruebas Locales

### Backend Local
```bash
run_local_tests.bat
```

**Verifica:**
- Entorno Python 3.11+
- Dependencias instaladas
- Conexión a base de datos
- Carga de modelos YOLO
- Servicios OCR
- Permisos de archivos
- Pruebas unitarias

### Frontend Local
```bash
cd frontend
python test_frontend_system.py
```

**Verifica:**
- Node.js y npm
- Dependencias React
- Compilación TypeScript
- Proceso de build
- Linting (si configurado)
- Componentes principales
- Variables de entorno

## 🐳 Pruebas Docker

### Sistema Completo con Docker
```bash
run_docker_tests.bat
```

**Verifica:**
- Docker y Docker Compose
- Imágenes necesarias
- Contenedores corriendo
- Redes Docker
- Volúmenes persistentes
- Base de datos PostgreSQL
- Redis
- Celery Worker
- Celery Flower
- API endpoints
- Integración completa

## 🔗 Pruebas de Integración

### Frontend-Backend
```bash
python test_integration.py
```

**Verifica:**
- Salud del backend
- Accesibilidad del frontend
- Flujo de autenticación
- Subida de documentos
- Documentación API
- Configuración CORS
- Conectividad de base de datos
- Manejo de errores

## 📊 Interpretación de Resultados

### Estados de Prueba
- ✅ **PASS**: Prueba exitosa
- ❌ **FAIL**: Prueba falló
- ⚠️ **WARNING**: Advertencia (no crítico)

### Códigos de Salida
- `0`: Todas las pruebas pasaron
- `1`: Una o más pruebas fallaron

## 🛠️ Solución de Problemas

### Problemas Comunes

#### 1. Backend no responde
```bash
# Verificar que el servidor esté corriendo
curl http://localhost:8000/health

# Iniciar servidor manualmente
cd backend
python run_local.py
```

#### 2. Frontend no compila
```bash
# Limpiar e instalar dependencias
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### 3. Docker no inicia
```bash
# Verificar Docker Desktop
docker --version
docker info

# Limpiar contenedores
docker-compose -f docker-compose.full.yml down
docker system prune -f
```

#### 4. Base de datos no conecta
```bash
# Verificar PostgreSQL
docker ps | grep postgres

# Reiniciar base de datos
docker-compose -f docker-compose.full.yml restart db
```

### Logs de Depuración

#### Backend
```bash
# Logs del servidor
cd backend
python run_local.py

# Logs de Docker
docker-compose -f docker-compose.full.yml logs backend
```

#### Frontend
```bash
# Logs de desarrollo
cd frontend
npm start

# Logs de build
npm run build
```

#### Docker
```bash
# Logs de todos los servicios
docker-compose -f docker-compose.full.yml logs

# Logs de un servicio específico
docker-compose -f docker-compose.full.yml logs backend
```

## 📁 Estructura de Archivos de Prueba

```
src/
├── run_all_tests.bat              # Script maestro
├── run_local_tests.bat            # Pruebas locales
├── run_docker_tests.bat           # Pruebas Docker
├── test_integration.py            # Pruebas de integración
├── backend/
│   ├── test_local_system.py       # Pruebas backend local
│   ├── test_docker_system.py      # Pruebas backend Docker
│   └── tests/                     # Pruebas unitarias
└── frontend/
    └── test_frontend_system.py    # Pruebas frontend
```

## 🔧 Configuración Avanzada

### Variables de Entorno

#### Backend (.env)
```env
DATABASE_URL=postgresql://ocr_user:password@localhost:5432/ocr_database
SECRET_KEY_JWT=your_secret_key
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### Frontend (.env.local)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
GENERATE_SOURCEMAP=false
```

### Puertos por Defecto
- Frontend: 3000
- Backend API: 8000
- PostgreSQL: 5432
- Redis: 6379
- Flower: 5555

## 📈 Métricas de Rendimiento

Las pruebas incluyen verificaciones de:
- Tiempo de respuesta de API
- Tiempo de compilación
- Uso de memoria
- Conectividad de red

## 🚨 Alertas y Notificaciones

El sistema de pruebas genera alertas para:
- Servicios no disponibles
- Errores de configuración
- Problemas de conectividad
- Fallos en dependencias

## 📝 Reportes

Los resultados se muestran en consola con:
- Resumen de pruebas pasadas/fallidas
- Porcentaje de éxito
- Detalles de errores
- Recomendaciones de solución

## 🔄 Automatización

### CI/CD
Los scripts pueden integrarse en pipelines de CI/CD:

```yaml
# Ejemplo para GitHub Actions
- name: Run Tests
  run: |
    run_all_tests.bat all
```

### Programación
Para ejecutar pruebas automáticamente:

```bash
# Windows Task Scheduler
schtasks /create /tn "OCR Tests" /tr "C:\path\to\run_all_tests.bat all" /sc daily
```

## 📞 Soporte

Para problemas o preguntas:
1. Revisar logs de error
2. Verificar configuración
3. Ejecutar pruebas individuales
4. Consultar documentación técnica

---

**Nota**: Este sistema de pruebas está diseñado para verificar la funcionalidad completa del sistema OCR en múltiples entornos, asegurando la calidad y confiabilidad del software.

