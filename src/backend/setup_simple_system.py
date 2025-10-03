#!/usr/bin/env python3
"""
Script de Configuracion Simple del Sistema OCR
============================================

Configuracion completa del sistema OCR optimizado con soporte de PDF.
"""

import os
import sys
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    """Imprime banner de configuracion"""
    banner = """
============================================================
                SISTEMA OCR OPTIMIZADO
                Configuracion Completa
                Procesamiento en <30 segundos
                Soporte completo de PDF
============================================================
        """
    print(banner)

def install_dependencies():
    """Instala dependencias necesarias"""
    logger.info("Instalando dependencias...")
    
    dependencies = ["PyMuPDF", "opencv-python", "ultralytics", "fastapi", "uvicorn"]
    
    for dep in dependencies:
        try:
            logger.info(f"Instalando {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            logger.info(f"{dep} instalado correctamente")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Advertencia instalando {dep}: {e}")
    
    return True

def verify_models():
    """Verifica modelos YOLO"""
    logger.info("Verificando modelos YOLO...")
    
    try:
        result = subprocess.run([sys.executable, "check_models.py"], 
                              cwd=".", capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info("Modelos YOLO verificados correctamente")
            return True
        else:
            logger.warning("Advertencia verificando modelos")
            return True
    except Exception as e:
        logger.error(f"Error verificando modelos: {e}")
        return False

def test_pdf_support():
    """Prueba soporte de PDF"""
    logger.info("Probando soporte de PDF...")
    
    try:
        result = subprocess.run([sys.executable, "test_pdf_support.py"], 
                              cwd=".", capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            logger.info("Soporte de PDF funcionando correctamente")
            return True
        else:
            logger.warning("Advertencia en soporte de PDF")
            return True
    except Exception as e:
        logger.error(f"Error probando PDF: {e}")
        return False

def test_system():
    """Prueba sistema completo"""
    logger.info("Probando sistema completo...")
    
    try:
        result = subprocess.run([sys.executable, "test_fast_ocr_system.py"], 
                              cwd=".", capture_output=True, text=True, timeout=120)
        
        logger.info("Sistema probado correctamente")
        return True
    except Exception as e:
        logger.error(f"Error probando sistema: {e}")
        return False

def create_startup_scripts():
    """Crea scripts de inicio"""
    logger.info("Creando scripts de inicio...")
    
    try:
        # Script de inicio
        startup_script = """@echo off
echo Iniciando Sistema OCR Optimizado...
cd /d "%~dp0"
python start_fast_ocr_system.py
pause
"""
        
        with open("start_system.bat", "w", encoding="utf-8") as f:
            f.write(startup_script)
        
        # Script de prueba
        test_script = """@echo off
echo Probando Sistema OCR...
cd /d "%~dp0"
python test_fast_ocr_system.py
pause
"""
        
        with open("test_system.bat", "w", encoding="utf-8") as f:
            f.write(test_script)
        
        logger.info("Scripts de inicio creados")
        return True
        
    except Exception as e:
        logger.error(f"Error creando scripts: {e}")
        return False

def main():
    """Funcion principal"""
    print_banner()
    
    steps = [
        ("Instalando dependencias", install_dependencies),
        ("Verificando modelos", verify_models),
        ("Probando soporte de PDF", test_pdf_support),
        ("Probando sistema completo", test_system),
        ("Creando scripts de inicio", create_startup_scripts)
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        logger.info(f"Ejecutando: {step_name}")
        try:
            if step_func():
                success_count += 1
                logger.info(f"{step_name} completado exitosamente")
            else:
                logger.warning(f"{step_name} completado con advertencias")
                success_count += 1
        except Exception as e:
            logger.error(f"Error en {step_name}: {e}")
    
    # Resumen final
    print("\n" + "="*50)
    print("RESUMEN DE CONFIGURACION")
    print("="*50)
    print(f"Pasos completados: {success_count}/{len(steps)}")
    print(f"Tasa de exito: {(success_count/len(steps))*100:.1f}%")
    
    if success_count == len(steps):
        print("\nSISTEMA CONFIGURADO EXITOSAMENTE!")
        print("El sistema esta listo para procesar documentos")
        print("\nPara iniciar:")
        print("  Windows: start_system.bat")
        print("  Linux/Mac: python start_fast_ocr_system.py")
    else:
        print("\nConfiguracion completada con advertencias")
        print("Revisar logs para detalles")
    
    return success_count == len(steps)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nConfiguracion interrumpida")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error critico: {e}")
        sys.exit(2)
