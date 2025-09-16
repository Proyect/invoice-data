@echo off
echo 🚀 Iniciando Frontend con Docker...
echo.

REM Verificar si Docker está ejecutándose
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está ejecutándose. Por favor, inicia Docker Desktop.
    pause
    exit /b 1
)

echo 📦 Construyendo imagen del frontend...
docker build -t ocr-frontend .

if %errorlevel% neq 0 (
    echo ❌ Error construyendo la imagen del frontend.
    pause
    exit /b 1
)

echo 🐳 Iniciando contenedor del frontend...
docker run -d ^
    --name ocr-frontend ^
    -p 3000:80 ^
    -e REACT_APP_API_URL=http://localhost:8000/api/v1 ^
    ocr-frontend

if %errorlevel% neq 0 (
    echo ❌ Error iniciando el contenedor del frontend.
    pause
    exit /b 1
)

echo.
echo ✅ Frontend iniciado correctamente!
echo 🌐 URL: http://localhost:3000
echo 📚 API: http://localhost:8000
echo.
echo Para detener el contenedor:
echo docker stop ocr-frontend
echo.
echo Para ver logs:
echo docker logs ocr-frontend
echo.
pause

