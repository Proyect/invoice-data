@echo off
echo 🚀 Iniciando Sistema OCR Completo con Docker...
echo.

REM Verificar si Docker está ejecutándose
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está ejecutándose. Por favor, inicia Docker Desktop.
    pause
    exit /b 1
)

echo 📦 Construyendo todas las imágenes...
docker-compose -f docker-compose.full.yml build

if %errorlevel% neq 0 (
    echo ❌ Error construyendo las imágenes.
    pause
    exit /b 1
)

echo 🐳 Iniciando todos los servicios...
docker-compose -f docker-compose.full.yml up -d

if %errorlevel% neq 0 (
    echo ❌ Error iniciando los servicios.
    pause
    exit /b 1
)

echo.
echo ✅ Sistema OCR iniciado correctamente!
echo.
echo 🌐 Servicios disponibles:
echo   - Frontend:     http://localhost:3000
echo   - Backend API:  http://localhost:8000
echo   - Documentación: http://localhost:8000/docs
echo   - Base de datos: localhost:5432
echo   - Redis:        localhost:6379
echo.
echo 📊 Para ver el estado de los servicios:
echo   docker-compose -f docker-compose.full.yml ps
echo.
echo 📋 Para ver logs:
echo   docker-compose -f docker-compose.full.yml logs -f
echo.
echo 🛑 Para detener todos los servicios:
echo   docker-compose -f docker-compose.full.yml down
echo.
echo ⚠️  Nota: La primera vez puede tardar varios minutos en descargar las imágenes.
echo.
pause

