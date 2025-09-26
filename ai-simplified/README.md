AI-Simplified OCR Extraction (LLM-based)

Resumen
- Backend FastAPI que extrae datos estructurados desde imágenes/PDF usando un proveedor LLM (OpenAI Vision) o un proveedor mock para desarrollo.
- Sin YOLO/Celery/Redis. Procesamiento síncrono por simplicidad.
- Endpoints mínimos: health y POST /api/v1/extract.

Rápido inicio (Docker)
1) Copia .env.example a .env y completa variables.
2) docker compose up --build
3) Probar health: http://localhost:8000/health

Rápido inicio (local)
1) cd backend
2) python -m venv .venv && source .venv/bin/activate
3) pip install -r requirements.txt
4) uvicorn app.main:app --reload

Variables de entorno (.env)
- PROVIDER=openai|mock (default: mock)
- OPENAI_API_KEY=sk-... (requerido si PROVIDER=openai)
- OPENAI_MODEL=gpt-4o-mini (default)

Endpoint principal
POST /api/v1/extract
- Form fields: file (UploadFile), document_type (query: dni_front|dni_back|invoice)
- Respuesta: { status: "success", provider: string, extracted: object }

Notas de arquitectura
- FastAPI + providers desacoplados en app/providers.
- Esquema de salida forzado a JSON; prompts específicos por tipo de documento.
- Se puede cambiar a Google DocAI / AWS Textract creando un nuevo provider.

Seguridad
- No se almacena el archivo; solo se procesa en memoria.
- Añadir autenticación JWT o API Key si se requiere.

Licencia
MIT

