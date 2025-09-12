#!/usr/bin/env python3
"""
Prueba comprehensiva de todos los modelos YOLO entrenados
"""

import os
import glob
import json
from datetime import datetime
from ultralytics import YOLO
import cv2
import numpy as np

class ModelTester:
    def __init__(self):
        self.results = {}
        self.test_images = {
            'dni': [],
            'invoice': []
        }
        self.load_test_images()
    
    def load_test_images(self):
        """Carga las imágenes de prueba disponibles"""
        # Imágenes DNI
        dni_images = glob.glob("datasets/dni_robust/images/test/*.jpg")
        dni_images.extend(glob.glob("datasets/dni_robust/images/train/*.jpg")[:3])  # Algunas de train también
        self.test_images['dni'] = dni_images[:5]  # Máximo 5 imágenes
        
        # Imágenes Invoice
        invoice_images = glob.glob("datasets/invoices_argentina/images/train/*.jpg")
        invoice_images.extend(glob.glob("models/yolo_models/test_invoice.jpg"))
        self.test_images['invoice'] = [img for img in invoice_images if os.path.exists(img)][:3]
        
        print(f"📸 Imágenes de prueba cargadas:")
        print(f"   DNI: {len(self.test_images['dni'])} imágenes")
        print(f"   Invoice: {len(self.test_images['invoice'])} imágenes")
    
    def get_model_type(self, model_path):
        """Determina el tipo de modelo basado en su nombre"""
        model_name = model_path.split('/')[-3].lower()
        if 'dni' in model_name:
            return 'dni'
        elif 'invoice' in model_name or 'factura' in model_name:
            return 'invoice'
        else:
            return 'unknown'
    
    def test_single_model(self, model_path):
        """Prueba un modelo individual"""
        model_name = model_path.split('/')[-3]
        model_type = self.get_model_type(model_path)
        
        print(f"\n🤖 PROBANDO: {model_name}")
        print("-" * 50)
        
        try:
            # Información básica del modelo
            model_size = os.path.getsize(model_path) / (1024 * 1024)
            print(f"📏 Tamaño: {model_size:.1f} MB")
            
            # Cargar modelo
            model = YOLO(model_path)
            print(f"🏷️  Clases: {len(model.names)} ({list(model.names.values())})")
            
            # Seleccionar imágenes de prueba apropiadas
            if model_type == 'dni' and self.test_images['dni']:
                test_images = self.test_images['dni']
            elif model_type == 'invoice' and self.test_images['invoice']:
                test_images = self.test_images['invoice']
            elif model_type == 'unknown':
                # Probar con ambos tipos
                test_images = self.test_images['dni'][:2] + self.test_images['invoice'][:1]
            else:
                print("⚠️  No hay imágenes de prueba apropiadas")
                return {
                    'model_name': model_name,
                    'model_type': model_type,
                    'size_mb': model_size,
                    'classes': len(model.names),
                    'class_names': list(model.names.values()),
                    'status': 'no_test_images',
                    'detections': []
                }
            
            # Probar con diferentes niveles de confianza
            confidence_levels = [0.1, 0.25, 0.5]
            detection_results = []
            
            for img_path in test_images[:2]:  # Máximo 2 imágenes por modelo
                img_name = os.path.basename(img_path)
                print(f"🖼️  Probando: {img_name}")
                
                for conf in confidence_levels:
                    try:
                        results = model(img_path, conf=conf, verbose=False)
                        
                        detections = 0
                        detection_details = []
                        
                        for r in results:
                            if r.boxes is not None:
                                detections = len(r.boxes)
                                
                                for box in r.boxes:
                                    conf_score = box.conf[0].item()
                                    cls = int(box.cls[0].item())
                                    class_name = model.names[cls]
                                    
                                    detection_details.append({
                                        'class': class_name,
                                        'confidence': conf_score,
                                        'bbox': box.xyxy[0].tolist()
                                    })
                        
                        detection_results.append({
                            'image': img_name,
                            'confidence_threshold': conf,
                            'detections_count': detections,
                            'detections': detection_details
                        })
                        
                        if detections > 0:
                            print(f"   Conf {conf}: {detections} detecciones")
                        
                    except Exception as e:
                        print(f"   ❌ Error con conf {conf}: {str(e)[:50]}")
            
            # Calcular estadísticas
            total_detections = sum(dr['detections_count'] for dr in detection_results)
            avg_detections = total_detections / len(detection_results) if detection_results else 0
            
            result = {
                'model_name': model_name,
                'model_type': model_type,
                'size_mb': model_size,
                'classes': len(model.names),
                'class_names': list(model.names.values()),
                'status': 'tested',
                'total_detections': total_detections,
                'avg_detections_per_test': avg_detections,
                'detection_results': detection_results
            }
            
            print(f"✅ Total detecciones: {total_detections}")
            print(f"📊 Promedio por prueba: {avg_detections:.1f}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            return {
                'model_name': model_name,
                'model_type': model_type,
                'status': 'error',
                'error': str(e)
            }
    
    def test_all_models(self):
        """Prueba todos los modelos disponibles"""
        print("🔍 INICIANDO PRUEBA COMPREHENSIVA DE TODOS LOS MODELOS")
        print("=" * 70)
        
        # Encontrar todos los modelos
        model_paths = glob.glob("models/yolo_models/*/weights/best.pt")
        
        if not model_paths:
            print("❌ No se encontraron modelos entrenados")
            return
        
        print(f"📦 Encontrados {len(model_paths)} modelos para probar")
        
        # Probar cada modelo
        for i, model_path in enumerate(model_paths, 1):
            print(f"\n[{i}/{len(model_paths)}]", end="")
            result = self.test_single_model(model_path)
            self.results[result['model_name']] = result
        
        # Generar reporte final
        self.generate_report()
    
    def generate_report(self):
        """Genera un reporte comprehensivo de todos los resultados"""
        print("\n" + "=" * 70)
        print("📊 REPORTE FINAL DE TODOS LOS MODELOS")
        print("=" * 70)
        
        # Clasificar modelos por tipo
        dni_models = []
        invoice_models = []
        other_models = []
        
        for model_name, result in self.results.items():
            if result.get('model_type') == 'dni':
                dni_models.append(result)
            elif result.get('model_type') == 'invoice':
                invoice_models.append(result)
            else:
                other_models.append(result)
        
        # Reporte por categoría
        self.print_category_report("🆔 MODELOS DNI", dni_models)
        self.print_category_report("🧾 MODELOS INVOICE", invoice_models)
        self.print_category_report("🔧 OTROS MODELOS", other_models)
        
        # Estadísticas generales
        self.print_general_stats()
        
        # Guardar reporte en JSON
        self.save_report()
    
    def print_category_report(self, title, models):
        """Imprime reporte de una categoría de modelos"""
        if not models:
            return
        
        print(f"\n{title} ({len(models)} modelos)")
        print("-" * 50)
        
        # Ordenar por total de detecciones
        models.sort(key=lambda x: x.get('total_detections', 0), reverse=True)
        
        for model in models:
            status = model.get('status', 'unknown')
            if status == 'tested':
                print(f"✅ {model['model_name']}")
                print(f"   📏 {model['size_mb']:.1f}MB | 🏷️ {model['classes']} clases | 🎯 {model['total_detections']} detecciones")
                
                # Mostrar mejores detecciones
                best_results = []
                for dr in model.get('detection_results', []):
                    if dr['detections_count'] > 0:
                        best_results.append(f"{dr['image']}({dr['detections_count']})")
                
                if best_results:
                    print(f"   🏆 Mejores: {', '.join(best_results[:3])}")
                else:
                    print(f"   ⚠️  Sin detecciones exitosas")
                    
            elif status == 'error':
                print(f"❌ {model['model_name']} - Error: {model.get('error', 'Unknown')[:30]}")
            else:
                print(f"⚠️  {model['model_name']} - {status}")
    
    def print_general_stats(self):
        """Imprime estadísticas generales"""
        print(f"\n📈 ESTADÍSTICAS GENERALES")
        print("-" * 30)
        
        total_models = len(self.results)
        tested_models = len([r for r in self.results.values() if r.get('status') == 'tested'])
        error_models = len([r for r in self.results.values() if r.get('status') == 'error'])
        
        total_detections = sum(r.get('total_detections', 0) for r in self.results.values())
        
        print(f"📦 Total modelos: {total_models}")
        print(f"✅ Probados exitosamente: {tested_models}")
        print(f"❌ Con errores: {error_models}")
        print(f"🎯 Total detecciones: {total_detections}")
        
        if tested_models > 0:
            avg_detections = total_detections / tested_models
            print(f"📊 Promedio detecciones por modelo: {avg_detections:.1f}")
        
        # Mejores modelos
        best_models = sorted(
            [r for r in self.results.values() if r.get('status') == 'tested'],
            key=lambda x: x.get('total_detections', 0),
            reverse=True
        )[:3]
        
        if best_models:
            print(f"\n🏆 TOP 3 MODELOS:")
            for i, model in enumerate(best_models, 1):
                print(f"   {i}. {model['model_name']}: {model['total_detections']} detecciones")
    
    def save_report(self):
        """Guarda el reporte en archivo JSON"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_models_tested': len(self.results),
            'test_images_used': self.test_images,
            'results': self.results
        }
        
        report_file = 'comprehensive_model_test_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado: {report_file}")

if __name__ == "__main__":
    tester = ModelTester()
    tester.test_all_models()
    print(f"\n🎉 PRUEBA COMPREHENSIVA COMPLETADA")
    print("=" * 70)
