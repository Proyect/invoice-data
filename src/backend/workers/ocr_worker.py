# ... (imports) ...
from services.preprocessing_service import preprocess_image_for_ocr
from services.ocr_service import perform_yolo_ocr 
from services.document_service import update_document_status, get_document_by_id_and_data_for_ocr # Ajustar esta función
from services.storage.local_storage import download_file # O S3
from database import SessionLocal
# ...

def process_document_for_ocr(document_id: str):
    db = None
    try:
        db = SessionLocal()
        logging.info(f"Iniciando procesamiento OCR (Yolo) para el documento: {document_id}")
        update_document_status(db, document_id, 'PROCESSING')

        # Obtener la entrada del documento desde la DB
        db_document_entry = get_document_by_id_and_data_for_ocr(db, document_id)
        if not db_document_entry:
            raise ValueError(f"Documento {document_id} no encontrado en la DB.")

        # 1. Descargar la imagen
        image_bytes = download_file(db_document_entry.storage_path) # Asumiendo un servicio de descarga
        nparr = np.frombuffer(image_bytes, np.uint8)
        original_image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 2. Preprocesar la imagen
        preprocessed_image = preprocess_image_for_ocr(original_image_cv)

        # 3. Realizar YOLO + Tesseract OCR
        extracted_data = perform_yolo_ocr(preprocessed_image, db_document_entry.document_type)
        
        # 4. Guardar resultados y actualizar estado
        # Esto es una simplificación; la lógica para guardar en `extracted_dni_data`
        # o `extracted_invoice_data` debe ir aquí, extrayendo los campos del diccionario `extracted_data`.
        # Por ahora, puedes guardar el `extracted_data` JSONB en el campo `raw_ocr_output` del documento.
        update_document_status(
            db,
            document_id,
            'COMPLETED',
            raw_ocr_output=extracted_data # Guarda el diccionario como JSONB
            # Aquí llamarías a una función como save_dni_data(db, document_id, extracted_data)
            # o save_invoice_data(db, document_id, extracted_data)
        )
        logging.info(f"Documento {document_id} procesado con éxito.")

    except Exception as e:
        logging.error(f"Error procesando documento {document_id}: {e}", exc_info=True)
        if db:
            update_document_status(db, document_id, 'FAILED', error_message=str(e))
    finally:
        if db:
            db.close()