#!/usr/bin/env python3
"""
Script para preparar y organizar datos de entrenamiento para YOLO
"""

import os
import shutil
import random
from pathlib import Path
import yaml

def create_directory_structure():
    """Crea la estructura de directorios para el entrenamiento"""
    
    base_path = Path("datasets/invoices_robust")
    
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
        print(f"✅ Directorio creado: {full_path}")
    
    return base_path

def collect_all_images():
    """Recopila todas las imágenes de facturas disponibles"""
    
    image_sources = [
        "datasets/invoices_argentina/images/train",
        "datasets/invoices_argentina/images/val", 
        "datasets/invoices_argentina/temp",
        "datasets/invoices/images/train",
        "datasets/invoices/images/val",
        "example_dataset/images"
    ]
    
    all_images = []
    
    for source in image_sources:
        if os.path.exists(source):
            for file in os.listdir(source):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    full_path = os.path.join(source, file)
                    all_images.append(full_path)
                    print(f"📸 Imagen encontrada: {full_path}")
    
    print(f"\n📊 Total de imágenes encontradas: {len(all_images)}")
    return all_images

def split_dataset(images, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
    """Divide el dataset en train/val/test"""
    
    # Mezclar las imágenes
    random.shuffle(images)
    
    total = len(images)
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)
    
    train_images = images[:train_count]
    val_images = images[train_count:train_count + val_count]
    test_images = images[train_count + val_count:]
    
    print(f"📊 División del dataset:")
    print(f"   Train: {len(train_images)} imágenes ({len(train_images)/total*100:.1f}%)")
    print(f"   Val: {len(val_images)} imágenes ({len(val_images)/total*100:.1f}%)")
    print(f"   Test: {len(test_images)} imágenes ({len(test_images)/total*100:.1f}%)")
    
    return train_images, val_images, test_images

def copy_images_and_labels(images, split_name, target_dir):
    """Copia imágenes y etiquetas al directorio de destino"""
    
    images_dir = target_dir / "images" / split_name
    labels_dir = target_dir / "labels" / split_name
    
    copied_count = 0
    
    for img_path in images:
        img_name = os.path.basename(img_path)
        name_without_ext = os.path.splitext(img_name)[0]
        
        # Copiar imagen
        target_img = images_dir / img_name
        shutil.copy2(img_path, target_img)
        
        # Buscar etiqueta correspondiente
        label_found = False
        possible_label_sources = [
            os.path.join(os.path.dirname(img_path), "..", "labels", split_name, f"{name_without_ext}.txt"),
            os.path.join(os.path.dirname(img_path), "..", "labels", "train", f"{name_without_ext}.txt"),
            os.path.join(os.path.dirname(img_path), "..", "labels", "val", f"{name_without_ext}.txt"),
            f"datasets/invoices_argentina/labels/train/{name_without_ext}.txt",
            f"datasets/invoices/labels/train/{name_without_ext}.txt"
        ]
        
        for label_source in possible_label_sources:
            if os.path.exists(label_source):
                target_label = labels_dir / f"{name_without_ext}.txt"
                shutil.copy2(label_source, target_label)
                label_found = True
                break
        
        if not label_found:
            print(f"⚠️  No se encontró etiqueta para: {img_name}")
            # Crear etiqueta vacía
            target_label = labels_dir / f"{name_without_ext}.txt"
            target_label.write_text("")
        
        copied_count += 1
    
    print(f"✅ {split_name}: {copied_count} imágenes copiadas")
    return copied_count

def create_dataset_yaml(target_dir):
    """Crea el archivo dataset.yaml para YOLO"""
    
    yaml_content = {
        'train': str(target_dir / 'images' / 'train'),
        'val': str(target_dir / 'images' / 'val'),
        'test': str(target_dir / 'images' / 'test'),
        'nc': 8,  # Número de clases
        'names': [
            'invoice_number',
            'date', 
            'vendor',
            'cuit',
            'subtotal',
            'tax',
            'total',
            'items_table'
        ]
    }
    
    yaml_path = target_dir / 'dataset.yaml'
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Archivo dataset.yaml creado: {yaml_path}")
    return yaml_path

def analyze_dataset(target_dir):
    """Analiza el dataset preparado"""
    
    print(f"\n📊 ANÁLISIS DEL DATASET PREPARADO")
    print("=" * 50)
    
    for split in ['train', 'val', 'test']:
        images_dir = target_dir / 'images' / split
        labels_dir = target_dir / 'labels' / split
        
        if images_dir.exists():
            image_count = len(list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png')))
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
        labels_dir = target_dir / 'labels' / split
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

def main():
    """Función principal"""
    
    print("🚀 PREPARANDO DATOS DE ENTRENAMIENTO")
    print("=" * 50)
    
    # Crear estructura de directorios
    target_dir = create_directory_structure()
    
    # Recopilar todas las imágenes
    all_images = collect_all_images()
    
    if not all_images:
        print("❌ No se encontraron imágenes para entrenar")
        return
    
    # Dividir dataset
    train_images, val_images, test_images = split_dataset(all_images)
    
    # Copiar archivos
    print(f"\n📁 COPIANDO ARCHIVOS...")
    copy_images_and_labels(train_images, 'train', target_dir)
    copy_images_and_labels(val_images, 'val', target_dir)
    copy_images_and_labels(test_images, 'test', target_dir)
    
    # Crear dataset.yaml
    dataset_yaml = create_dataset_yaml(target_dir)
    
    # Analizar dataset
    analyze_dataset(target_dir)
    
    print(f"\n🎉 DATOS PREPARADOS EXITOSAMENTE")
    print(f"📁 Directorio: {target_dir}")
    print(f"📄 Configuración: {dataset_yaml}")
    print(f"\n💡 Próximo paso: Ejecutar el entrenamiento con:")
    print(f"   python scripts/train_robust_model.py")

if __name__ == "__main__":
    # Establecer semilla para reproducibilidad
    random.seed(42)
    main()
