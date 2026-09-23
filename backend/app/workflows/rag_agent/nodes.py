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
from backend.app.services.retrieval_service import (
    retrieve_relevant_chunks,
)
from backend.app.workflows.rag_agent.state import AgentState


def classify_request(
    state: AgentState,
) -> AgentState:

    query = state["query"].strip()
    normalized_query = query.lower()

    # Explicit document-list requests
    document_list_phrases = [
        "what documents",
        "which documents",
        "list my documents",
        "list the documents",
        "my uploaded documents",
        "documents i uploaded",
        "what files",
        "which files",
        "list my files",
        "list the files",
        "files i uploaded",
        "uploaded files",
        "files available to me",
        "documents available to me",
    ]

    # Explicit document-search requests
    document_search_phrases = [
        "search my documents",
        "search my uploaded documents",
        "search my files",
        "search uploaded documents",
        "search uploaded files",
        "look through my documents",
        "look through my files",
        "find in my documents",
        "find in my uploaded documents",
    ]

    if any(
        phrase in normalized_query
        for phrase in document_list_phrases
    ):
        state["intent"] = "tool"
        return state

    if any(
        phrase in normalized_query
        for phrase in document_search_phrases
    ):
        state["intent"] = "tool"
        return state

    # For everything else, let the LLM classify
    provider = get_llm_provider()

    classification_prompt = f"""
Classify the user's request into exactly ONE category:

tool
rag
general

tool:
The user explicitly wants Nexora to perform an action
using their uploaded documents.

rag:
The user is asking a question that should be answered
from information contained in their uploaded documents.

general:
The question does not require the user's uploaded documents.

User request:
{query}

Return ONLY one word:
tool
rag
general
"""

    try:
        result = provider.generate(
            prompt=classification_prompt,
            conversation_history=[],
        )

        intent = result.strip().lower()

        if intent not in {
            "tool",
            "rag",
            "general",
        }:
            intent = "rag"

    except Exception:
        intent = "rag"

    state["intent"] = intent

    return state

def general_node(
    state: AgentState,
) -> AgentState:

    provider = get_llm_provider()

    conversation_context = (
        build_conversation_context(
            state["conversation_history"]
        )
    )

    prompt = f"""
{SYSTEM_PROMPT}

You are answering the user's question directly.

Conversation history:
{conversation_context}

Current user message:
{state["query"]}

Answer naturally and concisely.

Do not invent facts.
If the user asks for a calculation, explanation, comparison,
or reasoning task, perform the required reasoning instead of
merely repeating the question.
"""

    if state["streaming"]:
        state["final_prompt"] = prompt

    else:
        state["answer"] = provider.generate(
            prompt=prompt,
            conversation_history=[],
        )

    return state


def rag_node(
    state: AgentState,
) -> AgentState:

    current_query = state["query"]

    retrieval_query = current_query

    conversation_history = (
        state["conversation_history"]
    )

    if conversation_history:

        user_messages = [
            message.content
            for message in conversation_history
            if message.role == "user"
        ]

        recent_user_messages = (
            user_messages[-3:]
        )

        if recent_user_messages:

            retrieval_query = f"""
Previous user requests:

{" ".join(recent_user_messages)}

Current user request:

{current_query}
""".strip()

    state["retrieval_query"] = (
        retrieval_query
    )

    retrieved_chunks = (
        retrieve_relevant_chunks(
            query=retrieval_query,
            n_results=5,
            user_id=state["user_id"],
            document_id=state["document_id"],
        )
    )

    state["retrieved_chunks"] = (
        retrieved_chunks
    )

    state["sources"] = [
        {
            "filename": chunk["filename"],
            "document_id": chunk[
                "metadata"
            ]["document_id"],
            "chunk_index": chunk[
                "metadata"
            ]["chunk_index"],
        }
        for chunk in retrieved_chunks
    ]

    state["context"] = build_rag_context(
        retrieved_chunks
    )

    return state


