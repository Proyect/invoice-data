# 🐳 Guía de Desarrollo con Docker

## 📊 Análisis de Contenedores

### ✅ **CONTENEDORES ÚTILES PARA DESARROLLO**

#### **1. Servicios Base (ESENCIALES)**
- **PostgreSQL (`db`)**: Base de datos principal
- **Redis (`redis`)**: Broker para Celery y cache

#### **2. Backend (ESENCIAL)**
- **API (`api`)**: Backend principal con hot reload
- **Celery Worker (`celery_worker`)**: Procesamiento OCR asíncrono

#### **3. Monitoreo (OPCIONAL)**
- **Celery Flower (`celery_flower`)**: Interfaz web para debugging

### ❌ **CONTENEDORES INNECESARIOS PARA DESARROLLO**

#### **Frontend en Docker**
- **Razón**: Para desarrollo es mejor usar `npm start` directamente
- **Ventajas del desarrollo nativo**:
  - Hot reload más rápido
  - Debugging más fácil
  - Menos consumo de recursos
  - Herramientas de desarrollo nativas

## 🚀 **Configuraciones Recomendadas**

### **Opción 1: Desarrollo Híbrido (RECOMENDADO)**
```bash
# Solo servicios base en Docker
docker-compose -f docker-compose.dev.yml up -d db redis

# Backend y Frontend locales
cd backend && python main.py
cd frontend && npm start
```

### **Opción 2: Todo en Docker**
```bash
# Sistema completo en Docker (sin frontend)
docker-compose -f docker-compose.dev.yml up
```

### **Opción 3: Producción**
```bash
# Sistema completo para producción
docker-compose -f docker-compose.full.yml up
```

## 📁 **Archivos Creados**

1. **`docker-compose.dev.yml`**: Configuración optimizada para desarrollo
2. **`start-dev-docker.bat`**: Script para iniciar todo en Docker
3. **`start-dev-local.bat`**: Script para desarrollo híbrido

## 🎯 **Recomendaciones de Uso**

### **Para Desarrollo Diario**
- Usar **Opción 1** (Híbrido)
- Solo Docker para PostgreSQL y Redis
- Backend y Frontend locales para mejor experiencia

### **Para Testing Completo**
- Usar **Opción 2** (Todo Docker)
- Verificar integración completa
- Probar workers de Celery

### **Para Deployment**
- Usar **Opción 3** (Producción)
- Frontend construido y servido por Nginx
- Configuración optimizada para producción

## 🔧 **Comandos Útiles**

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.dev.yml logs -f

# Reiniciar un servicio específico
docker-compose -f docker-compose.dev.yml restart api

# Limpiar volúmenes (¡CUIDADO! Borra datos)
docker-compose -f docker-compose.dev.yml down -v

# Reconstruir imágenes
docker-compose -f docker-compose.dev.yml build --no-cache
```

## 📈 **Beneficios de la Optimización**

1. **Menor consumo de recursos**
2. **Desarrollo más rápido**
3. **Debugging más fácil**
4. **Configuración más simple**
5. **Flexibilidad de desarrollo**

## ⚠️ **Consideraciones**

- **Volúmenes**: Los datos se mantienen entre reinicios
- **Redes**: Servicios aislados en red `invoice-dev-network`
- **Health Checks**: Servicios esperan a que dependencias estén listas
- **Variables de Entorno**: Configuración separada para desarrollo
