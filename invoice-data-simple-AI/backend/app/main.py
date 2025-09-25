import os
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal

from .services import inference


class InferResponse(BaseModel):
    provider: str
    detections: list
    fields: dict


def create_app() -> FastAPI:
    app = FastAPI(title="Invoice Field Detector (RT-DETR)", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "ok", "provider": inference.get_provider_name()}

    @app.post("/infer", response_model=InferResponse)
    async def infer(
        file: UploadFile = File(...),
        document_type: Literal["invoice", "dni_front", "dni_back"] = Query("invoice"),
        conf: float = Query(float(os.getenv("CONF_THRESHOLD", 0.25))),
        iou: float = Query(float(os.getenv("IOU_THRESHOLD", 0.45)))
    ):
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Archivo vacío")
        detections, fields = await inference.run_inference(content, file.filename, document_type, conf, iou)
        return InferResponse(provider=inference.get_provider_name(), detections=detections, fields=fields)

    return app


app = create_app()

