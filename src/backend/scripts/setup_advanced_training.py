#!/usr/bin/env python3
"""
Script de configuración avanzada para el entorno de entrenamiento
Incluye verificación de dependencias, configuración automática y optimizaciones
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json
import yaml
from typing import Dict, List, Optional, Tuple

class AdvancedTrainingSetup:
    """Configurador avanzado del entorno de entrenamiento"""
    
    def __init__(self):
        self.system_info = self._get_system_info()
        self.requirements = self._load_requirements()
        self.config_paths = self._get_config_paths()
        
    def _get_system_info(self) -> Dict:
        """Obtiene información del sistema"""
        return {
            'platform': platform.system(),
            'python_version': sys.version,
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'cpu_count': os.cpu_count()
        }
    
    def _load_requirements(self) -> Dict:
        """Carga los requisitos necesarios"""
        return {
            'python_min_version': '3.8',
            'packages': {
                'ultralytics': '>=8.0.0',
                'torch': '>=1.12.0',
                'torchvision': '>=0.13.0',
                'opencv-python': '>=4.8.0',
                'pillow': '>=9.0.0',
                'matplotlib': '>=3.5.0',
                'seaborn': '>=0.11.0',
                'pandas': '>=1.5.0',
                'numpy': '>=1.21.0',
                'scikit-learn': '>=1.1.0',
                'optuna': '>=3.0.0',
                'wandb': '>=0.13.0',
                'psutil': '>=5.9.0',
                'tqdm': '>=4.64.0',
                'pyyaml': '>=6.0'
            },
            'optional_packages': {
                'tensorboard': '>=2.10.0',
                'albumentations': '>=1.3.0',
                'imgaug': '>=0.4.0',
                'onnx': '>=1.12.0',
                'onnxruntime': '>=1.12.0'
            }
        }
    
    def _get_config_paths(self) -> Dict:
        """Obtiene las rutas de configuración"""
        return {
            'venv_dir': Path('yolo_training_env'),
            'requirements_file': Path('requirements_training.txt'),
            'config_dir': Path('configs'),
            'datasets_dir': Path('datasets'),
            'models_dir': Path('models/yolo_models'),
            'scripts_dir': Path('scripts'),
            'logs_dir': Path('logs')
        }
    
    def check_system_requirements(self) -> bool:
        """Verifica los requisitos del sistema"""
        
        print("🔍 VERIFICANDO REQUISITOS DEL SISTEMA")
        print("=" * 50)
        
        all_good = True
        
        # Verificar Python
        python_version = sys.version_info
        min_version = tuple(map(int, self.requirements['python_min_version'].split('.')))
        
        if python_version >= min_version:
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (requerido: {self.requirements['python_min_version']}+)")
            all_good = False
        
        # Verificar CUDA si está disponible
        try:
            import torch
            if torch.cuda.is_available():
                cuda_version = torch.version.cuda
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                print(f"✅ CUDA {cuda_version} disponible")
                print(f"✅ GPU: {gpu_name} ({gpu_memory:.1f} GB)")
            else:
                print("⚠️ CUDA no disponible - Se usará CPU (entrenamiento será lento)")
        except ImportError:
            print("⚠️ PyTorch no instalado - Se instalará en el siguiente paso")
        
        # Verificar memoria RAM
        try:
            import psutil
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            available_gb = memory.available / (1024**3)
            
            if total_gb >= 8:
                print(f"✅ RAM: {total_gb:.1f} GB (disponible: {available_gb:.1f} GB)")
            elif total_gb >= 4:
                print(f"⚠️ RAM: {total_gb:.1f} GB (disponible: {available_gb:.1f} GB) - Recomendado 8+ GB")
            else:
                print(f"❌ RAM: {total_gb:.1f} GB - Insuficiente para entrenamiento")
                all_good = False
        except ImportError:
            print("⚠️ No se puede verificar RAM - psutil no instalado")
        
        # Verificar espacio en disco
        disk_usage = shutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        
        if free_gb >= 20:
            print(f"✅ Disco libre: {free_gb:.1f} GB")
        elif free_gb >= 10:
            print(f"⚠️ Disco libre: {free_gb:.1f} GB - Recomendado 20+ GB")
        else:
            print(f"❌ Disco libre: {free_gb:.1f} GB - Insuficiente")
            all_good = False
        
        return all_good
    
    def setup_environment(self, force_recreate: bool = False) -> bool:
        """Configura el entorno virtual"""
        
        print("\n🔧 CONFIGURANDO ENTORNO VIRTUAL")
        print("=" * 50)
        
        venv_path = self.config_paths['venv_dir']
        
        # Verificar si el entorno ya existe
        if venv_path.exists() and not force_recreate:
            print(f"✅ Entorno virtual ya existe: {venv_path}")
            return True
        
        # Crear entorno virtual
        if venv_path.exists() and force_recreate:
            print(f"🗑️ Eliminando entorno existente...")
            shutil.rmtree(venv_path)
        
        print(f"📦 Creando entorno virtual en: {venv_path}")
        
        try:
            subprocess.run([
                sys.executable, '-m', 'venv', str(venv_path)
            ], check=True, capture_output=True, text=True)
            
            print("✅ Entorno virtual creado exitosamente")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creando entorno virtual: {e}")
            print(f"   Salida: {e.stdout}")
            print(f"   Error: {e.stderr}")
            return False
    
    def install_dependencies(self, use_gpu: bool = True) -> bool:
        """Instala las dependencias necesarias"""
        
        print("\n📦 INSTALANDO DEPENDENCIAS")
        print("=" * 50)
        
        venv_path = self.config_paths['venv_dir']
        
        # Determinar el ejecutable de pip
        if platform.system() == 'Windows':
            pip_executable = venv_path / 'Scripts' / 'pip.exe'
        else:
            pip_executable = venv_path / 'bin' / 'pip'
        
        if not pip_executable.exists():
            print(f"❌ Pip no encontrado en: {pip_executable}")
            return False
        
        # Actualizar pip
        print("🔄 Actualizando pip...")
        try:
            subprocess.run([
                str(pip_executable), 'install', '--upgrade', 'pip'
            ], check=True, capture_output=True, text=True)
            print("✅ Pip actualizado")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Error actualizando pip: {e}")
        
        # Instalar PyTorch con soporte CUDA si se solicita
        if use_gpu:
            print("🎮 Instalando PyTorch con soporte CUDA...")
            try:
                subprocess.run([
                    str(pip_executable), 'install', 'torch', 'torchvision', 'torchaudio',
                    '--index-url', 'https://download.pytorch.org/whl/cu118'
                ], check=True, capture_output=True, text=True)
                print("✅ PyTorch con CUDA instalado")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Error instalando PyTorch con CUDA: {e}")
                print("🔄 Intentando con PyTorch CPU...")
                use_gpu = False
        
        if not use_gpu:
            print("💻 Instalando PyTorch CPU...")
            try:
                subprocess.run([
                    str(pip_executable), 'install', 'torch', 'torchvision', 'torchaudio'
                ], check=True, capture_output=True, text=True)
                print("✅ PyTorch CPU instalado")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error instalando PyTorch: {e}")
                return False
        
        # Instalar ultralytics
        print("🚀 Instalando Ultralytics...")
        try:
            subprocess.run([
                str(pip_executable), 'install', 'ultralytics'
            ], check=True, capture_output=True, text=True)
            print("✅ Ultralytics instalado")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando Ultralytics: {e}")
            return False
        
        # Instalar paquetes adicionales
        additional_packages = [
            'opencv-python', 'pillow', 'matplotlib', 'seaborn', 'pandas',
            'numpy', 'scikit-learn', 'optuna', 'wandb', 'psutil', 'tqdm', 'pyyaml'
        ]
        
        print(f"📚 Instalando paquetes adicionales...")
        try:
            subprocess.run([
                str(pip_executable), 'install'
            ] + additional_packages, check=True, capture_output=True, text=True)
            print("✅ Paquetes adicionales instalados")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Error instalando algunos paquetes: {e}")
        
        # Instalar paquetes opcionales
        optional_packages = ['tensorboard', 'albumentations']
        print(f"🔧 Instalando paquetes opcionales...")
        for package in optional_packages:
            try:
                subprocess.run([
                    str(pip_executable), 'install', package
                ], check=True, capture_output=True, text=True)
                print(f"✅ {package} instalado")
            except subprocess.CalledProcessError:
                print(f"⚠️ No se pudo instalar {package} (opcional)")
        
        return True
    
    def create_directories(self) -> bool:
        """Crea los directorios necesarios"""
        
        print("\n📁 CREANDO ESTRUCTURA DE DIRECTORIOS")
        print("=" * 50)
        
        directories = [
            self.config_paths['config_dir'],
            self.config_paths['datasets_dir'],
            self.config_paths['models_dir'],
            self.config_paths['scripts_dir'],
            self.config_paths['logs_dir'],
            self.config_paths['datasets_dir'] / 'dni' / 'images',
            self.config_paths['datasets_dir'] / 'dni' / 'labels',
            self.config_paths['datasets_dir'] / 'invoices' / 'images',
            self.config_paths['datasets_dir'] / 'invoices' / 'labels',
            self.config_paths['datasets_dir'] / 'dni_robust' / 'images',
            self.config_paths['datasets_dir'] / 'dni_robust' / 'labels',
            self.config_paths['datasets_dir'] / 'invoices_argentina' / 'images',
            self.config_paths['datasets_dir'] / 'invoices_argentina' / 'labels',
            self.config_paths['models_dir'] / 'pretrained',
            self.config_paths['models_dir'] / 'trained'
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✅ {directory}")
            except Exception as e:
                print(f"❌ Error creando {directory}: {e}")
                return False
        
        return True
    
    def create_config_files(self) -> bool:
        """Crea archivos de configuración"""
        
        print("\n⚙️ CREANDO ARCHIVOS DE CONFIGURACIÓN")
        print("=" * 50)
        
        # Configuración para DNI
        dni_config = {
            'path': './datasets/dni_robust',
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': 5,
            'names': {
                0: 'document_number',
                1: 'full_name',
                2: 'birth_date',
                3: 'gender',
                4: 'expiry_date'
            }
        }
        
        # Configuración para facturas
        invoice_config = {
            'path': './datasets/invoices_argentina',
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': 8,
            'names': {
                0: 'invoice_number',
                1: 'date',
                2: 'vendor',
                3: 'cuit',
                4: 'subtotal',
                5: 'tax',
                6: 'total',
                7: 'items_table'
            }
        }
        
        # Guardar configuraciones
        configs = [
            (self.config_paths['config_dir'] / 'dni_dataset.yaml', dni_config),
            (self.config_paths['config_dir'] / 'invoice_dataset.yaml', invoice_config)
        ]
        
        for config_path, config_data in configs:
            try:
                with open(config_path, 'w') as f:
                    yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
                print(f"✅ {config_path}")
            except Exception as e:
                print(f"❌ Error creando {config_path}: {e}")
                return False
        
        # Crear archivo de configuración de entrenamiento
        training_config = {
            'system': {
                'device': 'cuda' if self._check_cuda_available() else 'cpu',
                'workers': min(8, os.cpu_count()),
                'batch_size': 16 if self._check_cuda_available() else 8
            },
            'training': {
                'default_epochs': 300,
                'patience': 50,
                'save_period': 10,
                'validation_interval': 1
            },
            'optimization': {
                'use_hyperopt': True,
                'n_trials': 50,
                'use_cross_validation': False,
                'n_folds': 5
            },
            'monitoring': {
                'use_wandb': True,
                'wandb_project': 'ocr-document-detection',
                'monitoring_interval': 30
            }
        }
        
        try:
            config_file = self.config_paths['config_dir'] / 'training_config.json'
            with open(config_file, 'w') as f:
                json.dump(training_config, f, indent=2)
            print(f"✅ {config_file}")
        except Exception as e:
            print(f"❌ Error creando configuración de entrenamiento: {e}")
            return False
        
        return True
    
    def _check_cuda_available(self) -> bool:
        """Verifica si CUDA está disponible"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def download_pretrained_models(self) -> bool:
        """Descarga modelos preentrenados"""
        
        print("\n📥 DESCARGANDO MODELOS PRETRENADOS")
        print("=" * 50)
        
        venv_path = self.config_paths['venv_dir']
        
        # Determinar el ejecutable de Python
        if platform.system() == 'Windows':
            python_executable = venv_path / 'Scripts' / 'python.exe'
        else:
            python_executable = venv_path / 'bin' / 'python'
        
        if not python_executable.exists():
            print(f"❌ Python no encontrado en: {python_executable}")
            return False
        
        # Script para descargar modelos
        download_script = """
import torch
from ultralytics import YOLO
import os

print("Descargando YOLOv8n...")
model = YOLO('yolov8n.pt')
print("✅ YOLOv8n descargado")

print("Descargando YOLOv8s...")
model = YOLO('yolov8s.pt')
print("✅ YOLOv8s descargado")

print("Descargando YOLOv8m...")
model = YOLO('yolov8m.pt')
print("✅ YOLOv8m descargado")

# Mover a directorio de modelos pretrenados
import shutil
models_dir = 'models/pretrained'
os.makedirs(models_dir, exist_ok=True)

for model_name in ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt']:
    if os.path.exists(model_name):
        shutil.move(model_name, os.path.join(models_dir, model_name))
        print(f"Moved {model_name} to {models_dir}")

print("✅ Todos los modelos descargados")
"""
        
        try:
            subprocess.run([
                str(python_executable), '-c', download_script
            ], check=True, capture_output=True, text=True)
            print("✅ Modelos preentrenados descargados")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error descargando modelos: {e}")
            print(f"   Salida: {e.stdout}")
            print(f"   Error: {e.stderr}")
            return False
    
    def create_launcher_scripts(self) -> bool:
        """Crea scripts de lanzamiento"""
        
        print("\n🚀 CREANDO SCRIPTS DE LANZAMIENTO")
        print("=" * 50)
        
        venv_path = self.config_paths['venv_dir']
        
        # Script para entrenamiento básico
        basic_training_script = f"""#!/usr/bin/env python3
import sys
from pathlib import Path

# Agregar el directorio de scripts al path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from improved_training_system import ImprovedTrainingSystem

if __name__ == "__main__":
    trainer = ImprovedTrainingSystem()
    
    print("🎯 SELECCIONAR MODELO A ENTRENAR:")
    print("1. DNI")
    print("2. Facturas")
    
    choice = input("Selecciona opción (1-2): ").strip()
    
    if choice == '1':
        trainer.train_model('dni')
    elif choice == '2':
        trainer.train_model('invoices')
    else:
        print("Opción inválida")
"""
        
        # Script para entrenamiento avanzado
        advanced_training_script = f"""#!/usr/bin/env python3
import sys
from pathlib import Path

# Agregar el directorio de scripts al path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from advanced_training_system import AdvancedTrainingSystem

if __name__ == "__main__":
    trainer = AdvancedTrainingSystem(use_wandb=True)
    
    print("🎯 SELECCIONAR OPCIONES DE ENTRENAMIENTO:")
    print("1. DNI básico")
    print("2. Facturas básico")
    print("3. DNI con optimización")
    print("4. Facturas con validación cruzada")
    print("5. Ambos con todas las optimizaciones")
    
    choice = input("Selecciona opción (1-5): ").strip()
    
    if choice in ['1', '3', '5']:
        use_hyperopt = choice in ['3', '5']
        use_cv = choice == '5'
        trainer.train_model_advanced('dni', use_hyperopt=use_hyperopt, use_cv=use_cv)
    
    if choice in ['2', '4', '5']:
        use_hyperopt = choice in ['4', '5']
        use_cv = choice == '5'
        trainer.train_model_advanced('invoices', use_hyperopt=use_hyperopt, use_cv=use_cv)
"""
        
        # Script para optimización de hiperparámetros
        hyperopt_script = f"""#!/usr/bin/env python3
import sys
from pathlib import Path

# Agregar el directorio de scripts al path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from hyperparameter_optimizer import HyperparameterOptimizer

if __name__ == "__main__":
    print("🎯 OPTIMIZACIÓN DE HIPERPARÁMETROS")
    
    model_type = input("Tipo de modelo (dni/invoices): ").strip().lower()
    n_trials = int(input("Número de trials (default 50): ") or "50")
    train_final = input("Entrenar modelo final? (y/n): ").strip().lower() == 'y'
    
    optimizer = HyperparameterOptimizer(model_type, n_trials)
    optimizer.optimize()
    optimizer.analyze_results()
    optimizer.save_results()
    
    if train_final:
        optimizer.train_final_model()
"""
        
        # Script para monitoreo
        monitor_script = f"""#!/usr/bin/env python3
import sys
from pathlib import Path

# Agregar el directorio de scripts al path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from training_monitor import TrainingMonitor

if __name__ == "__main__":
    monitor = TrainingMonitor(monitoring_interval=30)
    
    try:
        monitor.start_monitoring()
        print("✅ Monitoreo iniciado. Presiona Ctrl+C para detener...")
        
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\\n⏹️ Deteniendo monitoreo...")
        monitor.stop_monitoring()
        print("✅ Monitoreo detenido")
"""
        
        scripts = [
            ('start_basic_training.py', basic_training_script),
            ('start_advanced_training.py', advanced_training_script),
            ('start_hyperopt.py', hyperopt_script),
            ('start_monitoring.py', monitor_script)
        ]
        
        for script_name, script_content in scripts:
            try:
                script_path = Path(script_name)
                with open(script_path, 'w') as f:
                    f.write(script_content)
                
                # Hacer ejecutable en sistemas Unix
                if platform.system() != 'Windows':
                    os.chmod(script_path, 0o755)
                
                print(f"✅ {script_path}")
            except Exception as e:
                print(f"❌ Error creando {script_name}: {e}")
                return False
        
        return True
    
    def run_system_test(self) -> bool:
        """Ejecuta una prueba del sistema"""
        
        print("\n🧪 EJECUTANDO PRUEBA DEL SISTEMA")
        print("=" * 50)
        
        venv_path = self.config_paths['venv_dir']
        
        # Determinar el ejecutable de Python
        if platform.system() == 'Windows':
            python_executable = venv_path / 'Scripts' / 'python.exe'
        else:
            python_executable = venv_path / 'bin' / 'python'
        
        test_script = """
import torch
from ultralytics import YOLO
import cv2
import numpy as np

print("🔍 Probando PyTorch...")
print(f"   PyTorch version: {torch.__version__}")
print(f"   CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   CUDA version: {torch.version.cuda}")
    print(f"   GPU: {torch.cuda.get_device_name(0)}")

print("\\n🔍 Probando Ultralytics...")
try:
    model = YOLO('yolov8n.pt')
    print("   ✅ YOLO cargado exitosamente")
except Exception as e:
    print(f"   ❌ Error cargando YOLO: {e}")

print("\\n🔍 Probando OpenCV...")
try:
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite('test_image.jpg', img)
    loaded_img = cv2.imread('test_image.jpg')
    if loaded_img is not None:
        print("   ✅ OpenCV funcionando correctamente")
        import os
        os.remove('test_image.jpg')
    else:
        print("   ❌ Error con OpenCV")
except Exception as e:
    print(f"   ❌ Error con OpenCV: {e}")

print("\\n✅ Prueba del sistema completada")
"""
        
        try:
            result = subprocess.run([
                str(python_executable), '-c', test_script
            ], check=True, capture_output=True, text=True)
            
            print(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en prueba del sistema: {e}")
            print(f"   Salida: {e.stdout}")
            print(f"   Error: {e.stderr}")
            return False
    
    def create_setup_report(self) -> Dict:
        """Crea un reporte de la configuración"""
        
        report = {
            'setup_date': str(datetime.now()),
            'system_info': self.system_info,
            'config_paths': {k: str(v) for k, v in self.config_paths.items()},
            'venv_exists': self.config_paths['venv_dir'].exists(),
            'directories_created': all(path.exists() for path in [
                self.config_paths['config_dir'],
                self.config_paths['datasets_dir'],
                self.config_paths['models_dir']
            ]),
            'cuda_available': self._check_cuda_available()
        }
        
        # Guardar reporte
        report_path = Path('setup_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Reporte de configuración guardado: {report_path}")
        
        return report
    
    def setup_complete(self, use_gpu: bool = True, force_recreate: bool = False) -> bool:
        """Ejecuta la configuración completa"""
        
        print("🚀 CONFIGURACIÓN AVANZADA DEL ENTORNO DE ENTRENAMIENTO")
        print("=" * 70)
        
        steps = [
            ("Verificar requisitos del sistema", self.check_system_requirements),
            ("Configurar entorno virtual", lambda: self.setup_environment(force_recreate)),
            ("Instalar dependencias", lambda: self.install_dependencies(use_gpu)),
            ("Crear directorios", self.create_directories),
            ("Crear archivos de configuración", self.create_config_files),
            ("Descargar modelos preentrenados", self.download_pretrained_models),
            ("Crear scripts de lanzamiento", self.create_launcher_scripts),
            ("Ejecutar prueba del sistema", self.run_system_test)
        ]
        
        success = True
        
        for step_name, step_function in steps:
            print(f"\n{'='*20} {step_name.upper()} {'='*20}")
            
            try:
                if not step_function():
                    print(f"❌ Falló: {step_name}")
                    success = False
                    break
            except Exception as e:
                print(f"❌ Error en {step_name}: {e}")
                success = False
                break
        
        # Crear reporte final
        self.create_setup_report()
        
        if success:
            print(f"\n🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 70)
            print("📋 PRÓXIMOS PASOS:")
            print("1. Coloca tus imágenes anotadas en datasets/[tipo]/images/")
            print("2. Coloca tus etiquetas en datasets/[tipo]/labels/")
            print("3. Ejecuta: python start_basic_training.py")
            print("4. Para entrenamiento avanzado: python start_advanced_training.py")
            print("5. Para optimización: python start_hyperopt.py")
            print("6. Para monitoreo: python start_monitoring.py")
        else:
            print(f"\n❌ CONFIGURACIÓN FALLÓ")
            print("=" * 70)
            print("Revisa los errores anteriores y vuelve a intentar")
        
        return success

def main():
    """Función principal"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Configuración avanzada del entorno de entrenamiento')
    parser.add_argument('--no-gpu', action='store_true', help='No usar GPU')
    parser.add_argument('--force-recreate', action='store_true', help='Recrear entorno virtual')
    
    args = parser.parse_args()
    
    setup = AdvancedTrainingSetup()
    success = setup.setup_complete(
        use_gpu=not args.no_gpu,
        force_recreate=args.force_recreate
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    from datetime import datetime
    main()
