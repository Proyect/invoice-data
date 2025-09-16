# 🐳 Frontend OCR - Guía Docker

## 📋 Prerrequisitos

- Docker Desktop instalado y ejecutándose
- Puerto 3000 disponible

## 🚀 Inicio Rápido

### Opción 1: Producción (Recomendado)
```bash
# Construir y ejecutar en modo producción
docker build -t ocr-frontend .
docker run -d --name ocr-frontend -p 3000:80 ocr-frontend
```

### Opción 2: Desarrollo con Hot Reload
```bash
# Construir y ejecutar en modo desarrollo
docker build -f Dockerfile.dev -t ocr-frontend-dev .
docker run -d --name ocr-frontend-dev -p 3000:3000 -v $(pwd):/app -v /app/node_modules ocr-frontend-dev
```

### Opción 3: Usar Scripts de Windows
```bash
# Para producción
start-docker.bat

# Para desarrollo
start-docker-dev.bat
```

## 🔧 Configuración

### Variables de Entorno
- `REACT_APP_API_URL`: URL del backend API (default: http://localhost:8000/api/v1)
- `CHOKIDAR_USEPOLLING`: Para hot reload en Docker (default: true)

### Puertos
- **3000**: Frontend (modo desarrollo)
- **80**: Frontend (modo producción)

## 📁 Estructura de Archivos Docker

```
frontend/
├── Dockerfile              # Imagen de producción
├── Dockerfile.dev          # Imagen de desarrollo
├── docker-compose.yml      # Orquestación de servicios
├── nginx.conf              # Configuración de Nginx
├── start-docker.bat        # Script de inicio producción
├── start-docker-dev.bat    # Script de inicio desarrollo
└── start-local.bat         # Script de inicio local (sin Docker)
```

## 🛠️ Comandos Útiles

### Construcción
```bash
# Imagen de producción
docker build -t ocr-frontend .

# Imagen de desarrollo
docker build -f Dockerfile.dev -t ocr-frontend-dev .
```

### Ejecución
```bash
# Producción
docker run -d --name ocr-frontend -p 3000:80 ocr-frontend

# Desarrollo
docker run -d --name ocr-frontend-dev -p 3000:3000 -v $(pwd):/app -v /app/node_modules ocr-frontend-dev
```

### Gestión de Contenedores
```bash
# Ver contenedores ejecutándose
docker ps

# Ver logs
docker logs ocr-frontend
docker logs ocr-frontend-dev

# Detener contenedor
docker stop ocr-frontend
docker stop ocr-frontend-dev

# Eliminar contenedor
docker rm ocr-frontend
docker rm ocr-frontend-dev

# Eliminar imagen
docker rmi ocr-frontend
docker rmi ocr-frontend-dev
```

## 🔍 Solución de Problemas

### Error: Puerto 3000 en uso
```bash
# Verificar qué proceso usa el puerto
netstat -ano | findstr :3000

# Detener proceso o usar otro puerto
docker run -d --name ocr-frontend -p 3001:80 ocr-frontend
```

### Error: Hot reload no funciona
```bash
# Asegurar que CHOKIDAR_USEPOLLING=true
docker run -d --name ocr-frontend-dev -p 3000:3000 -e CHOKIDAR_USEPOLLING=true -v $(pwd):/app -v /app/node_modules ocr-frontend-dev
```

### Error: No se conecta al backend
```bash
# Verificar que el backend esté ejecutándose en puerto 8000
curl http://localhost:8000

# Verificar variables de entorno
docker exec ocr-frontend env | grep REACT_APP
```

## 🌐 Acceso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

## 📝 Notas de Desarrollo

1. **Hot Reload**: Funciona correctamente en modo desarrollo
2. **Volúmenes**: El código se monta como volumen para desarrollo
3. **Nginx**: Configurado para SPA con fallback a index.html
4. **CORS**: Configurado para desarrollo local
5. **Compresión**: Habilitada para archivos estáticos

## 🔄 Integración con Backend

El frontend está configurado para conectarse automáticamente al backend en:
- **Desarrollo**: http://localhost:8000/api/v1
- **Producción**: Configurable via variable de entorno

## 📦 Optimizaciones

- **Multi-stage build**: Imagen de producción optimizada
- **Nginx**: Servidor web eficiente
- **Compresión gzip**: Archivos comprimidos
- **Cache headers**: Archivos estáticos cacheados

