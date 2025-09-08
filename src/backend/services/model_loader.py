from ultralytics import YOLO
import os
from config import YOLO_MODELS_PATH

# Ruta base donde se almacenan los modelos YOLO
# Usar ruta absoluta desde config.py
YOLO_MODELS = YOLO_MODELS_PATH

# Cache para modelos cargados
_yolo_model_cache = {}

def load_yolo_model(model_name: str) -> YOLO:
    """
    Carga un modelo YOLOv8 desde el disco y lo cachea.
    `model_name` debe ser el nombre del archivo del modelo (ej. 'yolov8n.pt').
    """
    if model_name not in _yolo_model_cache:
        model_path = os.path.join(YOLO_MODELS, model_name)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo YOLO '{model_name}' no encontrado en {YOLO_MODELS}")
        _yolo_model_cache[model_name] = YOLO(model_path)
    return _yolo_model_cache[model_name]



# Por ejemplo, al importar este módulo en ocr_worker.py:
# DNI_YOLO_MODEL = load_yolo_model("dni_yolov8.pt") # Esto fallará hasta que entrenes tu modelo
# INVOICE_YOLO_MODEL = load_yolo_model("invoice_yolov8.pt") # Esto fallará hasta que entrenes tu modelo