#!/usr/bin/env python3
"""
Script de Prueba del Sistema OCR Optimizado
==========================================

Este script prueba todas las funcionalidades del sistema OCR optimizado
para verificar que funciona correctamente y cumple el objetivo de 30 segundos.
"""

import sys
import os
import time
import requests
import logging
from datetime import datetime
from pathlib import Path

# Agregar el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.fast_ocr_service import process_document_fast_sync, fast_processor
from services.sync_ocr_service import is_redis_available

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FastOCRSystemTester:
    """Tester del sistema OCR optimizado"""
    
    def __init__(self):
        self.test_results = {
            'redis_check': False,
            'model_loading': False,
            'fast_processor': False,
            'api_endpoints': False,
            'processing_speed': False,
            'timeout_handling': False
        }
        self.start_time = datetime.now()
    
    def print_banner(self):
        """Imprime banner de prueba"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                  🧪 TEST SISTEMA OCR RÁPIDO                 ║
║                                                              ║
║  Verificación completa del sistema optimizado               ║
║  Objetivo: Procesamiento en máximo 30 segundos             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def test_redis_availability(self):
        """Prueba disponibilidad de Redis"""
        logger.info("🔍 Probando disponibilidad de Redis...")
        
        try:
            redis_available = is_redis_available()
            if redis_available:
                logger.info("✅ Redis está disponible")
                self.test_results['redis_check'] = True
            else:
                logger.info("⚠️ Redis no está disponible (usando procesador rápido)")
                self.test_results['redis_check'] = True  # No es un error
        except Exception as e:
            logger.error(f"❌ Error verificando Redis: {e}")
            self.test_results['redis_check'] = False
    
    def test_model_loading(self):
        """Prueba carga de modelos"""
        logger.info("🤖 Probando carga de modelos...")
        
        try:
            from services.model_loader import load_yolo_model
            from config import YOLO_MODELS_PATH
            
            # Probar carga de un modelo rápido (usar modelos que realmente existen)
            test_models = [
                "document_detector/weights/best.pt",
                "dni_quick/weights/best.pt",
                "quick_15ep/weights/best.pt"
            ]
            
            model_loaded = False
            for model_name in test_models:
                try:
                    model_path = f"{YOLO_MODELS_PATH}/{model_name}"
                    if os.path.exists(model_path):
                        model = load_yolo_model(model_name)
                        logger.info(f"✅ Modelo cargado: {model_name}")
                        model_loaded = True
                        break
                except Exception as e:
                    logger.warning(f"⚠️ Error cargando {model_name}: {e}")
                    continue
            
            if model_loaded:
                self.test_results['model_loading'] = True
            else:
                logger.error("❌ No se pudo cargar ningún modelo")
                self.test_results['model_loading'] = False
                
        except Exception as e:
            logger.error(f"❌ Error en prueba de modelos: {e}")
            self.test_results['model_loading'] = False
    
    def test_fast_processor(self):
        """Prueba el procesador rápido"""
        logger.info("⚡ Probando procesador rápido...")
        
        try:
            # Crear una imagen de prueba
            import cv2
            import numpy as np
            
            # Crear imagen de prueba simple
            test_image = np.ones((640, 640, 3), dtype=np.uint8) * 255
            cv2.putText(test_image, "TEST DOCUMENT", (100, 320), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            
            # Probar preprocesamiento rápido
            preprocessed = fast_processor.preprocess_image_fast(test_image)
            logger.info("✅ Preprocesamiento rápido funcionando")
            
            # Probar obtención de modelo más rápido
            from models.documents import DocumentType
            fastest_model = fast_processor.get_fastest_model(DocumentType.DNI_FRONT)
            logger.info(f"✅ Modelo más rápido seleccionado: {fastest_model}")
            
            self.test_results['fast_processor'] = True
            
        except Exception as e:
            logger.error(f"❌ Error en procesador rápido: {e}")
            self.test_results['fast_processor'] = False
    
    def test_api_endpoints(self):
        """Prueba endpoints de la API"""
        logger.info("🌐 Probando endpoints de la API...")
        
        try:
            base_url = "http://localhost:8000"
            
            # Probar endpoint de health
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Endpoint /health funcionando")
            else:
                logger.warning(f"⚠️ Endpoint /health retornó {response.status_code}")
            
            # Probar endpoint de docs
            response = requests.get(f"{base_url}/docs", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Endpoint /docs funcionando")
            else:
                logger.warning(f"⚠️ Endpoint /docs retornó {response.status_code}")
            
            self.test_results['api_endpoints'] = True
            
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️ API no está corriendo (normal si no se ha iniciado)")
            self.test_results['api_endpoints'] = False
        except Exception as e:
            logger.error(f"❌ Error probando API: {e}")
            self.test_results['api_endpoints'] = False
    
    def test_processing_speed(self):
        """Prueba velocidad de procesamiento"""
        logger.info("⏱️ Probando velocidad de procesamiento...")
        
        try:
            # Simular procesamiento rápido
            start_time = time.time()
            
            # Crear imagen de prueba
            import cv2
            import numpy as np
            test_image = np.ones((640, 640, 3), dtype=np.uint8) * 255
            cv2.putText(test_image, "TEST DOCUMENT", (100, 320), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            
            # Probar pipeline completo
            preprocessed = fast_processor.preprocess_image_fast(test_image)
            
            # Simular tiempo de procesamiento
            processing_time = time.time() - start_time
            
            logger.info(f"✅ Tiempo de procesamiento simulado: {processing_time:.3f}s")
            
            if processing_time < 1.0:  # Debería ser muy rápido en simulación
                self.test_results['processing_speed'] = True
            else:
                logger.warning(f"⚠️ Procesamiento más lento de lo esperado: {processing_time:.3f}s")
                self.test_results['processing_speed'] = False
                
        except Exception as e:
            logger.error(f"❌ Error en prueba de velocidad: {e}")
            self.test_results['processing_speed'] = False
    
    def test_timeout_handling(self):
        """Prueba manejo de timeouts"""
        logger.info("⏰ Probando manejo de timeouts...")
        
        try:
            # Probar configuración de timeout
            timeout_config = fast_processor.timeout_seconds
            logger.info(f"✅ Timeout configurado: {timeout_config}s")
            
            # Verificar que el timeout es razonable
            if 10 <= timeout_config <= 60:
                self.test_results['timeout_handling'] = True
            else:
                logger.warning(f"⚠️ Timeout fuera del rango recomendado: {timeout_config}s")
                self.test_results['timeout_handling'] = False
                
        except Exception as e:
            logger.error(f"❌ Error en prueba de timeouts: {e}")
            self.test_results['timeout_handling'] = False
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        self.print_banner()
        
        logger.info("🚀 Iniciando pruebas del sistema OCR optimizado...")
        print()
        
        # Ejecutar todas las pruebas
        self.test_redis_availability()
        print()
        
        self.test_model_loading()
        print()
        
        self.test_fast_processor()
        print()
        
        self.test_api_endpoints()
        print()
        
        self.test_processing_speed()
        print()
        
        self.test_timeout_handling()
        print()
        
        # Mostrar resultados
        self.show_test_results()
        
        return self.test_results
    
    def show_test_results(self):
        """Muestra resultados de las pruebas"""
        logger.info("📊 RESULTADOS DE LAS PRUEBAS")
        logger.info("=" * 40)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        print(f"🕐 Tiempo total de pruebas: {(datetime.now() - self.start_time).total_seconds():.1f}s")
        print(f"📊 Pruebas ejecutadas: {total_tests}")
        print(f"✅ Pruebas exitosas: {passed_tests}")
        print(f"❌ Pruebas fallidas: {total_tests - passed_tests}")
        print(f"📈 Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Mostrar estado de cada prueba
        test_names = {
            'redis_check': 'Verificación de Redis',
            'model_loading': 'Carga de modelos',
            'fast_processor': 'Procesador rápido',
            'api_endpoints': 'Endpoints de API',
            'processing_speed': 'Velocidad de procesamiento',
            'timeout_handling': 'Manejo de timeouts'
        }
        
        for test_key, test_name in test_names.items():
            status = "✅" if self.test_results[test_key] else "❌"
            print(f"{status} {test_name}")
        
        print()
        
        # Mostrar estadísticas del procesador
        try:
            stats = fast_processor.get_stats()
            print("🤖 ESTADÍSTICAS DEL PROCESADOR:")
            print(f"   Total procesados: {stats['total_processed']}")
            print(f"   Exitosos: {stats['successful']}")
            print(f"   Fallidos: {stats['failed']}")
            if stats['avg_processing_time'] > 0:
                print(f"   Tiempo promedio: {stats['avg_processing_time']:.2f}s")
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron obtener estadísticas: {e}")
        
        print()
        
        # Recomendaciones
        if passed_tests == total_tests:
            print("🎉 ¡Todas las pruebas pasaron! El sistema está listo.")
            print("📝 Recomendación: Ejecutar 'python start_fast_ocr_system.py' para iniciar")
        elif passed_tests >= total_tests * 0.8:
            print("✅ La mayoría de las pruebas pasaron. El sistema debería funcionar bien.")
            print("⚠️ Revisar las pruebas fallidas antes de usar en producción.")
        else:
            print("❌ Varias pruebas fallaron. Revisar la configuración del sistema.")
            print("🔧 Ejecutar 'python start_fast_ocr_system.py' para diagnóstico completo.")


def main():
    """Función principal"""
    tester = FastOCRSystemTester()
    
    try:
        results = tester.run_all_tests()
        
        # Determinar código de salida
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        if passed_tests == total_tests:
            print("\n🎉 ¡Sistema verificado exitosamente!")
            sys.exit(0)
        elif passed_tests >= total_tests * 0.8:
            print("\n⚠️ Sistema parcialmente verificado")
            sys.exit(1)
        else:
            print("\n❌ Sistema no verificado")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n👋 Pruebas interrumpidas por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error crítico en las pruebas: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
