#!/usr/bin/env python3
"""
Script completo para configurar y entrenar el modelo con el dataset de Downloads
"""

import os
import shutil
import json
import pandas as pd
from pathlib import Path
import yaml
from collections import defaultdict

def create_directory_structure():
    """Crea la estructura de directorios necesaria"""
    
    print("📁 CREANDO ESTRUCTURA DE DIRECTORIOS")
    print("=" * 40)
    
    base_path = Path("datasets/invoices_downloads")
    
    # Crear directorios
    dirs = [
        "images/train",
        "images/val", 
        "images/test",
        "labels/train",
        "labels/val",
        "labels/test"
    ]
    
    for dir_path in dirs:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {full_path}")
    
    return base_path

def copy_and_convert_dataset():
    """Copia y convierte el dataset de Downloads a formato YOLO"""
    
    print(f"\n🔄 COPIANDO Y CONVIRTIENDO DATASET")
    print("=" * 40)
    
    # Rutas
    source_path = Path("C:/Users/amdiaz/Downloads/FATURA/invoices_dataset_final")
    target_path = Path("datasets/invoices_downloads")
    
    if not source_path.exists():
        print(f"❌ Dataset no encontrado en: {source_path}")
        return False
    
    # Mapeo de clases a IDs (adaptado a tu modelo actual)
    class_mapping = {
        'INVOICE_INFO': 0,      # invoice_number
        'DATE': 1,              # date
        'BUYER': 2,             # vendor
        'GSTIN_BUYER': 3,       # cuit
        'SUB_TOTAL': 4,         # subtotal
        'TAX': 5,               # tax
        'TOTAL': 6,             # total
        'TABLE': 7              # items_table
    }
    
    # Leer archivos CSV para división
    try:
        train_df = pd.read_csv(source_path / "strat1_train.csv")
        val_df = pd.read_csv(source_path / "strat1_dev.csv")
        test_df = pd.read_csv(source_path / "strat1_test.csv")
        
        train_files = set(train_df['img_path'].str.replace('.jpg', ''))
        val_files = set(val_df['img_path'].str.replace('.jpg', ''))
        test_files = set(test_df['img_path'].str.replace('.jpg', ''))
        
        print(f"📊 División del dataset:")
        print(f"   Train: {len(train_files)} imágenes")
        print(f"   Val: {len(val_files)} imágenes")
        print(f"   Test: {len(test_files)} imágenes")
        
    except Exception as e:
        print(f"❌ Error leyendo archivos CSV: {e}")
        return False
    
    # Procesar imágenes
    images_dir = source_path / "images"
    annotations_dir = source_path / "Annotations" / "Original_Format"
    
    processed = 0
    errors = 0
    
    print(f"\n🔄 Procesando imágenes...")
    
    for img_file in images_dir.glob("*.jpg"):
        try:
            img_name = img_file.stem
            annotation_file = annotations_dir / f"{img_name}.json"
            
            if not annotation_file.exists():
                continue
            
            # Determinar split
            if img_name in train_files:
                split = "train"
            elif img_name in val_files:
                split = "val"
            elif img_name in test_files:
                split = "test"
            else:
                continue
            
            # Copiar imagen
            target_img = target_path / "images" / split / img_file.name
            shutil.copy2(img_file, target_img)
            
            # Convertir anotaciones
            with open(annotation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Crear archivo de etiquetas YOLO
            label_file = target_path / "labels" / split / f"{img_name}.txt"
            with open(label_file, 'w') as f:
                for class_name, class_data in data.items():
                    if class_name not in class_mapping or not isinstance(class_data, dict):
                        continue
                    
                    if "bbox" not in class_data or not class_data["bbox"]:
                        continue
                    
                    bbox = class_data["bbox"]
                    if len(bbox) != 2:
                        continue
                    
                    # Convertir bbox a formato YOLO (normalizado)
                    x1, y1 = bbox[0]
                    x2, y2 = bbox[1]
                    
                    # Asumir imagen 640x640 (tamaño estándar YOLO)
                    img_width, img_height = 640, 640
                    
                    x_center = (x1 + x2) / 2 / img_width
                    y_center = (y1 + y2) / 2 / img_height
                    width = abs(x2 - x1) / img_width
                    height = abs(y2 - y1) / img_height
                    
                    class_id = class_mapping[class_name]
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            processed += 1
            if processed % 100 == 0:
                print(f"   ✅ Procesadas: {processed} imágenes")
                
        except Exception as e:
            errors += 1
            if errors < 5:  # Mostrar solo los primeros 5 errores
                print(f"   ⚠️  Error en {img_file.name}: {e}")
    
    print(f"\n✅ CONVERSIÓN COMPLETADA")
    print(f"   Procesadas: {processed} imágenes")
    print(f"   Errores: {errors}")
    
    return True

def create_dataset_yaml():
    """Crea el archivo dataset.yaml para YOLO"""
    
    print(f"\n📄 CREANDO ARCHIVO DATASET.YAML")
    print("=" * 40)
    
    dataset_path = Path("datasets/invoices_downloads")
    
    yaml_content = {
        'train': str(dataset_path / 'images' / 'train'),
        'val': str(dataset_path / 'images' / 'val'),
        'test': str(dataset_path / 'images' / 'test'),
        'nc': 8,  # Número de clases
        'names': [
            'invoice_number',  # 0
            'date',            # 1
            'vendor',          # 2
            'cuit',            # 3
            'subtotal',        # 4
            'tax',             # 5
            'total',           # 6
            'items_table'      # 7
        ]
    }
    
    yaml_path = dataset_path / 'dataset.yaml'
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Archivo creado: {yaml_path}")
    return yaml_path

def analyze_final_dataset():
    """Analiza el dataset final preparado"""
    
    print(f"\n📊 ANÁLISIS DEL DATASET FINAL")
    print("=" * 40)
    
    dataset_path = Path("datasets/invoices_downloads")
    
    for split in ['train', 'val', 'test']:
        images_dir = dataset_path / 'images' / split
        labels_dir = dataset_path / 'labels' / split
        
        if images_dir.exists():
            image_count = len(list(images_dir.glob('*.jpg')))
            label_count = len(list(labels_dir.glob('*.txt')))
            
            print(f"{split.upper()}:")
            print(f"  Imágenes: {image_count}")
            print(f"  Etiquetas: {label_count}")
            
            if image_count != label_count:
                print(f"  ⚠️  ADVERTENCIA: Número de imágenes y etiquetas no coincide")
    
    # Contar anotaciones por clase
    print(f"\n📋 ANOTACIONES POR CLASE:")
    class_counts = {i: 0 for i in range(8)}
    class_names = ['invoice_number', 'date', 'vendor', 'cuit', 'subtotal', 'tax', 'total', 'items_table']
    
    for split in ['train', 'val']:
        labels_dir = dataset_path / 'labels' / split
        if labels_dir.exists():
            for label_file in labels_dir.glob('*.txt'):
                try:
                    with open(label_file, 'r') as f:
                        for line in f:
                            if line.strip():
                                class_id = int(line.split()[0])
                                if class_id in class_counts:
                                    class_counts[class_id] += 1
                except:
                    continue
    
    for class_id, count in class_counts.items():
        print(f"  {class_id}: {class_names[class_id]} - {count} anotaciones")

def create_training_script():
    """Crea el script de entrenamiento"""
    
    print(f"\n🤖 CREANDO SCRIPT DE ENTRENAMIENTO")
    print("=" * 40)
    
    training_script = """#!/usr/bin/env python3
'''
Script de entrenamiento para el modelo de facturas
'''

import os
from ultralytics import YOLO
import torch

def train_invoice_model():
    '''Entrena el modelo YOLO para facturas'''
    
    print("🚀 ENTRENANDO MODELO DE FACTURAS")
    print("=" * 50)
    
    # Configuración
    config = {
        'model': 'yolov8n.pt',
        'data': 'datasets/invoices_downloads/dataset.yaml',
        'epochs': 100,
        'imgsz': 640,
        'batch': 16,
        'device': 'cpu',  # Cambiar a 'cuda' si tienes GPU
        'patience': 20,
        'save': True,
        'project': 'models/yolo_models',
        'name': 'invoices_downloads',
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
        print(f"📁 Modelo guardado en: models/yolo_models/invoices_downloads")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print(f"🔧 PyTorch: {torch.__version__}")
    print(f"🔧 CUDA: {torch.cuda.is_available()}")
    
    results = train_invoice_model()
    
    if results:
        print(f"\\n🎉 ¡ENTRENAMIENTO EXITOSO!")
        print(f"💡 Actualiza services/ocr_service.py para usar el nuevo modelo")
"""
    
    with open("scripts/train_downloads_model.py", 'w', encoding='utf-8') as f:
        f.write(training_script)
    
    print(f"✅ Script creado: scripts/train_downloads_model.py")

def main():
    """Función principal"""
    
    print("🚀 CONFIGURACIÓN COMPLETA PARA ENTRENAMIENTO")
    print("=" * 60)
    
    # Paso 1: Crear estructura
    create_directory_structure()
    
    # Paso 2: Copiar y convertir dataset
    if not copy_and_convert_dataset():
        print("❌ Error en la conversión del dataset")
        return
    
    # Paso 3: Crear dataset.yaml
    create_dataset_yaml()
    
    # Paso 4: Analizar dataset
    analyze_final_dataset()
    
    # Paso 5: Crear script de entrenamiento
    create_training_script()
    
    print(f"\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("=" * 60)
    print(f"📁 Dataset preparado en: datasets/invoices_downloads")
    print(f"🤖 Script de entrenamiento: scripts/train_downloads_model.py")
    print(f"\n💡 PRÓXIMOS PASOS:")
    print(f"   1. Ejecutar: python scripts/train_downloads_model.py")
    print(f"   2. Esperar a que termine el entrenamiento")
    print(f"   3. Actualizar services/ocr_service.py con la nueva ruta del modelo")
    print(f"   4. Probar la API con el nuevo modelo")

if __name__ == "__main__":
    main()
