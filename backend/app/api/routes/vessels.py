"""Vessel routes - Global Fishing Watch v3 events, Maharashtra/Mumbai bbox slice.

Public read (like geospatial): the map needs vessel positions before login.
No hardcoded positions - reads vessel_tracks (GFW backfill).
"""
from fastapi import APIRouter, Query
import uuid
import psycopg
from app.database.connection import psycopg_conninfo

router = APIRouter()


@router.get("/")
async def get_vessels(
    bbox: str = Query(default="71.8,15.5,74.5,20.5", description="min_lon,min_lat,max_lon,max_lat"),
    limit: int = Query(default=50, le=200),
):
    """Live GFW fishing events in bbox. Returns newest first."""
    try:
        min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
    except Exception:
        min_lon, min_lat, max_lon, max_lat = 71.8, 15.5, 74.5, 20.5
    conn = psycopg.connect(psycopg_conninfo())
    cur = conn.cursor()
    cur.execute("""
        SELECT id::text, latitude, longitude, observation_time,
               vessel_id, vessel_name, event_type, metadata
        FROM vessel_tracks
        WHERE latitude BETWEEN %s AND %s AND longitude BETWEEN %s AND %s
        ORDER BY observation_time DESC LIMIT %s
    """, (min_lat, max_lat, min_lon, max_lon, limit))
    items = [{
        "id": r[0], "latitude": r[1], "longitude": r[2],
        "observation_time": r[3].isoformat() if r[3] else None,
        "vessel_id": r[4], "vessel_name": r[5], "event_type": r[6],
        "metadata": r[7],
    } for r in cur.fetchall()]
    conn.close()
    return {"count": len(items), "items": items,
            "source": "GFW v3 events (gateway.api.globalfishingwatch.org)",
            "request_id": str(uuid.uuid4())}
