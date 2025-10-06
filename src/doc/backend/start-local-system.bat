@echo off
echo 🚀 Iniciando Sistema OCR en modo desarrollo local...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado. Por favor, instala Python 3.11+.
    pause
    exit /b 1
)

REM Verificar si Node.js está instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js no está instalado. Por favor, instala Node.js.
    pause
    exit /b 1
)

echo 📦 Instalando dependencias del backend...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias del backend.
    pause
    exit /b 1
)

echo 📦 Instalando dependencias del frontend...
cd ..\frontend
npm install
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias del frontend.
    pause
    exit /b 1
)

echo 🔧 Configurando archivos de entorno...
REM Crear .env.local para frontend
echo REACT_APP_API_URL=http://localhost:8000/api/v1 > .env.local
echo GENERATE_SOURCEMAP=false >> .env.local

cd ..\backend
REM Crear .env para backend
if not exist .env (
    copy env.example .env
    echo ✅ Archivo .env creado desde env.example
    echo ⚠️  Por favor, edita el archivo .env con tus configuraciones.
)

echo.
echo 🚀 Iniciando backend...
start "Backend OCR" cmd /k "python run_local.py"

echo ⏳ Esperando 5 segundos para que el backend se inicie...
timeout /t 5 /nobreak >nul

echo 🚀 Iniciando frontend...
cd ..\frontend
start "Frontend OCR" cmd /k "npm start"

echo.
echo ✅ Sistema OCR iniciado en modo desarrollo!
echo.
echo 🌐 Servicios disponibles:
echo   - Frontend:     http://localhost:3000
echo   - Backend API:  http://localhost:8000
echo   - Documentación: http://localhost:8000/docs
echo.
echo 📋 Credenciales de prueba:
echo   - Usuario: testuser
echo   - Contraseña: testpassword
echo.
echo 🛑 Para detener los servicios, cierra las ventanas de comandos.
echo.
pause

