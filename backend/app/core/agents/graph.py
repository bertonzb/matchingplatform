from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from app.core.agents.state import AgentState
from app.core.agents.nodes import (
    data_collection_node,
    profile_building_node,
    matching_analysis_node,
    quality_check_node,
    should_retry,
)

def build_matching_graph(db: Session) -> StateGraph:
    graph = StateGraph(AgentState)

    # Wrap nodes to inject db session
    async def dc(state: AgentState):
        return await data_collection_node(state, db)
    async def pb(state: AgentState):
        return await profile_building_node(state, db)
    async def ma(state: AgentState):
        return await matching_analysis_node(state, db)
    async def qc(state: AgentState):
        return await quality_check_node(state, db)

    graph.add_node("data_collection", dc)
    graph.add_node("profile_building", pb)
    graph.add_node("matching_analysis", ma)
    graph.add_node("quality_check", qc)

    graph.set_entry_point("data_collection")
    graph.add_edge("data_collection", "profile_building")
    graph.add_edge("profile_building", "matching_analysis")
    graph.add_edge("matching_analysis", "quality_check")

    graph.add_conditional_edges(
        "quality_check",
        should_retry,
        {
            "retry": "matching_analysis",
            "done": END,
        },
    )

    return graph.compile()


async def run_matching_pipeline(user_requirement: str, top_n: int, db: Session) -> list[dict]:
    graph = build_matching_graph(db)
    initial_state: AgentState = {
        "user_requirement": user_requirement,
        "top_n": top_n,
        "retry_count": 0,
    }
    final_state = await graph.ainvoke(initial_state)
    return final_state.get("final_results", [])
