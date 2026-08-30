"""Tools - PFZ deterministic - docs 06_AGENT_SPEC Marine Data Agent tools."""
from typing import List, Dict, Any, Optional
import psycopg

def get_nearest_pfz(lat: float, lon: float, radius_km: float = 50) -> List[Dict[str, Any]]:
    """Deterministic PostGIS - no LLM."""
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
    cur = conn.cursor()
    cur.execute("""
        SELECT id::text, latitude, longitude, metadata, observation_time,
               ST_Distance(geometry, ST_GeographyFromText(%s))/1000 as dist_km
        FROM pfz_observations
        WHERE ST_DWithin(geometry, ST_GeographyFromText(%s), %s)
        ORDER BY dist_km ASC LIMIT 5
    """, (f"POINT({lon} {lat})", f"POINT({lon} {lat})", radius_km*1000))
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "latitude": r[1], "longitude": r[2], "metadata": r[3], "observation_time": r[4].isoformat() if r[4] else None, "distance_km": r[5]} for r in rows]

def get_pfz_all(limit: int = 10) -> List[Dict[str, Any]]:
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
    cur = conn.cursor()
    cur.execute("SELECT id::text, latitude, longitude, metadata FROM pfz_observations LIMIT %s", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "latitude": r[1], "longitude": r[2], "metadata": r[3]} for r in rows]
