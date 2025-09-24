@echo off
echo ===============================================
echo  SISTEMA OCR LIMPIO Y OPTIMIZADO
echo ===============================================

echo.
echo [1/3] Limpiando sistema anterior...
docker-compose -f docker-compose.full.yml down 2>nul
docker-compose -f docker-compose.dev.yml down 2>nul

echo.
echo [2/3] Iniciando servicios esenciales...
docker-compose -f docker-compose.dev.yml up -d db redis

echo.
echo [3/3] Esperando que los servicios estén listos...
timeout /t 15 /nobreak >nul

echo.
echo ===============================================
echo  SISTEMA INICIADO EXITOSAMENTE
echo ===============================================
echo.
echo Servicios disponibles:
echo   - PostgreSQL: localhost:5432
echo   - Redis: localhost:6379
echo.
echo Para iniciar Backend (Local):
echo   cd backend && .\.venv\Scripts\activate && python main.py
echo.
echo Para iniciar Frontend (Local):
echo   cd frontend && npm start
echo.
echo Para iniciar Celery Worker (Opcional):
echo   cd backend && .\.venv\Scripts\activate && celery -A ocr_worker.celery_app worker --loglevel=info
echo.
echo Para detener servicios:
echo   docker-compose -f docker-compose.dev.yml down
echo ===============================================
