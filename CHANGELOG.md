# ORCA Changelog

## Milestone 00 — Foundation & Dev Environment

Date: 2026-08-29

### Added
- Project scaffold `backend/app` (`api`, `agents/*`, `tools/*`, `services/*`, `models`, `schemas`, `database`, `rag`, `analytics`, `geospatial`, `routing`, `risk`, `config`), `frontend/src` (`components/chat/map/dashboard`, `pages`, `api`, `stores`), `infrastructure`, `data/knowledge/*`, `scripts`, `tests`
- `docker-compose.yml` (redis:7-alpine, qdrant:v1.13.5, minio:latest) on `orca-network`, volumes `orcelain*_data` inside `D:\Docker\DockerDesktopWSL\disk\docker_data.vhdx` (2.17GB), MinIO ports `9100/9101` to avoid Windows `8947-9046` reservation
- `.env.example` + `.env` + `backend/.env` (DATABASE_URL, REDIS_URL, QDRANT_URL, MINIO_ENDPOINT=localhost:9100, LLM_API_KEY shared)
- Backend skeleton: `FastAPI 0.110`, `Pydantic`, `SQLAlchemy`, `pyproject.toml`, `app/main.py` (CORS 5173), `api/routes/health`, `api/routes/chat` stub, `config/settings.py`, `database/connection.py`, `Dockerfile`
- Frontend skeleton: `React 18 + TypeScript + Vite 5.2 + Tailwind 3.4 + MapLibre 4.4 + ECharts`, `vite.config.ts` proxy `/api->:8000`, `App.tsx` chat+map placeholder
- `.gitignore` (env, venv, node_modules, data/raw, vhdx)

### Tests
- `python -m py_compile` backend `main.py`, `settings.py`, `health.py`, `chat.py` OK
- `docker compose config` validated
- `docker compose up -d` -> `orca-redis Up healthy`, `orca-qdrant Up`, `orca-minio Up healthy` on `D:`
- `redis-cli ping = PONG`, `Qdrant /healthz passed`, `MinIO /minio/health/live 200`

### Notes
- All Docker data on `D:\Docker\DockerDesktopWSL`, project on `D:\Foram_TP\ORCA` - no container data on `C:`
- Follows `04_TECH_STACK`, `16_DEPLOY`, `19_DEV_ENVIRONMENT`

---

## Milestone 01 — Polyglot Storage Layer

Date: 2026-08-29

### Added
- PostgreSQL `18.4` native `D:\PostreSQL` (5432, scram-sha-256) - database `orca_db` created, extensions `postgis 3.6.2`, `postgis_raster 3.6.2`, `uuid-ossp`, `plpgsql`
- `backend/app/database/init_m1.sql` - 20 tables: `users, conversations, messages, agent_runs, tool_runs, data_sources, ingestion_runs, pfz_observations, ocean_observations, weather_observations, marine_hazards, geofences, protected_areas, maritime_boundaries, risk_assessments, routes, alerts, knowledge_documents, knowledge_chunks` + GIST indexes `idx_pfz_geometry`, `idx_geofences_geom`, `idx_protected_geom`, `idx_hazards_geom`, `idx_routes_geom`
- Seeded `data_sources` (6): `INCOIS PFZ`, `INCOIS OSF`, `IMD Weather`, `IMD Cyclone`, `WDPA`, `Marine Regions EEZ`
- MinIO buckets (6): `orca-documents`, `orca-raw-data`, `orca-satellite`, `orca-raster`, `orca-processed`, `orca-artifacts` on `localhost:9100`
- Qdrant collection `orca_knowledge` (`size=384`, `distance=Cosine`, `status green`, `segments 8`)
- Password reset `postgres:postgres` via `pg_hba.conf trust` -> `ALTER USER`, PostGIS enabled

### Changed
- `.env.example` `MINIO_ENDPOINT=localhost:9100` (was 9000, blocked)
- `docker-compose.yml` MinIO ports `9100:9000`, `9101:9001`

### Fixed
- Windows `9000/9001` bind failure due to `excludedportrange 8947-9046` - migrated to `9100/9101`

