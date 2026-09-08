from backend.app.ai.base_provider import BaseLLMProvider
from backend.app.ai.gemini_provider import GeminiProvider
from backend.app.ai.ollama_provider import OllamaProvider
from backend.app.core.config import LLM_PROVIDER


def get_llm_provider() -> BaseLLMProvider:

    if LLM_PROVIDER == "gemini":
        return GeminiProvider()

    if LLM_PROVIDER == "ollama":
        return OllamaProvider()

    raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")