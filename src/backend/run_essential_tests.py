#!/usr/bin/env python3
"""
Suite de Tests Esenciales
=========================

Este script ejecuta todos los tests esenciales del sistema.
"""

import sys
import os
import logging
import subprocess
from pathlib import Path

# Agregar el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_test(test_file, description):
    """Ejecuta un test individual"""
    logger.info(f"🧪 Ejecutando: {description}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info(f"✅ {description} - EXITOSO")
            return True
        else:
            logger.error(f"❌ {description} - FALLÓ")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        logger.error(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Función principal"""
    logger.info("🚀 Iniciando Suite de Tests Esenciales")
    logger.info("=" * 50)
    
    # Lista de tests esenciales
    essential_tests = [
        ("test_fixed_system.py", "Sistema Principal Corregido"),
        ("test_fast_ocr_system.py", "Sistema OCR Optimizado"),
        ("tests/test_model_loader.py", "Cargador de Modelos"),
        ("tests/test_ocr_service.py", "Servicio OCR"),
        ("tests/test_document_service.py", "Servicio de Documentos"),
        ("tests/test_auth_service.py", "Servicio de Autenticación"),
        ("tests/test_preprocessing_service.py", "Preprocesamiento"),
    ]
    
    # Ejecutar tests
    success_count = 0
    total_tests = len(essential_tests)
    
    for test_file, description in essential_tests:
        if os.path.exists(test_file):
            if run_test(test_file, description):
                success_count += 1
        else:
            logger.warning(f"⚠️ Test no encontrado: {test_file}")
    
    # Resumen
    logger.info("\n" + "=" * 50)
    logger.info(f"📊 RESULTADOS:")
    logger.info(f"   Tests ejecutados: {total_tests}")
    logger.info(f"   Exitosos: {success_count}")
    logger.info(f"   Fallidos: {total_tests - success_count}")
    logger.info(f"   Tasa de éxito: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        logger.info("🎉 ¡Todos los tests esenciales pasaron!")
        return True
    else:
        logger.warning("⚠️ Algunos tests fallaron")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
