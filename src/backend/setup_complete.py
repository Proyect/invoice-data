#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuración completa para el backend FastAPI OCR
Automatiza la instalación y configuración inicial del proyecto
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Configurar encoding para Windows
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def print_step(step_num, description):
    """Imprime un paso del proceso de setup"""
    print(f"\n{'='*60}")
    print(f"PASO {step_num}: {description}")
    print(f"{'='*60}")

def run_command(command, description="", check=True):
    """Ejecuta un comando del sistema"""
    print(f"Ejecutando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"[OK] {description}")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error en: {description}")
        print(f"Error: {e.stderr}")
        return False

def create_directory(path, description=""):
    """Crea un directorio si no existe"""
    try:
        os.makedirs(path, exist_ok=True)
        print(f"[OK] Directorio creado: {path} - {description}")
        return True
    except Exception as e:
        print(f"[ERROR] Error creando directorio {path}: {e}")
        return False

def copy_file(source, destination, description=""):
    """Copia un archivo"""
    try:
        shutil.copy2(source, destination)
        print(f"[OK] Archivo copiado: {source} -> {destination} - {description}")
        return True
    except Exception as e:
        print(f"[ERROR] Error copiando archivo: {e}")
        return False

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"[ERROR] Python 3.8+ requerido. Version actual: {version.major}.{version.minor}")
        return False
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def setup_virtual_environment():
    """Configura el entorno virtual"""
    print_step(1, "CONFIGURACIÓN DEL ENTORNO VIRTUAL")
    
    if not check_python_version():
        return False
    
    # Crear entorno virtual si no existe
    if not os.path.exists('.venv'):
        if not run_command('python -m venv .venv', "Creando entorno virtual"):
            return False
    else:
        print("[OK] Entorno virtual ya existe")
    
    # Activar entorno virtual y actualizar pip
    activate_cmd = '.venv\\Scripts\\activate' if os.name == 'nt' else 'source .venv/bin/activate'
    pip_cmd = '.venv\\Scripts\\pip' if os.name == 'nt' else '.venv/bin/pip'
    
    run_command(f'{pip_cmd} install --upgrade pip', "Actualizando pip")
    
    return True

def install_dependencies():
    """Instala las dependencias del proyecto"""
    print_step(2, "INSTALACIÓN DE DEPENDENCIAS")
    
    pip_cmd = '.venv\\Scripts\\pip' if os.name == 'nt' else '.venv/bin/pip'
    
    if os.path.exists('requirements.txt'):
        return run_command(f'{pip_cmd} install -r requirements.txt', "Instalando dependencias de requirements.txt")
    else:
        print("[ERROR] requirements.txt no encontrado")
        return False

def setup_directories():
    """Crea los directorios necesarios"""
    print_step(3, "CREACIÓN DE DIRECTORIOS")
    
    directories = [
        ('uploaded_documents_local', 'Almacenamiento local de documentos'),
        ('models/yolo_models', 'Modelos YOLO entrenados'),
        ('logs', 'Archivos de log'),
        ('temp', 'Archivos temporales')
    ]
    
    success = True
    for directory, description in directories:
        if not create_directory(directory, description):
            success = False
    
    return success

def setup_environment_file():
    """Configura el archivo de entorno"""
    print_step(4, "CONFIGURACIÓN DE VARIABLES DE ENTORNO")
    
    if os.path.exists('.env.local') and not os.path.exists('.env'):
        return copy_file('.env.local', '.env', "Archivo de configuración de desarrollo")
    elif os.path.exists('.env'):
        print("[OK] Archivo .env ya existe")
        return True
    else:
        print("[ERROR] No se encontro .env.local para copiar")
        return False

def check_external_dependencies():
    """Verifica dependencias externas"""
    print_step(5, "VERIFICACIÓN DE DEPENDENCIAS EXTERNAS")
    
    dependencies = [
        ('tesseract', 'tesseract --version', 'Tesseract OCR'),
        ('redis', 'redis-cli --version', 'Redis (opcional para desarrollo)')
    ]
    
    results = {}
    for name, command, description in dependencies:
        print(f"\nVerificando {description}...")
        if run_command(command, f"{description} instalado", check=False):
            results[name] = True
        else:
            results[name] = False
            print(f"⚠️  {description} no encontrado - instalar manualmente si es necesario")
    
    return results

