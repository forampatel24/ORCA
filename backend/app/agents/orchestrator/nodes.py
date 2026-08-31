import json
import os
from langchain_core.messages import HumanMessage
from app.agents.orchestrator.state import OrcaState
from app.agents.orchestrator.schemas import IntentInterpretation, TaskPlan

def get_llm():
    """Provider-aware LLM factory — auto-detects Groq (gsk_) / Gemini (AIza/AQ.) else OpenAI.
    Respects LLM_PROVIDER/LMM_MODEL from .env. No key -> None -> mock fallback."""
    # Load via settings (pydantic loads backend/.env) with os.getenv fallback
    try:
        from app.config.settings import settings as _s
        _key = (_s.llm_api_key or "").strip()
        _provider = (_s.llm_provider or "").strip()
        _model = (_s.llm_model or "").strip()
        _base = (_s.llm_base_url or "").strip()
    except Exception:
        _key = _provider = _model = _base = ""
    key = (os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("GOOGLE_API_KEY") or _key or "").strip()
    if not key:
        return None
    provider = (os.getenv("LLM_PROVIDER") or _provider or "").lower().strip()
    model = (os.getenv("LLM_MODEL") or _model or "").strip()
    base_url_env = (os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_API_BASE") or _base or "").strip() or None
    # auto-detect if provider not explicit — Gemini now also uses AQ. prefix (2025+)
    if not provider:
        if key.startswith("gsk_"):
            provider = "groq"
        elif key.startswith("AIza") or key.startswith("AQ."):
            provider = "gemini"
        else:
            # default to gemini for long non-openai keys when user says Gemini
            provider = "gemini" if len(key) > 30 and not key.startswith("sk-") else "openai"
    # sane model defaults per provider
    if provider == "groq" and ("gpt-" in model or not model):
        model = model if "llama" in model or "mixtral" in model or "gemma" in model else "llama-3.3-70b-versatile"
        if not model:
            model = "llama-3.3-70b-versatile"
    elif provider == "gemini" and ("gpt-" in model or "llama" in model or not model):
        model = "gemini-3-flash-preview" if not model or "gpt" in model or "llama" in model else model
        if not model:
            model = "gemini-3-flash-preview"
    elif provider == "openai" and not model:
        model = "gpt-4o-mini"

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=model, temperature=0, api_key=key)  # type: ignore
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=model, temperature=0, google_api_key=key)  # type: ignore
    else:
        from langchain_openai import ChatOpenAI
        # also supports Groq via OpenAI-compatible base_url if user prefers openai provider + groq key
        base_url = base_url_env
        if key.startswith("gsk_") and not base_url:
            base_url = "https://api.groq.com/openai/v1"
        kwargs = {"model": model, "temperature": 0, "api_key": key}
        if base_url:
            kwargs["base_url"] = base_url  # type: ignore
        return ChatOpenAI(**kwargs)  # type: ignore

async def analyze_intent_node(state: OrcaState) -> OrcaState:
    """Extracts the intent from the user query. Falls back to mock if no LLM key."""
    llm = get_llm()
    query = state["user_query"]
    try:
        with open("C:/temp/orca_intent.log", "a", encoding="utf-8") as _f:
            _f.write(f"QUERY repr={repr(query)} lower={repr(query.lower())} contains सुरक्षित={('सुरक्षित' in query.lower())}\n")
    except: pass
    if llm is None:
        ql = query.lower()
        intent = "general_knowledge"
        # English + Marathi/Hindi keywords for M10 Indian languages
        if any(k in ql for k in ["pfz", "fishing zone", "मत्स्य", "फिशिंग"]):
            intent = "find_pfz"
        elif any(k in ql for k in ["safe", "safety", "सुरक्षित", "सुरक्षा"]):
            intent = "check_safety"
        elif any(k in ql for k in ["weather", "हवामान", "मौसम"]):
            intent = "weather_forecast"
        elif any(k in ql for k in ["route", "रस्ता", "मार्ग"]):
            intent = "route_planning"
        location = None
        # 12-state detection
        loc = None
        for k in ["mumbai","मुंबई","ratnagiri","goa","kochi","kerala","chennai","tamil","visakhapatnam","andhra","odisha","puri","kolkata","andaman","port blair","gujarat","kutch","karnataka","mangalore"]:
            if k in ql:
                loc = k.title() if k not in ["मुंबई"] else "Mumbai"
                if loc in ["Kochi","Kerala"]: loc="Kochi"
                if loc in ["Chennai","Tamil"]: loc="Chennai"
                break
        time_range = "tomorrow" if any(k in ql for k in ["tomorrow", "उद्या"]) else "today"
        return {"intent": intent, "location": loc, "time_range": time_range}
    try:
        structured_llm = llm.with_structured_output(IntentInterpretation)
        prompt = f"Analyze the following user marine query and extract the intent, location, and time range:\nQuery: '{query}'"
        result = await structured_llm.ainvoke(prompt)
        return {"intent": result.intent, "location": result.location, "time_range": result.time_range}
    except Exception:
        ql = query.lower()
        intent = "general_knowledge"
        if any(k in ql for k in ["pfz", "fishing zone"]):
            intent = "find_pfz"
        elif any(k in ql for k in ["safe", "safety", "सुरक्षित"]):
            intent = "check_safety"
        elif any(k in ql for k in ["weather", "हवामान"]):
            intent = "weather_forecast"
        elif any(k in ql for k in ["route", "रस्ता"]):
            intent = "route_planning"
        loc = None
        for k in ["mumbai","मुंबई","ratnagiri","goa","kochi","kerala","chennai","visakhapatnam","odisha","andaman","gujarat","karnataka"]:
            if k in ql:
                loc = k.title()
                break
        time_range = "tomorrow" if "tomorrow" in ql or "उद्या" in ql else "today"
        return {"intent": intent, "location": loc, "time_range": time_range}

