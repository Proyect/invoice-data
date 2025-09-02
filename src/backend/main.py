
from fastapi import FastAPI
from api.v1 import auth, documents

app = FastAPI(
    title="OCR Document Processor API",
    description="API para subir, procesar y extraer datos de documentos oficiales y facturas.",
    version="1.0.0",
)

# Incluir los routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])

@app.get("/")
async def root():
    return {"message": "Welcome to the OCR Document Processor API!"}

def main():
    print("start the process")
    
if __name__ == "__main__":
    main()
    