import json

from sqlalchemy.orm import Session

from backend.app.ai.context_builder import (
    build_conversation_context,
    build_rag_context,
)

from backend.app.ai.provider_factory import (
    get_llm_provider,
)

from backend.app.ai.system_prompt import SYSTEM_PROMPT

from backend.app.ai.tools import DOCUMENT_TOOLS

from backend.app.ai.tool_executor import (
    execute_tool,
)

from backend.app.services.retrieval_service import (
    retrieve_relevant_chunks,
)


class AIService:

    def __init__(self):
        self.provider = get_llm_provider()

    def is_document_list_query(self, prompt: str) -> bool:
        text = prompt.lower()

        keywords = [
            "what documents",
            "which documents",
            "my documents",
            "uploaded documents",
            "documents have i uploaded",
            "list my documents",
        ]

        return any(
            keyword in text
            for keyword in keywords
        )

    def generate_response(
        self,
        prompt: str,
        conversation_history,
        user_id: int,
        db: Session,
    ) -> dict:

        try:

            # -----------------------------------------
            # DOCUMENT TOOL FLOW
            # -----------------------------------------

            if self.is_document_list_query(prompt):

                tool_result = execute_tool(
                    tool_name="list_user_documents",
                    arguments={},
                    db=db,
                    user_id=user_id,
                )

                tool_prompt = f"""
{SYSTEM_PROMPT}

The user asked:
{prompt}

The user's uploaded documents are:
{json.dumps(tool_result, indent=2)}

Answer the user's question using the document information above.
Do not mention tools, databases, internal systems, or implementation details.
If there are no uploaded documents, clearly tell the user that no documents
have been uploaded.
"""

                response = self.provider.generate(
                    prompt=tool_prompt,
                    conversation_history=[],
                )

                if not response:
                    raise RuntimeError(
                        "LLM provider returned an empty response"
                    )

                return {
                    "answer": response,
                    "sources": [],
                }

            # -----------------------------------------
            # NORMAL RAG FLOW
            # -----------------------------------------

            conversation_context = (
                build_conversation_context(
                    conversation_history
                )
            )

            retrieved_chunks = (
                retrieve_relevant_chunks(
                    query=prompt,
                    n_results=3,
                    user_id=user_id,
                )
            )

            sources = [
                {
                    "filename": chunk["filename"],
                    "chunk_index": chunk["metadata"][
                        "chunk_index"
                    ],
                }
                for chunk in retrieved_chunks
            ]

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

            messages = [
                {
                    "role": "user",
                    "content": final_prompt,
                }
            ]

            response = self.provider.generate_with_tools(
                prompt=final_prompt,
                conversation_history=messages,
                tools=[],
            )

            answer = response.message.content

            if not answer:
                raise RuntimeError(
                    "LLM provider returned an empty response"
                )

            return {
                "answer": answer,
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

        conversation_context = (
            build_conversation_context(
                conversation_history
            )
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