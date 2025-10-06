@echo off
echo ================================================================
echo   PRUEBAS LOCALES DEL BACKEND - OCR DOCUMENT PROCESSOR
echo ================================================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado. Por favor, instala Python 3.11+.
    pause
    exit /b 1
)

echo Instalando dependencias del backend...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Error instalando dependencias del backend.
    pause
    exit /b 1
)

echo.
echo Iniciando servidor backend local...
start "Backend OCR Local" cmd /k "python run_local.py"

echo Esperando 15 segundos para que el backend se inicie...
timeout /t 15 /nobreak >nul

echo.
echo Ejecutando pruebas del sistema local...
python test_local_system.py
set TEST_RESULT=%errorlevel%

echo.
echo Cerrando servidor backend...
taskkill /f /im python.exe >nul 2>&1

if %TEST_RESULT% neq 0 (
    echo [ERROR] Las pruebas locales del backend fallaron
    echo Revisa los errores arriba para solucionar los problemas.
    pause
    exit /b 1
) else (
    echo [SUCCESS] Todas las pruebas locales del backend pasaron exitosamente
)

cd ..
echo.
echo Pruebas locales del backend completadas.
pause
