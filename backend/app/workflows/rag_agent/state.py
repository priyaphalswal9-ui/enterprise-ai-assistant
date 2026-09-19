from typing import TypedDict

from sqlalchemy.orm import Session


class AgentState(TypedDict):
    user_id: int
    conversation_id: int
    query: str
    conversation_history: list
    db: Session

    intent: str

    retrieved_chunks: list[dict]
    tool_results: list[dict]

    context: str
    answer: str
    sources: list[dict]