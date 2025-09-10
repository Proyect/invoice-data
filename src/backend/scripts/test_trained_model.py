#!/usr/bin/env python3
"""
Script para probar el modelo YOLO entrenado
"""

import sys
import os
sys.path.append('.')

from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

def test_trained_model():
    """Prueba el modelo entrenado con una imagen de ejemplo"""
    
    # Ruta al modelo entrenado
    model_path = "models/yolo_models/invoices_cpu_abs/weights/best.pt"
    
    # Ruta a la imagen de prueba
    test_image = "example_dataset/images/factura_ejemplo.jpg"
    
    print("🤖 PROBANDO MODELO YOLO ENTRENADO")
    print("=" * 50)
    
    # Verificar que el modelo existe
    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        return
    
    # Verificar que la imagen existe
    if not os.path.exists(test_image):
        print(f"❌ Imagen de prueba no encontrada: {test_image}")
        return
    
    try:
        # Cargar el modelo
        print(f"📦 Cargando modelo: {model_path}")
        model = YOLO(model_path)
        
        # Mostrar información del modelo
        print(f"✅ Modelo cargado exitosamente")
        print(f"📊 Clases detectadas: {len(model.names)}")
        for i, name in model.names.items():
            print(f"   {i}: {name}")
        
        # Realizar predicción
        print(f"\n🔍 Analizando imagen: {test_image}")
        results = model(test_image, conf=0.25)  # Confianza mínima 25%
        
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
        print(f"\n📋 RESULTADOS DE DETECCIÓN:")
        print(f"Total de detecciones: {len(detections)}")
        
        if detections:
            for i, det in enumerate(detections, 1):
                print(f"  {i}. {det['class']}: {det['confidence']:.2f} confianza")
                print(f"     Bbox: [{det['bbox'][0]:.0f}, {det['bbox'][1]:.0f}, {det['bbox'][2]:.0f}, {det['bbox'][3]:.0f}]")
        else:
            print("  ⚠️  No se detectaron campos")
            print("  💡 Prueba con conf=0.1 para detectar con menor confianza")
        
        # Guardar imagen con detecciones
        output_path = "models/yolo_models/invoices_cpu_abs/test_result.jpg"
        for r in results:
            r.save(output_path)
        print(f"\n💾 Imagen con detecciones guardada: {output_path}")
        
        return detections
        
    except Exception as e:
        print(f"❌ Error probando modelo: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_with_different_confidence():
    """Prueba el modelo con diferentes niveles de confianza"""
    
    model_path = "models/yolo_models/invoices_cpu_abs/weights/best.pt"
    test_image = "example_dataset/images/factura_ejemplo.jpg"
    
    if not os.path.exists(model_path) or not os.path.exists(test_image):
        return
    
    print(f"\n🎯 PROBANDO CON DIFERENTES NIVELES DE CONFIANZA")
    print("=" * 50)
    
    model = YOLO(model_path)
    confidence_levels = [0.1, 0.25, 0.5, 0.75]
    
    for conf in confidence_levels:
        results = model(test_image, conf=conf)
        detections = 0
        
        for r in results:
            if r.boxes is not None:
                detections = len(r.boxes)
        
        print(f"Confianza {conf}: {detections} detecciones")

if __name__ == "__main__":
    # Probar modelo principal
    detections = test_trained_model()
    
    # Probar con diferentes confianzas
    test_with_different_confidence()
    
    print(f"\n🎉 PRUEBA COMPLETADA")
    print("=" * 50)
