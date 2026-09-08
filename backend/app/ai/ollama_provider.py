from ollama import Client

from backend.app.ai.base_provider import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):

    def __init__(self):
        self.client = Client(host="http://localhost:11434")
        self.model = "llama3.2:1b"

    def generate(
        self,
        prompt: str,
        conversation_history,
    ) -> str:

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response["message"]["content"]