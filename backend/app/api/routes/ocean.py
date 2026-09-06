from fastapi import APIRouter, Depends
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
