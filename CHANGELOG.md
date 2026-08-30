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

---

## Milestone 06 � Intelligence Engines

Date: 2026-08-30

### Added
- pp/analytics/risk/engine.py:1 4 levels LOW/MODERATE/HIGH/VERY_HIGH thresholds wind 10/15/20 wave 1.5/2.5/3.5 + lightning/cyclone/geofence score safety_override
- pp/analytics/pfz/scoring.py:1 weighted ocean 0.3 + env 0.2 + safety 0.35 + access 0.15 pfz_score 0.776
- pp/analytics/ocean/anomaly.py:1 sst_anomaly aseline 27.0 chlorophyll_anomaly
- pp/analytics/routing/engine.py:1 haversine score_route cost=0.3*dist+0.2*time+0.5*risk geofence penalty
- Updated gents/risk/agent.py:1 gents/routing/agent.py:1 gents/marine/agent.py:1 scored_pfz + anomalies, 
odes.py:78 synthesis [M5/M6 Synthesis]

### Tests
- isk LOW 0 MOD 25 HIGH 95 VERY_HIGH 165 pfz 0.776 sst +1.5 haversine 33.43 oute cost 0.359 orchestrator check_safety -> risk 45 MODERATE verified ackend/.venv

### Notes
- Follows 15_ML_ANALYTICS deterministic AI-007 no LLM math, safety_override per docs 25

---

## Milestone 07 - Static GIS Datasets

Date: 2026-08-30

### Added
- data/external/eez_india.geojson India EEZ -> maritime_boundaries 1
- data/external/mpa_india.geojson 2 MPAs -> protected_areas 2
- data/external/coastline_india.geojson -> geofences 2
- data/external/cmfri_landings.csv 8 rows -> cmfri_landings 8
- data/processed/bathymetry_sample.tif 80 bytes -> MinIO orca-raster/bathymetry/gebco_subset_sample.tif
- scripts/ingest_m7.py verified ST_Contains true

### Tests
- maritime 1 + protected 2 + geofences 2 + cmfri 8 EEZ contains Mumbai true

---

## Milestone 08 - RAG Layer

Date: 2026-08-30

### Added
- app/rag/chunking.py 700/100 + ingestion.py MinIO->PyMuPDF->FastEmbed 384->Qdrant + retrieval.py rerank + citation
- 4 docs 6 chunks Qdrant 6 MinIO 4 PG docs 4 chunks 6 verified
- app/tools/rag.py delegates to retrieve, app/agents/rag/agent.py uses real RAG

### Tests
- wind risk 0.775 MPA 0.68 PFZ 0.674 cyclone 0.753 citation verified

### Fixed
- Qdrant 1.19 vs 1.13 check_compatibility=False, query_points API, chunking 3 chunks for long manual

---

## Milestone 09 - Frontend Command Center

Date: 2026-08-30

### Added
- frontend/src/api/client.ts axios + login + chat/pfz/weather/hazards + interceptors
- frontend/src/stores/chatStore.ts zustand + mapStore.ts center/pfz/layers
- frontend/src/components/map/MapView.tsx MapLibre 7 markers + NavigationControl
- frontend/src/components/chat/ChatPanel.tsx login + chat+map sync PFZ fetch + setCenter
- frontend/src/components/dashboard/RiskCard.tsx + Charts.tsx ECharts SST/Chl
- frontend/src/App.tsx 12-col Command Center header + time slider + evidence drawer + layer toggles + TanStack QueryClient

### Tests
- npm run build 2.1MB 738 modules 25s + vite dev 5173 406ms + proxy /api/v1/health 200 + login 200 + pfz 5 15.2km + chat 200 via 5173 proxy

### Fixed
- ImportMeta env TS2339 -> (import.meta as any).env
- npm run dev Start-Process npm.cmd vs npm
