@echo off
echo ===============================================
echo  INICIANDO SISTEMA DE DESARROLLO LOCAL
echo ===============================================

echo.
echo [1/4] Iniciando servicios de base (Docker)...
docker-compose -f docker-compose.dev.yml up -d db redis

echo.
echo [2/4] Esperando que los servicios estén listos...
timeout /t 10 /nobreak >nul

echo.
echo [3/4] Iniciando Backend (Local)...
cd backend
start "Backend API" cmd /k ".\.venv\Scripts\activate && python main.py"
cd ..

echo.
echo [4/4] Iniciando Frontend (Local)...
cd frontend
start "Frontend React" cmd /k "npm start"
cd ..

echo.
echo ===============================================
echo  SISTEMA INICIADO EXITOSAMENTE
echo ===============================================
echo.
echo Servicios disponibles:
echo   - API Backend: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - Frontend: http://localhost:3000
echo   - PostgreSQL: localhost:5432
echo   - Redis: localhost:6379
echo.
echo Para iniciar Celery Worker (opcional):
echo   cd backend && .\.venv\Scripts\activate && celery -A ocr_worker.celery_app worker --loglevel=info
echo.
echo Para detener servicios Docker:
echo   docker-compose -f docker-compose.dev.yml down
echo ===============================================
