import cv2
import numpy as np

def preprocess_image_for_ocr(np_image: np.ndarray) -> np.ndarray:
    """
    Realiza un preprocesamiento avanzado en una imagen para mejorar la precisión del OCR.
    Acepta una imagen OpenCV (np.ndarray) y retorna una imagen preprocesada.
    IMPORTANTE: Mantiene 3 canales RGB para compatibilidad con YOLO.
    
    MEJORAS IMPLEMENTADAS:
    - Filtro bilateral para reducción de ruido
    - Corrección de perspectiva mejorada
    - Mejora de contraste adaptativa
    - Binarización optimizada
    - Morfología para limpieza
    """
    if np_image is None:
        raise ValueError("Input image is None.")

    # Asegurar que la imagen tenga 3 canales (RGB/BGR)
    if len(np_image.shape) == 2:
        # Si es escala de grises, convertir a 3 canales
        np_image = cv2.cvtColor(np_image, cv2.COLOR_GRAY2BGR)
    elif np_image.shape[2] == 4:
        # Si tiene canal alpha, convertir a BGR
        np_image = cv2.cvtColor(np_image, cv2.COLOR_BGRA2BGR)

    # 1. Crear versión en escala de grises para procesamiento
    gray = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)

    # 2. Reducción de ruido con filtro bilateral (MEJORADO)
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # 3. Corrección de perspectiva mejorada
    doc_aligned = correct_perspective_improved(denoised)
    
    # 4. Corrección de rotación mejorada
    processed_gray = deskew_image_improved(doc_aligned)

    # 5. Mejora de contraste adaptativa (MEJORADO)
    enhanced = cv2.convertScaleAbs(processed_gray, alpha=1.2, beta=10)
    
    # 6. Binarización Adaptativa mejorada (MEJORADO)
    binary_image = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 15, 2)
    
    # 7. Morfología para limpiar (NUEVO)
    kernel = np.ones((2,2), np.uint8)
    cleaned = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)
    
    # 8. Convertir de vuelta a 3 canales para YOLO
    final_processed_image = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)

    return final_processed_image

def deskew_image(image: np.ndarray) -> np.ndarray:
    # corrección de rotación
    img = cv2.bitwise_not(image)
    coords = np.column_stack(np.where(img > 0))
    if len(coords) < 10:
        return image  # No enough text to determine skew
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    # Rotar la imagen para corregir la inclinación
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)   
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
#
def correct_perspective(image: np.ndarray) -> np.ndarray:
    #corrección de perspectiva
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image
    
    largest_contour = max(contours, key=cv2.contourArea)
    # Aproxima el contorno a un polígono de 4 lados (esquina)
    perimeter = cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, 0.02 * perimeter, True)
    if len(approx) == 4:
        # Reordena los puntos para que la transformación funcione
        # (superior-izq, superior-der, inferior-der, inferior-izq)
        points = approx.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        
        s = points.sum(axis=1)
        rect[0] = points[np.argmin(s)]
        rect[2] = points[np.argmax(s)]
        
        diff = np.diff(points, axis=1)
        rect[1] = points[np.argmin(diff)]
        rect[3] = points[np.argmax(diff)]
        
        # Calcula las dimensiones del nuevo documento
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        # Define los puntos de destino para la transformación
        dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
        
        # Obtiene la matriz de transformación y aplica la corrección
        M = cv2.getPerspectiveTransform(rect, dst)
        image = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return image

def correct_perspective_improved(image: np.ndarray) -> np.ndarray:
    """
    Versión mejorada de corrección de perspectiva
    - Mejor detección de contornos
    - Filtrado de contornos pequeños
    - Validación de geometría
    """
    # Aplicar blur para suavizar contornos
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Encontrar contornos con mejor precisión
    contours, _ = cv2.findContours(blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image
    
    # Filtrar contornos pequeños y encontrar el más grande
    min_area = image.shape[0] * image.shape[1] * 0.1  # 10% del área de la imagen
    valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
    
    if not valid_contours:
        return image
    
    largest_contour = max(valid_contours, key=cv2.contourArea)
    
    # Aproximación más precisa del contorno
    epsilon = 0.015 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
    
    if len(approx) == 4:
        # Validar que los puntos formen un rectángulo válido
        points = approx.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        
        s = points.sum(axis=1)
        rect[0] = points[np.argmin(s)]  # top-left
        rect[2] = points[np.argmax(s)]  # bottom-right
        
        diff = np.diff(points, axis=1)
        rect[1] = points[np.argmin(diff)]  # top-right
        rect[3] = points[np.argmax(diff)]  # bottom-left
        
        # Calcular dimensiones con validación
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        # Validar dimensiones mínimas
        if maxWidth < 100 or maxHeight < 100:
            return image
        
        # Definir puntos de destino
        dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
        
        # Aplicar transformación de perspectiva
        M = cv2.getPerspectiveTransform(rect, dst)
        corrected = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        return corrected
    
    return image

def deskew_image_improved(image: np.ndarray) -> np.ndarray:
    """
    Versión mejorada de corrección de rotación
    - Mejor detección de ángulo de rotación
    - Filtrado de ruido
    - Validación de ángulos
    """
    # Aplicar filtro para reducir ruido antes de detectar rotación
    filtered = cv2.medianBlur(image, 3)
    
    # Invertir imagen para detectar texto
    img = cv2.bitwise_not(filtered)
    
    # Encontrar coordenadas de píxeles no cero
    coords = np.column_stack(np.where(img > 0))
    
    if len(coords) < 50:  # Necesitamos suficientes puntos para detectar rotación
        return image
    
    try:
        # Calcular el rectángulo de área mínima
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        
        # Normalizar ángulo
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Solo corregir si el ángulo es significativo (> 0.5 grados)
        if abs(angle) > 0.5:
            # Rotar la imagen
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
        
        return image
        
    except Exception:
        # Si hay error en la detección de rotación, retornar imagen original
        return image 