### Tests
- `psql orca_db` - `SELECT PostGIS_Version() = 3.6 USE_GEOS=1` OK
- `psycopg` `SELECT PostGIS_Version()` OK
- `ST_Contains` geofence test `Test MPA Mumbai POLYGON -> POINT(72.8 19.0) = t` PASSED
- `SELECT count(*) FROM data_sources = 6` OK
- `minio list_buckets = 6` OK
- `Qdrant /collections/orca_knowledge status green` OK
- `redis set orca:test:health ok -> get ok` OK

### Notes
- Follows `05_DATABASE_DESIGN`, `20_DATABSE_ARCHITECTURE` - 5 stores: `PostgreSQL/PostGIS + Redis + MinIO + Qdrant` with correct responsibilities
- All persistent data on `D:` (`docker_data.vhdx` + `D:\PostreSQL\data`), `C:` only binary

---

## Milestone 02 — Data Registry & Pipeline

Date: 2026-08-29

### Added
- `app/services/ingestion/base.py` BaseConnector (`fetch`, `validate_source`, `get_metadata`, `provenance`) per `09_DATA_PIPELINE`
- `app/services/ingestion/validation.py` (`VALID/SUSPECT/INVALID`, `PFZ_SCHEMA`, `WEATHER_SCHEMA`, coord/range/timestamp) + `normalization.py` (UTC ISO8601, EPSG:4326, `K->C`, `ingestion_time` distinct per `05:46`)
- `app/services/ingestion/pipeline.py` IngestionPipeline (`Raw MinIO orca-raw-data -> Validation -> Normalization -> dedupe -> provenance -> Redis cache`) TTL `weather 1800, pfz 86400, hazard 600`
- `app/services/ingestion/connectors/pfz_connector.py` (3 PFZ mock Mumbai), `weather_connector.py` (2 forecasts +6h/+24h)
- `app/services/data_registry.py` DataRegistry (`INTENT_SOURCES`, `select_for_intent`, `check_freshness FRESH/AGING/STALE`) per `08_DATASET_REGISTRY`
- `backend/test_m2.py` end-to-end verification

### Tests
- `DataRegistry` `select pfz_discovery -> INCOIS PFZ` OK
- `IngestionPipeline PFZ 3/3 inserted, Weather 2/2 inserted` (after fix `forecast_time` in dedupe), `raw_stored` `raw/pfz/*.json`, `raw/weather/*.json` OK
- `pfz_observations count 6` (3+3 run), `ingestion_runs` inserted, `MinIO raw objects 2`, `Redis cache hit` on second fetch (`ingestion_cache_hit`), `structlog` `ingestion_completed`

### Fixed
- Weather dedupe incorrectly collapsed `+6h`/`+24h` forecasts (added `forecast_time`+`wind_speed` to key in `pipeline.py:19`)

### Notes
- Follows `07_DATA_ARCHITECTURE`, `08_DATASET_REGISTRY`, `09_DATA_PIPELINE` - `RAW -> MinIO -> Validation -> Normalization -> Structured PostGIS -> Redis TTL -> Agent Tool`
- Mock connectors ready to swap to real `INCOIS/IMD` `fetch()` in M3
- All data still on `D:`

---

## Milestone 03 — Backend API Layer

Date: 2026-08-29

### Added
- `app/main.py:41` 8 routers wired (`/api/v1/health`, `/auth`, `/chat`, `/pfz/nearest`, `/weather`, `/hazards`, `/risk/assess`, `/routes`, `/geospatial/geofence/check`) `Service->Repository->DB` per `12_API_SPEC`
- `database/repositories/pfZ_repo.py:32` `ST_Distance Geog` `weather_repo.py:32` `hazard_repo.py:32` + `schemas/chat.py:1` `pfz.py:1` `weather.py:1` `risk.py:1`
- `core/security.py:27` JWT `HS256` `bcrypt 4.0.1` + `api/deps.py:41` `get_current_user` `OAuth2PasswordBearer` `auth.py` login
- Health `/api/v1/health` `uptime`, `/health/services` live ping, streaming `POST /api/v1/chat/stream` `StreamingResponse` events

### Fixed
- `bcrypt` `passlib` `__about__` crash (downgrade `bcrypt==4.0.1`), `chat.py:83` auth optional for M3 demo

