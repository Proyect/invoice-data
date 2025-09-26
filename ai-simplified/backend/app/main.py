from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
import os

from .providers import get_provider

class ExtractResponse(BaseModel):
    status: Literal["success", "error"]
    provider: str
    extracted: dict | None = None
    error: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="AI-Simplified OCR Extraction", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        provider = os.getenv("PROVIDER", "mock")
        return {"status": "ok", "provider": provider}

    @app.post("/api/v1/extract", response_model=ExtractResponse)
    async def extract(
        file: UploadFile = File(...),
        document_type: Literal["dni_front", "dni_back", "invoice"] = Query("invoice")
    ):
        try:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Archivo vacío")

            provider = get_provider()
            result = await provider.extract(content, filename=file.filename, document_type=document_type)
            return ExtractResponse(status="success", provider=provider.name, extracted=result)
        except HTTPException:
            raise
        except Exception as e:
            return ExtractResponse(status="error", provider=os.getenv("PROVIDER", "mock"), error=str(e))

    return app


app = create_app()

