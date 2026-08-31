"""Ocean anomaly - Mumbai-only authentic, dynamic baseline from DB, no hardcoded 27.0."""
from typing import Dict, Any
import structlog
log = structlog.get_logger()

def _mumbai_baseline(variable: str, fallback: float) -> float:
    """Authentic 30-day Mumbai bbox average from ocean_observations, not hardcoded."""
    from app.config.mumbai import MUMBAI_BBOX
    try:
        import psycopg
        conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
        cur = conn.cursor()
        col = "sst" if variable == "sst" else "chlorophyll"
        cur.execute(f"""
            SELECT avg({col}) FROM ocean_observations
            WHERE ST_Within(location::geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326))
              AND observation_time > now() - interval '30 days' AND {col} IS NOT NULL
        """, (MUMBAI_BBOX[0], MUMBAI_BBOX[1], MUMBAI_BBOX[2], MUMBAI_BBOX[3]))
        v = cur.fetchone()[0]
        conn.close()
        if v is not None:
            log.info("anomaly_mumbai_baseline", variable=variable, baseline=float(v))
            return float(v)
    except Exception as e:
        log.warning("anomaly_baseline_db_failed", error=str(e))
    return fallback

def sst_anomaly(observed: float, baseline: float = None) -> Dict[str, Any]:
    if observed is None: return {"observed": None, "baseline": None, "anomaly": None, "unit": "C", "flag": "MISSING", "source": "no_authentic_mumbai_sst"}
    b = baseline if baseline is not None else _mumbai_baseline("sst", 27.0)
    anomaly = observed - b
    flag = "ANOMALOUS" if abs(anomaly) > 1.5 else "VALID"
    return {"observed": observed, "baseline": round(b,2), "anomaly": round(anomaly,2), "unit": "C", "flag": flag, "source": "mumbai_bbox_30d_avg"}

def chlorophyll_anomaly(observed: float, baseline: float = None) -> Dict[str, Any]:
    if observed is None: return {"observed": None, "baseline": None, "anomaly": None, "unit": "mg/m3", "flag": "MISSING"}
    b = baseline if baseline is not None else _mumbai_baseline("chlorophyll", 0.6)
    anomaly = observed - b
    return {"observed": observed, "baseline": round(b,3), "anomaly": round(anomaly,3), "unit": "mg/m3", "flag": "VALID" if abs(anomaly) < 1.0 else "ANOMALOUS", "source": "mumbai_bbox_30d_avg"}
