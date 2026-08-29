# ORCA — Current Status

## Current Milestone

**Milestone 02 — Data Registry & Pipeline (M2) Completed**

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

## Working

- `docker compose up -d` `orca-*` healthy on `D:`, `IngestionPipeline` `Raw->MinIO->Validation->Normalization->PostGIS->Redis` working
- `D:\PostreSQL` `pfz_observations 6 rows`, `ingestion_runs` tracking, `data_registry` `select_for_intent` `pfz_discovery -> INCOIS PFZ`
- MinIO `raw/pfz/*.json`, `raw/weather/*.json` stored, Qdrant ready, Redis `orca:pfz:*`/`orca:weather:*` TTL cached
- Backend pipeline verified `test_m2.py:1` `PFZ 3 + Weather 2`, `structlog` `ingestion_completed`

## In Progress

- M3 Backend API Layer (next)

## Pending

- M3 Backend API Layer (`/api/v1/chat`, auth, health/services)
- M4 Orchestration (LangGraph)
- M5 Agents + Tools
- M6 Risk/Route engines
- M7 Static GIS datasets (EEZ subset)
- M8 RAG ingestion
- M9 Frontend Map+Chat
- M10 Conversational
- M11 Security
- M12 Testing + Observability

## Known Issues

- MinIO `9000` blocked -> `9100` fixed (see `docker-compose.yml:22`)
- Weather mock dedupe needed `forecast_time` in key (fixed `pipeline.py:19`)
- Live INCOIS/IMD fetch still mock - swap to real `fetch()` in pipeline after `M3` (real APIs require network)
- `fastapi` not yet running as service (M3)

## Next Milestone

**M3: Backend API Layer** - FastAPI `12_API_SPEC` `/api/v1/health, /chat, /pfz, /weather, /ocean, /geofences, /risk, /routes` + Pydantic, Service->Repository, JWT, streaming

## Architecture Status

- Follows `03_ARCHITECTURE` 10 layers, `05_DATABASE_DESIGN` polyglot `PostgreSQL/PostGIS + Redis + MinIO + Qdrant` per `20_DATABSE_ARCHITECTURE`
- `Docker Desktop` data on `D:\Docker\DockerDesktopWSL`, project on `D:\Foram_TP\ORCA` - `C:` only has binary
- Native `PostGIS` retained per `19_DEV_ENVIRONMENT`, container `postgres` commented out in compose
