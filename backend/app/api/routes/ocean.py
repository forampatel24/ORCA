from fastapi import APIRouter, Depends, Query
from app.database.connection import psycopg_conninfo
import psycopg

router = APIRouter()

def _conn():
    return psycopg.connect(psycopg_conninfo())

@router.get("/history")
async def ocean_history(latitude: float, longitude: float, limit: int = 7):
    # Public read: charts/map need data before login. Latest-N chronological
    # (DESC in SQL, reversed) so limit=7 always means the past week to today.
    conn=_conn()
    cur=conn.cursor()
    cur.execute("SELECT sst, chlorophyll, wave_height, observation_time FROM ocean_observations WHERE ST_Within(location::geometry, ST_MakeEnvelope(72.2,18.5,73.2,19.5,4326)) ORDER BY observation_time DESC LIMIT %s", (limit,))
    rows=list(reversed(cur.fetchall()))
    conn.close()
    return {"items": [{"sst": r[0], "chlorophyll": r[1], "wave_height": r[2], "observation_time": r[3].isoformat() if r[3] else None} for r in rows]}

@router.get("/chlorophyll-history")
async def chlorophyll_history(latitude: float, longitude: float):
    # Public read. Real daily chlorophyll from the fresh Copernicus NRT grid
    # (bgc-pft_anfc, 0.25deg), nearest cell to the point. No mock fallback.
    from app.services.copernicus_store import chl_series
    items = chl_series(latitude, longitude)
    return {"items": items, "count": len(items),
            "source": "copernicus_bgc-pft_anfc Mumbai 01-07 Sep 2026, nearest 0.25deg cell"}

@router.get("/sst-grid")
async def sst_grid(bbox: str = Query(default="71.8,15.5,74.5,20.5")):
    # Public read. Full spatial SST from fresh NRT grid (phy hourly thetao,
    # 0.083deg, latest hour) for the SST map layer. No mocks.
    from app.services.copernicus_store import grid_cells
    try:
        bb = tuple(map(float, bbox.split(",")))
    except Exception:
        bb = (71.8, 15.5, 74.5, 20.5)
    cells, tdate = grid_cells("sst", bb)
    return {"count": len(cells), "bbox": bbox, "time": tdate, "cells": cells,
            "source": "copernicus_phy_anfc hourly thetao 0.083deg Mumbai"}

@router.get("/chlorophyll-grid")
async def chlorophyll_grid(bbox: str = Query(default="71.8,15.5,74.5,20.5")):
    # Public read. Full spatial chlorophyll from fresh NRT grid (bgc-pft_anfc,
    # 0.25deg, latest day) for the chlorophyll map layer. No mocks.
    from app.services.copernicus_store import grid_cells
    try:
        bb = tuple(map(float, bbox.split(",")))
    except Exception:
        bb = (71.8, 15.5, 74.5, 20.5)
    cells, tdate = grid_cells("chl", bb)
    return {"count": len(cells), "bbox": bbox, "time": tdate, "cells": cells,
            "source": "copernicus_bgc-pft_anfc daily chl 0.25deg Mumbai"}


@router.get("/currents-grid")
async def currents_grid(bbox: str = Query(default="71.8,15.5,74.5,20.5")):
    # Public read. Fresh NRT currents vectors (phy hourly uo/vo, 0.083deg,
    # latest hour) for the currents streamlines layer. No mocks.
    from app.services.copernicus_store import currents_cells
    try:
        bb = tuple(map(float, bbox.split(",")))
    except Exception:
        bb = (71.8, 15.5, 74.5, 20.5)
    cells, tdate = currents_cells(bb)
    return {"count": len(cells), "bbox": bbox, "time": tdate, "cells": cells,
            "source": "copernicus_phy_anfc hourly uo/vo 0.083deg Mumbai"}


@router.get("/waves-grid")
async def waves_grid(bbox: str = Query(default="71.8,15.5,74.5,20.5")):
    # Public read. Fresh NRT wave field (WAM VHM0/VTM02/VMDR, 0.083deg 3-hourly,
    # latest slot) for the waves layer. Every cell a real value, land masked.
    from app.services.copernicus_store import waves_cells
    try:
        bb = tuple(map(float, bbox.split(",")))
    except Exception:
        bb = (71.8, 15.5, 74.5, 20.5)
    cells, tdate = waves_cells(bb)
    return {"count": len(cells), "bbox": bbox, "time": tdate, "cells": cells,
            "source": "copernicus_wav_anfc VHM0/VTM02/VMDR 0.083deg Mumbai"}


@router.get("/wind-grid")
async def wind_grid(bbox: str = Query(default="71.8,15.5,74.5,20.5")):
    # Public read. Spatial wind field - live per-cell Open-Meteo forecast
    # (current wind_speed_10m + direction), no single-point copy.
    from app.services.wind_store import wind_cells
    try:
        bb = tuple(map(float, bbox.split(",")))
    except Exception:
        bb = (71.8, 15.5, 74.5, 20.5)
    cells, tdate = await wind_cells(bb)
    return {"count": len(cells), "bbox": bbox, "time": tdate, "cells": cells,
            "source": "open-meteo forecast wind_speed_10m/wind_direction_10m per-cell Mumbai"}


@router.get("/tides")
async def tides_live(hours: int = Query(default=48, le=120)):
    """Mumbai tides - harmonic prediction (Admiralty constituents), no mock series."""
    from app.services.tide_store import tides_window, tide_extremes
    return {"extremes": tide_extremes(hours=hours), "series": tides_window(hours=hours),
            "datum": "Chart datum (Mumbai Apollo Bunder), MSL 2.10 m",
            "source": "harmonic constituents (Admiralty NP 83, 10 constituents)"}

@router.get("/grid")
async def ocean_grid(bbox: str = Query(default="72.2,18.5,73.2,19.5")):
    """Real Copernicus gridded per-pixel values — thetao/sst, so, uo, vo, current_speed, chlorophyll. Water only (land NaN masked)."""
    try:
        min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
    except:
        min_lon, min_lat, max_lon, max_lat = 72.2, 18.5, 73.2, 19.5
    conn=_conn()
    cur=conn.cursor()
    cur.execute("""
        SELECT ST_Y(location::geometry) as lat, ST_X(location::geometry) as lon,
               sst as thetao, chlorophyll, current_speed,
               metadata->>'so' as so, metadata->>'zos' as zos, metadata->>'uo' as uo, metadata->>'vo' as vo,
               observation_time
        FROM ocean_observations
        WHERE metadata->>'source' LIKE 'copernicus_grid%%'
          AND ST_Within(location::geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326))
        ORDER BY lat, lon
    """, (min_lon, min_lat, max_lon, max_lat))
    rows = cur.fetchall()
    conn.close()
    points = []
    for r in rows:
        lat, lon, thetao, chl, curr, so, zos, uo, vo, ot = r
        points.append({
            "lat": lat, "lon": lon,
            "thetao": thetao, "sst": thetao,
            "chlorophyll": chl, "current_speed": curr,
            "so": float(so) if so else None, "zos": float(zos) if zos else None,
            "uo": float(uo) if uo else None, "vo": float(vo) if vo else None,
            "observation_time": ot.isoformat() if ot else None
        })
    return {"count": len(points), "bbox": bbox, "points": points, "source": "copernicus_grid_phy_20260620 (thetao/so/uo/vo/zos + chl reanalysis), 0.083° 13x12 water-masked"}