def setup_database():
    """Configura la base de datos"""
    print_step(6, "CONFIGURACIÓN DE BASE DE DATOS")
    
    python_cmd = '.venv\\Scripts\\python' if os.name == 'nt' else '.venv/bin/python'
    
    # Crear tablas de la base de datos
    setup_script = '''
import sys
sys.path.append('.')
from database import create_db_and_tables
try:
    create_db_and_tables()
    print("[OK] Tablas de base de datos creadas exitosamente")
except Exception as e:
    print(f"[ERROR] Error creando tablas: {e}")
'''
    
    with open('temp_db_setup.py', 'w') as f:
        f.write(setup_script)
    
    result = run_command(f'{python_cmd} temp_db_setup.py', "Creando tablas de base de datos")
    
    # Limpiar archivo temporal
    if os.path.exists('temp_db_setup.py'):
        os.remove('temp_db_setup.py')
    
    return result

def create_startup_scripts():
    """Crea scripts de inicio"""
    print_step(7, "CREACIÓN DE SCRIPTS DE INICIO")
    
    # Script para Windows
    windows_script = '''@echo off
echo Iniciando backend FastAPI OCR...
call .venv\\Scripts\\activate
python run_local.py
pause
'''
    
    # Script para Linux/Mac
    unix_script = '''#!/bin/bash
echo "Iniciando backend FastAPI OCR..."
source .venv/bin/activate
python run_local.py
'''
    
    try:
        with open('start_server.bat', 'w') as f:
            f.write(windows_script)
        print("[OK] Script de inicio para Windows creado: start_server.bat")
        
        with open('start_server.sh', 'w') as f:
            f.write(unix_script)
        os.chmod('start_server.sh', 0o755)
        print("[OK] Script de inicio para Unix creado: start_server.sh")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error creando scripts de inicio: {e}")
        return False

def print_final_instructions(external_deps):
    """Imprime las instrucciones finales"""
    print_step(8, "CONFIGURACIÓN COMPLETADA")
    
    print("\n🎉 ¡Configuración completada exitosamente!")
    print("\n📋 PRÓXIMOS PASOS:")
    
    print("\n1. DEPENDENCIAS EXTERNAS:")
    if not external_deps.get('tesseract', False):
        print("   [PENDIENTE] Instalar Tesseract OCR:")
        print("      - Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("      - Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-spa")
        print("      - macOS: brew install tesseract tesseract-lang")
    else:
        print("   [OK] Tesseract OCR instalado")
    
    if not external_deps.get('redis', False):
        print("   [OPCIONAL] Redis (opcional para desarrollo):")
        print("      - Windows: https://redis.io/docs/getting-started/installation/install-redis-on-windows/")
        print("      - Ubuntu: sudo apt-get install redis-server")
        print("      - macOS: brew install redis")
    else:
        print("   [OK] Redis instalado")
    
    print("\n2. MODELOS YOLO:")
    print("   [INFO] Colocar modelos entrenados en: models/yolo_models/")
    print("      - dni_yolov8.pt (para DNI)")
    print("      - invoice_yolov8.pt (para facturas)")
    
    print("\n3. INICIAR SERVIDOR:")
    if os.name == 'nt':
        print("   🚀 Windows: Ejecutar start_server.bat")
    else:
        print("   🚀 Unix: Ejecutar ./start_server.sh")
    print("   🌐 O manualmente: python run_local.py")
    
    print("\n4. ACCEDER A LA API:")
    print("   🌐 API: http://localhost:8000")
    print("   📚 Documentación: http://localhost:8000/docs")
    print("   🔍 Redoc: http://localhost:8000/redoc")
    
    print("\n5. TESTING:")
    print("   🧪 Usuario de prueba:")
    print("      - Username: testuser")
    print("      - Password: testpassword")
    
    print(f"\n{'='*60}")
    print("¡El backend FastAPI OCR está listo para usar!")
    print(f"{'='*60}")

def main():
    """Función principal del setup"""
    print("🚀 CONFIGURACIÓN AUTOMÁTICA DEL BACKEND FASTAPI OCR")
    print("Este script configurará automáticamente el entorno de desarrollo")
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    steps = [
        setup_virtual_environment,
        install_dependencies,
        setup_directories,
        setup_environment_file,
        setup_database,
        create_startup_scripts
    ]
    
    # Ejecutar pasos de configuración
    for step in steps:
        if not step():
            print(f"\n[ERROR] Error en el paso: {step.__name__}")
            print("Configuración interrumpida. Revisa los errores anteriores.")
            return False
    
    # Verificar dependencias externas
    external_deps = check_external_dependencies()
    
    # Mostrar instrucciones finales
    print_final_instructions(external_deps)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Configuracion cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        sys.exit(1)
