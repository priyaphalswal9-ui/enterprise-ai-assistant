from sqlalchemy.orm import Session

from backend.app.ai.context_builder import (
    build_conversation_context,
    build_rag_context,
)

from backend.app.ai.provider_factory import (
    get_llm_provider,
)

from backend.app.ai.system_prompt import SYSTEM_PROMPT

from backend.app.ai.tool_executor import (
    execute_tool,
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

    def is_document_search_query(self, prompt: str) -> bool:
        text = prompt.lower()

        keywords = [
            "according to the document",
            "according to the documents",
            "in the document",
            "in the documents",
            "what does the document say",
            "what do the documents say",
            "find in my documents",
            "search my documents",
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
            # DOCUMENT LIST TOOL
            # -----------------------------------------

            if self.is_document_list_query(prompt):

                tool_result = execute_tool(
                    tool_name="list_user_documents",
                    arguments={},
                    db=db,
                    user_id=user_id,
                )

                if not tool_result:
                    return {
                        "answer": "You have not uploaded any documents.",
                        "sources": [],
                    }

                document_lines = []

                for index, document in enumerate(
                    tool_result,
                    start=1,
                ):
                    document_lines.append(
                        f"{index}. {document['filename']}"
                    )

                return {
                    "answer": (
                        "You have uploaded the following documents:\n\n"
                        + "\n".join(document_lines)
                    ),
                    "sources": [],
                }

            # -----------------------------------------
            # DOCUMENT SEARCH TOOL
            # -----------------------------------------

            if self.is_document_search_query(prompt):

                tool_result = execute_tool(
                    tool_name="search_documents",
                    arguments={
                        "query": prompt,
                    },
                    db=db,
                    user_id=user_id,
                )

                sources = [
                    {
                        "filename": chunk["filename"],
                        "chunk_index": chunk["metadata"]["chunk_index"],
                    }
                    for chunk in tool_result
                ]

                document_context = build_rag_context(
                    tool_result
                )

                search_prompt = f"""
{SYSTEM_PROMPT}

Relevant information from the user's documents:
{document_context}

Current user question:
{prompt}

Answer the question using the relevant document information above.
Do not mention tools, databases, internal systems, or implementation details.
If the documents do not contain enough information to answer the question,
say so clearly.
"""

                response = self.provider.generate(
                    prompt=search_prompt,
                    conversation_history=[],
                )

                if not response:
                    raise RuntimeError(
                        "LLM provider returned an empty response"
                    )

                return {
                    "answer": response,
                    "sources": sources,
                }

            # -----------------------------------------
            # NORMAL RAG FLOW
            # -----------------------------------------

            conversation_context = (
                build_conversation_context(
                    conversation_history
                )
            )

            from backend.app.services.retrieval_service import (
                retrieve_relevant_chunks,
            )

            retrieved_chunks = retrieve_relevant_chunks(
                query=prompt,
                n_results=3,
                user_id=user_id,
            )

            sources = [
                {
                    "filename": chunk["filename"],
                    "chunk_index": chunk["metadata"]["chunk_index"],
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

            response = self.provider.generate(
                prompt=final_prompt,
                conversation_history=conversation_history,
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