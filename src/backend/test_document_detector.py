#!/usr/bin/env python3
"""
Script para probar el modelo detector de documentos
"""
import os
from ultralytics import YOLO

def test_document_detector():
    print("📄 PROBANDO MODELO DETECTOR DE DOCUMENTOS")
    print("=" * 50)
    
    # Cargar modelo
    model_path = "models/yolo_models/document_detector/weights/best.pt"
    if not os.path.exists(model_path):
        print(f"❌ Modelo no encontrado: {model_path}")
        return
    
    print(f"📦 Cargando modelo: {model_path}")
    model = YOLO(model_path)
    print("✅ Modelo cargado exitosamente")
    
    # Mostrar clases
    print(f"📊 Clases detectadas: {len(model.names)}")
    for i, name in model.names.items():
        print(f"   {i}: {name}")
    
    # Buscar imagen de prueba
    test_images = [
        "example_dataset/images/factura_ejemplo.jpg",
        "example_dataset/images/dni_ejemplo.jpg"
    ]
    
    test_image = None
    for img_path in test_images:
        if os.path.isfile(img_path):
            test_image = img_path
            break
    
    if not test_image:
        print("❌ No se encontró imagen de prueba")
        return
    
    print(f"\n🔍 Analizando imagen: {test_image}")
    
    # Realizar predicción
    results = model(test_image, conf=0.25)
    
    # Mostrar resultados
    print(f"\n📋 RESULTADOS DE DETECCIÓN:")
    total_detections = 0
    
    for result in results:
        if result.boxes is not None:
            detections = len(result.boxes)
            total_detections += detections
            print(f"   Total de detecciones: {detections}")
            
            if detections > 0:
                for i, box in enumerate(result.boxes):
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = model.names[cls]
                    print(f"   {i+1}. {class_name}: {conf:.3f}")
            else:
                print("   ⚠️  No se detectaron documentos")
        
        # Guardar imagen con detecciones
        output_path = "models/yolo_models/document_detector/test_result.jpg"
        result.save(output_path)
        print(f"\n💾 Imagen con detecciones guardada: {output_path}")
    
    print(f"\n🎉 PRUEBA COMPLETADA - Total detecciones: {total_detections}")

if __name__ == "__main__":
    test_document_detector()
