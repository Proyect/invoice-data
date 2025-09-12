#!/usr/bin/env python3
'''
Script de limpieza del sistema
'''

import os
import shutil
from pathlib import Path

def cleanup_system():
    '''Limpia archivos temporales y cache'''
    
    print("🧹 LIMPIEZA DEL SISTEMA")
    print("=" * 30)
    
    # Limpiar cache de Python
    cache_dirs = [
        "__pycache__",
        "*.pyc",
        "*.pyo"
    ]
    
    for pattern in cache_dirs:
        for file_path in Path(".").rglob(pattern):
            if file_path.is_dir():
                shutil.rmtree(file_path)
                print(f"✅ Eliminado: {file_path}")
            else:
                file_path.unlink()
                print(f"✅ Eliminado: {file_path}")
    
    # Limpiar logs antiguos
    logs_dir = Path("logs")
    if logs_dir.exists():
        for log_file in logs_dir.glob("*.log"):
            if log_file.stat().st_size > 10 * 1024 * 1024:  # > 10MB
                log_file.unlink()
                print(f"✅ Log eliminado: {log_file}")
    
    print("🎉 Limpieza completada")

if __name__ == "__main__":
    cleanup_system()
