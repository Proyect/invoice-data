Entrenamiento con RT-DETR (Ultralytics)

Requisitos
- Dataset con anotaciones formato YOLO: carpetas `train/images`, `train/labels`, `val/images`, `val/labels`.
- Clases sugeridas: `invoice_number`, `issuer_name`, `issue_date`, `total_amount`.
- Archivo `data/invoice_dataset.yaml` apuntando a las rutas del dataset.

Instalación local
1) `cd backend && python -m venv .venv && source .venv/bin/activate`
2) `pip install -r requirements.txt`

Comandos de entrenamiento
- RT-DETR large (recomendado):
```
yolo detect train data=../data/invoice_dataset.yaml model=rtdetr-l.pt imgsz=1024 epochs=50 batch=8 device=auto name=invoice_rtdetr_l
```
- RT-DETR x (más grande):
```
yolo detect train data=../data/invoice_dataset.yaml model=rtdetr-x.pt imgsz=1280 epochs=60 batch=8 device=auto name=invoice_rtdetr_x
```

Reanudar/validar
```
yolo detect val model=runs/detect/invoice_rtdetr_l/weights/best.pt data=../data/invoice_dataset.yaml imgsz=1024
```

Exportar
```
yolo export model=runs/detect/invoice_rtdetr_l/weights/best.pt format=onnx opset=13 dynamic=True
```

Uso en la API
- Copiar el peso final a `models/best.pt` y configurar `.env`:
```
MODEL_WEIGHTS=models/best.pt
```
- Reiniciar el servicio.

Notas
- Ajusta `imgsz`, `epochs`, `batch` según tu GPU/CPU.
- Para PDFs, la API convierte la primera página a imagen (pdf2image/poppler requerido).

