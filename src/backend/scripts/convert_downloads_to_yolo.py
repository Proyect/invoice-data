#!/usr/bin/env python3
"""
Script para convertir el dataset de Downloads a formato YOLO
"""

import os
import json
import shutil
from pathlib import Path
import pandas as pd

def convert_downloads_dataset():
    """Convierte el dataset de Downloads a formato YOLO"""
    
    print("🔄 CONVIRTIENDO DATASET DE DOWNLOADS A YOLO")
    print("=" * 50)
    
    # Rutas
    source_path = Path("C:/Users/amdiaz/Downloads/FATURA/invoices_dataset_final")
    target_path = Path("datasets/invoices_downloads")
    
    if not source_path.exists():
        print(f"❌ Dataset no encontrado en: {source_path}")
        return False
    
    # Crear estructura de directorios
    for split in ['train', 'val', 'test']:
        (target_path / 'images' / split).mkdir(parents=True, exist_ok=True)
        (target_path / 'labels' / split).mkdir(parents=True, exist_ok=True)
    
    # Mapeo de clases (adaptado a tu modelo actual)
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
    
    # Leer archivos CSV
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
    """Crea el archivo dataset.yaml"""
    
    print(f"\n📄 CREANDO DATASET.YAML")
    print("=" * 30)
    
    dataset_path = Path("datasets/invoices_downloads")
    
    yaml_content = f"""train: {dataset_path.resolve()}/images/train
val: {dataset_path.resolve()}/images/val
test: {dataset_path.resolve()}/images/test
names:
  0: invoice_number
  1: date
  2: vendor
  3: cuit
  4: subtotal
  5: tax
  6: total
  7: items_table
"""
    
    yaml_path = dataset_path / 'dataset.yaml'
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print(f"✅ Archivo creado: {yaml_path}")
    return yaml_path

def main():
    """Función principal"""
    
    print("🚀 CONVERSIÓN DE DATASET DE DOWNLOADS")
    print("=" * 50)
    
    # Convertir dataset
    if convert_downloads_dataset():
        # Crear dataset.yaml
        create_dataset_yaml()
        
        print(f"\n🎉 ¡CONVERSIÓN COMPLETADA!")
        print(f"📁 Dataset preparado en: datasets/invoices_downloads")
        print(f"\n💡 PRÓXIMO PASO:")
        print(f"   Ejecutar: python scripts/auto_prepare_and_train.py --source_images datasets/invoices_downloads/images/train")
    else:
        print("❌ Error en la conversión")

if __name__ == "__main__":
    main()
