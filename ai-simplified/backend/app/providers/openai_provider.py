import os
from typing import Any, Dict
from .base import BaseProvider
from openai import AsyncOpenAI


INVOICE_SYSTEM_PROMPT = (
    "Eres un extractor de datos de documentos. Devuelve JSON puro con campos: "
    "issuer_name, invoice_number, issue_date (YYYY-MM-DD), total_amount (string), currency (string, opcional)."
)

DNI_SYSTEM_PROMPT = (
    "Eres un extractor de datos de DNI argentino. Devuelve JSON puro con campos: "
    "apellido, nombre, numero_documento, fecha_nacimiento (YYYY-MM-DD)."
)


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY no configurada")
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    async def extract(self, content: bytes, filename: str, document_type: str) -> Dict[str, Any]:
        system_prompt = INVOICE_SYSTEM_PROMPT if "invoice" in document_type else DNI_SYSTEM_PROMPT

        # OpenAI Vison input con imagen en bytes
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Extrae datos del tipo: {document_type}. Devuelve JSON válido."},
                        {
                            "type": "input_image",
                            "image_url": {
                                "url": f"data:image/{_ext_from_name(filename)};base64,{_to_b64(content)}"
                            },
                        },
                    ],
                },
            ],
            temperature=0.0,
        )

        text = response.choices[0].message.content or "{}"
        # La respuesta debe ser JSON; el cliente puede validarlo/sanitizarlo si requiere
        return {"raw": text}


def _to_b64(content: bytes) -> str:
    import base64
    return base64.b64encode(content).decode("utf-8")


def _ext_from_name(name: str) -> str:
    name = (name or "").lower()
    if name.endswith(".png"):
        return "png"
    if name.endswith(".jpg") or name.endswith(".jpeg"):
        return "jpeg"
    if name.endswith(".webp"):
        return "webp"
    if name.endswith(".pdf"):
        return "pdf"
    return "png"

