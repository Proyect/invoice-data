@echo off
echo ===============================================
echo  INICIANDO SISTEMA DE DESARROLLO CON DOCKER
echo ===============================================

echo.
echo [1/3] Deteniendo contenedores existentes...
docker-compose -f docker-compose.dev.yml down

echo.
echo [2/3] Construyendo imágenes...
docker-compose -f docker-compose.dev.yml build

echo.
echo [3/3] Iniciando servicios de desarrollo...
docker-compose -f docker-compose.dev.yml up -d

echo.
echo ===============================================
echo  SISTEMA INICIADO EXITOSAMENTE
echo ===============================================
echo.
echo Servicios disponibles:
echo   - API Backend: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - Celery Flower: http://localhost:5555
echo   - PostgreSQL: localhost:5432
echo   - Redis: localhost:6379
echo.
echo Para ver logs en tiempo real:
echo   docker-compose -f docker-compose.dev.yml logs -f
echo.
echo Para detener el sistema:
echo   docker-compose -f docker-compose.dev.yml down
echo ===============================================
