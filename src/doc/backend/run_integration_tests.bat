@echo off
echo ================================================================
echo   PRUEBAS DE INTEGRACION - OCR DOCUMENT PROCESSOR
echo ================================================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado. Por favor, instala Python 3.11+.
    pause
    exit /b 1
)

REM Verificar si Node.js esta instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no esta instalado. Por favor, instala Node.js.
    pause
    exit /b 1
)

echo NOTA: Las pruebas de integracion requieren que tanto el frontend
echo como el backend esten ejecutandose.
echo.

echo Instalando dependencias del backend...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Error instalando dependencias del backend.
    cd ..
    pause
    exit /b 1
)
cd ..

echo Instalando dependencias del frontend...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo [ERROR] Error instalando dependencias del frontend.
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo Iniciando backend local...
cd backend
start "Backend Integration" cmd /k "python run_local.py"
cd ..

echo Esperando 10 segundos para que el backend se inicie...
timeout /t 10 /nobreak >nul

echo Iniciando frontend local...
cd frontend
start "Frontend Integration" cmd /k "npm start"
cd ..

echo Esperando 15 segundos para que el frontend se inicie...
timeout /t 15 /nobreak >nul

echo.
echo Ejecutando pruebas de integracion...
python test_integration.py
set TEST_RESULT=%errorlevel%

echo.
echo Cerrando servicios...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

if %TEST_RESULT% neq 0 (
    echo [ERROR] Las pruebas de integracion fallaron
    echo Revisa los errores arriba para solucionar los problemas.
    pause
    exit /b 1
) else (
    echo [SUCCESS] Todas las pruebas de integracion pasaron exitosamente
)

echo.
echo Pruebas de integracion completadas.
pause