async def planner_node(state: OrcaState) -> OrcaState:
    """Creates a task plan based on the intent. Mock fallback if no LLM."""
    llm = get_llm()
    if llm is None:
        intent = state.get("intent", "general_knowledge")
        # M10 multi-turn: if pronoun and history has previous check_safety, inherit
        history = state.get("history", [])
        if intent == "general_knowledge" and history:
            # look for previous assistant intent via content
            for m in reversed(history):
                if m["role"] == "user" and any(k in m["content"].lower() for k in ["safe", "सुरक्षित"]):
                    intent = "check_safety"
                    break
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
    try:
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
    except Exception:
        # fallback to mock logic
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
            tasks = [{"agent_name": "weather_agent", "task_description": "Get weather", "dependencies": []}, {"agent_name": "routing_agent", "task_description": "Optimize route", "dependencies": ["weather_agent"]}]
        else:
            tasks = [{"agent_name": "rag_agent", "task_description": "Retrieve knowledge", "dependencies": []}]
        return {"plan": tasks, "required_agents": list(set(t["agent_name"] for t in tasks))}

async def execute_agents_node(state: OrcaState) -> OrcaState:
    """M5: Execute 8 specialized agents via tools (docs 06_AGENT_SPEC)."""
    results = state.get("agent_results", {}) or {}
    # Data-driven location mapping — loads from data/location_coords.json (not hard-coded in code)
    import json, pathlib
    loc_str = (state.get("location") or "Mumbai").lower().strip()
    coords_path = pathlib.Path(__file__).parents[3] / "data" / "location_coords.json"
    # also try ORCA root
    if not coords_path.exists():
        coords_path = pathlib.Path("D:/Foram_TP/ORCA/data/location_coords.json")
    try:
        coords_raw = json.loads(coords_path.read_text(encoding="utf-8"))
        coords = {k.lower(): tuple(v) for k, v in coords_raw.items()}
    except Exception:
        coords = {"mumbai": (19.0, 72.8)}
    lat, lon = coords.get(loc_str, (19.0, 72.8))
    if (lat, lon) == (19.0, 72.8) and loc_str not in coords:
        for k, v in coords.items():
            if k in loc_str:
                lat, lon = v
                break
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
        intent = state.get("intent", "")
        if "risk" in str(results).lower() or intent == "check_safety":
            risk = results.get("risk_agent", {})
            level = risk.get("risk_level", "UNKNOWN") if isinstance(risk, dict) else "UNKNOWN"
            wind = risk.get("wind_speed", risk.get("inputs", {}).get("wind_speed", "?")) if isinstance(risk, dict) else "?"
            return {"final_response": f"[M5/M6 Synthesis] Safety {level} risk (score {risk.get('risk_score','?')}). Wind {wind} m/s. PFZ {len(results.get('marine_agent',{}).get('pfz',[]))} zones. Evidence: {json.dumps(results, indent=2)[:700]}"}
        return {"final_response": f"[M3/M4 Mock Synthesis] Query '{state['user_query']}' answered with evidence: {json.dumps(results)[:1000]}"}
    results_str = json.dumps(results, indent=2)
    prompt = (
        f"You are ORCA, an Agentic Marine Intelligence Platform.\n"
        f"User Query: {state['user_query']}\n"
        f"Agent Evidence:\n{results_str}\n\n"
        f"Synthesize this evidence into a final response. RULES: plain text only, NO markdown (no **, no ###, no * bullets, no - bullets), use numbered lines 1. 2. 3. if listing. Keep language same as user query (English/Marathi). Be concise and understandable."
    )
    response = await llm.ainvoke(prompt)
    content = response.content
    # Google returns list of dicts, OpenAI/Groq return string — normalize to string
    if isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                texts.append(part["text"])
            elif isinstance(part, str):
                texts.append(part)
            else:
                texts.append(str(part))
        content = "\n".join(texts)
    return {"final_response": str(content)}
