#!/usr/bin/env python3
"""
Script de Instalación para Soporte de PDF
========================================

Este script instala las dependencias necesarias para el soporte de PDF
en el sistema OCR optimizado.
"""

import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_package(package_name, import_name=None):
    """Instala un paquete Python"""
    if import_name is None:
        import_name = package_name
    
    try:
        # Verificar si ya está instalado
        __import__(import_name)
        logger.info(f"✅ {package_name} ya está instalado")
        return True
    except ImportError:
        logger.info(f"📦 Instalando {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            logger.info(f"✅ {package_name} instalado exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error instalando {package_name}: {e}")
            return False

def test_pdf_support():
    """Prueba el soporte de PDF después de la instalación"""
    logger.info("🧪 Probando soporte de PDF...")
    
    try:
        import fitz
        import cv2
        import numpy as np
        
        # Crear PDF de prueba
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 100), "PRUEBA PDF\nDNI: 12345678", fontsize=12)
        pdf_bytes = doc.tobytes()
        doc.close()
        
        # Probar conversión
        pix = fitz.open(stream=pdf_bytes, filetype="pdf")[0].get_pixmap()
        img_data = pix.tobytes("png")
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is not None:
            logger.info(f"✅ Conversión PDF → Imagen exitosa: {img.shape}")
            return True
        else:
            logger.error("❌ Error en conversión PDF → Imagen")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en prueba de PDF: {e}")
        return False

def main():
    """Función principal de instalación"""
    logger.info("🚀 INSTALANDO SOPORTE DE PDF")
    logger.info("=" * 40)
    
    # Paquetes necesarios
    packages = [
        ("PyMuPDF==1.24.0", "fitz"),
        ("opencv-python", "cv2"),
        ("numpy", "numpy")
    ]
    
    success_count = 0
    
    for package, import_name in packages:
        if install_package(package, import_name):
            success_count += 1
    
    logger.info(f"\n📊 Instalación: {success_count}/{len(packages)} paquetes exitosos")
    
    if success_count == len(packages):
        logger.info("✅ Todas las dependencias instaladas")
        
        # Probar funcionalidad
        if test_pdf_support():
            logger.info("\n🎉 ¡Soporte de PDF completamente funcional!")
            logger.info("📝 El sistema puede procesar PDFs en máximo 30 segundos")
            
            # Mostrar comandos útiles
            print("\n🛠️ Comandos útiles:")
            print("   • Probar soporte PDF: python test_pdf_support.py")
            print("   • Iniciar sistema: python start_fast_ocr_system.py")
            print("   • Verificar modelos: python check_models.py")
            
        else:
            logger.error("\n❌ Error en prueba de funcionalidad")
            return False
    else:
        logger.error(f"\n❌ Error instalando dependencias ({len(packages) - success_count} fallaron)")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
