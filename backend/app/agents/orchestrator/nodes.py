import json
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from app.agents.orchestrator.state import OrcaState
from app.agents.orchestrator.schemas import IntentInterpretation, TaskPlan
import os

def get_llm():
    # Will raise error at execution time if not set, instead of import time
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)

async def analyze_intent_node(state: OrcaState) -> OrcaState:
    """Extracts the intent from the user query."""
    llm = get_llm()
    query = state["user_query"]
    structured_llm = llm.with_structured_output(IntentInterpretation)
    
    prompt = f"Analyze the following user marine query and extract the intent, location, and time range:\nQuery: '{query}'"
    result = await structured_llm.ainvoke(prompt)
    
    return {
        "intent": result.intent,
        "location": result.location,
        "time_range": result.time_range,
    }

async def planner_node(state: OrcaState) -> OrcaState:
    """Creates a task plan based on the intent."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(TaskPlan)
    
    prompt = (
        f"You are the ORCA orchestrator. Create a multi-agent execution plan.\n"
        f"Query: '{state['user_query']}'\n"
        f"Intent: {state['intent']}\n"
        f"Location: {state['location']}\n"
        f"Time: {state['time_range']}\n\n"
        f"Available agents: 'weather_agent', 'marine_agent', 'risk_agent', 'rag_agent', 'routing_agent', 'geospatial_agent'.\n"
        f"Assign specific tasks to the necessary agents. Determine if any tasks depend on others."
    )
    
    plan = await structured_llm.ainvoke(prompt)
    
    plan_dicts = [{"agent_name": t.agent_name, "task_description": t.task_description, "dependencies": t.dependencies} for t in plan.tasks]
    required_agents = list(set([t.agent_name for t in plan.tasks]))
    
    return {
        "plan": plan_dicts,
        "required_agents": required_agents
    }

async def execute_agents_node(state: OrcaState) -> OrcaState:
    """Simulates parallel execution of agents for M4."""
    results = state.get("agent_results", {})
    
    # In M5, this will actually invoke the sub-graphs for each agent.
    # For now, we mock the responses based on the plan.
    for task in state["plan"]:
        agent = task["agent_name"]
        results[agent] = f"[MOCK RESULT from {agent}] Executed: {task['task_description']}"
        
    return {"agent_results": results}

async def synthesize_node(state: OrcaState) -> OrcaState:
    """Generates the final response based on agent results."""
    llm = get_llm()
    results_str = json.dumps(state.get("agent_results", {}), indent=2)
    
    prompt = (
        f"You are ORCA, an Agentic Marine Intelligence Platform.\n"
        f"User Query: {state['user_query']}\n"
        f"Agent Evidence:\n{results_str}\n\n"
        f"Synthesize this evidence into a final, helpful, and concise response to the user."
    )
    
    response = await llm.ainvoke(prompt)
    
    return {"final_response": response.content}