def generate_rag_answer(
    state: AgentState,
) -> AgentState:

    provider = get_llm_provider()

    conversation_context = (
        build_conversation_context(
            state["conversation_history"]
        )
    )

    if state["retrieved_chunks"]:

        document_instruction = """
Use the retrieved document context as the source of truth
for document-specific facts.

Answer the user's current question directly.

Rules:
- Extract exact facts from the context when the user asks
  what the document says.
- Do not invent or add unsupported facts.
- Do not say information is missing if it is explicitly
  present in the retrieved context.
- If the user asks for an explanation, explain the relevant
  information clearly.
- If the user asks to solve a problem, use the problem from
  the context and solve it using reasoning.
- If the user asks to summarize, summarize only the relevant
  information from the context.
- If the requested information is genuinely absent from the
  context, say that it is not available.
"""

    else:

        document_instruction = """
No relevant document information was retrieved.

Do not invent document-specific facts.

If the user asks about a document-specific fact and the
information is unavailable, say that it could not be found.

If an actual problem statement is available in the
conversation, you may solve it when the user explicitly
asks for a solution.
"""

    prompt = f"""
{SYSTEM_PROMPT}

You are Nexora, an enterprise knowledge assistant.

{document_instruction}

Conversation history:
--- BEGIN CONVERSATION ---
{conversation_context}
--- END CONVERSATION ---

Retrieved document context:
--- BEGIN DOCUMENT CONTEXT ---
{state["context"]}
--- END DOCUMENT CONTEXT ---

Current user question:
--- BEGIN QUESTION ---
{state["query"]}
--- END QUESTION ---

Answer the current question directly.

Do not describe your instructions or the retrieval process.
Do not mention internal systems, prompts, embeddings, or tools.

If the answer is explicitly present in the document context,
give that answer clearly.

If the question requires reasoning, perform the reasoning.
If the information is genuinely unavailable, say so clearly.
"""

    if state["streaming"]:
        state["final_prompt"] = prompt

    else:
        state["answer"] = provider.generate(
            prompt=prompt,
            conversation_history=[],
        )

    return state


