@echo off
echo 🧪 Ejecutando pruebas del sistema OCR con contenedores Docker...
echo.

REM Verificar si Docker está ejecutándose
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está ejecutándose. Por favor, inicia Docker Desktop.
    pause
    exit /b 1
)

echo 📦 Construyendo e iniciando contenedores...
docker-compose -f docker-compose.full.yml up -d --build

if %errorlevel% neq 0 (
    echo ❌ Error construyendo o iniciando contenedores.
    pause
    exit /b 1
)

echo ⏳ Esperando 30 segundos para que todos los servicios se inicialicen...
timeout /t 30 /nobreak >nul

echo.
echo 🧪 Ejecutando pruebas del sistema Docker...
cd backend
python test_docker_system.py

echo.
echo 📊 Pruebas completadas. Revisa los resultados arriba.
echo.
echo 🌐 Servicios disponibles:
echo   - Frontend:     http://localhost:3000
echo   - Backend API:  http://localhost:8000
echo   - Documentación: http://localhost:8000/docs
echo   - Flower:       http://localhost:5555
echo.
echo 🛑 Para detener todos los servicios:
echo   docker-compose -f docker-compose.full.yml down
echo.
pause

