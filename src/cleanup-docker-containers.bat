@echo off
echo ===============================================
echo  LIMPIEZA DE CONTENEDORES DOCKER INNECESARIOS
echo ===============================================

echo.
echo [1/4] Deteniendo contenedores innecesarios del proyecto OCR...
docker stop friendly_gould ocr-frontend sweet_burnell dreamy_payne src-ocr-worker-1 src-backend-1 src-redis-1 src-db-1 src-frontend-1 2>nul

echo.
echo [2/4] Eliminando contenedores detenidos...
docker rm friendly_gould ocr-frontend sweet_burnell dreamy_payne src-ocr-worker-1 src-backend-1 src-redis-1 src-db-1 src-frontend-1 2>nul

echo.
echo [3/4] Eliminando contenedores históricos obsoletos...
docker rm sweet_darwin goofy_lichterman jovial_noyce festive_davinci epic_wescoff 2>nul

echo.
echo [4/4] Limpiando imágenes no utilizadas...
docker image prune -f

echo.
echo ===============================================
echo  LIMPIEZA COMPLETADA
echo ===============================================
echo.
echo Contenedores eliminados:
echo   - friendly_gould (PostgreSQL obsoleto)
echo   - ocr-frontend (Frontend obsoleto)
echo   - sweet_burnell (PostgreSQL obsoleto)
echo   - dreamy_payne (Redis obsoleto)
echo   - src-* (Contenedores fallidos del proyecto)
echo   - Contenedores históricos obsoletos
echo.
echo Contenedores que se mantienen:
echo   - bos_* (Sistema backoffice activo)
echo   - ocr-frontend-dev (Frontend de desarrollo)
echo.
echo Para ver contenedores restantes:
echo   docker ps -a
echo ===============================================
