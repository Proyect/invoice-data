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

