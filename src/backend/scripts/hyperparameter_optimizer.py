#!/usr/bin/env python3
"""
Optimizador automático de hiperparámetros para modelos YOLO
Utiliza Optuna para encontrar la mejor configuración
"""

import os
import time
import json
import torch
import optuna
from pathlib import Path
from ultralytics import YOLO
import yaml
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class HyperparameterOptimizer:
    """Optimizador de hiperparámetros usando Optuna"""
    
    def __init__(self, model_type: str, n_trials: int = 50):
        self.model_type = model_type
        self.n_trials = n_trials
        self.study = None
        self.best_params = None
        self.trial_results = []
        
        # Configuraciones base por tipo de modelo
        self.base_configs = {
            'dni': {
                'model': 'yolov8n.pt',
                'data': 'datasets/dni_robust/dataset.yaml',
                'epochs': 100,  # Menos epochs para optimización
                'imgsz': 640,
                'device': 'cuda' if torch.cuda.is_available() else 'cpu',
                'project': 'models/yolo_models',
                'exist_ok': True,
                'pretrained': True,
                'verbose': False,
                'save': False,  # No guardar modelos durante optimización
                'plots': False,
                'val': True,
                'workers': 4,
                'seed': 42,
                'deterministic': True
            },
            'invoices': {
                'model': 'yolov8n.pt',
                'data': 'yolo/dataset_argentina.yaml',
                'epochs': 100,
                'imgsz': 640,
                'device': 'cuda' if torch.cuda.is_available() else 'cpu',
                'project': 'models/yolo_models',
                'exist_ok': True,
                'pretrained': True,
                'verbose': False,
                'save': False,
                'plots': False,
                'val': True,
                'workers': 4,
                'seed': 42,
                'deterministic': True
            }
        }
    
    def create_objective_function(self):
        """Crea la función objetivo para optimización"""
        
        def objective(trial):
            # Sugerir hiperparámetros
            config = self.base_configs[self.model_type].copy()
            
            # Parámetros principales a optimizar
            config['lr0'] = trial.suggest_float('lr0', 1e-5, 1e-2, log=True)
            config['weight_decay'] = trial.suggest_float('weight_decay', 1e-5, 1e-2, log=True)
            config['momentum'] = trial.suggest_float('momentum', 0.8, 0.98)
            config['warmup_epochs'] = trial.suggest_int('warmup_epochs', 3, 20)
            
            # Batch size
            config['batch'] = trial.suggest_categorical('batch', [8, 16, 32, 64])
            
            # Optimizador
            config['optimizer'] = trial.suggest_categorical('optimizer', ['SGD', 'Adam', 'AdamW', 'RMSProp'])
            
            # Loss weights
            config['box'] = trial.suggest_float('box', 0.5, 10.0)
            config['cls'] = trial.suggest_float('cls', 0.1, 2.0)
            config['dfl'] = trial.suggest_float('dfl', 0.5, 5.0)
            
            # Augmentaciones
            config['hsv_h'] = trial.suggest_float('hsv_h', 0.0, 0.1)
            config['hsv_s'] = trial.suggest_float('hsv_s', 0.0, 1.0)
            config['hsv_v'] = trial.suggest_float('hsv_v', 0.0, 1.0)
            config['degrees'] = trial.suggest_float('degrees', 0.0, 10.0)
            config['translate'] = trial.suggest_float('translate', 0.0, 0.5)
            config['scale'] = trial.suggest_float('scale', 0.0, 1.0)
            config['shear'] = trial.suggest_float('shear', 0.0, 10.0)
            config['perspective'] = trial.suggest_float('perspective', 0.0, 0.001)
            config['flipud'] = trial.suggest_float('flipud', 0.0, 1.0)
            config['fliplr'] = trial.suggest_float('fliplr', 0.0, 1.0)
            config['mosaic'] = trial.suggest_float('mosaic', 0.0, 1.0)
            config['mixup'] = trial.suggest_float('mixup', 0.0, 1.0)
            config['copy_paste'] = trial.suggest_float('copy_paste', 0.0, 1.0)
            
            # Configuraciones específicas por tipo
            if self.model_type == 'dni':
                # DNI: menos rotación, menos cambios de color
                config['degrees'] = trial.suggest_float('degrees', 0.0, 2.0)
                config['hsv_h'] = trial.suggest_float('hsv_h', 0.0, 0.02)
                config['fliplr'] = 0.0  # DNI no se voltean horizontalmente
                config['flipud'] = 0.0
            elif self.model_type == 'invoices':
                # Facturas: más variación permitida
                config['degrees'] = trial.suggest_float('degrees', 0.0, 5.0)
                config['hsv_h'] = trial.suggest_float('hsv_h', 0.0, 0.05)
            
            # Auto augment
            config['auto_augment'] = trial.suggest_categorical('auto_augment', ['randaugment', 'autoaugment', 'trivialaugmentwide'])
            
            # Erasing
            config['erasing'] = trial.suggest_float('erasing', 0.0, 0.5)
            
            # Configurar nombre único para este trial
            config['name'] = f'{self.model_type}_optuna_trial_{trial.number}'
            
            try:
                # Entrenar modelo
                model = YOLO(config['model'])
                results = model.train(**config)
                
                # Obtener métricas
                if hasattr(results, 'results_dict') and results.results_dict:
                    mAP50_95 = results.results_dict.get('metrics/mAP50-95(B)', 0.0)
                    mAP50 = results.results_dict.get('metrics/mAP50(B)', 0.0)
                    
                    # Usar mAP50-95 como métrica principal
                    score = mAP50_95
                    
                    # Penalizar si mAP50 es muy bajo
                    if mAP50 < 0.1:
                        score *= 0.5
                    
                    # Guardar resultados del trial
                    trial_result = {
                        'trial_number': trial.number,
                        'params': config.copy(),
                        'mAP50': mAP50,
                        'mAP50_95': mAP50_95,
                        'score': score,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Remover parámetros no serializables
                    if 'model' in trial_result['params']:
                        del trial_result['params']['model']
                    if 'data' in trial_result['params']:
                        del trial_result['params']['data']
                    if 'device' in trial_result['params']:
                        del trial_result['params']['device']
                    if 'project' in trial_result['params']:
                        del trial_result['params']['project']
                    
                    self.trial_results.append(trial_result)
                    
                    return score
                else:
                    print(f"⚠️ Trial {trial.number}: No se obtuvieron métricas")
                    return 0.0
                    
            except Exception as e:
                print(f"❌ Trial {trial.number} falló: {e}")
                return 0.0
        
        return objective
    
    def optimize(self, direction: str = 'maximize', n_jobs: int = 1):
        """Ejecuta la optimización de hiperparámetros"""
        
        print(f"🔍 OPTIMIZANDO HIPERPARÁMETROS PARA {self.model_type.upper()}")
        print(f"🎯 Objetivo: {direction}")
        print(f"🔄 Número de trials: {self.n_trials}")
        print(f"⚙️ Trabajos paralelos: {n_jobs}")
        print("=" * 60)
        
        # Crear estudio
        self.study = optuna.create_study(
            direction=direction,
            sampler=optuna.samplers.TPESampler(seed=42),
            pruner=optuna.pruners.MedianPruner(
                n_startup_trials=5,
                n_warmup_steps=10,
                interval_steps=10
            )
        )
        
        # Función objetivo
        objective_func = self.create_objective_function()
        
        # Ejecutar optimización
        start_time = time.time()
        
        self.study.optimize(
            objective_func,
            n_trials=self.n_trials,
            n_jobs=n_jobs,
            show_progress_bar=True
        )
        
        optimization_time = time.time() - start_time
        
        # Obtener mejores parámetros
        self.best_params = self.study.best_params.copy()
        
        print(f"\n✅ OPTIMIZACIÓN COMPLETADA")
        print(f"⏱️ Tiempo total: {optimization_time/60:.1f} minutos")
        print(f"🎯 Mejor score: {self.study.best_value:.4f}")
        print(f"📊 Trials completados: {len(self.trial_results)}")
        
        return self.best_params
    
    def get_best_config(self) -> Dict:
        """Obtiene la mejor configuración completa"""
        
        if not self.best_params:
            raise ValueError("No se ha ejecutado la optimización aún")
        
        # Configuración base
        config = self.base_configs[self.model_type].copy()
        
        # Aplicar mejores parámetros
        config.update(self.best_params)
        
        # Configuraciones adicionales para entrenamiento final
        config.update({
            'epochs': 300 if self.model_type == 'dni' else 400,
            'patience': 50,
            'save': True,
            'plots': True,
            'verbose': True,
            'name': f'{self.model_type}_optimized_final',
            'exist_ok': True
        })
        
        return config
    
    def analyze_results(self):
        """Analiza los resultados de la optimización"""
        
        if not self.trial_results:
            print("❌ No hay resultados para analizar")
            return
        
        print(f"\n📊 ANÁLISIS DE RESULTADOS")
        print("=" * 50)
        
        # Convertir a DataFrame para análisis
        df = pd.DataFrame(self.trial_results)
        
        # Estadísticas básicas
        print(f"📈 Estadísticas de Score:")
        print(f"   Mejor: {df['score'].max():.4f}")
        print(f"   Promedio: {df['score'].mean():.4f}")
        print(f"   Desviación: {df['score'].std():.4f}")
        print(f"   Mediana: {df['score'].median():.4f}")
        
        # Top 5 trials
        top_trials = df.nlargest(5, 'score')
        print(f"\n🏆 TOP 5 TRIALS:")
        for _, trial in top_trials.iterrows():
            print(f"   Trial {trial['trial_number']}: Score {trial['score']:.4f} (mAP50-95: {trial['mAP50_95']:.3f})")
        
        # Análisis de parámetros importantes
        self._analyze_parameter_importance(df)
        
        # Crear visualizaciones
        self._create_optimization_plots(df)
        
        return df
    
    def _analyze_parameter_importance(self, df: pd.DataFrame):
        """Analiza la importancia de los parámetros"""
        
        print(f"\n🔍 IMPORTANCIA DE PARÁMETROS:")
        
        # Parámetros numéricos a analizar
        numeric_params = [
            'lr0', 'weight_decay', 'momentum', 'warmup_epochs', 'batch',
            'box', 'cls', 'dfl', 'hsv_h', 'hsv_s', 'hsv_v', 'degrees',
            'translate', 'scale', 'shear', 'mosaic', 'mixup', 'erasing'
        ]
        
        correlations = {}
        for param in numeric_params:
            if param in df.columns:
                # Extraer valores de los parámetros
                param_values = []
                for _, row in df.iterrows():
                    if param in row['params']:
                        param_values.append(row['params'][param])
                    else:
                        param_values.append(np.nan)
                
                df[param] = param_values
                
                # Calcular correlación con el score
                corr = df[param].corr(df['score'])
                correlations[param] = abs(corr) if not np.isnan(corr) else 0
        
        # Ordenar por importancia
        sorted_params = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
        
        print(f"   Parámetros más importantes:")
        for param, importance in sorted_params[:10]:
            print(f"     {param}: {importance:.3f}")
    
    def _create_optimization_plots(self, df: pd.DataFrame):
        """Crea visualizaciones de la optimización"""
        
        # Gráfico de evolución del score
        plt.figure(figsize=(12, 8))
        
        # Subplot 1: Evolución del score
        plt.subplot(2, 2, 1)
        plt.plot(df['trial_number'], df['score'], 'b-', alpha=0.7, linewidth=1)
        plt.plot(df['trial_number'], df['score'].cummax(), 'r-', linewidth=2, label='Mejor hasta ahora')
        plt.xlabel('Trial Number')
        plt.ylabel('Score (mAP50-95)')
        plt.title('Evolución del Score')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Subplot 2: Distribución de scores
        plt.subplot(2, 2, 2)
        plt.hist(df['score'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.xlabel('Score')
        plt.ylabel('Frecuencia')
        plt.title('Distribución de Scores')
        plt.grid(True, alpha=0.3)
        
        # Subplot 3: mAP50 vs mAP50-95
        plt.subplot(2, 2, 3)
        plt.scatter(df['mAP50'], df['mAP50_95'], alpha=0.6, c=df['score'], cmap='viridis')
        plt.xlabel('mAP@0.5')
        plt.ylabel('mAP@0.5:0.95')
        plt.title('mAP@0.5 vs mAP@0.5:0.95')
        plt.colorbar(label='Score')
        plt.grid(True, alpha=0.3)
        
        # Subplot 4: Mejores parámetros (si hay suficientes trials)
        if len(df) > 10:
            plt.subplot(2, 2, 4)
            
            # Tomar los mejores 10 trials
            top_10 = df.nlargest(10, 'score')
            
            # Analizar algunos parámetros importantes
            params_to_plot = ['lr0', 'weight_decay', 'batch']
            param_means = []
            param_stds = []
            
            for param in params_to_plot:
                values = []
                for _, row in top_10.iterrows():
                    if param in row['params']:
                        values.append(row['params'][param])
                
                if values:
                    param_means.append(np.mean(values))
                    param_stds.append(np.std(values))
                else:
                    param_means.append(0)
                    param_stds.append(0)
            
            x_pos = np.arange(len(params_to_plot))
            plt.bar(x_pos, param_means, yerr=param_stds, alpha=0.7, capsize=5)
            plt.xlabel('Parámetros')
            plt.ylabel('Valor Promedio')
            plt.title('Mejores Parámetros (Top 10)')
            plt.xticks(x_pos, params_to_plot, rotation=45)
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'hyperparameter_optimization_{self.model_type}.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Gráficos guardados: hyperparameter_optimization_{self.model_type}.png")
    
    def save_results(self, filename: Optional[str] = None):
        """Guarda los resultados de la optimización"""
        
        if not self.trial_results:
            print("❌ No hay resultados para guardar")
            return
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'hyperparameter_optimization_{self.model_type}_{timestamp}.json'
        
        results_data = {
            'model_type': self.model_type,
            'optimization_date': datetime.now().isoformat(),
            'n_trials': len(self.trial_results),
            'best_params': self.best_params,
            'best_score': self.study.best_value if self.study else None,
            'trial_results': self.trial_results,
            'study_summary': {
                'n_trials': self.study.n_trials if self.study else 0,
                'best_value': self.study.best_value if self.study else 0,
                'best_params': self.study.best_params if self.study else {}
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        print(f"💾 Resultados guardados: {filename}")
        
        return filename
    
    def train_final_model(self, config: Optional[Dict] = None):
        """Entrena el modelo final con la mejor configuración"""
        
        if not self.best_params and not config:
            raise ValueError("No hay configuración optimizada disponible")
        
        if not config:
            config = self.get_best_config()
        
        print(f"\n🚀 ENTRENANDO MODELO FINAL CON CONFIGURACIÓN OPTIMIZADA")
        print("=" * 60)
        
        print(f"⚙️ Configuración final:")
        for key, value in config.items():
            if key not in ['model', 'data', 'device', 'project', 'name', 'exist_ok', 'pretrained', 'save', 'plots', 'verbose', 'val', 'workers', 'seed', 'deterministic']:
                print(f"   {key}: {value}")
        
        try:
            # Cargar modelo
            model = YOLO(config['model'])
            
            # Entrenar
            start_time = time.time()
            results = model.train(**config)
            training_time = time.time() - start_time
            
            print(f"\n✅ MODELO FINAL ENTRENADO")
            print(f"⏱️ Tiempo de entrenamiento: {training_time/60:.1f} minutos")
            print(f"📁 Modelo guardado en: {config['project']}/{config['name']}")
            
            # Mostrar métricas finales
            if hasattr(results, 'results_dict') and results.results_dict:
                print(f"\n📊 MÉTRICAS FINALES:")
                print(f"   mAP@0.5: {results.results_dict.get('metrics/mAP50(B)', 0.0):.3f}")
                print(f"   mAP@0.5:0.95: {results.results_dict.get('metrics/mAP50-95(B)', 0.0):.3f}")
                print(f"   Precisión: {results.results_dict.get('metrics/precision(B)', 0.0):.3f}")
                print(f"   Recall: {results.results_dict.get('metrics/recall(B)', 0.0):.3f}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error entrenando modelo final: {e}")
            return None

def main():
    """Función principal"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimizador de hiperparámetros para modelos YOLO')
    parser.add_argument('--model_type', type=str, choices=['dni', 'invoices'], required=True,
                       help='Tipo de modelo a optimizar')
    parser.add_argument('--n_trials', type=int, default=50,
                       help='Número de trials para optimización')
    parser.add_argument('--n_jobs', type=int, default=1,
                       help='Número de trabajos paralelos')
    parser.add_argument('--train_final', action='store_true',
                       help='Entrenar modelo final con mejor configuración')
    
    args = parser.parse_args()
    
    print("🔍 OPTIMIZADOR DE HIPERPARÁMETROS YOLO")
    print("=" * 50)
    
    # Crear optimizador
    optimizer = HyperparameterOptimizer(args.model_type, args.n_trials)
    
    # Ejecutar optimización
    best_params = optimizer.optimize(n_jobs=args.n_jobs)
    
    # Analizar resultados
    optimizer.analyze_results()
    
    # Guardar resultados
    optimizer.save_results()
    
    # Entrenar modelo final si se solicita
    if args.train_final:
        optimizer.train_final_model()
    
    print(f"\n🎉 OPTIMIZACIÓN COMPLETADA")
    print(f"💡 Mejores parámetros encontrados para {args.model_type}")
    print(f"📊 Revisa los gráficos y el archivo JSON para más detalles")

if __name__ == "__main__":
    main()
