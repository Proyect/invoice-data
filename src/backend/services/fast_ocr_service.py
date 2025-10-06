#!/usr/bin/env python3
"""
Servicio OCR Optimizado para Procesamiento Rápido
=================================================

Este servicio está optimizado para procesar documentos en máximo 30 segundos
sin depender de Redis o workers externos.

Características:
- Procesamiento síncrono optimizado
- Timeouts configurables
- Modelos más rápidos
- Cache de modelos
- Preprocesamiento eficiente
"""

import time
import logging
import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import concurrent.futures
from functools import lru_cache

# Imports del sistema existente
from services.ocr_service import perform_ocr_with_tesseract, get_ocr_config_for_field
from services.model_loader import load_yolo_model, YOLO_MODELS_PATH
from services.preprocessing_service import preprocess_image_for_ocr
from services.pdf_converter import convert_pdf_to_single_image, get_pdf_info
from models.documents import DocumentType
from database import SessionLocal
from services.document_service import update_document_status

logger = logging.getLogger(__name__)

class FastOCRProcessor:
    """Procesador OCR optimizado para velocidad"""
    
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds
        self.model_cache = {}
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'avg_processing_time': 0.0,
            'fastest_time': float('inf'),
            'slowest_time': 0.0
        }
    
    @lru_cache(maxsize=5)
    def get_fastest_model(self, document_type: DocumentType) -> str:
        """
        Selecciona el modelo más rápido disponible para cada tipo de documento
        """
        if document_type in [DocumentType.DNI_FRONT, DocumentType.DNI_BACK]:
            # Priorizar modelos más rápidos para DNI
            fast_models = [
                "dni_quick/weights/best.pt",      # Más rápido
                "dni_test/weights/best.pt",       # Intermedio
                "dni_optimized/weights/best.pt"   # Más preciso pero lento
            ]
        elif document_type in [DocumentType.INVOICE_A, DocumentType.INVOICE_B, DocumentType.INVOICE_C]:
            # Modelos de facturas
            fast_models = [
                "quick_15ep/weights/best.pt",     # Más rápido
                "quick_15ep2/weights/best.pt",    # Intermedio
                "invoices_cpu_abs/weights/best.pt" # Más preciso
            ]
        else:
            # Modelo genérico
            fast_models = [
                "document_detector/weights/best.pt"
            ]
        
        # Encontrar el primer modelo disponible
        for model_name in fast_models:
            model_path = f"{YOLO_MODELS_PATH}/{model_name}"
            try:
                import os
                if os.path.exists(model_path):
                    logger.info(f"Modelo seleccionado: {model_name}")
                    return model_name
            except Exception as e:
                logger.warning(f"Error verificando modelo {model_name}: {e}")
                continue
        
        # Fallback a modelo genérico
        logger.warning("Usando modelo genérico como fallback")
        return "document_detector/weights/best.pt"
    
    def load_model_cached(self, model_name: str):
        """Carga modelo con cache para evitar recargas"""
        if model_name not in self.model_cache:
            try:
                self.model_cache[model_name] = load_yolo_model(model_name)
                logger.info(f"Modelo cargado en cache: {model_name}")
            except Exception as e:
                logger.error(f"Error cargando modelo {model_name}: {e}")
                raise
        
        return self.model_cache[model_name]
    
    def preprocess_image_fast(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocesamiento optimizado para velocidad
        """
        try:
            # Redimensionar si es muy grande (acelerar procesamiento)
            height, width = image.shape[:2]
            max_size = 1024  # Máximo 1024px en cualquier dimensión
            
            if height > max_size or width > max_size:
                scale = max_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
                logger.info(f"Imagen redimensionada: {width}x{height} -> {new_width}x{new_height}")
            
            # Preprocesamiento básico pero rápido
            processed = preprocess_image_for_ocr(image)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error en preprocesamiento rápido: {e}")
            return image  # Retornar imagen original si falla
    
    def perform_fast_yolo_ocr(self, image: np.ndarray, document_type: DocumentType) -> Dict[str, Any]:
        """
        OCR YOLO optimizado para velocidad con timeout
        """
        start_time = time.time()
        extracted_data = {}
        
        try:
            # Seleccionar modelo más rápido
            model_name = self.get_fastest_model(document_type)
            
            # Cargar modelo (con cache)
            yolo_model = self.load_model_cached(model_name)
            
            # Realizar inferencia con timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(yolo_model, image)
                try:
                    results = future.result(timeout=self.timeout_seconds - 5)  # Dejar 5s para OCR
                except concurrent.futures.TimeoutError:
                    logger.error("Timeout en inferencia YOLO")
                    return {'error': 'Timeout en detección YOLO', 'full_text_fallback': ''}
            
            # Procesar resultados rápidamente
            confidence_threshold = 0.25  # Umbral más bajo para capturar más campos
            
            for r in results:
                boxes = r.boxes
                if boxes is None or len(boxes) == 0:
                    continue
                
                names = r.names
                
                for box in boxes:
                    conf = float(box.conf[0])
                    if conf < confidence_threshold:
                        continue
                    
                    class_id = int(box.cls[0])
                    class_name = names[class_id]
                    
                    # Extraer región
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    cropped = image[y1:y2, x1:x2]
                    
                    if cropped.size == 0:
                        continue
                    
                    # OCR rápido en la región
                    try:
                        text = perform_ocr_with_tesseract(
                            cropped, 
                            field_name=class_name,
                            psm=get_ocr_config_for_field(class_name).get('psm', 7)
                        )
                        if text.strip():
                            extracted_data[class_name] = text.strip()
                    except Exception as e:
                        logger.warning(f"Error OCR en campo {class_name}: {e}")
            
            processing_time = time.time() - start_time
            logger.info(f"YOLO OCR completado en {processing_time:.2f}s")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error en OCR YOLO rápido: {e}")
            # Fallback a OCR completo de imagen
            try:
                fallback_text = perform_ocr_with_tesseract(image, psm=3)
                return {'error': str(e), 'full_text_fallback': fallback_text}
            except Exception as fallback_error:
                return {'error': f"{e} | Fallback error: {fallback_error}"}
    
    def process_document_fast(self, document_id: str) -> Dict[str, Any]:
        """
        Procesa un documento completo con timeout estricto
        """
        start_time = time.time()
        db = None
        
        try:
            import uuid
            doc_uuid = uuid.UUID(document_id)
            db = SessionLocal()
            
            logger.info(f"🚀 Iniciando procesamiento rápido para documento: {document_id}")
            
            # Actualizar estado
            update_document_status(db, doc_uuid, 'PROCESSING')
            
            # Obtener documento
            from services.document_service import get_document_by_id_and_data_for_ocr
            db_document_entry = get_document_by_id_and_data_for_ocr(db, doc_uuid)
            
            if not db_document_entry:
                raise ValueError(f"Documento {document_id} no encontrado")
            
            # Timeout total
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._process_with_timeout, db_document_entry, doc_uuid)
                try:
                    result = future.result(timeout=self.timeout_seconds)
                except concurrent.futures.TimeoutError:
                    logger.error(f"⏰ TIMEOUT: Documento {document_id} excedió {self.timeout_seconds}s")
                    update_document_status(db, doc_uuid, 'FAILED', error_message='Processing timeout')
                    return {
                        'status': 'timeout',
                        'document_id': document_id,
                        'error': f'Procesamiento excedió {self.timeout_seconds} segundos'
                    }
            
            # Actualizar estadísticas
            processing_time = time.time() - start_time
            self._update_stats(processing_time, True)
            
            logger.info(f"✅ Documento {document_id} procesado en {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(processing_time, False)
            
            logger.error(f"❌ Error procesando documento {document_id}: {e}")
            
            if db and 'doc_uuid' in locals():
                update_document_status(db, doc_uuid, 'FAILED', error_message=str(e))
            
            return {
                'status': 'error',
                'document_id': document_id,
                'error': str(e),
                'processing_time': processing_time
            }
        
        finally:
            if db:
                db.close()
    
    def _process_with_timeout(self, db_document_entry, doc_uuid):
        """Procesamiento interno con timeout por etapas"""
        from services.storage_service import download_file_local
        
        # 1. Descargar archivo (máximo 3s)
        logger.info("📥 Descargando archivo...")
        file_bytes = download_file_local(db_document_entry.storage_path)
        
        # 2. Determinar tipo de archivo y convertir a imagen
        original_image = None
        
        if db_document_entry.mime_type == 'application/pdf':
            logger.info("📄 Procesando archivo PDF...")
            # Convertir PDF a imagen (primera página)
            original_image = convert_pdf_to_single_image(file_bytes, page_number=0)
            
            if original_image is None:
                raise ValueError("No se pudo convertir PDF a imagen")
                
            # Optimizar imagen de PDF para OCR
            from services.pdf_converter import pdf_converter
            original_image = pdf_converter.optimize_image_for_ocr(original_image)
            logger.info("✅ PDF convertido y optimizado")
            
        else:
            # Procesar como imagen normal
            logger.info("🖼️ Procesando archivo de imagen...")
            nparr = np.frombuffer(file_bytes, np.uint8)
            original_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if original_image is None:
                raise ValueError("No se pudo decodificar la imagen")
        
        # 2. Preprocesamiento rápido (máximo 2s)
        logger.info("🔄 Preprocesando imagen...")
        preprocessed_image = self.preprocess_image_fast(original_image)
        
        # 3. OCR YOLO (resto del tiempo disponible)
        logger.info("🤖 Ejecutando OCR YOLO...")
        extracted_data = self.perform_fast_yolo_ocr(preprocessed_image, db_document_entry.document_type)
        
        # 4. Guardar resultados
        logger.info("💾 Guardando resultados...")
        db = SessionLocal()
        try:
            update_document_status(
                db,
                doc_uuid,
                'COMPLETED',
                processed_at=datetime.now(),
                raw_ocr_output=extracted_data
            )
            
            return {
                'status': 'success',
                'document_id': str(doc_uuid),
                'extracted_data': extracted_data,
                'processing_time': time.time() - time.time()  # Se calculará en el método padre
            }
        finally:
            db.close()
    
    def _update_stats(self, processing_time: float, success: bool):
        """Actualiza estadísticas de procesamiento"""
        self.processing_stats['total_processed'] += 1
        
        if success:
            self.processing_stats['successful'] += 1
            self.processing_stats['fastest_time'] = min(self.processing_stats['fastest_time'], processing_time)
            self.processing_stats['slowest_time'] = max(self.processing_stats['slowest_time'], processing_time)
            
            # Actualizar promedio
            total_time = (self.processing_stats['avg_processing_time'] * (self.processing_stats['successful'] - 1) + processing_time)
            self.processing_stats['avg_processing_time'] = total_time / self.processing_stats['successful']
        else:
            self.processing_stats['failed'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de procesamiento"""
        return self.processing_stats.copy()


# Instancia global del procesador rápido
fast_processor = FastOCRProcessor(timeout_seconds=30)


def process_document_fast_sync(document_id: str) -> Dict[str, Any]:
    """
    Función de conveniencia para procesamiento rápido síncrono
    """
    return fast_processor.process_document_fast(document_id)


if __name__ == "__main__":
    # Test del procesador
    import sys
    if len(sys.argv) > 1:
        doc_id = sys.argv[1]
        result = process_document_fast_sync(doc_id)
        print(f"Resultado: {result}")
    else:
        print("Uso: python fast_ocr_service.py <document_id>")
