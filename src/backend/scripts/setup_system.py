#!/usr/bin/env python3
"""
Script de setup rápido del sistema OCR
Configura y verifica todos los componentes necesarios
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_directories():
    """Crear directorios necesarios"""
    print("📁 Configurando directorios...")
    
    directories = [
        "models/yolo_models",
        "uploaded_documents_local",
        "logs",
        "datasets/invoices",
        "datasets/dni"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")

def setup_environment():
    """Configurar variables de entorno"""
    print("\n🌍 Configurando entorno...")
    
    env_vars = {
        'YOLO_CONFIG_DIR': '/tmp/yolo_config',
        'PYTHONPATH': '/app'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"   ✅ {key}={value}")

def check_dependencies():
    """Verificar dependencias críticas"""
    print("\n📦 Verificando dependencias...")
    
    critical_packages = [
        'ultralytics',
        'torch',
        'opencv-python',
        'fastapi',
        'sqlalchemy'
    ]
    
    for package in critical_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Instalar con: pip install {package}")

def setup_yolo_config():
    """Configurar directorio de YOLO"""
    print("\n🤖 Configurando YOLO...")
    
    yolo_dir = Path('/tmp/yolo_config')
    yolo_dir.mkdir(exist_ok=True)
    
    # Crear archivo de configuración básico
    config_content = """# YOLO Configuration
model: yolov8n.pt
epochs: 100
batch: 16
imgsz: 640
device: auto
"""
    
    config_file = yolo_dir / 'config.yaml'
    config_file.write_text(config_content)
    
    print(f"   ✅ Configuración YOLO creada en {config_file}")

def create_example_dataset():
    """Crear dataset de ejemplo si no existe"""
    print("\n📊 Creando dataset de ejemplo...")
    
    dataset_dir = Path('example_dataset')
    if not dataset_dir.exists():
        # Ejecutar script de ejemplo
        try:
            subprocess.run([sys.executable, 'scripts/simple_example.py'], 
                         check=True, capture_output=True)
            print("   ✅ Dataset de ejemplo creado")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Error creando dataset: {e}")
    else:
        print("   ✅ Dataset de ejemplo ya existe")

def main():
    """Función principal de setup"""
    print("🚀 SETUP RÁPIDO DEL SISTEMA OCR")
    print("=" * 40)
    
    try:
        setup_directories()
        setup_environment()
        check_dependencies()
        setup_yolo_config()
        create_example_dataset()
        
        print("\n" + "=" * 40)
        print("✅ SETUP COMPLETADO EXITOSAMENTE")
        print("\n📋 Próximos pasos:")
        print("1. Ejecutar: python scripts/quick_validation.py")
        print("2. Probar: python scripts/quick_train_example.py")
        print("3. Iniciar API: uvicorn main:app --reload")
        
    except Exception as e:
        print(f"\n❌ Error durante setup: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

