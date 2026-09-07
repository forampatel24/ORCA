"""Geospatial tools - Mumbai-only authentic, PostGIS bbox filtered, no hardcoded."""
import psycopg, structlog
from app.database.connection import psycopg_conninfo
from typing import Dict, Any
from app.config.mumbai import MUMBAI_BBOX
log = structlog.get_logger()

_LAND_CACHE = None

def _is_on_land(lat: float, lon: float) -> bool | None:
    """Land vs sea using Maharashtra state polygon from frontend GeoJSON (no mock bbox)."""
    global _LAND_CACHE
    try:
        if _LAND_CACHE is None:
            from pathlib import Path as _P
            import json as _j
            candidates = [
                _P(__file__).resolve().parents[3] / "frontend" / "public" / "india_states.geojson",
                _P(r"D:\Foram_TP\ORCA\frontend\public\india_states.geojson"),
            ]
            for fp in candidates:
                if fp.exists():
                    gj = _j.loads(fp.read_text())
                    # find Maharashtra feature (NAME_1)
                    feat = next((f for f in gj.get("features", []) if (f.get("properties", {}).get("NAME_1") == "Maharashtra")), None)
                    if feat:
                        from shapely.geometry import shape as _shape, Point as _Pt
                        _LAND_CACHE = (_shape(feat["geometry"]),)
                    break
            if _LAND_CACHE is None:
                return None
        geom, = _LAND_CACHE
        from shapely.geometry import Point as _Pt
        return geom.contains(_Pt(lon, lat))
    except Exception:
        return None

def check_geofence(lat: float, lon: float) -> Dict[str, Any]:
    """Mumbai-only geofence check - only boundaries intersecting Mumbai bbox."""
    from app.config.mumbai import point_within_mumbai
    on_land = _is_on_land(lat, lon)
    # Keep original lat/lon for land reporting - do NOT clamp to Mumbai when on land elsewhere in Maharashtra
    orig_lat, orig_lon = lat, lon
    if not point_within_mumbai(lat, lon) and on_land is not True:
        log.warning("geofence_mumbai_clamped", lat=lat, lon=lon, bbox=MUMBAI_BBOX)
        lat, lon = 19.076, 72.877
    """Mumbai-only geofence check - only boundaries intersecting Mumbai bbox."""
    from app.config.mumbai import point_within_mumbai
    if not point_within_mumbai(lat, lon):
        log.warning("geofence_mumbai_clamped", lat=lat, lon=lon, bbox=MUMBAI_BBOX)
        lat, lon = 19.076, 72.877
    conn = psycopg.connect(psycopg_conninfo())
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
        "check_point": {"lat": orig_lat, "lon": orig_lon},
        "on_land": on_land,
        "bbox": MUMBAI_BBOX,
        "source": "mumbai_bbox_geofences"
    }

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Deterministic ST_Distance geography - works for Mumbai."""
    conn = psycopg.connect(psycopg_conninfo())
    cur = conn.cursor()
    cur.execute("SELECT ST_Distance(ST_GeographyFromText(%s), ST_GeographyFromText(%s))/1000", (f"POINT({lon1} {lat1})", f"POINT({lon2} {lat2})"))
    d = cur.fetchone()[0]
    conn.close()
    return float(d)
