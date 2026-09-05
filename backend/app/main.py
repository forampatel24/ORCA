"""ORCA FastAPI entrypoint - docs 03_ARCHITECTURE API Layer."""
import os
from pathlib import Path
# M7 fix: PROJ/GDAL mismatch — auto-detect venv's PROJ data portable (no D: hardcode)
# Friend clone on any drive/OS: use relative venv if exists, else leave env untouched
try:
    import sys
    _venv_proj = Path(sys.prefix) / "Lib" / "site-packages" / "pyproj" / "proj_dir" / "share" / "proj"
    # also try import location (works for .venv, venv, global)
    import pyproj as _pyproj
    _import_proj = Path(_pyproj.__file__).parent / "proj_dir" / "share" / "proj"
    for _cand in [_venv_proj, _import_proj]:
        if _cand.exists() and _cand.is_dir():
            os.environ.setdefault("PROJ_LIB", str(_cand))
            os.environ.setdefault("PROJ_DATA", str(_cand))
            break
except Exception:
    pass
try:
    import rasterio as _rio  # type: ignore
    _rio_gdal = Path(_rio.__file__).parent / "gdal_data"
    if _rio_gdal.exists():
        os.environ.setdefault("GDAL_DATA", str(_rio_gdal))
except Exception:
    pass
import structlog
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.api.routes import health, chat, auth, pfz, weather, hazards, risk, routes, geospatial
from app.core.middleware import RequestIDMiddleware

log = structlog.get_logger()

app = FastAPI(
    title="ORCA Marine Intelligence Platform",
    version="0.1.0",
    description="Agentic AI-powered Marine Intelligence Platform",
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(pfz.router, prefix="/api/v1/pfz", tags=["pfz"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["weather"])
app.include_router(hazards.router, prefix="/api/v1/hazards", tags=["hazards"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["risk"])
app.include_router(routes.router, prefix="/api/v1/routes", tags=["routes"])
app.include_router(geospatial.router, prefix="/api/v1/geospatial", tags=["geospatial"])


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {"service": "ORCA", "status": "running", "docs": "/docs"}


@app.on_event("startup")
async def on_startup():
    log.info("orca_startup", environment="development")
