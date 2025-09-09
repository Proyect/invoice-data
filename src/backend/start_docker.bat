@echo off
echo ====================================
echo  INICIANDO PROYECTO CON DOCKER
echo ====================================

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker no está instalado o no está en el PATH
    echo Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Verificar si docker-compose está disponible
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: docker-compose no está disponible
    echo Asegúrate de tener Docker Desktop actualizado
    pause
    exit /b 1
)

REM Copiar archivo de configuración si no existe
if not exist .env (
    echo Copiando configuración de Docker...
    copy .env.docker .env
    echo ✓ Archivo .env creado desde .env.docker
) else (
    echo ✓ Archivo .env ya existe
)

echo.
echo Construyendo e iniciando contenedores...
echo Esto puede tomar varios minutos la primera vez...
echo.

REM Construir e iniciar todos los servicios
docker compose up --build -d

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Falló al iniciar los contenedores
    echo Revisa los logs con: docker compose logs
    pause
    exit /b 1
)

echo.
echo ====================================
echo  ✓ PROYECTO INICIADO CORRECTAMENTE
echo ====================================
echo.
echo Servicios disponibles:
echo  • API FastAPI:     http://localhost:8000
echo  • Documentación:   http://localhost:8000/docs
echo  • Base de datos:   localhost:5432
echo  • Redis:           localhost:6379
echo  • Celery Flower:   http://localhost:5555
echo.
echo Para ver logs:      docker compose logs -f
echo Para detener:       docker compose down
echo.
pause
