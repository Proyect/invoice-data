import os
from .base import BaseProvider
from .mock_provider import MockProvider
from .openai_provider import OpenAIProvider


def get_provider() -> BaseProvider:
    provider_name = os.getenv("PROVIDER", "mock").lower()
    if provider_name == "openai":
        return OpenAIProvider()
    return MockProvider()

