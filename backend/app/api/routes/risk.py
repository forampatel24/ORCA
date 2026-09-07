"""Risk routes - live deterministic assessment from Mumbai observations, no mock."""
from fastapi import APIRouter
from app.analytics.risk.engine import calculate_risk
from app.schemas.risk import RiskResponse, RiskFactor
import datetime

router = APIRouter()

@router.post("/assess", response_model=RiskResponse)
async def assess_risk(latitude: float, longitude: float):
    # Live inputs from the same sources as the map - no hardcoded 0.72.
    # Each factor is taken from the latest Mumbai observation when available,
    # otherwise falls back to "missing" -> risk engine treats as 0.
    from app.tools.weather import get_weather
    from app.tools.ocean import get_ocean
    from app.tools.geospatial import check_geofence
    import psycopg as _psycopg
    from app.database.connection import psycopg_conninfo

    w = get_weather(latitude, longitude)
    o = get_ocean(latitude, longitude)
    g = check_geofence(latitude, longitude)
    # active hazard flags for this point
    has_lightning = has_cyclone = False
    try:
        conn = _psycopg.connect(psycopg_conninfo())
        cur = conn.cursor()
        cur.execute("SELECT hazard_type FROM marine_hazards WHERE valid_to > now() AND ST_DWithin(geometry::geography, ST_GeographyFromText(%s), 50000)",
                    (f"POINT({longitude} {latitude})",))
        types = [r[0] for r in cur.fetchall()]
        conn.close()
        has_lightning = any("lightning" in t for t in types)
        has_cyclone = any("cyclone" in t for t in types)
    except Exception:
        pass

    res = calculate_risk(
        wind_speed=w.get("wind_speed") or 0,
        wave_height=o.get("wave_height") or 0,
        wave_period=o.get("wave_period") or 0,
        rainfall=w.get("rainfall") or 0,
        lightning=has_lightning,
        cyclone=has_cyclone,
        inside_geofence=bool(g.get("inside_geofence") or g.get("inside_protected")),
    )
    return RiskResponse(
        risk_score=res["risk_score"],
        risk_level=res["risk_level"],
        factors=[RiskFactor(factor=f, contribution=0) for f in res["risk_factors"]],
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
