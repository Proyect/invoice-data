# Tutorial Completo: Entrenamiento de Modelos YOLO para OCR de Documentos

## Índice
1. [Introducción](#introducción)
2. [Preparación del Entorno](#preparación-del-entorno)
3. [Recolección y Preparación de Datos](#recolección-y-preparación-de-datos)
4. [Anotación de Imágenes](#anotación-de-imágenes)
5. [Configuración del Dataset](#configuración-del-dataset)
6. [Entrenamiento del Modelo](#entrenamiento-del-modelo)
7. [Evaluación y Optimización](#evaluación-y-optimización)
8. [Integración en la Aplicación](#integración-en-la-aplicación)

## Introducción

Este tutorial te guiará para entrenar modelos YOLO personalizados para detectar campos específicos en documentos como facturas y DNIs. Tu aplicación actual necesita detectar:

**Para Facturas:**
- invoice_number (número de factura)
- date (fecha)
- vendor (proveedor)
- cuit (CUIT)
- subtotal
- tax (impuestos)
- total
- items_table (tabla de items)

**Para DNIs:**
- Número de documento
- Nombres y apellidos
- Fecha de nacimiento
- Sexo
- Fecha de vencimiento

## Preparación del Entorno

### 1. Instalación de Dependencias

```bash
# Crear entorno virtual
python -m venv yolo_training_env
source yolo_training_env/bin/activate  # Linux/Mac
# o
yolo_training_env\Scripts\activate  # Windows

# Instalar ultralytics (incluye YOLOv8)
pip install ultralytics

# Dependencias adicionales
pip install roboflow
pip install labelImg
pip install opencv-python
pip install matplotlib
pip install pandas
pip install pillow
```

### 2. Estructura de Directorios

```
yolo_training/
├── datasets/
│   ├── invoices/
│   │   ├── images/
│   │   │   ├── train/
│   │   │   ├── val/
│   │   │   └── test/
│   │   └── labels/
│   │       ├── train/
│   │       ├── val/
│   │       └── test/
│   └── dni/
│       ├── images/
│       └── labels/
├── models/
│   ├── pretrained/
│   └── trained/
├── configs/
└── scripts/
```

## Recolección y Preparación de Datos

### 1. Recolección de Imágenes

**Cantidad recomendada:**
- Mínimo: 100-200 imágenes por clase
- Recomendado: 500-1000 imágenes por clase
- Óptimo: 1000+ imágenes por clase

**Diversidad necesaria:**
- Diferentes formatos de facturas
- Distintas calidades de imagen
- Varios ángulos y orientaciones
- Diferentes iluminaciones
- Documentos escaneados vs fotografiados

### 2. Script para Organizar Imágenes

```python
# scripts/organize_dataset.py
import os
import shutil
import random
from pathlib import Path

def split_dataset(images_dir, output_dir, train_ratio=0.7, val_ratio=0.2):
    """
    Divide el dataset en train/val/test
    """
    images = list(Path(images_dir).glob("*.jpg")) + list(Path(images_dir).glob("*.png"))
    random.shuffle(images)
    
    total = len(images)
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)
    
    # Crear directorios
    for split in ['train', 'val', 'test']:
        os.makedirs(f"{output_dir}/images/{split}", exist_ok=True)
        os.makedirs(f"{output_dir}/labels/{split}", exist_ok=True)
    
    # Dividir imágenes
    splits = {
        'train': images[:train_count],
        'val': images[train_count:train_count + val_count],
        'test': images[train_count + val_count:]
    }
    
    for split, image_list in splits.items():
        for img_path in image_list:
            # Copiar imagen
            shutil.copy(img_path, f"{output_dir}/images/{split}/")
            
            # Copiar label si existe
            label_path = img_path.with_suffix('.txt')
            if label_path.exists():
                shutil.copy(label_path, f"{output_dir}/labels/{split}/")

if __name__ == "__main__":
    split_dataset(
        "raw_images/invoices",
        "datasets/invoices"
    )
```

## Anotación de Imágenes

### 1. Instalación de LabelImg

```bash
pip install labelImg
# o usar la versión web: https://www.makesense.ai/
```

### 2. Proceso de Anotación

**Pasos:**
1. Abrir LabelImg: `labelImg`
2. Configurar formato YOLO: View → Auto Save mode
3. Cambiar formato: PascalVOC → YOLO
4. Cargar directorio de imágenes
5. Para cada imagen:
   - Crear bounding box alrededor de cada campo
   - Asignar clase correspondiente
   - Guardar (Ctrl+S)

**Clases para Facturas (dataset.yaml):**
```yaml
names:
  0: invoice_number
  1: date
  2: vendor
  3: cuit
  4: subtotal
  5: tax
  6: total
  7: items_table
```

### 3. Formato de Anotaciones YOLO

Cada imagen debe tener un archivo `.txt` con el mismo nombre:
```
# ejemplo: factura001.txt
0 0.5 0.1 0.3 0.05  # invoice_number: center_x center_y width height
1 0.7 0.1 0.2 0.04  # date
2 0.3 0.2 0.4 0.06  # vendor
```

**Valores normalizados (0-1):**
- center_x, center_y: centro del bounding box
- width, height: ancho y alto del bounding box

## Configuración del Dataset

### 1. Archivo de Configuración

```yaml
# configs/invoice_dataset.yaml
path: ./datasets/invoices
train: images/train
val: images/val
test: images/test

nc: 8  # número de clases
names:
  0: invoice_number
  1: date
  2: vendor
  3: cuit
  4: subtotal
  5: tax
  6: total
  7: items_table
```

### 2. Script de Validación

```python
# scripts/validate_dataset.py
import os
from pathlib import Path
import yaml

def validate_dataset(config_path):
    """
    Valida que el dataset esté correctamente estructurado
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    dataset_path = Path(config['path'])
    
    for split in ['train', 'val', 'test']:
        img_dir = dataset_path / config[split]
        label_dir = dataset_path / 'labels' / split
        
        images = list(img_dir.glob('*.jpg')) + list(img_dir.glob('*.png'))
        labels = list(label_dir.glob('*.txt'))
        
        print(f"{split}: {len(images)} imágenes, {len(labels)} labels")
        
        # Verificar que cada imagen tenga su label
        for img in images:
            label_file = label_dir / f"{img.stem}.txt"
            if not label_file.exists():
                print(f"⚠️  Falta label para: {img.name}")

if __name__ == "__main__":
    validate_dataset("configs/invoice_dataset.yaml")
```

## Entrenamiento del Modelo

### 1. Script de Entrenamiento Básico

```python
# scripts/train_yolo.py
from ultralytics import YOLO
import torch

def train_invoice_model():
    """
    Entrena modelo YOLO para facturas
    """
    # Verificar GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Usando dispositivo: {device}")
    
    # Cargar modelo preentrenado
    model = YOLO('yolov8n.pt')  # nano version (más rápido)
    # model = YOLO('yolov8s.pt')  # small version (balance)
    # model = YOLO('yolov8m.pt')  # medium version (mejor precisión)
    
    # Entrenar
    results = model.train(
        data='configs/invoice_dataset.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        device=device,
        project='models/trained',
        name='invoice_detector',
        save_period=10,  # guardar cada 10 epochs
        patience=20,     # early stopping
        verbose=True
    )
    
    return results

if __name__ == "__main__":
    train_invoice_model()
```

### 2. Configuración Avanzada

```python
# scripts/train_advanced.py
from ultralytics import YOLO

def train_with_hyperparameters():
    model = YOLO('yolov8n.pt')
    
    # Hiperparámetros optimizados para documentos
    results = model.train(
        data='configs/invoice_dataset.yaml',
        epochs=200,
        imgsz=640,
        batch=16,
        
        # Optimización
        optimizer='AdamW',
        lr0=0.01,
        weight_decay=0.0005,
        
        # Augmentaciones específicas para documentos
        hsv_h=0.015,      # Variación de matiz (bajo para documentos)
        hsv_s=0.7,        # Saturación
        hsv_v=0.4,        # Valor/brillo
        degrees=5,        # Rotación máxima (documentos suelen estar rectos)
        translate=0.1,    # Traslación
        scale=0.2,        # Escala
        shear=2,          # Cizallamiento
        perspective=0.0,  # Sin perspectiva (documentos planos)
        flipud=0.0,       # Sin volteo vertical
        fliplr=0.0,       # Sin volteo horizontal
        mosaic=1.0,       # Mosaic augmentation
        mixup=0.1,        # Mixup
        
        # Configuración de entrenamiento
        patience=30,
        save_period=5,
        device='cuda' if torch.cuda.is_available() else 'cpu',
        workers=8,
        project='models/trained',
        name='invoice_detector_advanced'
    )
    
    return results
```

### 3. Monitoreo del Entrenamiento

```python
# scripts/monitor_training.py
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def plot_training_results(results_dir):
    """
    Visualiza los resultados del entrenamiento
    """
    results_file = Path(results_dir) / 'results.csv'
    
    if results_file.exists():
        df = pd.read_csv(results_file)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Loss
        axes[0, 0].plot(df['epoch'], df['train/box_loss'], label='Box Loss')
        axes[0, 0].plot(df['epoch'], df['train/cls_loss'], label='Class Loss')
        axes[0, 0].set_title('Training Loss')
        axes[0, 0].legend()
        
        # mAP
        axes[0, 1].plot(df['epoch'], df['metrics/mAP50'], label='mAP@0.5')
        axes[0, 1].plot(df['epoch'], df['metrics/mAP50-95'], label='mAP@0.5:0.95')
        axes[0, 1].set_title('Mean Average Precision')
        axes[0, 1].legend()
        
        # Precision & Recall
        axes[1, 0].plot(df['epoch'], df['metrics/precision'], label='Precision')
        axes[1, 0].plot(df['epoch'], df['metrics/recall'], label='Recall')
        axes[1, 0].set_title('Precision & Recall')
        axes[1, 0].legend()
        
        # Learning Rate
        axes[1, 1].plot(df['epoch'], df['lr/pg0'], label='Learning Rate')
        axes[1, 1].set_title('Learning Rate')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig(f"{results_dir}/training_plots.png")
        plt.show()
```

## Evaluación y Optimización

### 1. Script de Evaluación

```python
# scripts/evaluate_model.py
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

def evaluate_model(model_path, test_data_path):
    """
    Evalúa el modelo entrenado
    """
    model = YOLO(model_path)
    
    # Validación en dataset de test
    results = model.val(
        data='configs/invoice_dataset.yaml',
        split='test',
        imgsz=640,
        conf=0.25,
        iou=0.5
    )
    
    print(f"mAP@0.5: {results.box.map50:.3f}")
    print(f"mAP@0.5:0.95: {results.box.map:.3f}")
    
    return results

def test_inference(model_path, image_path):
    """
    Prueba inferencia en una imagen
    """
    model = YOLO(model_path)
    results = model(image_path)
    
    # Visualizar resultados
    for r in results:
        im_array = r.plot()
        im = Image.fromarray(im_array[..., ::-1])
        im.show()
        
    return results
```

### 2. Optimización de Hiperparámetros

```python
# scripts/hyperparameter_tuning.py
from ultralytics import YOLO
import optuna

def objective(trial):
    """
    Función objetivo para optimización con Optuna
    """
    # Sugerir hiperparámetros
    lr0 = trial.suggest_float('lr0', 1e-5, 1e-1, log=True)
    weight_decay = trial.suggest_float('weight_decay', 1e-5, 1e-2, log=True)
    batch_size = trial.suggest_categorical('batch', [8, 16, 32])
    
    model = YOLO('yolov8n.pt')
    
    results = model.train(
        data='configs/invoice_dataset.yaml',
        epochs=50,  # Menos epochs para tuning
        imgsz=640,
        batch=batch_size,
        lr0=lr0,
        weight_decay=weight_decay,
        device='cuda',
        verbose=False,
        project='tuning',
        name=f'trial_{trial.number}'
    )
    
    return results.results_dict['metrics/mAP50-95']

def run_hyperparameter_tuning():
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=20)
    
    print("Mejores hiperparámetros:")
    print(study.best_params)
```

## Integración en la Aplicación

### 1. Actualizar model_loader.py

```python
# Actualización para services/model_loader.py
class YOLOModelLoader:
    def __init__(self):
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """Carga los modelos YOLO entrenados"""
        model_paths = {
            'invoice': 'models/yolo_models/invoice_yolov8.pt',
            'dni': 'models/yolo_models/dni_yolov8.pt'
        }
        
        for doc_type, path in model_paths.items():
            if os.path.exists(path):
                self.models[doc_type] = YOLO(path)
                logger.info(f"Modelo {doc_type} cargado desde {path}")
            else:
                logger.warning(f"Modelo {doc_type} no encontrado en {path}")
    
    def detect_fields(self, image_path: str, document_type: str, confidence: float = 0.5):
        """
        Detecta campos en el documento usando YOLO
        """
        if document_type not in self.models:
            raise ValueError(f"Modelo para {document_type} no disponible")
        
        model = self.models[document_type]
        results = model(image_path, conf=confidence)
        
        detections = []
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    class_name = model.names[cls]
                    
                    detections.append({
                        'class': class_name,
                        'confidence': conf,
                        'bbox': [x1, y1, x2, y2]
                    })
        
        return detections
```

### 2. Script de Conversión de Modelos

```python
# scripts/convert_model.py
from ultralytics import YOLO

def convert_to_production_format(model_path, output_path):
    """
    Convierte modelo para producción
    """
    model = YOLO(model_path)
    
    # Exportar a diferentes formatos
    model.export(format='onnx', dynamic=True)  # ONNX para inferencia rápida
    model.export(format='torchscript')         # TorchScript
    model.export(format='tflite')              # TensorFlow Lite para móviles
    
    print(f"Modelo exportado en múltiples formatos desde {model_path}")

if __name__ == "__main__":
    convert_to_production_format(
        'models/trained/invoice_detector/weights/best.pt',
        'models/yolo_models/invoice_yolov8.pt'
    )
```

## Comandos de Ejecución

```bash
# 1. Preparar dataset
python scripts/organize_dataset.py

# 2. Validar dataset
python scripts/validate_dataset.py

# 3. Entrenar modelo básico
python scripts/train_yolo.py

# 4. Entrenar con configuración avanzada
python scripts/train_advanced.py

# 5. Evaluar modelo
python scripts/evaluate_model.py

# 6. Convertir para producción
python scripts/convert_model.py

# 7. Optimizar hiperparámetros (opcional)
python scripts/hyperparameter_tuning.py
```

## Consejos y Mejores Prácticas

### 1. Calidad de Datos
- **Consistencia**: Mantén un estilo consistente de anotación
- **Diversidad**: Incluye variaciones de formato, calidad y orientación
- **Balance**: Asegúrate de tener ejemplos balanceados de cada clase

### 2. Entrenamiento
- **Transfer Learning**: Siempre usa modelos preentrenados como punto de partida
- **Early Stopping**: Usa patience para evitar overfitting
- **Validación**: Monitorea métricas en conjunto de validación

### 3. Optimización
- **Confidence Threshold**: Ajusta según precisión vs recall requeridos
- **NMS Threshold**: Optimiza para evitar detecciones duplicadas
- **Image Size**: 640px es un buen balance velocidad/precisión

### 4. Producción
- **Formato ONNX**: Para inferencia más rápida
- **Batch Processing**: Procesa múltiples imágenes juntas
- **Caching**: Cachea modelos cargados en memoria

Este tutorial te proporciona una base sólida para entrenar modelos YOLO específicos para tu aplicación de OCR. ¡Comienza con un dataset pequeño y ve escalando gradualmente!
