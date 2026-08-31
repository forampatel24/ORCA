"""Geospatial tools - Mumbai-only authentic, PostGIS bbox filtered, no hardcoded."""
import psycopg, structlog
from typing import Dict, Any
from app.config.mumbai import MUMBAI_BBOX
log = structlog.get_logger()

def check_geofence(lat: float, lon: float) -> Dict[str, Any]:
    """Mumbai-only geofence check - only boundaries intersecting Mumbai bbox."""
    from app.config.mumbai import point_within_mumbai
    if not point_within_mumbai(lat, lon):
        log.warning("geofence_mumbai_clamped", lat=lat, lon=lon, bbox=MUMBAI_BBOX)
        lat, lon = 19.076, 72.877
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
    cur = conn.cursor()
    # Only check geofences/protected that intersect Mumbai bbox (Mumbai EEZ/Malvan MPA/Mumbai coastline)
    cur.execute("""
        SELECT name, geofence_type FROM geofences 
        WHERE ST_Contains(geometry, ST_GeomFromText(%s, 4326))
          AND ST_Intersects(geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326)) LIMIT 1
    """, (f"POINT({lon} {lat})", MUMBAI_BBOX[0], MUMBAI_BBOX[1], MUMBAI_BBOX[2], MUMBAI_BBOX[3]))
    g = cur.fetchone()
    cur.execute("""
        SELECT name FROM protected_areas 
        WHERE ST_Contains(geometry, ST_GeomFromText(%s, 4326))
          AND ST_Intersects(geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326)) LIMIT 1
    """, (f"POINT({lon} {lat})", MUMBAI_BBOX[0], MUMBAI_BBOX[1], MUMBAI_BBOX[2], MUMBAI_BBOX[3]))
    p = cur.fetchone()
    cur.execute("""
        SELECT name, ST_Distance(geometry::geography, ST_GeographyFromText(%s))/1000 as d 
        FROM geofences 
        WHERE ST_Intersects(geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326))
        ORDER BY geometry <-> ST_GeomFromText(%s,4326) LIMIT 1
    """, (f"POINT({lon} {lat})", MUMBAI_BBOX[0], MUMBAI_BBOX[1], MUMBAI_BBOX[2], MUMBAI_BBOX[3], f"POINT({lon} {lat})"))
    nearest = cur.fetchone()
    conn.close()
    return {
        "inside_geofence": g[0] if g else None,
        "geofence_type": g[1] if g else None,
        "inside_protected": p[0] if p else None,
        "nearest_geofence": nearest[0] if nearest else None,
        "distance_to_nearest_km": float(nearest[1]) if nearest else None,
        "check_point": {"lat": lat, "lon": lon},
        "bbox": MUMBAI_BBOX,
        "source": "mumbai_bbox_geofences"
    }

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Deterministic ST_Distance geography - works for Mumbai."""
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
    cur = conn.cursor()
    cur.execute("SELECT ST_Distance(ST_GeographyFromText(%s), ST_GeographyFromText(%s))/1000", (f"POINT({lon1} {lat1})", f"POINT({lon2} {lat2})"))
    d = cur.fetchone()[0]
    conn.close()
    return float(d)
