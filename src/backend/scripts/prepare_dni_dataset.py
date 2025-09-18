#!/usr/bin/env python3
"""
Script para preparar dataset de DNI para entrenamiento YOLO
"""

import os
import shutil
import random
from pathlib import Path
import yaml
from collections import defaultdict

def create_dni_directory_structure():
    """Crea la estructura de directorios para DNI"""
    
    print("📁 CREANDO ESTRUCTURA PARA DNI")
    print("=" * 40)
    
    base_path = Path("datasets/dni_robust")
    
    # Crear directorios
    dirs = [
        "images/train",
        "images/val", 
        "images/test",
        "labels/train",
        "labels/val",
        "labels/test",
        "raw_images"
    ]
    
    for dir_path in dirs:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {full_path}")
    
    return base_path

def create_dni_dataset_yaml():
    """Crea el archivo dataset.yaml para DNI"""
    
    print(f"\n📄 CREANDO DATASET.YAML PARA DNI")
    print("=" * 40)
    
    dataset_path = Path("datasets/dni_robust")
    
    yaml_content = {
        'train': str(dataset_path / 'images' / 'train'),
        'val': str(dataset_path / 'images' / 'val'),
        'test': str(dataset_path / 'images' / 'test'),
        'nc': 8,  # Número de clases para DNI
        'names': [
            'dni_number',      # 0 - Número de DNI
            'first_name',      # 1 - Nombre
            'last_name',       # 2 - Apellido
            'birth_date',      # 3 - Fecha de nacimiento
            'gender',          # 4 - Sexo
            'nationality',     # 5 - Nacionalidad
            'address',         # 6 - Domicilio
            'photo'            # 7 - Foto
        ]
    }
    
    yaml_path = dataset_path / 'dataset.yaml'
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Archivo creado: {yaml_path}")
    return yaml_path

def create_sample_dni_annotations():
    """Crea anotaciones de ejemplo para DNI"""
    
    print(f"\n📝 CREANDO ANOTACIONES DE EJEMPLO")
    print("=" * 40)
    
    dataset_path = Path("datasets/dni_robust")
    
    # Anotaciones de ejemplo (coordenadas normalizadas)
    sample_annotations = {
        'dni_front_sample.txt': [
            '0 0.5 0.15 0.3 0.08',  # dni_number
            '1 0.3 0.25 0.4 0.06',  # first_name
            '2 0.3 0.32 0.4 0.06',  # last_name
            '3 0.3 0.39 0.3 0.06',  # birth_date
            '4 0.3 0.46 0.2 0.06',  # gender
            '5 0.3 0.53 0.3 0.06',  # nationality
            '6 0.3 0.60 0.4 0.08',  # address
            '7 0.75 0.3 0.2 0.4'    # photo
        ],
        'dni_back_sample.txt': [
            '0 0.5 0.2 0.3 0.08',   # dni_number
            '6 0.3 0.4 0.4 0.1',    # address
            '7 0.75 0.3 0.2 0.4'    # photo
        ]
    }
    
    # Crear archivos de anotación
    for filename, annotations in sample_annotations.items():
        label_path = dataset_path / 'labels' / 'train' / filename
        with open(label_path, 'w') as f:
            f.write('\n'.join(annotations))
        print(f"✅ Anotación creada: {filename}")
    
    return sample_annotations

