#!/usr/bin/env python3
"""
Script para verificar modelos YOLO entrenados disponibles
"""
import os

def check_models():
    models_dir = "models/yolo_models"
    print("🔍 VERIFICANDO MODELOS YOLO ENTRENADOS")
    print("=" * 50)
    
    if not os.path.exists(models_dir):
        print("❌ Directorio de modelos no encontrado")
        return
    
    models = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
    
    trained_models = []
    untrained_models = []
    
    for model in sorted(models):
        weights_path = os.path.join(models_dir, model, "weights", "best.pt")
        if os.path.exists(weights_path):
            trained_models.append(model)
            print(f"✅ {model}")
        else:
            untrained_models.append(model)
            print(f"❌ {model}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESUMEN:")
    print(f"   Modelos entrenados: {len(trained_models)}")
    print(f"   Modelos sin entrenar: {len(untrained_models)}")
    
    if trained_models:
        print(f"\n🎯 MODELOS LISTOS PARA USAR:")
        for model in trained_models:
            print(f"   - {model}")
    
    if untrained_models:
        print(f"\n⚠️  MODELOS QUE NECESITAN ENTRENAMIENTO:")
        for model in untrained_models:
            print(f"   - {model}")

if __name__ == "__main__":
    check_models()
