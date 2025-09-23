#!/usr/bin/env python3
"""
Script rápido para entrenar con imágenes de ejemplo
- Usa las imágenes existentes en el proyecto
- Entrena con más épocas
- Hace predicciones de prueba
"""

import subprocess
import sys
from pathlib import Path


def main():
    print("🚀 Entrenamiento rápido con imágenes existentes...")
    
    # Usar el dataset actual pero con más épocas
    cmd = [
        "yolo_training_env/Scripts/yolo.exe", "detect", "train",
        "data=yolo/dataset.yaml",
        "model=models/yolo_models/yolov8n.pt",
        "epochs=15",
        "imgsz=640",
        "batch=1",
        "workers=0",
        "project=models/yolo_models",
        "name=quick_15ep"
    ]
    
    print("📊 Configuración:")
    print(f"   - Épocas: 15")
    print(f"   - Dataset: yolo/dataset.yaml")
    print(f"   - Modelo: yolov8n.pt")
    
    try:
        # Usar ultralytics directamente
        from ultralytics import YOLO
        
        # Cargar modelo
        model = YOLO("models/yolo_models/yolov8n.pt")
        
        # Entrenar
        results = model.train(
            data="example_dataset/dataset.yaml",
            epochs=15,
            imgsz=640,
            batch=16,
            device='auto',
            project='quick_training',
            name='quick_15ep',
            save=True,
            plots=True
        )
        
        print("✅ Entrenamiento completado!")
        
        # Hacer predicción de prueba
        print("\n🔮 Haciendo predicción de prueba...")
        test_results = model.predict(
            source="models/yolo_models/test_invoice.jpg",
            imgsz=640,
            save=True,
            project="models/yolo_models",
            name="pred_quick_15ep"
        )
        
        print("✅ Predicción completada!")
        
        print(f"\n🎉 ¡Entrenamiento y predicción completados!")
        print(f"📁 Resultados guardados en: models/yolo_models/pred_quick_15ep/")
        print(f"   - Modelo: models/yolo_models/quick_15ep/weights/best.pt")
        print(f"   - Predicción: models/yolo_models/pred_quick_15ep/")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
