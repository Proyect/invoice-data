# Imagen base con Python 3.11 (slim para reducir tamaño)
FROM python:3.11-slim-bookworm

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema:
# - tesseract-ocr y datos de español
# - libgl1-mesa-glx (para OpenCV)
# - build-essential y python3-dev (para compilar paquetes sin wheel precompilado)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 1000 -r requirements.txt

# Copia los modelos Yolo
COPY models/yolo_models/ /app/models/yolo_models/

# Copiar el resto del código fuente al contenedor
COPY . .

# Exponer puerto de la API
EXPOSE 8000

# Comando de arranque con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
