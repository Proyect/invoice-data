# backend/ocr_worker/celery_app.py
import os
from celery import Celery

# Configuración de Redis como broker
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
print(f"Celery worker conectándose a Redis en: {REDIS_URL}")

celery_app = Celery(
    'ocr_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL, # Para almacenar resultados de tareas
    include=['ocr_worker.worker'] # Importa el módulo donde están tus tareas
)

# Configuración adicional de Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    result_expires=3600,  # 1 hora
    timezone='America/Argentina/Buenos_Aires',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # Configuración simplificada para evitar errores de backend
    result_backend_transport_options={
        'visibility_timeout': 3600,
    },
)

