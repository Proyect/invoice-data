#!/usr/bin/env python3
"""
Script de entrenamiento rápido para el modelo YOLO de DNI (solo 10 épocas para pruebas)
"""

import os
from ultralytics import YOLO
import torch

def quick_train_dni_model():
    """Entrena el modelo YOLO para DNI con configuración rápida"""
    
    print("🆔 ENTRENAMIENTO RÁPIDO DE MODELO DE DNI")
    print("=" * 50)
    
    # Configuración rápida para pruebas
    config = {
        'model': 'yolov8n.pt',
        'data': 'datasets/dni_robust/dataset.yaml',
        'epochs': 10,  # Solo 10 épocas para pruebas rápidas
        'imgsz': 640,
        'batch': 4,    # Batch más pequeño para CPU
        'device': 'cpu',
        'patience': 5,
        'save': True,
        'project': 'models/yolo_models',
        'name': 'dni_quick',
        'exist_ok': True,
        'pretrained': True,
        'optimizer': 'AdamW',
        'lr0': 0.01,
        'lrf': 0.01,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 1,
        'box': 7.5,
        'cls': 0.5,
        'dfl': 1.5,
        'hsv_h': 0.015,
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 0.0,
        'translate': 0.1,
        'scale': 0.5,
        'shear': 0.0,
        'perspective': 0.0,
        'flipud': 0.0,
        'fliplr': 0.5,
        'mosaic': 1.0,
        'mixup': 0.0,
        'copy_paste': 0.0,
        'auto_augment': 'randaugment',
        'erasing': 0.4,
        'workers': 2  # Menos workers para CPU
    }
    
    try:
        # Cargar modelo
        print(f"📦 Cargando modelo: {config['model']}")
        model = YOLO(config['model'])
        
        # Entrenar
        print(f"🏋️ Iniciando entrenamiento rápido ({config['epochs']} épocas)...")
        results = model.train(**config)
        
        print(f"\n✅ ENTRENAMIENTO RÁPIDO COMPLETADO")
        print(f"📁 Modelo guardado en: models/yolo_models/dni_quick")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_quick_model():
    """Prueba el modelo entrenado rápidamente"""
    
    model_path = "models/yolo_models/dni_quick/weights/best.pt"
    test_image = "example_dataset/images/factura_ejemplo.jpg"
    
    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        return
    
    print(f"\n🧪 PROBANDO MODELO RÁPIDO DE DNI")
    print("=" * 30)
    
    try:
        model = YOLO(model_path)
        results = model(test_image, conf=0.25)
        
        detections = 0
        for r in results:
            if r.boxes is not None:
                detections = len(r.boxes)
        
        print(f"✅ Detecciones encontradas: {detections}")
        
        # Guardar resultado
        output_path = "models/yolo_models/dni_quick/test_result.jpg"
        for r in results:
            r.save(output_path)
        print(f"💾 Resultado guardado: {output_path}")
        
    except Exception as e:
        print(f"❌ Error probando modelo: {e}")

if __name__ == "__main__":
    print(f"🔧 PyTorch: {torch.__version__}")
    print(f"🔧 CUDA: {torch.cuda.is_available()}")
    
    results = quick_train_dni_model()
    
    if results:
        test_quick_model()
        print(f"\n🎉 ¡ENTRENAMIENTO RÁPIDO EXITOSO!")
        print(f"💡 Para entrenamiento completo, usa: python scripts/train_dni_model.py")
