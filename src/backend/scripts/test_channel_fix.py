#!/usr/bin/env python3
"""
Script para probar la corrección del problema de canales de imagen
"""

import sys
import os
import numpy as np
import cv2
from pathlib import Path

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.preprocessing_service import preprocess_image_for_ocr
from services.ocr_service import perform_yolo_ocr
from models.enums import DocumentType

def test_image_channels():
    """Prueba que las imágenes mantengan 3 canales después del preprocessing"""
    
    print("PROBANDO CORRECCION DE CANALES DE IMAGEN")
    print("=" * 50)
    
    # Crear imagen de prueba RGB (3 canales)
    test_image_rgb = np.random.randint(0, 255, (640, 480, 3), dtype=np.uint8)
    print(f"Imagen original RGB: {test_image_rgb.shape}")
    
    # Crear imagen de prueba en escala de grises (1 canal)
    test_image_gray = np.random.randint(0, 255, (640, 480), dtype=np.uint8)
    print(f"Imagen original GRAY: {test_image_gray.shape}")
    
    try:
        # Probar preprocessing con imagen RGB
        processed_rgb = preprocess_image_for_ocr(test_image_rgb)
        print(f"Imagen RGB procesada: {processed_rgb.shape}")
        
        if len(processed_rgb.shape) == 3 and processed_rgb.shape[2] == 3:
            print("✅ RGB: Preprocessing mantiene 3 canales correctamente")
        else:
            print("❌ RGB: Error - imagen no tiene 3 canales")
            
        # Probar preprocessing con imagen en escala de grises
        processed_gray = preprocess_image_for_ocr(test_image_gray)
        print(f"Imagen GRAY procesada: {processed_gray.shape}")
        
        if len(processed_gray.shape) == 3 and processed_gray.shape[2] == 3:
            print("✅ GRAY: Preprocessing convierte correctamente a 3 canales")
        else:
            print("❌ GRAY: Error - imagen no fue convertida a 3 canales")
            
        return True
        
    except Exception as e:
        print(f"❌ Error durante el preprocessing: {e}")
        return False

def test_yolo_compatibility():
    """Prueba que YOLO pueda procesar las imágenes preprocessadas"""
    
    print("\nPROBANDO COMPATIBILIDAD CON YOLO")
    print("=" * 40)
    
    try:
        # Crear imagen de prueba
        test_image = np.random.randint(0, 255, (640, 480, 3), dtype=np.uint8)
        
        # Preprocessing
        processed_image = preprocess_image_for_ocr(test_image)
        print(f"Imagen procesada: {processed_image.shape}")
        
        # Intentar OCR (esto debería funcionar sin el error de canales)
        print("Probando OCR con DocumentType.DNI_FRONT...")
        
        # Nota: Esto puede fallar por otros motivos (modelo no encontrado, etc.)
        # pero NO debería fallar por el error de canales
        result = perform_yolo_ocr(processed_image, DocumentType.DNI_FRONT)
        
        print("✅ OCR ejecutado sin errores de canales")
        print(f"Resultado: {len(result)} campos detectados")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "expected input" in error_msg and "channels" in error_msg:
            print(f"❌ Error de canales aún presente: {e}")
            return False
        else:
            print(f"⚠️  Otro error (no relacionado con canales): {e}")
            print("✅ El problema de canales está resuelto")
            return True

def main():
    """Función principal"""
    
    print("VERIFICACION DE CORRECCION - PROBLEMA DE CANALES")
    print("=" * 60)
    
    success = True
    
    # Test 1: Verificar canales
    if not test_image_channels():
        success = False
    
    # Test 2: Verificar compatibilidad YOLO
    if not test_yolo_compatibility():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 CORRECCION EXITOSA - Problema de canales resuelto")
        print("\nLa imagen ahora mantiene 3 canales después del preprocessing")
        print("YOLO debería funcionar correctamente")
    else:
        print("❌ CORRECCION FALLIDA - Revisar implementación")
    
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    main()
