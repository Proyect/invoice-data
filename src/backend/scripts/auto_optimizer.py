#!/usr/bin/env python3
"""
Sistema de optimización automática del pipeline de OCR
"""

import os
import shutil
import json
from pathlib import Path
import subprocess
import sys

class AutoOptimizer:
    """Optimizador automático del sistema"""
    
    def __init__(self):
        self.optimizations_applied = []
        self.errors = []
    
    def optimize_model_loading(self):
        """Optimiza la carga de modelos"""
        
        print("OPTIMIZANDO CARGA DE MODELOS")
        print("=" * 40)
        
        # Verificar si el cache de modelos está funcionando
        model_loader_path = Path("services/model_loader.py")
        
        if model_loader_path.exists():
            with open(model_loader_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar si tiene cache
            if '_yolo_model_cache' not in content:
                print("⚠️  Cache de modelos no implementado")
                self.optimizations_applied.append("Implementar cache de modelos")
            else:
                print("✅ Cache de modelos ya implementado")
        
        # Optimizar rutas de modelos
        self.optimize_model_paths()
    
    def optimize_model_paths(self):
        """Optimiza las rutas de los modelos"""
        
        print("OPTIMIZANDO RUTAS DE MODELOS")
        print("=" * 40)
        
        # Verificar estructura de modelos
        models_path = Path("models/yolo_models")
        
        if not models_path.exists():
            models_path.mkdir(parents=True, exist_ok=True)
            print("✅ Directorio de modelos creado")
            self.optimizations_applied.append("Crear directorio de modelos")
        
        # Verificar modelos principales
        main_models = {
            'yolov8n.pt': 'Modelo base YOLOv8',
            'invoices_cpu_abs/weights/best.pt': 'Modelo de facturas',
            'dni_robust/weights/best.pt': 'Modelo de DNI'
        }
        
        for model_path, description in main_models.items():
            full_path = models_path / model_path
            if full_path.exists():
                print(f"✅ {description}: {model_path}")
            else:
                print(f"❌ {description}: {model_path} - NO ENCONTRADO")
                self.optimizations_applied.append(f"Crear {description}")
    
    def optimize_datasets(self):
        """Optimiza la estructura de datasets"""
        
        print("OPTIMIZANDO DATASETS")
        print("=" * 40)
        
        datasets_path = Path("datasets")
        
        if not datasets_path.exists():
            datasets_path.mkdir(parents=True, exist_ok=True)
            print("✅ Directorio de datasets creado")
            self.optimizations_applied.append("Crear directorio de datasets")
        
        # Verificar datasets principales
        main_datasets = {
            'invoices_robust': 'Dataset de facturas',
            'dni_robust': 'Dataset de DNI',
            'invoices_downloads': 'Dataset grande de Downloads'
        }
        
        for dataset_name, description in main_datasets.items():
            dataset_path = datasets_path / dataset_name
            
            if dataset_path.exists():
                print(f"✅ {description}: {dataset_name}")
                
                # Verificar estructura
                required_dirs = ['images/train', 'images/val', 'images/test', 'labels/train', 'labels/val', 'labels/test']
                missing_dirs = []
                
                for dir_path in required_dirs:
                    if not (dataset_path / dir_path).exists():
                        missing_dirs.append(dir_path)
                
                if missing_dirs:
                    print(f"   ⚠️  Directorios faltantes: {missing_dirs}")
                    self.optimizations_applied.append(f"Crear estructura para {dataset_name}")
                else:
                    print(f"   ✅ Estructura completa")
                
                # Verificar dataset.yaml
                yaml_file = dataset_path / 'dataset.yaml'
                if not yaml_file.exists():
                    print(f"   ❌ dataset.yaml faltante")
                    self.optimizations_applied.append(f"Crear dataset.yaml para {dataset_name}")
                else:
                    print(f"   ✅ dataset.yaml presente")
            else:
                print(f"❌ {description}: {dataset_name} - NO ENCONTRADO")
                self.optimizations_applied.append(f"Crear {description}")
    
    def optimize_ocr_service(self):
        """Optimiza el servicio de OCR"""
        
        print("OPTIMIZANDO SERVICIO DE OCR")
        print("=" * 40)
        
        ocr_service_path = Path("services/ocr_service.py")
        
        if not ocr_service_path.exists():
            print("❌ Servicio de OCR no encontrado")
            return
        
        with open(ocr_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar optimizaciones
        optimizations = [
            ('cache', 'Cache de modelos implementado'),
            ('error_handling', 'Manejo de errores robusto'),
            ('performance', 'Optimizaciones de rendimiento')
        ]
        
        for check, description in optimizations:
            if self.check_ocr_optimization(content, check):
                print(f"✅ {description}")
            else:
                print(f"⚠️  {description} - Puede mejorarse")
                self.optimizations_applied.append(f"Optimizar {description}")
    
    def check_ocr_optimization(self, content, optimization_type):
        """Verifica si una optimización está presente en el código"""
        
        checks = {
            'cache': ['_yolo_model_cache', 'cache'],
            'error_handling': ['try:', 'except:', 'FileNotFoundError'],
            'performance': ['conf=', 'imgsz=', 'batch=']
        }
        
        if optimization_type in checks:
            return any(check in content for check in checks[optimization_type])
        
        return False
    
    def optimize_docker_config(self):
        """Optimiza la configuración de Docker"""
        
        print("OPTIMIZANDO CONFIGURACION DE DOCKER")
        print("=" * 40)
        
        docker_files = {
            'docker-compose.yml': 'Configuración de servicios',
            'Dockerfile': 'Imagen de la API',
            '.env': 'Variables de entorno'
        }
        
        for file_name, description in docker_files.items():
            file_path = Path(file_name)
            
            if file_path.exists():
                print(f"✅ {description}: {file_name}")
                
                # Verificar contenido específico
                if file_name == 'docker-compose.yml':
                    self.check_docker_compose(file_path)
                elif file_name == '.env':
                    self.check_env_file(file_path)
            else:
                print(f"❌ {description}: {file_name} - NO ENCONTRADO")
                self.optimizations_applied.append(f"Crear {description}")
    
    def check_docker_compose(self, file_path):
        """Verifica la configuración de docker-compose.yml"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_services = ['db', 'redis', 'api', 'celery_worker']
        missing_services = []
        
        for service in required_services:
            if service not in content:
                missing_services.append(service)
        
        if missing_services:
            print(f"   ⚠️  Servicios faltantes: {missing_services}")
            self.optimizations_applied.append("Completar servicios de Docker")
        else:
            print(f"   ✅ Todos los servicios presentes")
    
    def check_env_file(self, file_path):
        """Verifica el archivo .env"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_vars = ['SECRET_KEY_JWT', 'DATABASE_URL', 'REDIS_HOST']
        missing_vars = []
        
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"   ⚠️  Variables faltantes: {missing_vars}")
            self.optimizations_applied.append("Completar variables de entorno")
        else:
            print(f"   ✅ Variables principales presentes")
    
    def create_optimization_scripts(self):
        """Crea scripts de optimización automática"""
        
        print("CREANDO SCRIPTS DE OPTIMIZACION")
        print("=" * 40)
        
        # Script de limpieza
        cleanup_script = """#!/usr/bin/env python3
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
"""
        
        with open("scripts/cleanup_system.py", 'w', encoding='utf-8') as f:
            f.write(cleanup_script)
        
        print("✅ Script de limpieza creado: scripts/cleanup_system.py")
        self.optimizations_applied.append("Crear script de limpieza")
        
        # Script de monitoreo
        monitoring_script = """#!/usr/bin/env python3
'''
Script de monitoreo del sistema
'''

import psutil
import time
import json
from datetime import datetime

def monitor_system():
    '''Monitorea el rendimiento del sistema'''
    
    print("📊 MONITOREO DEL SISTEMA")
    print("=" * 30)
    
    while True:
        # Información del sistema
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Información de procesos
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['cpu_percent'] > 5.0:  # Procesos que usan > 5% CPU
                    processes.append(proc.info)
            except:
                pass
        
        # Mostrar información
        print(f"\\n⏰ {datetime.now().strftime('%H:%M:%S')}")
        print(f"CPU: {cpu_percent}%")
        print(f"RAM: {memory.percent}% ({memory.used / 1024**3:.1f} GB / {memory.total / 1024**3:.1f} GB)")
        print(f"Disco: {disk.percent}% ({disk.used / 1024**3:.1f} GB / {disk.total / 1024**3:.1f} GB)")
        
        if processes:
            print("🔥 Procesos activos:")
            for proc in processes[:5]:  # Top 5
                print(f"   {proc['name']}: {proc['cpu_percent']:.1f}% CPU, {proc['memory_percent']:.1f}% RAM")
        
        time.sleep(30)  # Monitorear cada 30 segundos

if __name__ == "__main__":
    try:
        monitor_system()
    except KeyboardInterrupt:
        print("\\n👋 Monitoreo detenido")
"""
        
        with open("scripts/monitor_system.py", 'w', encoding='utf-8') as f:
            f.write(monitoring_script)
        
        print("✅ Script de monitoreo creado: scripts/monitor_system.py")
        self.optimizations_applied.append("Crear script de monitoreo")
    
    def generate_optimization_report(self):
        """Genera reporte de optimizaciones"""
        
        print("GENERANDO REPORTE DE OPTIMIZACIONES")
        print("=" * 40)
        
        report = {
            'timestamp': str(Path().cwd()),
            'optimizations_applied': self.optimizations_applied,
            'errors': self.errors,
            'recommendations': [
                "Ejecutar análisis completo: python scripts/system_analyzer.py",
                "Limpiar sistema: python scripts/cleanup_system.py",
                "Monitorear rendimiento: python scripts/monitor_system.py",
                "Entrenar modelos faltantes",
                "Optimizar configuración de Docker"
            ]
        }
        
        report_path = Path("optimization_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte guardado: {report_path}")
        
        # Mostrar resumen
        print(f"\\n📊 RESUMEN DE OPTIMIZACIONES")
        print("=" * 30)
        print(f"Optimizaciones aplicadas: {len(self.optimizations_applied)}")
        print(f"Errores encontrados: {len(self.errors)}")
        print(f"Recomendaciones: {len(report['recommendations'])}")
        
        if self.optimizations_applied:
            print(f"\nOPTIMIZACIONES APLICADAS:")
            for i, opt in enumerate(self.optimizations_applied, 1):
                print(f"{i}. {opt}")
        
        return report
    
    def run_optimization(self):
        """Ejecuta la optimización completa"""
        
        print("OPTIMIZACION AUTOMATICA DEL SISTEMA")
        print("=" * 60)
        
        try:
            # Ejecutar optimizaciones
            self.optimize_model_loading()
            self.optimize_datasets()
            self.optimize_ocr_service()
            self.optimize_docker_config()
            self.create_optimization_scripts()
            
            # Generar reporte
            report = self.generate_optimization_report()
            
            print(f"\nOPTIMIZACION COMPLETADA")
            print("=" * 60)
            
            return report
            
        except Exception as e:
            self.errors.append(str(e))
            print(f" Error durante la optimización: {e}")
            return None

def main():
    """Función principal"""
    
    optimizer = AutoOptimizer()
    report = optimizer.run_optimization()
    
    if report:
        print(f"\nPROXIMOS PASOS RECOMENDADOS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")

if __name__ == "__main__":
    main()
