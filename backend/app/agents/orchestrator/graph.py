from langgraph.graph import StateGraph, START, END
from app.agents.orchestrator.state import OrcaState
from app.agents.orchestrator.nodes import (
    analyze_intent_node,
    planner_node,
    execute_agents_node,
    synthesize_node
)

def build_orchestrator_graph():
    """Builds and compiles the ORCA Orchestrator StateGraph."""
    workflow = StateGraph(OrcaState)
    
    # Add Nodes
    workflow.add_node("analyze_intent", analyze_intent_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("execute_agents", execute_agents_node)
    workflow.add_node("synthesize", synthesize_node)
    
    # Define Edges
    workflow.add_edge(START, "analyze_intent")
    workflow.add_edge("analyze_intent", "planner")
    workflow.add_edge("planner", "execute_agents")
    workflow.add_edge("execute_agents", "synthesize")
    workflow.add_edge("synthesize", END)
    
    # Compile
    app = workflow.compile()
    return app

# Singleton compiled graph
orchestrator_app = build_orchestrator_graph()
