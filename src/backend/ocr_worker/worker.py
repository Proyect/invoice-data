# backend/ocr_worker/worker.py
import os
import sys
import logging
import uuid
import numpy as np
import cv2
from datetime import datetime
from typing import Dict, Any

# Agregar el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar Celery app
from .celery_app import celery_app

# Importar servicios del backend
from services.preprocessing_service import preprocess_image_for_ocr
from services.ocr_service import perform_yolo_ocr
from services.document_service import update_document_status, get_document_by_id_and_data_for_ocr
from services.storage.local_storage import download_file_local
from database import SessionLocal
from models.extracted_data import raw_ocr_to_dni_data, raw_ocr_to_invoice_data
from models.enums import DocumentType

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='ocr_tasks.process_document')
def process_document_celery(self, document_id: str) -> Dict[str, Any]:
    """
    Tarea Celery para procesar un documento con OCR.
    
    Args:
        document_id: ID del documento a procesar (como string)
        
    Returns:
        Dict con el resultado del procesamiento
    """
    db = None
    doc_uuid = None
    
    try:
        # Convertir string a UUID
        doc_uuid = uuid.UUID(document_id)
        
        # Actualizar estado de la tarea
        self.update_state(
            state='PROCESSING',
            meta={'document_id': document_id, 'stage': 'initializing'}
        )
        
        db = SessionLocal()
        logger.info(f"[Celery] Iniciando procesamiento OCR para documento: {document_id}")
        
        # Actualizar estado en DB
        update_document_status(db, doc_uuid, 'PROCESSING')
        
        # Obtener datos del documento
        db_document_entry = get_document_by_id_and_data_for_ocr(db, doc_uuid)
        if not db_document_entry:
            raise ValueError(f"Documento {document_id} no encontrado en la DB.")
        
        # Actualizar progreso
        self.update_state(
            state='PROCESSING',
            meta={'document_id': document_id, 'stage': 'downloading_file'}
        )
        
        # 1. Descargar la imagen
        logger.info(f"[Celery] Descargando archivo: {db_document_entry.storage_path}")
        image_bytes = download_file_local(db_document_entry.storage_path)
        nparr = np.frombuffer(image_bytes, np.uint8)
        original_image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if original_image_cv is None:
            raise ValueError("No se pudo decodificar la imagen")
        
        # Actualizar progreso
        self.update_state(
            state='PROCESSING',
            meta={'document_id': document_id, 'stage': 'preprocessing'}
        )
        
        # 2. Preprocesar la imagen
        logger.info("[Celery] Preprocesando imagen para OCR")
        preprocessed_image = preprocess_image_for_ocr(original_image_cv)
        
        # Actualizar progreso
        self.update_state(
            state='PROCESSING',
            meta={'document_id': document_id, 'stage': 'ocr_processing'}
        )
        
        # 3. Realizar YOLO + Tesseract OCR
        logger.info(f"[Celery] Ejecutando YOLO + OCR para tipo: {db_document_entry.document_type}")
        raw_extracted_data = perform_yolo_ocr(preprocessed_image, db_document_entry.document_type)
        
        # Actualizar progreso
        self.update_state(
            state='PROCESSING',
            meta={'document_id': document_id, 'stage': 'data_structuring'}
        )
        
        # 4. Estructurar datos según el tipo de documento
        structured_data = None
        processing_quality = determine_processing_quality(raw_extracted_data)
        
        if db_document_entry.document_type in [DocumentType.DNI_FRONT, DocumentType.DNI_BACK]:
            structured_data = raw_ocr_to_dni_data(doc_uuid, raw_extracted_data)
            structured_data.processing_quality = processing_quality
        elif db_document_entry.document_type in [DocumentType.INVOICE_A, DocumentType.INVOICE_B, DocumentType.INVOICE_C]:
            structured_data = raw_ocr_to_invoice_data(doc_uuid, raw_extracted_data)
            structured_data.processing_quality = processing_quality
        
        # Actualizar progreso
        self.update_state(
            state='PROCESSING',
            meta={'document_id': document_id, 'stage': 'saving_results'}
        )
        
        # 5. Guardar resultados
        logger.info("[Celery] Guardando resultados del OCR")
        
        # Preparar datos para guardar
        save_data = {
            'raw_ocr_output': raw_extracted_data,
            'structured_data': structured_data.dict() if structured_data else None,
            'processing_quality': processing_quality,
            'processing_metadata': {
                'celery_task_id': self.request.id,
                'processing_time': datetime.now().isoformat(),
                'image_dimensions': original_image_cv.shape[:2] if original_image_cv is not None else None
            }
        }
        
        update_document_status(
            db,
            doc_uuid,
            'COMPLETED',
            processed_at=datetime.now(),
            raw_ocr_output=save_data
        )
        
        logger.info(f"[Celery] Documento {document_id} procesado con éxito.")
        
        return {
            "status": "success",
            "document_id": document_id,
            "extracted_data": raw_extracted_data,
            "structured_data": structured_data.dict() if structured_data else None,
            "processing_quality": processing_quality,
            "celery_task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"[Celery] Error procesando documento {document_id}: {e}", exc_info=True)
        
        # Actualizar estado de error
        self.update_state(
            state='FAILURE',
            meta={
                'document_id': document_id,
                'error': str(e),
                'celery_task_id': self.request.id
            }
        )
        
        if db and doc_uuid:
            update_document_status(
                db, 
                doc_uuid, 
                'FAILED', 
                error_message=str(e)
            )
        
        # Re-lanzar la excepción para que Celery la maneje
        raise
        
    finally:
        if db:
            db.close()

def determine_processing_quality(raw_data: Dict[str, Any]) -> str:
    """
    Determina la calidad del procesamiento basado en los datos extraídos.
    
    Args:
        raw_data: Datos raw del OCR
        
    Returns:
        'high', 'medium', o 'low'
    """
    if not raw_data:
        return 'low'
    
    # Contar campos detectados y sus confianzas
    total_fields = len(raw_data)
    high_confidence_fields = 0
    medium_confidence_fields = 0
    
    for field_name, field_data in raw_data.items():
        if isinstance(field_data, dict) and 'confidence' in field_data:
            confidence = field_data['confidence']
            if confidence >= 0.8:
                high_confidence_fields += 1
            elif confidence >= 0.5:
                medium_confidence_fields += 1
    
    # Determinar calidad
    if total_fields == 0:
        return 'low'
    
    high_confidence_ratio = high_confidence_fields / total_fields
    medium_confidence_ratio = (high_confidence_fields + medium_confidence_fields) / total_fields
    
    if high_confidence_ratio >= 0.7:
        return 'high'
    elif medium_confidence_ratio >= 0.5:
        return 'medium'
    else:
        return 'low'

@celery_app.task(name='ocr_tasks.health_check')
def health_check() -> Dict[str, Any]:
    """Tarea de verificación de salud del worker"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "worker_info": {
            "celery_version": celery_app.version,
            "python_version": sys.version
        }
    }

# Configuración adicional de Celery
@celery_app.task(bind=True)
def debug_task(self):
    """Tarea de debug para verificar configuración"""
    print(f'Request: {self.request!r}')
    return {'task_id': self.request.id, 'status': 'debug_ok'}