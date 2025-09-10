#!/usr/bin/env python3
"""
Script para analizar y convertir el dataset de Downloads a formato YOLO
"""

import os
import json
import shutil
from pathlib import Path
import pandas as pd
from collections import defaultdict

def analyze_dataset():
    """Analiza el dataset en Downloads"""
    
    dataset_path = Path("C:/Users/amdiaz/Downloads/FATURA/invoices_dataset_final")
    
    print("🔍 ANÁLISIS DEL DATASET EN DOWNLOADS")
    print("=" * 50)
    
    # Verificar estructura
    if not dataset_path.exists():
        print(f"❌ Dataset no encontrado en: {dataset_path}")
        return False
    
    # Contar imágenes
    images_dir = dataset_path / "images"
    if images_dir.exists():
        image_files = list(images_dir.glob("*.jpg"))
        print(f"📸 Total de imágenes: {len(image_files)}")
        
        # Analizar templates
        templates = defaultdict(int)
        for img in image_files:
            template = img.name.split('_')[0]  # Template1, Template2, etc.
            templates[template] += 1
        
        print(f"📋 Templates encontrados: {len(templates)}")
        for template, count in sorted(templates.items()):
            print(f"   {template}: {count} imágenes")
    
    # Analizar anotaciones
    annotations_dir = dataset_path / "Annotations" / "Original_Format"
    if annotations_dir.exists():
        json_files = list(annotations_dir.glob("*.json"))
        print(f"📝 Total de anotaciones: {len(json_files)}")
        
        # Analizar clases
        class_counts = defaultdict(int)
        sample_annotation = None
        
        for json_file in json_files[:5]:  # Analizar solo las primeras 5
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if sample_annotation is None:
                        sample_annotation = data
                    
                    for key in data.keys():
                        if key != "OTHER" and isinstance(data[key], dict) and "bbox" in data[key]:
                            class_counts[key] += 1
            except Exception as e:
                print(f"⚠️  Error leyendo {json_file}: {e}")
        
        print(f"\n📊 CLASES DETECTADAS:")
        for class_name, count in sorted(class_counts.items()):
            print(f"   {class_name}: {count} anotaciones")
        
        # Mostrar estructura de ejemplo
        if sample_annotation:
            print(f"\n📋 ESTRUCTURA DE ANOTACIÓN (ejemplo):")
            for key, value in sample_annotation.items():
                if key != "OTHER":
                    if isinstance(value, dict) and "bbox" in value:
                        bbox = value["bbox"]
                        text = value.get("text", "")[:50] + "..." if len(value.get("text", "")) > 50 else value.get("text", "")
                        print(f"   {key}: bbox={bbox}, text='{text}'")
    
    # Analizar archivos CSV
    csv_files = list(dataset_path.glob("*.csv"))
    if csv_files:
        print(f"\n📊 ARCHIVOS CSV ENCONTRADOS:")
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                print(f"   {csv_file.name}: {len(df)} filas")
                if len(df) > 0:
                    print(f"      Columnas: {list(df.columns)}")
            except Exception as e:
                print(f"   {csv_file.name}: Error - {e}")
    
    return True

