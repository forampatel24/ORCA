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
    # Portable debug log — no C:/ hardcode; uses project logs/ if writable else silent
    try:
        import pathlib as _pl
        _log_path = _pl.Path(__file__).resolve().parents[3] / "logs" / "orca_intent.log"
        _log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(_log_path, "a", encoding="utf-8") as _f:
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
        # Mumbai-only: default to Mumbai when no explicit location, else Mumbai bbox
        loc = "Mumbai"
        for k in ["mumbai","मुंबई","maharashtra","महाराष्ट्र"]:
            if k in ql:
                loc = "Mumbai"
                break
        # Keep compat but log non-Mumbai as Mumbai-only enforced
        if any(x in ql for x in ["ratnagiri","goa","kochi","kerala","chennai","tamil","visakhapatnam","andhra","odisha","puri","kolkata","andaman","port blair","gujarat","kutch","karnataka","mangalore"]):
            loc = "Mumbai"  # enforce Mumbai-only per requirement
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
        loc = "Mumbai"  # Mumbai-only enforced
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
    # Data-driven location mapping — loads from data/location_coords.json portable
    import json, pathlib
    loc_str = (state.get("location") or "Mumbai").lower().strip()
    # Portable: repo root is parents[3] from backend/app/agents/orchestrator/
    coords_path = pathlib.Path(__file__).resolve().parents[3] / "data" / "location_coords.json"
    # Env override for custom location file
    import os
    _env_coords = os.getenv("ORCA_LOCATION_COORDS")
    if _env_coords:
        _env_p = pathlib.Path(_env_coords)
        if _env_p.exists():
            coords_path = _env_p
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
    """Generates final response. No mock synthesis - honest structured evidence when LLM unavailable."""
    llm = get_llm()
    results = state.get("agent_results", {})
    # --- Live route injection for Marathi + English: ensure LLM never estimates distance ---
    try:
        ql = (state.get("user_query") or "").lower()
        is_route = any(k in ql for k in ["route", "मार्ग", "रूट", "रस्ता", "पासून", "पर्यंत"])
        # also "from X to Y" pattern
        if not is_route and " from " in ql and " to " in ql:
            is_route = True
        if is_route and "route_live" not in results:
            # Try to resolve two PFZ names (English or Devanagari) from the query
            DEV_TO_EN = {"एडावण": "Edavan/Kore", "कोरे": "Edavan/Kore", "पटवाडी": "Patwadi", "अरनाळा": "Arnala", "आर्णाला": "Arnala", "टेंभी": "Tembhi", "मलबार": "Malabar Port (Mumbai)", "वरळी": "Worli", "ससून": "SasoonDock", "कालबादेवी": "Kalbadevi", "चिंचबंदर": "Chinchbunder", "ससवणे": "Sasawane", "कोलाबा": "Colaba Pt.(Mumbai)", "नवगाव": "Navgaon", "थाळ": "Thal", "वरसोली": "VarsoliChalmala", "अलिबाग": "Alibag", "नागाव": "Nagaon", "रेवदंडा": "Revadanda", "कोर्लई": "Korlai"}
            # collect Devanagari hits
            dev_hits = [en for dev, en in DEV_TO_EN.items() if dev in state.get("user_query", "")]
            # also English PFZ hits via DB names
            try:
                import psycopg as _psycopg
                from app.database.connection import psycopg_conninfo
                conn = _psycopg.connect(psycopg_conninfo())
                cur = conn.cursor()
                cur.execute("SELECT metadata->>'landing_centre' FROM pfz_observations")
                all_names = [r[0] for r in cur.fetchall() if r[0]]
                conn.close()
                # token match for English
                for n in all_names:
                    toks = [t for t in n.lower().split("/") if len(t) >= 3] + [n.lower()]
                    if any(t in ql for t in toks) and n not in dev_hits:
                        dev_hits.append(n)
            except Exception:
                pass
            if len(dev_hits) >= 2:
                # compute live route for LLM evidence
                try:
                    from app.api.routes.routes import _resolve_pfz, _safe_polyline
                    from app.analytics.routing.engine import haversine
                    a = _resolve_pfz(dev_hits[0]); b = _resolve_pfz(dev_hits[1])
                    if a and b:
                        coords = _safe_polyline(a[0], a[1], b[0], b[1])
                        dist = sum(haversine(coords[i][1], coords[i][0], coords[i+1][1], coords[i+1][0]) for i in range(len(coords)-1))
                        results["route_live"] = {"start": dev_hits[0], "end": dev_hits[1], "start_lat": a[0], "start_lon": a[1], "end_lat": b[0], "end_lon": b[1], "distance_km": round(dist, 2), "coordinates": coords, "safety": "hazards/MPA/EEZ checked via _safe_polyline, no estimate"}
                except Exception as e:
                    results["route_live_error"] = str(e)[:200]
            elif len(dev_hits) == 1:
                # single PFZ route from vessel/Mumbai default - still provide distance
                try:
                    from app.api.routes.routes import _resolve_pfz, _safe_polyline
                    from app.analytics.routing.engine import haversine
                    b = _resolve_pfz(dev_hits[0])
                    if b:
                        a_lat, a_lon = 19.076, 72.877
                        # try vessel position from state if available
                        try:
                            vp = state.get("user_location") or state.get("vessel_pos")
                            if vp and len(vp) == 2:
                                a_lat, a_lon = float(vp[0]), float(vp[1])
                        except Exception:
                            pass
                        coords = _safe_polyline(a_lat, a_lon, b[0], b[1])
                        dist = sum(haversine(coords[i][1], coords[i][0], coords[i+1][1], coords[i+1][0]) for i in range(len(coords)-1))
                        results["route_live"] = {"start": f"{a_lat},{a_lon}", "end": dev_hits[0], "distance_km": round(dist, 2), "coordinates": coords}
                except Exception:
                    pass
    except Exception:
        pass
    if llm is None:
        # No LLM key configured - do not fabricate natural language. Return deterministic
        # evidence summary with explicit provenance so the UI can show honest state.
        return {"final_response": (
            "ORCA evidence summary (LLM not configured - live data only, no mock synthesis):\n"
            f"Query: {state['user_query']}\n"
            f"Agents executed: {', '.join(results.keys()) if results else 'none'}\n"
            f"Evidence:\n{json.dumps(results, indent=2)[:1800]}\n"
            "Set LLM_API_KEY in backend/.env to enable natural-language synthesis."
        )}
    results_str = json.dumps(results, indent=2)
    prompt = (
        f"You are ORCA, an Agentic Marine Intelligence Platform.\n"
        f"User Query: {state['user_query']}\n"
        f"Agent Evidence:\n{results_str}\n\n"
        f"Synthesize this evidence into a final response. RULES: plain text only, NO markdown (no **, no ###, no * bullets, no - bullets), use numbered lines 1. 2. 3. if listing. Keep language same as user query (English/Marathi). Be concise and understandable. If route_live is present, use its distance_km and coordinates exactly — do not estimate distances. If wind/wave/sst values are present, use them verbatim."
    )
    try:
        response = await llm.ainvoke(prompt)
    except Exception as e:
        # Graceful fallback for quota/rate-limit (e.g. Gemini free 20/day) — never 500
        msg = str(e)
        is_rate = "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower() or "rate" in msg.lower()
        if is_rate:
            log.warning("llm_rate_limited_fallback_to_evidence", error=msg[:200])
            evidence_lines = []
            if "route_live" in results:
                rl = results["route_live"]
                evidence_lines.append(f"Route {rl.get('start')} → {rl.get('end')} — {rl.get('distance_km')} km (live, safety-checked).")
            # include key live values for user
            try:
                import psycopg as _psycopg
                from app.database.connection import psycopg_conninfo
                conn = _psycopg.connect(psycopg_conninfo())
                cur = conn.cursor()
                cur.execute("SELECT wind_speed FROM weather_observations ORDER BY observation_time DESC LIMIT 1")
                w = cur.fetchone()
                cur.execute("SELECT wave_height FROM ocean_observations ORDER BY observation_time DESC LIMIT 1")
                o = cur.fetchone()
                conn.close()
                if w and w[0] is not None:
                    evidence_lines.append(f"Wind {float(w[0]):.1f} m/s, Wave {float(o[0]):.1f} m" if o and o[0] is not None else f"Wind {float(w[0]):.1f} m/s")
            except Exception:
                pass
            fallback = (
                "ORCA — live evidence (LLM quota exceeded, showing deterministic summary — no estimate):\n"
                + "\n".join(f"{i+1}. {l}" for i, l in enumerate(evidence_lines[:8])) + "\n"
                + f"Full evidence: {results_str[:1400]}\n"
                + "Note: Gemini free tier 20/day reached — retry in ~60s or set GROQ_API_KEY for higher limits. Map route is still live."
            )
            return {"final_response": fallback}
        raise
    content = response.content
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
