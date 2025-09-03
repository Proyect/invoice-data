# ocr_api/workers/ocr_worker.py

import logging
import uuid
import numpy as np
import cv2
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from services.preprocessing_service import preprocess_image_for_ocr
from services.ocr_service import perform_yolo_ocr
from services.document_service import update_document_status, get_document_by_id_and_data_for_ocr
from services.storage.local_storage import download_file_local
from database import SessionLocal

def process_document_for_ocr(document_id: str):
    """
    Procesa un documento para extraer texto usando YOLO + OCR.
    
    Args:
        document_id: ID del documento a procesar (como string)
    """
    db = None
    try:
        # Convertir string a UUID
        doc_uuid = uuid.UUID(document_id)
        
        db = SessionLocal()
        logger.info(f"Iniciando procesamiento OCR (YOLO) para el documento: {document_id}")
        
        # Actualizar estado a PROCESSING
        update_document_status(db, doc_uuid, 'PROCESSING')

        # Obtener la entrada del documento desde la DB
        db_document_entry = get_document_by_id_and_data_for_ocr(db, doc_uuid)
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
            doc_uuid,
            'COMPLETED',
            processed_at=datetime.now(),
            raw_ocr_output=extracted_data
        )
        
        logger.info(f"Documento {document_id} procesado con éxito.")
        return {
            "status": "success",
            "document_id": document_id,
            "extracted_data": extracted_data
        }

    except Exception as e:
        logger.error(f"Error procesando documento {document_id}: {e}", exc_info=True)
        if db:
            update_document_status(
                db, 
                doc_uuid if 'doc_uuid' in locals() else uuid.UUID(document_id), 
                'FAILED', 
                error_message=str(e)
            )
        return {
            "status": "error",
            "document_id": document_id,
            "error": str(e)
        }
    finally:
        if db:
            db.close()

# Función para ejecutar el worker como script independiente
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python -m workers.ocr_worker <document_id>")
        sys.exit(1)
    
    document_id = sys.argv[1]
    result = process_document_for_ocr(document_id)
    print(f"Resultado: {result}")