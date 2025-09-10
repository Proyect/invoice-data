#!/usr/bin/env python3
"""
Utilidades para manejo de datasets YOLO
"""

import os
import shutil
import random
import cv2
import numpy as np
from pathlib import Path
import yaml
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

def split_dataset(images_dir, labels_dir, output_dir, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
    """
    Divide el dataset en train/val/test manteniendo la correspondencia imagen-label
    """
    print(f"📂 Dividiendo dataset desde {images_dir}")
    
    # Obtener lista de imágenes
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    images = []
    
    for ext in image_extensions:
        images.extend(list(Path(images_dir).glob(f"*{ext}")))
        images.extend(list(Path(images_dir).glob(f"*{ext.upper()}")))
    
    print(f"📊 Encontradas {len(images)} imágenes")
    
    # Verificar que cada imagen tenga su label
    valid_pairs = []
    for img_path in images:
        label_path = Path(labels_dir) / f"{img_path.stem}.txt"
        if label_path.exists():
            valid_pairs.append((img_path, label_path))
        else:
            print(f"⚠️  Label faltante para: {img_path.name}")
    
    print(f"✅ Pares válidos imagen-label: {len(valid_pairs)}")
    
    if len(valid_pairs) == 0:
        print("❌ No se encontraron pares válidos imagen-label")
        return
    
    # Mezclar aleatoriamente
    random.shuffle(valid_pairs)
    
    # Calcular divisiones
    total = len(valid_pairs)
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)
    test_count = total - train_count - val_count
    
    print(f"📊 División del dataset:")
    print(f"  - Train: {train_count} ({train_ratio*100:.1f}%)")
    print(f"  - Val: {val_count} ({val_ratio*100:.1f}%)")
    print(f"  - Test: {test_count} ({test_ratio*100:.1f}%)")
    
    # Crear directorios
    splits = ['train', 'val', 'test']
    for split in splits:
        os.makedirs(f"{output_dir}/images/{split}", exist_ok=True)
        os.makedirs(f"{output_dir}/labels/{split}", exist_ok=True)
    
    # Dividir archivos
    split_ranges = {
        'train': (0, train_count),
        'val': (train_count, train_count + val_count),
        'test': (train_count + val_count, total)
    }
    
    for split, (start, end) in split_ranges.items():
        print(f"📁 Copiando archivos para {split}...")
        
        for img_path, label_path in valid_pairs[start:end]:
            # Copiar imagen
            dst_img = f"{output_dir}/images/{split}/{img_path.name}"
            shutil.copy2(img_path, dst_img)
            
            # Copiar label
            dst_label = f"{output_dir}/labels/{split}/{label_path.name}"
            shutil.copy2(label_path, dst_label)
    
    print("Dataset dividido exitosamente")

def validate_annotations(labels_dir, class_names):
    """
    Valida las anotaciones YOLO
    """
    print(f"Validando anotaciones en {labels_dir}")
    
    label_files = list(Path(labels_dir).glob("*.txt"))
    issues = []
    class_counts = {i: 0 for i in range(len(class_names))}
    
    for label_file in label_files:
        with open(label_file, 'r') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) != 5:
                issues.append(f"{label_file.name}:{line_num} - Formato incorrecto (debe tener 5 valores)")
                continue
            
            try:
                class_id = int(parts[0])
                x_center, y_center, width, height = map(float, parts[1:])
                
                # Validar clase
                if class_id < 0 or class_id >= len(class_names):
                    issues.append(f"{label_file.name}:{line_num} - Clase inválida: {class_id}")
                else:
                    class_counts[class_id] += 1
                
                # Validar coordenadas (deben estar entre 0 y 1)
                for coord_name, coord_val in [('x_center', x_center), ('y_center', y_center), 
                                            ('width', width), ('height', height)]:
                    if coord_val < 0 or coord_val > 1:
                        issues.append(f"{label_file.name}:{line_num} - {coord_name} fuera de rango: {coord_val}")
                
            except ValueError as e:
                issues.append(f"{label_file.name}:{line_num} - Error de formato: {e}")
    
    # Mostrar resultados
    print(f"📊 Estadísticas de validación:")
    print(f"  - Archivos procesados: {len(label_files)}")
    print(f"  - Problemas encontrados: {len(issues)}")
    
    print(f"\n📈 Distribución de clases:")
    for class_id, count in class_counts.items():
        class_name = class_names.get(class_id, f"Clase_{class_id}")
        print(f"  - {class_name}: {count}")
    
    if issues:
        print(f"\n⚠️  Problemas encontrados:")
        for issue in issues[:10]:  # Mostrar solo los primeros 10
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... y {len(issues) - 10} más")
    else:
        print("✅ Todas las anotaciones son válidas")
    
    return issues, class_counts

