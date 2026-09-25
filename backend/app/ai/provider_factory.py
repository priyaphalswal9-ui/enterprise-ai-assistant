from backend.app.core.config import LLM_PROVIDER


def get_llm_provider():
    if LLM_PROVIDER == "gemini":
        from backend.app.ai.gemini_provider import GeminiProvider

        return GeminiProvider()

    if LLM_PROVIDER == "ollama":
        from backend.app.ai.ollama_provider import OllamaProvider

        return OllamaProvider()

    raise ValueError(
        f"Unsupported LLM provider: {LLM_PROVIDER}"
    )