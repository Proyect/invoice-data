#!/usr/bin/env python3
"""
Script para probar el modelo actual con imágenes del dataset de Downloads
"""

import os
import sys
import json
import random
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np

def test_model_with_downloads():
    """Prueba el modelo actual con imágenes de Downloads"""
    
    print("🧪 PROBANDO MODELO CON IMÁGENES DE DOWNLOADS")
    print("=" * 60)
    
    # Rutas
    downloads_path = Path("C:/Users/amdiaz/Downloads/FATURA/invoices_dataset_final")
    model_path = "models/yolo_models/invoices_cpu_abs/weights/best.pt"
    
    # Verificar que el modelo existe
    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        print("💡 Usando modelo genérico...")
        model_path = "models/yolo_models/yolov8n.pt"
    
    # Verificar que el dataset existe
    if not downloads_path.exists():
        print(f"❌ Dataset no encontrado: {downloads_path}")
        return
    
    try:
        # Cargar modelo
        print(f"📦 Cargando modelo: {model_path}")
        model = YOLO(model_path)
        
        # Mostrar información del modelo
        print(f"✅ Modelo cargado exitosamente")
        print(f"📊 Clases detectadas: {len(model.names)}")
        for i, name in model.names.items():
            print(f"   {i}: {name}")
        
        # Seleccionar imágenes aleatorias para probar
        images_dir = downloads_path / "images"
        all_images = list(images_dir.glob("*.jpg"))
        
        if not all_images:
            print("❌ No se encontraron imágenes en el dataset")
            return
        
        # Seleccionar 5 imágenes aleatorias
        test_images = random.sample(all_images, min(5, len(all_images)))
        
        print(f"\n🔍 PROBANDO CON {len(test_images)} IMÁGENES ALEATORIAS")
        print("=" * 50)
        
        results_summary = []
        
        for i, img_path in enumerate(test_images, 1):
            print(f"\n📸 Imagen {i}: {img_path.name}")
            
            # Realizar predicción
            results = model(str(img_path), conf=0.25)  # Confianza mínima 25%
            
            # Procesar resultados
            detections = []
            for r in results:
                if r.boxes is not None:
                    for box in r.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        conf = box.conf[0].item()
                        cls = int(box.cls[0].item())
                        class_name = model.names[cls]
                        
                        detections.append({
                            'class': class_name,
                            'confidence': conf,
                            'bbox': [x1, y1, x2, y2]
                        })
            
            # Mostrar resultados
            print(f"   Detecciones encontradas: {len(detections)}")
            if detections:
                for det in detections:
                    print(f"     - {det['class']}: {det['confidence']:.2f} confianza")
            
            # Guardar imagen con detecciones
            output_path = f"models/yolo_models/invoices_cpu_abs/test_downloads_{i}.jpg"
            for r in results:
                r.save(output_path)
            print(f"   💾 Resultado guardado: {output_path}")
            
            results_summary.append({
                'image': img_path.name,
                'detections': len(detections),
                'classes_found': [det['class'] for det in detections]
            })
        
        # Resumen final
        print(f"\n📊 RESUMEN DE PRUEBAS")
        print("=" * 50)
        total_detections = sum(r['detections'] for r in results_summary)
        avg_detections = total_detections / len(results_summary)
        
        print(f"Total de imágenes probadas: {len(results_summary)}")
        print(f"Total de detecciones: {total_detections}")
        print(f"Promedio de detecciones por imagen: {avg_detections:.1f}")
        
        # Mostrar clases más detectadas
        all_classes = []
        for r in results_summary:
            all_classes.extend(r['classes_found'])
        
        if all_classes:
            from collections import Counter
            class_counts = Counter(all_classes)
            print(f"\n🏷️ CLASES MÁS DETECTADAS:")
            for class_name, count in class_counts.most_common():
                print(f"   {class_name}: {count} veces")
        
        # Comparar con anotaciones reales
        print(f"\n🔍 COMPARANDO CON ANOTACIONES REALES")
        print("=" * 50)
        
        for i, img_path in enumerate(test_images, 1):
            img_name = img_path.stem
            annotation_file = downloads_path / "Annotations" / "Original_Format" / f"{img_name}.json"
            
            if annotation_file.exists():
                with open(annotation_file, 'r', encoding='utf-8') as f:
                    real_annotations = json.load(f)
                
                real_classes = [key for key in real_annotations.keys() if key != "OTHER" and isinstance(real_annotations[key], dict) and "bbox" in real_annotations[key]]
                detected_classes = results_summary[i-1]['classes_found']
                
                print(f"📸 {img_name}:")
                print(f"   Anotaciones reales: {len(real_classes)} clases")
                print(f"   Detecciones del modelo: {len(detected_classes)} clases")
                
                # Calcular precisión
                if real_classes:
                    precision = len(set(detected_classes) & set(real_classes)) / len(real_classes) * 100
                    print(f"   Precisión: {precision:.1f}%")
        
        return results_summary
        
    except Exception as e:
        print(f"❌ Error probando modelo: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_with_different_confidence_levels():
    """Prueba el modelo con diferentes niveles de confianza"""
    
    print(f"\n🎯 PROBANDO CON DIFERENTES NIVELES DE CONFIANZA")
    print("=" * 50)
    
    model_path = "models/yolo_models/invoices_cpu_abs/weights/best.pt"
    downloads_path = Path("C:/Users/amdiaz/Downloads/FATURA/invoices_dataset_final")
    
    if not os.path.exists(model_path) or not downloads_path.exists():
        return
    
    # Seleccionar una imagen aleatoria
    images_dir = downloads_path / "images"
    all_images = list(images_dir.glob("*.jpg"))
    if not all_images:
        return
    
    test_image = random.choice(all_images)
    print(f"📸 Imagen de prueba: {test_image.name}")
    
    model = YOLO(model_path)
    confidence_levels = [0.1, 0.25, 0.5, 0.75, 0.9]
    
    for conf in confidence_levels:
        results = model(str(test_image), conf=conf)
        detections = 0
        
        for r in results:
            if r.boxes is not None:
                detections = len(r.boxes)
        
        print(f"Confianza {conf}: {detections} detecciones")

def main():
    """Función principal"""
    
    print("🚀 PRUEBAS DEL MODELO CON IMÁGENES DE DOWNLOADS")
    print("=" * 60)
    
    # Establecer semilla para reproducibilidad
    random.seed(42)
    
    # Probar modelo principal
    results = test_model_with_downloads()
    
    if results:
        # Probar con diferentes confianzas
        test_with_different_confidence_levels()
        
        print(f"\n🎉 PRUEBAS COMPLETADAS")
        print("=" * 60)
        print(f"💡 CONCLUSIONES:")
        print(f"   - El modelo actual puede detectar campos en las imágenes")
        print(f"   - Revisa las imágenes guardadas para ver la calidad")
        print(f"   - Considera entrenar con más datos para mejorar precisión")
    else:
        print(f"\n❌ ERROR EN LAS PRUEBAS")
        print(f"💡 Verifica que el modelo y las imágenes existan")

if __name__ == "__main__":
    main()
