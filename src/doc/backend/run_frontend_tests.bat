@echo off
echo ================================================================
echo   PRUEBAS DEL FRONTEND - OCR DOCUMENT PROCESSOR
echo ================================================================
echo.

REM Verificar si Node.js esta instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no esta instalado. Por favor, instala Node.js.
    pause
    exit /b 1
)

REM Verificar si Python esta instalado (para el script de pruebas)
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado. Por favor, instala Python 3.11+.
    pause
    exit /b 1
)

echo Instalando dependencias del frontend...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo [ERROR] Error instalando dependencias del frontend.
    pause
    exit /b 1
)

echo.
echo Ejecutando pruebas del frontend...
python test_frontend_system.py
set TEST_RESULT=%errorlevel%

if %TEST_RESULT% neq 0 (
    echo [ERROR] Las pruebas del frontend fallaron
    echo Revisa los errores arriba para solucionar los problemas.
    cd ..
    pause
    exit /b 1
) else (
    echo [SUCCESS] Todas las pruebas del frontend pasaron exitosamente
)

cd ..
echo.
echo Pruebas del frontend completadas.
pause
