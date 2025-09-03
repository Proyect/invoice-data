# ocr_api/api/v1/documents.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import Annotated
import uuid

# Importa los nuevos servicios
from models.documents import DocumentUploadResponse, DocumentStatusResponse, DocumentType
from models.auth import User # Asegúrate de importar User para current_user
from services.auth_service import get_current_active_user
from services.document_service import create_document_entry, get_document_by_id
from services.storage.local_storage import upload_file_local # Importa tu servicio de almacenamiento
from services.task_queue_service import add_ocr_task
from database import get_db 
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED, summary="Subir un documento para OCR")
async def upload_document(
    file: Annotated[UploadFile, File(description="Archivo de imagen o PDF a procesar.")],
    document_type: DocumentType, # Hacemos que sea requerido para saber qué modelo YOLO usar
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Sube un documento (imagen o PDF) para ser procesado por OCR.
    El procesamiento se realiza de forma asíncrona.
    """
    document_id = uuid.uuid4()
    
    # 1. Almacenar el archivo original en el sistema de almacenamiento local
    # upload_file_local ahora espera el objeto UploadFile completo
    storage_path = await upload_file_local(file) # Esta es la ruta relativa (ej. "abc-123.jpg")

    # 2. Crear una entrada en la base de datos
    db_document = create_document_entry(
        db,
        document_id=document_id,
        original_filename=file.filename,
        storage_path=storage_path, # Guarda la ruta relativa
        mime_type=file.content_type,
        document_type=document_type,
        user_id=current_user.id # Asumiendo que User tiene un campo ID
    )

    # 3. Añadir una tarea a la cola
    await add_ocr_task(str(document_id)) # RQ prefiere strings para IDs de tareas

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        status="PENDING",
        message="Document uploaded and queued for processing."
    )

# ... (otros endpoints get_document_status, get_extracted_data) ...

# Para get_extracted_data, el retorno será el JSONB que guardamos
@router.get("/{document_id}/extracted_data", summary="Obtener datos extraídos de un documento")
async def get_extracted_data(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    db_document = get_document_by_id(db, document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    
    if db_document.status != 'COMPLETED':
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document not yet processed or failed.")

    return db_document.raw_ocr_output # Retorna el JSONB directamente por ahora