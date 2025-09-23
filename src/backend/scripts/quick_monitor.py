#!/usr/bin/env python3
"""
Script de monitoreo rápido del sistema OCR
Muestra estado de servicios y recursos
"""

import psutil
import requests
import time
from datetime import datetime

def check_system_resources():
    """Verificar recursos del sistema"""
    print("💻 Recursos del Sistema:")
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"   CPU: {cpu_percent}%")
    
    # Memoria
    memory = psutil.virtual_memory()
    print(f"   RAM: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
    
    # Disco
    disk = psutil.disk_usage('/')
    print(f"   Disco: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")

def check_services():
    """Verificar servicios"""
    print("\n🌐 Servicios:")
    
    services = [
        ("Frontend", "http://localhost:3000"),
        ("Backend API", "http://localhost:8000"),
        ("API Docs", "http://localhost:8000/docs")
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ UP" if response.status_code == 200 else f"⚠️ {response.status_code}"
            print(f"   {name}: {status}")
        except requests.exceptions.RequestException:
            print(f"   {name}: ❌ DOWN")

def check_docker_containers():
    """Verificar contenedores Docker"""
    print("\n🐳 Contenedores Docker:")
    
    try:
        import subprocess
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        name = parts[0]
                        status = parts[1]
                        status_icon = "✅" if "Up" in status else "❌"
                        print(f"   {status_icon} {name}: {status}")
        else:
            print("   ❌ Error ejecutando docker ps")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_yolo_models():
    """Verificar modelos YOLO"""
    print("\n🤖 Modelos YOLO:")
    
    import os
    model_paths = [
        "models/yolo_models/yolov8n.pt",
        "models/yolo_models/test_invoice.jpg"
    ]
    
    for path in model_paths:
        if os.path.exists(path):
            size = os.path.getsize(path) / (1024*1024)
            print(f"   ✅ {path} ({size:.1f} MB)")
        else:
            print(f"   ❌ {path}")

def main():
    """Función principal de monitoreo"""
    print("📊 MONITOREO RÁPIDO DEL SISTEMA OCR")
    print("=" * 50)
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        check_system_resources()
        check_services()
        check_docker_containers()
        check_yolo_models()
        
        print("\n" + "=" * 50)
        print("✅ Monitoreo completado")
        
    except Exception as e:
        print(f"\n❌ Error durante monitoreo: {e}")

if __name__ == "__main__":
    main()

