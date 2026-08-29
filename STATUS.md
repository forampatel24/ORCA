# ORCA — Current Status

## Current Milestone

**Milestone 01 — Polyglot Storage Layer (M1) Completed** (M0 Foundation also completed)

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

## Working

- `docker compose up -d` brings `orca-redis`, `orca-qdrant`, `orca-minio` healthy on `D:`
- `D:\PostreSQL` `5432` `PostGIS` spatial queries work (`ST_DWithin`, `ST_Contains`, `ST_Distance`)
- MinIO buckets reachable, Qdrant vector store ready for `FastEmbed bge-small-en 384`
- Backend skeleton compiles (`py_compile` OK), frontend scaffold ready
- All storage on `D:`: `D:\Docker\DockerDesktopWSL` + `D:\PostreSQL\data` + `D:\Foram_TP\ORCA\data`

## In Progress

- M2 Data Registry & Pipeline (next)

## Pending

- M2 Data Registry & Pipeline
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

- MinIO default `9000/9001` blocked by Windows `excludedportrange 8947-9046` - mitigated via `9100/9101` (see `docker-compose.yml:22`)
- `fastapi` not yet installed in host `venv` - scaffold only, `uvicorn` not yet running (will be in M3)
- No real datasets loaded yet - only registry + empty tables (M2 will populate)

## Next Milestone

**M2: Data Registry & Pipeline** - implement `data_sources` connector abstraction, ingestion validation/normalization, `ingestion_runs` tracking, Redis TTL caching

## Architecture Status

- Follows `03_ARCHITECTURE` 10 layers, `05_DATABASE_DESIGN` polyglot `PostgreSQL/PostGIS + Redis + MinIO + Qdrant` per `20_DATABSE_ARCHITECTURE`
- `Docker Desktop` data on `D:\Docker\DockerDesktopWSL`, project on `D:\Foram_TP\ORCA` - `C:` only has binary
- Native `PostGIS` retained per `19_DEV_ENVIRONMENT`, container `postgres` commented out in compose
