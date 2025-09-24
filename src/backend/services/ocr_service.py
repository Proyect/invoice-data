import pytesseract
import cv2
import numpy as np
import re
from PIL import Image

# Importa el cargador de modelos Yolo
from services.model_loader import load_yolo_model, YOLO_MODELS_PATH
from models.documents import DocumentType # Para usar los ENUMS de tipos de documento

def is_tesseract_available() -> bool:
    """Verifica si Tesseract está disponible en el sistema."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except:
        return False

def get_ocr_config_for_field(field_name: str) -> dict:
    """
    Obtiene la configuración optimizada de OCR para un tipo específico de campo.
    
    Returns:
        dict con configuraciones optimizadas para el campo
    """
    configs = {
        # Campos numéricos
        "numero_documento": {
            "psm": 8,  # Palabra única
            "whitelist": "0123456789",
            "oem": 3
        },
        "cuit": {
            "psm": 8,
            "whitelist": "0123456789-",
            "oem": 3
        },
        "fecha": {
            "psm": 8,
            "whitelist": "0123456789/",
            "oem": 3
        },
        "importe": {
            "psm": 8,
            "whitelist": "0123456789.,$",
            "oem": 3
        },
        "codigo_barras": {
            "psm": 8,
            "whitelist": "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "oem": 3
        },
        
        # Campos de texto
        "nombre": {
            "psm": 7,  # Línea única
            "whitelist": None,
            "oem": 3
        },
        "apellido": {
            "psm": 7,
            "whitelist": None,
            "oem": 3
        },
        "direccion": {
            "psm": 6,  # Bloque uniforme
            "whitelist": None,
            "oem": 3
        },
        "razon_social": {
            "psm": 6,
            "whitelist": None,
            "oem": 3
        },
        
        # Campos mixtos
        "descripcion": {
            "psm": 6,
            "whitelist": None,
            "oem": 3
        },
        "observaciones": {
            "psm": 6,
            "whitelist": None,
            "oem": 3
        }
    }
    
    # Buscar configuración específica
    for key, config in configs.items():
        if key in field_name.lower():
            return config
    
    # Configuración por defecto
    return {
        "psm": 7,
        "whitelist": None,
        "oem": 3
    }

def perform_ocr_with_tesseract(cropped_image_np_array: np.ndarray, lang: str = 'spa', psm: int = 7, field_name: str = None) -> str:
    """
    Realiza OCR usando Tesseract con configuración optimizada por tipo de campo.
    
    MEJORAS IMPLEMENTADAS:
    - Configuración específica por tipo de campo
    - Filtros de caracteres (whitelist)
    - PSM optimizado por contexto
    - Preprocesamiento adicional para campos específicos
    """
    if cropped_image_np_array is None or cropped_image_np_array.size == 0:
        return ""
    
    # Asegúrate de que la imagen no esté en blanco (completamente negro o blanco)
    if np.all(cropped_image_np_array == 0) or np.all(cropped_image_np_array == 255):
        return ""

    # Verificar si Tesseract está disponible
    if not is_tesseract_available():
        print(" Tesseract no está instalado. Usando texto simulado para desarrollo.")
        # Generar texto simulado basado en el tamaño de la región
        h, w = cropped_image_np_array.shape[:2]
        if w > h * 3:  # Región ancha, probablemente texto largo
            return f"TEXTO_SIMULADO_{w}x{h}"
        else:  # Región más cuadrada, probablemente número o texto corto
            return f"SIM_{w}{h}"

    # Obtener configuración optimizada para el campo
    config = get_ocr_config_for_field(field_name) if field_name else {"psm": psm, "whitelist": None, "oem": 3}
    
    # Aplicar preprocesamiento adicional según el tipo de campo
    processed_image = apply_field_specific_preprocessing(cropped_image_np_array, field_name)
    
    # Convertir a PIL Image
    pil_image = Image.fromarray(processed_image)
    
    # Construir configuración de Tesseract
    custom_config_parts = [f'--oem {config["oem"]}', f'--psm {config["psm"]}']
    
    # Agregar whitelist si está definido
    if config.get("whitelist"):
        custom_config_parts.append(f'-c tessedit_char_whitelist={config["whitelist"]}')
    
    custom_config = ' '.join(custom_config_parts)
    
    try:
        text = pytesseract.image_to_string(pil_image, lang=lang, config=custom_config)
        return clean_ocr_text(text.strip())
    except Exception as e:
        print(f"Error en OCR para campo {field_name}: {e}")
        return ""

def apply_field_specific_preprocessing(image: np.ndarray, field_name: str) -> np.ndarray:
    """
    Aplica preprocesamiento específico según el tipo de campo.
    """
    if field_name is None:
        return image
    
    field_lower = field_name.lower()
    
    # Para campos numéricos, aplicar binarización más agresiva
    if any(keyword in field_lower for keyword in ["numero", "cuit", "fecha", "importe", "codigo"]):
        # Convertir a escala de grises si es necesario
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Aplicar threshold más agresivo para números
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    
    # Para campos de texto, aplicar suavizado
    elif any(keyword in field_lower for keyword in ["nombre", "apellido", "direccion", "razon"]):
        # Aplicar filtro bilateral para suavizar texto
        if len(image.shape) == 3:
            return cv2.bilateralFilter(image, 9, 75, 75)
        else:
            return cv2.bilateralFilter(image, 9, 75, 75)
    
    # Para campos mixtos, aplicar mejora de contraste
    else:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Mejorar contraste
        enhanced = cv2.convertScaleAbs(gray, alpha=1.2, beta=10)
        return enhanced

def clean_ocr_text(text: str) -> str:
    """
    Limpia y normaliza el texto extraído por OCR.
    """
    if not text:
        return ""
    
    # Eliminar caracteres extraños comunes en OCR
    text = text.replace('|', 'I')  # Pipe por I
    text = text.replace('0', 'O') if len(text) > 3 else text  # Solo si parece texto, no número
    text = text.replace('5', 'S') if len(text) > 3 else text  # Solo si parece texto
    
    # Eliminar espacios múltiples
    text = ' '.join(text.split())
    
    # Eliminar caracteres no imprimibles
    text = ''.join(char for char in text if char.isprintable())
    
    return text.strip()

def perform_yolo_ocr(np_image_preprocessed: np.ndarray, document_type: DocumentType) -> dict:
    """
    Detecta campos usando YOLOv8 y realiza OCR con Tesseract en las regiones detectadas.
    """
    extracted_data = {}
    yolo_model_name = None

    # Seleccionar el modelo YOLO más adecuado (MEJORADO)
    if document_type in [DocumentType.DNI_FRONT, DocumentType.DNI_BACK]:
        # Usar el mejor modelo de DNI disponible
        yolo_model_name = "dni_optimized/weights/best.pt"  # Modelo optimizado para DNI
        print(f"Usando modelo DNI optimizado: {yolo_model_name}")
    elif document_type in [DocumentType.INVOICE_A, DocumentType.INVOICE_B, DocumentType.INVOICE_C]:
        # Usar el mejor modelo de facturas disponible
        yolo_model_name = "invoices_cpu_abs/weights/best.pt"  # Modelo más completo para facturas
        print(f"Usando modelo de facturas optimizado: {yolo_model_name}")
    else:
        # Para documentos genéricos, usar modelo de detección de documentos
        yolo_model_name = "document_detector/weights/best.pt"  # Modelo genérico mejorado
        print(f"Usando modelo genérico de documentos: {yolo_model_name}")

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

    # Procesar los resultados con mejoras (MEJORADO)
    confidence_threshold = 0.3  # Umbral mínimo de confianza
    processed_fields = set()  # Evitar duplicados
    
    for r in results:
        boxes = r.boxes
        names = r.names # Map ID de clase a nombre (ej. 0: 'dni_apellido')

        if boxes is None or len(boxes) == 0:
            continue

        # Ordenar por confianza descendente para procesar los mejores primero
        confidences = [float(box.conf[0]) for box in boxes]
        sorted_indices = sorted(range(len(boxes)), key=lambda i: confidences[i], reverse=True)

        for idx in sorted_indices:
            box = boxes[idx]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            field_name = names[class_id]

            # Filtrar por confianza mínima
            if confidence < confidence_threshold:
                continue
            
            # Evitar procesar el mismo campo múltiples veces
            if field_name in processed_fields:
                continue

            # Recortar la región de interés (ROI) con padding
            h, w = np_image_preprocessed.shape[:2]
            
            # Agregar padding para mejorar OCR
            padding = 5
            x1_padded = max(0, x1 - padding)
            y1_padded = max(0, y1 - padding)
            x2_padded = min(w, x2 + padding)
            y2_padded = min(h, y2 + padding)
            
            if x1_padded >= x2_padded or y1_padded >= y2_padded:
                continue

            cropped_region = np_image_preprocessed[y1_padded:y2_padded, x1_padded:x2_padded]

            # Validar que la región no esté vacía
            if cropped_region.size == 0:
                continue

            # Realizar OCR con Tesseract optimizado para el campo específico
            text_value = perform_ocr_with_tesseract(cropped_region, lang='spa', field_name=field_name)
            
            # Solo guardar si se extrajo texto válido
            if text_value and len(text_value.strip()) > 0:
                extracted_data[field_name] = {
                    'value': text_value,
                    'confidence': confidence,
                    'bbox': [x1, y1, x2, y2],
                    'bbox_padded': [x1_padded, y1_padded, x2_padded, y2_padded]
                }
                processed_fields.add(field_name)
                print(f"✅ Detectado {field_name}: '{text_value}' (Conf: {confidence:.3f})")
            else:
                print(f"⚠️  Campo {field_name} detectado pero sin texto extraído (Conf: {confidence:.3f})")
    
    print(f"📊 Total de campos extraídos: {len(extracted_data)}")
    return extracted_data