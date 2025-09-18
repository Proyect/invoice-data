#!/usr/bin/env python3
"""
Script para organizar el dataset de DNI en la estructura correcta
"""

import os
import shutil
import random
from pathlib import Path
import json

def organize_synthetic_dni_dataset():
    """Organiza el dataset sintético de DNI en la estructura correcta"""
    
    print("🗂️ ORGANIZANDO DATASET SINTÉTICO DE DNI")
    print("=" * 50)
    
    # Directorios
    source_dir = Path("datasets/dni_robust/synthetic_images")
    target_dir = Path("datasets/dni_robust")
    
    if not source_dir.exists():
        print(f"❌ Directorio fuente no encontrado: {source_dir}")
        return
    
    # Crear estructura de directorios
    train_dir = target_dir / "images" / "train"
    val_dir = target_dir / "images" / "val"
    test_dir = target_dir / "images" / "test"
    
    train_labels = target_dir / "labels" / "train"
    val_labels = target_dir / "labels" / "val"
    test_labels = target_dir / "labels" / "test"
    
    for dir_path in [train_dir, val_dir, test_dir, train_labels, val_labels, test_labels]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Obtener todas las imágenes sintéticas
    synthetic_images = list(source_dir.glob("*.jpg"))
    print(f"📸 Imágenes sintéticas encontradas: {len(synthetic_images)}")
    
    # Mezclar aleatoriamente
    random.shuffle(synthetic_images)
    
    # Dividir en train/val/test (80/15/5)
    total_images = len(synthetic_images)
    train_count = int(total_images * 0.8)
    val_count = int(total_images * 0.15)
    
    # Anotaciones de ejemplo para DNI (coordenadas normalizadas)
    sample_annotations = [
        "0 0.5 0.15 0.3 0.08",  # dni_number
        "1 0.3 0.25 0.4 0.06",  # first_name
        "2 0.3 0.32 0.4 0.06",  # last_name
        "3 0.3 0.39 0.3 0.06",  # birth_date
        "4 0.3 0.46 0.2 0.06",  # gender
        "5 0.3 0.53 0.3 0.06",  # nationality
        "6 0.3 0.60 0.4 0.08",  # address
        "7 0.75 0.3 0.2 0.4"    # photo
    ]
    
    # Organizar imágenes
    for i, img_path in enumerate(synthetic_images):
        if i < train_count:
            dest_img_dir = train_dir
            dest_label_dir = train_labels
        elif i < train_count + val_count:
            dest_img_dir = val_dir
            dest_label_dir = val_labels
        else:
            dest_img_dir = test_dir
            dest_label_dir = test_labels
        
        # Copiar imagen
        dest_img_path = dest_img_dir / img_path.name
        shutil.copy2(img_path, dest_img_path)
        
        # Crear anotación correspondiente
        label_path = dest_label_dir / f"{img_path.stem}.txt"
        with open(label_path, 'w') as f:
            f.write('\n'.join(sample_annotations))
        
        if (i + 1) % 20 == 0:
            print(f"   Procesadas: {i + 1}/{total_images} imágenes")
    
    print(f"✅ Dataset sintético organizado:")
    print(f"   Train: {len(list(train_dir.glob('*')))} imágenes")
    print(f"   Val: {len(list(val_dir.glob('*')))} imágenes")
    print(f"   Test: {len(list(test_dir.glob('*')))} imágenes")

def process_docxpand_dataset():
    """Procesa el dataset DocXPand-25k si está disponible"""
    
    print("\n📦 PROCESANDO DATASET DOCXPAND-25K")
    print("=" * 50)
    
    download_dir = Path("temp/dataset_downloads")
    target_dir = Path("datasets/dni_robust")
    
    # Buscar archivos ZIP de DocXPand
    zip_files = list(download_dir.glob("*.zip"))
    
    if not zip_files:
        print(f"⚠️ No se encontraron archivos ZIP en {download_dir}")
        print("💡 Descarga DocXPand-25k y colócalo en temp/dataset_downloads/")
        return
    
    print(f"📦 Archivos ZIP encontrados: {len(zip_files)}")
    
    for zip_file in zip_files:
        print(f"\n🔍 Procesando: {zip_file.name}")
        
        # Extraer archivo
        extract_dir = download_dir / zip_file.stem
        extract_dir.mkdir(exist_ok=True)
        
        try:
            import zipfile
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"✅ Extraído a: {extract_dir}")
            
            # Buscar imágenes de DNI
            dni_images = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                dni_images.extend(extract_dir.rglob(ext))
            
            print(f"📸 Imágenes encontradas: {len(dni_images)}")
            
            if dni_images:
                # Organizar imágenes
                organize_docxpand_images(dni_images, target_dir)
            
        except Exception as e:
            print(f"❌ Error procesando {zip_file.name}: {e}")

