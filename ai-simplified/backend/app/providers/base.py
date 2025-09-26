from abc import ABC, abstractmethod


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def extract(self, content: bytes, filename: str, document_type: str) -> dict:
        ...

