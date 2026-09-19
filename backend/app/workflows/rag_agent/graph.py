from langgraph.graph import END, START, StateGraph

from backend.app.workflows.rag_agent.nodes import (
    classify_request,
    general_node,
    generate_rag_answer,
    rag_node,
    tool_node,
)
from backend.app.workflows.rag_agent.state import AgentState


def route_request(state: AgentState) -> str:
    return state["intent"]


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_request", classify_request)
    graph.add_node("general", general_node)
    graph.add_node("rag", rag_node)
    graph.add_node("generate_rag_answer", generate_rag_answer)
    graph.add_node("tool", tool_node)

    graph.add_edge(START, "classify_request")

    graph.add_conditional_edges(
        "classify_request",
        route_request,
        {
            "general": "general",
            "rag": "rag",
            "tool": "tool",
        },
    )

    graph.add_edge("general", END)

    graph.add_edge("rag", "generate_rag_answer")
    graph.add_edge("generate_rag_answer", END)

    graph.add_edge("tool", END)

    return graph.compile()


agent_graph = build_graph()