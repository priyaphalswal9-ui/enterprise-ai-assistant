from backend.app.ai.context_builder import build_conversation_context
from backend.app.ai.provider_factory import get_llm_provider
from backend.app.ai.system_prompt import SYSTEM_PROMPT


class AIService:

    def __init__(self):
        self.provider = get_llm_provider()

    def generate_response(
        self,
        prompt: str,
        conversation_history,
    ) -> str:

        context = build_conversation_context(
            conversation_history
        )

        final_prompt = f"""
{SYSTEM_PROMPT}

Conversation history:
{context}

Current user message:
{prompt}
"""

        try:
            response = self.provider.generate(
                final_prompt,
                conversation_history,
            )

            if not response:
                raise RuntimeError(
                    "LLM provider returned an empty response"
                )

            return response

        except Exception as error:
            raise RuntimeError(
                f"AI generation failed: {error}"
            ) from error

    def generate_response_stream(
        self,
        prompt: str,
        conversation_history,
    ):

        context = build_conversation_context(
            conversation_history
        )

        final_prompt = f"""
{SYSTEM_PROMPT}

Conversation history:
{context}

Current user message:
{prompt}
"""

        return self.provider.generate_stream(
            final_prompt,
            conversation_history,
        )