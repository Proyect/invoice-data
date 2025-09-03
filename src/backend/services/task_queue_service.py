# ocr_api/services/task_queue_service.py

import redis
from rq import Queue
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

# Configurar conexión a Redis
redis_conn = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

# Crear cola de tareas
ocr_queue = Queue('ocr_tasks', connection=redis_conn)

async def add_ocr_task(document_id: str):
    """
    Añade una tarea de procesamiento OCR a la cola.
    
    Args:
        document_id: ID del documento a procesar
        
    Returns:
        Job ID de la tarea encolada
    """
    try:
        # Importar aquí para evitar dependencias circulares
        from workers.ocr_worker import process_document_for_ocr
        
        # Encolar la tarea
        job = ocr_queue.enqueue(
            process_document_for_ocr,
            args=[document_id],
            job_timeout='10m',  # Timeout de 10 minutos
            result_ttl=3600,    # Mantener resultado por 1 hora
            failure_ttl=3600    # Mantener fallos por 1 hora
        )
        
        print(f"Tarea OCR encolada para documento {document_id} con Job ID: {job.id}")
        return job.id
        
    except Exception as e:
        print(f"Error al encolar tarea OCR para documento {document_id}: {e}")
        raise

def get_job_status(job_id: str):
    """
    Obtiene el estado de una tarea en la cola.
    
    Args:
        job_id: ID de la tarea
        
    Returns:
        Estado de la tarea (queued, started, finished, failed)
    """
    try:
        job = ocr_queue.fetch_job(job_id)
        if job is None:
            return "not_found"
        return job.get_status()
    except Exception as e:
        print(f"Error al obtener estado de tarea {job_id}: {e}")
        return "error"

def get_queue_info():
    """
    Obtiene información sobre la cola de tareas.
    
    Returns:
        Diccionario con información de la cola
    """
    try:
        return {
            "queue_name": ocr_queue.name,
            "jobs_in_queue": len(ocr_queue),
            "failed_jobs": len(ocr_queue.failed_job_registry),
            "started_jobs": len(ocr_queue.started_job_registry),
            "deferred_jobs": len(ocr_queue.deferred_job_registry)
        }
    except Exception as e:
        print(f"Error al obtener información de la cola: {e}")
        return {"error": str(e)}
