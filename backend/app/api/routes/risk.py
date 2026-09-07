"""Risk routes - live deterministic assessment from Mumbai observations, no mock."""
from fastapi import APIRouter, Query
from app.analytics.risk.engine import calculate_risk
from app.schemas.risk import RiskResponse, RiskFactor
import datetime

router = APIRouter()

@router.get("/trend")
async def risk_trend(days: int = Query(default=30, le=60), latitude: float = 19.076, longitude: float = 72.877):
    """Past N days deterministic risk - same engine as /assess, per-day wind/wave + hazards."""
    import psycopg as _psycopg
    from app.database.connection import psycopg_conninfo
    from app.tools.geospatial import check_geofence
    g = check_geofence(latitude, longitude)
    inside = bool(g.get("inside_geofence") or g.get("inside_protected"))
    conn = _psycopg.connect(psycopg_conninfo())
    cur = conn.cursor()
    # weather + ocean aligned by date (noon)
    cur.execute("""
        SELECT w.observation_time::date AS d, w.wind_speed, w.rainfall, o.wave_height, o.wave_period
        FROM weather_observations w
        LEFT JOIN ocean_observations o ON o.observation_time::date = w.observation_time::date
          AND ST_Within(o.location::geometry, ST_MakeEnvelope(72.2,18.5,73.2,19.5,4326))
        WHERE ST_Within(w.location::geometry, ST_MakeEnvelope(72.2,18.5,73.2,19.5,4326))
        ORDER BY d ASC
    """)
    rows = cur.fetchall()
    # keep last N days
    rows = rows[-days:] if len(rows) > days else rows
    # hazards per day
    cur.execute("SELECT hazard_type, valid_from::date, valid_to::date FROM marine_hazards WHERE valid_to > now() - interval '60 days'")
    hazs = cur.fetchall()
    conn.close()
    items = []
    for d, wind, rain, wave, period in rows:
        has_cycl = any(h[0] == "cyclone" and h[1] <= d <= h[2] for h in hazs if h[1] and h[2])
        has_light = any(h[0] == "lightning" and h[1] <= d <= h[2] for h in hazs if h[1] and h[2])
        r = calculate_risk(wind_speed=wind or 0, wave_height=wave or 0, wave_period=period or 0, rainfall=rain or 0,
                           lightning=has_light, cyclone=has_cycl, inside_geofence=inside)
        items.append({"date": d.isoformat(), "risk_score": r["risk_score"], "risk_level": r["risk_level"], "factors": r["risk_factors"]})
    return {"count": len(items), "items": items, "source": "risk/engine.py live per-day wind/wave + marine_hazards"}

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
