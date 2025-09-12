#!/usr/bin/env python3
'''
Script para probar el modelo YOLO de DNI
'''

import os
import sys
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np

def test_dni_model():
    '''Prueba el modelo de DNI con imágenes de ejemplo'''
    
    print("🆔 PROBANDO MODELO DE DNI")
    print("=" * 50)
    
    # Rutas
    model_path = "models/yolo_models/dni_robust/weights/best.pt"
    test_images_dir = Path("datasets/dni_robust/raw_images")
    
    # Verificar que el modelo existe
    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        print("💡 Entrena primero el modelo con: python scripts/train_dni_model.py")
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
        
        # Buscar imágenes de prueba
        if test_images_dir.exists():
            test_images = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))
        else:
            # Usar imagen de ejemplo
            test_images = [Path("example_dataset/images/factura_ejemplo.jpg")]
        
        if not test_images:
            print("❌ No se encontraron imágenes de prueba")
            return
        
        print(f"\n🔍 PROBANDO CON {len(test_images)} IMÁGENES")
        print("=" * 50)
        
        for i, img_path in enumerate(test_images, 1):
            print(f"\n📸 Imagen {i}: {img_path.name}")
            
            # Realizar predicción
            results = model(str(img_path), conf=0.25)
            
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
            output_path = f"models/yolo_models/dni_robust/test_dni_{i}.jpg"
            for r in results:
                r.save(output_path)
            print(f"   💾 Resultado guardado: {output_path}")
        
        print(f"\n🎉 PRUEBAS COMPLETADAS")
        
    except Exception as e:
        print(f"❌ Error probando modelo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dni_model()
