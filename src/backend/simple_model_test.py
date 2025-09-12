#!/usr/bin/env python3
"""
Prueba simple de todos los modelos YOLO
"""

import os
import glob
from ultralytics import YOLO

def test_all_models():
    print("🔍 PROBANDO TODOS LOS MODELOS YOLO")
    print("=" * 50)
    
    # Encontrar todos los modelos
    model_paths = glob.glob("models/yolo_models/*/weights/best.pt")
    
    print(f"📦 Encontrados {len(model_paths)} modelos")
    print()
    
    results = []
    
    for i, model_path in enumerate(model_paths, 1):
        model_name = model_path.split(os.sep)[-3]
        
        print(f"[{i:2d}/{len(model_paths)}] 🤖 {model_name}")
        
        try:
            # Información básica
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            
            # Cargar modelo
            model = YOLO(model_path)
            
            # Información del modelo
            num_classes = len(model.names)
            class_names = list(model.names.values())
            
            print(f"         📏 {size_mb:.1f}MB | 🏷️ {num_classes} clases")
            print(f"         📋 Clases: {', '.join(class_names)}")
            
            # Determinar tipo de modelo
            model_type = "DNI" if "dni" in model_name.lower() else "Invoice" if "invoice" in model_name.lower() else "Other"
            
            results.append({
                'name': model_name,
                'type': model_type,
                'size_mb': size_mb,
                'classes': num_classes,
                'class_names': class_names,
                'status': 'OK'
            })
            
            print(f"         ✅ Tipo: {model_type}")
            
        except Exception as e:
            print(f"         ❌ Error: {str(e)[:50]}")
            results.append({
                'name': model_name,
                'status': 'ERROR',
                'error': str(e)
            })
        
        print()
    
    # Resumen por categorías
    print("📊 RESUMEN POR CATEGORÍAS")
    print("=" * 50)
    
    dni_models = [r for r in results if r.get('type') == 'DNI' and r.get('status') == 'OK']
    invoice_models = [r for r in results if r.get('type') == 'Invoice' and r.get('status') == 'OK']
    other_models = [r for r in results if r.get('type') == 'Other' and r.get('status') == 'OK']
    error_models = [r for r in results if r.get('status') == 'ERROR']
    
    print(f"🆔 MODELOS DNI: {len(dni_models)}")
    for model in dni_models:
        print(f"   ✅ {model['name']} ({model['size_mb']:.1f}MB, {model['classes']} clases)")
    
    print(f"\n🧾 MODELOS INVOICE: {len(invoice_models)}")
    for model in invoice_models:
        print(f"   ✅ {model['name']} ({model['size_mb']:.1f}MB, {model['classes']} clases)")
    
    print(f"\n🔧 OTROS MODELOS: {len(other_models)}")
    for model in other_models:
        print(f"   ✅ {model['name']} ({model['size_mb']:.1f}MB, {model['classes']} clases)")
    
    if error_models:
        print(f"\n❌ MODELOS CON ERROR: {len(error_models)}")
        for model in error_models:
            print(f"   ❌ {model['name']}: {model.get('error', 'Unknown error')[:50]}")
    
    print(f"\n📈 ESTADÍSTICAS FINALES")
    print(f"   📦 Total modelos: {len(results)}")
    print(f"   ✅ Funcionando: {len([r for r in results if r.get('status') == 'OK'])}")
    print(f"   ❌ Con errores: {len(error_models)}")
    
    total_size = sum(r.get('size_mb', 0) for r in results if r.get('status') == 'OK')
    print(f"   💾 Tamaño total: {total_size:.1f}MB")
    
    return results

if __name__ == "__main__":
    results = test_all_models()
    print("\n🎉 PRUEBA COMPLETADA")
