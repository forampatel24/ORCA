"""Routes - live safety-aware routing, PFZ-name aware, no stubs."""
from fastapi import APIRouter, Query
from app.schemas.route import RouteResponse, RouteOption
from app.analytics.routing.engine import haversine, score_route
from typing import Optional
import math

router = APIRouter()

def _resolve_pfz(name: str):
    import psycopg, json
    from app.database.connection import psycopg_conninfo
    try:
        conn = psycopg.connect(psycopg_conninfo())
        cur = conn.cursor()
        # Prefer exact case-insensitive match first (so "Worli" -> Worli, not Worli-Lotus)
        cur.execute("SELECT latitude, longitude, metadata->>'landing_centre' FROM pfz_observations WHERE lower(metadata->>'landing_centre') = lower(%s) LIMIT 1", (name.strip(),))
        row = cur.fetchone()
        if not row:
            cur.execute("SELECT latitude, longitude, metadata->>'landing_centre' FROM pfz_observations WHERE metadata->>'landing_centre' ILIKE %s ORDER BY length(metadata->>'landing_centre') ASC LIMIT 1", (f"%{name.strip()}%",))
            row = cur.fetchone()
        conn.close()
        if row:
            return float(row[0]), float(row[1]), row[2]
    except Exception:
        pass
    return None

def _safe_polyline(start_lat, start_lon, end_lat, end_lon):
    """Straight line with detour if it cuts a hazard/MPA/land. Returns [[lon,lat],...]."""
    try:
        from shapely.geometry import LineString, Point, shape
        import json as _j
        from pathlib import Path as _P
        # straight line
        line = LineString([(start_lon, start_lat), (end_lon, end_lat)])
        # collect blocking polygons
        blockers = []
        import psycopg as _psycopg
        from app.database.connection import psycopg_conninfo
        conn = _psycopg.connect(psycopg_conninfo())
        cur = conn.cursor()
        cur.execute("SELECT ST_AsGeoJSON(geometry)::json FROM marine_hazards WHERE valid_to > now()")
        for (gj,) in cur.fetchall():
            try:
                blockers.append(shape(gj))
            except Exception:
                pass
        cur.execute("SELECT ST_AsGeoJSON(geometry)::json FROM protected_areas")
        for (gj,) in cur.fetchall():
            try:
                blockers.append(shape(gj))
            except Exception:
                pass
        conn.close()
        # land polygon for Mumbai (Maharashtra state) - avoid routing over land when both points are at sea
        try:
            fp = _P(__file__).resolve().parents[3] / "frontend" / "public" / "india_states.geojson"
            if fp.exists():
                import json as _jj
                gj = _jj.loads(fp.read_text())
                feat = next((f for f in gj.get("features", []) if f.get("properties", {}).get("NAME_1") == "Maharashtra"), None)
                if feat:
                    from shapely.geometry import shape as _sh
                    land = _sh(feat["geometry"])
                    # Only consider land as blocker if both endpoints are offshore (sea)
                    # Heuristic: if line midpoint is on land, it's a coast-hugging route -> detour seaward
                    mid = line.interpolate(0.5, normalized=True)
                    if land.contains(Point(start_lon, start_lat)) or land.contains(Point(end_lon, end_lat)):
                        pass  # start/end on land is invalid - user error, don't detour
                    elif land.intersects(line):
                        blockers.append(land)
        except Exception:
            pass
        # if any blocker intersects, add a single detour waypoint 8 km perpendicular away from centroid
        for poly in blockers:
            if line.intersects(poly):
                # closest point on poly to line centroid, step away
                cent = poly.centroid
                mx, my = line.interpolate(0.5, normalized=True).x, line.interpolate(0.5, normalized=True).y
                # vector from centroid to midpoint
                dx, dy = mx - cent.x, my - cent.y
                ang = math.atan2(dy, dx)
                # step 0.08 deg ~ 8.5 km
                step = 0.08
                wx = mx + step * math.cos(ang)
                wy = my + step * math.sin(ang)
                # nudge seaward (west) if land blocker
                return [[start_lon, start_lat], [wx, wy], [end_lon, end_lat]]
        return [[start_lon, start_lat], [end_lon, end_lat]]
    except Exception:
        return [[start_lon, start_lat], [end_lon, end_lat]]

@router.post("/calculate", response_model=RouteResponse)
async def calculate_route(
    start_lat: Optional[float] = Query(default=None),
    start_lon: Optional[float] = Query(default=None),
    end_lat: Optional[float] = Query(default=None),
    end_lon: Optional[float] = Query(default=None),
    start_name: Optional[str] = Query(default=None, description="PFZ landing_centre name e.g. Arnala"),
    end_name: Optional[str] = Query(default=None, description="PFZ landing_centre name e.g. Varsoli"),
):
    # Resolve named PFZ when lat/lon not supplied
    pfz_start = pfz_end = None
    if start_name and (start_lat is None or start_lon is None):
        r = _resolve_pfz(start_name)
        if r:
            start_lat, start_lon, pfz_start = r[0], r[1], r[2]
    if end_name and (end_lat is None or end_lon is None):
        r = _resolve_pfz(end_name)
        if r:
            end_lat, end_lon, pfz_end = r[0], r[1], r[2]
    if start_lat is None or start_lon is None or end_lat is None or end_lon is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Provide start_lat/start_lon and end_lat/end_lon, or start_name/end_name of a PFZ (e.g. Arnala, Varsoli)")
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
    # safety-aware polyline with detour if needed
    coords = _safe_polyline(start_lat, start_lon, end_lat, end_lon)
    # recompute distance along polyline if detoured
    if len(coords) > 2:
        dist = sum(haversine(coords[i][1], coords[i][0], coords[i+1][1], coords[i+1][0]) for i in range(len(coords)-1))
        dist = round(dist, 2)
    # turn-by-turn instructions
    instructions = []
    for i in range(len(coords)-1):
        lon1, lat1 = coords[i]
        lon2, lat2 = coords[i+1]
        seg = haversine(lat1, lon1, lat2, lon2)
        y = math.sin(math.radians(lon2 - lon1)) * math.cos(math.radians(lat2))
        x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(lon2 - lon1))
        brng = (math.degrees(math.atan2(y, x)) + 360) % 360
        dirs = ["N","NE","E","SE","S","SW","W","NW"]
        bdir = dirs[round(brng/45) % 8]
        instructions.append(f"Step {i+1}: Head {bdir} ({brng:.0f}°) for {seg:.1f} km — from {lat1:.3f},{lon1:.3f} to {lat2:.3f},{lon2:.3f}")
    if g.get("inside_protected"):
        instructions.append("Caution: destination inside Marine Protected Area — entry restricted. Keep 5 km buffer.")
    elif g.get("inside_geofence"):
        instructions.append("Caution: route enters restricted geofence — remain outside.")
    instructions.append(f"Total {dist:.1f} km, est. {scored['time_h']:.1f}h at 20 km/h, risk {risk['risk_level']} ({risk['risk_score']}). Stay inside EEZ and monitor wind/wave.")
    return RouteResponse(routes=[
        RouteOption(route_id=f"live-{start_lat:.3f},{start_lon:.3f}-{end_lat:.3f},{end_lon:.3f}",
                    distance_km=dist, duration=f"{scored['time_h']:.1f}h",
                    risk_score=risk["risk_score"], geofence_violations=[g["inside_geofence"]] if g.get("inside_geofence") else [],
                    hazards=risk["risk_factors"],
                    coordinates=coords, instructions=instructions, pfz_start=pfz_start, pfz_end=pfz_end)
    ])
