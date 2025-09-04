# test_document_service.py
import sys
sys.path.append(r'c:\Users\amdiaz\Desktop\code\Python\v.13.13\invoice-data')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from src.backend.database import create_db_and_tables
from src.backend.services.document_service import *
from src.backend.models.documents import DocumentType

# Crear las tablas si no existen
create_db_and_tables()

# Configura la conexión (ajusta según tu DB)
engine = create_engine("sqlite:///test.db")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

doc_id = uuid.uuid4()

# Crea un documento de prueba
doc = create_document_entry(
    db=db,
    document_id=doc_id,
    original_filename="test_invoice.jpg",
    storage_path="uploads/test_invoice.jpg",
    mime_type="application/jpg",
    document_type=DocumentType.INVOICE_A,
    user_id=None
)
print("Documento creado: ",doc)

# Probar get_document_by_id
doc_fetched = get_document_by_id(db, doc_id)
print("Documento obtenido por ID:", doc_fetched)

# Probar get_document_by_id_and_data_for_ocr
ocr_data = get_document_by_id_and_data_for_ocr(db, doc_id)
print("Datos para OCR:", ocr_data)

# Probar update_document_status
updated_doc = update_document_status(
    db=db,
    document_id=doc_id,
    status="PROCESSED",
    error_message=None,
    raw_ocr_output={"result": "ok"}
)
print("Documento actualizado:", updated_doc)