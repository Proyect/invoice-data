@echo off
echo 🚀 Iniciando Frontend en modo desarrollo local...
echo.

REM Verificar si Node.js está instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js no está instalado. Por favor, instala Node.js.
    pause
    exit /b 1
)

REM Verificar si npm está disponible
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm no está disponible. Por favor, instala npm.
    pause
    exit /b 1
)

REM Crear archivo .env.local si no existe
if not exist .env.local (
    echo Creando archivo .env.local...
    echo REACT_APP_API_URL=http://localhost:8000/api/v1 > .env.local
    echo GENERATE_SOURCEMAP=false >> .env.local
)

REM Verificar si node_modules existe
if not exist node_modules (
    echo 📦 Instalando dependencias...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Error instalando dependencias.
        pause
        exit /b 1
    )
)

echo 🌐 Iniciando servidor de desarrollo...
echo 📚 API Backend: http://localhost:8000
echo 🌐 Frontend: http://localhost:3000
echo.
echo Presiona Ctrl+C para detener
echo.

npm start

