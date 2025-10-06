@echo off
echo ================================================================
echo   PRUEBAS DOCKER DEL BACKEND - OCR DOCUMENT PROCESSOR
echo ================================================================
echo.

REM Verificar si Docker esta ejecutandose
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta ejecutandose. Por favor, inicia Docker Desktop.
    pause
    exit /b 1
)

echo Construyendo e iniciando contenedores Docker...
docker-compose -f docker-compose.full.yml up -d --build

if %errorlevel% neq 0 (
    echo [ERROR] Error construyendo o iniciando contenedores Docker.
    pause
    exit /b 1
)

echo Esperando 30 segundos para que todos los servicios se inicialicen...
timeout /t 30 /nobreak >nul

echo.
echo Ejecutando pruebas del sistema Docker...
cd backend
python test_docker_system.py
set TEST_RESULT=%errorlevel%
cd ..

if %TEST_RESULT% neq 0 (
    echo [ERROR] Las pruebas con Docker fallaron
    echo Deteniendo contenedores...
    docker-compose -f docker-compose.full.yml down
    pause
    exit /b 1
) else (
    echo [SUCCESS] Todas las pruebas con Docker pasaron exitosamente
    echo.
    echo Servicios Docker disponibles:
    echo   - Frontend:     http://localhost:3000
    echo   - Backend API:  http://localhost:8000
    echo   - Documentacion: http://localhost:8000/docs
    echo   - Flower:       http://localhost:5555
    echo.
    echo Para detener los contenedores: docker-compose -f docker-compose.full.yml down
)

echo.
echo Pruebas Docker del backend completadas.
pause
