"""ORCA FastAPI entrypoint - docs 03_ARCHITECTURE API Layer."""
import os
# M7 thorough fix: rasterio PROJ mismatch (PostGIS proj.db MINOR 2 vs rasterio needs >=6) - force venv's PROJ
os.environ["PROJ_LIB"] = r"D:\Foram_TP\ORCA\backend\.venv\Lib\site-packages\pyproj\proj_dir\share\proj"
os.environ["GDAL_DATA"] = r"D:\Foram_TP\ORCA\backend\.venv\Lib\site-packages\rasterio\gdal_data"
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, chat, auth, pfz, weather, hazards, risk, routes, geospatial

log = structlog.get_logger()

app = FastAPI(
    title="ORCA Marine Intelligence Platform",
    version="0.1.0",
    description="Agentic AI-powered Marine Intelligence Platform",
)

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


@app.get("/")
async def root():
    return {"service": "ORCA", "status": "running", "docs": "/docs"}


@app.on_event("startup")
async def on_startup():
    log.info("orca_startup", environment="development")
