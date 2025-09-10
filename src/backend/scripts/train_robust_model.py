#!/usr/bin/env python3
"""
Script para entrenar un modelo YOLO robusto con múltiples facturas
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO
import torch

def train_robust_model():
    """Entrena un modelo YOLO robusto"""
    
    print("🚀 ENTRENANDO MODELO YOLO ROBUSTO")
    print("=" * 50)
    
    # Verificar que el dataset existe
    dataset_path = "datasets/invoices_robust/dataset.yaml"
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset no encontrado: {dataset_path}")
        print("💡 Ejecuta primero: python scripts/prepare_training_data.py")
        return
    
    # Configuración de entrenamiento
    config = {
        'model': 'yolov8n.pt',  # Modelo base
        'data': dataset_path,
        'epochs': 50,  # Más épocas para mejor entrenamiento
        'imgsz': 640,
        'batch': 8,  # Batch size
        'device': 'cpu',  # Cambiar a 'cuda' si tienes GPU
        'patience': 10,  # Early stopping
        'save': True,
        'project': 'models/yolo_models',
        'name': 'invoices_robust',
        'exist_ok': True,
        'pretrained': True,
        'optimizer': 'AdamW',
        'lr0': 0.01,
        'lrf': 0.01,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 3,
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
        'crop_fraction': 1.0
    }
    
    try:
        # Cargar modelo
        print(f"📦 Cargando modelo base: {config['model']}")
        model = YOLO(config['model'])
        
        # Verificar dataset
        print(f"📊 Verificando dataset: {config['data']}")
        
        # Iniciar entrenamiento
        print(f"🏋️ Iniciando entrenamiento...")
        print(f"   Épocas: {config['epochs']}")
        print(f"   Batch size: {config['batch']}")
        print(f"   Dispositivo: {config['device']}")
        
        results = model.train(**config)
        
        print(f"\n✅ ENTRENAMIENTO COMPLETADO")
        print(f"📁 Modelo guardado en: models/yolo_models/invoices_robust")
        
        # Mostrar métricas finales
        if hasattr(results, 'results_dict'):
            metrics = results.results_dict
            print(f"\n📊 MÉTRICAS FINALES:")
            print(f"   mAP50: {metrics.get('metrics/mAP50(B)', 'N/A')}")
            print(f"   mAP50-95: {metrics.get('metrics/mAP50-95(B)', 'N/A')}")
            print(f"   Precision: {metrics.get('metrics/precision(B)', 'N/A')}")
            print(f"   Recall: {metrics.get('metrics/recall(B)', 'N/A')}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error durante el entrenamiento: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_trained_model():
    """Prueba el modelo entrenado"""
    
    model_path = "models/yolo_models/invoices_robust/weights/best.pt"
    test_image = "example_dataset/images/factura_ejemplo.jpg"
    
    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        return
    
    print(f"\n🧪 PROBANDO MODELO ENTRENADO")
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
        output_path = "models/yolo_models/invoices_robust/test_result.jpg"
        for r in results:
            r.save(output_path)
        print(f"💾 Resultado guardado: {output_path}")
        
    except Exception as e:
        print(f"❌ Error probando modelo: {e}")

if __name__ == "__main__":
    # Verificar PyTorch
    print(f"🔧 PyTorch version: {torch.__version__}")
    print(f"🔧 CUDA disponible: {torch.cuda.is_available()}")
    
    # Entrenar modelo
    results = train_robust_model()
    
    if results:
        # Probar modelo
        test_trained_model()
        
        print(f"\n🎉 PROCESO COMPLETADO")
        print(f"💡 Para usar el nuevo modelo, actualiza services/ocr_service.py")
        print(f"   Cambia la ruta a: models/yolo_models/invoices_robust/weights/best.pt")