### Tests
- `uvicorn :8000` `GET / 200` `GET /health 200 {status ok}`, `POST /chat/ 200` `MODERATE` synthesis, `GET /pfz/nearest?lat=19 lon=72.8 200 4 items distance_km`, `GET /weather 200`, `GET /hazards 200` with `Bearer test@orca.local` `JWT 165 chars` (`psycopg` `test@orca.local`)

---

## Milestone 04 — Orchestration Core

Date: 2026-08-29

### Added
- `agents/orchestrator/graph.py:32` `StateGraph(OrcaState)` `analyze_intent->planner->execute_agents->synthesize` singleton
- `state.py:28` `OrcaState` `schemas.py:18` `IntentInterpretation` `TaskPlan` Pydantic structured output
- `nodes.py:78` `get_llm()` fallback `None` if no `LLM_API_KEY` -> mock `find_pfz/check_safety/weather_forecast`, `execute_agents_node` real `psycopg` `pfz_observations`/`geofences`/`weather` + deterministic `risk MODERATE/HIGH`, `synthesize_node` mock `[M3/M4 Mock Synthesis]` when no key else `ChatOpenAI gpt-4o-mini`
- Wired `POST /api/v1/chat` `POST /api/v1/chat/stream` `ainvoke`/`astream_events`

### Tests
- `backend/.venv python test_m4.py` without `OPENAI_API_KEY`: `find_pfz -> marine_agent 2 PFZ`, `check_safety -> 4 agents risk MODERATE wind 12.5` PASSED
- `POST /chat` via `uvicorn 8000` `MODERATE risk` evidence from DB verified

### Notes
- Mock synthesis used until `LLM_API_KEY` set in `.env` -> real `gpt-4o-mini` automatically
- All integration on `D:` `uvicorn 2 processes` + `docker_data.vhdx`

---

## Milestone 05 — 8 Specialized Agents + Tools

Date: 2026-08-30

### Added
- Tools `app/tools/pfz.py:1` `get_nearest_pfz` `ST_DWithin`/`ST_Distance` Geog, `weather.py:1` `get_weather`/`get_hazards`, `geospatial.py:1` `check_geofence` `ST_Contains`/`calculate_distance` `ST_Distance`, `ocean.py:1` `get_ocean`, `risk.py:1` `calculate_risk` `LOW/MODERATE/HIGH` `score 0-100` deterministic, `rag.py:1` `search_knowledge` Qdrant mock
- Agents `app/agents/marine/agent.py:1` `MarineAgent` `pfz+ocean`, `weather/agent.py:1` `WeatherAgent` `weather+hazards`, `ocean/agent.py:1`, `geospatial/agent.py:1` `PostGIS`, `risk/agent.py:1` `weather+ocean+geofence -> risk_score 45`, `routing/agent.py:1` `distance 18km`, `rag/agent.py:1` `evidence`
- Refactored `agents/orchestrator/nodes.py:78` `execute_agents_node` to use `agent_map` `marine/weather/ocean/geospatial/risk/routing/rag` with dependency-aware sequential exec, location `Mumbai 19.0,72.8`/`Ratnagiri 16.9,73.3`
- `agents/*/__init__.py` dirs created

### Tests
- `backend/.venv` `asyncio.run(orchestrator.ainvoke)`: `Where is nearest PFZ? -> marine_agent 3 PFZ 15.2km`, `Is it safe tomorrow Mumbai? -> 4 agents weather 12.5 + marine 3 PFZ + geofence inside Test MPA + risk MODERATE 45`, `What is weather Ratnagiri? -> weather_agent`, `uvicorn :8000` `POST /chat 1114 chars` `MODERATE risk` verified, `check_geofence 19.0,72.8 -> inside Test MPA protected distance 0.0`, `calculate_risk 18,3.0 -> HIGH 70`

### Notes
- Follows `06_AGENT_SPEC` 8 agents `AI-010..017` each single responsibility + tools, `AI-007` deterministic `PostGIS` no LLM math, `AI-005` collaboration via `OrcaState` `agent_results`
- All data on `D:` `docker_data.vhdx` + `D:\PostreSQL`
