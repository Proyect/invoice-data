# ocr_api/api/v1/documents.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from fastapi.responses import FileResponse
from typing import Annotated
import uuid
import logging
import os
import httpx
from sqlalchemy.orm import Session

from models.documents import DocumentUploadResponse, DocumentStatusResponse, DocumentType
from models.auth import User as UserModel
from services.auth_service import get_current_active_user
from services.document_service import create_document_entry, get_document_by_id, delete_document, get_documents_by_user
from services.storage.local_storage import upload_file_local, download_file_local, LOCAL_STORAGE_PATH
from services.task_queue_service import add_ocr_task
from services.sync_ocr_service import process_document_sync, is_redis_available
from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/infer", summary="Proxy de inferencia RT-DETR")
async def infer_document(
    file: Annotated[UploadFile, File(description="Imagen o PDF")],
    document_type: Annotated[str, Query(description="Tipo de documento", regex="^(invoice|dni_front|dni_back)$")] = "invoice",
):
    """
    Reenvía el archivo al servicio RT-DETR para detección de campos.
    Devuelve detecciones y campos extraídos (mock o reales).
    """
    base_url = os.getenv("RTDETR_API_URL", "http://localhost:8010")
    infer_url = f"{base_url}/infer"

    try:
        file_bytes = await file.read()
        async with httpx.AsyncClient(timeout=60) as client:
            files = {"file": (file.filename or "upload.bin", file_bytes, file.content_type or "application/octet-stream")}
            params = {"document_type": document_type}
            resp = await client.post(infer_url, params=params, files=files)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"RT-DETR error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al invocar RT-DETR: {str(e)}")

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

        # 3. Procesar documento - usar Redis si está disponible, sino procesamiento síncrono
        if is_redis_available():
            # Usar cola de tareas con Redis
            await add_ocr_task(str(document_id))
            return DocumentUploadResponse(
                document_id=document_id,
                filename=file.filename,
                status="PENDING",
                message="Document uploaded and queued for processing."
            )
        else:
            # Procesamiento síncrono para desarrollo local
            logger.info(f"Redis no disponible, procesando documento {document_id} de forma síncrona")
            result = process_document_sync(document_id)
            
            if result["status"] == "success":
                return DocumentUploadResponse(
                    document_id=document_id,
                    filename=file.filename,
                    status="COMPLETED",
                    message="Document uploaded and processed successfully."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing document: {result.get('error', 'Unknown error')}"
                )
    
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un documento")
async def delete_document_endpoint(
    document_id: str,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Elimina un documento específico del usuario autenticado.
    
    - **document_id**: ID único del documento a eliminar
    
    Retorna 204 No Content si se eliminó exitosamente.
    Retorna 404 si el documento no existe o no pertenece al usuario.
    """
    try:
        # Convertir string a UUID
        doc_uuid = uuid.UUID(document_id)
        
        # Verificar que el documento existe y pertenece al usuario
        db_document = get_document_by_id(db, doc_uuid)
        if not db_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Verificar que el documento pertenece al usuario actual
        if db_document.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar este documento"
            )
        
        # Eliminar el documento
        success = delete_document(db, doc_uuid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        logger.info(f"Document {document_id} deleted successfully by user {current_user.id}")
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de documento inválido"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", summary="Listar documentos del usuario")
async def list_user_documents(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de documentos a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de documentos a retornar")
):
    """
    Lista todos los documentos del usuario autenticado con paginación.
    
    - **skip**: Número de documentos a omitir (para paginación)
    - **limit**: Número máximo de documentos a retornar (máximo 1000)
    
    Retorna una lista de documentos con sus metadatos.
    """
    try:
        documents = get_documents_by_user(db, current_user.id, skip=skip, limit=limit)
        
        # Convertir a formato de respuesta
        documents_response = []
        for doc in documents:
            documents_response.append({
                "id": str(doc.id),
                "original_filename": doc.original_filename,
                "document_type": doc.document_type,
                "status": doc.status,
                "uploaded_at": doc.uploaded_at.isoformat(),
                "processed_at": doc.processed_at.isoformat() if doc.processed_at else None,
                "processing_error": doc.processing_error
            })
        
        return {
            "documents": documents_response,
            "total": len(documents_response),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error listing documents for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
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

@router.get("/{document_id}/download", summary="Descargar un documento")
async def download_document(
    document_id: uuid.UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Descarga el archivo original de un documento.
    """
    db_document = get_document_by_id(db, document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    
    # Verificar que el documento pertenece al usuario actual
    if db_document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document.")
    
    try:
        # Construir la ruta completa del archivo
        file_path = os.path.join(LOCAL_STORAGE_PATH, db_document.storage_path)
        
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on server.")
        
        # Retornar el archivo como respuesta
        return FileResponse(
            path=file_path,
            filename=db_document.original_filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error downloading document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error downloading file"
        )