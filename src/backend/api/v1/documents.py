from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import Annotated
import uuid

from models.documents import DocumentUploadResponse, DocumentStatusResponse, DocumentType
from services.auth_service import get_current_active_user # Para proteger rutas
from services.document_service import upload_document_to_storage, create_document_entry, get_document_by_id
from services.task_queue_service import add_ocr_task # Servicio para añadir a la cola
from database import get_db # Para obtener la sesión de DB

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED, summary="Subir un documento para OCR")
async def upload_document(
    file: Annotated[UploadFile, File(description="Archivo de imagen o PDF a procesar.")],
    document_type: DocumentType = DocumentType.DNI_FRONT, # Tipo de documento, se puede inferir más tarde
    current_user: Annotated[User, Depends(get_current_active_user)], # Proteger el endpoint
    db: Annotated[Session, Depends(get_db)] # Inyección de dependencia de la DB
):
    """
    Sube un documento (imagen o PDF) para ser procesado por OCR.
    El procesamiento se realiza de forma asíncrona.
    """
    document_id = uuid.uuid4()
    file_bytes = await file.read() # Leer el contenido del archivo

    # 1. Almacenar el archivo original en el sistema de almacenamiento (S3/MinIO)
    storage_path = await upload_document_to_storage(document_id, file.filename, file_bytes, file.content_type)

    # 2. Crear una entrada en la base de datos con estado PENDING
    db_document = create_document_entry(
        db,
        document_id=document_id,
        original_filename=file.filename,
        storage_path=storage_path,
        mime_type=file.content_type,
        document_type=document_type,
        user_id=current_user.id # Asumiendo que el User tiene un ID
    )

    # 3. Añadir una tarea a la cola para el procesamiento OCR asíncrono
    await add_ocr_task(document_id)

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        status="PENDING",
        message="Document uploaded and queued for processing."
    )

@router.get("/{document_id}/status", response_model=DocumentStatusResponse, summary="Obtener el estado de procesamiento de un documento")
async def get_document_status(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Recupera el estado actual de procesamiento de un documento por su ID.
    """
    db_document = get_document_by_id(db, document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # Puedes agregar lógica para verificar si el usuario tiene permiso para ver este documento
    # if db_document.user_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this document.")

    return DocumentStatusResponse(
        id=db_document.id,
        original_filename=db_document.original_filename,
        status=db_document.status,
        document_type=db_document.document_type,
        uploaded_at=db_document.uploaded_at,
        processed_at=db_document.processed_at,
        processing_error=db_document.processing_error
    )

@router.get("/{document_id}/extracted_data", summary="Obtener datos extraídos de un documento")
async def get_extracted_data(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Recupera los datos extraídos de OCR para un documento específico.
    El formato de la respuesta dependerá del tipo de documento.
    """
    db_document = get_document_by_id(db, document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    
    if db_document.status != 'COMPLETED':
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document not yet processed or failed.")

    # Lógica para obtener los datos específicos según el document_type
    # Ej: if db_document.document_type in ['DNI_FRONT', 'DNI_BACK']:
    #        return get_extracted_dni_data(db, document_id)
    #    elif db_document.document_type in ['INVOICE_A', 'INVOICE_B']:
    #        return get_extracted_invoice_data(db, document_id)
    # Esto devolvería los modelos Pydantic correspondientes a cada tipo de dato.
    return {"message": "Implementación pendiente para tipo de documento específico."}