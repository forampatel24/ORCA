# ORCA — Current Status

## Current Milestone

**Milestone 06 — Intelligence Engines (M6) Completed**

Date: 2026-08-30

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
  - `nodes.py:78` `get_llm()` fallback `None` if no `LLM_API_KEY` -> mock intent/planner/synthesize, real `ChatOpenAI gpt-4o-mini`
  - `execute_agents_node` initial real DB queries + deterministic risk (M4), wired `POST /api/v1/chat` `astream_events`

- **M5: 8 Specialized Agents + Tools (06_AGENT_SPEC)**
  - Tools `app/tools/pfz.py:1` `get_nearest_pfz` `ST_DWithin` `ST_Distance`, `weather.py:1` `get_weather`/`get_hazards`, `geospatial.py:1` `check_geofence` `ST_Contains` `calculate_distance` `ST_Distance`, `ocean.py:1` `get_ocean`, `risk.py:1` `calculate_risk` `LOW/MODERATE/HIGH` deterministic, `rag.py:1` `search_knowledge` Qdrant mock
  - Agents `app/agents/marine/agent.py:1` `MarineAgent` `pfz+ocean`, `weather/agent.py:1` `WeatherAgent` `weather+hazards`, `ocean/agent.py:1`, `geospatial/agent.py:1` `PostGIS`, `risk/agent.py:1` `weather+ocean+geofence -> risk_score`, `routing/agent.py:1` `calculate_distance`, `rag/agent.py:1` `evidence`
  - Refactored `agents/orchestrator/nodes.py:78` `execute_agents_node` to use `agent_map` `marine/weather/ocean/geospatial/risk/routing/rag` with dependency-aware sequential exec, location `Mumbai 19.0,72.8`/`Ratnagiri 16.9,73.3` mapping

- **M6: Intelligence Engines (15_ML_ANALYTICS)**
  - `app/analytics/risk/engine.py:1` 4 levels `LOW/MODERATE/HIGH/VERY_HIGH` `wind 10/15/20` `wave 1.5/2.5/3.5` + `lightning/cyclone/geofence` `score 0-165` `safety_override`
  - `app/analytics/pfz/scoring.py:1` weighted `ocean 0.3 + env 0.2 + safety 0.35 + access 0.15` `sst 27-29 + chl 0.5-1.5` `pfz_score 0.776`
  - `app/analytics/ocean/anomaly.py:1` `sst_anomaly` `baseline 27.0` `+1.5` `chlorophyll_anomaly` `flag ANOMALOUS`, `app/analytics/routing/engine.py:1` `haversine` `score_route` `cost =0.3*dist+0.2*time+0.5*risk` `geofence penalty 100` `A* placeholder`
  - Updated `agents/risk/agent.py:1` to use `analytics/risk`, `agents/routing/agent.py:1` `find_safe_route`, `agents/marine/agent.py:1` `scored_pfz` `anomalies`, `nodes.py:78` synthesis now `[M5/M6 Synthesis]` with `risk_score` + `pfz count`

## Working

- `docker compose up -d` `orca-*` 30h healthy on `D:` `9100/6333/6379` + `D:\PostreSQL 5432 PostGIS 3.6.2` + `uvicorn :8000` `GET / 200` `POST /api/v1/chat 1114 chars` `M5/M6 Synthesis MODERATE` `pfz_observations 6 rows`
- `M6 engines` `risk LOW 0, MOD 25, HIGH 95 VERY_HIGH 165`, `pfz_score 0.776 ocean 1.0`, `sst_anomaly +1.5`, `haversine 33.43km`, `route cost 0.359` + `orchestrator check_safety -> 4 agents risk 45 MODERATE safety_override OK scored_pfz 0.776`
- `POST /chat` via `uvicorn 8000` 200, `GET /pfz/nearest 4 items 15.2km`, `geospatial inside Test MPA distance 0.0`, `risk HIGH 70` `VERY_HIGH` cyclone

## In Progress

- M7 Static GIS Datasets (next)

## Pending

- M7 Static GIS datasets (EEZ subset)
- M8 RAG ingestion
- M9 Frontend Map+Chat
- M10 Conversational
- M11 Security
- M12 Testing + Observability

## Known Issues

- MinIO `9000` -> `9100` fixed (`docker-compose.yml:22`)
- `bcrypt` crash fixed `bcrypt==4.0.1`
- Chat unauthenticated demo (will re-enable after M9 login)
- `LLM_API_KEY` not set -> mock `[M5/M6 Synthesis]` (real `gpt-4o-mini` when set)

## Fixed in M6 Patch
- `weather_observations` now 2 rows `wind 12.5/18.0` `temp 29.0` `source weather_observations` `tools/weather.py:1` verified `get_weather 12.5`
- `Qdrant orca_knowledge` now 2 points `INCOIS Advisory + Safety Guideline` `BGE-small-en-v1.5` `384` `search_knowledge` real `query_points` `check_compatibility=False` `score 0.84`, `rag_agent` returns `INCOIS 18-22 m/s` evidence

## Next Milestone

**M7: Static GIS Datasets** - `Marine Regions EEZ` + `WDPA` + `GEBCO 2026 subset` + `CMFRI` + `PostGIS GIST` per `08_DATASET_REGISTRY`

## Architecture Status

- Follows `03_ARCHITECTURE` 10 layers, `05_DATABASE_DESIGN` polyglot `PostgreSQL/PostGIS + Redis + MinIO + Qdrant` per `20_DATABSE_ARCHITECTURE`
- `Docker Desktop` data on `D:\Docker\DockerDesktopWSL`, project on `D:\Foram_TP\ORCA` - `C:` only has binary
- Native `PostGIS` retained per `19_DEV_ENVIRONMENT`, container `postgres` commented out in compose
