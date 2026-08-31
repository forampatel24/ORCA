"""Ocean tools - Mumbai-only authentic, no hardcoded mocks."""
import psycopg
import structlog
from app.config.mumbai import MUMBAI_BBOX
log = structlog.get_logger()

def get_ocean(lat: float, lon: float):
    """Authentic Mumbai ocean observations from DB filtered to Mumbai bbox. No mock fallback."""
    from app.config.mumbai import MUMBAI_BBOX
    try:
        conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
        cur = conn.cursor()
        # Mumbai bbox only - not global
        cur.execute("""
            SELECT sst, chlorophyll, wave_height, wave_period, current_speed, observation_time
            FROM ocean_observations
            WHERE ST_Within(location::geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326))
            ORDER BY observation_time DESC LIMIT 1
        """, (MUMBAI_BBOX[0], MUMBAI_BBOX[1], MUMBAI_BBOX[2], MUMBAI_BBOX[3]))
        r = cur.fetchone()
        conn.close()
        if r and r[0] is not None:
            return {
                "sst": float(r[0]) if r[0] is not None else None,
                "chlorophyll": float(r[1]) if r[1] is not None else None,
                "wave_height": float(r[2]) if r[2] is not None else None,
                "wave_period": float(r[3]) if r[3] is not None else None,
                "current_speed": float(r[4]) if r[4] is not None else None,
                "observation_time": r[5].isoformat() if r[5] else None,
                "source": "ocean_observations_mumbai_bbox",
                "bbox": MUMBAI_BBOX
            }
    except Exception as e:
        log.warning("ocean_tool_mumbai_db_failed", error=str(e))
    # No hardcoded mock - return explicit empty with provenance per AGENTS safety
    return {"sst": None, "chlorophyll": None, "wave_height": None, "source": "no_authentic_mumbai_ocean_data", "bbox": MUMBAI_BBOX, "note": "Ingest via OceanConnector Mumbai bbox first"}