def create_dni_training_script():
    """Crea el script de entrenamiento para DNI"""
    
    print(f"\n🤖 CREANDO SCRIPT DE ENTRENAMIENTO PARA DNI")
    print("=" * 40)
    
    training_script = """#!/usr/bin/env python3
'''
Script de entrenamiento para el modelo YOLO de DNI
'''

import os
from ultralytics import YOLO
import torch

def train_dni_model():
    '''Entrena el modelo YOLO para DNI'''
    
    print("🆔 ENTRENANDO MODELO DE DNI")
    print("=" * 50)
    
    # Configuración específica para DNI
    config = {
        'model': 'yolov8n.pt',
        'data': 'datasets/dni_robust/dataset.yaml',
        'epochs': 100,
        'imgsz': 640,
        'batch': 8,
        'device': 'cpu',  # Cambiar a 'cuda' si tienes GPU
        'patience': 20,
        'save': True,
        'project': 'models/yolo_models',
        'name': 'dni_robust',
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
        'erasing': 0.4
    }
    
    try:
        # Cargar modelo
        print(f"📦 Cargando modelo: {config['model']}")
        model = YOLO(config['model'])
        
        # Entrenar
        print(f"🏋️ Iniciando entrenamiento...")
        results = model.train(**config)
        
        print(f"\\n✅ ENTRENAMIENTO COMPLETADO")
        print(f"📁 Modelo guardado en: models/yolo_models/dni_robust")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_dni_model():
    '''Prueba el modelo entrenado'''
    
    model_path = "models/yolo_models/dni_robust/weights/best.pt"
    test_image = "example_dataset/images/factura_ejemplo.jpg"  # Usar imagen de prueba
    
    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        return
    
    print(f"\\n🧪 PROBANDO MODELO DE DNI")
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
        output_path = "models/yolo_models/dni_robust/test_result.jpg"
        for r in results:
            r.save(output_path)
        print(f"💾 Resultado guardado: {output_path}")
        
    except Exception as e:
        print(f"❌ Error probando modelo: {e}")

if __name__ == "__main__":
    print(f"🔧 PyTorch: {torch.__version__}")
    print(f"🔧 CUDA: {torch.cuda.is_available()}")
    
    results = train_dni_model()
    
    if results:
        test_dni_model()
        print(f"\\n🎉 ¡ENTRENAMIENTO DE DNI EXITOSO!")
        print(f"💡 Actualiza services/ocr_service.py para usar el modelo de DNI")
"""
    
    with open("scripts/train_dni_model.py", 'w', encoding='utf-8') as f:
        f.write(training_script)
    
    print(f"✅ Script creado: scripts/train_dni_model.py")

