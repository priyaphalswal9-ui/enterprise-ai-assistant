import json

from sqlalchemy.orm import Session

from backend.app.ai.context_builder import (
    build_conversation_context,
    build_rag_context,
)
from backend.app.ai.provider_factory import get_llm_provider
from backend.app.ai.system_prompt import SYSTEM_PROMPT
from backend.app.ai.tool_executor import execute_tool
from backend.app.ai.tools import DOCUMENT_TOOLS
from backend.app.services.retrieval_service import retrieve_relevant_chunks
from backend.app.workflows.rag_agent.state import AgentState


def classify_request(state: AgentState) -> AgentState:
    query = state["query"].lower().strip()

    if any(
        phrase in query
        for phrase in [
            "uploaded documents",
            "my documents",
            "what documents",
            "list my documents",
            "documents i uploaded",
            "files i uploaded",
            "uploaded files",
        ]
    ):
        state["intent"] = "tool"
    else:
        state["intent"] = "rag"

    return state


def general_node(state: AgentState) -> AgentState:
    provider = get_llm_provider()

    conversation_context = build_conversation_context(
        state["conversation_history"]
    )

    prompt = f"""
{SYSTEM_PROMPT}

Conversation history:
{conversation_context}

Current user message:
{state["query"]}
"""

    if state["streaming"]:
        state["final_prompt"] = prompt
    else:
        state["answer"] = provider.generate(
            prompt=prompt,
            conversation_history=[],
        )

    return state


def rag_node(state: AgentState) -> AgentState:
    retrieved_chunks = retrieve_relevant_chunks(
        query=state["query"],
        n_results=5,
        user_id=state["user_id"],
    )

    state["retrieved_chunks"] = retrieved_chunks

    state["sources"] = [
        {
            "filename": chunk["filename"],
            "chunk_index": chunk["metadata"]["chunk_index"],
        }
        for chunk in retrieved_chunks
    ]

    state["context"] = build_rag_context(retrieved_chunks)

    return state


def generate_rag_answer(state: AgentState) -> AgentState:
    provider = get_llm_provider()

    conversation_context = build_conversation_context(
        state["conversation_history"]
    )

    if state["retrieved_chunks"]:
        document_instruction = """
Use the retrieved document context as the primary source for answering
the user's question.

IMPORTANT:
- Read ALL retrieved context carefully.
- If the answer is present anywhere in the context, use that information.
- Extract the exact fact from the context.
- Do not say that information is missing when it is present.
- Do not invent or add facts that are not supported by the context.
"""
    else:
        document_instruction = """
No relevant information was retrieved from the user's uploaded documents.
Do not invent an answer from the documents.
Clearly state that the information could not be found.
"""

    prompt = f"""
{SYSTEM_PROMPT}

{document_instruction}

Conversation history:
{conversation_context}

Retrieved document context:
{state["context"]}

Current user question:
{state["query"]}

Answer the user's question directly and concisely.
"""

    if state["streaming"]:
        state["final_prompt"] = prompt
    else:
        state["answer"] = provider.generate(
            prompt=prompt,
            conversation_history=[],
        )

    return state


def tool_node(state: AgentState) -> AgentState:
    provider = get_llm_provider()

    conversation_context = build_conversation_context(
        state["conversation_history"]
    )

    tool_prompt = f"""
{SYSTEM_PROMPT}

Conversation history:
{conversation_context}

Current user message:
{state["query"]}

You have access to tools for working with the user's documents.

If the user asks what documents they uploaded, use list_user_documents.

If the user asks for information contained in their documents,
use search_documents.

For search_documents, always provide the user's question as the query argument.

Do not use a tool for general knowledge questions.
"""

    response = provider.generate_with_tools(
        prompt=tool_prompt,
        conversation_history=[],
        tools=DOCUMENT_TOOLS,
    )

    tool_calls = getattr(response.message, "tool_calls", None)

    # No tool call
    if not tool_calls:
        if state["streaming"]:
            state["final_prompt"] = tool_prompt
        else:
            state["answer"] = provider.generate(
                prompt=tool_prompt,
                conversation_history=[],
            )

        return state

    db: Session = state["db"]

    tool_results = []

    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments or {}

        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        if tool_name == "search_documents":
            if not isinstance(arguments, dict):
                arguments = {}

            if not arguments.get("query"):
                arguments["query"] = state["query"]

        result = execute_tool(
            tool_name=tool_name,
            arguments=arguments,
            db=db,
            user_id=state["user_id"],
        )

        tool_results.append(
            {
                "tool": tool_name,
                "result": result,
            }
        )

    state["tool_results"] = tool_results

    final_prompt = f"""
{SYSTEM_PROMPT}

Current user message:
{state["query"]}

Tool results:
{json.dumps(tool_results, indent=2, default=str)}

Answer the user's question using the tool results above.

Do not mention tools, databases, internal systems, or implementation details.

If the tool results do not contain enough information, say so clearly.
"""

    if state["streaming"]:
        state["final_prompt"] = final_prompt
    else:
        state["answer"] = provider.generate(
            prompt=final_prompt,
            conversation_history=[],
        )

    # Add document sources returned by search_documents
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
                state["sources"].append(
                    {
                        "filename": item["filename"],
                        "chunk_index": item["metadata"]["chunk_index"],
                    }
                )

    return state