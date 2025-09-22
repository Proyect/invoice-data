#!/usr/bin/env python3
"""
Workflow completo de entrenamiento de modelos YOLO
Integra todas las mejoras en un flujo automatizado
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Importar todos los sistemas mejorados
from advanced_training_system import AdvancedTrainingSystem
from hyperparameter_optimizer import HyperparameterOptimizer
from training_monitor import TrainingMonitor
from model_analyzer import ModelAnalyzer

class CompleteTrainingWorkflow:
    """Workflow completo de entrenamiento"""
    
    def __init__(self):
        self.workflow_results = {}
        self.start_time = None
        
    def run_complete_workflow(self, 
                            model_type: str,
                            use_hyperopt: bool = True,
                            use_cv: bool = False,
                            use_monitoring: bool = True,
                            n_trials: int = 50,
                            final_epochs: int = 300) -> Dict:
        """Ejecuta el workflow completo de entrenamiento"""
        
        self.start_time = datetime.now()
        
        print("🚀 WORKFLOW COMPLETO DE ENTRENAMIENTO YOLO")
        print("=" * 60)
        print(f"🎯 Modelo: {model_type}")
        print(f"🔍 Optimización de hiperparámetros: {'✅' if use_hyperopt else '❌'}")
        print(f"🔄 Validación cruzada: {'✅' if use_cv else '❌'}")
        print(f"📊 Monitoreo: {'✅' if use_monitoring else '❌'}")
        print(f"🎲 Trials de optimización: {n_trials}")
        print(f"⏱️ Épocas finales: {final_epochs}")
        print("=" * 60)
        
        workflow_steps = []
        
        try:
            # PASO 1: Optimización de hiperparámetros
            if use_hyperopt:
                print(f"\n🔍 PASO 1: OPTIMIZACIÓN DE HIPERPARÁMETROS")
                print("-" * 50)
                
                optimizer = HyperparameterOptimizer(model_type, n_trials)
                best_params = optimizer.optimize()
                
                if best_params:
                    workflow_steps.append({
                        'step': 'hyperparameter_optimization',
                        'status': 'completed',
                        'best_params': best_params,
                        'best_score': optimizer.study.best_value if optimizer.study else 0
                    })
                    print(f"✅ Optimización completada - Mejor score: {optimizer.study.best_value:.4f}")
                else:
                    print("❌ Falló la optimización de hiperparámetros")
                    workflow_steps.append({
                        'step': 'hyperparameter_optimization',
                        'status': 'failed'
                    })
            else:
                print(f"\n⏭️ PASO 1: SALTANDO OPTIMIZACIÓN DE HIPERPARÁMETROS")
                workflow_steps.append({
                    'step': 'hyperparameter_optimization',
                    'status': 'skipped'
                })
            
            # PASO 2: Entrenamiento con monitoreo
            print(f"\n🏋️ PASO 2: ENTRENAMIENTO CON MONITOREO")
            print("-" * 50)
            
            # Configurar monitoreo si se solicita
            monitor = None
            if use_monitoring:
                monitor = TrainingMonitor(monitoring_interval=30)
                monitor.start_monitoring()
                print("📊 Monitoreo iniciado")
            
            # Configurar entrenamiento avanzado
            trainer = AdvancedTrainingSystem(use_wandb=True)
            
            # Usar mejores parámetros si están disponibles
            custom_config = None
            if use_hyperopt and workflow_steps[0]['status'] == 'completed':
                custom_config = workflow_steps[0]['best_params']
                custom_config['epochs'] = final_epochs
            
            # Entrenar modelo
            training_results = trainer.train_model_advanced(
                model_type, 
                use_hyperopt=False,  # Ya se hizo la optimización
                use_cv=use_cv,
                custom_config=custom_config
            )
            
            # Detener monitoreo
            if monitor:
                monitor.stop_monitoring()
                print("📊 Monitoreo detenido")
            
            if training_results:
                workflow_steps.append({
                    'step': 'training',
                    'status': 'completed',
                    'model_path': training_results['model_path'],
                    'final_metrics': training_results['final_metrics'],
                    'training_time': training_results['training_time']
                })
                print(f"✅ Entrenamiento completado - Modelo: {training_results['model_path']}")
            else:
                print("❌ Falló el entrenamiento")
                workflow_steps.append({
                    'step': 'training',
                    'status': 'failed'
                })
            
            # PASO 3: Validación cruzada (si se solicita)
            if use_cv:
                print(f"\n🔄 PASO 3: VALIDACIÓN CRUZADA")
                print("-" * 50)
                
                cv_results = trainer.cross_validation(model_type)
                
                if cv_results:
                    workflow_steps.append({
                        'step': 'cross_validation',
                        'status': 'completed',
                        'cv_stats': cv_results
                    })
                    print(f"✅ Validación cruzada completada")
                else:
                    print("❌ Falló la validación cruzada")
                    workflow_steps.append({
                        'step': 'cross_validation',
                        'status': 'failed'
                    })
            else:
                workflow_steps.append({
                    'step': 'cross_validation',
                    'status': 'skipped'
                })
            
            # PASO 4: Análisis de modelos
            print(f"\n📊 PASO 4: ANÁLISIS DE MODELOS")
            print("-" * 50)
            
            analyzer = ModelAnalyzer()
            models = analyzer.find_all_models()
            
            if models:
                comparison = analyzer.compare_models(models)
                analyzer.create_visualizations(comparison)
                report_path = analyzer.generate_report(comparison)
                
                workflow_steps.append({
                    'step': 'model_analysis',
                    'status': 'completed',
                    'best_model': comparison['best_model'],
                    'report_path': report_path
                })
                print(f"✅ Análisis completado - Mejor modelo: {comparison['best_model']}")
            else:
                print("❌ No se encontraron modelos para analizar")
                workflow_steps.append({
                    'step': 'model_analysis',
                    'status': 'failed'
                })
            
            # PASO 5: Generar reporte final
            print(f"\n📄 PASO 5: GENERANDO REPORTE FINAL")
            print("-" * 50)
            
            final_report = self._generate_final_report(workflow_steps)
            
            workflow_steps.append({
                'step': 'final_report',
                'status': 'completed',
                'report_path': 'complete_workflow_report.json'
            })
            
            print(f"✅ Reporte final generado")
            
        except Exception as e:
            print(f"❌ Error en el workflow: {e}")
            workflow_steps.append({
                'step': 'error',
                'status': 'failed',
                'error': str(e)
            })
        
        # Calcular tiempo total
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        # Resultados finales
        self.workflow_results = {
            'workflow_date': self.start_time.isoformat(),
            'model_type': model_type,
            'total_time_seconds': total_time,
            'total_time_minutes': total_time / 60,
            'steps': workflow_steps,
            'success': all(step['status'] in ['completed', 'skipped'] for step in workflow_steps),
            'settings': {
                'use_hyperopt': use_hyperopt,
                'use_cv': use_cv,
                'use_monitoring': use_monitoring,
                'n_trials': n_trials,
                'final_epochs': final_epochs
            }
        }
        
        # Guardar resultados
        with open('complete_workflow_report.json', 'w') as f:
            json.dump(self.workflow_results, f, indent=2, default=str)
        
        # Mostrar resumen final
        self._show_final_summary()
        
        return self.workflow_results
    
    def _generate_final_report(self, workflow_steps: List[Dict]) -> Dict:
        """Genera el reporte final del workflow"""
        
        report = {
            'workflow_summary': {
                'total_steps': len(workflow_steps),
                'completed_steps': len([s for s in workflow_steps if s['status'] == 'completed']),
                'failed_steps': len([s for s in workflow_steps if s['status'] == 'failed']),
                'skipped_steps': len([s for s in workflow_steps if s['status'] == 'skipped'])
            },
            'step_details': workflow_steps,
            'recommendations': self._generate_workflow_recommendations(workflow_steps),
            'next_steps': self._generate_next_steps(workflow_steps)
        }
        
        with open('workflow_summary_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report
    
    def _generate_workflow_recommendations(self, workflow_steps: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en el workflow"""
        
        recommendations = []
        
        # Verificar optimización de hiperparámetros
        hyperopt_step = next((s for s in workflow_steps if s['step'] == 'hyperparameter_optimization'), None)
        if hyperopt_step and hyperopt_step['status'] == 'completed':
            best_score = hyperopt_step.get('best_score', 0)
            if best_score < 0.3:
                recommendations.append("🚨 Score de optimización bajo - Considera más trials o mejor configuración inicial")
            elif best_score > 0.7:
                recommendations.append("✅ Excelente optimización - Los hiperparámetros están bien ajustados")
        
        # Verificar entrenamiento
        training_step = next((s for s in workflow_steps if s['step'] == 'training'), None)
        if training_step and training_step['status'] == 'completed':
            training_time = training_step.get('training_time', 0)
            if training_time > 7200:  # Más de 2 horas
                recommendations.append("⏱️ Entrenamiento muy lento - Considera usar GPU o reducir batch size")
        
        # Verificar validación cruzada
        cv_step = next((s for s in workflow_steps if s['step'] == 'cross_validation'), None)
        if cv_step and cv_step['status'] == 'completed':
            cv_stats = cv_step.get('cv_stats', {})
            if cv_stats.get('std_mAP50_95', 0) > 0.1:
                recommendations.append("📊 Alta variabilidad en CV - El modelo podría no ser robusto")
        
        # Verificar análisis
        analysis_step = next((s for s in workflow_steps if s['step'] == 'model_analysis'), None)
        if analysis_step and analysis_step['status'] == 'completed':
            best_model = analysis_step.get('best_model')
            if best_model:
                recommendations.append(f"🏆 Usar modelo '{best_model}' para producción")
        
        return recommendations
    
    def _generate_next_steps(self, workflow_steps: List[Dict]) -> List[str]:
        """Genera los próximos pasos recomendados"""
        
        next_steps = []
        
        # Verificar si el workflow fue exitoso
        if all(step['status'] in ['completed', 'skipped'] for step in workflow_steps):
            next_steps.extend([
                "✅ Workflow completado exitosamente",
                "📦 Integrar el mejor modelo en la aplicación",
                "🧪 Probar el modelo con datos reales",
                "📊 Monitorear el rendimiento en producción",
                "🔄 Configurar retraining automático si es necesario"
            ])
        else:
            next_steps.extend([
                "❌ Revisar los pasos que fallaron",
                "🔧 Corregir errores y volver a ejecutar",
                "📞 Considerar contactar soporte técnico"
            ])
        
        return next_steps
    
    def _show_final_summary(self):
        """Muestra el resumen final del workflow"""
        
        print(f"\n🎉 WORKFLOW COMPLETADO")
        print("=" * 60)
        
        total_time = self.workflow_results['total_time_minutes']
        success = self.workflow_results['success']
        
        print(f"⏱️ Tiempo total: {total_time:.1f} minutos")
        print(f"📊 Estado: {'✅ EXITOSO' if success else '❌ FALLÓ'}")
        
        print(f"\n📋 PASOS EJECUTADOS:")
        for i, step in enumerate(self.workflow_results['steps'], 1):
            status_icon = {
                'completed': '✅',
                'failed': '❌',
                'skipped': '⏭️'
            }.get(step['status'], '❓')
            
            print(f"   {i}. {status_icon} {step['step'].replace('_', ' ').title()}")
        
        if 'recommendations' in self.workflow_results:
            print(f"\n💡 RECOMENDACIONES:")
            for rec in self.workflow_results['recommendations']:
                print(f"   {rec}")
        
        print(f"\n📄 ARCHIVOS GENERADOS:")
        print(f"   - complete_workflow_report.json")
        print(f"   - workflow_summary_report.json")
        print(f"   - model_comparison.png")
        print(f"   - best_model_radar.png")
        print(f"   - model_analysis_report.json")
        print(f"   - model_analysis_report.txt")
        
        if success:
            print(f"\n🚀 PRÓXIMOS PASOS:")
            print(f"   1. Revisar el reporte de análisis")
            print(f"   2. Integrar el mejor modelo en tu aplicación")
            print(f"   3. Probar con datos reales")
            print(f"   4. Configurar monitoreo en producción")

def main():
    """Función principal"""
    
    parser = argparse.ArgumentParser(description='Workflow completo de entrenamiento YOLO')
    parser.add_argument('--model_type', type=str, choices=['dni', 'invoices'], required=True,
                       help='Tipo de modelo a entrenar')
    parser.add_argument('--no-hyperopt', action='store_true',
                       help='Saltar optimización de hiperparámetros')
    parser.add_argument('--use-cv', action='store_true',
                       help='Usar validación cruzada')
    parser.add_argument('--no-monitoring', action='store_true',
                       help='Desactivar monitoreo en tiempo real')
    parser.add_argument('--n-trials', type=int, default=50,
                       help='Número de trials para optimización')
    parser.add_argument('--epochs', type=int, default=300,
                       help='Número de épocas para entrenamiento final')
    
    args = parser.parse_args()
    
    workflow = CompleteTrainingWorkflow()
    
    results = workflow.run_complete_workflow(
        model_type=args.model_type,
        use_hyperopt=not args.no_hyperopt,
        use_cv=args.use_cv,
        use_monitoring=not args.no_monitoring,
        n_trials=args.n_trials,
        final_epochs=args.epochs
    )
    
    sys.exit(0 if results['success'] else 1)

if __name__ == "__main__":
    main()
