# ocr_api/services/task_queue_service.py

import logging

logger = logging.getLogger(__name__)

async def add_ocr_task(document_id: str):
    """
    Encola una tarea OCR para procesamiento asíncrono usando Celery.
    
    Args:
        document_id: ID del documento a procesar
        
    Returns:
        Task ID de Celery
    """
    try:
        from ocr_worker.celery_app import celery_app
        
        logger.info(f"Encolando tarea OCR para documento: {document_id}")
        
        # Encolar la tarea usando send_task (por nombre)
        task = celery_app.send_task('ocr_tasks.process_document_task', args=[document_id])
        
        logger.info(f"Tarea OCR encolada para documento {document_id} con Task ID: {task.id}")
        return task.id
        
    except Exception as e:
        logger.error(f"Error al encolar tarea OCR para documento {document_id}: {e}")
        raise

def get_task_status(task_id: str):
    """
    Obtiene el estado de una tarea de Celery.
    
    Args:
        task_id: ID de la tarea
        
    Returns:
        Estado de la tarea (PENDING, STARTED, SUCCESS, FAILURE, etc.)
    """
    try:
        from ocr_worker.celery_app import celery_app
        result = celery_app.AsyncResult(task_id)
        return result.status
    except Exception as e:
        logger.error(f"Error al obtener estado de tarea {task_id}: {e}")
        return "ERROR"

def get_queue_info():
    """
    Obtiene información sobre las colas de Celery.
    
    Returns:
        Diccionario con información de las colas
    """
    try:
        from ocr_worker.celery_app import celery_app
        inspect = celery_app.control.inspect()
        active = inspect.active()
        scheduled = inspect.scheduled()
        reserved = inspect.reserved()
        
        return {
            "active_tasks": active,
            "scheduled_tasks": scheduled,
            "reserved_tasks": reserved
        }
    except Exception as e:
        logger.error(f"Error al obtener información de la cola: {e}")
        return {"error": str(e)}
