#!/usr/bin/env python3
"""
Sistema de monitoreo en tiempo real para entrenamiento de modelos YOLO
Incluye visualizaciones, alertas y métricas avanzadas
"""

import os
import time
import json
import psutil
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import threading
import queue
import subprocess
import cv2
from typing import Dict, List, Optional, Tuple
import seaborn as sns

class TrainingMonitor:
    """Monitor de entrenamiento en tiempo real"""
    
    def __init__(self, monitoring_interval: int = 30):
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitoring_thread = None
        self.metrics_queue = queue.Queue()
        self.system_metrics = []
        self.training_logs = []
        self.start_time = None
        
    def start_monitoring(self, training_process_pid: Optional[int] = None):
        """Inicia el monitoreo en tiempo real"""
        
        print("🔍 Iniciando monitoreo de entrenamiento...")
        
        self.is_monitoring = True
        self.start_time = datetime.now()
        self.training_process_pid = training_process_pid
        
        # Iniciar hilo de monitoreo
        self.monitoring_thread = threading.Thread(target=self._monitor_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        # Iniciar monitoreo de logs
        self._monitor_training_logs()
        
    def stop_monitoring(self):
        """Detiene el monitoreo"""
        
        print("⏹️ Deteniendo monitoreo...")
        self.is_monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self._generate_final_report()
    
    def _monitor_loop(self):
        """Loop principal de monitoreo"""
        
        while self.is_monitoring:
            try:
                # Recopilar métricas del sistema
                system_metrics = self._collect_system_metrics()
                self.system_metrics.append(system_metrics)
                
                # Recopilar métricas de entrenamiento si están disponibles
                training_metrics = self._collect_training_metrics()
                if training_metrics:
                    self.training_logs.append(training_metrics)
                
                # Verificar alertas
                self._check_alerts(system_metrics, training_metrics)
                
                # Actualizar visualizaciones
                self._update_visualizations()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"❌ Error en monitoreo: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self) -> Dict:
        """Recopila métricas del sistema"""
        
        timestamp = datetime.now()
        
        # CPU y memoria
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        metrics = {
            'timestamp': timestamp,
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / (1024**3),
            'memory_available_gb': memory.available / (1024**3),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024**3)
        }
        
        # Métricas de GPU si está disponible
        try:
            import torch
            if torch.cuda.is_available():
                metrics.update({
                    'gpu_memory_allocated_mb': torch.cuda.memory_allocated(0) / (1024**2),
                    'gpu_memory_reserved_mb': torch.cuda.memory_reserved(0) / (1024**2),
                    'gpu_utilization': self._get_gpu_utilization()
                })
        except ImportError:
            pass
        
        # Temperatura si está disponible
        try:
            temperatures = psutil.sensors_temperatures()
            if temperatures:
                for name, entries in temperatures.items():
                    if entries:
                        metrics[f'temp_{name}'] = entries[0].current
        except:
            pass
        
        return metrics
    
    def _get_gpu_utilization(self) -> float:
        """Obtiene la utilización de GPU"""
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return 0.0
    
    def _collect_training_metrics(self) -> Optional[Dict]:
        """Recopila métricas del entrenamiento desde logs de YOLO"""
        
        # Buscar archivos de resultados más recientes
        results_dirs = list(Path('models/yolo_models').glob('*/'))
        if not results_dirs:
            return None
        
        latest_run = max(results_dirs, key=lambda p: p.stat().st_mtime)
        results_csv = latest_run / 'results.csv'
        
        if not results_csv.exists():
            return None
        
        try:
            # Leer el último resultado del CSV
            df = pd.read_csv(results_csv)
            if df.empty:
                return None
            
            latest_row = df.iloc[-1]
            
            return {
                'timestamp': datetime.now(),
                'epoch': int(latest_row.get('epoch', 0)),
                'train_box_loss': float(latest_row.get('train/box_loss', 0)),
                'train_cls_loss': float(latest_row.get('train/cls_loss', 0)),
                'train_dfl_loss': float(latest_row.get('train/dfl_loss', 0)),
                'val_box_loss': float(latest_row.get('val/box_loss', 0)),
                'val_cls_loss': float(latest_row.get('val/cls_loss', 0)),
                'val_dfl_loss': float(latest_row.get('val/dfl_loss', 0)),
                'mAP50': float(latest_row.get('metrics/mAP50(B)', 0)),
                'mAP50_95': float(latest_row.get('metrics/mAP50-95(B)', 0)),
                'precision': float(latest_row.get('metrics/precision(B)', 0)),
                'recall': float(latest_row.get('metrics/recall(B)', 0)),
                'learning_rate': float(latest_row.get('lr/pg0', 0))
            }
            
        except Exception as e:
            print(f"⚠️ Error leyendo métricas de entrenamiento: {e}")
            return None
    
    def _monitor_training_logs(self):
        """Monitorea logs de entrenamiento en tiempo real"""
        
        # Buscar procesos de entrenamiento activos
        training_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python' and 'train' in ' '.join(proc.info['cmdline']):
                    training_processes.append(proc.info['pid'])
            except:
                continue
        
        if training_processes:
            print(f"🎯 Procesos de entrenamiento detectados: {training_processes}")
    
    def _check_alerts(self, system_metrics: Dict, training_metrics: Optional[Dict]):
        """Verifica alertas del sistema"""
        
        alerts = []
        
        # Alertas de sistema
        if system_metrics['cpu_percent'] > 90:
            alerts.append(f"🚨 CPU alta: {system_metrics['cpu_percent']:.1f}%")
        
        if system_metrics['memory_percent'] > 90:
            alerts.append(f"🚨 Memoria alta: {system_metrics['memory_percent']:.1f}%")
        
        if system_metrics['disk_percent'] > 90:
            alerts.append(f"🚨 Disco lleno: {system_metrics['disk_percent']:.1f}%")
        
        # Alertas de GPU
        if 'gpu_memory_allocated_mb' in system_metrics:
            gpu_usage = system_metrics['gpu_memory_allocated_mb'] / (system_metrics['gpu_memory_reserved_mb'] + 1e-6) * 100
            if gpu_usage > 95:
                alerts.append(f"🚨 GPU memoria alta: {gpu_usage:.1f}%")
        
        # Alertas de entrenamiento
        if training_metrics:
            if training_metrics['mAP50'] > 0 and training_metrics['mAP50'] < 0.1:
                alerts.append(f"⚠️ mAP@0.5 muy bajo: {training_metrics['mAP50']:.3f}")
            
            if training_metrics['train_box_loss'] > 10:
                alerts.append(f"⚠️ Box loss muy alto: {training_metrics['train_box_loss']:.3f}")
        
        # Mostrar alertas
        if alerts:
            print(f"\n🚨 ALERTAS ({datetime.now().strftime('%H:%M:%S')}):")
            for alert in alerts:
                print(f"   {alert}")
    
    def _update_visualizations(self):
        """Actualiza visualizaciones en tiempo real"""
        
        if len(self.system_metrics) < 2:
            return
        
        # Crear gráfico de métricas del sistema
        self._create_system_plot()
        
        # Crear gráfico de métricas de entrenamiento
        if self.training_logs:
            self._create_training_plot()
    
    def _create_system_plot(self):
        """Crea gráfico de métricas del sistema"""
        
        if len(self.system_metrics) < 2:
            return
        
        df = pd.DataFrame(self.system_metrics)
        df['time'] = [(m['timestamp'] - self.start_time).total_seconds() / 60 for m in self.system_metrics]
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Métricas del Sistema - Monitoreo en Tiempo Real', fontsize=16)
        
        # CPU
        axes[0, 0].plot(df['time'], df['cpu_percent'], 'b-', linewidth=2)
        axes[0, 0].set_title('Uso de CPU (%)')
        axes[0, 0].set_ylabel('CPU %')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].set_ylim(0, 100)
        
        # Memoria
        axes[0, 1].plot(df['time'], df['memory_percent'], 'r-', linewidth=2)
        axes[0, 1].set_title('Uso de Memoria (%)')
        axes[0, 1].set_ylabel('Memoria %')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].set_ylim(0, 100)
        
        # Memoria GPU si está disponible
        if 'gpu_memory_allocated_mb' in df.columns:
            axes[1, 0].plot(df['time'], df['gpu_memory_allocated_mb'], 'g-', linewidth=2, label='Memoria GPU')
            axes[1, 0].set_title('Memoria GPU (MB)')
            axes[1, 0].set_ylabel('MB')
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].legend()
        else:
            axes[1, 0].text(0.5, 0.5, 'GPU no disponible', ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Memoria GPU')
        
        # Disco
        axes[1, 1].plot(df['time'], df['disk_percent'], 'm-', linewidth=2)
        axes[1, 1].set_title('Uso de Disco (%)')
        axes[1, 1].set_ylabel('Disco %')
        axes[1, 1].set_xlabel('Tiempo (minutos)')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_ylim(0, 100)
        
        plt.tight_layout()
        plt.savefig('training_system_metrics.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def _create_training_plot(self):
        """Crea gráfico de métricas de entrenamiento"""
        
        if len(self.training_logs) < 2:
            return
        
        df = pd.DataFrame(self.training_logs)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Métricas de Entrenamiento - Monitoreo en Tiempo Real', fontsize=16)
        
        # Loss
        axes[0, 0].plot(df['epoch'], df['train_box_loss'], 'b-', label='Train Box Loss', linewidth=2)
        axes[0, 0].plot(df['epoch'], df['val_box_loss'], 'r-', label='Val Box Loss', linewidth=2)
        axes[0, 0].set_title('Box Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # mAP
        axes[0, 1].plot(df['epoch'], df['mAP50'], 'g-', label='mAP@0.5', linewidth=2)
        axes[0, 1].plot(df['epoch'], df['mAP50_95'], 'orange', label='mAP@0.5:0.95', linewidth=2)
        axes[0, 1].set_title('Mean Average Precision')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('mAP')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Precision & Recall
        axes[1, 0].plot(df['epoch'], df['precision'], 'purple', label='Precision', linewidth=2)
        axes[1, 0].plot(df['epoch'], df['recall'], 'brown', label='Recall', linewidth=2)
        axes[1, 0].set_title('Precision & Recall')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Score')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Learning Rate
        axes[1, 1].plot(df['epoch'], df['learning_rate'], 'red', linewidth=2)
        axes[1, 1].set_title('Learning Rate')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('LR')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('training_metrics_realtime.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    def _generate_final_report(self):
        """Genera reporte final del monitoreo"""
        
        if not self.system_metrics:
            return
        
        print("\n📊 GENERANDO REPORTE FINAL DE MONITOREO")
        print("=" * 50)
        
        # Estadísticas del sistema
        df_system = pd.DataFrame(self.system_metrics)
        
        print(f"⏱️ Tiempo total de monitoreo: {(datetime.now() - self.start_time).total_seconds() / 60:.1f} minutos")
        print(f"📊 Muestras recopiladas: {len(self.system_metrics)}")
        
        print(f"\n💻 ESTADÍSTICAS DEL SISTEMA:")
        print(f"   CPU promedio: {df_system['cpu_percent'].mean():.1f}% (máx: {df_system['cpu_percent'].max():.1f}%)")
        print(f"   Memoria promedio: {df_system['memory_percent'].mean():.1f}% (máx: {df_system['memory_percent'].max():.1f}%)")
        print(f"   Disco usado: {df_system['disk_percent'].mean():.1f}%")
        
        if 'gpu_memory_allocated_mb' in df_system.columns:
            print(f"   GPU memoria promedio: {df_system['gpu_memory_allocated_mb'].mean():.1f} MB")
        
        # Estadísticas de entrenamiento
        if self.training_logs:
            df_training = pd.DataFrame(self.training_logs)
            print(f"\n🎯 ESTADÍSTICAS DE ENTRENAMIENTO:")
            print(f"   Épocas monitoreadas: {df_training['epoch'].min()} - {df_training['epoch'].max()}")
            print(f"   mAP@0.5 final: {df_training['mAP50'].iloc[-1]:.3f}")
            print(f"   mAP@0.5:0.95 final: {df_training['mAP50_95'].iloc[-1]:.3f}")
            print(f"   Precisión final: {df_training['precision'].iloc[-1]:.3f}")
            print(f"   Recall final: {df_training['recall'].iloc[-1]:.3f}")
        
        # Guardar datos
        report_data = {
            'monitoring_start': self.start_time.isoformat(),
            'monitoring_end': datetime.now().isoformat(),
            'system_metrics': self.system_metrics,
            'training_logs': self.training_logs,
            'summary': {
                'total_samples': len(self.system_metrics),
                'avg_cpu': float(df_system['cpu_percent'].mean()),
                'max_cpu': float(df_system['cpu_percent'].max()),
                'avg_memory': float(df_system['memory_percent'].mean()),
                'max_memory': float(df_system['memory_percent'].max())
            }
        }
        
        if self.training_logs:
            report_data['summary'].update({
                'final_mAP50': float(df_training['mAP50'].iloc[-1]),
                'final_mAP50_95': float(df_training['mAP50_95'].iloc[-1]),
                'final_precision': float(df_training['precision'].iloc[-1]),
                'final_recall': float(df_training['recall'].iloc[-1])
            })
        
        with open('training_monitoring_report.json', 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n📄 Reporte guardado: training_monitoring_report.json")
        print(f"📊 Gráficos guardados: training_system_metrics.png, training_metrics_realtime.png")

def main():
    """Función principal para monitoreo standalone"""
    
    print("🔍 SISTEMA DE MONITOREO DE ENTRENAMIENTO")
    print("=" * 50)
    
    monitor = TrainingMonitor(monitoring_interval=30)
    
    try:
        monitor.start_monitoring()
        
        print("✅ Monitoreo iniciado. Presiona Ctrl+C para detener...")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo monitoreo...")
        monitor.stop_monitoring()
        print("✅ Monitoreo detenido")

if __name__ == "__main__":
    main()