def create_dni_test_script():
    """Crea script para probar el modelo de DNI"""
    
    print(f"\n🧪 CREANDO SCRIPT DE PRUEBAS PARA DNI")
    print("=" * 40)
    
    test_script = """#!/usr/bin/env python3
'''
Script para probar el modelo YOLO de DNI
'''

import os
import sys
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np

def test_dni_model():
    '''Prueba el modelo de DNI con imágenes de ejemplo'''
    
    print("🆔 PROBANDO MODELO DE DNI")
    print("=" * 50)
    
    # Rutas
    model_path = "models/yolo_models/dni_robust/weights/best.pt"
    test_images_dir = Path("datasets/dni_robust/raw_images")
    
    # Verificar que el modelo existe
    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        print("💡 Entrena primero el modelo con: python scripts/train_dni_model.py")
        return
    
    try:
        # Cargar modelo
        print(f"📦 Cargando modelo: {model_path}")
        model = YOLO(model_path)
        
        # Mostrar información del modelo
        print(f"✅ Modelo cargado exitosamente")
        print(f"📊 Clases detectadas: {len(model.names)}")
        for i, name in model.names.items():
            print(f"   {i}: {name}")
        
        # Buscar imágenes de prueba
        if test_images_dir.exists():
            test_images = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))
        else:
            # Usar imagen de ejemplo
            test_images = [Path("example_dataset/images/factura_ejemplo.jpg")]
        
        if not test_images:
            print("❌ No se encontraron imágenes de prueba")
            return
        
        print(f"\\n🔍 PROBANDO CON {len(test_images)} IMÁGENES")
        print("=" * 50)
        
        for i, img_path in enumerate(test_images, 1):
            print(f"\\n📸 Imagen {i}: {img_path.name}")
            
            # Realizar predicción
            results = model(str(img_path), conf=0.25)
            
            # Procesar resultados
            detections = []
            for r in results:
                if r.boxes is not None:
                    for box in r.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        conf = box.conf[0].item()
                        cls = int(box.cls[0].item())
                        class_name = model.names[cls]
                        
                        detections.append({
                            'class': class_name,
                            'confidence': conf,
                            'bbox': [x1, y1, x2, y2]
                        })
            
            # Mostrar resultados
            print(f"   Detecciones encontradas: {len(detections)}")
            if detections:
                for det in detections:
                    print(f"     - {det['class']}: {det['confidence']:.2f} confianza")
            
            # Guardar imagen con detecciones
            output_path = f"models/yolo_models/dni_robust/test_dni_{i}.jpg"
            for r in results:
                r.save(output_path)
            print(f"   💾 Resultado guardado: {output_path}")
        
        print(f"\\n🎉 PRUEBAS COMPLETADAS")
        
    except Exception as e:
        print(f"❌ Error probando modelo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dni_model()
"""
    
    with open("scripts/test_dni_model.py", 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print(f"✅ Script creado: scripts/test_dni_model.py")

def update_ocr_service_for_dni():
    """Actualiza el servicio OCR para incluir el modelo de DNI"""
    
    print(f"\n🔧 ACTUALIZANDO SERVICIO OCR PARA DNI")
    print("=" * 40)
    
    # Leer el archivo actual
    ocr_service_path = Path("services/ocr_service.py")
    if not ocr_service_path.exists():
        print(f"❌ Archivo no encontrado: {ocr_service_path}")
        return
    
    with open(ocr_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la sección de selección de modelo
    old_model_selection = '''    # Seleccionar el modelo YOLO adecuado
    if document_type in [DocumentType.DNI_FRONT, DocumentType.DNI_BACK]:
        yolo_model_name = "dni_yolov8.pt" # Aquí tu modelo entrenado para DNI
    elif document_type in [DocumentType.INVOICE_A, DocumentType.INVOICE_B, DocumentType.INVOICE_C]:
        yolo_model_name = "invoices_cpu_abs/weights/best.pt" # Tu modelo entrenado para facturas
    else:
        # Para el desarrollo inicial, usa un modelo genérico
        print(f"Advertencia: Tipo de documento {document_type} no tiene un modelo YOLO específico. Usando yolov8n.pt")
        yolo_model_name = "yolov8n.pt" # Modelo genérico solo para pruebas, NO para prod.'''
    
    new_model_selection = '''    # Seleccionar el modelo YOLO adecuado
    if document_type in [DocumentType.DNI_FRONT, DocumentType.DNI_BACK]:
        yolo_model_name = "dni_robust/weights/best.pt" # Modelo entrenado para DNI
    elif document_type in [DocumentType.INVOICE_A, DocumentType.INVOICE_B, DocumentType.INVOICE_C]:
        yolo_model_name = "invoices_cpu_abs/weights/best.pt" # Modelo entrenado para facturas
    else:
        # Para el desarrollo inicial, usa un modelo genérico
        print(f"Advertencia: Tipo de documento {document_type} no tiene un modelo YOLO específico. Usando yolov8n.pt")
        yolo_model_name = "yolov8n.pt" # Modelo genérico solo para pruebas, NO para prod.'''
    
    # Reemplazar la sección
    if old_model_selection in content:
        content = content.replace(old_model_selection, new_model_selection)
        
        # Escribir el archivo actualizado
        with open(ocr_service_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Servicio OCR actualizado para usar modelo de DNI")
    else:
        print(f"⚠️  No se encontró la sección a actualizar en {ocr_service_path}")

def main():
    """Función principal"""
    
    print("🚀 CONFIGURACIÓN COMPLETA PARA MODELO DE DNI")
    print("=" * 60)
    
    # Paso 1: Crear estructura
    create_dni_directory_structure()
    
    # Paso 2: Crear dataset.yaml
    create_dni_dataset_yaml()
    
    # Paso 3: Crear anotaciones de ejemplo
    create_sample_dni_annotations()
    
    # Paso 4: Crear script de entrenamiento
    create_dni_training_script()
    
    # Paso 5: Crear script de pruebas
    create_dni_test_script()
    
    # Paso 6: Actualizar servicio OCR
    update_ocr_service_for_dni()
    
    print(f"\n🎉 ¡CONFIGURACIÓN DE DNI COMPLETADA!")
    print("=" * 60)
    print(f"📁 Dataset preparado en: datasets/dni_robust")
    print(f"🤖 Script de entrenamiento: scripts/train_dni_model.py")
    print(f"🧪 Script de pruebas: scripts/test_dni_model.py")
    print(f"\n💡 PRÓXIMOS PASOS:")
    print(f"   1. Agregar imágenes de DNI en: datasets/dni_robust/raw_images")
    print(f"   2. Crear anotaciones correspondientes en: datasets/dni_robust/labels/train")
    print(f"   3. Ejecutar: python scripts/train_dni_model.py")
    print(f"   4. Probar: python scripts/test_dni_model.py")

if __name__ == "__main__":
    main()
