@echo off
echo 🚀 Iniciando Frontend en modo desarrollo con Docker...
echo.

REM Verificar si Docker está ejecutándose
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está ejecutándose. Por favor, inicia Docker Desktop.
    pause
    exit /b 1
)

echo 📦 Construyendo imagen de desarrollo del frontend...
docker build -f Dockerfile.dev -t ocr-frontend-dev .

if %errorlevel% neq 0 (
    echo ❌ Error construyendo la imagen de desarrollo del frontend.
    pause
    exit /b 1
)

echo 🐳 Iniciando contenedor de desarrollo del frontend...
docker run -d ^
    --name ocr-frontend-dev ^
    -p 3000:3000 ^
    -e REACT_APP_API_URL=http://localhost:8000/api/v1 ^
    -e CHOKIDAR_USEPOLLING=true ^
    -v "%cd%":/app ^
    -v /app/node_modules ^
    ocr-frontend-dev

if %errorlevel% neq 0 (
    echo ❌ Error iniciando el contenedor de desarrollo del frontend.
    pause
    exit /b 1
)

echo.
echo ✅ Frontend en modo desarrollo iniciado correctamente!
echo 🌐 URL: http://localhost:3000
echo 📚 API: http://localhost:8000
echo 🔥 Hot reload habilitado
echo.
echo Para detener el contenedor:
echo docker stop ocr-frontend-dev
echo.
echo Para ver logs:
echo docker logs -f ocr-frontend-dev
echo.
pause

