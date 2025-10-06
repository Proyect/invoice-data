@echo off
setlocal enabledelayedexpansion

echo ================================================================
echo   SISTEMA COMPLETO DE PRUEBAS - OCR DOCUMENT PROCESSOR
echo ================================================================
echo.

REM Verificar argumentos
if "%1"=="" goto :show_help
if "%1"=="local" goto :local_tests
if "%1"=="docker" goto :docker_tests
if "%1"=="frontend" goto :frontend_tests
if "%1"=="integration" goto :integration_tests
if "%1"=="all" goto :all_tests
goto :show_help

:show_help
echo Uso: run_all_tests.bat [opcion]
echo.
echo Opciones disponibles:
echo   local      - Ejecutar solo pruebas locales del backend
echo   docker     - Ejecutar solo pruebas con contenedores Docker
echo   frontend   - Ejecutar solo pruebas del frontend
echo   integration- Ejecutar solo pruebas de integracion
echo   all        - Ejecutar todas las pruebas (recomendado)
echo.
echo Ejemplos:
echo   run_all_tests.bat local
echo   run_all_tests.bat docker
echo   run_all_tests.bat all
echo.
pause
exit /b 1

:local_tests
echo ================================================================
echo   EJECUTANDO PRUEBAS LOCALES DEL BACKEND
echo ================================================================
echo.
echo Iniciando servidor backend local...
cd backend
start "Backend Local" cmd /k "python run_local.py"
cd ..

echo Esperando 15 segundos para que el backend se inicie...
timeout /t 15 /nobreak >nul

echo.
echo Ejecutando pruebas del backend local...
cd backend
python test_local_system.py
set LOCAL_RESULT=%errorlevel%
cd ..

if %LOCAL_RESULT% neq 0 (
    echo [ERROR] Las pruebas locales del backend fallaron
    echo Cerrando servidor backend...
    taskkill /f /im python.exe >nul 2>&1
    pause
    exit /b 1
) else (
    echo [SUCCESS] Pruebas locales del backend completadas exitosamente
    echo Cerrando servidor backend...
    taskkill /f /im python.exe >nul 2>&1
)
goto :end

:docker_tests
echo ================================================================
echo   EJECUTANDO PRUEBAS CON CONTENEDORES DOCKER
echo ================================================================
echo.

REM Verificar si Docker esta corriendo
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta ejecutandose. Por favor, inicia Docker Desktop.
    pause
    exit /b 1
)

echo Construyendo e iniciando contenedores Docker...
docker-compose -f docker-compose.full.yml up -d --build

if %errorlevel% neq 0 (
    echo [ERROR] Error construyendo o iniciando contenedores Docker.
    pause
    exit /b 1
)

echo Esperando 30 segundos para que todos los servicios se inicialicen...
timeout /t 30 /nobreak >nul

echo.
echo Ejecutando pruebas del sistema Docker...
cd backend
python test_docker_system.py
set DOCKER_RESULT=%errorlevel%
cd ..

if %DOCKER_RESULT% neq 0 (
    echo [ERROR] Las pruebas con Docker fallaron
    echo Deteniendo contenedores...
    docker-compose -f docker-compose.full.yml down
    pause
    exit /b 1
) else (
    echo [SUCCESS] Pruebas con Docker completadas exitosamente
    echo.
    echo Servicios Docker disponibles:
    echo   - Frontend:     http://localhost:3000
    echo   - Backend API:  http://localhost:8000
    echo   - Documentacion: http://localhost:8000/docs
    echo   - Flower:       http://localhost:5555
    echo.
    echo Para detener los contenedores: docker-compose -f docker-compose.full.yml down
)
goto :end

:frontend_tests
echo ================================================================
echo   EJECUTANDO PRUEBAS DEL FRONTEND
echo ================================================================
echo.

REM Verificar si Node.js esta instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no esta instalado. Por favor, instala Node.js.
    pause
    exit /b 1
)

echo Ejecutando pruebas del frontend...
cd frontend
python test_frontend_system.py
set FRONTEND_RESULT=%errorlevel%
cd ..

if %FRONTEND_RESULT% neq 0 (
    echo [ERROR] Las pruebas del frontend fallaron
    pause
    exit /b 1
) else (
    echo [SUCCESS] Pruebas del frontend completadas exitosamente
)
goto :end

:integration_tests
echo ================================================================
echo   EJECUTANDO PRUEBAS DE INTEGRACION
echo ================================================================
echo.

echo NOTA: Las pruebas de integracion requieren que tanto el frontend
echo como el backend esten ejecutandose.
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
set INTEGRATION_RESULT=%errorlevel%

echo Cerrando servicios...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

if %INTEGRATION_RESULT% neq 0 (
    echo [ERROR] Las pruebas de integracion fallaron
    pause
    exit /b 1
) else (
    echo [SUCCESS] Pruebas de integracion completadas exitosamente
)
goto :end

:all_tests
echo ================================================================
echo   EJECUTANDO TODAS LAS PRUEBAS
echo ================================================================
echo.

echo PASO 1/4: Pruebas del Frontend
echo ================================
cd frontend
python test_frontend_system.py
if %errorlevel% neq 0 (
    echo [ERROR] Las pruebas del frontend fallaron
    cd ..
    pause
    exit /b 1
)
echo [SUCCESS] Pruebas del frontend completadas
cd ..

echo.
echo PASO 2/4: Pruebas Locales del Backend
echo ======================================
cd backend
start "Backend All Tests" cmd /k "python run_local.py"
cd ..

echo Esperando 15 segundos para que el backend se inicie...
timeout /t 15 /nobreak >nul

cd backend
python test_local_system.py
if %errorlevel% neq 0 (
    echo [ERROR] Las pruebas locales del backend fallaron
    cd ..
    taskkill /f /im python.exe >nul 2>&1
    pause
    exit /b 1
)
echo [SUCCESS] Pruebas locales del backend completadas
cd ..

echo Cerrando servidor backend local...
taskkill /f /im python.exe >nul 2>&1

echo.
echo PASO 3/4: Pruebas con Contenedores Docker
echo ==========================================
docker-compose -f docker-compose.full.yml up -d --build

if %errorlevel% neq 0 (
    echo [ERROR] Error construyendo o iniciando contenedores Docker.
    pause
    exit /b 1
)

echo Esperando 30 segundos para que todos los servicios se inicialicen...
timeout /t 30 /nobreak >nul

cd backend
python test_docker_system.py
if %errorlevel% neq 0 (
    echo [ERROR] Las pruebas con Docker fallaron
    cd ..
    docker-compose -f docker-compose.full.yml down
    pause
    exit /b 1
)
echo [SUCCESS] Pruebas con Docker completadas
cd ..

echo.
echo PASO 4/4: Pruebas de Integracion
echo =================================
python test_integration.py
if %errorlevel% neq 0 (
    echo [ERROR] Las pruebas de integracion fallaron
    docker-compose -f docker-compose.full.yml down
    pause
    exit /b 1
)
echo [SUCCESS] Pruebas de integracion completadas

echo.
echo ================================================================
echo   TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE
echo ================================================================
echo.
echo [SUCCESS] El sistema OCR esta funcionando correctamente en todos los entornos
echo.
echo Servicios disponibles:
echo   - Frontend:     http://localhost:3000
echo   - Backend API:  http://localhost:8000
echo   - Documentacion: http://localhost:8000/docs
echo   - Flower:       http://localhost:5555
echo.
echo Para detener los contenedores Docker:
echo   docker-compose -f docker-compose.full.yml down
echo.
goto :end

:end
echo.
echo Pruebas finalizadas
echo.
pause