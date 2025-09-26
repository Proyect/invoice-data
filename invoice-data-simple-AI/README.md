invoice-data-simple-AI

Resumen
- API de inferencia para detección de campos en facturas usando RT-DETR (alternativa a YOLO) vía Ultralytics.
- FastAPI expone `/health` y `POST /infer` (subida de imagen/PDF). Si no hay pesos, usa modo mock.
- Diseñado para integrarse con tu frontend React existente y/o tu backend actual (FastAPI).

Inicio rápido (Docker)
1) Copiar `.env.example` a `.env` y configurar `MODEL_WEIGHTS` si tienes pesos locales (opcional).
2) `docker compose up --build`
3) Probar: `http://localhost:8010/health`

Inicio rápido (local)
1) `cd backend`
2) `python -m venv .venv && source .venv/bin/activate`
3) `pip install -r requirements.txt`
4) `uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload`

Inferencia
- `POST /infer` (multipart/form-data)
  - `file`: imagen (jpg/png) o PDF (primera página)
  - `document_type`: `invoice` | `dni_front` | `dni_back` (opcional, default `invoice`)
  - Respuesta: `{ detections: [...], fields: {...}, provider: "rtdetr|mock" }`

Entrenamiento (opcional)
- Requiere dataset con anotaciones YOLO (bounding boxes por campo) y `data/invoice_dataset.yaml` apuntando a `train/val`.
- Ejemplo (línea de comandos Ultralytics):
  - `yolo detect train data=data/invoice_dataset.yaml model=rtdetr-l.pt imgsz=1024 epochs=50 batch=8`
- Exportar a ONNX/TensorRT: `yolo export model=best.pt format=onnx`

Integración con tu sistema
- Frontend actual: cambiar la subida a llamar `POST /infer` y consumir `fields`/`detections`.
- Backend actual (opcional): crear un proxy `POST /api/v1/documents/extract` que reenvíe a este servicio y persista resultados si se desea.

Variables de entorno (.env)
- `MODEL_WEIGHTS` (opcional): ruta a `.pt` (por ejemplo `models/rtdetr-l.pt`). Si no existe, se usa modo `mock`.
- `CONF_THRESHOLD` (opcional): confianza mínima (default `0.25`).
- `IOU_THRESHOLD` (opcional): iou para NMS (default `0.45`).

Licencia
MIT

