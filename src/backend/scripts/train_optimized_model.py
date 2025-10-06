#!/usr/bin/env python3
"""
Script de entrenamiento optimizado para modelo YOLO de facturas argentinas
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path
import time
from datetime import datetime

class YOLOTrainer:
    def __init__(self):
        self.project_dir = Path("models/yolo_models")
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración de entrenamiento optimizada
        self.training_configs = {
            "basic": {
                "epochs": 50,
                "batch": 8,
                "imgsz": 640,
                "lr0": 0.01,
                "patience": 15,
                "description": "Entrenamiento básico - 50 épocas"
            },
            "intermediate": {
                "epochs": 100,
                "batch": 4,
                "imgsz": 640,
                "lr0": 0.005,
                "patience": 25,
                "description": "Entrenamiento intermedio - 100 épocas"
            },
            "advanced": {
                "epochs": 200,
                "batch": 2,
                "imgsz": 640,
                "lr0": 0.003,
                "patience": 50,
                "description": "Entrenamiento avanzado - 200 épocas"
            }
        }
    
    def check_environment(self):
        """Verifica que el entorno esté configurado correctamente"""
        print("🔍 Verificando entorno de entrenamiento...")
        
        # Verificar que ultralytics esté instalado
        try:
            import ultralytics
            print(f"✅ Ultralytics instalado: {ultralytics.__version__}")
        except ImportError:
            print("❌ Ultralytics no está instalado")
            return False
        
        # Verificar que exista el modelo base
        model_path = Path("models/yolo_models/yolov8n.pt")
        if not model_path.exists():
            print("❌ Modelo base yolov8n.pt no encontrado")
            print("   Descargando modelo base...")
            try:
                from ultralytics import YOLO
                model = YOLO('yolov8n.pt')
                model.save(str(model_path))
                print("✅ Modelo base descargado")
            except Exception as e:
                print(f"❌ Error descargando modelo base: {e}")
                return False
        
        # Verificar datasets
        datasets = [
            "datasets/invoices_argentina_synthetic",
            "datasets/invoices_argentina_advanced"
        ]
        
        available_datasets = []
        for dataset in datasets:
            dataset_path = Path(dataset)
            if dataset_path.exists() and (dataset_path / "dataset.yaml").exists():
                available_datasets.append(dataset)
                print(f"✅ Dataset encontrado: {dataset}")
            else:
                print(f"⚠️  Dataset no encontrado: {dataset}")
        
        if not available_datasets:
            print("❌ No se encontraron datasets válidos")
            return False
        
        return available_datasets
    
    def train_model(self, dataset_path, config_name, model_name):
        """Entrena un modelo con la configuración especificada"""
        config = self.training_configs[config_name]
        dataset_yaml = Path(dataset_path) / "dataset.yaml"
        
        print(f"\n🚀 Iniciando entrenamiento: {config['description']}")
        print(f"   Dataset: {dataset_path}")
        print(f"   Modelo: {model_name}")
        print(f"   Épocas: {config['epochs']}")
        print(f"   Batch: {config['batch']}")
        print(f"   Learning Rate: {config['lr0']}")
        
        # Comando de entrenamiento
        cmd = [
            "python", "-m", "ultralytics.yolo.v8.detect.train",
            f"data={dataset_yaml}",
            f"model=models/yolo_models/yolov8n.pt",
            f"epochs={config['epochs']}",
            f"batch={config['batch']}",
            f"imgsz={config['imgsz']}",
            f"lr0={config['lr0']}",
            f"patience={config['patience']}",
            f"project={self.project_dir}",
            f"name={model_name}",
            "save=True",
            "save_period=10",
            "cache=True",
            "workers=4",
            "device=0" if self.check_gpu() else "cpu"
        ]
        
        print(f"   Comando: {' '.join(cmd)}")
        
        # Ejecutar entrenamiento
        start_time = time.time()
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            training_time = time.time() - start_time
            
            print(f"✅ Entrenamiento completado en {training_time/60:.1f} minutos")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en entrenamiento: {e}")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            return False
    
    def check_gpu(self):
        """Verifica si hay GPU disponible"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def evaluate_model(self, model_path, test_images_path):
        """Evalúa el modelo entrenado"""
        print(f"\n📊 Evaluando modelo: {model_path}")
        
        try:
            from ultralytics import YOLO
            model = YOLO(str(model_path))
            
            # Evaluar en dataset de prueba
            results = model.val(data=str(test_images_path))
            
            print("✅ Evaluación completada")
            print(f"   mAP@0.5: {results.box.map50:.3f}")
            print(f"   mAP@0.5:0.95: {results.box.map:.3f}")
            print(f"   Precision: {results.box.mp:.3f}")
            print(f"   Recall: {results.box.mr:.3f}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error en evaluación: {e}")
            return None
    
    def run_training_pipeline(self):
        """Ejecuta el pipeline completo de entrenamiento"""
        print("🚀 PIPELINE DE ENTRENAMIENTO YOLO - FACTURAS ARGENTINAS")
        print("=" * 60)
        
        # Verificar entorno
        available_datasets = self.check_environment()
        if not available_datasets:
            print("❌ No se puede continuar sin datasets válidos")
            return False
        
        # Seleccionar dataset (usar el más avanzado si está disponible)
        if "datasets/invoices_argentina_advanced" in available_datasets:
            dataset_path = "datasets/invoices_argentina_advanced"
            print(f"📁 Usando dataset avanzado: {dataset_path}")
        else:
            dataset_path = available_datasets[0]
            print(f"📁 Usando dataset: {dataset_path}")
        
        # Entrenar modelos con diferentes configuraciones
        models_trained = []
        
        for config_name in ["basic", "intermediate", "advanced"]:
            model_name = f"argentina_invoices_{config_name}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            
            print(f"\n{'='*60}")
            print(f"ENTRENANDO MODELO: {config_name.upper()}")
            print(f"{'='*60}")
            
            success = self.train_model(dataset_path, config_name, model_name)
            
            if success:
                models_trained.append({
                    "name": model_name,
                    "config": config_name,
                    "path": self.project_dir / model_name / "weights" / "best.pt"
                })
                print(f"✅ Modelo {config_name} entrenado exitosamente")
            else:
                print(f"❌ Error entrenando modelo {config_name}")
        
        # Evaluar modelos entrenados
        if models_trained:
            print(f"\n{'='*60}")
            print("EVALUACIÓN DE MODELOS")
            print(f"{'='*60}")
            
            for model_info in models_trained:
                if model_info["path"].exists():
                    self.evaluate_model(model_info["path"], dataset_path)
                else:
                    print(f"⚠️  Modelo {model_info['name']} no encontrado para evaluación")
        
        # Resumen final
        print(f"\n{'='*60}")
        print("RESUMEN FINAL")
        print(f"{'='*60}")
        print(f"✅ Modelos entrenados: {len(models_trained)}")
        
        for model_info in models_trained:
            if model_info["path"].exists():
                print(f"   - {model_info['name']}: {model_info['path']}")
        
        print(f"\n🎯 Próximos pasos:")
        print("1. Revisar métricas de entrenamiento en los directorios de modelos")
        print("2. Probar los modelos con imágenes reales")
        print("3. Seleccionar el mejor modelo para producción")
        print("4. Integrar el modelo seleccionado en el sistema OCR")
        
        return True

def main():
    """Función principal"""
    trainer = YOLOTrainer()
    success = trainer.run_training_pipeline()
    
    if success:
        print("\n🎉 Pipeline de entrenamiento completado exitosamente!")
    else:
        print("\n❌ Pipeline de entrenamiento falló")
        sys.exit(1)

if __name__ == "__main__":
    main()
