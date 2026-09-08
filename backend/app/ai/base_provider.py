from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str, conversation_history) -> str:
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, conversation_history):
        pass