from google import genai

from backend.app.ai.base_provider import BaseLLMProvider
from backend.app.core.config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiProvider(BaseLLMProvider):

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    def generate(
        self,
        prompt: str,
        conversation_history,
    ) -> str:

        response = self.client.interactions.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text