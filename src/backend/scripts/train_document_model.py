#!/usr/bin/env python3
"""
Script para entrenar modelo YOLO específico para documentos
Entrena un modelo personalizado para detectar campos de facturas y DNIs
"""

import os
import sys
from pathlib import Path

def train_invoice_model():
    """Entrenar modelo específico para facturas"""
    print("🚀 ENTRENANDO MODELO ESPECÍFICO PARA DOCUMENTOS")
    print("=" * 60)
    
    try:
        from ultralytics import YOLO
        
        # Configuración del entrenamiento
        config = {
            'data': 'example_dataset/dataset.yaml',
            'epochs': 10,  # Menos épocas para CPU
            'imgsz': 640,
            'batch': 8,    # Batch size más pequeño para estabilidad
            'device': 'cpu',  # Forzar CPU ya que CUDA no está disponible
            'project': 'models/yolo_models',
            'name': 'document_detector',
            'save': True,
            'plots': True,
            'verbose': True,
            'patience': 10,  # Early stopping
            'save_period': 10,  # Guardar cada 10 épocas
            'cache': True,   # Cachear imágenes para velocidad
            'workers': 4,    # Número de workers
            'optimizer': 'AdamW',
            'lr0': 0.01,
            'weight_decay': 0.0005,
            'momentum': 0.937,
            'warmup_epochs': 3,
            'warmup_momentum': 0.8,
            'warmup_bias_lr': 0.1,
            'box': 7.5,
            'cls': 0.5,
            'dfl': 1.5,
            'hsv_h': 0.015,
            'hsv_s': 0.7,
            'hsv_v': 0.4,
            'degrees': 0.0,
            'translate': 0.1,
            'scale': 0.5,
            'shear': 0.0,
            'perspective': 0.0,
            'flipud': 0.0,
            'fliplr': 0.5,
            'mosaic': 1.0,
            'mixup': 0.0,
            'copy_paste': 0.0
        }
        
        print("📊 Configuración de entrenamiento:")
        for key, value in config.items():
            print(f"   {key}: {value}")
        
        # Cargar modelo base
        print("\n🤖 Cargando modelo base YOLOv8n...")
        model = YOLO('models/yolo_models/yolov8n.pt')
        
        # Verificar dataset
        dataset_path = config['data']
        if not os.path.exists(dataset_path):
            print(f"❌ Dataset no encontrado: {dataset_path}")
            return False
            
        print(f"✅ Dataset encontrado: {dataset_path}")
        
        # Iniciar entrenamiento
        print("\n🏃 Iniciando entrenamiento...")
        print("⏱️ Esto puede tomar varios minutos...")
        
        results = model.train(**config)
        
        print("\n✅ ENTRENAMIENTO COMPLETADO!")
        print(f"📁 Modelo guardado en: {results.save_dir}")
        print(f"🎯 Mejor modelo: {results.save_dir}/weights/best.pt")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante entrenamiento: {e}")
        return False

def test_trained_model():
    """Probar el modelo entrenado"""
    print("\n🔮 PROBANDO MODELO ENTRENADO")
    print("=" * 40)
    
    try:
        from ultralytics import YOLO
        
        # Cargar modelo entrenado
        model_path = 'models/yolo_models/document_detector/weights/best.pt'
        
        if not os.path.exists(model_path):
            print(f"❌ Modelo entrenado no encontrado: {model_path}")
            return False
            
        print(f"📁 Cargando modelo: {model_path}")
        model = YOLO(model_path)
        
        # Probar con imagen de test
        test_image = 'models/yolo_models/test_invoice.jpg'
        
        if not os.path.exists(test_image):
            print(f"❌ Imagen de test no encontrada: {test_image}")
            return False
            
        print(f"🖼️ Probando con imagen: {test_image}")
        
        # Hacer predicción
        results = model.predict(
            source=test_image,
            imgsz=640,
            conf=0.25,  # Umbral de confianza
            save=True,
            project='models/yolo_models',
            name='test_document_detector',
            show_labels=True,
            show_conf=True
        )
        
        # Analizar resultados
        if results and len(results) > 0:
            detections = len(results[0].boxes) if results[0].boxes is not None else 0
            print(f"✅ Predicción exitosa: {detections} campos detectados")
            
            if detections > 0:
                print("🎯 Campos detectados:")
                for i, box in enumerate(results[0].boxes):
                    conf = box.conf.item()
                    cls = int(box.cls.item())
                    class_name = model.names[cls]
                    print(f"   {i+1}. {class_name}: {conf:.2f}")
                    
                print(f"📁 Resultado guardado en: models/yolo_models/test_document_detector/")
            else:
                print("⚠️ No se detectaron campos de documento")
                
        return True
        
    except Exception as e:
        print(f"❌ Error probando modelo: {e}")
        return False

