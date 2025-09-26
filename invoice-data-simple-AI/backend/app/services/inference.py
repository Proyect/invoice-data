import os
import io
from typing import Tuple, List, Dict
import numpy as np
from PIL import Image
from ultralytics import YOLO


_MODEL_PATH = os.getenv("MODEL_WEIGHTS", "models/rtdetr-l.pt")
_PROVIDER = "mock"
_MODEL = None


def _try_load_model() -> None:
    global _MODEL, _PROVIDER
    if _MODEL is not None:
        return
    if os.path.exists(_MODEL_PATH):
        try:
            _MODEL = YOLO(_MODEL_PATH)
            _PROVIDER = "rtdetr"
        except Exception:
            _MODEL = None
            _PROVIDER = "mock"
    else:
        _PROVIDER = "mock"


def get_provider_name() -> str:
    _try_load_model()
    return _PROVIDER


async def run_inference(content: bytes, filename: str, document_type: str, conf: float, iou: float) -> Tuple[List[dict], Dict[str, str]]:
    _try_load_model()

    image = _bytes_to_image(content, filename)

    if _MODEL is None:
        detections = [
            {"cls": 0, "name": "invoice_number", "conf": 0.99, "xyxy": [50, 50, 300, 120]},
            {"cls": 1, "name": "issuer_name", "conf": 0.95, "xyxy": [60, 130, 600, 200]},
        ]
        fields = {
            "invoice_number": "F-000123",
            "issuer_name": "ACME S.A.",
            "issue_date": "2024-01-31",
            "total_amount": "12345.67",
        }
        return detections, fields

    # Ejecutar modelo
    results = _MODEL.predict(source=image, conf=conf, iou=iou, verbose=False)

    detections: List[dict] = []
    fields: Dict[str, str] = {}

    for r in results:
        names = r.names
        if r.boxes is None:
            continue
        for b in r.boxes:
            cls_id = int(b.cls[0])
            name = names.get(cls_id, str(cls_id))
            conf_val = float(b.conf[0])
            x1, y1, x2, y2 = [int(v) for v in b.xyxy[0].tolist()]
            detections.append({"cls": cls_id, "name": name, "conf": conf_val, "xyxy": [x1, y1, x2, y2]})
            # Heurística: mapear clases a campos; OCR se podría añadir aquí o en el backend existente
            if name in ("invoice_number", "issuer_name", "issue_date", "total_amount"):
                fields[name] = fields.get(name) or f"<detected:{name}>"

    return detections, fields


def _bytes_to_image(content: bytes, filename: str) -> np.ndarray:
    ext = (filename or "").lower()
    if ext.endswith(".pdf"):
        # Tomar primera página (requiere poppler para pdf2image; simplificado: error controlado)
        try:
            from pdf2image import convert_from_bytes
            pages = convert_from_bytes(content, dpi=200, fmt="png")
            if not pages:
                raise ValueError("PDF sin páginas")
            image = np.array(pages[0])
            return image
        except Exception:
            raise ValueError("No se pudo procesar el PDF. Asegura poppler y dependencias.")
    # Imagen normal
    pil = Image.open(io.BytesIO(content)).convert("RGB")
    return np.array(pil)

