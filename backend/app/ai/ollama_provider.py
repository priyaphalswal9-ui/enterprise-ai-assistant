import time

from ollama import Client

from backend.app.ai.base_provider import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):

    def __init__(self):
        self.client = Client(host="http://localhost:11434")
        self.model = "llama3.2:1b"
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
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )

                content = response["message"]["content"]

                if not content:
                    raise RuntimeError(
                        "Ollama returned an empty response"
                    )

                return content

            except Exception as error:
                last_error = error

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise RuntimeError(
                        f"Ollama generation failed after "
                        f"{self.max_retries} attempts: {last_error}"
                    ) from last_error

    def generate_stream(
        self,
        prompt: str,
        conversation_history,
    ):

        stream = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            stream=True,
        )

        for chunk in stream:
            content = chunk["message"]["content"]

            if content:
                yield content