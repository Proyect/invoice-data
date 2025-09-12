#!/usr/bin/env python3
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
    
    print("\n🎉 PROCESO COMPLETADO")
