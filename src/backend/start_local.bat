@echo off
echo 🚀 Iniciando Backend FastAPI OCR...
echo.

REM Activar entorno virtual
call .venv\Scripts\activate

REM Verificar que las dependencias estén instaladas
echo 📦 Verificando dependencias...
python -c "import fastapi, uvicorn, sqlalchemy" 2>nul
if errorlevel 1 (
    echo ❌ Dependencias faltantes. Instalando...
    pip install -r requirements.txt
)

REM Crear directorios si no existen
if not exist "uploaded_documents_local" mkdir uploaded_documents_local
if not exist "models\yolo_models" mkdir models\yolo_models
if not exist "logs" mkdir logs

REM Crear archivo .env si no existe
if not exist ".env" (
    if exist ".env.local" (
        copy ".env.local" ".env"
        echo ✅ Archivo .env creado desde .env.local
    )
)

REM Inicializar base de datos
echo 💾 Inicializando base de datos...
python -c "from database import create_db_and_tables; create_db_and_tables()" 2>nul

echo.
echo 🌐 Iniciando servidor en http://localhost:8000
echo 📚 Documentación en http://localhost:8000/docs
echo 🛑 Presiona Ctrl+C para detener
echo.

REM Iniciar servidor
python run_local.py

pause
