import sys
import os
import cv2
import numpy as np
from dotenv import load_dotenv

# Configurar el path del proyecto
load_dotenv()
project_root = os.getenv("PROJECT_ROOT")
if project_root and project_root not in sys.path:
    sys.path.append(project_root)

from services.preprocessing_service import (
    preprocess_image_for_ocr, 
    deskew_image, 
    correct_perspective
)

def test_preprocess_image_for_ocr():
    """Test de la función principal de preprocesamiento"""
    print("Testing preprocess_image_for_ocr...")
    
    # Usa una imagen de prueba
    image_path = os.path.join(project_root, "src", "backend", "tests", "test_invoice.jpg")
    img = cv2.imread(image_path)
    assert img is not None, f"No se pudo cargar la imagen de prueba en {image_path}"

    # Test con imagen válida
    processed = preprocess_image_for_ocr(img)
    assert isinstance(processed, np.ndarray), "El resultado debe ser un array de NumPy"
    assert len(processed.shape) == 2, "La imagen procesada debe ser en escala de grises (2D)"
    assert processed.dtype == np.uint8, "La imagen procesada debe ser uint8"
    
    # Verifica que la imagen tenga valores binarios (0 y 255)
    unique_vals = np.unique(processed)
    assert set(unique_vals).issubset({0, 255}), "La imagen debe estar binarizada (solo 0 y 255)"
    
    # Test con imagen None
    try:
        preprocess_image_for_ocr(None)
        assert False, "Debería haber lanzado ValueError para imagen None"
    except ValueError as e:
        assert "Input image is None" in str(e), f"Error inesperado: {e}"
    
    print("✓ Test de preprocesamiento de imagen para OCR exitoso.")

def test_deskew_image():
    """Test de la función de corrección de inclinación"""
    print("Testing deskew_image...")
    
    # Crear una imagen de prueba con texto inclinado
    img = np.zeros((100, 200), dtype=np.uint8)
    # Dibujar algunas líneas que simulen texto inclinado
    cv2.line(img, (10, 20), (50, 30), 255, 2)
    cv2.line(img, (10, 40), (50, 50), 255, 2)
    cv2.line(img, (10, 60), (50, 70), 255, 2)
    
    # Test con imagen válida
    deskewed = deskew_image(img)
    assert isinstance(deskewed, np.ndarray), "El resultado debe ser un array de NumPy"
    assert deskewed.shape == img.shape, "La imagen debe mantener las mismas dimensiones"
    assert deskewed.dtype == np.uint8, "La imagen debe ser uint8"
    
    # Test con imagen sin suficiente contenido
    empty_img = np.zeros((50, 50), dtype=np.uint8)
    result = deskew_image(empty_img)
    assert np.array_equal(result, empty_img), "Imagen vacía debe retornarse sin cambios"
    
    print("✓ Test de corrección de inclinación exitoso.")

def test_correct_perspective():
    """Test de la función de corrección de perspectiva"""
    print("Testing correct_perspective...")
    
    # Crear una imagen de prueba con contornos
    img = np.zeros((100, 200), dtype=np.uint8)
    # Dibujar un rectángulo que simule un documento
    cv2.rectangle(img, (20, 20), (180, 80), 255, -1)
    
    # Test con imagen válida
    corrected = correct_perspective(img)
    assert isinstance(corrected, np.ndarray), "El resultado debe ser un array de NumPy"
    assert corrected.dtype == np.uint8, "La imagen debe ser uint8"
    
    # Test con imagen sin contornos
    empty_img = np.zeros((50, 50), dtype=np.uint8)
    result = correct_perspective(empty_img)
    assert np.array_equal(result, empty_img), "Imagen sin contornos debe retornarse sin cambios"
    
    print("✓ Test de corrección de perspectiva exitoso.")

def test_integration_preprocessing():
    """Test de integración de todo el pipeline de preprocesamiento"""
    print("Testing integration preprocessing...")
    
    # Cargar imagen real
    image_path = os.path.join(project_root, "src", "backend", "tests", "test_invoice.jpg")
    img = cv2.imread(image_path)
    assert img is not None, f"No se pudo cargar la imagen de prueba en {image_path}"
    
    # Pipeline completo
    processed = preprocess_image_for_ocr(img)
    deskewed = deskew_image(processed)
    corrected = correct_perspective(deskewed)
    
    # Verificaciones
    assert isinstance(processed, np.ndarray), "Procesamiento principal debe retornar array"
    assert isinstance(deskewed, np.ndarray), "Corrección de inclinación debe retornar array"
    assert isinstance(corrected, np.ndarray), "Corrección de perspectiva debe retornar array"
    
    # Verificar que todas las imágenes son binarias
    for img_name, img_array in [("processed", processed), ("deskewed", deskewed), ("corrected", corrected)]:
        unique_vals = np.unique(img_array)
        assert set(unique_vals).issubset({0, 255}), f"Imagen {img_name} debe estar binarizada"
    
    print("✓ Test de integración de preprocesamiento exitoso.")

def test_edge_cases():
    """Test de casos extremos"""
    print("Testing edge cases...")
    
    # Test con imagen muy pequeña
    small_img = np.zeros((10, 10), dtype=np.uint8)
    cv2.rectangle(small_img, (2, 2), (8, 8), 255, -1)
    
    processed = preprocess_image_for_ocr(small_img)
    assert processed.shape == (10, 10), "Imagen pequeña debe mantener dimensiones"
    
    # Test con imagen muy grande (simulada)
    large_img = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
    processed = preprocess_image_for_ocr(large_img)
    assert processed.shape == (1000, 1000), "Imagen grande debe mantener dimensiones"
    
    print("✓ Test de casos extremos exitoso.")

if __name__ == "__main__":
    print("Ejecutando tests del servicio de preprocesamiento...")
    print("=" * 50)
    
    try:
        test_preprocess_image_for_ocr()
        test_deskew_image()
        test_correct_perspective()
        test_integration_preprocessing()
        test_edge_cases()
        
        print("=" * 50)
        print("🎉 Todos los tests del servicio de preprocesamiento pasaron exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en los tests: {e} \n")
        import traceback
        traceback.print_exc()