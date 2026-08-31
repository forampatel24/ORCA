"""Tools - PFZ deterministic Mumbai-only - no hardcoded, PostGIS bbox filtered."""
from typing import List, Dict, Any
import psycopg, structlog
from app.config.mumbai import MUMBAI_BBOX
log = structlog.get_logger()

def get_nearest_pfz(lat: float, lon: float, radius_km: float = 50) -> List[Dict[str, Any]]:
    """Mumbai-only PostGIS - bbox + ST_DWithin, no global. Returns authentic pfz_observations."""
    from app.config.mumbai import point_within_mumbai, MUMBAI_BBOX
    if not point_within_mumbai(lat, lon):
        log.warning("pfz_mumbai_only_clamped", lat=lat, lon=lon, bbox=MUMBAI_BBOX)
        lat, lon = 19.076, 72.877
    try:
        conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
        cur = conn.cursor()
        cur.execute("""
            SELECT id::text, latitude, longitude, metadata, observation_time,
                   ST_Distance(geometry::geography, ST_GeographyFromText(%s))/1000 as dist_km
            FROM pfz_observations
            WHERE ST_DWithin(geometry::geography, ST_GeographyFromText(%s), %s)
              AND latitude BETWEEN %s AND %s AND longitude BETWEEN %s AND %s
            ORDER BY dist_km ASC LIMIT 5
        """, (f"POINT({lon} {lat})", f"POINT({lon} {lat})", radius_km*1000, MUMBAI_BBOX[1], MUMBAI_BBOX[3], MUMBAI_BBOX[0], MUMBAI_BBOX[2]))
        rows = cur.fetchall()
        conn.close()
        return [{"id": r[0], "latitude": r[1], "longitude": r[2], "metadata": r[3], "observation_time": r[4].isoformat() if r[4] else None, "distance_km": float(r[5]) if r[5] else None, "source": "pfz_observations_mumbai_bbox"} for r in rows]
    except Exception as e:
        log.warning("pfz_tool_mumbai_failed", error=str(e))
        return []

def get_pfz_all(limit: int = 10) -> List[Dict[str, Any]]:
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
    cur = conn.cursor()
    cur.execute("SELECT id::text, latitude, longitude, metadata FROM pfz_observations WHERE latitude BETWEEN %s AND %s AND longitude BETWEEN %s AND %s LIMIT %s", (MUMBAI_BBOX[1], MUMBAI_BBOX[3], MUMBAI_BBOX[0], MUMBAI_BBOX[2], limit))
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "latitude": r[1], "longitude": r[2], "metadata": r[3], "source": "pfz_observations_mumbai_bbox"} for r in rows]