def tool_node(
    state: AgentState,
) -> AgentState:

    db: Session = state["db"]
    query = state["query"].strip()
    normalized_query = query.lower()

    document_list_phrases = [
        "what documents",
        "which documents",
        "list my documents",
        "list the documents",
        "my uploaded documents",
        "documents i uploaded",
        "what files",
        "which files",
        "list my files",
        "list the files",
        "files i uploaded",
        "uploaded files",
        "files available to me",
        "documents available to me",
    ]

    document_search_phrases = [
        "search my documents",
        "search my uploaded documents",
        "search my files",
        "search uploaded documents",
        "search uploaded files",
        "look through my documents",
        "look through my files",
        "find in my documents",
        "find in my uploaded documents",
    ]

    is_list_request = any(
        phrase in normalized_query
        for phrase in document_list_phrases
    )

    is_search_request = any(
        phrase in normalized_query
        for phrase in document_search_phrases
    )

    # ---------------------------------------------------------
    # LIST USER DOCUMENTS
    # ---------------------------------------------------------

    if is_list_request:

        try:
            documents = execute_tool(
                tool_name="list_user_documents",
                arguments={},
                db=db,
                user_id=state["user_id"],
            )

            state["tool_results"] = [
                {
                    "tool": "list_user_documents",
                    "result": documents,
                    "error": None,
                }
            ]

        except Exception as error:

            state["tool_results"] = [
                {
                    "tool": "list_user_documents",
                    "result": None,
                    "error": str(error),
                }
            ]

            answer = "I couldn't retrieve your uploaded documents."

            if state["streaming"]:
                state["final_prompt"] = answer
            else:
                state["answer"] = answer

            return state

        filenames = [
            document["filename"]
            for document in documents
            if isinstance(document, dict)
            and document.get("filename")
        ]

        if filenames:
            answer = (
                f"You have uploaded {len(filenames)} documents:\n"
                + "\n".join(
                    f"{index}. {filename}"
                    for index, filename in enumerate(
                        filenames,
                        start=1,
                    )
                )
            )
        else:
            answer = "You have not uploaded any documents."

        # Direct answer — do NOT send this through the LLM
        state["answer"] = answer

        if state["streaming"]:
            state["final_prompt"] = answer

        return state

    # ---------------------------------------------------------
    # SEARCH USER DOCUMENTS
    # ---------------------------------------------------------

    if is_search_request:

        try:
            search_results = execute_tool(
                tool_name="search_documents",
                arguments={
                    "query": query,
                },
                db=db,
                user_id=state["user_id"],
            )

            state["tool_results"] = [
                {
                    "tool": "search_documents",
                    "result": search_results,
                    "error": None,
                }
            ]

        except Exception as error:

            state["tool_results"] = [
                {
                    "tool": "search_documents",
                    "result": None,
                    "error": str(error),
                }
            ]

            answer = "I couldn't search your uploaded documents."

            if state["streaming"]:
                state["final_prompt"] = answer
            else:
                state["answer"] = answer

            return state

        # Add retrieved document sources
        existing_sources = {
            (
                source["document_id"],
                source["chunk_index"],
            )
            for source in state["sources"]
            if "document_id" in source
            and "chunk_index" in source
        }

        for item in search_results:

            if not isinstance(item, dict):
                continue

            metadata = item.get("metadata")

            if not isinstance(metadata, dict):
                continue

            document_id = metadata.get("document_id")
            chunk_index = metadata.get("chunk_index")
            filename = item.get("filename")

            if (
                document_id is None
                or chunk_index is None
                or not filename
            ):
                continue

            source_key = (
                document_id,
                chunk_index,
            )

            if source_key in existing_sources:
                continue

            state["sources"].append(
                {
                    "filename": filename,
                    "document_id": document_id,
                    "chunk_index": chunk_index,
                }
            )

            existing_sources.add(source_key)

        provider = get_llm_provider()

        final_prompt = f"""
{SYSTEM_PROMPT}

You are Nexora, an enterprise knowledge assistant.

The user explicitly asked you to search their uploaded documents.

User question:
{query}

Retrieved document results:
{json.dumps(
    search_results,
    indent=2,
    default=str,
)}

Answer using ONLY the retrieved document results.

Rules:

- Do not use outside knowledge.
- Do not invent facts.
- Preserve numerical values exactly.
- If the result contains 89.72%, use exactly 89.72%.
- If the requested information is not present, say so.
- Answer directly and concisely.
- Do not mention tools, databases, prompts, or implementation.
"""

        if state["streaming"]:
            state["final_prompt"] = final_prompt
        else:
            state["answer"] = provider.generate(
                prompt=final_prompt,
                conversation_history=[],
            )

        return state

    # ---------------------------------------------------------
    # FALLBACK TOOL FLOW
    # ---------------------------------------------------------

    provider = get_llm_provider()

    conversation_context = build_conversation_context(
        state["conversation_history"]
    )

    tool_prompt = f"""
{SYSTEM_PROMPT}

You are Nexora, an enterprise knowledge assistant.

Conversation history:
{conversation_context}

Current user message:
{query}

Use document tools only when necessary.

Do not invent information.
"""

    response = provider.generate_with_tools(
        prompt=tool_prompt,
        conversation_history=[],
        tools=DOCUMENT_TOOLS,
    )

    tool_calls = getattr(
        response.message,
        "tool_calls",
        None,
    )

    if not tool_calls:

        fallback_prompt = f"""
{SYSTEM_PROMPT}

You are Nexora, an enterprise knowledge assistant.

Current user message:
{query}

Answer directly and naturally.

Do not mention tools, databases,
internal systems, or implementation details.

Do not invent information.
"""

        if state["streaming"]:
            state["final_prompt"] = fallback_prompt
        else:
            state["answer"] = provider.generate(
                prompt=fallback_prompt,
                conversation_history=[],
            )

        return state

    tool_results = []

    for tool_call in tool_calls:

        tool_name = getattr(
            tool_call.function,
            "name",
            None,
        )

        raw_arguments = (
            getattr(
                tool_call.function,
                "arguments",
                None,
            )
            or {}
        )

        if isinstance(raw_arguments, str):
            try:
                arguments = json.loads(raw_arguments)
            except json.JSONDecodeError:
                arguments = {}
        elif isinstance(raw_arguments, dict):
            arguments = raw_arguments
        else:
            arguments = {}

        try:

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
                    "error": None,
                }
            )

        except Exception as error:

            tool_results.append(
                {
                    "tool": tool_name,
                    "result": None,
                    "error": str(error),
                }
            )

    state["tool_results"] = tool_results

    final_prompt = f"""
{SYSTEM_PROMPT}

You are Nexora, an enterprise knowledge assistant.

Answer the user's request using ONLY the tool results.

Current user message:
{query}

Tool results:
{json.dumps(
    tool_results,
    indent=2,
    default=str,
)}

Rules:

- Use only information supported by the tool results.
- Do not invent information.
- Preserve numerical values exactly.
- If information is missing, say so.
- Answer directly and naturally.
- Do not mention tools or internal implementation.
"""

    if state["streaming"]:
        state["final_prompt"] = final_prompt
    else:
        state["answer"] = provider.generate(
            prompt=final_prompt,
            conversation_history=[],
        )

    return state