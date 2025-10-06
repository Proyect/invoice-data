@echo off
echo ===============================================
echo  REPARACIÓN DE PROBLEMAS DOCKER
echo ===============================================

echo.
echo [1/6] Limpiando contenedores fallidos...
docker rm -f goofy_jepsen magical_hypatia 2>nul

echo.
echo [2/6] Limpiando imágenes huérfanas...
docker image prune -f

echo.
echo [3/6] Verificando archivo de variables de entorno...
if not exist "backend\docker.env" (
    echo ❌ Archivo docker.env no encontrado
    echo Creando archivo de variables de entorno...
    echo SECRET_KEY_JWT=dev_jwt_secret_key_for_development_only > backend\docker.env
    echo ACCESS_TOKEN_EXPIRE_MINUTES=60 >> backend\docker.env
    echo DATABASE_URL=postgresql://ocr_user:dev_password_123@db:5432/ocr_database >> backend\docker.env
    echo REDIS_HOST=redis >> backend\docker.env
    echo REDIS_PORT=6379 >> backend\docker.env
    echo REDIS_DB=0 >> backend\docker.env
    echo REDIS_URL=redis://redis:6379/0 >> backend\docker.env
    echo LOCAL_STORAGE_PATH=/app/uploaded_documents_local >> backend\docker.env
    echo YOLO_MODELS_PATH=/app/models/yolo_models >> backend\docker.env
    echo PYTHONPATH=/app >> backend\docker.env
    echo ✅ Archivo docker.env creado
) else (
    echo ✅ Archivo docker.env existe
)

echo.
echo [4/6] Verificando redes Docker...
docker network inspect ocr-dev-network >nul 2>&1
if errorlevel 1 (
    echo ❌ Red ocr-dev-network no existe
    echo Creando red...
    docker network create ocr-dev-network
    echo ✅ Red creada
) else (
    echo ✅ Red ocr-dev-network existe
)

echo.
echo [5/6] Verificando volúmenes...
docker volume inspect invoice_postgres_data >nul 2>&1
if errorlevel 1 (
    echo ❌ Volumen postgres_data no existe
    echo Creando volumen...
    docker volume create invoice_postgres_data
    echo ✅ Volumen creado
) else (
    echo ✅ Volumen postgres_data existe
)

docker volume inspect invoice_redis_data >nul 2>&1
if errorlevel 1 (
    echo ❌ Volumen redis_data no existe
    echo Creando volumen...
    docker volume create invoice_redis_data
    echo ✅ Volumen creado
) else (
    echo ✅ Volumen redis_data existe
)

echo.
echo [6/6] Construyendo imágenes actualizadas...
docker-compose -f docker-compose.dev.yml build --no-cache

echo.
echo ===============================================
echo  REPARACIÓN COMPLETADA
echo ===============================================
echo.
echo Problemas corregidos:
echo   ✅ Contenedores fallidos eliminados
echo   ✅ Variables de entorno configuradas
echo   ✅ Redes Docker verificadas
echo   ✅ Volúmenes Docker verificados
echo   ✅ Imágenes reconstruidas
echo.
echo Para iniciar el sistema:
echo   docker-compose -f docker-compose.dev.yml up -d
echo.
echo Para ver logs:
echo   docker-compose -f docker-compose.dev.yml logs -f
echo ===============================================
