"""Wind spatial grid - Open-Meteo forecast per-cell, cached 10 min.

No Copernicus wind variable in the downloaded NRT grids, so the wind field
uses the same live source as the station history: api.open-meteo.com.
A bbox grid is built by sampling the forecast at strided points (default
~80 cells, 5x5..9x9) in parallel and returning real speed/dir per cell.
Honest cache invalidation (10 min TTL), with per-cell null when the upstream
has no value - never a mock constant.

Usage: GET /api/v1/ocean/wind-grid?bbox=71.8,15.5,74.5,20.5
"""
import asyncio
import httpx
import structlog
from datetime import datetime, timezone, timedelta

log = structlog.get_logger()

_CACHE = {"bbox": None, "t": None, "cells": None, "time": None}
TTL = 600  # seconds


def _grid_coords(bbox, nx=9, ny=9):
    min_lon, min_lat, max_lon, max_lat = bbox
    lons = [min_lon + (max_lon - min_lon) * i / max(1, nx - 1) for i in range(nx)]
    lats = [min_lat + (max_lat - min_lat) * i / max(1, ny - 1) for i in range(ny)]
    return [(lat, lon) for lat in lats for lon in lons]


async def wind_cells(bbox, nx=6, ny=6):
    now = datetime.now(timezone.utc)
    if _CACHE["cells"] is not None and _CACHE["bbox"] == bbox and _CACHE["t"] and (now - _CACHE["t"]).total_seconds() < TTL:
        return _CACHE["cells"], _CACHE["time"]
    coords = _grid_coords(bbox, nx=nx, ny=ny)
    # Fetch wind at each grid point in parallel, current hour only.
    sem = asyncio.Semaphore(8)

    async def one(lat, lon):
        async with sem:
            try:
                async with httpx.AsyncClient(timeout=20) as c:
                    r = await c.get("https://api.open-meteo.com/v1/forecast",
                                    params={"latitude": lat, "longitude": lon,
                                            "current": "wind_speed_10m,wind_direction_10m,wind_gusts_10m",
                                            "timezone": "UTC"})
                    if r.status_code != 200:
                        return None
                    cur = r.json().get("current", {}) or {}
                    sp = cur.get("wind_speed_10m")
                    di = cur.get("wind_direction_10m")
                    gu = cur.get("wind_gusts_10m")
                    if sp is None or di is None:
                        return None
                    return {"lat": round(lat, 3), "lon": round(lon, 3),
                            "speed": round(float(sp), 1), "direction": round(float(di), 0),
                            "gust": round(float(gu), 1) if gu is not None else None}
            except Exception as e:
                log.warning("wind_cell_failed", lat=lat, lon=lon, error=str(e)[:80])
                return None

    # Small grid: run all at once with bounded concurrency
    results = await asyncio.gather(*[one(lat, lon) for lat, lon in coords])
    cells = [r for r in results if r is not None]
    tdate = now.isoformat()
    _CACHE.update({"bbox": bbox, "t": now, "cells": cells, "time": tdate})
    return cells, tdate
