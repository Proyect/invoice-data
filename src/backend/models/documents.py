from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

# Re-export DocumentType for backward compatibility
from models.enums import DocumentType

__all__ = ['DocumentUploadResponse', 'DocumentStatusResponse', 'DocumentType']

class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    filename: str
    status: str
    message: str
    
    model_config = {"from_attributes": True}

class DocumentStatusResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    status: str
    document_type: str
    uploaded_at: datetime
    processed_at: Optional[datetime]
    processing_error: Optional[str]
    
    model_config = {"from_attributes": True}