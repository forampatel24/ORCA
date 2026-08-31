"""Weather tools - Mumbai-only authentic, no hardcoded mocks."""
import psycopg, structlog
from typing import Dict, Any, Optional
from app.config.mumbai import MUMBAI_BBOX
log = structlog.get_logger()

def get_weather(lat: float, lon: float, time_filter: Optional[str] = None) -> Dict[str, Any]:
    """Mumbai-only weather from DB filtered to bbox. No mock fallback."""
    try:
        conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
        cur = conn.cursor()
        cur.execute("""
            SELECT wind_speed, temperature, rainfall, pressure, observation_time, forecast_time
            FROM weather_observations
            WHERE ST_Within(location::geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326))
            ORDER BY observation_time DESC LIMIT 1
        """, (MUMBAI_BBOX[0], MUMBAI_BBOX[1], MUMBAI_BBOX[2], MUMBAI_BBOX[3]))
        r = cur.fetchone()
        conn.close()
        if r and r[0] is not None:
            return {
                "wind_speed": float(r[0]) if r[0] is not None else None,
                "temperature": float(r[1]) if r[1] is not None else None,
                "rainfall": float(r[2]) if r[2] is not None else None,
                "pressure": float(r[3]) if r[3] is not None else None,
                "observation_time": r[4].isoformat() if r[4] else None,
                "forecast_time": r[5].isoformat() if r[5] else None,
                "source": "weather_observations_mumbai_bbox", "bbox": MUMBAI_BBOX
            }
    except Exception as e:
        log.warning("weather_tool_mumbai_failed", error=str(e))
    return {"wind_speed": None, "temperature": None, "rainfall": None, "pressure": None, "source": "no_authentic_mumbai_weather", "bbox": MUMBAI_BBOX, "note": "Ingest via WeatherConnector Mumbai live API first"}

def get_hazards(lat: float, lon: float, radius_km: float = 100) -> list:
    import psycopg
    from app.config.mumbai import MUMBAI_BBOX
    # Hazards filtered to Mumbai bbox + radius from point (still Mumbai-only)
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
    cur = conn.cursor()
    cur.execute("""
        SELECT hazard_type, severity, description, ST_Distance(geometry::geography, ST_GeographyFromText(%s))/1000 as d
        FROM marine_hazards 
        WHERE ST_DWithin(geometry::geography, ST_GeographyFromText(%s), %s)
          AND ST_Within(geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326))
        LIMIT 10
    """, (f"POINT({lon} {lat})", f"POINT({lon} {lat})", radius_km*1000, MUMBAI_BBOX[0], MUMBAI_BBOX[1], MUMBAI_BBOX[2], MUMBAI_BBOX[3]))
    rows = cur.fetchall()
    conn.close()
    return [{"type": r[0], "severity": r[1], "description": r[2], "distance_km": r[3], "source": "marine_hazards_mumbai_bbox"} for r in rows]
