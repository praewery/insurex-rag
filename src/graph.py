from langgraph.graph import StateGraph, START, END
from src.models import AgentState
from src.nodes import (
    classify_intent,
    retrieve_docs,
    generate_answer,
    handle_not_found,
    collect_lead,
    check_relevance,
    rewrite_query,
)


def route_intent(state: AgentState) -> str:
    return state.intent


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_docs", retrieve_docs)
    graph.add_node("generate_answer", generate_answer)
    graph.add_node("handle_not_found", handle_not_found)
    graph.add_node("collect_lead", collect_lead)

    graph.add_edge(START, "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "rag": "retrieve_docs",
            "lead_collection": "collect_lead",
        }
    )

    graph.add_node("rewrite_query", rewrite_query) 
    graph.add_conditional_edges(
        "retrieve_docs",
        check_relevance,
        {
            "generate":  "generate_answer",
            "not_found": "handle_not_found",
            "rewrite":   "rewrite_query",   
        }
    )

    graph.add_edge("generate_answer", END)
    graph.add_edge("rewrite_query", "retrieve_docs")
    graph.add_edge("handle_not_found", END)
    graph.add_edge("collect_lead", END)

    return graph.compile()
