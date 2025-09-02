# Usa una imagen base de Python oficial, preferiblemente con Alpine o Slim para menor tamaño
FROM python:3.13

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala Tesseract OCR y sus datos de idioma para español
# `tesseract-ocr` es el motor, `tesseract-ocr-spa` son los datos para español
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \ # Requerido por OpenCV en algunos sistemas sin display
    && rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código fuente de tu aplicación al contenedor
COPY . .

# Expone el puerto en el que correrá la API
EXPOSE 8000

# Comando para iniciar la aplicación usando Uvicorn
# --host 0.0.0.0 es necesario para que sea accesible desde fuera del contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]