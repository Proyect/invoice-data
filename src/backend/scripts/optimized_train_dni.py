#!/usr/bin/env python3
"""
Script optimizado para entrenar el modelo de DNI con configuración mejorada
"""

import os
import time
from ultralytics import YOLO
import torch

def optimized_train_dni():
    """Entrena el modelo con configuración optimizada para CPU"""
    
    print("🚀 ENTRENAMIENTO OPTIMIZADO DE DNI")
    print("=" * 50)
    
    # Configuración optimizada para CPU
    config = {
        'model': 'yolov8n.pt',
        'data': 'datasets/dni_robust/dataset.yaml',
        'epochs': 5,           # Menos épocas para prueba rápida
        'imgsz': 416,          # Imagen más pequeña (menos memoria)
        'batch': 2,            # Batch más pequeño
        'device': 'cpu',
        'patience': 3,         # Menos paciencia
        'save': True,
        'project': 'models/yolo_models',
        'name': 'dni_optimized',
        'exist_ok': True,
        'pretrained': True,
        'optimizer': 'AdamW',
        'lr0': 0.01,
        'lrf': 0.01,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 1,    # Menos warmup
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
        'workers': 2,          # Menos workers
        'verbose': True,
        'plots': False,        # Sin gráficos para ahorrar memoria
        'save_period': -1,     # No guardar checkpoints intermedios
        'cache': False,        # Sin caché para ahorrar memoria
        'amp': False           # Sin mixed precision
    }
    
    try:
        print(f"📦 Cargando modelo: {config['model']}")
        model = YOLO(config['model'])
        
        print(f"🏋️ Iniciando entrenamiento optimizado...")
        print(f"   - Épocas: {config['epochs']}")
        print(f"   - Batch size: {config['batch']}")
        print(f"   - Imagen size: {config['imgsz']}")
        print(f"   - Workers: {config['workers']}")
        
        start_time = time.time()
        results = model.train(**config)
        end_time = time.time()
        
        print(f"\n✅ ENTRENAMIENTO COMPLETADO")
        print(f"⏱️ Tiempo total: {end_time - start_time:.2f} segundos")
        print(f"📁 Modelo guardado en: models/yolo_models/dni_optimized")
        
        return results
        
    except Exception as e:
        print(f"❌ Error durante el entrenamiento: {e}")
        return None

def test_optimized_model():
    """Prueba el modelo optimizado"""
    
    model_path = "models/yolo_models/dni_optimized/weights/best.pt"
    test_image = "example_dataset/images/factura_ejemplo.jpg"
    
    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        return
    
    print(f"\n🧪 PROBANDO MODELO OPTIMIZADO")
    print("=" * 40)
    
    try:
        model = YOLO(model_path)
        results = model(test_image, conf=0.25)
        
        detections = 0
        if results[0].boxes is not None:
            detections = len(results[0].boxes)
        
        print(f"✅ Detecciones encontradas: {detections}")
        
        # Guardar resultado
        output_path = "models/yolo_models/dni_optimized/test_result.jpg"
        results[0].save(output_path)
        print(f"💾 Resultado guardado: {output_path}")
        
        # Mostrar detalles de las detecciones
        if detections > 0:
            print(f"\n📊 DETALLES DE DETECCIONES:")
            for i, box in enumerate(results[0].boxes):
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                class_name = model.names[cls]
                print(f"   {i+1}. {class_name}: {conf:.3f} confianza")
        
    except Exception as e:
        print(f"❌ Error probando modelo: {e}")

def check_system_resources():
    """Verifica los recursos del sistema"""
    
    print("🔍 VERIFICANDO RECURSOS DEL SISTEMA")
    print("=" * 40)
    
    # Verificar PyTorch
    print(f"🔧 PyTorch: {torch.__version__}")
    print(f"🔧 CUDA disponible: {torch.cuda.is_available()}")
    
    # Verificar memoria disponible
    import psutil
    memory = psutil.virtual_memory()
    print(f"💾 RAM total: {memory.total / (1024**3):.1f} GB")
    print(f"💾 RAM disponible: {memory.available / (1024**3):.1f} GB")
    print(f"💾 RAM usada: {memory.percent:.1f}%")
    
    # Verificar CPU
    cpu_count = psutil.cpu_count()
    print(f"🖥️ CPUs disponibles: {cpu_count}")
    
    # Verificar espacio en disco
    disk = psutil.disk_usage('.')
    print(f"💿 Espacio libre: {disk.free / (1024**3):.1f} GB")

def main():
    """Función principal"""
    
    print("🚀 ENTRENAMIENTO OPTIMIZADO DE DNI")
    print("=" * 60)
    
    # Verificar recursos
    check_system_resources()
    
    # Entrenar modelo
    results = optimized_train_dni()
    
    if results:
        # Probar modelo
        test_optimized_model()
        print(f"\n🎉 ¡ENTRENAMIENTO OPTIMIZADO EXITOSO!")
    else:
        print(f"\n❌ El entrenamiento falló. Revisa los recursos del sistema.")

if __name__ == "__main__":
    main()
