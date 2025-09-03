from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    filename: str
    status: str
    message: str

class DocumentStatusResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    status: str
    document_type: str
    uploaded_at: datetime
    processed_at: Optional[datetime]
    processing_error: Optional[str]

class DocumentType(str, Enum): # Usaremos Enum para tipos de documento para validar
    DNI_FRONT = "DNI_FRONT"
    DNI_BACK = "DNI_BACK"
    INVOICE_A = "INVOICE_A"
    INVOICE_B = "INVOICE_B"
    INVOICE_C = "INVOICE_C"
    