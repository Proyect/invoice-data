#!/usr/bin/env python3
"""
Script para corregir las anotaciones del dataset de DNI
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

def analyze_synthetic_image(img_path):
    """Analiza una imagen sintética para entender su estructura"""
    
    print(f"🔍 ANALIZANDO IMAGEN: {img_path.name}")
    
    # Cargar imagen
    img = Image.open(img_path)
    width, height = img.size
    
    print(f"   Tamaño: {width}x{height}")
    
    # Las imágenes sintéticas tienen texto en líneas verticales
    # Estructura aproximada basada en el código de generación:
    # - DNI: línea 1 (y=20)
    # - Nombre: línea 2 (y=50) 
    # - Apellido: línea 3 (y=80)
    # - Fecha Nac: línea 4 (y=110)
    # - Sexo: línea 5 (y=140)
    # - Nacionalidad: línea 6 (y=170)
    
    # Calcular coordenadas normalizadas basadas en la estructura real
    annotations = []
    
    # DNI (primera línea)
    dni_y = 20
    dni_bbox = [0.1, dni_y/height, 0.9, (dni_y + 20)/height]
    annotations.append(f"0 {dni_bbox[0]} {dni_bbox[1]} {dni_bbox[2]} {dni_bbox[3]}")
    
    # Nombre (segunda línea)
    name_y = 50
    name_bbox = [0.1, name_y/height, 0.9, (name_y + 20)/height]
    annotations.append(f"1 {name_bbox[0]} {name_bbox[1]} {name_bbox[2]} {name_bbox[3]}")
    
    # Apellido (tercera línea)
    lastname_y = 80
    lastname_bbox = [0.1, lastname_y/height, 0.9, (lastname_y + 20)/height]
    annotations.append(f"2 {lastname_bbox[0]} {lastname_bbox[1]} {lastname_bbox[2]} {lastname_bbox[3]}")
    
    # Fecha de nacimiento (cuarta línea)
    birth_y = 110
    birth_bbox = [0.1, birth_y/height, 0.9, (birth_y + 20)/height]
    annotations.append(f"3 {birth_bbox[0]} {birth_bbox[1]} {birth_bbox[2]} {birth_bbox[3]}")
    
    # Sexo (quinta línea)
    gender_y = 140
    gender_bbox = [0.1, gender_y/height, 0.9, (gender_y + 20)/height]
    annotations.append(f"4 {gender_bbox[0]} {gender_bbox[1]} {gender_bbox[2]} {gender_bbox[3]}")
    
    # Nacionalidad (sexta línea)
    nationality_y = 170
    nationality_bbox = [0.1, nationality_y/height, 0.9, (nationality_y + 20)/height]
    annotations.append(f"5 {nationality_bbox[0]} {nationality_bbox[1]} {nationality_bbox[2]} {nationality_bbox[3]}")
    
    # Address (séptima línea - si existe)
    address_y = 200
    if address_y < height - 20:
        address_bbox = [0.1, address_y/height, 0.9, (address_y + 20)/height]
        annotations.append(f"6 {address_bbox[0]} {address_bbox[1]} {address_bbox[2]} {address_bbox[3]}")
    
    # Photo (área derecha simulada)
    photo_bbox = [0.7, 0.1, 0.95, 0.6]
    annotations.append(f"7 {photo_bbox[0]} {photo_bbox[1]} {photo_bbox[2]} {photo_bbox[3]}")
    
    return annotations

def fix_all_annotations():
    """Corrige todas las anotaciones del dataset"""
    
    print("🔧 CORRIGIENDO ANOTACIONES DEL DATASET DNI")
    print("=" * 50)
    
    # Directorios
    images_dir = Path("datasets/dni_robust/synthetic_images")
    train_labels_dir = Path("datasets/dni_robust/labels/train")
    val_labels_dir = Path("datasets/dni_robust/labels/val")
    test_labels_dir = Path("datasets/dni_robust/labels/test")
    
    # Obtener todas las imágenes sintéticas
    synthetic_images = list(images_dir.glob("*.jpg"))
    print(f"📸 Imágenes sintéticas encontradas: {len(synthetic_images)}")
    
    # Procesar cada imagen
    for i, img_path in enumerate(synthetic_images):
        # Generar anotaciones corregidas
        annotations = analyze_synthetic_image(img_path)
        
        # Determinar en qué split está la imagen
        img_name = img_path.stem
        
        # Buscar en train
        train_label_path = train_labels_dir / f"{img_name}.txt"
        if train_label_path.exists():
            with open(train_label_path, 'w') as f:
                f.write('\n'.join(annotations))
            print(f"   ✅ Train: {img_name}.txt")
        
        # Buscar en val
        val_label_path = val_labels_dir / f"{img_name}.txt"
        if val_label_path.exists():
            with open(val_label_path, 'w') as f:
                f.write('\n'.join(annotations))
            print(f"   ✅ Val: {img_name}.txt")
        
        # Buscar en test
        test_label_path = test_labels_dir / f"{img_name}.txt"
        if test_label_path.exists():
            with open(test_label_path, 'w') as f:
                f.write('\n'.join(annotations))
            print(f"   ✅ Test: {img_name}.txt")
        
        if (i + 1) % 20 == 0:
            print(f"   Procesadas: {i + 1}/{len(synthetic_images)} imágenes")

def create_improved_synthetic_dataset():
    """Crea un dataset sintético mejorado con estructura más realista de DNI"""
    
    print("\n🎨 CREANDO DATASET SINTÉTICO MEJORADO")
    print("=" * 50)
    
    from PIL import Image, ImageDraw, ImageFont
    import random
    import string
    
    # Crear directorio para imágenes mejoradas
    improved_dir = Path("datasets/dni_robust/improved_synthetic")
    improved_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar 50 imágenes mejoradas
    for i in range(50):
        # Crear imagen base (tamaño típico de DNI argentino)
        img = Image.new('RGB', (400, 250), color='white')
        draw = ImageDraw.Draw(img)
        
        # Intentar cargar una fuente más realista
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        # Simular estructura de DNI argentino
        # Encabezado
        draw.rectangle([10, 10, 390, 30], outline='black', width=2)
        draw.text((20, 15), "REPUBLICA ARGENTINA", fill='black', font=font)
        
        # DNI
        dni_num = f"{random.randint(10000000, 99999999)}"
        draw.text((20, 50), f"DNI: {dni_num}", fill='black', font=font)
        
        # Nombre
        first_name = f"NOMBRE_{i}"
        draw.text((20, 80), f"NOMBRE: {first_name}", fill='black', font=font)
        
        # Apellido
        last_name = f"APELLIDO_{i}"
        draw.text((20, 110), f"APELLIDO: {last_name}", fill='black', font=font)
        
        # Fecha de nacimiento
        birth_date = f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/{random.randint(1950,2000)}"
        draw.text((20, 140), f"FECHA NAC: {birth_date}", fill='black', font=font)
        
        # Sexo
        gender = random.choice(["M", "F"])
        draw.text((20, 170), f"SEXO: {gender}", fill='black', font=font)
        
        # Nacionalidad
        draw.text((20, 200), "NACIONALIDAD: ARGENTINA", fill='black', font=font)
        
        # Simular foto (área derecha)
        draw.rectangle([280, 50, 380, 200], outline='black', width=2)
        draw.text((290, 100), "FOTO", fill='gray', font=font)
        
        # Guardar imagen
        img_path = improved_dir / f"improved_dni_{i:03d}.jpg"
        img.save(img_path)
        
        if (i + 1) % 10 == 0:
            print(f"   Generadas: {i + 1}/50 imágenes mejoradas")
    
    print(f"✅ Dataset mejorado creado: {improved_dir}")

def main():
    """Función principal"""
    
    print("🚀 CORRECTOR DE ANOTACIONES DNI")
    print("=" * 60)
    
    # Paso 1: Corregir anotaciones existentes
    fix_all_annotations()
    
    # Paso 2: Crear dataset sintético mejorado
    create_improved_synthetic_dataset()
    
    print(f"\n🎉 CORRECCIÓN COMPLETADA")
    print("=" * 40)
    print("✅ Anotaciones corregidas para imágenes existentes")
    print("✅ Dataset sintético mejorado creado")
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Reentrenar modelo: python scripts/quick_train_dni.py")
    print("2. Probar modelo mejorado: python scripts/test_dni_model.py")

if __name__ == "__main__":
    main()
