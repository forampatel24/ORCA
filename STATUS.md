# ORCA — Current Status

## Current Milestone

**Milestone 15 — Visualization Sidebar + Copernicus Gridded (Honest Station, Mausam-aligned)**

Date: 2026-09-06

Branch: feat/ui-marine-visualization-sidebar → merged to main @ 9181902 + docs 7f5391b

## Completed

- **M13 — Mumbai Live Legit:** Weather 23 / Ocean 23 (19.076,72.877 single-point 15 Aug–06 Sep Open-Meteo Archive/Marine), Maritime 5, Geofences 1 (Natural Earth 10m 557 pts), PFZ 46 (INCOIS derived), Protected 0 legit, DB 38 MB, Copernicus fpatel1 dry-run 43KB validated, GFW 30 vessels.

- **M14 — Ocean Grid Ingestion:** Copernicus `data/raw_copernicus/*.nc` `13×12 0.083°` physics `thetao/so/uo/vo/zos` + `chl 5×4` ingested via `scripts/ingest_copernicus_grid.py` — 102 water-only rows `metadata.source=copernicus_grid_phy_20260620` land NaN masked, `ocean_observations` 23 → 125, `GET /ocean/grid?bbox=72.2,18.5,73.2,19.5` returns 87 pts `{lat,lon,thetao,so,uo,vo,current_speed,zos,chlorophyll}` per-pixel real.

- **M15 — Visualization Workspace:** 3-panel `Chat 380px + Map Leaflet OSM + Viz Sidebar 320px slide-out` — 4 categories `Fishing/Marine/Safety/Navigation` → 18 subs, deterministic honest **single real station marker** `19.076,72.877` for SST/Chl/Wind/Waves/Weather/Sea (no random, no waves on land) + optional 87-pt Copernicus grid overlay (SST/currents, water-only, per-pixel true), legend + info card, Maharashtra transparent fill + `#0284c7` coastline (Mausam-aligned), `frontend 781 modules 1,473kB` vite build.

## Working

- `docker compose` 4 healthy `orca-postgres:5432 (PostGIS 16-3.4 alpine)` / `orca-redis:6379` / `orca-minio:9100` / `orca-qdrant:6333`, `uvicorn :8000` 10 routers (`/chat`, `/pfz/nearest`, `/weather`, `/hazards`, `/risk/assess`, `/routes/calculate`, `/geospatial/*`, `/ocean/{history,grid}`, `/health`), `vite :5173` (or 5174), `GET /ocean/grid 200 87 pts`, `GET /ocean/history 23`, `geospatial/eez 200` `coastline 200` `pfz 401 auth`.

## Pending

- Ingest `2026-08-15→09-06` daily Copernicus NRT grid 23× via `copernicusmarine` (`fpatel1`) to replace single-date `2026-06-20` with 23-day spatial heatmap; PFZ live when INCOIS window opens; GFW vessel bbox extended; `CMFRI/OBIS` → `GET /fish` API; `GET /ports` dataset.

## Known Issues

- Single-station `SST/Chl/Wind/Waves` is honest but not spatial — Copernicus grid currently single date `2026-06-20` (real) not yet 23-day series. Currents now real `uo/vo` per-pixel but only for that date. `protected_areas 0` / `marine_hazards 0` are legit empty in Mumbai bbox per `09_DATA_PIPELINE`.

## Next Milestone

**M16 — 23-day Copernicus NRT daily grid + Fish/Ports APIs + Risk/Route real scoring**

## Architecture Status

- Docker PostGIS on `D: docker_data.vhdx` `orca-postgres` volume, `init_m1.sql` `GEOMETRY(GEOMETRY,4326)` + `GIST` + `ALTER DEFAULT PRIVILEGES`, `.env` `fpatel1/ForamPatel@31` + `GFW` valid, `data/raw_copernicus/*.nc` tracked (102 rows ingested), no hardcode via `app/config/mumbai.py`, land `fillOpacity 0` + coastline `#0284c7` Mausam-aligned, `no random` policy enforced.
