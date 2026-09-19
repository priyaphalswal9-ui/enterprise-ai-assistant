from sqlalchemy.orm import Session

from backend.app.ai.provider_factory import get_llm_provider
from backend.app.workflows.rag_agent.graph import agent_graph


class AIService:

    def generate_response(
        self,
        prompt,
        conversation_history,
        user_id,
        db,
    ) -> dict:

        initial_state = {
            "user_id": user_id,
            "conversation_id": 0,
            "query": prompt,
            "conversation_history": conversation_history,
            "db": db,
            "intent": "",
            "retrieved_chunks": [],
            "tool_results": [],
            "context": "",
            "answer": "",
            "sources": [],
            "final_prompt": "",
            "streaming": False,
        }

        result = agent_graph.invoke(initial_state)

        return {
            "answer": result["answer"],
            "sources": result.get("sources", []),
        }

    def generate_response_stream(
        self,
        prompt,
        conversation_history,
        user_id,
        db,
    ):
        initial_state = {
            "user_id": user_id,
            "conversation_id": 0,
            "query": prompt,
            "conversation_history": conversation_history,
            "db": db,
            "intent": "",
            "retrieved_chunks": [],
            "tool_results": [],
            "context": "",
            "answer": "",
            "sources": [],
            "final_prompt": "",
            "streaming": True,
        }

        # LangGraph handles:
        # classification → retrieval/tools → prompt preparation
        result = agent_graph.invoke(initial_state)

        final_prompt = result.get("final_prompt")

        if not final_prompt:
            raise RuntimeError(
                "Streaming prompt was not prepared"
            )

        provider = get_llm_provider()

        # Only the final LLM response is streamed token-by-token
        token_stream = provider.generate_stream(
            prompt=final_prompt,
            conversation_history=[],
        )

        return (
            result.get("sources", []),
            token_stream,
        )