def visualize_annotations(image_path, label_path, class_names, output_path=None):
    """
    Visualiza las anotaciones sobre la imagen
    """
    # Cargar imagen
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ No se pudo cargar la imagen: {image_path}")
        return
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w = image.shape[:2]
    
    # Leer anotaciones
    if not os.path.exists(label_path):
        print(f"❌ Archivo de labels no encontrado: {label_path}")
        return
    
    with open(label_path, 'r') as f:
        lines = f.readlines()
    
    # Dibujar bounding boxes
    colors = plt.cm.Set3(np.linspace(0, 1, len(class_names)))
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        if len(parts) != 5:
            continue
        
        class_id = int(parts[0])
        x_center, y_center, width, height = map(float, parts[1:])
        
        # Convertir a coordenadas de píxeles
        x_center *= w
        y_center *= h
        width *= w
        height *= h
        
        # Calcular esquinas del bounding box
        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)
        
        # Dibujar rectángulo
        color = tuple(int(c * 255) for c in colors[class_id][:3])
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Añadir etiqueta
        class_name = class_names.get(class_id, f"Clase_{class_id}")
        label_text = f"{class_name}"
        
        # Fondo para el texto
        (text_w, text_h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(image, (x1, y1 - text_h - 5), (x1 + text_w, y1), color, -1)
        cv2.putText(image, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Mostrar o guardar imagen
    plt.figure(figsize=(12, 8))
    plt.imshow(image)
    plt.axis('off')
    plt.title(f"Anotaciones: {Path(image_path).name}")
    
    if output_path:
        plt.savefig(output_path, bbox_inches='tight', dpi=150)
        print(f"✅ Visualización guardada en: {output_path}")
    else:
        plt.show()

def augment_dataset(images_dir, labels_dir, output_dir, augmentations_per_image=3):
    """
    Aplica aumentaciones básicas al dataset
    """
    print(f"🔄 Aplicando aumentaciones al dataset")
    
    os.makedirs(f"{output_dir}/images", exist_ok=True)
    os.makedirs(f"{output_dir}/labels", exist_ok=True)
    
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png']:
        image_files.extend(list(Path(images_dir).glob(f"*{ext}")))
    
    total_generated = 0
    
    for img_path in image_files:
        label_path = Path(labels_dir) / f"{img_path.stem}.txt"
        
        if not label_path.exists():
            continue
        
        # Cargar imagen original
        image = cv2.imread(str(img_path))
        if image is None:
            continue
        
        # Leer anotaciones
        with open(label_path, 'r') as f:
            annotations = f.readlines()
        
        # Copiar originales
        shutil.copy2(img_path, f"{output_dir}/images/{img_path.name}")
        shutil.copy2(label_path, f"{output_dir}/labels/{label_path.name}")
        
        # Generar aumentaciones
        for i in range(augmentations_per_image):
            aug_image = image.copy()
            aug_annotations = annotations.copy()
            
            # Aplicar aumentaciones simples
            if random.random() > 0.5:
                # Ajuste de brillo
                brightness = random.uniform(0.8, 1.2)
                aug_image = cv2.convertScaleAbs(aug_image, alpha=brightness, beta=0)
            
            if random.random() > 0.5:
                # Ruido gaussiano
                noise = np.random.normal(0, 10, aug_image.shape).astype(np.uint8)
                aug_image = cv2.add(aug_image, noise)
            
            # Guardar imagen aumentada
            aug_name = f"{img_path.stem}_aug_{i}{img_path.suffix}"
            cv2.imwrite(f"{output_dir}/images/{aug_name}", aug_image)
            
            # Guardar anotaciones (sin cambios para aumentaciones simples)
            with open(f"{output_dir}/labels/{img_path.stem}_aug_{i}.txt", 'w') as f:
                f.writelines(aug_annotations)
            
            total_generated += 1
    
    print(f"Generadas {total_generated} imagenes aumentadas")

def create_sample_annotations():
    """
    Crea anotaciones de ejemplo para testing
    """
    print("Creando anotaciones de ejemplo...")
    
    # Crear directorios de ejemplo
    os.makedirs("example_dataset/images", exist_ok=True)
    os.makedirs("example_dataset/labels", exist_ok=True)
    
    # Crear imagen de ejemplo
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Simular una factura simple
    cv2.rectangle(img, (50, 50), (750, 550), (200, 200, 200), 2)
    cv2.putText(img, "FACTURA EJEMPLO", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "Numero: 001-001-000123", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Fecha: 08/09/2024", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Proveedor: Empresa XYZ", (100, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Total: $1,234.56", (100, 500), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Guardar imagen
    cv2.imwrite("example_dataset/images/factura_ejemplo.jpg", img)
    
    # Crear anotaciones correspondientes (formato YOLO)
    annotations = [
        "0 0.4 0.1875 0.25 0.0417",  # invoice_number
        "1 0.25 0.25 0.15 0.0417",   # date  
        "2 0.35 0.3125 0.3 0.0417",  # vendor
        "6 0.25 0.8333 0.2 0.0667"   # total
    ]
    
    with open("example_dataset/labels/factura_ejemplo.txt", 'w') as f:
        for ann in annotations:
            f.write(ann + '\n')
    
    print("Ejemplo creado en example_dataset/")
    return "example_dataset/images/factura_ejemplo.jpg", "example_dataset/labels/factura_ejemplo.txt"

if __name__ == "__main__":
    # Ejemplo de uso
    print("Utilidades de Dataset YOLO")
    
    # Crear ejemplo
    img_path, label_path = create_sample_annotations()
    
    # Definir clases
    class_names = {
        0: 'invoice_number',
        1: 'date', 
        2: 'vendor',
        3: 'cuit',
        4: 'subtotal',
        5: 'tax',
        6: 'total',
        7: 'items_table'
    }
    
    # Validar anotaciones
    validate_annotations("example_dataset/labels", class_names)
    
    # Visualizar ejemplo
    visualize_annotations(img_path, label_path, class_names, "example_visualization.png")
    
    print("Ejemplo completado")
