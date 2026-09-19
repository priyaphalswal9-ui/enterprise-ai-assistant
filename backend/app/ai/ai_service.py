import json

from sqlalchemy.orm import Session

from backend.app.ai.context_builder import (
    build_conversation_context,
    build_rag_context,
)
from backend.app.ai.provider_factory import get_llm_provider
from backend.app.ai.system_prompt import SYSTEM_PROMPT
from backend.app.ai.tools import DOCUMENT_TOOLS
from backend.app.ai.tool_executor import execute_tool
from backend.app.services.retrieval_service import retrieve_relevant_chunks


class AIService:

    def __init__(self):
        self.provider = get_llm_provider()

    def generate_response(
        self,
        prompt: str,
        conversation_history,
        user_id: int,
        db: Session,
    ) -> dict:

        try:
            conversation_context = build_conversation_context(
                conversation_history
            )

            # -----------------------------------------
            # TOOL-CALLING FLOW
            # -----------------------------------------

            tool_prompt = f"""
{SYSTEM_PROMPT}

Conversation history:
{conversation_context}

Current user message:
{prompt}

You have access to tools for working with the user's documents.
Use a tool when the user's request requires information about
their uploaded documents.

If the user asks what documents they uploaded, use
list_user_documents.

If the user asks for information contained in their documents,
use search_documents.

Do not use a tool for general knowledge questions.
"""

            response = self.provider.generate_with_tools(
                prompt=tool_prompt,
                conversation_history=[],
                tools=DOCUMENT_TOOLS,
            )

            tool_calls = getattr(
                response.message,
                "tool_calls",
                None,
            )

            # -----------------------------------------
            # NO TOOL CALL
            # -----------------------------------------

            if not tool_calls:

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

                answer = self.provider.generate(
                    prompt=final_prompt,
                    conversation_history=[],
                )

                if not answer:
                    raise RuntimeError(
                        "LLM provider returned an empty response"
                    )

                return {
                    "answer": answer,
                    "sources": sources,
                }

            # -----------------------------------------
            # TOOL EXECUTION
            # -----------------------------------------

            tool_results = []

            for tool_call in tool_calls:

                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments or {}

                if isinstance(arguments, str):
                    arguments = json.loads(arguments)

                result = execute_tool(
                    tool_name=tool_name,
                    arguments=arguments,
                    db=db,
                    user_id=user_id,
                )

                tool_results.append(
                    {
                        "tool": tool_name,
                        "result": result,
                    }
                )

            # -----------------------------------------
            # FINAL RESPONSE AFTER TOOL
            # -----------------------------------------

            final_prompt = f"""
{SYSTEM_PROMPT}

Current user message:
{prompt}

Tool results:
{json.dumps(tool_results, indent=2, default=str)}

Answer the user's question using the tool results above.

Do not mention tools, databases, internal systems,
or implementation details.

If the tool results do not contain enough information,
say so clearly.
"""

            answer = self.provider.generate(
                prompt=final_prompt,
                conversation_history=[],
            )

            if not answer:
                raise RuntimeError(
                    "LLM provider returned an empty response"
                )

            # -----------------------------------------
            # BUILD SOURCES
            # -----------------------------------------

            sources = []

            for tool_result in tool_results:

                result = tool_result["result"]

                if not isinstance(result, list):
                    continue

                for item in result:

                    if (
                        isinstance(item, dict)
                        and "filename" in item
                        and "metadata" in item
                    ):
                        sources.append(
                            {
                                "filename": item["filename"],
                                "chunk_index": item["metadata"][
                                    "chunk_index"
                                ],
                            }
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