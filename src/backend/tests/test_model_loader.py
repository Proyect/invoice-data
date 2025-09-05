import sys
import os
from dotenv import load_dotenv
load_dotenv()
project_root = os.getenv("PROJECT_ROOT")
if project_root and project_root not in sys.path:
    sys.path.append(project_root)

from services.model_loader import load_yolo_model

def test_load_model():
    # Cambia el path/modelo según lo que uses en tu proyecto
    model_path = "yolov8n.pt"
    model = load_yolo_model(model_path)
    print("Modelo cargado:", model)
    assert model is not None

if __name__ == "__main__":
    test_load_model()