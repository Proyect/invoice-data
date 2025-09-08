#!/usr/bin/env python3
"""
Script de configuración para desarrollo local
Crea directorios necesarios y descarga modelos YOLO básicos
"""
import os
import requests
from pathlib import Path

def create_directories():
    """Crear directorios necesarios para el proyecto"""
    directories = [
        "models/yolo_models",
        "uploaded_documents_local",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio creado: {directory}")

def download_yolo_model():
    """Descargar modelo YOLO básico para pruebas"""
    model_path = Path("models/yolo_models/yolov8n.pt")
    
    if model_path.exists():
        print(f"✅ Modelo ya existe: {model_path}")
        return
    
    print("📥 Descargando modelo YOLOv8n...")
    try:
        # YOLOv8n se descarga automáticamente al importar ultralytics
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')  # Esto descarga automáticamente
        
        # Mover el modelo al directorio correcto
        import shutil
        if Path("yolov8n.pt").exists():
            shutil.move("yolov8n.pt", model_path)
            print(f"✅ Modelo descargado: {model_path}")
        else:
            print("⚠️ No se pudo descargar el modelo automáticamente")
            
    except Exception as e:
        print(f"❌ Error descargando modelo: {e}")

def create_test_env():
    """Crear archivo .env para pruebas si no existe"""
    env_path = Path(".env")
    env_local_path = Path(".env.local")
    
    if not env_path.exists() and env_local_path.exists():
        import shutil
        shutil.copy(env_local_path, env_path)
        print("✅ Archivo .env creado desde .env.local")

def main():
    print("🚀 Configurando entorno de desarrollo local...")
    print("-" * 50)
    
    create_directories()
    download_yolo_model()
    create_test_env()
    
    print("-" * 50)
    print("✅ Configuración completada!")
    print("\n📋 Próximos pasos:")
    print("1. Instalar Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    print("2. Instalar Redis (opcional): https://redis.io/download")
    print("3. Ejecutar: python run_local.py")

if __name__ == "__main__":
    main()
