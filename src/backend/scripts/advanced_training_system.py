#!/usr/bin/env python3
"""
Sistema de entrenamiento avanzado con monitoreo en tiempo real,
optimización automática y mejores prácticas
"""

import os
import time
import json
import torch
import psutil
import wandb
from pathlib import Path
from ultralytics import YOLO
import yaml
import cv2
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List, Optional, Tuple
import optuna
from sklearn.model_selection import KFold

class AdvancedTrainingSystem:
    """Sistema de entrenamiento avanzado con optimizaciones"""
    
    def __init__(self, use_wandb: bool = True, wandb_project: str = "ocr-document-detection"):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.results = {}
        self.use_wandb = use_wandb
        self.wandb_project = wandb_project
        self.training_configs = self.load_advanced_configs()
        
        # Inicializar wandb si está habilitado
        if self.use_wandb:
            try:
                wandb.login()
                print("✅ Wandb inicializado correctamente")
            except Exception as e:
                print(f"⚠️ No se pudo inicializar wandb: {e}")
                self.use_wandb = False
        
    def load_advanced_configs(self) -> Dict:
        """Configuraciones avanzadas optimizadas para documentos"""
        
        return {
            'dni': {
                'model': 'yolov8n.pt',
                'data': 'datasets/dni_robust/dataset.yaml',
                'epochs': 300,
                'imgsz': 640,
                'batch': 16 if self.device == 'cuda' else 8,
                'device': self.device,
                'patience': 50,
                'save': True,
                'project': 'models/yolo_models',
                'name': 'dni_advanced_v3',
                'exist_ok': True,
                'pretrained': True,
                
                # Optimizador avanzado
                'optimizer': 'AdamW',
                'lr0': 0.001,
                'lrf': 0.01,
                'momentum': 0.937,
                'weight_decay': 0.0005,
                'warmup_epochs': 10,
                'warmup_momentum': 0.8,
                'warmup_bias_lr': 0.1,
                
                # Loss weights optimizados
                'box': 7.5,
                'cls': 0.5,
                'dfl': 1.5,
                
                # Augmentaciones específicas para DNI
                'hsv_h': 0.01,
                'hsv_s': 0.3,
                'hsv_v': 0.2,
                'degrees': 0.0,  # DNI no se rotan
                'translate': 0.02,
                'scale': 0.1,
                'shear': 0.0,
                'perspective': 0.0,
                'flipud': 0.0,
                'fliplr': 0.0,
                'mosaic': 1.0,
                'mixup': 0.0,
                'copy_paste': 0.0,
                'auto_augment': 'randaugment',
                'erasing': 0.1,
                
                # Configuración avanzada
                'workers': 8 if self.device == 'cuda' else 4,
                'amp': True,  # Mixed precision
                'fraction': 1.0,
                'close_mosaic': 10,
                'resume': False,
                'seed': 42,
                'deterministic': True,
                'single_cls': False,
                'rect': False,
                'cos_lr': True,
                'overlap_mask': True,
                'mask_ratio': 4,
                'dropout': 0.0,
                'val': True,
                'plots': True,
                'save_json': True,
                'save_hybrid': False,
                'conf': None,
                'iou': 0.7,
                'max_det': 300,
                'half': False,
                'dnn': False,
                'vid_stride': 1,
                'stream_buffer': False,
                'visualize': False,
                'augment': True,
                'agnostic_nms': False,
                'retina_masks': False,
                'format': 'torchscript',
                'keras': False,
                'optimize': False,
                'int8': False,
                'dynamic': False,
                'simplify': False,
                'opset': None,
                'workspace': 4,
                'nms': False,
                'lr_scheduler': 'cosine',
                'cos_lr_epochs': 50,
                'cos_lr_eta_min': 0.0001,
                'label_smoothing': 0.0,
                'bbox_interval': -1,
                'nbs': 64,
                'hsv_h': 0.015,
                'hsv_s': 0.7,
                'hsv_v': 0.4,
                'cache': False,
                'image_weights': False,
                'multi_scale': False,
                'single_cls': False,
                'rect': False,
                'pad': 0.0,
                'min_items': 0,
                'cfg': None,
                'data': None,
                'hyp': None,
                'epochs': 300,
                'batch': 16,
                'imgsz': 640,
                'patience': 50,
                'save': True,
                'save_period': -1,
                'cache': False,
                'device': '',
                'workers': 8,
                'project': 'runs/detect',
                'name': 'exp',
                'exist_ok': False,
                'pretrained': True,
                'optimizer': 'auto',
                'verbose': True,
                'seed': 0,
                'deterministic': True,
                'single_cls': False,
                'rect': False,
                'cos_lr': False,
                'close_mosaic': 10,
                'resume': False,
                'amp': True,
                'fraction': 1.0,
                'profile': False,
                'freeze': None,
                'multi_scale': False,
                'overlap_mask': True,
                'mask_ratio': 4,
                'dropout': 0.0,
                'val': True,
                'plots': True,
                'save_json': False,
                'save_hybrid': False,
                'conf': None,
                'iou': 0.7,
                'max_det': 300,
                'half': False,
                'dnn': False,
                'vid_stride': 1,
                'stream_buffer': False,
                'visualize': False,
                'augment': False,
                'agnostic_nms': False,
                'retina_masks': False,
                'format': 'torchscript',
                'keras': False,
                'optimize': False,
                'int8': False,
                'dynamic': False,
                'simplify': False,
                'opset': None,
                'workspace': 4,
                'nms': False,
                'batch': 16,
                'imgsz': 640,
                'conf': None,
                'iou': 0.7,
                'max_det': 300,
                'half': False,
                'dnn': False,
                'vid_stride': 1,
                'stream_buffer': False,
                'visualize': False,
                'augment': False,
                'agnostic_nms': False,
                'retina_masks': False,
                'format': 'torchscript',
                'keras': False,
                'optimize': False,
                'int8': False,
                'dynamic': False,
                'simplify': False,
                'opset': None,
                'workspace': 4,
                'nms': False
            },
            'invoices': {
                'model': 'yolov8n.pt',
                'data': 'yolo/dataset_argentina.yaml',
                'epochs': 400,
                'imgsz': 640,
                'batch': 12 if self.device == 'cuda' else 6,
                'device': self.device,
                'patience': 60,
                'save': True,
                'project': 'models/yolo_models',
                'name': 'invoices_advanced_v3',
                'exist_ok': True,
                'pretrained': True,
                
                # Optimizador avanzado
                'optimizer': 'AdamW',
                'lr0': 0.0008,
                'lrf': 0.01,
                'momentum': 0.937,
                'weight_decay': 0.0005,
                'warmup_epochs': 15,
                'warmup_momentum': 0.8,
                'warmup_bias_lr': 0.1,
                
                # Loss weights optimizados
                'box': 7.5,
                'cls': 0.5,
                'dfl': 1.5,
                
                # Augmentaciones específicas para facturas
                'hsv_h': 0.02,
                'hsv_s': 0.8,
                'hsv_v': 0.5,
                'degrees': 3.0,
                'translate': 0.15,
                'scale': 0.4,
                'shear': 2.0,
                'perspective': 0.0,
                'flipud': 0.0,
                'fliplr': 0.0,
                'mosaic': 1.0,
                'mixup': 0.15,
                'copy_paste': 0.0,
                'auto_augment': 'randaugment',
                'erasing': 0.4,
                
                # Configuración avanzada
                'workers': 8 if self.device == 'cuda' else 4,
                'amp': True,
                'fraction': 1.0,
                'close_mosaic': 15,
                'resume': False,
                'seed': 42,
                'deterministic': True,
                'single_cls': False,
                'rect': False,
                'cos_lr': True,
                'overlap_mask': True,
                'mask_ratio': 4,
                'dropout': 0.0,
                'val': True,
                'plots': True,
                'save_json': True,
                'save_hybrid': False,
                'conf': None,
                'iou': 0.7,
                'max_det': 300,
                'half': False,
                'dnn': False,
                'vid_stride': 1,
                'stream_buffer': False,
                'visualize': False,
                'augment': True,
                'agnostic_nms': False,
                'retina_masks': False,
                'format': 'torchscript',
                'keras': False,
                'optimize': False,
                'int8': False,
                'dynamic': False,
                'simplify': False,
                'opset': None,
                'workspace': 4,
                'nms': False,
                'lr_scheduler': 'cosine',
                'cos_lr_epochs': 75,
                'cos_lr_eta_min': 0.00005,
                'label_smoothing': 0.05,
                'bbox_interval': -1,
                'nbs': 64,
                'cache': False,
                'image_weights': False,
                'multi_scale': False,
                'single_cls': False,
                'rect': False,
                'pad': 0.0,
                'min_items': 0,
                'cfg': None,
                'data': None,
                'hyp': None,
                'epochs': 400,
                'batch': 12,
                'imgsz': 640,
                'patience': 60,
                'save': True,
                'save_period': -1,
                'cache': False,
                'device': '',
                'workers': 8,
                'project': 'runs/detect',
                'name': 'exp',
                'exist_ok': False,
                'pretrained': True,
                'optimizer': 'auto',
                'verbose': True,
                'seed': 0,
                'deterministic': True,
                'single_cls': False,
                'rect': False,
                'cos_lr': False,
                'close_mosaic': 15,
                'resume': False,
                'amp': True,
                'fraction': 1.0,
                'profile': False,
                'freeze': None,
                'multi_scale': False,
                'overlap_mask': True,
                'mask_ratio': 4,
                'dropout': 0.0,
                'val': True,
                'plots': True,
                'save_json': False,
                'save_hybrid': False,
                'conf': None,
                'iou': 0.7,
                'max_det': 300,
                'half': False,
                'dnn': False,
                'vid_stride': 1,
                'stream_buffer': False,
                'visualize': False,
                'augment': False,
                'agnostic_nms': False,
                'retina_masks': False,
                'format': 'torchscript',
                'keras': False,
                'optimize': False,
                'int8': False,
                'dynamic': False,
                'simplify': False,
                'opset': None,
                'workspace': 4,
                'nms': False,
                'batch': 12,
                'imgsz': 640,
                'conf': None,
                'iou': 0.7,
                'max_det': 300,
                'half': False,
                'dnn': False,
                'vid_stride': 1,
                'stream_buffer': False,
                'visualize': False,
                'augment': False,
                'agnostic_nms': False,
                'retina_masks': False,
                'format': 'torchscript',
                'keras': False,
                'optimize': False,
                'int8': False,
                'dynamic': False,
                'simplify': False,
                'opset': None,
                'workspace': 4,
                'nms': False
            }
        }
    
    def setup_wandb(self, model_type: str, config: Dict):
        """Configura Weights & Biases para monitoreo"""
        if not self.use_wandb:
            return None
            
        run_name = f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        wandb.init(
            project=self.wandb_project,
            name=run_name,
            config=config,
            tags=[model_type, "yolo", "document-detection"]
        )
        
        return wandb
    
    def hyperparameter_optimization(self, model_type: str, n_trials: int = 20) -> Dict:
        """Optimización automática de hiperparámetros usando Optuna"""
        
        def objective(trial):
            # Sugerir hiperparámetros
            lr0 = trial.suggest_float('lr0', 1e-5, 1e-2, log=True)
            weight_decay = trial.suggest_float('weight_decay', 1e-5, 1e-2, log=True)
            batch_size = trial.suggest_categorical('batch', [8, 16, 32])
            warmup_epochs = trial.suggest_int('warmup_epochs', 3, 20)
            
            config = self.training_configs[model_type].copy()
            config.update({
                'lr0': lr0,
                'weight_decay': weight_decay,
                'batch': batch_size,
                'warmup_epochs': warmup_epochs,
                'epochs': 50,  # Menos epochs para optimización
                'name': f'{model_type}_trial_{trial.number}',
                'verbose': False
            })
            
            try:
                model = YOLO(config['model'])
                results = model.train(**config)
                
                # Retornar mAP como métrica a maximizar
                return results.results_dict.get('metrics/mAP50-95', 0.0)
                
            except Exception as e:
                print(f"Error en trial {trial.number}: {e}")
                return 0.0
        
        print(f"🔍 Optimizando hiperparámetros para {model_type}...")
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials)
        
        best_params = study.best_params
        print(f"✅ Mejores hiperparámetros encontrados:")
        for param, value in best_params.items():
            print(f"   {param}: {value}")
        
        # Actualizar configuración con mejores parámetros
        self.training_configs[model_type].update(best_params)
        
        return best_params
    
    def cross_validation(self, model_type: str, n_folds: int = 5) -> Dict:
        """Validación cruzada para evaluar robustez del modelo"""
        
        print(f"🔄 Ejecutando validación cruzada ({n_folds} folds) para {model_type}")
        
        dataset_path = Path(self.training_configs[model_type]['data'])
        images_dir = dataset_path.parent / 'images' / 'train'
        labels_dir = dataset_path.parent / 'labels' / 'train'
        
        # Obtener todas las imágenes
        images = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
        
        if len(images) < n_folds:
            print(f"⚠️ No hay suficientes imágenes para {n_folds} folds")
            return {}
        
        # Crear splits para validación cruzada
        kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
        cv_results = []
        
        for fold, (train_idx, val_idx) in enumerate(kf.split(images)):
            print(f"📊 Fold {fold + 1}/{n_folds}")
            
            # Crear directorios temporales para este fold
            temp_dataset = Path(f"temp_cv_dataset_fold_{fold}")
            temp_dataset.mkdir(exist_ok=True)
            
            # Crear splits temporales
            (temp_dataset / 'images' / 'train').mkdir(parents=True)
            (temp_dataset / 'images' / 'val').mkdir(parents=True)
            (temp_dataset / 'labels' / 'train').mkdir(parents=True)
            (temp_dataset / 'labels' / 'val').mkdir(parents=True)
            
            # Copiar archivos de entrenamiento
            for idx in train_idx:
                img = images[idx]
                label = labels_dir / f"{img.stem}.txt"
                
                img.copy(temp_dataset / 'images' / 'train' / img.name)
                if label.exists():
                    label.copy(temp_dataset / 'labels' / 'train' / label.name)
            
            # Copiar archivos de validación
            for idx in val_idx:
                img = images[idx]
                label = labels_dir / f"{img.stem}.txt"
                
                img.copy(temp_dataset / 'images' / 'val' / img.name)
                if label.exists():
                    label.copy(temp_dataset / 'labels' / 'val' / label.name)
            
            # Crear dataset.yaml temporal
            yaml_content = f"""train: {temp_dataset / 'images' / 'train'}
val: {temp_dataset / 'images' / 'val'}
nc: {self.training_configs[model_type].get('nc', 8)}
names: {self.training_configs[model_type].get('names', [])}
"""
            (temp_dataset / 'dataset.yaml').write_text(yaml_content)
            
            # Entrenar modelo para este fold
            config = self.training_configs[model_type].copy()
            config.update({
                'data': str(temp_dataset / 'dataset.yaml'),
                'epochs': 100,  # Menos epochs para CV
                'name': f'{model_type}_cv_fold_{fold}',
                'verbose': False
            })
            
            try:
                model = YOLO(config['model'])
                results = model.train(**config)
                
                cv_results.append({
                    'fold': fold,
                    'mAP50': results.results_dict.get('metrics/mAP50', 0.0),
                    'mAP50-95': results.results_dict.get('metrics/mAP50-95', 0.0),
                    'precision': results.results_dict.get('metrics/precision', 0.0),
                    'recall': results.results_dict.get('metrics/recall', 0.0)
                })
                
            except Exception as e:
                print(f"❌ Error en fold {fold}: {e}")
                cv_results.append({'fold': fold, 'error': str(e)})
            
            # Limpiar directorio temporal
            import shutil
            shutil.rmtree(temp_dataset)
        
        # Calcular estadísticas de CV
        valid_results = [r for r in cv_results if 'error' not in r]
        if valid_results:
            cv_stats = {
                'mean_mAP50': np.mean([r['mAP50'] for r in valid_results]),
                'std_mAP50': np.std([r['mAP50'] for r in valid_results]),
                'mean_mAP50-95': np.mean([r['mAP50-95'] for r in valid_results]),
                'std_mAP50-95': np.std([r['mAP50-95'] for r in valid_results]),
                'mean_precision': np.mean([r['precision'] for r in valid_results]),
                'std_precision': np.std([r['precision'] for r in valid_results]),
                'mean_recall': np.mean([r['recall'] for r in valid_results]),
                'std_recall': np.std([r['recall'] for r in valid_results])
            }
            
            print(f"📊 RESULTADOS DE VALIDACIÓN CRUZADA:")
            print(f"   mAP@0.5: {cv_stats['mean_mAP50']:.3f} ± {cv_stats['std_mAP50']:.3f}")
            print(f"   mAP@0.5:0.95: {cv_stats['mean_mAP50-95']:.3f} ± {cv_stats['std_mAP50-95']:.3f}")
            print(f"   Precisión: {cv_stats['mean_precision']:.3f} ± {cv_stats['std_precision']:.3f}")
            print(f"   Recall: {cv_stats['mean_recall']:.3f} ± {cv_stats['std_recall']:.3f}")
            
            return cv_stats
        
        return {}
    
    def train_model_advanced(self, model_type: str, use_hyperopt: bool = False, 
                           use_cv: bool = False, custom_config: Optional[Dict] = None) -> Dict:
        """Entrena modelo con configuraciones avanzadas"""
        
        print(f"\n🚀 ENTRENAMIENTO AVANZADO: {model_type.upper()}")
        print("=" * 60)
        
        if model_type not in self.training_configs:
            print(f"❌ Tipo de modelo no soportado: {model_type}")
            return {}
        
        config = self.training_configs[model_type].copy()
        if custom_config:
            config.update(custom_config)
        
        # Optimización de hiperparámetros si se solicita
        if use_hyperopt:
            best_params = self.hyperparameter_optimization(model_type)
            config.update(best_params)
        
        # Validación cruzada si se solicita
        cv_results = {}
        if use_cv:
            cv_results = self.cross_validation(model_type)
        
        # Configurar wandb
        wandb_run = self.setup_wandb(model_type, config)
        
        try:
            # Verificar dataset
            dataset_info = self.analyze_dataset_quality(config['data'])
            if not dataset_info:
                return {}
            
            # Cargar modelo
            print(f"📦 Cargando modelo: {config['model']}")
            model = YOLO(config['model'])
            
            # Mostrar configuración
            print(f"⚙️ Configuración avanzada:")
            print(f"   Épocas: {config['epochs']}")
            print(f"   Batch size: {config['batch']}")
            print(f"   Learning rate: {config['lr0']}")
            print(f"   Optimizador: {config['optimizer']}")
            print(f"   Mixed precision: {config.get('amp', False)}")
            print(f"   Cosine LR: {config.get('cos_lr', False)}")
            
            # Entrenar
            start_time = time.time()
            print(f"\n🏋️ Iniciando entrenamiento avanzado...")
            
            results = model.train(**config)
            
            training_time = time.time() - start_time
            
            print(f"\n✅ ENTRENAMIENTO AVANZADO COMPLETADO")
            print(f"⏱️ Tiempo total: {training_time/60:.1f} minutos")
            print(f"📁 Modelo guardado en: {config['project']}/{config['name']}")
            
            # Guardar métricas
            training_results = {
                'training_time': training_time,
                'config': config,
                'dataset_info': dataset_info,
                'model_path': f"{config['project']}/{config['name']}/weights/best.pt",
                'cv_results': cv_results,
                'final_metrics': results.results_dict if hasattr(results, 'results_dict') else {}
            }
            
            self.results[model_type] = training_results
            
            # Log a wandb si está disponible
            if wandb_run:
                wandb.log({
                    'training_time_minutes': training_time / 60,
                    'final_mAP50': results.results_dict.get('metrics/mAP50', 0.0),
                    'final_mAP50-95': results.results_dict.get('metrics/mAP50-95', 0.0),
                    'final_precision': results.results_dict.get('metrics/precision', 0.0),
                    'final_recall': results.results_dict.get('metrics/recall', 0.0)
                })
                wandb.finish()
            
            return training_results
            
        except Exception as e:
            print(f"❌ Error durante el entrenamiento: {e}")
            if wandb_run:
                wandb.finish()
            return {}
    
    def analyze_dataset_quality(self, dataset_path: str) -> Optional[Dict]:
        """Análisis avanzado de calidad del dataset"""
        
        print(f"\n📊 ANÁLISIS AVANZADO DEL DATASET: {dataset_path}")
        print("=" * 60)
        
        dataset_info = {
            'images': {'train': 0, 'val': 0, 'test': 0},
            'labels': {'train': 0, 'val': 0, 'test': 0},
            'total_size_mb': 0,
            'classes_distribution': {},
            'issues': [],
            'quality_metrics': {}
        }
        
        dataset_dir = Path(dataset_path)
        
        if not dataset_dir.exists():
            print(f"❌ Dataset no encontrado: {dataset_path}")
            return None
        
        # Cargar configuración del dataset
        yaml_path = dataset_dir if dataset_dir.suffix == '.yaml' else dataset_dir / 'dataset.yaml'
        if yaml_path.exists():
            with open(yaml_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
                dataset_info['config'] = yaml_config
        
        # Análisis detallado por split
        for split in ['train', 'val', 'test']:
            images_dir = dataset_dir.parent / 'images' / split if dataset_dir.suffix == '.yaml' else dataset_dir / 'images' / split
            labels_dir = dataset_dir.parent / 'labels' / split if dataset_dir.suffix == '.yaml' else dataset_dir / 'labels' / split
            
            if images_dir.exists():
                images = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
                dataset_info['images'][split] = len(images)
                
                # Análisis de calidad de imágenes
                image_qualities = []
                for img_path in images[:10]:  # Muestra de 10 imágenes
                    try:
                        img = cv2.imread(str(img_path))
                        if img is not None:
                            # Calcular métricas de calidad
                            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                            brightness = np.mean(gray)
                            contrast = np.std(gray)
                            
                            image_qualities.append({
                                'file': img_path.name,
                                'laplacian_var': laplacian_var,
                                'brightness': brightness,
                                'contrast': contrast,
                                'size': img.shape
                            })
                        else:
                            dataset_info['issues'].append(f"Imagen corrupta: {img_path.name}")
                    except Exception as e:
                        dataset_info['issues'].append(f"Error leyendo {img_path.name}: {e}")
                
                if image_qualities:
                    dataset_info['quality_metrics'][split] = {
                        'avg_laplacian_var': np.mean([q['laplacian_var'] for q in image_qualities]),
                        'avg_brightness': np.mean([q['brightness'] for q in image_qualities]),
                        'avg_contrast': np.mean([q['contrast'] for q in image_qualities]),
                        'image_sizes': [q['size'] for q in image_qualities]
                    }
            
            if labels_dir.exists():
                labels = list(labels_dir.glob('*.txt'))
                dataset_info['labels'][split] = len(labels)
                
                # Análisis de distribución de clases
                for label_path in labels:
                    try:
                        with open(label_path, 'r') as f:
                            for line in f:
                                if line.strip():
                                    parts = line.strip().split()
                                    if len(parts) >= 5:
                                        class_id = int(parts[0])
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
        print(f"🏷️ Etiquetas: {total_labels} (Train: {dataset_info['labels']['train']}, Val: {dataset_info['labels']['val']}, Test: {dataset_info['labels']['test']})")
        print(f"💾 Tamaño: {dataset_info['total_size_mb']:.1f} MB")
        
        # Mostrar métricas de calidad
        for split, metrics in dataset_info['quality_metrics'].items():
            print(f"🔍 Calidad {split}:")
            print(f"   Claridad (Laplacian): {metrics['avg_laplacian_var']:.1f}")
            print(f"   Brillo promedio: {metrics['avg_brightness']:.1f}")
            print(f"   Contraste promedio: {metrics['avg_contrast']:.1f}")
        
        # Verificar balance de clases
        if dataset_info['classes_distribution']:
            print(f"📊 Distribución de clases:")
            total_instances = sum(dataset_info['classes_distribution'].values())
            for class_id, count in sorted(dataset_info['classes_distribution'].items()):
                percentage = (count / total_instances) * 100
                print(f"   Clase {class_id}: {count} instancias ({percentage:.1f}%)")
                
                # Verificar desbalance
                if percentage < 5:
                    dataset_info['issues'].append(f"Clase {class_id} muy poco representada ({percentage:.1f}%)")
        
        # Verificar problemas
        if dataset_info['issues']:
            print(f"⚠️ Problemas encontrados:")
            for issue in dataset_info['issues'][:5]:
                print(f"   - {issue}")
        
        # Recomendaciones
        if total_images < 200:
            print(f"🚨 ADVERTENCIA: Dataset pequeño ({total_images} imágenes)")
            print(f"   Recomendado: Mínimo 500-1000 imágenes para entrenamiento robusto")
        
        if total_images != total_labels:
            print(f"⚠️ Desbalance: {total_images} imágenes vs {total_labels} etiquetas")
        
        return dataset_info
    
    def create_advanced_report(self):
        """Crea reporte avanzado con visualizaciones"""
        
        report_path = Path("advanced_training_report.json")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.get_system_info(),
            'training_results': self.results,
            'recommendations': self.generate_advanced_recommendations()
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte avanzado guardado: {report_path}")
        
        # Crear visualizaciones
        self.create_training_visualizations()
        
        return report
    
    def get_system_info(self) -> Dict:
        """Obtiene información detallada del sistema"""
        
        info = {
            'device': self.device,
            'cuda_available': torch.cuda.is_available(),
            'cuda_version': torch.version.cuda if torch.cuda.is_available() else None,
            'pytorch_version': torch.__version__,
            'python_version': sys.version,
            'memory': psutil.virtual_memory()._asdict(),
            'cpu_count': psutil.cpu_count(),
            'disk_usage': psutil.disk_usage('.')._asdict()
        }
        
        if torch.cuda.is_available():
            info['gpu_info'] = {
                'name': torch.cuda.get_device_name(0),
                'memory_total': torch.cuda.get_device_properties(0).total_memory,
                'memory_allocated': torch.cuda.memory_allocated(0),
                'memory_reserved': torch.cuda.memory_reserved(0)
            }
        
        return info
    
    def generate_advanced_recommendations(self) -> List[str]:
        """Genera recomendaciones avanzadas basadas en los resultados"""
        
        recommendations = []
        
        # Verificar métricas de rendimiento
        for model_type, result in self.results.items():
            if 'final_metrics' in result and result['final_metrics']:
                mAP50 = result['final_metrics'].get('metrics/mAP50', 0.0)
                mAP50_95 = result['final_metrics'].get('metrics/mAP50-95', 0.0)
                
                if mAP50 < 0.3:
                    recommendations.append(f"🚨 Modelo {model_type}: mAP@0.5 muy bajo ({mAP50:.3f}) - Necesita más datos o mejor preprocesamiento")
                elif mAP50 < 0.5:
                    recommendations.append(f"⚠️ Modelo {model_type}: mAP@0.5 moderado ({mAP50:.3f}) - Considera más épocas o data augmentation")
                else:
                    recommendations.append(f"✅ Modelo {model_type}: mAP@0.5 bueno ({mAP50:.3f})")
                
                if mAP50_95 < 0.2:
                    recommendations.append(f"📊 Modelo {model_type}: mAP@0.5:0.95 bajo ({mAP50_95:.3f}) - Mejora la precisión de localización")
        
        # Verificar tiempo de entrenamiento
        for model_type, result in self.results.items():
            training_time = result.get('training_time', 0)
            if training_time > 3600:  # Más de 1 hora
                recommendations.append(f"⏱️ Modelo {model_type}: Entrenamiento lento ({training_time/60:.1f} min) - Considera usar GPU o reducir batch size")
        
        # Verificar tamaño de datasets
        for model_type, result in self.results.items():
            if 'dataset_info' in result:
                total_images = sum(result['dataset_info']['images'].values())
                if total_images < 500:
                    recommendations.append(f"📊 Dataset {model_type}: Solo {total_images} imágenes - Recolecta más datos para mejor generalización")
        
        return recommendations
    
    def create_training_visualizations(self):
        """Crea visualizaciones de los resultados de entrenamiento"""
        
        for model_type, result in self.results.items():
            if 'final_metrics' not in result:
                continue
            
            # Crear gráfico de métricas
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Métricas de Entrenamiento - {model_type.upper()}', fontsize=16)
            
            # Aquí podrías agregar más visualizaciones específicas
            # Por ahora, creamos un gráfico simple
            
            plt.tight_layout()
            plt.savefig(f"training_metrics_{model_type}.png", dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 Visualizaciones guardadas: training_metrics_{model_type}.png")

def main():
    """Función principal"""
    
    print("🚀 SISTEMA DE ENTRENAMIENTO AVANZADO")
    print("=" * 60)
    
    trainer = AdvancedTrainingSystem(use_wandb=True)
    
    # Verificar sistema
    system_info = trainer.get_system_info()
    print(f"💻 Sistema: {system_info['device']}")
    if system_info['cuda_available']:
        print(f"🎮 GPU: {system_info['gpu_info']['name']}")
    
    # Seleccionar opciones
    print(f"\n🎯 OPCIONES DE ENTRENAMIENTO:")
    print("1. DNI básico")
    print("2. Facturas básico")
    print("3. DNI con optimización de hiperparámetros")
    print("4. Facturas con validación cruzada")
    print("5. Ambos modelos con todas las optimizaciones")
    
    choice = input("Selecciona opción (1-5): ").strip()
    
    if choice in ['1', '3', '5']:
        use_hyperopt = choice in ['3', '5']
        use_cv = choice == '5'
        trainer.train_model_advanced('dni', use_hyperopt=use_hyperopt, use_cv=use_cv)
    
    if choice in ['2', '4', '5']:
        use_hyperopt = choice in ['4', '5']
        use_cv = choice == '5'
        trainer.train_model_advanced('invoices', use_hyperopt=use_hyperopt, use_cv=use_cv)
    
    # Crear reporte avanzado
    trainer.create_advanced_report()
    
    print(f"\n🎉 ENTRENAMIENTO AVANZADO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
