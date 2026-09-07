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
