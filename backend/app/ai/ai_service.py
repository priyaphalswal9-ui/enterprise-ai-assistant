from backend.app.ai.context_builder import (
    build_conversation_context,
    build_rag_context,
)

from backend.app.ai.provider_factory import (
    get_llm_provider,
)

from backend.app.ai.system_prompt import SYSTEM_PROMPT

from backend.app.services.retrieval_service import (
    retrieve_relevant_chunks,
)


class AIService:

    def __init__(self):
        self.provider = get_llm_provider()

    def generate_response(
        self,
        prompt: str,
        conversation_history,
        user_id: int,
    ) -> str:

        # Build conversation history context
        conversation_context = build_conversation_context(
            conversation_history
        )

        # Retrieve relevant document chunks from Chroma
        retrieved_chunks = retrieve_relevant_chunks(
            query=prompt,
            n_results=3,
            user_id=user_id,
        )

        # Prepare source information for citations
        sources = [
            {
                "filename": chunk["filename"],
                "chunk_index": chunk["metadata"]["chunk_index"],
            }
            for chunk in retrieved_chunks
        ]

        # Build context from retrieved document chunks
        rag_context = build_rag_context(
            retrieved_chunks
        )

        final_prompt = f"""
{SYSTEM_PROMPT}

Conversation history:
{conversation_context}

Relevant document context:
{rag_context}

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

            return {
                "answer": response,
                "sources": sources,
            }

        except Exception as error:
            raise RuntimeError(
                f"AI generation failed: {error}"
            ) from error

    def generate_response_stream(
        self,
        prompt: str,
        conversation_history,
    ):

        conversation_context = build_conversation_context(
            conversation_history
        )

        final_prompt = f"""
{SYSTEM_PROMPT}

Conversation history:
{conversation_context}

Current user message:
{prompt}
"""

        return self.provider.generate_stream(
            final_prompt,
            conversation_history,
        )