from ultralytics import YOLO
import os
import logging
from pathlib import Path
from config import YOLO_MODELS_PATH

logger = logging.getLogger(__name__)

# Cache para modelos cargados
_yolo_model_cache = {}

def get_models_path():
    """Obtiene la ruta de modelos de forma robusta"""
    # Usar la configuración del sistema
    if YOLO_MODELS_PATH and os.path.exists(YOLO_MODELS_PATH):
        return YOLO_MODELS_PATH
    
    # Intentar desde variable de entorno
    env_path = os.getenv('YOLO_MODELS_PATH')
    if env_path and os.path.exists(env_path):
        return env_path
    
    # Ruta por defecto relativa al script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, '..', 'models', 'yolo_models')
    default_path = os.path.abspath(default_path)
    
    if os.path.exists(default_path):
        return default_path
    
    # Buscar en directorio actual
    current_path = os.path.join(os.getcwd(), 'models', 'yolo_models')
    if os.path.exists(current_path):
        return current_path
    
    # Último recurso: directorio models en el mismo nivel
    fallback_path = os.path.join(script_dir, 'models', 'yolo_models')
    return fallback_path

def load_yolo_model(model_name: str) -> YOLO:
    """
    Carga un modelo YOLOv8 desde el disco y lo cachea.
    `model_name` debe ser el nombre del archivo del modelo (ej. 'document_detector/weights/best.pt').
    """
    if model_name not in _yolo_model_cache:
        models_path = get_models_path()
        model_path = os.path.join(models_path, model_name)
        
        logger.info(f"🔍 Buscando modelo: {model_name}")
        logger.info(f"📁 Ruta base: {models_path}")
        logger.info(f"📄 Ruta completa: {model_path}")
        
        # Verificar si el archivo existe
        if not os.path.exists(model_path):
            # Buscar en subdirectorios
            found_path = None
            for root, dirs, files in os.walk(models_path):
                for file in files:
                    if file == os.path.basename(model_name):
                        found_path = os.path.join(root, file)
                        break
                if found_path:
                    break
            
            if found_path:
                model_path = found_path
                logger.info(f"✅ Modelo encontrado en: {model_path}")
            else:
                # Listar archivos disponibles para debug
                available_files = []
                for root, dirs, files in os.walk(models_path):
                    for file in files:
                        if file.endswith('.pt'):
                            rel_path = os.path.relpath(os.path.join(root, file), models_path)
                            available_files.append(rel_path)
                
                logger.error(f"❌ Modelo '{model_name}' no encontrado en {models_path}")
                logger.error(f"📋 Archivos disponibles:")
                for file in sorted(available_files):
                    logger.error(f"   - {file}")
                
                raise FileNotFoundError(f"Modelo YOLO '{model_name}' no encontrado en {models_path}")
        
        logger.info(f"🔄 Cargando modelo: {model_path}")
        _yolo_model_cache[model_name] = YOLO(model_path)
        logger.info(f"✅ Modelo cargado exitosamente: {model_name}")
    
    return _yolo_model_cache[model_name]

def get_available_models():
    """Retorna lista de modelos disponibles"""
    models = []
    models_path = get_models_path()
    
    if os.path.exists(models_path):
        for root, dirs, files in os.walk(models_path):
            for file in files:
                if file.endswith('.pt'):
                    rel_path = os.path.relpath(os.path.join(root, file), models_path)
                    models.append(rel_path)
    
    return sorted(models)

def load_best_model():
    """Carga el mejor modelo disponible"""
    available_models = get_available_models()
    
    if not available_models:
        raise RuntimeError("No se encontraron modelos YOLO disponibles")
    
    # Prioridad de modelos
    priority_models = [
        "document_detector/weights/best.pt",
        "dni_quick/weights/best.pt",
        "quick_15ep/weights/best.pt",
        "dni_test/weights/best.pt",
        "invoices_cpu_abs/weights/best.pt"
    ]
    
    for model_name in priority_models:
        if model_name in available_models:
            try:
                return load_yolo_model(model_name)
            except Exception as e:
                logger.warning(f"⚠️ Error cargando {model_name}: {e}")
                continue
    
    # Si no se encuentra ninguno prioritario, usar el primero disponible
    return load_yolo_model(available_models[0])
