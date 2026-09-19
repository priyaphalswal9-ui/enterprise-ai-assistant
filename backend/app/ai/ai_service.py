from sqlalchemy.orm import Session

from backend.app.workflows.rag_agent.graph import agent_graph


class AIService:

    def generate_response(
        self,
        prompt: str,
        conversation_history,
        user_id: int,
        db: Session,
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
        }

        result = agent_graph.invoke(initial_state)

        return {
            "answer": result["answer"],
            "sources": result.get("sources", []),
        }