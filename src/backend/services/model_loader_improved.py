from ultralytics import YOLO
import os
import logging
from config import YOLO_MODELS_PATH

logger = logging.getLogger(__name__)

# Cache para modelos cargados
_yolo_model_cache = {}

def load_yolo_model(model_name: str) -> YOLO:
    """
    Carga un modelo YOLOv8 desde el disco y lo cachea.
    `model_name` debe ser el nombre del archivo del modelo (ej. 'document_detector/weights/best.pt').
    """
    if model_name not in _yolo_model_cache:
        model_path = os.path.join(YOLO_MODELS_PATH, model_name)
        
        # Verificar si el archivo existe
        if not os.path.exists(model_path):
            # Buscar en subdirectorios
            found_path = None
            for root, dirs, files in os.walk(YOLO_MODELS_PATH):
                for file in files:
                    if file == os.path.basename(model_name):
                        found_path = os.path.join(root, file)
                        break
                if found_path:
                    break
            
            if found_path:
                model_path = found_path
                logger.info(f"📁 Modelo encontrado en: {model_path}")
            else:
                raise FileNotFoundError(f"Modelo YOLO '{model_name}' no encontrado en {YOLO_MODELS_PATH}")
        
        logger.info(f"🔄 Cargando modelo: {model_path}")
        _yolo_model_cache[model_name] = YOLO(model_path)
        logger.info(f"✅ Modelo cargado: {model_name}")
    
    return _yolo_model_cache[model_name]

def get_available_models():
    """Retorna lista de modelos disponibles"""
    models = []
    for root, dirs, files in os.walk(YOLO_MODELS_PATH):
        for file in files:
            if file.endswith('.pt'):
                rel_path = os.path.relpath(os.path.join(root, file), YOLO_MODELS_PATH)
                models.append(rel_path)
    return sorted(models)

def load_best_model():
    """Carga el mejor modelo disponible"""
    available_models = get_available_models()
    
    # Prioridad de modelos
    priority_models = [
        "document_detector/weights/best.pt",
        "dni_quick/weights/best.pt",
        "quick_15ep/weights/best.pt",
        "dni_test/weights/best.pt"
    ]
    
    for model_name in priority_models:
        if model_name in available_models:
            try:
                return load_yolo_model(model_name)
            except Exception as e:
                logger.warning(f"⚠️ Error cargando {model_name}: {e}")
                continue
    
    # Si no se encuentra ninguno prioritario, usar el primero disponible
    if available_models:
        return load_yolo_model(available_models[0])
    
    raise RuntimeError("No se encontraron modelos YOLO disponibles")