def convert_to_yolo_format():
    """Convierte el dataset a formato YOLO"""
    
    dataset_path = Path("C:/Users/amdiaz/Downloads/FATURA/invoices_dataset_final")
    output_path = Path("datasets/invoices_downloads")
    
    print(f"\n🔄 CONVIRTIENDO A FORMATO YOLO")
    print("=" * 50)
    
    # Crear estructura de directorios
    dirs = ["images/train", "images/val", "images/test", "labels/train", "labels/val", "labels/test"]
    for dir_path in dirs:
        (output_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Mapeo de clases a IDs
    class_mapping = {
        'INVOICE_INFO': 0,
        'BUYER': 1,
        'DATE': 2,
        'DUE_DATE': 3,
        'PO_NUMBER': 4,
        'SELLER_ADDRESS': 5,
        'SELLER_EMAIL': 6,
        'SELLER_SITE': 7,
        'GSTIN_SELLER': 8,
        'GSTIN_BUYER': 9,
        'SUB_TOTAL': 10,
        'TAX': 11,
        'DISCOUNT': 12,
        'TOTAL': 13,
        'TOTAL_WORDS': 14,
        'PAYMENT_DETAILS': 15,
        'NOTE': 16,
        'TITLE': 17,
        'LOGO': 18,
        'TABLE': 19
    }
    
    # Leer archivos CSV para división train/val/test
    train_files = set()
    val_files = set()
    test_files = set()
    
    try:
        train_df = pd.read_csv(dataset_path / "strat1_train.csv")
        val_df = pd.read_csv(dataset_path / "strat1_dev.csv")
        test_df = pd.read_csv(dataset_path / "strat1_test.csv")
        
        train_files = set(train_df['img_path'].str.replace('.jpg', ''))
        val_files = set(val_df['img_path'].str.replace('.jpg', ''))
        test_files = set(test_df['img_path'].str.replace('.jpg', ''))
        
        print(f"📊 División del dataset:")
        print(f"   Train: {len(train_files)} imágenes")
        print(f"   Val: {len(val_files)} imágenes")
        print(f"   Test: {len(test_files)} imágenes")
        
    except Exception as e:
        print(f"⚠️  Error leyendo archivos CSV: {e}")
        print("💡 Usando división manual 70/20/10")
        return False
    
    # Procesar imágenes y anotaciones
    images_dir = dataset_path / "images"
    annotations_dir = dataset_path / "Annotations" / "Original_Format"
    
    processed = 0
    errors = 0
    
    for img_file in images_dir.glob("*.jpg"):
        try:
            img_name = img_file.stem  # Sin extensión
            annotation_file = annotations_dir / f"{img_name}.json"
            
            if not annotation_file.exists():
                print(f"⚠️  Anotación no encontrada para: {img_name}")
                continue
            
            # Determinar split
            if img_name in train_files:
                split = "train"
            elif img_name in val_files:
                split = "val"
            elif img_name in test_files:
                split = "test"
            else:
                print(f"⚠️  Imagen no encontrada en ningún split: {img_name}")
                continue
            
            # Copiar imagen
            target_img = output_path / "images" / split / img_file.name
            shutil.copy2(img_file, target_img)
            
            # Convertir anotaciones
            with open(annotation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Crear archivo de etiquetas YOLO
            label_file = output_path / "labels" / split / f"{img_name}.txt"
            with open(label_file, 'w') as f:
                for class_name, class_data in data.items():
                    if class_name == "OTHER" or not isinstance(class_data, dict):
                        continue
                    
                    if "bbox" not in class_data:
                        continue
                    
                    bbox = class_data["bbox"]
                    if not bbox or len(bbox) != 2:
                        continue
                    
                    # Convertir bbox a formato YOLO
                    x1, y1 = bbox[0]
                    x2, y2 = bbox[1]
                    
                    # Normalizar coordenadas (asumiendo imagen 640x640)
                    img_width, img_height = 640, 640  # Necesitarías obtener las dimensiones reales
                    
                    x_center = (x1 + x2) / 2 / img_width
                    y_center = (y1 + y2) / 2 / img_height
                    width = abs(x2 - x1) / img_width
                    height = abs(y2 - y1) / img_height
                    
                    # Obtener ID de clase
                    if class_name in class_mapping:
                        class_id = class_mapping[class_name]
                        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            processed += 1
            if processed % 100 == 0:
                print(f"✅ Procesadas: {processed} imágenes")
                
        except Exception as e:
            print(f"❌ Error procesando {img_file.name}: {e}")
            errors += 1
    
    print(f"\n✅ CONVERSIÓN COMPLETADA")
    print(f"   Procesadas: {processed} imágenes")
    print(f"   Errores: {errors}")
    
    # Crear dataset.yaml
    create_dataset_yaml(output_path, class_mapping)
    
    return True

def create_dataset_yaml(output_path, class_mapping):
    """Crea el archivo dataset.yaml"""
    
    yaml_content = {
        'train': str(output_path / 'images' / 'train'),
        'val': str(output_path / 'images' / 'val'),
        'test': str(output_path / 'images' / 'test'),
        'nc': len(class_mapping),
        'names': list(class_mapping.keys())
    }
    
    yaml_path = output_path / 'dataset.yaml'
    import yaml
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Archivo dataset.yaml creado: {yaml_path}")

def main():
    """Función principal"""
    
    print("🚀 ANÁLISIS Y CONVERSIÓN DEL DATASET")
    print("=" * 50)
    
    # Analizar dataset
    if not analyze_dataset():
        return
    
    # Preguntar si continuar
    print(f"\n❓ ¿Deseas convertir el dataset a formato YOLO? (y/n)")
    response = input().lower().strip()
    
    if response in ['y', 'yes', 'sí', 'si']:
        convert_to_yolo_format()
        print(f"\n🎉 PROCESO COMPLETADO")
        print(f"💡 Próximo paso: Entrenar el modelo con:")
        print(f"   python scripts/train_downloads_model.py")
    else:
        print("❌ Conversión cancelada")

if __name__ == "__main__":
    main()
