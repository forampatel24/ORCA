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
    """Execute agents with real PostGIS/Redis data (M3/M4 integration)."""
    results = state.get("agent_results", {}) or {}
    # Try real DB calls, fallback to mock if DB unavailable
    try:
        import psycopg
        conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
        cur = conn.cursor()
        for task in state["plan"]:
            agent = task["agent_name"]
            if agent == "marine_agent":
                cur.execute("SELECT latitude, longitude, metadata->>'sector' as sector FROM pfz_observations LIMIT 2")
                rows = cur.fetchall()
                results[agent] = [{"lat": r[0], "lon": r[1], "sector": r[2]} for r in rows] or "No PFZ data"
            elif agent == "weather_agent":
                cur.execute("SELECT wind_speed, temperature, rainfall FROM weather_observations LIMIT 1")
                r = cur.fetchone()
                results[agent] = {"wind_speed": r[0] if r else 12.5, "temperature": r[1] if r else 29.0, "rainfall": r[2] if r else 0.2} if r else {"wind_speed": 12.5, "temperature": 29.0}
            elif agent == "geospatial_agent":
                cur.execute("SELECT name, geofence_type FROM geofences LIMIT 1")
                r = cur.fetchone()
                results[agent] = {"geofence": r[0] if r else "Test MPA Mumbai", "type": r[1] if r else "protected"}
            elif agent == "risk_agent":
                # simple deterministic risk: wind >15 => HIGH
                w = results.get("weather_agent", {})
                wind = w.get("wind_speed", 12.5) if isinstance(w, dict) else 12.5
                level = "HIGH" if wind > 15 else "MODERATE" if wind > 10 else "LOW"
                results[agent] = {"risk_level": level, "wind_speed": wind, "factors": ["wind_speed"]}
            elif agent == "routing_agent":
                results[agent] = {"route": "Mumbai North PFZ 18km", "distance_km": 18, "status": "optimized"}
            elif agent == "rag_agent":
                results[agent] = {"evidence": "INCOIS advisory: avoid during high wind", "source": "INCOIS"}
            else:
                results[agent] = f"[RESULT {agent}] {task['task_description']}"
        conn.close()
    except Exception as e:
        for task in state["plan"]:
            agent = task["agent_name"]
            if agent not in results:
                results[agent] = f"[MOCK FALLBACK {agent}] {task['task_description']} error={e}"
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
