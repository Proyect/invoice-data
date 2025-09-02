import cv2
import numpy as np

def preprocess_image_for_ocr(np_image: np.ndarray) -> np.ndarray:
    """
    Realiza un preprocesamiento básico en una imagen para mejorar la precisión del OCR.
    Acepta una imagen OpenCV (np.ndarray) y retorna una imagen preprocesada.
    """
    if np_image is None:
        raise ValueError("Input image is None.")

    # 1. Escala de grises
    gray = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)

    # 2. Suavizado para reducir ruido (Filtro Gaussiano)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Binarización Adaptativa
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

    # --- Placeholder para funciones avanzadas de corrección ---
    # Estas funciones serían complejas y podrían merecer sus propios módulos
    # doc_aligned = deskew_image(binary)
    # final_processed_image = correct_perspective(doc_aligned)

    return binary

# Puedes añadir stubs o implementaciones básicas aquí para deskew_image y correct_perspective
# def deskew_image(image: np.ndarray) -> np.ndarray:
#     # Implementar corrección de rotación aquí
#     return image
#
# def correct_perspective(image: np.ndarray) -> np.ndarray:
#     # Implementar corrección de perspectiva aquí
#     return image