import time

from google import genai

from backend.app.ai.base_provider import BaseLLMProvider
from backend.app.core.config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiProvider(BaseLLMProvider):

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

        self.max_retries = 3
        self.retry_delay = 1

    def generate(
        self,
        prompt: str,
        conversation_history,
    ) -> str:

        last_error = None

        for attempt in range(self.max_retries):

            try:
                response = self.client.interactions.create(
                    model=self.model,
                    input=prompt,
                )

                content = response.output_text

                if not content:
                    raise RuntimeError(
                        "Gemini returned an empty response"
                    )

                return content

            except Exception as error:
                last_error = error

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise RuntimeError(
                        f"Gemini generation failed after "
                        f"{self.max_retries} attempts: {last_error}"
                    ) from last_error

    def generate_stream(
        self,
        prompt: str,
        conversation_history,
    ):

        stream = self.client.interactions.create(
            model=self.model,
            input=prompt,
            stream=True,
        )

        for event in stream:
            if getattr(event, "type", None) == "content.delta":
                text = getattr(event.delta, "text", None)

                if text:
                    yield text