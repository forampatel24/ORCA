import json
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from app.agents.orchestrator.state import OrcaState
from app.agents.orchestrator.schemas import IntentInterpretation, TaskPlan
import os

def get_llm():
    import os
    key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    if not key:
        return None
    return ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=key)

async def analyze_intent_node(state: OrcaState) -> OrcaState:
    """Extracts the intent from the user query. Falls back to mock if no LLM key."""
    llm = get_llm()
    query = state["user_query"]
    if llm is None:
        # Mock fallback for M3/M4 testing without API key
        ql = query.lower()
        intent = "general_knowledge"
        if "pfz" in ql or "fishing zone" in ql:
            intent = "find_pfz"
        elif "safe" in ql or "safety" in ql:
            intent = "check_safety"
        elif "weather" in ql:
            intent = "weather_forecast"
        elif "route" in ql:
            intent = "route_planning"
        location = "Mumbai" if "mumbai" in ql else None
        time_range = "tomorrow" if "tomorrow" in ql else "today"
        return {"intent": intent, "location": location, "time_range": time_range}
    structured_llm = llm.with_structured_output(IntentInterpretation)
    prompt = f"Analyze the following user marine query and extract the intent, location, and time range:\nQuery: '{query}'"
    result = await structured_llm.ainvoke(prompt)
    return {"intent": result.intent, "location": result.location, "time_range": result.time_range}

async def planner_node(state: OrcaState) -> OrcaState:
    """Creates a task plan based on the intent. Mock fallback if no LLM."""
    llm = get_llm()
    if llm is None:
        intent = state.get("intent", "general_knowledge")
        if intent == "find_pfz":
            tasks = [{"agent_name": "marine_agent", "task_description": "Find nearest PFZ", "dependencies": []}]
        elif intent == "check_safety":
            tasks = [
                {"agent_name": "weather_agent", "task_description": "Get weather + wind", "dependencies": []},
                {"agent_name": "marine_agent", "task_description": "Get wave/ocean", "dependencies": []},
                {"agent_name": "geospatial_agent", "task_description": "Check geofences", "dependencies": []},
                {"agent_name": "risk_agent", "task_description": "Assess risk", "dependencies": ["weather_agent","marine_agent","geospatial_agent"]},
            ]
        elif intent == "weather_forecast":
            tasks = [{"agent_name": "weather_agent", "task_description": "Get weather forecast", "dependencies": []}]
        elif intent == "route_planning":
            tasks = [
                {"agent_name": "weather_agent", "task_description": "Get weather", "dependencies": []},
                {"agent_name": "routing_agent", "task_description": "Optimize route", "dependencies": ["weather_agent"]},
            ]
        else:
            tasks = [{"agent_name": "rag_agent", "task_description": "Retrieve knowledge", "dependencies": []}]
        return {"plan": tasks, "required_agents": list(set(t["agent_name"] for t in tasks))}
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
    return {"plan": plan_dicts, "required_agents": required_agents}

async def execute_agents_node(state: OrcaState) -> OrcaState:
    """M5: Execute 8 specialized agents via tools (docs 06_AGENT_SPEC)."""
    results = state.get("agent_results", {}) or {}
    # Default location from state or Mumbai
    loc_str = state.get("location") or "Mumbai"
    lat, lon = 19.0, 72.8
    if loc_str and "ratnagiri" in loc_str.lower():
        lat, lon = 16.9, 73.3
    # Import agents lazily to avoid circular
    from app.agents.marine.agent import marine_agent
    from app.agents.weather.agent import weather_agent
    from app.agents.ocean.agent import ocean_agent
    from app.agents.geospatial.agent import geospatial_agent
    from app.agents.risk.agent import risk_agent
    from app.agents.routing.agent import routing_agent
    from app.agents.rag.agent import rag_agent
    agent_map = {
        "marine_agent": marine_agent,
        "weather_agent": weather_agent,
        "ocean_agent": ocean_agent,
        "geospatial_agent": geospatial_agent,
        "risk_agent": risk_agent,
        "routing_agent": routing_agent,
        "rag_agent": rag_agent,
        "geofence_agent": geospatial_agent,
        "fishing_agent": marine_agent,
    }
    # Execute in plan order - respects dependencies (planner already orders)
    for task in state.get("plan", []):
        agent_name = task["agent_name"]
        agent = agent_map.get(agent_name)
        if not agent:
            results[agent_name] = f"[UNKNOWN AGENT {agent_name}] {task['task_description']}"
            continue
        try:
            if agent_name == "marine_agent":
                results[agent_name] = await agent.run(lat=lat, lon=lon)
            elif agent_name == "weather_agent":
                results[agent_name] = await agent.run(lat=lat, lon=lon)
            elif agent_name == "ocean_agent":
                results[agent_name] = await agent.run(lat=lat, lon=lon)
            elif agent_name == "geospatial_agent":
                results[agent_name] = await agent.run(lat=lat, lon=lon)
            elif agent_name == "risk_agent":
                # risk needs prior results
                results[agent_name] = await agent.run(
                    weather=results.get("weather_agent"),
                    ocean=results.get("ocean_agent") or results.get("marine_agent"),
                    geofence=results.get("geospatial_agent")
                )
            elif agent_name == "routing_agent":
                results[agent_name] = await agent.run(origin={"lat": lat, "lon": lon}, destination={"lat": 19.1, "lon": 72.5})
            elif agent_name == "rag_agent":
                results[agent_name] = await agent.run(query=state.get("user_query", ""))
            else:
                results[agent_name] = await agent.run()
        except Exception as e:
            results[agent_name] = {"error": str(e), "task": task["task_description"]}
    return {"agent_results": results}

async def synthesize_node(state: OrcaState) -> OrcaState:
    """Generates final response. Mock fallback if no LLM."""
    llm = get_llm()
    results = state.get("agent_results", {})
    if llm is None:
        # Deterministic synthesis without LLM
        intent = state.get("intent", "")
        if "risk" in str(results).lower() or intent == "check_safety":
            risk = results.get("risk_agent", {})
            level = risk.get("risk_level", "UNKNOWN") if isinstance(risk, dict) else "UNKNOWN"
            return {"final_response": f"[M3/M4 Mock Synthesis] Safety assessment: {level} risk. Wind {risk.get('wind_speed','?')} m/s. Evidence: {json.dumps(results, indent=2)[:800]}"}
        return {"final_response": f"[M3/M4 Mock Synthesis] Query '{state['user_query']}' answered with evidence: {json.dumps(results)[:1000]}"}
    results_str = json.dumps(results, indent=2)
    prompt = (
        f"You are ORCA, an Agentic Marine Intelligence Platform.\n"
        f"User Query: {state['user_query']}\n"
        f"Agent Evidence:\n{results_str}\n\n"
        f"Synthesize this evidence into a final, helpful, and concise response to the user."
    )
    response = await llm.ainvoke(prompt)
    return {"final_response": response.content}
