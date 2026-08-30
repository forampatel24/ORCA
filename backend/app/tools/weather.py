"""Weather tools - deterministic."""
import psycopg
from typing import Dict, Any, Optional
from datetime import datetime, timezone

def get_weather(lat: float, lon: float, time_filter: Optional[str] = None) -> Dict[str, Any]:
    """Return nearest weather observation + forecast window."""
    # For M5 mock pipeline, return stored or fallback
    try:
        conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
        cur = conn.cursor()
        cur.execute("SELECT wind_speed, temperature, rainfall, pressure FROM weather_observations ORDER BY observation_time DESC LIMIT 1")
        r = cur.fetchone()
        conn.close()
        if r:
            return {"wind_speed": r[0], "temperature": r[1], "rainfall": r[2], "pressure": r[3], "source": "weather_observations"}
    except: pass
    # fallback mock via ingestion
    return {"wind_speed": 12.5, "temperature": 29.0, "rainfall": 0.2, "pressure": 1008, "source": "mock"}

def get_hazards(lat: float, lon: float, radius_km: float = 100) -> list:
    import psycopg
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
    cur = conn.cursor()
    cur.execute("""
        SELECT hazard_type, severity, description, ST_Distance(geometry, ST_GeographyFromText(%s))/1000 as d
        FROM marine_hazards WHERE ST_DWithin(geometry::geography, ST_GeographyFromText(%s), %s) LIMIT 5
    """, (f"POINT({lon} {lat})", f"POINT({lon} {lat})", radius_km*1000))
    rows = cur.fetchall()
    conn.close()
    return [{"type": r[0], "severity": r[1], "description": r[2], "distance_km": r[3]} for r in rows]
