# Imagen base con Python 3.11 (slim para reducir tamaño)
FROM python:3.11-slim-bookworm

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema:
# - tesseract-ocr y datos de español
# - libgl1-mesa-glx (para OpenCV)
# - build-essential y python3-dev (para compilar paquetes sin wheel precompilado)
# - libglib2.0-0 (para OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 1000 -r requirements.txt

# Crear directorios necesarios
RUN mkdir -p /app/models/yolo_models /app/uploaded_documents_local /app/logs

# Copia los modelos Yolo (si existen)
COPY models/yolo_models/ /app/models/yolo_models/

# Copiar el resto del código fuente al contenedor
COPY . .

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Exponer puerto de la API
EXPOSE 8000

# Comando de arranque con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
