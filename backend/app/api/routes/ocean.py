from fastapi import APIRouter, Depends, Query
from app.api.deps import get_current_user
import psycopg, os
from urllib.parse import urlparse

router = APIRouter()

def _conn():
    url=os.getenv("DATABASE_URL","postgresql+psycopg://postgres:postgres@localhost:5432/orca_db")
    if url.startswith("postgresql+psycopg://"):
        url=url.replace("postgresql+psycopg://","postgresql://")
    p=urlparse(url)
    return psycopg.connect(f"host={p.hostname or 'localhost'} port={p.port or 5432} dbname={(p.path or '/orca_db').lstrip('/')} user={p.username or 'postgres'} password={p.password or 'postgres'}")

@router.get("/history")
async def ocean_history(latitude: float, longitude: float, limit: int = 23, current_user = Depends(get_current_user)):
    conn=_conn()
    cur=conn.cursor()
    cur.execute("SELECT sst, chlorophyll, wave_height, observation_time FROM ocean_observations WHERE ST_Within(location::geometry, ST_MakeEnvelope(72.2,18.5,73.2,19.5,4326)) ORDER BY observation_time ASC LIMIT %s", (limit,))
    rows=cur.fetchall()
    conn.close()
    return {"items": [{"sst": r[0], "chlorophyll": r[1], "wave_height": r[2], "observation_time": r[3].isoformat() if r[3] else None} for r in rows]}

@router.get("/grid")
async def ocean_grid(bbox: str = Query(default="72.2,18.5,73.2,19.5"), current_user = Depends(get_current_user)):
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
