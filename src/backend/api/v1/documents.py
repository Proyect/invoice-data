# ocr_api/api/v1/documents.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from typing import Annotated
import uuid

# Importa los nuevos servicios
from models.documents import DocumentUploadResponse, DocumentStatusResponse, DocumentType
from models.auth import User as UserModel # Usar modelo Pydantic
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
    document_type: Annotated[DocumentType, Query(description="Tipo de documento a procesar")],
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Sube un documento (imagen o PDF) para ser procesado por OCR.
    El procesamiento se realiza de forma asíncrona.
    """
    # Validaciones de seguridad
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required.")
    
    # Validar tipo de archivo
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.tiff', '.bmp'}
    file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    if f'.{file_extension}' not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"File type not allowed. Supported: {', '.join(allowed_extensions)}"
        )
    
    # Validar MIME type
    allowed_mime_types = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'image/bmp',
        'application/pdf'
    }
    if file.content_type not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MIME type not allowed: {file.content_type}"
        )
    
    # Validar tamaño del archivo (máximo 10MB)
    max_file_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size: 10MB"
        )
    
    # Resetear el puntero del archivo
    await file.seek(0)
    
    document_id = uuid.uuid4()
    
    try:
        # 1. Almacenar el archivo original en el sistema de almacenamiento local
        storage_path = await upload_file_local(file)
        
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
    
    except Exception as e:
        # En caso de error, limpiar recursos si es necesario
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file upload: {str(e)}"
        )

@router.get("/{document_id}/extracted_data", summary="Obtener datos extraídos de un documento")
async def get_extracted_data(
    document_id: uuid.UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    db_document = get_document_by_id(db, document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    
    # Verificar que el documento pertenece al usuario actual
    if db_document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document.")
    
    if db_document.status != 'COMPLETED':
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document not yet processed or failed.")

    return db_document.raw_ocr_output # Retorna el JSONB directamente por ahora

@router.get("/{document_id}/status", response_model=DocumentStatusResponse, summary="Obtener estado de un documento")
async def get_document_status(
    document_id: uuid.UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Obtiene el estado actual de procesamiento de un documento.
    """
    db_document = get_document_by_id(db, document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    
    # Verificar que el documento pertenece al usuario actual
    if db_document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document.")
    
    return DocumentStatusResponse(
        id=db_document.id,
        original_filename=db_document.original_filename,
        status=db_document.status,
        document_type=db_document.document_type.value,
        uploaded_at=db_document.uploaded_at,
        processed_at=db_document.processed_at,
        processing_error=db_document.processing_error
    )

@router.get("/{document_id}/structured_data", summary="Obtener datos estructurados de un documento")
async def get_structured_data(
    document_id: uuid.UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Obtiene los datos extraídos en formato estructurado según el tipo de documento.
    """
    db_document = get_document_by_id(db, document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    
    # Verificar que el documento pertenece al usuario actual
    if db_document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document.")
    
    if db_document.status != 'COMPLETED':
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document not yet processed or failed.")

    # Obtener datos estructurados si existen
    raw_data = db_document.raw_ocr_output
    if not raw_data or 'structured_data' not in raw_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No structured data available.")
    
    return raw_data['structured_data']