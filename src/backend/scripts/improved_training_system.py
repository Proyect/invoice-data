#!/usr/bin/env python3
"""
Sistema de entrenamiento mejorado para modelos YOLO
Incluye optimizaciones automáticas y mejores prácticas
"""

import os
import time
import json
import torch
import psutil
from pathlib import Path
from ultralytics import YOLO
import yaml
import cv2
import numpy as np
from datetime import datetime

class ImprovedTrainingSystem:
    """Sistema de entrenamiento optimizado"""
    
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.results = {}
        self.training_configs = self.load_training_configs()
        
    def load_training_configs(self):
        """Carga configuraciones optimizadas para diferentes tipos de documentos"""
        
        return {
            'dni': {
                'model': 'yolov8n.pt',
                'data': 'datasets/dni_robust/dataset.yaml',
                'epochs': 200,
                'imgsz': 640,
                'batch': 16 if self.device == 'cuda' else 8,
                'device': self.device,
                'patience': 30,
                'save': True,
                'project': 'models/yolo_models',
                'name': 'dni_optimized_v2',
                'exist_ok': True,
                'pretrained': True,
                'optimizer': 'AdamW',
                'lr0': 0.003,
                'lrf': 0.01,
                'momentum': 0.937,
                'weight_decay': 0.0005,
                'warmup_epochs': 5,
                'box': 7.5,
                'cls': 0.5,
                'dfl': 1.5,
                # Augmentaciones específicas para DNI
                'hsv_h': 0.01,
                'hsv_s': 0.5,
                'hsv_v': 0.3,
                'degrees': 0.0,
                'translate': 0.05,
                'scale': 0.2,
                'shear': 0.0,
                'perspective': 0.0,
                'flipud': 0.0,
                'fliplr': 0.0,
                'mosaic': 1.0,
                'mixup': 0.0,
                'copy_paste': 0.0,
                'auto_augment': 'randaugment',
                'erasing': 0.2,
                'workers': 8 if self.device == 'cuda' else 4
            },
            'invoices': {
                'model': 'yolov8n.pt',
                'data': 'yolo/dataset_argentina.yaml',
                'epochs': 300,
                'imgsz': 640,
                'batch': 12 if self.device == 'cuda' else 6,
                'device': self.device,
                'patience': 50,
                'save': True,
                'project': 'models/yolo_models',
                'name': 'invoices_optimized_v2',
                'exist_ok': True,
                'pretrained': True,
                'optimizer': 'AdamW',
                'lr0': 0.002,
                'lrf': 0.01,
                'momentum': 0.937,
                'weight_decay': 0.0005,
                'warmup_epochs': 10,
                'box': 7.5,
                'cls': 0.5,
                'dfl': 1.5,
                # Augmentaciones específicas para facturas
                'hsv_h': 0.015,
                'hsv_s': 0.7,
                'hsv_v': 0.4,
                'degrees': 2.0,
                'translate': 0.1,
                'scale': 0.3,
                'shear': 1.0,
                'perspective': 0.0,
                'flipud': 0.0,
                'fliplr': 0.0,
                'mosaic': 1.0,
                'mixup': 0.1,
                'copy_paste': 0.0,
                'auto_augment': 'randaugment',
                'erasing': 0.3,
                'workers': 8 if self.device == 'cuda' else 4
            }
        }
    
    def check_system_requirements(self):
        """Verifica los requisitos del sistema"""
        
        print("🔍 VERIFICANDO REQUISITOS DEL SISTEMA")
        print("=" * 50)
        
        # Verificar GPU
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"✅ GPU: {gpu_name} ({gpu_memory:.1f} GB)")
        else:
            print("⚠️  GPU no disponible - Usando CPU (entrenamiento será lento)")
        
        # Verificar memoria RAM
        memory = psutil.virtual_memory()
        print(f"💾 RAM: {memory.total / (1024**3):.1f} GB (Disponible: {memory.available / (1024**3):.1f} GB)")
        
        if memory.available < 4 * (1024**3):  # Menos de 4GB
            print("⚠️  RAM insuficiente - Considera cerrar otras aplicaciones")
        
        # Verificar espacio en disco
        disk = psutil.disk_usage('.')
        free_gb = disk.free / (1024**3)
        print(f"💿 Disco libre: {free_gb:.1f} GB")
        
        if free_gb < 10:
            print("⚠️  Espacio en disco bajo - Considera liberar espacio")
        
        return {
            'gpu_available': torch.cuda.is_available(),
            'ram_gb': memory.total / (1024**3),
            'disk_free_gb': free_gb
        }
    
    def analyze_dataset_quality(self, dataset_path):
        """Analiza la calidad del dataset"""
        
        print(f"\n📊 ANALIZANDO DATASET: {dataset_path}")
        print("=" * 50)
        
        dataset_info = {
            'images': {'train': 0, 'val': 0, 'test': 0},
            'labels': {'train': 0, 'val': 0, 'test': 0},
            'total_size_mb': 0,
            'classes_distribution': {},
            'issues': []
        }
        
        dataset_dir = Path(dataset_path)
        
        if not dataset_dir.exists():
            print(f"❌ Dataset no encontrado: {dataset_path}")
            return None
        
        # Contar imágenes y etiquetas
        for split in ['train', 'val', 'test']:
            images_dir = dataset_dir / 'images' / split
            labels_dir = dataset_dir / 'labels' / split
            
            if images_dir.exists():
                images = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
                dataset_info['images'][split] = len(images)
                
                # Verificar calidad de imágenes
                for img_path in images[:5]:  # Muestra de 5 imágenes
                    try:
                        img = cv2.imread(str(img_path))
                        if img is None:
                            dataset_info['issues'].append(f"Imagen corrupta: {img_path.name}")
                    except Exception as e:
                        dataset_info['issues'].append(f"Error leyendo {img_path.name}: {e}")
            
            if labels_dir.exists():
                labels = list(labels_dir.glob('*.txt'))
                dataset_info['labels'][split] = len(labels)
                
                # Analizar distribución de clases
                for label_path in labels:
                    try:
                        with open(label_path, 'r') as f:
                            for line in f:
                                if line.strip():
                                    class_id = int(line.split()[0])
                                    if class_id not in dataset_info['classes_distribution']:
                                        dataset_info['classes_distribution'][class_id] = 0
                                    dataset_info['classes_distribution'][class_id] += 1
                    except Exception as e:
                        dataset_info['issues'].append(f"Error leyendo {label_path.name}: {e}")
        
        # Calcular tamaño total
        total_size = 0
        for file_path in dataset_dir.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        dataset_info['total_size_mb'] = total_size / (1024 * 1024)
        
        # Mostrar resultados
        total_images = sum(dataset_info['images'].values())
        total_labels = sum(dataset_info['labels'].values())
        
        print(f"📁 Imágenes: {total_images} (Train: {dataset_info['images']['train']}, Val: {dataset_info['images']['val']}, Test: {dataset_info['images']['test']})")
        print(f"🏷️  Etiquetas: {total_labels} (Train: {dataset_info['labels']['train']}, Val: {dataset_info['labels']['val']}, Test: {dataset_info['labels']['test']})")
        print(f"💾 Tamaño: {dataset_info['total_size_mb']:.1f} MB")
        
        # Verificar balance de clases
        if dataset_info['classes_distribution']:
            print(f"📊 Distribución de clases:")
            for class_id, count in sorted(dataset_info['classes_distribution'].items()):
                print(f"   Clase {class_id}: {count} instancias")
        
        # Verificar problemas
        if dataset_info['issues']:
            print(f"⚠️  Problemas encontrados:")
            for issue in dataset_info['issues'][:5]:  # Mostrar solo los primeros 5
                print(f"   - {issue}")
        
        # Recomendaciones
        if total_images < 100:
            print(f"🚨 ADVERTENCIA: Dataset muy pequeño ({total_images} imágenes)")
            print(f"   Recomendado: Mínimo 200-500 imágenes para entrenamiento efectivo")
        
        if total_images != total_labels:
            print(f"⚠️  Desbalance: {total_images} imágenes vs {total_labels} etiquetas")
        
        return dataset_info
    
    def train_model(self, model_type, custom_config=None):
        """Entrena un modelo con configuración optimizada"""
        
        print(f"\n🏋️ ENTRENANDO MODELO: {model_type.upper()}")
        print("=" * 50)
        
        if model_type not in self.training_configs:
            print(f"❌ Tipo de modelo no soportado: {model_type}")
            return None
        
        config = self.training_configs[model_type].copy()
        if custom_config:
            config.update(custom_config)
        
        # Verificar dataset
        dataset_info = self.analyze_dataset_quality(config['data'])
        if not dataset_info:
            return None
        
        try:
            # Cargar modelo
            print(f"📦 Cargando modelo: {config['model']}")
            model = YOLO(config['model'])
            
            # Mostrar configuración
            print(f"⚙️  Configuración:")
            print(f"   Épocas: {config['epochs']}")
            print(f"   Batch size: {config['batch']}")
            print(f"   Dispositivo: {config['device']}")
            print(f"   Learning rate: {config['lr0']}")
            
            # Entrenar
            start_time = time.time()
            print(f"\n🚀 Iniciando entrenamiento...")
            
            results = model.train(**config)
            
            training_time = time.time() - start_time
            
            print(f"\n✅ ENTRENAMIENTO COMPLETADO")
            print(f"⏱️  Tiempo total: {training_time/60:.1f} minutos")
            print(f"📁 Modelo guardado en: {config['project']}/{config['name']}")
            
            # Guardar métricas
            self.results[model_type] = {
                'training_time': training_time,
                'config': config,
                'dataset_info': dataset_info,
                'model_path': f"{config['project']}/{config['name']}/weights/best.pt"
            }
            
            return results
            
        except Exception as e:
            print(f"❌ Error durante el entrenamiento: {e}")
            return None
    
    def evaluate_model(self, model_path, test_data_path=None):
        """Evalúa un modelo entrenado"""
        
        print(f"\n🧪 EVALUANDO MODELO: {model_path}")
        print("=" * 50)
        
        if not os.path.exists(model_path):
            print(f"❌ Modelo no encontrado: {model_path}")
            return None
        
        try:
            model = YOLO(model_path)
            
            # Evaluación en dataset de validación
            if test_data_path:
                results = model.val(data=test_data_path, split='val')
            else:
                # Usar dataset por defecto
                results = model.val()
            
            # Mostrar métricas
            print(f"📊 MÉTRICAS DE RENDIMIENTO:")
            print(f"   mAP@0.5: {results.box.map50:.3f}")
            print(f"   mAP@0.5:0.95: {results.box.map:.3f}")
            print(f"   Precisión: {results.box.mp:.3f}")
            print(f"   Recall: {results.box.mr:.3f}")
            
            # Evaluar por clase
            if hasattr(results.box, 'maps'):
                print(f"\n📈 MÉTRICAS POR CLASE:")
                for i, (class_name, map_score) in enumerate(zip(model.names.values(), results.box.maps)):
                    print(f"   {class_name}: {map_score:.3f}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error durante la evaluación: {e}")
            return None
    
    def create_training_report(self):
        """Crea un reporte detallado del entrenamiento"""
        
        report_path = Path("training_report.json")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.check_system_requirements(),
            'training_results': self.results,
            'recommendations': self.generate_recommendations()
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte guardado: {report_path}")
        return report
    
    def generate_recommendations(self):
        """Genera recomendaciones basadas en los resultados"""
        
        recommendations = []
        
        # Verificar métricas de rendimiento
        for model_type, result in self.results.items():
            if 'evaluation' in result:
                mAP = result['evaluation'].box.map50
                if mAP < 0.3:
                    recommendations.append(f"🚨 Modelo {model_type}: mAP muy bajo ({mAP:.3f}) - Necesita más datos")
                elif mAP < 0.5:
                    recommendations.append(f"⚠️  Modelo {model_type}: mAP moderado ({mAP:.3f}) - Considera más épocas")
                else:
                    recommendations.append(f"✅ Modelo {model_type}: mAP bueno ({mAP:.3f})")
        
        # Verificar tamaño de datasets
        for model_type, result in self.results.items():
            if 'dataset_info' in result:
                total_images = sum(result['dataset_info']['images'].values())
                if total_images < 200:
                    recommendations.append(f"📊 Dataset {model_type}: Solo {total_images} imágenes - Recolecta más datos")
        
        return recommendations

def main():
    """Función principal"""
    
    print("🚀 SISTEMA DE ENTRENAMIENTO MEJORADO")
    print("=" * 60)
    
    trainer = ImprovedTrainingSystem()
    
    # Verificar sistema
    system_info = trainer.check_system_requirements()
    
    # Entrenar modelos
    print(f"\n🎯 SELECCIONAR MODELOS A ENTRENAR:")
    print("1. DNI")
    print("2. Facturas")
    print("3. Ambos")
    
    choice = input("Selecciona opción (1-3): ").strip()
    
    if choice in ['1', '3']:
        trainer.train_model('dni')
    
    if choice in ['2', '3']:
        trainer.train_model('invoices')
    
    # Crear reporte
    trainer.create_training_report()
    
    print(f"\n🎉 ENTRENAMIENTO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
