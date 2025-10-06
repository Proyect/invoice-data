#!/usr/bin/env python3
"""
Script de Instalación de Dependencias
=====================================

Este script instala todas las dependencias necesarias para el sistema OCR
usando las versiones compatibles y sin problemas de compilación.

Dependencias principales:
- pdf2image (en lugar de PyMuPDF)
- Pillow
- python-decouple
- Todas las dependencias del requirements.txt
"""

import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    try:
        logger.info(f"🔄 {description}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} - Completado")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - Error: {e.stderr}")
        return False

def install_dependencies():
    """Instala todas las dependencias necesarias"""
    
    logger.info("🚀 Iniciando instalación de dependencias...")
    
    # Lista de comandos de instalación
    commands = [
        ("pip install --upgrade pip", "Actualizando pip"),
        ("pip install python-decouple==3.8", "Instalando python-decouple"),
        ("pip install pdf2image==1.17.0", "Instalando pdf2image"),
        ("pip install Pillow==10.0.0", "Instalando Pillow"),
        ("pip install opencv-python", "Instalando OpenCV"),
        ("pip install numpy", "Instalando NumPy"),
        ("pip install pytesseract", "Instalando Tesseract"),
        ("pip install fastapi", "Instalando FastAPI"),
        ("pip install uvicorn", "Instalando Uvicorn"),
        ("pip install sqlalchemy", "Instalando SQLAlchemy"),
        ("pip install psycopg2-binary", "Instalando PostgreSQL driver"),
        ("pip install python-multipart", "Instalando python-multipart"),
        ("pip install python-jose[cryptography]", "Instalando python-jose"),
        ("pip install passlib[bcrypt]", "Instalando passlib"),
        ("pip install ultralytics", "Instalando YOLO"),
        ("pip install torch torchvision", "Instalando PyTorch"),
        ("pip install requests", "Instalando requests"),
        ("pip install python-dotenv", "Instalando python-dotenv"),
    ]
    
    # Ejecutar comandos
    success_count = 0
    total_commands = len(commands)
    
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
        else:
            logger.warning(f"⚠️ Falló: {description}")
    
    # Instalar desde requirements.txt si existe
    if os.path.exists("requirements.txt"):
        logger.info("📦 Instalando dependencias desde requirements.txt...")
        if run_command("pip install -r requirements.txt", "Instalando desde requirements.txt"):
            success_count += 1
            total_commands += 1
    
    # Resumen
    logger.info(f"📊 Resumen: {success_count}/{total_commands} comandos exitosos")
    
    if success_count == total_commands:
        logger.info("🎉 ¡Todas las dependencias instaladas correctamente!")
        return True
    else:
        logger.warning("⚠️ Algunas dependencias fallaron, pero el sistema debería funcionar")
        return False

def test_imports():
    """Prueba las importaciones principales"""
    logger.info("🧪 Probando importaciones...")
    
    test_imports = [
        ("pdf2image", "pdf2image"),
        ("PIL", "Pillow"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("decouple", "python-decouple"),
        ("fastapi", "FastAPI"),
        ("ultralytics", "YOLO"),
    ]
    
    success_count = 0
    for module, name in test_imports:
        try:
            __import__(module)
            logger.info(f"✅ {name} - OK")
            success_count += 1
        except ImportError as e:
            logger.error(f"❌ {name} - Error: {e}")
    
    logger.info(f"📊 Importaciones: {success_count}/{len(test_imports)} exitosas")
    return success_count == len(test_imports)

if __name__ == "__main__":
    logger.info("🔧 Script de Instalación de Dependencias")
    logger.info("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("requirements.txt"):
        logger.error("❌ No se encontró requirements.txt. Ejecuta desde el directorio backend/")
        sys.exit(1)
    
    # Instalar dependencias
    install_success = install_dependencies()
    
    # Probar importaciones
    test_success = test_imports()
    
    if install_success and test_success:
        logger.info("🎉 ¡Sistema listo para usar!")
        logger.info("💡 Ejecuta: python test_fast_ocr_system.py")
    else:
        logger.warning("⚠️ Algunos problemas detectados, pero puedes intentar ejecutar el sistema")
        logger.info("💡 Si hay errores, ejecuta: python test_fast_ocr_system.py")
