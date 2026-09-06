# ORCA — Current Status

## Current Milestone

**Milestone 13 — Mumbai Live (15 Aug → 06 Sep) — Auth + Docker + 23-Day Legit**

Date: 2026-09-06

Branch: feat/m13b-mumbai-pfz-rag-copernicus → merged to main

## Completed

- **M12 fixes carried:** Docker PostGIS 16-3.4 alpine on 5432 (was native D:\PostreSQL / C:\Program Files), orca-postgres healthy, email-validator installed, bcrypt 4.0.1, Charts 23-day Mumbai trend.

- **M13 — Mumbai Live Legit (no synthetic):**
  - Weather 23 days 2026-08-15→09-06 Open-Meteo Archive legit, Ocean 23 days SST/wave Open-Meteo Marine legit, Maritime 5 MarineRegions WFS Mumbai bbox 72.2,18.5,73.2,19.5, Geofences 1 Natural Earth 10m clipped, CMFRI 8 Maharashtra, Knowledge 4 docs 6 chunks Qdrant 6, DB 38 MB 0.37% of 10GB, MinIO 3230 bytes.
  - PFZ 0 legit (INCOIS daily window closed, no synthetic 3 zones), Chlorophyll null (Open-Meteo Marine no chl, needs Copernicus/MOSDAC), Protected 0 legit (no MPA in Mumbai bbox).
  - Copernicus validated fpatel1 dry-run thetao 2026-06-20 43KB Mumbai bbox, GFW 782 chars 200 OK 30 vessels.
  - Backend health 200 metrics has orca, login test@orca.local 200 weather 23 08-15, frontend build 779 modules 476kB, Charts SstChart/ChlorophyllChart 23-day legit.

## Working

- docker compose 4 healthy orca-postgres/redis/minio/qdrant, uvicorn :8000 startup complete, vite :5173, geospatial/eez 200 coastline 200 mpa 200, pfz 401 expected auth.

## Pending

- PFZ live when INCOIS advisory opens, chlorophyll via Copernicus/MOSDAC, bathymetry real GEBCO subset, GFW vessel bbox extended.

## Known Issues

- None — pfz 0/chlorophyll null are legit STALE per 09_DATA_PIPELINE, not synthetic.

## Next Milestone

**M14 — Copernicus/MOSDAC live chlorophyll + GFW vessel ingestion to MinIO/PostGIS**

## Architecture Status

- Docker PostGIS on D: docker_data.vhdx, init_m1.sql fixed GEOM(GEOMETRY,4326) for future clones, grants extended ALTER DEFAULT, .env fpatel1/GFW valid, no hardcode coords via app/config/mumbai.py
