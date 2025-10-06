#!/usr/bin/env python3
"""
Script para Optimizar Modelos YOLO para Velocidad
===============================================

Este script optimiza la configuración de los modelos YOLO existentes
para lograr procesamiento en máximo 30 segundos.

Optimizaciones aplicadas:
- Configuración de inferencia rápida
- Reducción de umbrales de confianza
- Optimización de batch size
- Configuración de dispositivo (CPU/GPU)
- Cache de modelos
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Agregar el directorio backend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import YOLO_MODELS_PATH
from services.model_loader import load_yolo_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelOptimizer:
    """Optimizador de modelos YOLO para velocidad"""
    
    def __init__(self):
        self.models_path = Path(YOLO_MODELS_PATH)
        self.optimization_config = {
            'inference_settings': {
                'conf': 0.25,  # Umbral de confianza más bajo para capturar más campos
                'iou': 0.45,   # IoU threshold para NMS
                'max_det': 50,  # Máximo detecciones
                'agnostic_nms': False,
                'half': False,  # FP16 si está disponible
                'device': 'cpu',  # Usar CPU por defecto
                'verbose': False
            },
            'model_settings': {
                'cache_models': True,
                'warmup_runs': 2,  # Calentamiento del modelo
                'batch_size': 1,   # Procesar una imagen a la vez
                'imgsz': 640       # Tamaño de imagen optimizado
            }
        }
        self.results = {}
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Obtiene lista de modelos disponibles con información"""
        models = []
        
        if not self.models_path.exists():
            logger.error(f"Directorio de modelos no encontrado: {self.models_path}")
            return models
        
        for model_dir in self.models_path.iterdir():
            if model_dir.is_dir():
                weights_path = model_dir / "weights" / "best.pt"
                if weights_path.exists():
                    # Obtener información del modelo
                    model_info = {
                        'name': model_dir.name,
                        'path': str(weights_path),
                        'size_mb': weights_path.stat().st_size / (1024 * 1024),
                        'optimized': False,
                        'inference_time': 0.0,
                        'recommended_for': self._classify_model(model_dir.name)
                    }
                    models.append(model_info)
        
        return sorted(models, key=lambda x: x['name'])
    
    def _classify_model(self, model_name: str) -> str:
        """Clasifica el modelo según su nombre"""
        model_name_lower = model_name.lower()
        
        if 'dni' in model_name_lower:
            if 'quick' in model_name_lower:
                return 'DNI - Rápido'
            elif 'optimized' in model_name_lower:
                return 'DNI - Equilibrado'
            else:
                return 'DNI - Estándar'
        elif 'invoice' in model_name_lower or 'factura' in model_name_lower:
            if 'quick' in model_name_lower:
                return 'Facturas - Rápido'
            else:
                return 'Facturas - Estándar'
        elif 'document' in model_name_lower:
            return 'Documentos Genéricos'
        else:
            return 'Genérico'
    
    def benchmark_model(self, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza benchmark de velocidad del modelo"""
        model_name = model_info['name']
        model_path = model_info['path']
        
        logger.info(f"🔬 Benchmarking modelo: {model_name}")
        
        try:
            # Cargar modelo
            start_time = time.time()
            model = load_yolo_model(model_info['path'])
            load_time = time.time() - start_time
            
            # Crear imagen de prueba
            import cv2
            import numpy as np
            test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            
            # Calentamiento del modelo
            warmup_runs = self.optimization_config['model_settings']['warmup_runs']
            for _ in range(warmup_runs):
                _ = model(test_image, **self.optimization_config['inference_settings'])
            
            # Benchmark de inferencia
            inference_times = []
            benchmark_runs = 5
            
            for _ in range(benchmark_runs):
                start_time = time.time()
                results = model(test_image, **self.optimization_config['inference_settings'])
                inference_time = time.time() - start_time
                inference_times.append(inference_time)
            
            # Calcular estadísticas
            avg_inference_time = sum(inference_times) / len(inference_times)
            min_inference_time = min(inference_times)
            max_inference_time = max(inference_times)
            
            # Clasificar velocidad
            if avg_inference_time < 1.0:
                speed_rating = "Muy Rápido"
            elif avg_inference_time < 3.0:
                speed_rating = "Rápido"
            elif avg_inference_time < 5.0:
                speed_rating = "Moderado"
            else:
                speed_rating = "Lento"
            
            benchmark_result = {
                'model_name': model_name,
                'load_time': load_time,
                'avg_inference_time': avg_inference_time,
                'min_inference_time': min_inference_time,
                'max_inference_time': max_inference_time,
                'speed_rating': speed_rating,
                'recommended_for_30s': avg_inference_time < 5.0,
                'fps': 1.0 / avg_inference_time if avg_inference_time > 0 else 0,
                'total_processing_time_estimate': avg_inference_time + 2.0  # +2s para OCR
            }
            
            logger.info(f"   ✅ Tiempo promedio: {avg_inference_time:.3f}s ({speed_rating})")
            logger.info(f"   📊 FPS: {benchmark_result['fps']:.1f}")
            logger.info(f"   ⏱️ Tiempo total estimado: {benchmark_result['total_processing_time_estimate']:.1f}s")
            
            return benchmark_result
            
        except Exception as e:
            logger.error(f"   ❌ Error en benchmark: {e}")
            return {
                'model_name': model_name,
                'error': str(e),
                'avg_inference_time': float('inf'),
                'speed_rating': 'Error',
                'recommended_for_30s': False
            }
    
    def optimize_model_config(self, model_name: str) -> Dict[str, Any]:
        """Optimiza la configuración para un modelo específico"""
        logger.info(f"⚙️ Optimizando configuración para: {model_name}")
        
        # Configuraciones optimizadas por tipo de modelo
        if 'dni' in model_name.lower():
            optimized_config = {
                'conf': 0.2,  # Más permisivo para DNI
                'iou': 0.4,
                'max_det': 30,
                'imgsz': 512,  # Imagen más pequeña para DNI
                'device': 'cpu'
            }
        elif 'invoice' in model_name.lower():
            optimized_config = {
                'conf': 0.3,  # Más estricto para facturas
                'iou': 0.5,
                'max_det': 50,
                'imgsz': 640,
                'device': 'cpu'
            }
        else:
            optimized_config = {
                'conf': 0.25,
                'iou': 0.45,
                'max_det': 40,
                'imgsz': 640,
                'device': 'cpu'
            }
        
        logger.info(f"   🎯 Configuración optimizada: {optimized_config}")
        return optimized_config
    
    def generate_recommendations(self, benchmark_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera recomendaciones basadas en los benchmarks"""
        logger.info("📋 Generando recomendaciones...")
        
        # Filtrar modelos exitosos
        successful_models = [r for r in benchmark_results if 'error' not in r]
        
        # Clasificar por tipo y velocidad
        dni_models = [r for r in successful_models if 'dni' in r['model_name'].lower()]
        invoice_models = [r for r in successful_models if 'invoice' in r['model_name'].lower()]
        generic_models = [r for r in successful_models if r not in dni_models and r not in invoice_models]
        
        recommendations = {
            'dni_models': {
                'fastest': None,
                'most_accurate': None,
                'recommended': None
            },
            'invoice_models': {
                'fastest': None,
                'most_accurate': None,
                'recommended': None
            },
            'generic_models': {
                'fastest': None,
                'recommended': None
            },
            'overall_recommendations': []
        }
        
        # Recomendaciones para DNI
        if dni_models:
            fastest_dni = min(dni_models, key=lambda x: x['avg_inference_time'])
            recommendations['dni_models']['fastest'] = fastest_dni
            
            # Buscar el más balanceado (rápido pero no el más lento)
            suitable_dni = [r for r in dni_models if r['avg_inference_time'] < 3.0]
            if suitable_dni:
                recommended_dni = min(suitable_dni, key=lambda x: x['avg_inference_time'])
                recommendations['dni_models']['recommended'] = recommended_dni
        
        # Recomendaciones para Facturas
        if invoice_models:
            fastest_invoice = min(invoice_models, key=lambda x: x['avg_inference_time'])
            recommendations['invoice_models']['fastest'] = fastest_invoice
            
            suitable_invoice = [r for r in invoice_models if r['avg_inference_time'] < 4.0]
            if suitable_invoice:
                recommended_invoice = min(suitable_invoice, key=lambda x: x['avg_inference_time'])
                recommendations['invoice_models']['recommended'] = recommended_invoice
        
        # Recomendaciones para modelos genéricos
        if generic_models:
            fastest_generic = min(generic_models, key=lambda x: x['avg_inference_time'])
            recommendations['generic_models']['fastest'] = fastest_generic
            
            suitable_generic = [r for r in generic_models if r['avg_inference_time'] < 5.0]
            if suitable_generic:
                recommended_generic = min(suitable_generic, key=lambda x: x['avg_inference_time'])
                recommendations['generic_models']['recommended'] = recommended_generic
        
        # Recomendaciones generales
        all_suitable = [r for r in successful_models if r['avg_inference_time'] < 5.0]
        if all_suitable:
            recommendations['overall_recommendations'].append(
                f"✅ {len(all_suitable)} modelos cumplen el objetivo de <5s de inferencia"
            )
        else:
            recommendations['overall_recommendations'].append(
                "⚠️ Ningún modelo cumple el objetivo de <5s de inferencia"
            )
        
        return recommendations
    
    def run_optimization(self) -> Dict[str, Any]:
        """Ejecuta el proceso completo de optimización"""
        logger.info("🚀 INICIANDO OPTIMIZACIÓN DE MODELOS")
        logger.info("=" * 50)
        
        start_time = time.time()
        
        # Obtener modelos disponibles
        models = self.get_available_models()
        if not models:
            logger.error("❌ No se encontraron modelos para optimizar")
            return {}
        
        logger.info(f"📦 Encontrados {len(models)} modelos para optimizar")
        
        # Realizar benchmarks
        benchmark_results = []
        for model_info in models:
            result = self.benchmark_model(model_info)
            benchmark_results.append(result)
        
        # Generar recomendaciones
        recommendations = self.generate_recommendations(benchmark_results)
        
        # Crear configuración optimizada
        optimization_result = {
            'timestamp': datetime.now().isoformat(),
            'total_models': len(models),
            'successful_benchmarks': len([r for r in benchmark_results if 'error' not in r]),
            'failed_benchmarks': len([r for r in benchmark_results if 'error' in r]),
            'benchmark_results': benchmark_results,
            'recommendations': recommendations,
            'optimization_config': self.optimization_config,
            'processing_time': time.time() - start_time
        }
        
        # Guardar resultados
        self.save_results(optimization_result)
        
        # Mostrar resumen
        self.print_summary(optimization_result)
        
        return optimization_result
    
    def save_results(self, results: Dict[str, Any]):
        """Guarda los resultados en archivo JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'model_optimization_results_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"💾 Resultados guardados en: {filename}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Imprime resumen de la optimización"""
        logger.info("\n📊 RESUMEN DE OPTIMIZACIÓN")
        logger.info("=" * 50)
        
        print(f"📦 Total de modelos: {results['total_models']}")
        print(f"✅ Benchmarks exitosos: {results['successful_benchmarks']}")
        print(f"❌ Benchmarks fallidos: {results['failed_benchmarks']}")
        print(f"⏱️ Tiempo total: {results['processing_time']:.1f}s")
        
        print(f"\n🎯 RECOMENDACIONES:")
        recs = results['recommendations']
        
        if recs['dni_models']['recommended']:
            model = recs['dni_models']['recommended']
            print(f"   📄 DNI: {model['model_name']} ({model['speed_rating']}, {model['avg_inference_time']:.2f}s)")
        
        if recs['invoice_models']['recommended']:
            model = recs['invoice_models']['recommended']
            print(f"   📋 Facturas: {model['model_name']} ({model['speed_rating']}, {model['avg_inference_time']:.2f}s)")
        
        if recs['generic_models']['recommended']:
            model = recs['generic_models']['recommended']
            print(f"   📄 Genérico: {model['model_name']} ({model['speed_rating']}, {model['avg_inference_time']:.2f}s)")
        
        print(f"\n💡 RECOMENDACIONES GENERALES:")
        for rec in recs['overall_recommendations']:
            print(f"   {rec}")


def main():
    """Función principal"""
    optimizer = ModelOptimizer()
    results = optimizer.run_optimization()
    
    if results:
        print(f"\n✅ Optimización completada exitosamente")
        print(f"📁 Ver archivo de resultados para detalles completos")
    else:
        print(f"\n❌ Error en la optimización")
        sys.exit(1)


if __name__ == "__main__":
    main()
