"""Geospatial tools - deterministic PostGIS - docs 06 Geospatial Agent."""
import psycopg
from typing import Dict, Any

def check_geofence(lat: float, lon: float) -> Dict[str, Any]:
    """Check whether point inside restricted/protected."""
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
    cur = conn.cursor()
    # geofences
    cur.execute("SELECT name, geofence_type FROM geofences WHERE ST_Contains(geometry, ST_GeomFromText(%s, 4326)) LIMIT 1", (f"POINT({lon} {lat})",))
    g = cur.fetchone()
    # protected
    cur.execute("SELECT name FROM protected_areas WHERE ST_Contains(geometry, ST_GeomFromText(%s, 4326)) LIMIT 1", (f"POINT({lon} {lat})",))
    p = cur.fetchone()
    # distance to nearest geofence
    cur.execute("SELECT name, ST_Distance(geometry::geography, ST_GeographyFromText(%s))/1000 as d FROM geofences ORDER BY geometry <-> ST_GeomFromText(%s,4326) LIMIT 1", (f"POINT({lon} {lat})", f"POINT({lon} {lat})"))
    nearest = cur.fetchone()
    conn.close()
    return {
        "inside_geofence": g[0] if g else None,
        "geofence_type": g[1] if g else None,
        "inside_protected": p[0] if p else None,
        "nearest_geofence": nearest[0] if nearest else None,
        "distance_to_nearest_km": nearest[1] if nearest else None,
        "check_point": {"lat": lat, "lon": lon}
    }

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Deterministic ST_Distance geography."""
    import psycopg
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
    cur = conn.cursor()
    cur.execute("SELECT ST_Distance(ST_GeographyFromText(%s), ST_GeographyFromText(%s))/1000", (f"POINT({lon1} {lat1})", f"POINT({lon2} {lat2})"))
    d = cur.fetchone()[0]
    conn.close()
    return float(d)