def compare_models():
    """Comparar modelo preentrenado vs entrenado"""
    print("\n📊 COMPARACIÓN DE MODELOS")
    print("=" * 40)
    
    try:
        from ultralytics import YOLO
        
        test_image = 'models/yolo_models/test_invoice.jpg'
        
        # Modelo preentrenado
        print("🔍 Probando modelo preentrenado...")
        pretrained_model = YOLO('models/yolo_models/yolov8n.pt')
        pretrained_results = pretrained_model.predict(
            source=test_image,
            imgsz=640,
            conf=0.25,
            save=False
        )
        
        pretrained_detections = len(pretrained_results[0].boxes) if pretrained_results[0].boxes is not None else 0
        print(f"   📊 Detecciones: {pretrained_detections}")
        
        if pretrained_detections > 0:
            print("   🎯 Objetos detectados:")
            for box in pretrained_results[0].boxes:
                cls = int(box.cls.item())
                class_name = pretrained_model.names[cls]
                conf = box.conf.item()
                print(f"      - {class_name}: {conf:.2f}")
        
        # Modelo entrenado (si existe)
        trained_model_path = 'models/yolo_models/document_detector/weights/best.pt'
        if os.path.exists(trained_model_path):
            print("\n🔍 Probando modelo entrenado...")
            trained_model = YOLO(trained_model_path)
            trained_results = trained_model.predict(
                source=test_image,
                imgsz=640,
                conf=0.25,
                save=False
            )
            
            trained_detections = len(trained_results[0].boxes) if trained_results[0].boxes is not None else 0
            print(f"   📊 Detecciones: {trained_detections}")
            
            if trained_detections > 0:
                print("   🎯 Campos detectados:")
                for box in trained_results[0].boxes:
                    cls = int(box.cls.item())
                    class_name = trained_model.names[cls]
                    conf = box.conf.item()
                    print(f"      - {class_name}: {conf:.2f}")
        else:
            print("\n⚠️ Modelo entrenado no encontrado")
            
        return True
        
    except Exception as e:
        print(f"❌ Error comparando modelos: {e}")
        return False

def main():
    """Función principal"""
    print("🎯 ENTRENAMIENTO DE MODELO ESPECÍFICO PARA DOCUMENTOS")
    print("=" * 70)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('models/yolo_models/yolov8n.pt'):
        print("❌ Modelo base no encontrado. Asegúrate de estar en el directorio correcto.")
        return 1
    
    # Entrenar modelo
    if not train_invoice_model():
        print("❌ Error en el entrenamiento")
        return 1
    
    # Probar modelo entrenado
    if not test_trained_model():
        print("⚠️ Error probando modelo entrenado")
    
    # Comparar modelos
    compare_models()
    
    print("\n🎉 PROCESO COMPLETADO!")
    print("📋 Próximos pasos:")
    print("1. Revisar resultados en models/yolo_models/document_detector/")
    print("2. Usar el modelo entrenado para detección específica")
    print("3. Ajustar parámetros si es necesario")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
