import pytesseract
import cv2
import numpy as np
import re
from PIL import Image

# Importa el cargador de modelos Yolo
from services.model_loader import load_yolo_model, YOLO_MODELS_PATH
from models.documents import DocumentType # Para usar los ENUMS de tipos de documento

def perform_ocr_with_tesseract(cropped_image_np_array: np.ndarray, lang: str = 'spa', psm: int = 7) -> str:
    """
    Realiza OCR usando Tesseract en una imagen recortada (array de NumPy).
    PSM 7: Trata la imagen como una sola línea de texto.
    PSM 8: Trata la imagen como una sola palabra.
    Estos son buenos para regiones ya detectadas.
    """
    if cropped_image_np_array is None or cropped_image_np_array.size == 0:
        return ""
    
    # Asegúrate de que la imagen no esté en blanco (completamente negro o blanco)
    if np.all(cropped_image_np_array == 0) or np.all(cropped_image_np_array == 255):
        return ""

    pil_image = Image.fromarray(cropped_image_np_array)
    custom_config = f'--oem 3 --psm {psm}' # OEM 3 para motor LSTM, PSM según el campo
    text = pytesseract.image_to_string(pil_image, lang=lang, config=custom_config)
    return text.strip()

def perform_yolo_ocr(np_image_preprocessed: np.ndarray, document_type: DocumentType) -> dict:
    """
    Detecta campos usando YOLOv8 y realiza OCR con Tesseract en las regiones detectadas.
    """
    extracted_data = {}
    yolo_model_name = None

    # Seleccionar el modelo YOLO adecuado
    if document_type in [DocumentType.DNI_FRONT, DocumentType.DNI_BACK]:
        yolo_model_name = "dni_yolov8.pt" # Aquí tu modelo entrenado para DNI
    elif document_type in [DocumentType.INVOICE_A, DocumentType.INVOICE_B, DocumentType.INVOICE_C]:
        yolo_model_name = "invoices_cpu_abs/weights/best.pt" # Tu modelo entrenado para facturas
    else:
        # Para el desarrollo inicial, usa un modelo genérico
        print(f"Advertencia: Tipo de documento {document_type} no tiene un modelo YOLO específico. Usando yolov8n.pt")
        yolo_model_name = "yolov8n.pt" # Modelo genérico solo para pruebas, NO para prod.

    try:
        yolo_model = load_yolo_model(yolo_model_name)
    except FileNotFoundError as e:
        print(f"Error al cargar modelo YOLO: {e}. Asegúrate de que los modelos estén en {YOLO_MODELS_PATH}")
        # Fallback: Si no hay modelo YOLO, intentar OCR genérico (menos preciso)
        # O simplemente lanzar el error para que el worker lo marque como fallido
        extracted_data['full_text_fallback'] = perform_ocr_with_tesseract(np_image_preprocessed, psm=3)
        return extracted_data

    # Realizar inferencia
    results = yolo_model(np_image_preprocessed)

    # Procesar los resultados
    for r in results:
        boxes = r.boxes
        names = r.names # Map ID de clase a nombre (ej. 0: 'dni_apellido')

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            field_name = names[class_id]

            # Recortar la región de interés (ROI) de la imagen preprocesada
            # Asegurarse de que las coordenadas sean válidas
            h, w = np_image_preprocessed.shape[:2]
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)
            
            if x1 >= x2 or y1 >= y2: # Región inválida
                continue

            cropped_region = np_image_preprocessed[y1:y2, x1:x2]

            # Realizar OCR con Tesseract en la región recortada
            # Puedes ajustar el PSM según el tipo de campo
            psm_mode = 7 # Por defecto, una línea
            # Ej: if "numero" in field_name: psm_mode = 8 # para palabras
            text_value = perform_ocr_with_tesseract(cropped_region, lang='spa', psm=psm_mode)
            
            # Guardar el resultado y la confianza
            extracted_data[field_name] = {
                'value': text_value,
                'confidence': confidence,
                'bbox': [x1, y1, x2, y2]
            }
            print(f"Detectado {field_name}: '{text_value}' (Conf: {confidence:.2f})")
    
    return extracted_data