# ORCA — Current Status

## Current Milestone

**Milestone 09 — Frontend Command Center (M9) Completed**

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

- **M7: Static GIS Datasets (08_DATASET_REGISTRY)**
  - `data/external/eez_india.geojson:1` `India EEZ Polygon 68,8-75,24` -> `maritime_boundaries 1` `ST_Contains Mumbai true`, `mpa_india.geojson:1` `Gulf of Mannar 78,8.5-79.5,9.5 + Malvan 73.3,16.0` -> `protected_areas 2` `ST_Contains Gulf true`
  - `coastline_india.geojson:1` `Maharashtra Line 72.5,18.5-73.0,20.0` -> `geofences 2` (Test MPA + `Maharashtra Coastline 5km buffer` `ST_Buffer`), `data/external/cmfri_landings.csv:8` `2020-2023 Maharashtra/Gujarat` -> `cmfri_landings 8` `12500->7100 decline`
  - `data/processed/bathymetry_sample.tif` `442 bytes` real GeoTIFF `10x10` `EPSG:4326` (after `PROJ_LIB` fix) -> `MinIO orca-raster/bathymetry/gebco_subset_sample.tif`
  - `scripts/ingest_m7.py:1` + `test_m7_verify.py:1` verified `ST_DWithin 10km coastline true`, `ST_Contains EEZ/MPA true`, `GIST` indexes `idx_maritime_geom` etc. already from M1, altered `maritime_boundaries` to `GEOMETRY(GEOMETRY,4326)` to allow Polygon

- **M8: RAG Layer (10_RAG_ARCHITECTURE)**
  - `app/rag/chunking.py:1` `chunk_text 700/100` `clean_text`, `app/rag/ingestion.py:1` `MinIO orca-documents -> PyMuPDF (fitz 1.28.2) -> chunk -> FastEmbed BGE-small-en-v1.5 384 -> Qdrant orca_knowledge + PG knowledge_documents/chunks` idempotent
  - `app/rag/retrieval.py:1` `retrieve top_k 5 -> rerank top_n 3` `cosine` `citation source/title#chunk`, `app/tools/rag.py:1` delegates to `retrieve`, `app/agents/rag/agent.py:1` uses `tools/rag`
  - Ingested `4 docs` `incois_advisory_2026.txt 1 chunk + pfz_advisory_2026.pdf 1 chunk (PyMuPDF) + comprehensive_safety_manual.txt 3 chunks (700/100) + marine_safety_guideline.txt 1 chunk` `=6 chunks` `MinIO orca-documents 4 objects` `Qdrant 6 points` `PG docs 4 chunks 6`
  - Retrieval `wind risk 15 -> safety/comprehensive#chunk0 0.775`, `MPA buffer -> safety/marine 0.68`, `PFZ SST -> pfz_advisory 0.674`, `rag_agent` real `INCOIS High Wind 18-22 m/s` `citation`

- **M9: Frontend Command Center (13_FRONTEND_ARCHITECTURE)**
  - `frontend/src/api/client.ts:1` `axios` `login` `chat/pfz/weather/hazards` `localStorage token` `VITE_API_BASE_URL`, `frontend/src/stores/chatStore.ts:1` `zustand` `messages/loading`, `mapStore.ts:1` `center/pfz/layers`
  - `frontend/src/components/map/MapView.tsx:1` `MapLibre 4.4` `NavigationControl` `PFZ markers` `selectedPfz amber`, `frontend/src/components/chat/ChatPanel.tsx:1` `ensureLogin test@orca.local` `chat+map sync` `getNearestPFZ -> setPfz/setCenter`
  - `frontend/src/components/dashboard/RiskCard.tsx:1` `Charts.tsx:1` `ReactECharts` `SST line 27.8-28.5` `Chl bar 0.6-1.1`, `frontend/src/App.tsx:1` `12-col` `header time slider` `evidence drawer` `layer toggles pfz/mpa/eez` `QueryClientProvider` `TanStack`
  - `vite.config.ts:1` `proxy /api -> 8000`, `package.json:1` `zustand 4.5 + tanstack 5.50 + maplibre 4.4 + echarts 5.5`

## Working

- `docker compose up -d` `orca-*` 31h healthy on `D:` `9100/6333/6379` `2.51GB` + `D:\PostreSQL 5432 PostGIS 3.6.2` `20 tables` + `uvicorn :8000` `1740s` `GET / 200` + `vite :5173` `200` `proxy /api -> 8000` `2.1MB` `738 modules`
- `M6 engines` `risk VERY_HIGH 165` `pfz 0.776` `sst +1.5` + `M7 GIS` `maritime 1 + protected 2 + geofences 2 + cmfri 8` + `M8 RAG` `4 docs 6 chunks Qdrant 6` `retrieval 0.775` + `M9` `POST /chat via 5173 proxy 200` `PFZ 5 15.2km` `MapLibre markers` `ECharts SST/Chl` `chat+map sync` `Zustand/TanStack`

## In Progress

- M10 Conversational Layer (next)

## Pending

- M10 Conversational `there/that zone/tomorrow`
- M9 Frontend Map+Chat
- M10 Conversational
- M11 Security
- M12 Testing + Observability

## Known Issues

- None - all `M0-M7` issues resolved. `M7` `PROJ` rasterio `MINOR 2 vs 6` thorough fix: `PROJ_LIB` forced to `backend/.venv/pyproj/proj_dir` `GDAL_DATA` to `rasterio/gdal_data` in `app/main.py:1`, `ingest_m7.py:1` now creates real GeoTIFF `bathymetry_sample.tif` `10x10` `442 bytes` `CRS EPSG:4326` verified `rasterio.open width 10 height 10` (fallback dummy retained for CI without PROJ update).

## Fixed - Thorough Resolution 2026-08-30
- `weather_observations` `mock 0 -> real 2 rows` `wind 12.5/18.0` `temp 29.0` `POINT(72.8 19.0)` `tools/weather.py:1` `source weather_observations` `GET /weather 200` verified
- `Qdrant orca_knowledge` `0 -> 2 points` `INCOIS 227b + Safety 268b` `FastEmbed BGE-small-en-v1.5 384` `search_knowledge` `query_points` `score 0.84` `rag_agent` real `INCOIS 18-22 m/s`
- `POST /api/v1/chat` `unauthenticated -> authenticated` per `14_SECURITY` - `auth.py:38` `login` `test@orca.local/test123` `JWT 165 chars` `401 without token` `200 with Bearer` verified `chat_auth.json`
- `bcrypt 4.0.1` `MinIO 9100` `docker_data.vhdx 2.17GB` on `D:` already fixed, `LLM_API_KEY` mock `[M5/M6 Synthesis]` with clear fallback when not set (real `gpt-4o-mini` when set in `.env`)

## Next Milestone

**M10: Conversational Layer** - `multi-turn` `there/that zone/tomorrow` `language detection` per `02_CONV` `03_ARCHITECTURE`

## Architecture Status

- Follows `03_ARCHITECTURE` 10 layers, `05_DATABASE_DESIGN` polyglot `PostgreSQL/PostGIS + Redis + MinIO + Qdrant` per `20_DATABSE_ARCHITECTURE`
- `Docker Desktop` data on `D:\Docker\DockerDesktopWSL`, project on `D:\Foram_TP\ORCA` - `C:` only has binary
- Native `PostGIS` retained per `19_DEV_ENVIRONMENT`, container `postgres` commented out in compose
