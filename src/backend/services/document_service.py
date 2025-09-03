# ocr_api/services/document_service.py

import uuid
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

# Importa tu modelo de base de datos (SQLAlchemy)
from database import Document # Solo Document por ahora
from models.documents import DocumentType # Para el enum

def create_document_entry(
    db: Session,
    document_id: uuid.UUID,
    original_filename: str,
    storage_path: str, # Esta es la ruta relativa devuelta por local_storage
    mime_type: str,
    document_type: DocumentType, # verificar tipo de datos
    user_id: Optional[uuid.UUID] = None # Asumiendo que el User tiene un ID
) -> Document:
    """Crea una nueva entrada de documento en la base de datos."""
    db_document = Document(
        id=document_id,
        original_filename=original_filename,
        storage_path=storage_path,
        mime_type=mime_type,
        uploaded_at=datetime.now(datetime.timezone.utc),
        status="PENDING",
        document_type=document_type, # Guardar el enum directamente, no .value
        user_id=user_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document_by_id(db: Session, document_id: uuid.UUID) -> Optional[Document]:
    """Obtiene un documento por su ID."""
    return db.query(Document).filter(Document.id == document_id).first()

def get_document_by_id_and_data_for_ocr(db: Session, document_id: uuid.UUID):
    """
    Obtiene un documento por su ID, con los campos necesarios para el worker OCR.
    Retorna un objeto con `storage_path`, `document_type`.
    """
    # Puedes crear una clase o un Pydantic model más específico para esto
    doc_entry = db.query(Document.storage_path, Document.document_type).filter(Document.id == document_id).first()
    return doc_entry

def update_document_status(
    db: Session,
    document_id: uuid.UUID,
    status: str,
    processed_at: Optional[datetime] = None,
    error_message: Optional[str] = None,
    raw_ocr_output: Optional[dict] = None # Para guardar el diccionario de resultados de YOLO como JSONB
):
    """Actualiza el estado de procesamiento de un documento y sus metadatos."""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document:
        db_document.status = status
        db_document.processed_at = processed_at if processed_at else datetime.now(datetime.timezone.utc)
        db_document.processing_error = error_message
        if raw_ocr_output is not None:
            db_document.raw_ocr_output = raw_ocr_output # Asumiendo que tu modelo SQLAlchemy Document tiene un campo JSONB `raw_ocr_output`
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
    return db_document

# Aquí irán las funciones para guardar datos específicos de DNI o facturas
# def save_extracted_dni_data(db: Session, document_id: uuid.UUID, extracted_data: dict):
#     # Implementar la lógica para guardar en ExtractedDniData
#     pass

# def save_extracted_invoice_data(db: Session, document_id: uuid.UUID, extracted_data: dict):
#     # Implementar la lógica para guardar en ExtractedInvoiceData
#     pass