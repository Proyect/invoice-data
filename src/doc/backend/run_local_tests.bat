@echo off
echo 🧪 Ejecutando pruebas del sistema OCR en entorno local...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado. Por favor, instala Python 3.11+.
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

echo.
echo 🚀 Iniciando servidor backend en segundo plano...
start "Backend OCR" cmd /k "python run_local.py"

echo ⏳ Esperando 10 segundos para que el backend se inicie...
timeout /t 10 /nobreak >nul

echo.
echo 🧪 Ejecutando pruebas del sistema...
python test_local_system.py

echo.
echo 📊 Pruebas completadas. Revisa los resultados arriba.
echo.
echo 🛑 Para detener el servidor backend, cierra la ventana "Backend OCR".
echo.
pause

