import base64
from .base import BaseProvider


class MockProvider(BaseProvider):
    name = "mock"

    async def extract(self, content: bytes, filename: str, document_type: str) -> dict:
        preview_b64 = base64.b64encode(content[:64]).decode("utf-8")
        return {
            "document_type": document_type,
            "filename": filename,
            "size_bytes": len(content),
            "preview_b64_first64": preview_b64,
            "fields": {
                "issuer_name": "ACME S.A.",
                "invoice_number": "F-000123",
                "issue_date": "2024-01-31",
                "total_amount": "12345.67",
            },
        }

