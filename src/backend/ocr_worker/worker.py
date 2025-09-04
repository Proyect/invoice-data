# --- Configuración de la Ruta del Modelo ---
import os

BASE_MODEL_DIR = "/app/models/yolo_models"
YOLO_MODEL_NAME = "best.pt"  # ¡DEBE COINCIDIR CON EL NOMBRE DEL ARCHIVO QUE PUSISTE EN 1.1!
YOLO_MODEL_PATH = os.path.join(BASE_MODEL_DIR, YOLO_MODEL_NAME)