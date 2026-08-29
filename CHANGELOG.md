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
- `backend/app/api/routes` completed with routers for `health`, `auth`, `chat`, `pfz`, `weather`, `hazards`, `risk`, `routes`, `geospatial`.
- `backend/app/database/repositories` base and specific repos for users, PFZ, weather, and hazards.
- `backend/app/schemas` Pydantic models for request/response serialization across endpoints.
- JWT Authentication and RBAC via `security.py` and `deps.py`.
- Service health endpoint `/api/v1/health/services` that live pings PostgreSQL, Redis, Qdrant, and MinIO.
- Real-time chat streaming endpoint via `StreamingResponse`.

### Tests
- `/api/v1/health/services` successfully connected to all four databases simultaneously.
- Routers successfully wired and verified in `main.py`.

---

## Milestone 04 — Orchestration Core

Date: 2026-08-29

### Added
- LangGraph orchestration application inside `backend/app/agents/orchestrator`.
- `state.py` for shared `OrcaState` (intent, plan, agent_results).
- `schemas.py` for LLM structured output parsing (`IntentInterpretation`, `TaskPlan`).
- `nodes.py` defining the graph workflow (`analyze_intent`, `planner`, `execute_agents`, `synthesize`).
- `graph.py` compiling the StateGraph.
- Lazy-loading of `ChatOpenAI` LLM initialization to prevent `FastAPI` startup crashes without an `OPENAI_API_KEY`.
- Directly wired orchestrator events to `/api/v1/chat/stream`.

### Tests
- Simulated execution flow successfully steps through Intent -> Plan -> Execute -> Synthesize.
- Fallback import test confirmed no crashes without `OPENAI_API_KEY`.
