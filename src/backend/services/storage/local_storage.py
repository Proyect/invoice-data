# ocr_api/services/storage/local_storage.py

import os
import uuid
from typing import BinaryIO
from fastapi import UploadFile

from config import LOCAL_STORAGE_PATH

# Asegurarse de que el directorio de almacenamiento exista
os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)

async def upload_file_local(file: UploadFile) -> str:
    """
    Guarda un archivo subido en el almacenamiento local.
    Retorna la ruta relativa del archivo guardado.
    """
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(LOCAL_STORAGE_PATH, unique_filename)

    with open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024) # Leer en chunks de 1MB
            if not chunk:
                break
            buffer.write(chunk)
    
    return os.path.relpath(file_path, LOCAL_STORAGE_PATH) # Retorna solo el nombre_unico.ext

def download_file_local(relative_file_path: str) -> bytes:
    """
    Descarga un archivo del almacenamiento local y retorna sus bytes.
    `relative_file_path` es la ruta retornada por `upload_file_local`.
    """
    file_path = os.path.join(LOCAL_STORAGE_PATH, relative_file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Archivo no encontrado en la ruta: {file_path}")

    with open(file_path, "rb") as f:
        return f.read()

# También puedes añadir un wrapper para compatibilidad si eventualmente usas S3
# def get_storage_service():
#     # Aquí podrías retornar local_storage o s3_storage según la configuración
#     return LocalStorageService()