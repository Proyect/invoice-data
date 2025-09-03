# ocr_api/main.py

from fastapi import FastAPI
from api.v1 import auth, documents
from database import create_db_and_tables # Importa la función de creación de tablas

app = FastAPI(
    title="OCR Document Processor API",
    description="API para subir, procesar y extraer datos de documentos oficiales y facturas.",
    version="1.0.0",
)

# Incluir los routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])

# Se ejecutará al iniciar la aplicación (solo si se ejecuta directamente con `uvicorn main:app`)
# Si usas docker-compose y migraciones, esto podría no ser necesario aquí
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Welcome to the OCR Document Processor API!"}