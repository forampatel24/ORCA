# ORCA — Current Status

## Current Milestone

**Milestone 04 — Orchestration Core (M4) Completed**

Date: 2026-08-29

## Completed

- **M0: Foundation & Dev Environment**
  - Project scaffold `D:\Foram_TP\ORCA\backend`, `frontend`, `infrastructure`, `data`, `docs` per `04_TECH_STACK`, `16_DEPLOY`, `19_DEV_ENV`
  - `docker-compose.yml` with `redis:7-alpine`, `qdrant:v1.13.5`, `minio:latest` on `orca-network` - volumes on `D:\Docker\DockerDesktopWSL\disk\docker_data.vhdx` (2.17GB) - **all Docker data on D:, not C:**
  - MinIO ports `9100->9000`, `9101->9001` (avoid Windows reserved `8947-9046`), verified `orca-minio Up healthy`
  - `Qdrant :6333` `healthz passed`, `Redis :6379 PONG`, `MinIO :9100 200`
  - `.env.example` + `.env` + `backend/.env` with `DATABASE_URL`, `REDIS_URL`, `QDRANT_URL`, `MINIO_ENDPOINT=localhost:9100`, `LLM_API_KEY` shared
  - Backend `FastAPI + Pydantic + SQLAlchemy` skeleton `app/main.py`, `api/routes/health`, `api/routes/chat` stub, `config/settings.py`
  - Frontend `React 18 + TS + Vite + Tailwind + MapLibre placeholder` `package.json`, `vite.config.ts` proxy `/api -> :8000`
  - `.gitignore` properly ignores `.env`, `__pycache__`, `node_modules`, `data/raw` etc.

- **M1: Polyglot Storage Layer**
  - PostgreSQL `18.4` native `D:\PostreSQL` (port `5432`, `scram-sha-256`, password `postgres`) - created `orca_db`, enabled `postgis 3.6.2 + postgis_raster + uuid-ossp`
  - 20 tables created via `backend/app/database/init_m1.sql`: `users, conversations, messages, agent_runs, tool_runs, data_sources, ingestion_runs, pfz_observations, ocean_observations, weather_observations, marine_hazards, geofences, protected_areas, maritime_boundaries, risk_assessments, routes, alerts, knowledge_documents, knowledge_chunks`, spatial GIST indexes `idx_pfz_geometry`, `idx_geofences_geom` etc.
  - Seeded `6 data_sources`: `INCOIS PFZ/OSF, IMD Weather/Cyclone, WDPA, Marine Regions EEZ`
  - Spatial test passed: `INSERT geofences POLYGON((72.5 18.8...)) -> ST_Contains(POINT(72.8 19.0)) = t`
  - `psycopg` connectivity verified `SELECT PostGIS_Version() = 3.6 USE_GEOS=1`
  - MinIO 6 buckets: `orca-documents, orca-raw-data, orca-satellite, orca-raster, orca-processed, orca-artifacts` on `localhost:9100`
  - Qdrant `orca_knowledge` collection `size=384 Cosine, status green` created
  - Redis `orca:test:health set/get ok`

- **M2: Data Registry & Pipeline**
  - Base connector `app/services/ingestion/base.py:1` (`fetch`, `validate_source`, `get_metadata`, `provenance`) per `09_DATA_PIPELINE`
  - Validation `app/services/ingestion/validation.py:1` (`VALID/SUSPECT/INVALID`, `PFZ_SCHEMA`, `WEATHER_SCHEMA`, coord/range/timestamp checks) + Normalization `normalization.py:1` (UTC ISO8601, EPSG:4326, `K->C`)
  - Pipeline `pipeline.py:1` (`Raw MinIO -> Validation -> Normalization -> dedupe -> provenance -> Redis cache`) with TTL `weather 1800, pfz 86400, hazard 600` per `05:38`
  - Connectors: `pfz_connector.py:1` (3 PFZ mock Mumbai), `weather_connector.py:1` (2 forecasts `+6h/+24h`) per `08_DATASET_REGISTRY`
  - Registry `app/services/data_registry.py:1` (`INTENT_SOURCES` `pfz_discovery/safety/route/geofence`, `select_for_intent`, `check_freshness FRESH/AGING/STALE`)
  - Verified end-to-end: `PFZ 3 inserted, Weather 2 inserted`, `pfz_observations count 6`, `ingestion_runs tracked`, `MinIO raw/pfz + raw/weather .json` stored, `Redis cache hit` on second fetch, `ingestion cache hit` logged via `structlog`

