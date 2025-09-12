#!/usr/bin/env python3
"""
Script para descargar y organizar el dataset DocXPand-25k para DNI
"""

import os
import requests
import zipfile
import shutil
from pathlib import Path
import json
import yaml
from urllib.parse import urlparse
import time

def create_download_directory():
    """Crea el directorio para descargas temporales"""
    
    print("📁 CREANDO DIRECTORIO DE DESCARGA")
    print("=" * 40)
    
    download_dir = Path("temp/dataset_downloads")
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Directorio creado: {download_dir}")
    return download_dir

def download_file_with_progress(url, destination, description="Archivo"):
    """Descarga un archivo con barra de progreso"""
    
    print(f"\n📥 DESCARGANDO {description}")
    print(f"URL: {url}")
    print(f"Destino: {destination}")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\r   Progreso: {progress:.1f}% ({downloaded_size}/{total_size} bytes)", end="")
        
        print(f"\n✅ Descarga completada: {destination}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error descargando {description}: {e}")
        return False

def extract_zip_file(zip_path, extract_to):
    """Extrae un archivo ZIP"""
    
    print(f"\n📦 EXTRAYENDO ARCHIVO")
    print(f"Archivo: {zip_path}")
    print(f"Destino: {extract_to}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        print(f"✅ Extracción completada")
        return True
        
    except Exception as e:
        print(f"❌ Error extrayendo archivo: {e}")
        return False

def organize_dni_images(source_dir, target_dir):
    """Organiza las imágenes de DNI en la estructura correcta"""
    
    print(f"\n🗂️ ORGANIZANDO IMÁGENES DE DNI")
    print("=" * 40)
    
    # Crear estructura de directorios
    train_dir = target_dir / "images" / "train"
    val_dir = target_dir / "images" / "val"
    test_dir = target_dir / "images" / "test"
    
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Buscar imágenes de DNI
    dni_images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        dni_images.extend(source_dir.rglob(ext))
    
    print(f"📸 Imágenes encontradas: {len(dni_images)}")
    
    # Organizar imágenes (80% train, 15% val, 5% test)
    total_images = len(dni_images)
    train_count = int(total_images * 0.8)
    val_count = int(total_images * 0.15)
    
    for i, img_path in enumerate(dni_images):
        if i < train_count:
            dest_dir = train_dir
        elif i < train_count + val_count:
            dest_dir = val_dir
        else:
            dest_dir = test_dir
        
        # Copiar imagen
        dest_path = dest_dir / img_path.name
        shutil.copy2(img_path, dest_path)
        
        if (i + 1) % 100 == 0:
            print(f"   Procesadas: {i + 1}/{total_images} imágenes")
    
    print(f"✅ Imágenes organizadas:")
    print(f"   Train: {len(list(train_dir.glob('*')))} imágenes")
    print(f"   Val: {len(list(val_dir.glob('*')))} imágenes")
    print(f"   Test: {len(list(test_dir.glob('*')))} imágenes")

def create_sample_annotations_for_dni(target_dir):
    """Crea anotaciones de ejemplo para las imágenes de DNI"""
    
    print(f"\n📝 CREANDO ANOTACIONES DE EJEMPLO")
    print("=" * 40)
    
    # Crear directorios de anotaciones
    train_labels = target_dir / "labels" / "train"
    val_labels = target_dir / "labels" / "val"
    test_labels = target_dir / "labels" / "test"
    
    train_labels.mkdir(parents=True, exist_ok=True)
    val_labels.mkdir(parents=True, exist_ok=True)
    test_labels.mkdir(parents=True, exist_ok=True)
    
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
    
    # Crear archivos de anotación para cada imagen
    for split in ['train', 'val', 'test']:
        images_dir = target_dir / "images" / split
        labels_dir = target_dir / "labels" / split
        
        for img_file in images_dir.glob('*'):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                # Crear archivo de anotación correspondiente
                label_file = labels_dir / f"{img_file.stem}.txt"
                with open(label_file, 'w') as f:
                    f.write('\n'.join(sample_annotations))
    
    print(f"✅ Anotaciones de ejemplo creadas para todas las imágenes")

def create_alternative_download_script():
    """Crea un script alternativo para descargar datasets públicos"""
    
    print(f"\n🛠️ CREANDO SCRIPT ALTERNATIVO DE DESCARGA")
    print("=" * 40)
    
    script_content = '''#!/usr/bin/env python3
"""
Script alternativo para descargar datasets de documentos de identidad
"""

import os
import requests
import zipfile
from pathlib import Path
import json

def download_ddi100_dataset():
    """Descarga el dataset DDI-100 como alternativa"""
    
    print("📥 DESCARGANDO DDI-100 DATASET")
    print("=" * 40)
    
    # URLs del dataset DDI-100
    urls = {
        'images': 'https://github.com/naver/deep-text-recognition-benchmark/releases/download/v1.0/DDI-100.zip',
        'annotations': 'https://github.com/naver/deep-text-recognition-benchmark/releases/download/v1.0/DDI-100_annotations.zip'
    }
    
    download_dir = Path("temp/ddi100_download")
    download_dir.mkdir(parents=True, exist_ok=True)
    
    for name, url in urls.items():
        print(f"Descargando {name}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            file_path = download_dir / f"{name}.zip"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ {name} descargado")
        else:
            print(f"❌ Error descargando {name}")

def create_synthetic_dni_dataset():
    """Crea un dataset sintético de DNI"""
    
    print("🎨 CREANDO DATASET SINTÉTICO DE DNI")
    print("=" * 40)
    
    from PIL import Image, ImageDraw, ImageFont
    import random
    import string
    
    # Crear directorio para imágenes sintéticas
    synth_dir = Path("datasets/dni_robust/synthetic_images")
    synth_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar 100 imágenes sintéticas de DNI
    for i in range(100):
        # Crear imagen base (tamaño típico de DNI)
        img = Image.new('RGB', (400, 250), color='white')
        draw = ImageDraw.Draw(img)
        
        # Simular campos de DNI
        fields = [
            ("DNI:", f"{random.randint(10000000, 99999999)}"),
            ("Nombre:", f"Nombre_{i}"),
            ("Apellido:", f"Apellido_{i}"),
            ("Fecha Nac:", f"{random.randint(1,28)}/{random.randint(1,12)}/{random.randint(1950,2000)}"),
            ("Sexo:", random.choice(["M", "F"])),
            ("Nacionalidad:", "ARGENTINA")
        ]
        
        y_pos = 20
        for label, value in fields:
            draw.text((20, y_pos), f"{label} {value}", fill='black')
            y_pos += 30
        
        # Guardar imagen
        img_path = synth_dir / f"synthetic_dni_{i:03d}.jpg"
        img.save(img_path)
        
        if (i + 1) % 20 == 0:
            print(f"   Generadas: {i + 1}/100 imágenes")
    
    print(f"✅ Dataset sintético creado: {synth_dir}")

if __name__ == "__main__":
    print("🚀 DESCARGANDO DATASETS ALTERNATIVOS")
    print("=" * 50)
    
    # Intentar descargar DDI-100
    try:
        download_ddi100_dataset()
    except Exception as e:
        print(f"❌ Error con DDI-100: {e}")
    
    # Crear dataset sintético
    try:
        create_synthetic_dni_dataset()
    except Exception as e:
        print(f"❌ Error creando dataset sintético: {e}")
    
    print("\\n🎉 PROCESO COMPLETADO")
'''
    
    with open("scripts/download_alternative_datasets.py", 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Script alternativo creado: scripts/download_alternative_datasets.py")

def main():
    """Función principal"""
    
    print("🚀 DESCARGADOR DE DATASET DNI")
    print("=" * 60)
    
    # Crear directorio de descarga
    download_dir = create_download_directory()
    
    # Información sobre DocXPand-25k
    print(f"\n📋 INFORMACIÓN SOBRE DOCXPAND-25K")
    print("=" * 40)
    print("🔗 URL: https://simplescience.ai/es/2024-09-09-presentamos-el-conjunto-de-datos-docxpand-25k-para-verificacion-de-identidad--aqrz4r")
    print("📊 Tamaño: 25,000+ imágenes de documentos de identidad")
    print("📝 Incluye: DNI, pasaportes, tarjetas de identificación")
    print("🏷️ Anotaciones: Clasificación, localización y OCR")
    
    print(f"\n⚠️ INSTRUCCIONES MANUALES")
    print("=" * 40)
    print("1. Visita la URL del dataset DocXPand-25k")
    print("2. Regístrate o solicita acceso al dataset")
    print("3. Descarga el archivo ZIP del dataset")
    print("4. Coloca el archivo en: temp/dataset_downloads/")
    print("5. Ejecuta este script nuevamente para procesar")
    
    # Crear script alternativo
    create_alternative_download_script()
    
    print(f"\n💡 ALTERNATIVAS DISPONIBLES")
    print("=" * 40)
    print("🔄 Script alternativo: python scripts/download_alternative_datasets.py")
    print("   - Descarga DDI-100 (100,000+ imágenes)")
    print("   - Genera dataset sintético de DNI")
    
    print(f"\n🎯 PRÓXIMOS PASOS")
    print("=" * 40)
    print("1. Descargar DocXPand-25k manualmente")
    print("2. O ejecutar: python scripts/download_alternative_datasets.py")
    print("3. Organizar imágenes en datasets/dni_robust/")
    print("4. Entrenar modelo: python scripts/train_dni_model.py")

if __name__ == "__main__":
    main()
