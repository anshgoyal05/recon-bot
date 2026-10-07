from app.ai.provider import LLMProvider
from app.ai.gemini import GeminiProvider
from app.ai.mock import MockProvider
from app.config import settings

def get_llm_provider() -> LLMProvider:
    if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 5:
        return GeminiProvider(api_key=settings.GEMINI_API_KEY)
    return MockProvider()

__all__ = ["LLMProvider", "GeminiProvider", "MockProvider", "get_llm_provider"]
