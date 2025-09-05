from dotenv import load_dotenv
import os
import sys
load_dotenv()
project_root = os.getenv("PROJECT_ROOT")
if project_root and project_root not in sys.path:
    sys.path.append(project_root)

import cv2
import numpy as np
from services.ocr_service import perform_ocr_with_tesseract, perform_yolo_ocr
from models.documents import DocumentType

def test_perform_ocr_with_tesseract():
    image_path = os.path.join(project_root, "src", "backend", "tests", "test_invoice.jpg")
    img = cv2.imread(image_path)
    assert img is not None, "No se pudo cargar la imagen de prueba"
    text = perform_ocr_with_tesseract(img, lang='spa', psm=7)
    print("Texto extraído con Tesseract:", text)
    assert len(text.strip()) > 0, "El resultado OCR está vacío"

def test_perform_yolo_ocr():
    image_path = os.path.join(project_root, "src", "backend", "tests", "test_invoice.jpg")
    img = cv2.imread(image_path)
    assert img is not None, "No se pudo cargar la imagen de prueba"
    # Usa un tipo de documento genérico para probar el fallback si no tienes modelos YOLO entrenados
    result = perform_yolo_ocr(img, DocumentType.INVOICE_A)
    print("Resultado YOLO OCR:", result)
    assert isinstance(result, dict), "El resultado debe ser un diccionario"
    assert len(result) > 0, "El resultado YOLO OCR está vacío"

if __name__ == "__main__":
    print("First test \n")
    test_perform_ocr_with_tesseract()
    print("Second test \n")
    test_perform_yolo_ocr() #not finished yet