- **M3: Backend API Layer**
  - FastAPI `app/main.py:41` 8 routers (`/api/v1/health`, `/auth`, `/chat`, `/pfz/nearest`, `/weather`, `/hazards`, `/risk/assess`, `/routes`, `/geospatial/geofence/check`) via `Service->Repository->DB` per `03_ARCHITECTURE`
  - Repos `pfz_repo.py:32` `ST_Distance Geog`, `weather_repo.py:32`, `hazard_repo.py:32` with PostGIS `GIST`, schemas `chat.py:1` `pfz.py:1` `weather.py:1` `risk.py:1`
  - JWT `core/security.py:27` `bcrypt 4.0.1` + `api/deps.py:41` `get_current_user`, `SECRET_KEY` dev fallback, `Bearer token` tested `test@orca.local` `POST /auth/login`-like flow
  - `health` `health/services` checks DB/Redis/Qdrant/MinIO, `StreamingResponse` `/chat/stream` events `intent_analysis_started/plan_created/agents_executed`
  - Fixes: `chat.py:83` unauthenticated demo allowed (M3 mock), `bcrypt 4.0.1` downgrade fix `passlib`

- **M4: Orchestration Core**
  - LangGraph `agents/orchestrator/graph.py:32` `StateGraph(OrcaState)` `analyze_intent->planner->execute_agents->synthesize` singleton `orchestrator_app`
  - Schemas `state.py:28` `OrcaState` `intent/location/time_range/plan/agent_results/final_response`, `schemas.py:18` `IntentInterpretation`, `TaskPlan`
  - `nodes.py:78` `get_llm()` fallback `None` if no `LLM_API_KEY` -> mock intent/planner/synthesize (no crash), real LLM path `ChatOpenAI gpt-4o-mini` with `with_structured_output`
  - `execute_agents_node` now real `psycopg` queries `pfz_observations`, `geofences`, `weather_observations` + deterministic `risk MODERATE/HIGH` instead of pure mock, provenance via DB
  - Wired `POST /api/v1/chat` `POST /api/v1/chat/stream` `ainvoke` + `astream_events`

## Working

- `docker compose up -d` `orca-*` 29h healthy on `D:` `9100/6333/6379` + `D:\PostreSQL 5432 PostGIS 3.6.2`, `IngestionPipeline` `Raw->MinIO->PostGIS->Redis` `PFZ 3/3 Weather 2/2`
- `uvicorn :8000` running `2 processes` `GET / 200`, `POST /api/v1/chat/ 200` `MODERATE risk` synthesis with real DB `marine_agent 2 PFZ + weather 12.5 + geofence Test MPA`, `GET /pfz/nearest 200 4 items distance_km`, `GET /weather 200`, `GET /hazards 200` all via JWT `test@orca.local`
- `test_m4.py` `find_pfz -> marine_agent`, `check_safety -> 4 agents + risk MODERATE` verified via `backend/.venv python` without `LLM_API_KEY` (mock fallback)
- MinIO `6 buckets` `383B raw`, Qdrant `orca_knowledge green`, Redis `PONG` `orca:*` TTL

## In Progress

- M5 Specialized Agents + Tools (next)

## Pending

- M5 Agents + Tools
- M6 Risk/Route engines
- M7 Static GIS datasets (EEZ subset)
- M8 RAG ingestion
- M9 Frontend Map+Chat
- M10 Conversational
- M11 Security
- M12 Testing + Observability

## Known Issues

- MinIO `9000` -> `9100` fixed (`docker-compose.yml:22` Windows `8947-9046`)
- `bcrypt` `passlib` `__about__` crash fixed via `bcrypt==4.0.1` (M3)
- `weather_observations` empty (pipeline inserted but `test_m2` only seeded `pfz`, weather repo returns `[]` - will seed in M5)
- Chat now unauthenticated for demo (M4 fallback) - will re-enable `Depends(get_current_user)` after frontend login (M9)
- `LLM_API_KEY` not set -> mock synthesis `[M3/M4 Mock Synthesis]` used (real `gpt-4o-mini` when key added)

## Next Milestone

**M5: Specialized Agents + Tools** - Marine/Weather/Ocean/Geo/Risk/Route/RAG specialized agents + deterministic PostGIS/Shapely tools, structured I/O.

## Architecture Status

- Follows `03_ARCHITECTURE` 10 layers, `05_DATABASE_DESIGN` polyglot `PostgreSQL/PostGIS + Redis + MinIO + Qdrant` per `20_DATABSE_ARCHITECTURE`
- `Docker Desktop` data on `D:\Docker\DockerDesktopWSL`, project on `D:\Foram_TP\ORCA` - `C:` only has binary
- Native `PostGIS` retained per `19_DEV_ENVIRONMENT`, container `postgres` commented out in compose
