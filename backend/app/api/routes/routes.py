"""Routes - live deterministic routing with haversine + geofence penalty, no stub distance."""
from fastapi import APIRouter
from app.schemas.route import RouteResponse, RouteOption
from app.analytics.routing.engine import haversine, score_route

router = APIRouter()

@router.post("/calculate", response_model=RouteResponse)
async def calculate_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    # Live: haversine distance + risk at destination + geofence penalty from
    # the same PostGIS checks used by /geospatial/notify.
    from app.analytics.risk.engine import calculate_risk
    from app.tools.weather import get_weather
    from app.tools.ocean import get_ocean
    from app.tools.geospatial import check_geofence
    import psycopg as _psycopg
    from app.database.connection import psycopg_conninfo

    w = get_weather(end_lat, end_lon)
    o = get_ocean(end_lat, end_lon)
    g = check_geofence(end_lat, end_lon)
    has_cyclone = False
    try:
        conn = _psycopg.connect(psycopg_conninfo())
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM marine_hazards WHERE hazard_type='cyclone' AND valid_to > now() AND ST_DWithin(geometry::geography, ST_GeographyFromText(%s), 50000)",
                    (f"POINT({end_lon} {end_lat})",))
        has_cyclone = bool(cur.fetchone())
        conn.close()
    except Exception:
        pass
    risk = calculate_risk(wind_speed=w.get("wind_speed") or 0, wave_height=o.get("wave_height") or 0,
                          lightning=False, cyclone=has_cyclone, inside_geofence=bool(g.get("inside_geofence") or g.get("inside_protected")))
    penalty = 100 if g.get("inside_protected") else (10 if g.get("inside_geofence") else 0)
    scored = score_route({"lat": start_lat, "lon": start_lon}, {"lat": end_lat, "lon": end_lon}, risk["risk_score"], penalty)
    dist = scored["distance_km"]
    return RouteResponse(routes=[
        RouteOption(route_id=f"live-{start_lat:.3f},{start_lon:.3f}-{end_lat:.3f},{end_lon:.3f}",
                    distance_km=dist, duration=f"{scored['time_h']:.1f}h",
                    risk_score=risk["risk_score"], geofence_violations=[g["inside_geofence"]] if g.get("inside_geofence") else [],
                    hazards=[h for h in [risk["risk_factors"]] if h])
    ])
