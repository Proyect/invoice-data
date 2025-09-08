#!/usr/bin/env python3
"""
Script para ejecutar la API localmente con configuración de desarrollo
"""
import os
import sys
import uvicorn

# Configurar variables de entorno para desarrollo local
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['REDIS_HOST'] = 'localhost'
os.environ['REDIS_PORT'] = '6379'
os.environ['REDIS_DB'] = '0'
os.environ['SECRET_KEY_JWT'] = 'your_super_secret_jwt_key_here_make_it_long_and_random_123456789'
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'
os.environ['LOCAL_STORAGE_PATH'] = './uploaded_documents_local'
os.environ['YOLO_MODELS_PATH'] = './models/yolo_models'

# Agregar el directorio actual al path
sys.path.append('.')

if __name__ == "__main__":
    print("🚀 Iniciando API en modo desarrollo local...")
    print("📊 Base de datos: SQLite (test.db)")
    print("🌐 URL: http://localhost:8000")
    print("📚 Documentación: http://localhost:8000/docs")
    print("🛑 Presiona Ctrl+C para detener")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


