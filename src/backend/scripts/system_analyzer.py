#!/usr/bin/env python3
"""
Sistema de análisis y optimización del pipeline de OCR
"""

import os
import time
import json
import psutil
import sys
from pathlib import Path
from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO

class SystemAnalyzer:
    """Analizador del sistema de OCR y detección"""
    
    def __init__(self):
        self.results = {}
        self.performance_metrics = {}
        
    def analyze_models(self):
        """Analiza todos los modelos disponibles"""
        
        print("🔍 ANÁLISIS DE MODELOS")
        print("=" * 50)
        
        models_path = Path("models/yolo_models")
        if not models_path.exists():
            print("❌ Directorio de modelos no encontrado")
            return
        
        models_info = {}
        
        for model_dir in models_path.iterdir():
            if model_dir.is_dir() and (model_dir / "weights").exists():
                weights_dir = model_dir / "weights"
                best_model = weights_dir / "best.pt"
                last_model = weights_dir / "last.pt"
                
                model_info = {
                    'name': model_dir.name,
                    'best_exists': best_model.exists(),
                    'last_exists': last_model.exists(),
                    'size_mb': 0,
                    'classes': [],
                    'performance': {}
                }
                
                # Calcular tamaño
                if best_model.exists():
                    model_info['size_mb'] = best_model.stat().st_size / (1024 * 1024)
                
                # Cargar modelo para obtener información
                try:
                    if best_model.exists():
                        model = YOLO(str(best_model))
                        model_info['classes'] = list(model.names.values())
                        model_info['num_classes'] = len(model.names)
                    elif last_model.exists():
                        model = YOLO(str(last_model))
                        model_info['classes'] = list(model.names.values())
                        model_info['num_classes'] = len(model.names)
                except Exception as e:
                    model_info['error'] = str(e)
                
                models_info[model_dir.name] = model_info
                
                print(f"📦 {model_dir.name}:")
                print(f"   Tamaño: {model_info['size_mb']:.1f} MB")
                print(f"   Clases: {model_info['num_classes']}")
                print(f"   best.pt: {'✅' if model_info['best_exists'] else '❌'}")
                print(f"   last.pt: {'✅' if model_info['last_exists'] else '❌'}")
                if 'error' in model_info:
                    print(f"   Error: {model_info['error']}")
        
        self.results['models'] = models_info
        return models_info
    
    def analyze_datasets(self):
        """Analiza todos los datasets disponibles"""
        
        print(f"\n📊 ANÁLISIS DE DATASETS")
        print("=" * 50)
        
        datasets_path = Path("datasets")
        if not datasets_path.exists():
            print("❌ Directorio de datasets no encontrado")
            return
        
        datasets_info = {}
        
        for dataset_dir in datasets_path.iterdir():
            if dataset_dir.is_dir():
                dataset_info = {
                    'name': dataset_dir.name,
                    'images': {'train': 0, 'val': 0, 'test': 0},
                    'labels': {'train': 0, 'val': 0, 'test': 0},
                    'total_size_mb': 0,
                    'has_yaml': False
                }
                
                # Contar imágenes y etiquetas
                for split in ['train', 'val', 'test']:
                    images_dir = dataset_dir / 'images' / split
                    labels_dir = dataset_dir / 'labels' / split
                    
                    if images_dir.exists():
                        dataset_info['images'][split] = len(list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png')))
                    
                    if labels_dir.exists():
                        dataset_info['labels'][split] = len(list(labels_dir.glob('*.txt')))
                
                # Calcular tamaño total
                total_size = 0
                for file_path in dataset_dir.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                dataset_info['total_size_mb'] = total_size / (1024 * 1024)
                
                # Verificar dataset.yaml
                yaml_file = dataset_dir / 'dataset.yaml'
                dataset_info['has_yaml'] = yaml_file.exists()
                
                datasets_info[dataset_dir.name] = dataset_info
                
                print(f"📁 {dataset_dir.name}:")
                print(f"   Imágenes: Train={dataset_info['images']['train']}, Val={dataset_info['images']['val']}, Test={dataset_info['images']['test']}")
                print(f"   Etiquetas: Train={dataset_info['labels']['train']}, Val={dataset_info['labels']['val']}, Test={dataset_info['labels']['test']}")
                print(f"   Tamaño: {dataset_info['total_size_mb']:.1f} MB")
                print(f"   dataset.yaml: {'✅' if dataset_info['has_yaml'] else '❌'}")
        
        self.results['datasets'] = datasets_info
        return datasets_info
    
    def analyze_performance(self):
        """Analiza el rendimiento del sistema"""
        
        print(f"\n⚡ ANÁLISIS DE RENDIMIENTO")
        print("=" * 50)
        
        # Información del sistema
        system_info = {
            'cpu_count': psutil.cpu_count(),
            'memory_gb': psutil.virtual_memory().total / (1024**3),
            'disk_free_gb': psutil.disk_usage('/').free / (1024**3) if os.name != 'nt' else psutil.disk_usage('C:').free / (1024**3),
            'python_version': sys.version,
            'platform': sys.platform
        }
        
        print(f"💻 Sistema:")
        print(f"   CPU: {system_info['cpu_count']} cores")
        print(f"   RAM: {system_info['memory_gb']:.1f} GB")
        print(f"   Disco libre: {system_info['disk_free_gb']:.1f} GB")
        print(f"   Python: {system_info['python_version'].split()[0]}")
        print(f"   Plataforma: {system_info['platform']}")
        
        # Probar rendimiento de modelos
        self.test_model_performance()
        
        self.results['system'] = system_info
        return system_info
    
    def test_model_performance(self):
        """Prueba el rendimiento de los modelos"""
        
        print(f"\n🧪 PRUEBA DE RENDIMIENTO DE MODELOS")
        print("=" * 50)
        
        # Crear imagen de prueba
        test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        models_path = Path("models/yolo_models")
        performance_results = {}
        
        for model_dir in models_path.iterdir():
            if model_dir.is_dir() and (model_dir / "weights" / "best.pt").exists():
                model_path = model_dir / "weights" / "best.pt"
                
                try:
                    print(f"📦 Probando {model_dir.name}...")
                    
                    # Cargar modelo
                    start_time = time.time()
                    model = YOLO(str(model_path))
                    load_time = time.time() - start_time
                    
                    # Inferencia
                    start_time = time.time()
                    results = model(test_image, verbose=False)
                    inference_time = time.time() - start_time
                    
                    # Contar detecciones
                    detections = 0
                    for r in results:
                        if r.boxes is not None:
                            detections = len(r.boxes)
                    
                    performance_results[model_dir.name] = {
                        'load_time': load_time,
                        'inference_time': inference_time,
                        'detections': detections,
                        'fps': 1.0 / inference_time if inference_time > 0 else 0
                    }
                    
                    print(f"   Carga: {load_time:.3f}s")
                    print(f"   Inferencia: {inference_time:.3f}s")
                    print(f"   FPS: {performance_results[model_dir.name]['fps']:.1f}")
                    print(f"   Detecciones: {detections}")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    performance_results[model_dir.name] = {'error': str(e)}
        
        self.results['performance'] = performance_results
        return performance_results
    
    def analyze_ocr_pipeline(self):
        """Analiza el pipeline de OCR"""
        
        print(f"\n🔍 ANÁLISIS DEL PIPELINE DE OCR")
        print("=" * 50)
        
        # Verificar dependencias
        dependencies = {
            'opencv': self.check_dependency('cv2'),
            'pytesseract': self.check_dependency('pytesseract'),
            'ultralytics': self.check_dependency('ultralytics'),
            'pillow': self.check_dependency('PIL'),
            'numpy': self.check_dependency('numpy')
        }
        
        print("📦 Dependencias:")
        for dep, status in dependencies.items():
            print(f"   {dep}: {'✅' if status else '❌'}")
        
        # Verificar configuración
        config_issues = []
        
        # Verificar Tesseract
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            print("   Tesseract: ✅")
        except Exception as e:
            print(f"   Tesseract: ❌ - {e}")
            config_issues.append(f"Tesseract no configurado: {e}")
        
        # Verificar rutas de modelos
        models_path = Path("models/yolo_models")
        if not models_path.exists():
            config_issues.append("Directorio de modelos no existe")
        
        self.results['dependencies'] = dependencies
        self.results['config_issues'] = config_issues
        
        return dependencies, config_issues
    
    def check_dependency(self, module_name):
        """Verifica si una dependencia está instalada"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def generate_recommendations(self):
        """Genera recomendaciones de optimización"""
        
        print(f"\n💡 RECOMENDACIONES DE OPTIMIZACIÓN")
        print("=" * 50)
        
        recommendations = []
        
        # Análisis de modelos
        if 'models' in self.results:
            models = self.results['models']
            
            # Verificar modelos faltantes
            if not any('dni' in name.lower() for name in models.keys()):
                recommendations.append("🚨 Crear modelo específico para DNI")
            
            if not any('invoice' in name.lower() for name in models.keys()):
                recommendations.append("🚨 Mejorar modelo de facturas")
            
            # Verificar tamaños de modelos
            for name, info in models.items():
                if info.get('size_mb', 0) > 100:
                    recommendations.append(f"⚠️  Modelo {name} es muy grande ({info['size_mb']:.1f} MB)")
        
        # Análisis de datasets
        if 'datasets' in self.results:
            datasets = self.results['datasets']
            
            for name, info in datasets.items():
                total_images = sum(info['images'].values())
                if total_images < 100:
                    recommendations.append(f"📊 Dataset {name} tiene pocas imágenes ({total_images})")
                
                if not info['has_yaml']:
                    recommendations.append(f"📄 Dataset {name} necesita dataset.yaml")
        
        # Análisis de rendimiento
        if 'performance' in self.results:
            performance = self.results['performance']
            
            for name, info in performance.items():
                if 'fps' in info and info['fps'] < 10:
                    recommendations.append(f"⚡ Modelo {name} es lento ({info['fps']:.1f} FPS)")
        
        # Análisis de dependencias
        if 'dependencies' in self.results:
            dependencies = self.results['dependencies']
            
            for dep, status in dependencies.items():
                if not status:
                    recommendations.append(f"📦 Instalar dependencia: {dep}")
        
        # Mostrar recomendaciones
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("✅ Sistema optimizado - No se encontraron problemas críticos")
        
        self.results['recommendations'] = recommendations
        return recommendations
    
    def save_report(self):
        """Guarda el reporte de análisis"""
        
        report_path = Path("system_analysis_report.json")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado: {report_path}")
        return report_path
    
    def run_full_analysis(self):
        """Ejecuta el análisis completo del sistema"""
        
        print("🚀 ANÁLISIS COMPLETO DEL SISTEMA")
        print("=" * 60)
        
        # Ejecutar todos los análisis
        self.analyze_models()
        self.analyze_datasets()
        self.analyze_performance()
        self.analyze_ocr_pipeline()
        self.generate_recommendations()
        
        # Guardar reporte
        self.save_report()
        
        print(f"\n🎉 ANÁLISIS COMPLETADO")
        print("=" * 60)
        
        return self.results

def main():
    """Función principal"""
    
    analyzer = SystemAnalyzer()
    results = analyzer.run_full_analysis()
    
    # Resumen final
    print(f"\n📋 RESUMEN FINAL")
    print("=" * 30)
    print(f"Modelos analizados: {len(results.get('models', {}))}")
    print(f"Datasets analizados: {len(results.get('datasets', {}))}")
    print(f"Recomendaciones: {len(results.get('recommendations', []))}")
    print(f"Problemas de configuración: {len(results.get('config_issues', []))}")

if __name__ == "__main__":
    main()