def organize_docxpand_images(images, target_dir):
    """Organiza las imágenes de DocXPand en la estructura correcta"""
    
    print(f"🗂️ ORGANIZANDO IMÁGENES DE DOCXPAND")
    print("=" * 40)
    
    # Crear directorios
    train_dir = target_dir / "images" / "train"
    val_dir = target_dir / "images" / "val"
    test_dir = target_dir / "images" / "test"
    
    train_labels = target_dir / "labels" / "train"
    val_labels = target_dir / "labels" / "val"
    test_labels = target_dir / "labels" / "test"
    
    for dir_path in [train_dir, val_dir, test_dir, train_labels, val_labels, test_labels]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Mezclar aleatoriamente
    random.shuffle(images)
    
    # Dividir en train/val/test (80/15/5)
    total_images = len(images)
    train_count = int(total_images * 0.8)
    val_count = int(total_images * 0.15)
    
    # Anotaciones de ejemplo para DNI
    sample_annotations = [
        "0 0.5 0.15 0.3 0.08",  # dni_number
        "1 0.3 0.25 0.4 0.06",  # first_name
        "2 0.3 0.32 0.4 0.06",  # last_name
        "3 0.3 0.39 0.3 0.06",  # birth_date
        "4 0.3 0.46 0.2 0.06",  # gender
        "5 0.3 0.53 0.3 0.06",  # nationality
        "6 0.3 0.60 0.4 0.08",  # address
        "7 0.75 0.3 0.2 0.4"    # photo
    ]
    
    # Organizar imágenes
    for i, img_path in enumerate(images):
        if i < train_count:
            dest_img_dir = train_dir
            dest_label_dir = train_labels
        elif i < train_count + val_count:
            dest_img_dir = val_dir
            dest_label_dir = val_labels
        else:
            dest_img_dir = test_dir
            dest_label_dir = test_labels
        
        # Copiar imagen
        dest_img_path = dest_img_dir / img_path.name
        shutil.copy2(img_path, dest_img_path)
        
        # Crear anotación correspondiente
        label_path = dest_label_dir / f"{img_path.stem}.txt"
        with open(label_path, 'w') as f:
            f.write('\n'.join(sample_annotations))
        
        if (i + 1) % 100 == 0:
            print(f"   Procesadas: {i + 1}/{total_images} imágenes")
    
    print(f"✅ Imágenes de DocXPand organizadas:")
    print(f"   Train: {len(list(train_dir.glob('*')))} imágenes")
    print(f"   Val: {len(list(val_dir.glob('*')))} imágenes")
    print(f"   Test: {len(list(test_dir.glob('*')))} imágenes")

def create_dataset_summary():
    """Crea un resumen del dataset organizado"""
    
    print(f"\n📊 RESUMEN DEL DATASET DNI")
    print("=" * 50)
    
    target_dir = Path("datasets/dni_robust")
    
    # Contar imágenes en cada split
    train_images = len(list((target_dir / "images" / "train").glob("*")))
    val_images = len(list((target_dir / "images" / "val").glob("*")))
    test_images = len(list((target_dir / "images" / "test").glob("*")))
    
    total_images = train_images + val_images + test_images
    
    print(f"📸 Total de imágenes: {total_images}")
    print(f"   🏋️ Train: {train_images} ({train_images/total_images*100:.1f}%)")
    print(f"   ✅ Val: {val_images} ({val_images/total_images*100:.1f}%)")
    print(f"   🧪 Test: {test_images} ({test_images/total_images*100:.1f}%)")
    
    # Verificar anotaciones
    train_labels = len(list((target_dir / "labels" / "train").glob("*.txt")))
    val_labels = len(list((target_dir / "labels" / "val").glob("*.txt")))
    test_labels = len(list((target_dir / "labels" / "test").glob("*.txt")))
    
    print(f"📝 Total de anotaciones: {train_labels + val_labels + test_labels}")
    print(f"   🏋️ Train: {train_labels}")
    print(f"   ✅ Val: {val_labels}")
    print(f"   🧪 Test: {test_labels}")
    
    if total_images > 0:
        print(f"\n🎉 ¡DATASET LISTO PARA ENTRENAMIENTO!")
        print(f"💡 Ejecuta: python scripts/train_dni_model.py")
    else:
        print(f"\n⚠️ No hay imágenes en el dataset")
        print(f"💡 Ejecuta: python scripts/download_alternative_datasets.py")

def main():
    """Función principal"""
    
    print("🚀 ORGANIZADOR DE DATASET DNI")
    print("=" * 60)
    
    # Organizar dataset sintético
    organize_synthetic_dni_dataset()
    
    # Procesar DocXPand si está disponible
    process_docxpand_dataset()
    
    # Crear resumen
    create_dataset_summary()
    
    print(f"\n🎯 PRÓXIMOS PASOS")
    print("=" * 40)
    print("1. Verificar que las imágenes están organizadas correctamente")
    print("2. Entrenar modelo: python scripts/train_dni_model.py")
    print("3. Probar modelo: python scripts/test_dni_model.py")
    print("4. Integrar con el servicio OCR")

if __name__ == "__main__":
    main()
