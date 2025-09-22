#!/usr/bin/env python3
"""
Analizador y comparador de modelos YOLO entrenados
Incluye métricas detalladas, visualizaciones y recomendaciones
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import cv2
from ultralytics import YOLO
import torch

class ModelAnalyzer:
    """Analizador completo de modelos YOLO"""
    
    def __init__(self, models_dir: str = "models/yolo_models"):
        self.models_dir = Path(models_dir)
        self.analysis_results = {}
        
    def find_all_models(self) -> List[Dict]:
        """Encuentra todos los modelos entrenados"""
        
        print("🔍 BUSCANDO MODELOS ENTRENADOS")
        print("=" * 50)
        
        models = []
        
        if not self.models_dir.exists():
            print(f"❌ Directorio de modelos no encontrado: {self.models_dir}")
            return models
        
        # Buscar en subdirectorios
        for model_dir in self.models_dir.iterdir():
            if model_dir.is_dir():
                weights_dir = model_dir / 'weights'
                
                if weights_dir.exists():
                    model_info = {
                        'name': model_dir.name,
                        'path': model_dir,
                        'weights_dir': weights_dir,
                        'best_model': weights_dir / 'best.pt',
                        'last_model': weights_dir / 'last.pt',
                        'results_csv': model_dir / 'results.csv',
                        'results_png': model_dir / 'results.png',
                        'confusion_matrix': model_dir / 'confusion_matrix.png'
                    }
                    
                    # Verificar qué archivos existen
                    model_info['best_exists'] = model_info['best_model'].exists()
                    model_info['last_exists'] = model_info['last_model'].exists()
                    model_info['results_csv_exists'] = model_info['results_csv'].exists()
                    model_info['results_png_exists'] = model_info['results_png'].exists()
                    model_info['confusion_matrix_exists'] = model_info['confusion_matrix'].exists()
                    
                    models.append(model_info)
                    
                    print(f"✅ {model_info['name']}")
                    print(f"   Best model: {'✅' if model_info['best_exists'] else '❌'}")
                    print(f"   Results CSV: {'✅' if model_info['results_csv_exists'] else '❌'}")
        
        print(f"\n📊 Total de modelos encontrados: {len(models)}")
        return models
    
    def analyze_single_model(self, model_info: Dict) -> Dict:
        """Analiza un modelo individual"""
        
        print(f"\n🔍 ANALIZANDO MODELO: {model_info['name']}")
        print("-" * 40)
        
        analysis = {
            'name': model_info['name'],
            'path': str(model_info['path']),
            'files_available': {
                'best_model': model_info['best_exists'],
                'last_model': model_info['last_exists'],
                'results_csv': model_info['results_csv_exists'],
                'results_png': model_info['results_png_exists'],
                'confusion_matrix': model_info['confusion_matrix_exists']
            },
            'metrics': {},
            'performance': {},
            'recommendations': []
        }
        
        # Analizar archivo de resultados CSV
        if model_info['results_csv_exists']:
            try:
                df = pd.read_csv(model_info['results_csv'])
                
                if not df.empty:
                    # Obtener métricas finales
                    final_row = df.iloc[-1]
                    
                    analysis['metrics'] = {
                        'final_epoch': int(final_row.get('epoch', 0)),
                        'train_box_loss': float(final_row.get('train/box_loss', 0)),
                        'train_cls_loss': float(final_row.get('train/cls_loss', 0)),
                        'train_dfl_loss': float(final_row.get('train/dfl_loss', 0)),
                        'val_box_loss': float(final_row.get('val/box_loss', 0)),
                        'val_cls_loss': float(final_row.get('val/cls_loss', 0)),
                        'val_dfl_loss': float(final_row.get('val/dfl_loss', 0)),
                        'mAP50': float(final_row.get('metrics/mAP50(B)', 0)),
                        'mAP50_95': float(final_row.get('metrics/mAP50-95(B)', 0)),
                        'precision': float(final_row.get('metrics/precision(B)', 0)),
                        'recall': float(final_row.get('metrics/recall(B)', 0)),
                        'final_lr': float(final_row.get('lr/pg0', 0))
                    }
                    
                    # Análisis de convergencia
                    analysis['convergence'] = self._analyze_convergence(df)
                    
                    # Análisis de overfitting
                    analysis['overfitting'] = self._analyze_overfitting(df)
                    
                    print(f"   📊 Épocas: {analysis['metrics']['final_epoch']}")
                    print(f"   📊 mAP@0.5: {analysis['metrics']['mAP50']:.3f}")
                    print(f"   📊 mAP@0.5:0.95: {analysis['metrics']['mAP50_95']:.3f}")
                    print(f"   📊 Precisión: {analysis['metrics']['precision']:.3f}")
                    print(f"   📊 Recall: {analysis['metrics']['recall']:.3f}")
                    
            except Exception as e:
                print(f"   ❌ Error analizando CSV: {e}")
                analysis['csv_error'] = str(e)
        
        # Analizar el modelo si está disponible
        if model_info['best_exists']:
            try:
                model = YOLO(str(model_info['best_model']))
                
                # Información del modelo
                analysis['model_info'] = {
                    'model_type': getattr(model.model, 'model_type', 'unknown'),
                    'num_classes': len(model.names) if hasattr(model, 'names') else 0,
                    'class_names': model.names if hasattr(model, 'names') else {},
                    'model_size_mb': model_info['best_model'].stat().st_size / (1024 * 1024)
                }
                
                print(f"   📦 Tamaño del modelo: {analysis['model_info']['model_size_mb']:.1f} MB")
                print(f"   📦 Clases: {analysis['model_info']['num_classes']}")
                
                # Prueba de inferencia rápida
                analysis['inference_test'] = self._test_inference_speed(model)
                
            except Exception as e:
                print(f"   ❌ Error analizando modelo: {e}")
                analysis['model_error'] = str(e)
        
        # Generar recomendaciones
        analysis['recommendations'] = self._generate_model_recommendations(analysis)
        
        return analysis
    
    def _analyze_convergence(self, df: pd.DataFrame) -> Dict:
        """Analiza la convergencia del entrenamiento"""
        
        convergence = {
            'converged': False,
            'convergence_epoch': None,
            'stability_epochs': 0
        }
        
        if 'metrics/mAP50(B)' in df.columns:
            mAP_values = df['metrics/mAP50(B)'].dropna()
            
            if len(mAP_values) > 10:
                # Buscar convergencia (mejora < 0.001 por epoch en últimos 20 epochs)
                window_size = min(20, len(mAP_values) // 4)
                recent_values = mAP_values.tail(window_size)
                
                if len(recent_values) >= 10:
                    # Calcular mejora promedio
                    improvements = recent_values.diff().dropna()
                    avg_improvement = improvements.mean()
                    
                    if avg_improvement < 0.001:
                        convergence['converged'] = True
                        convergence['convergence_epoch'] = len(mAP_values) - window_size
                        convergence['stability_epochs'] = window_size
        
        return convergence
    
    def _analyze_overfitting(self, df: pd.DataFrame) -> Dict:
        """Analiza el overfitting"""
        
        overfitting = {
            'detected': False,
            'gap_train_val': 0,
            'recommendation': None
        }
        
        if 'train/box_loss' in df.columns and 'val/box_loss' in df.columns:
            train_loss = df['train/box_loss'].dropna()
            val_loss = df['val/box_loss'].dropna()
            
            if len(train_loss) > 0 and len(val_loss) > 0:
                final_train = train_loss.iloc[-1]
                final_val = val_loss.iloc[-1]
                
                gap = final_val - final_train
                overfitting['gap_train_val'] = gap
                
                if gap > 0.5:  # Gap significativo
                    overfitting['detected'] = True
                    overfitting['recommendation'] = "Considera reducir learning rate o aumentar regularización"
                elif gap > 1.0:  # Gap muy grande
                    overfitting['detected'] = True
                    overfitting['recommendation'] = "Overfitting severo - reduce complejidad del modelo o aumenta datos"
        
        return overfitting
    
    def _test_inference_speed(self, model) -> Dict:
        """Prueba la velocidad de inferencia"""
        
        try:
            # Crear imagen de prueba
            test_image = np.zeros((640, 640, 3), dtype=np.uint8)
            
            # Medir tiempo de inferencia
            import time
            
            # Warmup
            for _ in range(3):
                _ = model(test_image, verbose=False)
            
            # Medir tiempo real
            times = []
            for _ in range(10):
                start_time = time.time()
                _ = model(test_image, verbose=False)
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = np.mean(times)
            std_time = np.std(times)
            
            return {
                'avg_inference_time_ms': avg_time * 1000,
                'std_inference_time_ms': std_time * 1000,
                'fps': 1.0 / avg_time,
                'times': times
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_model_recommendations(self, analysis: Dict) -> List[str]:
        """Genera recomendaciones para el modelo"""
        
        recommendations = []
        
        # Verificar métricas básicas
        if 'metrics' in analysis:
            mAP50 = analysis['metrics'].get('mAP50', 0)
            mAP50_95 = analysis['metrics'].get('mAP50_95', 0)
            precision = analysis['metrics'].get('precision', 0)
            recall = analysis['metrics'].get('recall', 0)
            
            if mAP50 < 0.3:
                recommendations.append("🚨 mAP@0.5 muy bajo - Considera más datos de entrenamiento")
            elif mAP50 < 0.5:
                recommendations.append("⚠️ mAP@0.5 moderado - Podrías mejorar con más épocas o mejor data augmentation")
            else:
                recommendations.append("✅ mAP@0.5 bueno - Modelo funcionando bien")
            
            if mAP50_95 < 0.2:
                recommendations.append("📊 mAP@0.5:0.95 bajo - Mejora la precisión de localización")
            
            if precision < 0.5:
                recommendations.append("🎯 Precisión baja - Muchos falsos positivos")
            
            if recall < 0.5:
                recommendations.append("🔍 Recall bajo - Muchos falsos negativos")
        
        # Verificar convergencia
        if 'convergence' in analysis:
            if not analysis['convergence']['converged']:
                recommendations.append("🔄 Modelo no convergió completamente - Considera más épocas")
        
        # Verificar overfitting
        if 'overfitting' in analysis:
            if analysis['overfitting']['detected']:
                recommendations.append(f"⚠️ Overfitting detectado: {analysis['overfitting']['recommendation']}")
        
        # Verificar velocidad de inferencia
        if 'inference_test' in analysis and 'error' not in analysis['inference_test']:
            fps = analysis['inference_test'].get('fps', 0)
            if fps < 10:
                recommendations.append("🐌 Inferencia lenta - Considera optimizar el modelo")
            elif fps > 50:
                recommendations.append("🚀 Inferencia muy rápida - Excelente para producción")
        
        return recommendations
    
    def compare_models(self, models: List[Dict]) -> Dict:
        """Compara múltiples modelos"""
        
        print(f"\n📊 COMPARANDO {len(models)} MODELOS")
        print("=" * 50)
        
        comparison = {
            'models_compared': len(models),
            'comparison_date': datetime.now().isoformat(),
            'summary': {},
            'rankings': {},
            'best_model': None,
            'detailed_comparison': []
        }
        
        # Analizar cada modelo
        analyses = []
        for model in models:
            analysis = self.analyze_single_model(model)
            analyses.append(analysis)
            self.analysis_results[model['name']] = analysis
        
        # Crear DataFrame para comparación
        metrics_data = []
        for analysis in analyses:
            if 'metrics' in analysis:
                row = {'model_name': analysis['name']}
                row.update(analysis['metrics'])
                metrics_data.append(row)
        
        if metrics_data:
            df_comparison = pd.DataFrame(metrics_data)
            
            # Rankings
            comparison['rankings'] = {
                'mAP50': df_comparison.nlargest(len(df_comparison), 'mAP50')[['model_name', 'mAP50']].to_dict('records'),
                'mAP50_95': df_comparison.nlargest(len(df_comparison), 'mAP50_95')[['model_name', 'mAP50_95']].to_dict('records'),
                'precision': df_comparison.nlargest(len(df_comparison), 'precision')[['model_name', 'precision']].to_dict('records'),
                'recall': df_comparison.nlargest(len(df_comparison), 'recall')[['model_name', 'recall']].to_dict('records')
            }
            
            # Mejor modelo general
            best_mAP50_idx = df_comparison['mAP50'].idxmax()
            comparison['best_model'] = df_comparison.iloc[best_mAP50_idx]['model_name']
            
            # Estadísticas resumidas
            comparison['summary'] = {
                'avg_mAP50': df_comparison['mAP50'].mean(),
                'max_mAP50': df_comparison['mAP50'].max(),
                'min_mAP50': df_comparison['mAP50'].min(),
                'avg_mAP50_95': df_comparison['mAP50_95'].mean(),
                'max_mAP50_95': df_comparison['mAP50_95'].max(),
                'avg_precision': df_comparison['precision'].mean(),
                'avg_recall': df_comparison['recall'].mean()
            }
            
            # Comparación detallada
            comparison['detailed_comparison'] = df_comparison.to_dict('records')
            
            print(f"🏆 Mejor modelo general: {comparison['best_model']}")
            print(f"📊 mAP@0.5 promedio: {comparison['summary']['avg_mAP50']:.3f}")
            print(f"📊 mAP@0.5 máximo: {comparison['summary']['max_mAP50']:.3f}")
        
        return comparison
    
    def create_visualizations(self, comparison: Dict):
        """Crea visualizaciones de la comparación"""
        
        print(f"\n📊 CREANDO VISUALIZACIONES")
        print("=" * 30)
        
        if not comparison['detailed_comparison']:
            print("❌ No hay datos para visualizar")
            return
        
        df = pd.DataFrame(comparison['detailed_comparison'])
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Crear figura con subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Comparación de Modelos YOLO', fontsize=16, fontweight='bold')
        
        # 1. Comparación de mAP
        ax1 = axes[0, 0]
        x_pos = np.arange(len(df))
        width = 0.35
        
        bars1 = ax1.bar(x_pos - width/2, df['mAP50'], width, label='mAP@0.5', alpha=0.8)
        bars2 = ax1.bar(x_pos + width/2, df['mAP50_95'], width, label='mAP@0.5:0.95', alpha=0.8)
        
        ax1.set_xlabel('Modelos')
        ax1.set_ylabel('mAP')
        ax1.set_title('Comparación de mAP')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(df['model_name'], rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Agregar valores en las barras
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=8)
        
        # 2. Precision vs Recall
        ax2 = axes[0, 1]
        scatter = ax2.scatter(df['precision'], df['recall'], 
                            s=df['mAP50']*500, alpha=0.7, c=df['mAP50_95'], 
                            cmap='viridis')
        
        ax2.set_xlabel('Precisión')
        ax2.set_ylabel('Recall')
        ax2.set_title('Precisión vs Recall (tamaño=mAP@0.5, color=mAP@0.5:0.95)')
        ax2.grid(True, alpha=0.3)
        
        # Agregar nombres de modelos
        for i, model in enumerate(df['model_name']):
            ax2.annotate(model, (df['precision'].iloc[i], df['recall'].iloc[i]),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.colorbar(scatter, ax=ax2, label='mAP@0.5:0.95')
        
        # 3. Pérdidas de entrenamiento vs validación
        ax3 = axes[1, 0]
        ax3.bar(x_pos - width/2, df['train_box_loss'], width, label='Train Box Loss', alpha=0.8)
        ax3.bar(x_pos + width/2, df['val_box_loss'], width, label='Val Box Loss', alpha=0.8)
        
        ax3.set_xlabel('Modelos')
        ax3.set_ylabel('Box Loss')
        ax3.set_title('Pérdidas de Entrenamiento vs Validación')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(df['model_name'], rotation=45, ha='right')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Épocas de entrenamiento
        ax4 = axes[1, 1]
        bars = ax4.bar(df['model_name'], df['final_epoch'], alpha=0.8, color='skyblue')
        ax4.set_xlabel('Modelos')
        ax4.set_ylabel('Épocas Finales')
        ax4.set_title('Épocas de Entrenamiento')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
        
        # Agregar valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('model_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Crear gráfico de radar para el mejor modelo
        if comparison['best_model']:
            self._create_radar_chart(df, comparison['best_model'])
        
        print("✅ Visualizaciones guardadas:")
        print("   - model_comparison.png")
        print("   - best_model_radar.png")
    
    def _create_radar_chart(self, df: pd.DataFrame, best_model_name: str):
        """Crea gráfico de radar para el mejor modelo"""
        
        best_model = df[df['model_name'] == best_model_name].iloc[0]
        
        # Métricas a mostrar
        metrics = ['mAP50', 'mAP50_95', 'precision', 'recall']
        values = [best_model[metric] for metric in metrics]
        
        # Normalizar valores (0-1)
        normalized_values = [v for v in values]  # Ya están en escala 0-1
        
        # Ángulos para cada métrica
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Cerrar el círculo
        
        # Valores + primer valor para cerrar
        normalized_values += normalized_values[:1]
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # Dibujar
        ax.plot(angles, normalized_values, 'o-', linewidth=2, label=best_model_name, color='red')
        ax.fill(angles, normalized_values, alpha=0.25, color='red')
        
        # Configurar
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 1)
        ax.set_title(f'Perfil del Mejor Modelo: {best_model_name}', size=16, fontweight='bold', pad=20)
        ax.grid(True)
        
        # Agregar valores
        for angle, value, metric in zip(angles[:-1], values, metrics):
            ax.text(angle, value + 0.05, f'{value:.3f}', ha='center', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('best_model_radar.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_report(self, comparison: Dict) -> str:
        """Genera reporte completo"""
        
        print(f"\n📄 GENERANDO REPORTE COMPLETO")
        print("=" * 30)
        
        report = {
            'analysis_date': datetime.now().isoformat(),
            'summary': comparison['summary'],
            'best_model': comparison['best_model'],
            'rankings': comparison['rankings'],
            'detailed_results': self.analysis_results,
            'recommendations': self._generate_overall_recommendations(comparison)
        }
        
        # Guardar reporte
        report_path = 'model_analysis_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Crear reporte en texto
        self._create_text_report(report)
        
        print(f"✅ Reporte guardado: {report_path}")
        print(f"✅ Reporte texto: model_analysis_report.txt")
        
        return report_path
    
    def _generate_overall_recommendations(self, comparison: Dict) -> List[str]:
        """Genera recomendaciones generales"""
        
        recommendations = []
        
        if comparison['summary']['avg_mAP50'] < 0.4:
            recommendations.append("🚨 Rendimiento general bajo - Considera mejorar la calidad de los datos")
        
        if comparison['summary']['max_mAP50'] - comparison['summary']['min_mAP50'] > 0.3:
            recommendations.append("📊 Alta variabilidad entre modelos - Revisa la configuración de entrenamiento")
        
        if comparison['summary']['avg_precision'] < comparison['summary']['avg_recall']:
            recommendations.append("🎯 Precisión menor que recall - Muchos falsos positivos, ajusta threshold de confianza")
        
        if comparison['best_model']:
            recommendations.append(f"🏆 Usar modelo '{comparison['best_model']}' para producción")
        
        return recommendations
    
    def _create_text_report(self, report: Dict):
        """Crea reporte en formato texto"""
        
        with open('model_analysis_report.txt', 'w') as f:
            f.write("ANÁLISIS DE MODELOS YOLO\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Fecha de análisis: {report['analysis_date']}\n\n")
            
            f.write("RESUMEN GENERAL\n")
            f.write("-" * 20 + "\n")
            summary = report['summary']
            f.write(f"mAP@0.5 promedio: {summary['avg_mAP50']:.3f}\n")
            f.write(f"mAP@0.5 máximo: {summary['max_mAP50']:.3f}\n")
            f.write(f"mAP@0.5:0.95 promedio: {summary['avg_mAP50_95']:.3f}\n")
            f.write(f"Precisión promedio: {summary['avg_precision']:.3f}\n")
            f.write(f"Recall promedio: {summary['avg_recall']:.3f}\n\n")
            
            f.write(f"MEJOR MODELO: {report['best_model']}\n\n")
            
            f.write("RECOMENDACIONES\n")
            f.write("-" * 20 + "\n")
            for rec in report['recommendations']:
                f.write(f"{rec}\n")
            
            f.write("\nRANKINGS\n")
            f.write("-" * 20 + "\n")
            
            for metric, ranking in report['rankings'].items():
                f.write(f"\n{metric.upper()}:\n")
                for i, item in enumerate(ranking, 1):
                    f.write(f"  {i}. {item['model_name']}: {item[metric]:.3f}\n")
            
            f.write("\nRESULTADOS DETALLADOS\n")
            f.write("-" * 20 + "\n")
            
            for model_name, analysis in report['detailed_results'].items():
                f.write(f"\n{model_name}:\n")
                if 'metrics' in analysis:
                    metrics = analysis['metrics']
                    f.write(f"  mAP@0.5: {metrics['mAP50']:.3f}\n")
                    f.write(f"  mAP@0.5:0.95: {metrics['mAP50_95']:.3f}\n")
                    f.write(f"  Precisión: {metrics['precision']:.3f}\n")
                    f.write(f"  Recall: {metrics['recall']:.3f}\n")
                    f.write(f"  Épocas: {metrics['final_epoch']}\n")
                
                if 'recommendations' in analysis:
                    f.write(f"  Recomendaciones:\n")
                    for rec in analysis['recommendations']:
                        f.write(f"    - {rec}\n")

def main():
    """Función principal"""
    
    print("🔍 ANALIZADOR DE MODELOS YOLO")
    print("=" * 50)
    
    analyzer = ModelAnalyzer()
    
    # Encontrar modelos
    models = analyzer.find_all_models()
    
    if not models:
        print("❌ No se encontraron modelos para analizar")
        return
    
    # Comparar modelos
    comparison = analyzer.compare_models(models)
    
    # Crear visualizaciones
    analyzer.create_visualizations(comparison)
    
    # Generar reporte
    analyzer.generate_report(comparison)
    
    print(f"\n🎉 ANÁLISIS COMPLETADO")
    print("=" * 50)
    print("📊 Archivos generados:")
    print("   - model_comparison.png")
    print("   - best_model_radar.png")
    print("   - model_analysis_report.json")
    print("   - model_analysis_report.txt")

if __name__ == "__main__":
    main()
