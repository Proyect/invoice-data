import sys
sys.path.append(r'c:\Users\amdiaz\Desktop\code\Python\v.13.13\invoice-data')

from src.backend.services.model_loader import load_yolo_model

def test_load_model():
    # Cambia el path/modelo según lo que uses en tu proyecto
    model_path = "yolov8n.pt"
    model = load_yolo_model(model_path)
    print("Modelo cargado:", model)
    assert model is not None

if __name__ == "__main__":
    test_load_model()