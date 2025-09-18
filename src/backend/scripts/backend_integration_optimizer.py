#!/usr/bin/env python3
"""
Optimizador de integración de modelos en el backend
Mejora la carga, cache y rendimiento de modelos YOLO
"""

import os
import json
import time
import psutil
from pathlib import Path
from ultralytics import YOLO
import torch
import threading
from typing import Dict, Optional, List
import logging

class BackendIntegrationOptimizer:
    """Optimizador de integración de modelos en el backend"""
    
    def __init__(self):
        self.models_cache = {}
        self.model_metadata = {}
        self.performance_metrics = {}
        self.logger = self.setup_logging()
        
    def setup_logging(self):
        """Configura el sistema de logging"""
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/model_optimization.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def analyze_current_integration(self):
        """Analiza la integración actual de modelos en el backend"""
        
        print("🔍 ANALIZANDO INTEGRACIÓN ACTUAL")
        print("=" * 50)
        
        # Verificar servicios existentes
        services_path = Path("services")
        integration_analysis = {
            'model_loader': self.analyze_model_loader(),
            'ocr_service': self.analyze_ocr_service(),
            'preprocessing_service': self.analyze_preprocessing_service(),
            'model_paths': self.analyze_model_paths(),
            'performance_issues': []
        }
        
        # Mostrar resultados
        print(f"📦 Model Loader: {'✅' if integration_analysis['model_loader']['exists'] else '❌'}")
        print(f"🔍 OCR Service: {'✅' if integration_analysis['ocr_service']['exists'] else '❌'}")
        print(f"🔄 Preprocessing Service: {'✅' if integration_analysis['preprocessing_service']['exists'] else '❌'}")
        
        return integration_analysis
    
    def analyze_model_loader(self):
        """Analiza el servicio de carga de modelos"""
        
        model_loader_path = Path("services/model_loader.py")
        
        if not model_loader_path.exists():
            return {'exists': False, 'issues': ['Archivo no encontrado']}
        
        with open(model_loader_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        features = []
        
        # Verificar características
        if 'cache' in content.lower():
            features.append('Cache implementado')
        else:
            issues.append('Sin sistema de cache')
        
        if 'threading' in content or 'async' in content:
            features.append('Carga asíncrona')
        else:
            issues.append('Carga síncrona (puede ser lenta)')
        
        if 'error_handling' in content or 'try:' in content:
            features.append('Manejo de errores')
        else:
            issues.append('Manejo de errores limitado')
        
        if 'performance' in content or 'optimize' in content:
            features.append('Optimizaciones de rendimiento')
        else:
            issues.append('Sin optimizaciones específicas')
        
        return {
            'exists': True,
            'features': features,
            'issues': issues,
            'size_kb': model_loader_path.stat().st_size / 1024
        }
    
    def analyze_ocr_service(self):
        """Analiza el servicio de OCR"""
        
        ocr_service_path = Path("services/ocr_service.py")
        
        if not ocr_service_path.exists():
            return {'exists': False, 'issues': ['Archivo no encontrado']}
        
        with open(ocr_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        features = []
        
        # Verificar características
        if 'yolo' in content.lower():
            features.append('Integración con YOLO')
        else:
            issues.append('Sin integración con YOLO')
        
        if 'confidence' in content or 'conf=' in content:
            features.append('Umbral de confianza configurable')
        else:
            issues.append('Umbral de confianza fijo')
        
        if 'batch' in content.lower():
            features.append('Procesamiento por lotes')
        else:
            issues.append('Procesamiento individual')
        
        if 'cache' in content.lower():
            features.append('Sistema de cache')
        else:
            issues.append('Sin cache')
        
        return {
            'exists': True,
            'features': features,
            'issues': issues,
            'size_kb': ocr_service_path.stat().st_size / 1024
        }
    
    def analyze_preprocessing_service(self):
        """Analiza el servicio de preprocesamiento"""
        
        preprocessing_path = Path("services/preprocessing_service.py")
        
        if not preprocessing_path.exists():
            return {'exists': False, 'issues': ['Archivo no encontrado']}
        
        with open(preprocessing_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        features = []
        
        # Verificar características
        if 'opencv' in content.lower() or 'cv2' in content:
            features.append('OpenCV integrado')
        else:
            issues.append('Sin OpenCV')
        
        if 'resize' in content or 'rescale' in content:
            features.append('Redimensionamiento de imágenes')
        else:
            issues.append('Sin redimensionamiento')
        
        if 'normalize' in content or 'normalization' in content:
            features.append('Normalización de imágenes')
        else:
            issues.append('Sin normalización')
        
        return {
            'exists': True,
            'features': features,
            'issues': issues,
            'size_kb': preprocessing_path.stat().st_size / 1024
        }
    
    def analyze_model_paths(self):
        """Analiza las rutas de modelos disponibles"""
        
        models_path = Path("models/yolo_models")
        
        if not models_path.exists():
            return {'exists': False, 'models': []}
        
        models = []
        for model_dir in models_path.iterdir():
            if model_dir.is_dir() and (model_dir / "weights").exists():
                weights_dir = model_dir / "weights"
                best_model = weights_dir / "best.pt"
                last_model = weights_dir / "last.pt"
                
                model_info = {
                    'name': model_dir.name,
                    'best_exists': best_model.exists(),
                    'last_exists': last_model.exists(),
                    'size_mb': 0,
                    'ready_for_production': False
                }
                
                if best_model.exists():
                    model_info['size_mb'] = best_model.stat().st_size / (1024 * 1024)
                    model_info['ready_for_production'] = True
                
                models.append(model_info)
        
        return {
            'exists': True,
            'models': models,
            'total_models': len(models)
        }
    
    def create_optimized_model_loader(self):
        """Crea un modelo loader optimizado"""
        
        print("\n🔧 CREANDO MODEL LOADER OPTIMIZADO")
        print("=" * 50)
        
        optimized_loader = '''#!/usr/bin/env python3
"""
Model Loader Optimizado para Backend
Incluye cache, carga asíncrona y optimizaciones de rendimiento
"""

import os
import time
import threading
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
from ultralytics import YOLO
import torch
import psutil
from functools import lru_cache

class OptimizedModelLoader:
    """Cargador de modelos optimizado con cache y carga asíncrona"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models_cache: Dict[str, YOLO] = {}
        self.model_metadata: Dict[str, Dict] = {}
        self.loading_threads: Dict[str, threading.Thread] = {}
        self.model_configs = self.load_model_configs()
        
        # Configuración de rendimiento
        self.max_models_in_memory = 3
        self.model_load_timeout = 30
        self.enable_gpu_optimization = torch.cuda.is_available()
        
        self.logger.info("ModelLoader optimizado inicializado")
    
    def load_model_configs(self) -> Dict[str, Dict]:
        """Carga configuraciones de modelos desde archivo JSON"""
        
        config_path = Path("configs/model_configs.json")
        
        default_configs = {
            "dni": {
                "path": "models/yolo_models/dni_optimized/weights/best.pt",
                "confidence": 0.5,
                "device": "auto",
                "batch_size": 1,
                "priority": 1
            },
            "invoices": {
                "path": "models/yolo_models/invoices_optimized/weights/best.pt",
                "confidence": 0.4,
                "device": "auto",
                "batch_size": 1,
                "priority": 2
            }
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error cargando configuraciones: {e}")
        
        return default_configs
    
    @lru_cache(maxsize=10)
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Obtiene información del modelo (con cache)"""
        
        if model_name not in self.model_configs:
            return None
        
        config = self.model_configs[model_name]
        model_path = Path(config["path"])
        
        if not model_path.exists():
            return None
        
        return {
            "name": model_name,
            "path": str(model_path),
            "size_mb": model_path.stat().st_size / (1024 * 1024),
            "exists": True,
            "config": config
        }
    
    def preload_models(self, model_names: List[str] = None):
        """Precarga modelos en background"""
        
        if model_names is None:
            model_names = list(self.model_configs.keys())
        
        self.logger.info(f"Precargando modelos: {model_names}")
        
        for model_name in model_names:
            if model_name not in self.loading_threads:
                thread = threading.Thread(
                    target=self._load_model_async,
                    args=(model_name,),
                    daemon=True
                )
                self.loading_threads[model_name] = thread
                thread.start()
    
    def _load_model_async(self, model_name: str):
        """Carga un modelo de forma asíncrona"""
        
        try:
            self.logger.info(f"Cargando modelo {model_name} en background...")
            start_time = time.time()
            
            model_info = self.get_model_info(model_name)
            if not model_info:
                self.logger.error(f"Modelo {model_name} no encontrado")
                return
            
            # Cargar modelo
            model = YOLO(model_info["path"])
            
            # Optimizaciones de GPU
            if self.enable_gpu_optimization:
                model.to('cuda')
                torch.backends.cudnn.benchmark = True
            
            # Guardar en cache
            self.models_cache[model_name] = model
            self.model_metadata[model_name] = {
                "loaded_at": time.time(),
                "load_time": time.time() - start_time,
                "device": str(model.device),
                "config": model_info["config"]
            }
            
            self.logger.info(f"Modelo {model_name} cargado en {time.time() - start_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error cargando modelo {model_name}: {e}")
        finally:
            # Limpiar thread
            if model_name in self.loading_threads:
                del self.loading_threads[model_name]
    
    def get_model(self, model_name: str, wait_for_load: bool = True) -> Optional[YOLO]:
        """Obtiene un modelo del cache o lo carga si es necesario"""
        
        # Verificar si ya está cargado
        if model_name in self.models_cache:
            return self.models_cache[model_name]
        
        # Verificar si está cargando
        if model_name in self.loading_threads:
            if wait_for_load:
                self.loading_threads[model_name].join(timeout=self.model_load_timeout)
                return self.models_cache.get(model_name)
            else:
                return None
        
        # Cargar inmediatamente
        self._load_model_async(model_name)
        if wait_for_load:
            time.sleep(0.1)  # Pequeña pausa para permitir carga
            return self.models_cache.get(model_name)
        
        return None
    
    def detect_fields(self, image_path: str, model_name: str, 
                     confidence: float = None, **kwargs) -> List[Dict]:
        """Detecta campos en una imagen usando el modelo especificado"""
        
        model = self.get_model(model_name)
        if not model:
            raise ValueError(f"Modelo {model_name} no disponible")
        
        # Usar confianza del modelo si no se especifica
        if confidence is None:
            confidence = self.model_configs[model_name].get("confidence", 0.5)
        
        try:
            # Procesar imagen
            results = model(image_path, conf=confidence, **kwargs)
            
            detections = []
            for r in results:
                if r.boxes is not None:
                    for box in r.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        conf = box.conf[0].item()
                        cls = int(box.cls[0].item())
                        class_name = model.names[cls]
                        
                        detections.append({
                            'class': class_name,
                            'confidence': conf,
                            'bbox': [x1, y1, x2, y2],
                            'model': model_name
                        })
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Error en detección con modelo {model_name}: {e}")
            return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de rendimiento del sistema"""
        
        metrics = {
            "models_loaded": len(self.models_cache),
            "models_loading": len(self.loading_threads),
            "memory_usage_mb": psutil.Process().memory_info().rss / (1024 * 1024),
            "gpu_available": torch.cuda.is_available(),
            "cache_hit_rate": self._calculate_cache_hit_rate()
        }
        
        if torch.cuda.is_available():
            metrics["gpu_memory_used_mb"] = torch.cuda.memory_allocated() / (1024 * 1024)
            metrics["gpu_memory_total_mb"] = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
        
        return metrics
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calcula la tasa de aciertos del cache"""
        
        # Implementación simplificada
        total_requests = len(self.models_cache) + len(self.loading_threads)
        if total_requests == 0:
            return 1.0
        
        return len(self.models_cache) / total_requests
    
    def cleanup_unused_models(self):
        """Limpia modelos no utilizados del cache"""
        
        if len(self.models_cache) <= self.max_models_in_memory:
            return
        
        # Ordenar por tiempo de carga (más antiguos primero)
        sorted_models = sorted(
            self.model_metadata.items(),
            key=lambda x: x[1]["loaded_at"]
        )
        
        # Eliminar modelos más antiguos
        models_to_remove = len(self.models_cache) - self.max_models_in_memory
        for model_name, _ in sorted_models[:models_to_remove]:
            if model_name in self.models_cache:
                del self.models_cache[model_name]
                del self.model_metadata[model_name]
                self.logger.info(f"Modelo {model_name} removido del cache")
    
    def shutdown(self):
        """Cierra el loader y limpia recursos"""
        
        self.logger.info("Cerrando ModelLoader...")
        
        # Esperar a que terminen los threads de carga
        for thread in self.loading_threads.values():
            thread.join(timeout=5)
        
        # Limpiar cache
        self.models_cache.clear()
        self.model_metadata.clear()
        
        # Limpiar memoria GPU
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.logger.info("ModelLoader cerrado correctamente")

# Instancia global
model_loader = OptimizedModelLoader()

# Funciones de conveniencia
def get_model(model_name: str) -> Optional[YOLO]:
    """Obtiene un modelo por nombre"""
    return model_loader.get_model(model_name)

def detect_fields(image_path: str, model_name: str, **kwargs) -> List[Dict]:
    """Detecta campos en una imagen"""
    return model_loader.detect_fields(image_path, model_name, **kwargs)

def preload_models(model_names: List[str] = None):
    """Precarga modelos"""
    model_loader.preload_models(model_names)

def get_performance_metrics() -> Dict[str, Any]:
    """Obtiene métricas de rendimiento"""
    return model_loader.get_performance_metrics()
'''
        
        # Crear directorio de configs si no existe
        configs_dir = Path("configs")
        configs_dir.mkdir(exist_ok=True)
        
        # Guardar modelo loader optimizado
        with open("services/optimized_model_loader.py", 'w', encoding='utf-8') as f:
            f.write(optimized_loader)
        
        # Crear archivo de configuración de modelos
        model_configs = {
            "dni": {
                "path": "models/yolo_models/dni_optimized/weights/best.pt",
                "confidence": 0.5,
                "device": "auto",
                "batch_size": 1,
                "priority": 1,
                "description": "Modelo para detección de campos en DNI"
            },
            "invoices": {
                "path": "models/yolo_models/invoices_optimized/weights/best.pt",
                "confidence": 0.4,
                "device": "auto",
                "batch_size": 1,
                "priority": 2,
                "description": "Modelo para detección de campos en facturas"
            }
        }
        
        with open("configs/model_configs.json", 'w', encoding='utf-8') as f:
            json.dump(model_configs, f, indent=2, ensure_ascii=False)
        
        print("✅ Model Loader optimizado creado")
        print("✅ Configuración de modelos creada")
        
        return True
    
    def create_optimized_ocr_service(self):
        """Crea un servicio de OCR optimizado"""
        
        print("\n🔧 CREANDO OCR SERVICE OPTIMIZADO")
        print("=" * 50)
        
        optimized_ocr = '''#!/usr/bin/env python3
"""
OCR Service Optimizado
Integración mejorada con modelos YOLO y optimizaciones de rendimiento
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import cv2
import numpy as np
import pytesseract
from PIL import Image
import json

# Importar el modelo loader optimizado
from services.optimized_model_loader import model_loader, detect_fields

class OptimizedOCRService:
    """Servicio de OCR optimizado con detección YOLO"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.preprocessing_config = self.load_preprocessing_config()
        self.tesseract_config = self.load_tesseract_config()
        
        # Preload modelos críticos
        model_loader.preload_models(['dni', 'invoices'])
        
        self.logger.info("OCR Service optimizado inicializado")
    
    def load_preprocessing_config(self) -> Dict:
        """Carga configuración de preprocesamiento"""
        
        config_path = Path("configs/preprocessing_config.json")
        
        default_config = {
            "image_size": 640,
            "denoise": True,
            "sharpen": True,
            "contrast_enhancement": True,
            "adaptive_threshold": True,
            "morphology_ops": True
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error cargando configuración: {e}")
        
        return default_config
    
    def load_tesseract_config(self) -> Dict:
        """Carga configuración de Tesseract"""
        
        config_path = Path("configs/tesseract_config.json")
        
        default_config = {
            "lang": "spa+eng",
            "config": "--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,-/:()",
            "timeout": 30
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error cargando configuración Tesseract: {e}")
        
        return default_config
    
    def preprocess_image(self, image_path: Union[str, Path], 
                        target_size: int = None) -> np.ndarray:
        """Preprocesa imagen para optimizar OCR"""
        
        if target_size is None:
            target_size = self.preprocessing_config["image_size"]
        
        # Cargar imagen
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Redimensionar si es necesario
        if max(gray.shape) > target_size:
            scale = target_size / max(gray.shape)
            new_width = int(gray.shape[1] * scale)
            new_height = int(gray.shape[0] * scale)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Denoising
        if self.preprocessing_config["denoise"]:
            gray = cv2.fastNlMeansDenoising(gray)
        
        # Mejora de contraste
        if self.preprocessing_config["contrast_enhancement"]:
            gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(gray)
        
        # Sharpen
        if self.preprocessing_config["sharpen"]:
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            gray = cv2.filter2D(gray, -1, kernel)
        
        # Threshold adaptativo
        if self.preprocessing_config["adaptive_threshold"]:
            gray = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        
        # Operaciones morfológicas
        if self.preprocessing_config["morphology_ops"]:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        
        return gray
    
    def extract_text_from_region(self, image: np.ndarray, bbox: List[float], 
                                config: str = None) -> str:
        """Extrae texto de una región específica de la imagen"""
        
        if config is None:
            config = self.tesseract_config["config"]
        
        try:
            # Extraer región
            x1, y1, x2, y2 = map(int, bbox)
            region = image[y1:y2, x1:x2]
            
            if region.size == 0:
                return ""
            
            # Convertir a PIL Image
            pil_image = Image.fromarray(region)
            
            # OCR con Tesseract
            text = pytesseract.image_to_string(
                pil_image,
                lang=self.tesseract_config["lang"],
                config=config,
                timeout=self.tesseract_config["timeout"]
            )
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error extrayendo texto de región: {e}")
            return ""
    
    def process_document(self, image_path: Union[str, Path], 
                        document_type: str, 
                        confidence: float = None) -> Dict[str, Any]:
        """Procesa un documento completo con detección YOLO + OCR"""
        
        start_time = time.time()
        
        try:
            # Preprocesar imagen
            processed_image = self.preprocess_image(image_path)
            
            # Detectar campos con YOLO
            detections = detect_fields(
                str(image_path), 
                document_type, 
                confidence=confidence
            )
            
            # Extraer texto de cada campo detectado
            extracted_data = {}
            for detection in detections:
                class_name = detection['class']
                bbox = detection['bbox']
                conf = detection['confidence']
                
                # Extraer texto de la región
                text = self.extract_text_from_region(processed_image, bbox)
                
                if text:  # Solo agregar si se extrajo texto
                    extracted_data[class_name] = {
                        'text': text,
                        'confidence': conf,
                        'bbox': bbox
                    }
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'document_type': document_type,
                'extracted_data': extracted_data,
                'detections_count': len(detections),
                'processing_time': processing_time,
                'image_path': str(image_path)
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando documento: {e}")
            return {
                'success': False,
                'error': str(e),
                'document_type': document_type,
                'processing_time': time.time() - start_time
            }
    
    def batch_process_documents(self, image_paths: List[Union[str, Path]], 
                               document_type: str) -> List[Dict[str, Any]]:
        """Procesa múltiples documentos en lote"""
        
        results = []
        
        for image_path in image_paths:
            result = self.process_document(image_path, document_type)
            results.append(result)
        
        return results
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de rendimiento del servicio"""
        
        return {
            "model_loader_metrics": model_loader.get_performance_metrics(),
            "preprocessing_config": self.preprocessing_config,
            "tesseract_config": self.tesseract_config
        }
    
    def optimize_for_document_type(self, document_type: str):
        """Optimiza el servicio para un tipo específico de documento"""
        
        optimizations = {
            "dni": {
                "image_size": 512,
                "denoise": True,
                "sharpen": False,
                "contrast_enhancement": True,
                "adaptive_threshold": True,
                "morphology_ops": False
            },
            "invoices": {
                "image_size": 640,
                "denoise": True,
                "sharpen": True,
                "contrast_enhancement": True,
                "adaptive_threshold": False,
                "morphology_ops": True
            }
        }
        
        if document_type in optimizations:
            self.preprocessing_config.update(optimizations[document_type])
            self.logger.info(f"Optimizado para {document_type}")

# Instancia global
ocr_service = OptimizedOCRService()

# Funciones de conveniencia
def process_document(image_path: Union[str, Path], document_type: str, **kwargs) -> Dict[str, Any]:
    """Procesa un documento"""
    return ocr_service.process_document(image_path, document_type, **kwargs)

def batch_process_documents(image_paths: List[Union[str, Path]], document_type: str) -> List[Dict[str, Any]]:
    """Procesa múltiples documentos"""
    return ocr_service.batch_process_documents(image_paths, document_type)

def get_performance_metrics() -> Dict[str, Any]:
    """Obtiene métricas de rendimiento"""
    return ocr_service.get_performance_metrics()
'''
        
        # Guardar servicio OCR optimizado
        with open("services/optimized_ocr_service.py", 'w', encoding='utf-8') as f:
            f.write(optimized_ocr)
        
        # Crear configuraciones
        preprocessing_config = {
            "image_size": 640,
            "denoise": True,
            "sharpen": True,
            "contrast_enhancement": True,
            "adaptive_threshold": True,
            "morphology_ops": True,
            "document_types": {
                "dni": {
                    "image_size": 512,
                    "denoise": True,
                    "sharpen": False,
                    "contrast_enhancement": True,
                    "adaptive_threshold": True,
                    "morphology_ops": False
                },
                "invoices": {
                    "image_size": 640,
                    "denoise": True,
                    "sharpen": True,
                    "contrast_enhancement": True,
                    "adaptive_threshold": False,
                    "morphology_ops": True
                }
            }
        }
        
        tesseract_config = {
            "lang": "spa+eng",
            "config": "--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,-/:()",
            "timeout": 30,
            "document_types": {
                "dni": {
                    "config": "--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                },
                "invoices": {
                    "config": "--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,-/:()$"
                }
            }
        }
        
        # Crear directorio de configs
        configs_dir = Path("configs")
        configs_dir.mkdir(exist_ok=True)
        
        with open("configs/preprocessing_config.json", 'w', encoding='utf-8') as f:
            json.dump(preprocessing_config, f, indent=2, ensure_ascii=False)
        
        with open("configs/tesseract_config.json", 'w', encoding='utf-8') as f:
            json.dump(tesseract_config, f, indent=2, ensure_ascii=False)
        
        print("✅ OCR Service optimizado creado")
        print("✅ Configuraciones de preprocesamiento creadas")
        
        return True
    
    def create_integration_guide(self):
        """Crea una guía de integración"""
        
        guide = '''# Guía de Integración de Modelos Optimizados

## 🚀 Servicios Optimizados Creados

### 1. Model Loader Optimizado (`services/optimized_model_loader.py`)

**Características:**
- ✅ Cache inteligente de modelos
- ✅ Carga asíncrona en background
- ✅ Optimizaciones de GPU automáticas
- ✅ Gestión de memoria eficiente
- ✅ Métricas de rendimiento en tiempo real

**Uso:**
```python
from services.optimized_model_loader import get_model, detect_fields

# Obtener modelo
model = get_model('dni')

# Detectar campos
detections = detect_fields('image.jpg', 'dni', confidence=0.5)
```

### 2. OCR Service Optimizado (`services/optimized_ocr_service.py`)

**Características:**
- ✅ Integración completa con YOLO
- ✅ Preprocesamiento inteligente de imágenes
- ✅ Configuración específica por tipo de documento
- ✅ Procesamiento por lotes
- ✅ Extracción de texto optimizada

**Uso:**
```python
from services.optimized_ocr_service import process_document

# Procesar documento
result = process_document('document.jpg', 'dni')
print(result['extracted_data'])
```

## 📁 Archivos de Configuración

### `configs/model_configs.json`
Configuración de modelos YOLO con rutas, confianza y prioridades.

### `configs/preprocessing_config.json`
Configuración de preprocesamiento de imágenes por tipo de documento.

### `configs/tesseract_config.json`
Configuración de Tesseract OCR optimizada.

## 🔧 Integración en el Backend

### 1. Actualizar `services/model_loader.py`
```python
# Reemplazar importación
from services.optimized_model_loader import model_loader as yolo_loader

# Usar en lugar del loader anterior
def detect_document_fields(image_path, document_type):
    return yolo_loader.detect_fields(image_path, document_type)
```

### 2. Actualizar `services/ocr_service.py`
```python
# Reemplazar importación
from services.optimized_ocr_service import ocr_service as optimized_ocr

# Usar en lugar del servicio anterior
def process_document_ocr(image_path, document_type):
    return optimized_ocr.process_document(image_path, document_type)
```

### 3. Actualizar `api/v1/documents.py`
```python
# Agregar endpoint de métricas
@router.get("/performance-metrics")
async def get_performance_metrics():
    from services.optimized_model_loader import get_performance_metrics
    return get_performance_metrics()
```

## 📊 Monitoreo y Métricas

### Métricas Disponibles:
- Modelos cargados en memoria
- Tiempo de carga de modelos
- Uso de memoria RAM/GPU
- Tasa de aciertos del cache
- Tiempo de procesamiento por documento

### Endpoint de Monitoreo:
```
GET /api/v1/performance-metrics
```

## 🚀 Próximos Pasos

1. **Probar servicios optimizados** con datos reales
2. **Entrenar modelos mejorados** con más datos
3. **Implementar métricas de producción**
4. **Configurar monitoreo automático**
5. **Optimizar para casos de uso específicos**

## ⚠️ Consideraciones

- Los servicios optimizados requieren más memoria RAM
- Se recomienda usar GPU para mejor rendimiento
- Configurar límites de memoria según hardware disponible
- Monitorear métricas de rendimiento regularmente
'''
        
        with open("INTEGRATION_GUIDE.md", 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print("✅ Guía de integración creada")
        return True
    
    def run_optimization(self):
        """Ejecuta la optimización completa"""
        
        print("🚀 OPTIMIZACIÓN DE INTEGRACIÓN DEL BACKEND")
        print("=" * 60)
        
        # Analizar integración actual
        analysis = self.analyze_current_integration()
        
        # Crear servicios optimizados
        self.create_optimized_model_loader()
        self.create_optimized_ocr_service()
        self.create_integration_guide()
        
        # Generar reporte
        report = {
            'timestamp': time.time(),
            'analysis': analysis,
            'optimizations_applied': [
                'Model Loader optimizado con cache',
                'OCR Service con integración YOLO',
                'Configuraciones específicas por documento',
                'Sistema de métricas y monitoreo',
                'Guía de integración completa'
            ],
            'next_steps': [
                'Probar servicios optimizados',
                'Entrenar modelos con más datos',
                'Implementar en producción',
                'Configurar monitoreo automático'
            ]
        }
        
        with open("backend_integration_report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ OPTIMIZACIÓN COMPLETADA")
        print("=" * 60)
        print(f"📄 Reporte guardado: backend_integration_report.json")
        print(f"📖 Guía creada: INTEGRATION_GUIDE.md")
        
        return report

def main():
    """Función principal"""
    
    optimizer = BackendIntegrationOptimizer()
    optimizer.run_optimization()

if __name__ == "__main__":
    main()
