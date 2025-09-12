#!/usr/bin/env python3
"""
Análisis completo de los modelos entrenados
"""

import os
from ultralytics import YOLO
import glob

def analyze_trained_models():
    """Analiza todos los modelos entrenados disponibles"""
    
    print("🔍 ANÁLISIS DE MODELOS ENTRENADOS")
    print("=" * 60)
    
    # Buscar todos los modelos best.pt
    model_paths = glob.glob("models/yolo_models/*/weights/best.pt")
    
    if not model_paths:
        print("❌ No se encontraron modelos entrenados")
        return
    
    print(f"📊 Encontrados {len(model_paths)} modelos entrenados:")
    print()
    
    for model_path in model_paths:
        model_name = model_path.split('/')[-3]  # Extraer nombre del directorio
        
        try:
            # Obtener tamaño del archivo
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            
            # Cargar modelo para obtener información
            model = YOLO(model_path)
            
            print(f"🤖 MODELO: {model_name}")
            print(f"   📁 Ruta: {model_path}")
            print(f"   📏 Tamaño: {size_mb:.1f} MB")
            print(f"   🏷️  Clases: {len(model.names)} clases detectables")
            
            # Mostrar clases
            for i, class_name in model.names.items():
                print(f"      {i}: {class_name}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error analizando {model_name}: {e}")
            print()

def test_dni_model():
    """Prueba específica del modelo DNI"""
    
    print("🆔 PRUEBA DEL MODELO DNI")
    print("=" * 40)
    
    # Buscar modelo DNI más reciente
    dni_models = glob.glob("models/yolo_models/dni*/weights/best.pt")
    
    if not dni_models:
        print("❌ No se encontró modelo DNI")
        return
    
    # Usar el modelo más reciente
    model_path = max(dni_models, key=os.path.getmtime)
    model_name = model_path.split('/')[-3]
    
    print(f"📦 Usando modelo: {model_name}")
    
    # Buscar imagen de prueba DNI
    test_images = glob.glob("datasets/dni_robust/images/test/*.jpg")
    
    if not test_images:
        print("❌ No se encontraron imágenes de prueba DNI")
        return
    
    test_image = test_images[0]
    print(f"🖼️  Imagen de prueba: {os.path.basename(test_image)}")
    
    try:
        model = YOLO(model_path)
        results = model(test_image, conf=0.25)
        
        detections = 0
        for r in results:
            if r.boxes is not None:
                detections = len(r.boxes)
                
                print(f"✅ Detecciones encontradas: {detections}")
                
                for i, box in enumerate(r.boxes):
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    class_name = model.names[cls]
                    print(f"   {i+1}. {class_name}: {conf:.2f} confianza")
        
        if detections == 0:
            print("⚠️  No se detectaron campos (prueba con confianza más baja)")
            
    except Exception as e:
        print(f"❌ Error probando modelo DNI: {e}")

def test_invoice_model():
    """Prueba específica del modelo de facturas"""
    
    print("🧾 PRUEBA DEL MODELO DE FACTURAS")
    print("=" * 40)
    
    # Buscar modelo de facturas
    invoice_models = glob.glob("models/yolo_models/*invoice*/weights/best.pt")
    
    if not invoice_models:
        print("❌ No se encontró modelo de facturas")
        return
    
    # Usar el modelo más reciente
    model_path = max(invoice_models, key=os.path.getmtime)
    model_name = model_path.split('/')[-3]
    
    print(f"📦 Usando modelo: {model_name}")
    
    # Buscar imagen de prueba de factura
    test_images = glob.glob("datasets/invoices_argentina/images/train/*.jpg")
    
    if not test_images:
        print("❌ No se encontraron imágenes de prueba de facturas")
        return
    
    test_image = test_images[0]
    print(f"🖼️  Imagen de prueba: {os.path.basename(test_image)}")
    
    try:
        model = YOLO(model_path)
        results = model(test_image, conf=0.25)
        
        detections = 0
        for r in results:
            if r.boxes is not None:
                detections = len(r.boxes)
                
                print(f"✅ Detecciones encontradas: {detections}")
                
                for i, box in enumerate(r.boxes):
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    class_name = model.names[cls]
                    print(f"   {i+1}. {class_name}: {conf:.2f} confianza")
        
        if detections == 0:
            print("⚠️  No se detectaron campos (prueba con confianza más baja)")
            
    except Exception as e:
        print(f"❌ Error probando modelo de facturas: {e}")

if __name__ == "__main__":
    analyze_trained_models()
    print()
    test_dni_model()
    print()
    test_invoice_model()
    print()
    print("🎉 ANÁLISIS COMPLETADO")
