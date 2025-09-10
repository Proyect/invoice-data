#!/usr/bin/env python3
"""
Ejemplo simple para crear y validar un dataset de ejemplo
"""

import os
import cv2
import numpy as np
from pathlib import Path

def create_simple_example():
    """Crea un ejemplo simple sin emojis para evitar problemas de encoding"""
    print("Creando ejemplo de dataset...")
    
    # Crear directorios
    os.makedirs("example_dataset/images", exist_ok=True)
    os.makedirs("example_dataset/labels", exist_ok=True)
    
    # Crear imagen de ejemplo (factura simulada)
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Dibujar elementos de la factura
    cv2.rectangle(img, (50, 50), (750, 550), (200, 200, 200), 2)
    cv2.putText(img, "FACTURA EJEMPLO", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "Numero: 001-001-000123", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Fecha: 08/09/2024", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Proveedor: Empresa XYZ", (100, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "CUIT: 20-12345678-9", (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Subtotal: $1,000.00", (100, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "IVA: $210.00", (100, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Total: $1,210.00", (100, 520), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Guardar imagen
    cv2.imwrite("example_dataset/images/factura_ejemplo.jpg", img)
    
    # Crear anotaciones YOLO (formato: class_id center_x center_y width height)
    annotations = [
        "0 0.4 0.1875 0.25 0.0417",   # invoice_number (numero de factura)
        "1 0.25 0.25 0.15 0.0417",    # date (fecha)
        "2 0.35 0.3125 0.3 0.0417",   # vendor (proveedor)
        "3 0.35 0.375 0.25 0.0417",   # cuit
        "4 0.3 0.75 0.2 0.0417",      # subtotal
        "5 0.25 0.8 0.15 0.0417",     # tax (IVA)
        "6 0.25 0.8667 0.2 0.0417"    # total
    ]
    
    with open("example_dataset/labels/factura_ejemplo.txt", 'w') as f:
        for ann in annotations:
            f.write(ann + '\n')
    
    print("Ejemplo creado exitosamente en example_dataset/")
    print("- Imagen: example_dataset/images/factura_ejemplo.jpg")
    print("- Anotaciones: example_dataset/labels/factura_ejemplo.txt")
    
    return "example_dataset/images/factura_ejemplo.jpg", "example_dataset/labels/factura_ejemplo.txt"

def validate_simple_annotations(labels_dir):
    """Valida anotaciones de forma simple"""
    print(f"Validando anotaciones en {labels_dir}")
    
    label_files = list(Path(labels_dir).glob("*.txt"))
    print(f"Archivos encontrados: {len(label_files)}")
    
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
    
    class_counts = {i: 0 for i in range(len(class_names))}
    total_annotations = 0
    
    for label_file in label_files:
        print(f"Procesando: {label_file.name}")
        with open(label_file, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) == 5:
                class_id = int(parts[0])
                if class_id in class_counts:
                    class_counts[class_id] += 1
                    total_annotations += 1
    
    print(f"Total de anotaciones: {total_annotations}")
    print("Distribucion por clase:")
    for class_id, count in class_counts.items():
        if count > 0:
            class_name = class_names.get(class_id, f"Clase_{class_id}")
            print(f"  - {class_name}: {count}")
    
    return class_counts

if __name__ == "__main__":
    print("=== EJEMPLO DE DATASET YOLO ===")
    
    # Crear ejemplo
    img_path, label_path = create_simple_example()
    
    # Validar
    validate_simple_annotations("example_dataset/labels")
    
    print("\nEjemplo completado. Puedes:")
    print("1. Ver la imagen generada en: example_dataset/images/factura_ejemplo.jpg")
    print("2. Ver las anotaciones en: example_dataset/labels/factura_ejemplo.txt")
    print("3. Usar este ejemplo como base para tu dataset real")
