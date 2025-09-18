# services/sync_ocr_service.py

import logging
import uuid
import numpy as np
import cv2
from datetime import datetime

from services.preprocessing_service import preprocess_image_for_ocr
from services.ocr_service import perform_yolo_ocr
from services.document_service import update_document_status, get_document_by_id_and_data_for_ocr
from services.storage.local_storage import download_file_local
from database import SessionLocal

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_document_sync(document_id: uuid.UUID) -> dict:
    """
    Procesa un documento de forma síncrona para desarrollo local.
    
    Args:
        document_id: UUID del documento a procesar
        
    Returns:
        Dict con el resultado del procesamiento
    """
    db = None
    try:
        db = SessionLocal()
        logger.info(f"Iniciando procesamiento OCR síncrono para documento: {document_id}")
        
        # Actualizar estado a PROCESSING
        update_document_status(db, document_id, 'PROCESSING')

        # Obtener la entrada del documento desde la DB
        db_document_entry = get_document_by_id_and_data_for_ocr(db, document_id)
        if not db_document_entry:
            raise ValueError(f"Documento {document_id} no encontrado en la DB.")

        # 1. Descargar la imagen
        logger.info(f"Descargando archivo: {db_document_entry.storage_path}")
        image_bytes = download_file_local(db_document_entry.storage_path)
        nparr = np.frombuffer(image_bytes, np.uint8)
        original_image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if original_image_cv is None:
            raise ValueError("No se pudo decodificar la imagen")

        # 2. Preprocesar la imagen
        logger.info("Preprocesando imagen para OCR")
        preprocessed_image = preprocess_image_for_ocr(original_image_cv)

        # 3. Realizar YOLO + Tesseract OCR
        logger.info(f"Ejecutando YOLO + OCR para tipo: {db_document_entry.document_type}")
        extracted_data = perform_yolo_ocr(preprocessed_image, db_document_entry.document_type)
        
        # 4. Guardar resultados y actualizar estado
        logger.info("Guardando resultados del OCR")
        update_document_status(
            db,
            document_id,
            'COMPLETED',
            processed_at=datetime.now(),
            raw_ocr_output=extracted_data
        )
        
        logger.info(f"Documento {document_id} procesado con éxito (modo síncrono).")
        return {
            "status": "success",
            "document_id": str(document_id),
            "extracted_data": extracted_data
        }

    except Exception as e:
        logger.error(f"Error procesando documento {document_id}: {e}", exc_info=True)
        if db:
            update_document_status(
                db, 
                document_id, 
                'FAILED', 
                error_message=str(e)
            )
        return {
            "status": "error",
            "document_id": str(document_id),
            "error": str(e)
        }
    finally:
        if db:
            db.close()

def is_redis_available() -> bool:
    """
    Verifica si Redis está disponible para usar RQ.
    
    Returns:
        True si Redis está disponible, False en caso contrario
    """
    try:
        import redis
        from config import REDIS_HOST, REDIS_PORT, REDIS_DB
        
        redis_conn = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        redis_conn.ping()
        return True
    except Exception as e:
        logger.warning(f"Redis no disponible: {e}")
        return False
