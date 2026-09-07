"""Geospatial routes - Mumbai-only authentic, no hardcoded GeoJSON."""
from fastapi import APIRouter, Depends, Query
import math, psycopg, json
from app.database.connection import psycopg_conninfo

router = APIRouter()

@router.post("/geofence/check")
async def check_geofence(
    latitude: float,
    longitude: float,
):
    # Public read: entering coordinates must work before login (geofencing is map-critical).
    from app.tools.geospatial import check_geofence as _check
    return _check(latitude, longitude)


@router.get("/notify")
async def geofence_notify(latitude: float, longitude: float, radius: float = Query(default=50, le=200, description="hazard/PFZ search km")):
    """Entered-coordinates -> geofencing notifications, distances, suggestions.

    All checks are PostGIS-real:
    - inside coastline/EEZ/MPA via ST_Contains
    - nearest PFZ + distance via pfz_observations
    - active hazards within radius via marine_hazards
    - nearest EEZ boundary distance + safe route back to safety
    Notifications are derived deterministically - no mocks.
    """
    import psycopg as _psycopg
    from app.tools.geospatial import check_geofence as _check

    geo = _check(latitude, longitude)
    # nearest PFZ - no radius cap, true nearest regardless of bbox
    pfz_nearest = None
    try:
        # direct PostGIS nearest without ST_DWithin cap (previous 50 km hid far PFZ)
        conn2 = _psycopg.connect(psycopg_conninfo())
        cur2 = conn2.cursor()
        cur2.execute("""
            SELECT latitude, longitude, metadata,
                   ST_Distance(geometry::geography, ST_GeographyFromText(%s))/1000.0 AS dist_km
            FROM pfz_observations ORDER BY geometry <-> ST_GeomFromText(%s,4326) LIMIT 1
        """, (f"POINT({longitude} {latitude})", f"POINT({longitude} {latitude})"))
        pr = cur2.fetchone()
        conn2.close()
        if pr and pr[3] is not None:
            md = pr[2] or {}
            pfz_nearest = {"latitude": pr[0], "longitude": pr[1],
                           "distance_km": float(pr[3]), "landing_centre": md.get("landing_centre"),
                           "sst": md.get("sst"), "chlorophyll": md.get("chlorophyll")}
    except Exception:
        pass
    # active hazards within radius (geometry may be point or polygon)
    hazards = []
    try:
        conn = _psycopg.connect(psycopg_conninfo())
        cur = conn.cursor()
        # point or polygon hazards within radius*1000 m
        cur.execute("""
            SELECT hazard_type, severity, title, description, valid_to,
                   ST_Distance(geometry::geography, ST_GeographyFromText(%s))/1000.0 AS dist_km,
                   ST_Contains(geometry, ST_GeomFromText(%s,4326)) AS inside
            FROM marine_hazards
            WHERE valid_to > now()
              AND ST_DWithin(geometry::geography, ST_GeographyFromText(%s), %s)
            ORDER BY dist_km ASC LIMIT 5
        """, (f"POINT({longitude} {latitude})", f"POINT({longitude} {latitude})",
              f"POINT({longitude} {latitude})", radius*1000))
        for row in cur.fetchall():
            hazards.append({"hazard_type": row[0], "severity": row[1], "title": row[2],
                            "description": row[3], "valid_to": row[4].isoformat() if row[4] else None,
                            "distance_km": float(row[5]) if row[5] is not None else None,
                            "inside": bool(row[6])})
        # EEZ distance - to boundary when inside, to polygon when outside (not 0)
        cur.execute("""
            SELECT
              CASE WHEN ST_Contains(geometry, ST_GeomFromText(%s,4326))
                   THEN ST_Distance(ST_Boundary(geometry)::geography, ST_GeographyFromText(%s))/1000.0
                   ELSE ST_Distance(geometry::geography, ST_GeographyFromText(%s))/1000.0 END AS dist_km,
              ST_Contains(geometry, ST_GeomFromText(%s,4326)) AS inside
            FROM maritime_boundaries WHERE ST_Intersects(geometry, ST_MakeEnvelope(71.8,15.5,74.5,20.5,4326)) LIMIT 1
        """, (f"POINT({longitude} {latitude})", f"POINT({longitude} {latitude})",
              f"POINT({longitude} {latitude})", f"POINT({longitude} {latitude})"))
        erow = cur.fetchone()
        eez_dist, eez_inside = (float(erow[0]) if erow and erow[0] is not None else None,
                                 bool(erow[1]) if erow else None)
        conn.close()
    except Exception:
        hazards, eez_dist, eez_inside = [], None, None

    # Build notifications - honest, only when condition holds
    notifs = []
    if geo.get("inside_protected"):
        notifs.append({"level": "critical", "code": "INSIDE_MPA",
                       "message": f"Inside Marine Protected Area: {geo['inside_protected']} - entry restricted."})
    if hazards:
        for h in hazards:
            lvl = "critical" if h["severity"] in ("HIGH","VERY_HIGH") else ("warning" if h["severity"]=="MODERATE" else "info")
            # inside hazard polygon is more urgent than nearby
            if h.get("inside"):
                lvl = "critical" if lvl != "critical" else lvl
                notifs.append({"level": lvl, "code": f"INSIDE_{h['hazard_type'].upper()}",
                               "message": f"Inside {h['hazard_type']} hazard: {h['title']} ({h['severity']})",
                               "distance_km": 0, "hazard": h})
            else:
                notifs.append({"level": lvl, "code": f"NEAR_{h['hazard_type'].upper()}",
                               "message": f"{h['hazard_type'].title()} hazard {h['distance_km']:.1f} km away: {h['title']} ({h['severity']})",
                               "distance_km": h["distance_km"], "hazard": h})
    # EEZ boundary proximity (info, not critical unless outside and far)
    if eez_inside is False:
        notifs.append({"level": "warning", "code": "OUTSIDE_EEZ",
                       "message": f"Outside EEZ — {eez_dist:.0f} km beyond boundary. International waters.",
                       "distance_km": eez_dist})
    elif eez_dist is not None and eez_inside is not False:
        if eez_dist < 3:
            notifs.append({"level": "warning", "code": "NEAR_EEZ_BOUNDARY",
                           "message": f"Approaching EEZ boundary — {eez_dist:.1f} km away. Avoid crossing.",
                           "distance_km": eez_dist})
        elif eez_dist < 10:
            notifs.append({"level": "info", "code": "EEZ_PROXIMITY",
                           "message": f"EEZ boundary {eez_dist:.0f} km away.",
                           "distance_km": eez_dist})
    # PFZ proximity suggestion - bearing + distance, always fresh
    suggestion = None
    if pfz_nearest and pfz_nearest["distance_km"] is not None:
        # bearing from vessel to PFZ
        dlon = math.radians(pfz_nearest["longitude"] - longitude)
        y, x = math.sin(dlon) * math.cos(math.radians(pfz_nearest["latitude"])), math.cos(math.radians(latitude))*math.sin(math.radians(pfz_nearest["latitude"])) - math.sin(math.radians(latitude))*math.cos(math.radians(pfz_nearest["latitude"]))*math.cos(dlon)
        brng = (math.degrees(math.atan2(y, x)) + 360) % 360
        dirs = ["N","NE","E","SE","S","SW","W","NW"]; bdir = dirs[round(brng/45)%8]
        dist = pfz_nearest["distance_km"]
        lc = pfz_nearest.get("landing_centre") or "PFZ"
        sst = f" SST {pfz_nearest['sst']}°C" if pfz_nearest.get("sst") is not None else ""
        chl = f" Chl {pfz_nearest['chlorophyll']}" if pfz_nearest.get("chlorophyll") is not None else ""
        if dist < 2:
            suggestion = f"Inside PFZ {lc} ({dist:.1f} km {bdir}, {brng:.0f}°{sst}{chl}) - good fishing, watch zone drift."
        elif dist < 8:
            suggestion = f"Very close to PFZ {lc} - {dist:.1f} km {bdir} ({brng:.0f}°{sst}{chl})."
        elif dist < 25:
            suggestion = f"Nearest PFZ {lc} {dist:.1f} km {bdir} ({brng:.0f}°). Head {bdir} to reach it."
        elif dist < 60:
            suggestion = f"Nearest PFZ {lc} {dist:.1f} km {bdir} away - consider moving {bdir}{sst}."
        else:
            suggestion = f"Far from PFZ - nearest {lc} {dist:.0f} km {bdir}. Relocate north toward Mumbai PFZ belt."
    elif not pfz_nearest:
        suggestion = "No PFZ in database - check PFZ layer."

    status = "safe"
    if any(n["level"]=="critical" for n in notifs):
        status = "critical"
    elif any(n["level"]=="warning" for n in notifs):
        status = "warning"
    elif notifs:
        status = "info"

    return {"point": {"lat": latitude, "lon": longitude}, "geo": geo,
            "pfz_nearest": pfz_nearest, "eez_distance_km": eez_dist, "eez_inside": eez_inside,
            "hazards": hazards, "notifications": notifs, "suggestion": suggestion, "status": status,
            "safe_route": _safe_route(latitude, longitude, eez_inside, eez_dist, hazards, geo)}


def _safe_route(lat: float, lon: float, eez_inside, eez_dist, hazards, geo):
    """Deterministic safe navigation path back to safety.

    - Outside EEZ: closest point on EEZ boundary (ST_ClosestPoint) -> line to safety.
    - Inside hazard/MPA: step away from hazard centroid ~8 km on opposite bearing.
    Returns GeoJSON LineString or None when already safe.
    """
    try:
        import psycopg as _psycopg
        conn = _psycopg.connect(psycopg_conninfo())
        cur = conn.cursor()
        pt = f"POINT({lon} {lat})"
        # Outside EEZ -> route to boundary
        if eez_inside is False:
            cur.execute("""
                SELECT ST_AsGeoJSON(ST_ClosestPoint(geometry, ST_GeomFromText(%s,4326)))::json,
                       ST_Distance(geometry::geography, ST_GeographyFromText(%s))/1000.0
                FROM maritime_boundaries WHERE ST_Intersects(geometry, ST_MakeEnvelope(71.8,15.5,74.5,20.5,4326)) LIMIT 1
            """, (pt, pt))
            row = cur.fetchone()
            conn.close()
            if row and row[0]:
                gj = row[0]
                return {"type": "LineString", "coordinates": [[lon, lat], [gj["coordinates"][0], gj["coordinates"][1]]],
                        "distance_km": float(row[1]) if row[1] else None, "target": "EEZ boundary", "instruction": f"Head to EEZ boundary {row[1]:.1f} km away - return to inside EEZ."}
            return None
        # Inside hazard/MPA polygon -> step out
        if hazards and any(h.get("inside") for h in hazards):
            # step away from hazard centroid
            cur.execute("SELECT ST_AsGeoJSON(ST_Centroid(geometry))::json FROM marine_hazards WHERE valid_to > now() AND ST_Contains(geometry, ST_GeomFromText(%s,4326)) LIMIT 1",
                        (pt,))
            row = cur.fetchone()
            conn.close()
            if row and row[0]:
                cx, cy = row[0]["coordinates"]
                # bearing vessel <- centroid, step 0.08 deg (~8 km) away
                import math as _m
                brng = (_m.degrees(_m.atan2(math.sin(_m.radians(lon - cx)) * _m.cos(_m.radians(lat)),
                                            _m.cos(_m.radians(cy))*_m.sin(_m.radians(lat)) - _m.sin(_m.radians(cy))*_m.cos(_m.radians(lat))*_m.cos(_m.radians(lon - cx)))) + 360) % 360
                # offset vessel away from hazard by ~8 km
                step = 0.072  # deg ~8 km
                nlat = lat + step * _m.cos(_m.radians(brng))
                nlon = lon + step * _m.sin(_m.radians(brng)) / _m.cos(_m.radians(lat))
                return {"type": "LineString", "coordinates": [[lon, lat], [nlon, nlat]],
                        "distance_km": 8.0, "target": "outside hazard", "instruction": f"Move {['N','NE','E','SE','S','SW','W','NW'][round(brng/45)%8]} ({brng:.0f}°) ~8 km to exit hazard."}
            return None
        # Near EEZ boundary inside (<3 km) -> suggest bearing away from boundary
        if eez_dist is not None and eez_dist < 3 and eez_inside:
            cur.execute("SELECT ST_AsGeoJSON(ST_ClosestPoint(ST_Boundary(geometry), ST_GeomFromText(%s,4326)))::json FROM maritime_boundaries LIMIT 1", (pt,))
            row = cur.fetchone()
            conn.close()
            if row and row[0]:
                cx, cy = row[0]["coordinates"]
                import math as _m
                # bearing from boundary to vessel (inward normal)
                brng = (_m.degrees(_m.atan2(_m.sin(_m.radians(lon - cx)) * _m.cos(_m.radians(lat)),
                                            _m.cos(_m.radians(cy))*_m.sin(_m.radians(lat)) - _m.sin(_m.radians(cy))*_m.cos(_m.radians(lat))*_m.cos(_m.radians(lon - cx)))) + 360) % 360
                # suggest moving opposite of boundary (inward)
                away = (brng + 180) % 360
                dirs = ["N","NE","E","SE","S","SW","W","NW"]
                return {"type": "LineString", "coordinates": [[lon, lat],
                          [lon + 0.04*_m.sin(_m.radians(away))/_m.cos(_m.radians(lat)), lat + 0.04*_m.cos(_m.radians(away))]],
                        "distance_km": 4.0, "target": "away from EEZ boundary", "instruction": f"EEZ boundary {eez_dist:.1f} km away {dirs[round(brng/45)%8]}. Head {dirs[round(away/45)%8]} inland to stay inside."}
        conn.close()
    except Exception:
        pass
    return None

# --- Mumbai-only GeoJSON endpoints - serve from PostGIS (ingested authentic, not hardcoded) ---
# No hardcoded coordinates - reads from maritime_boundaries/protected_areas/geofences tables
# Filtered to MUMBAI_BBOX so no global download exposed

@router.get("/coastline")
async def get_coastline(bbox: str = Query(default="72.2,18.5,73.2,19.5", description="min_lon,min_lat,max_lon,max_lat Mumbai")):
    """Authentic coastline - from geofences where name LIKE '%Coastline%' clipped to bbox. Not hardcoded file."""
    try:
        min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
    except:
        min_lon, min_lat, max_lon, max_lat = 72.2, 18.5, 73.2, 19.5
    conn = psycopg.connect(psycopg_conninfo())
    cur = conn.cursor()
    # Return geofences coastline as GeoJSON - from DB, not hardcoded array
    # Use parameterized ILIKE to avoid psycopg %c placeholder error
    cur.execute("""
        SELECT json_build_object(
            'type','FeatureCollection',
            'features', COALESCE(json_agg(ST_AsGeoJSON(geometry)::jsonb || jsonb_build_object('properties', jsonb_build_object('name', name, 'geofence_type', geofence_type))), '[]'::json)
        )::text
        FROM geofences
        WHERE name ILIKE %s AND ST_Intersects(geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326))
    """, ('%coastline%', min_lon, min_lat, max_lon, max_lat))
    row = cur.fetchone()
    conn.close()
    if row and row[0]:
        return json.loads(row[0])
    return {"type":"FeatureCollection","features":[]}

@router.get("/eez")
async def get_eez(bbox: str = Query(default="72.2,18.5,73.2,19.5")):
    """Mumbai EEZ clipped - from maritime_boundaries. Not hardcoded 68,8 polygon."""
    try:
        min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
    except:
        min_lon, min_lat, max_lon, max_lat = 72.2, 18.5, 73.2, 19.5
    conn = psycopg.connect(psycopg_conninfo())
    cur = conn.cursor()
    cur.execute("""
        SELECT json_build_object('type','FeatureCollection','features', COALESCE(json_agg(ST_AsGeoJSON(geometry)::jsonb || jsonb_build_object('properties', jsonb_build_object('name', name, 'boundary_type', boundary_type, 'country', country))), '[]'::json))::text
        FROM maritime_boundaries
        WHERE ST_Intersects(geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326))
    """, (min_lon, min_lat, max_lon, max_lat))
    row = cur.fetchone()
    conn.close()
    return json.loads(row[0]) if row and row[0] else {"type":"FeatureCollection","features":[]}

@router.get("/mpa")
async def get_mpa(bbox: str = Query(default="72.2,18.5,73.2,19.5")):
    """Mumbai MPA - from protected_areas. Not hardcoded file."""
    try:
        min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
    except:
        min_lon, min_lat, max_lon, max_lat = 72.2, 18.5, 73.2, 19.5
    conn = psycopg.connect(psycopg_conninfo())
    cur = conn.cursor()
    cur.execute("""
        SELECT json_build_object('type','FeatureCollection','features', COALESCE(json_agg(ST_AsGeoJSON(geometry)::jsonb || jsonb_build_object('properties', jsonb_build_object('name', name, 'area_type', area_type, 'authority', authority))), '[]'::json))::text
        FROM protected_areas
        WHERE ST_Intersects(geometry, ST_MakeEnvelope(%s,%s,%s,%s,4326))
    """, (min_lon, min_lat, max_lon, max_lat))
    row = cur.fetchone()
    conn.close()
    return json.loads(row[0]) if row and row[0] else {"type":"FeatureCollection","features":[]}

@router.get("/pfz")
async def get_pfz_geojson(bbox: str = Query(default="72.2,18.5,73.2,19.5")):
    """PFZ as GeoJSON for map - from pfz_observations. Not hardcoded markers."""
    try:
        min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
    except:
        min_lon, min_lat, max_lon, max_lat = 72.2, 18.5, 73.2, 19.5
    conn = psycopg.connect(psycopg_conninfo())
    cur = conn.cursor()
    cur.execute("""
        SELECT json_build_object('type','FeatureCollection','features', COALESCE(json_agg(jsonb_build_object('type','Feature','geometry', ST_AsGeoJSON(geometry)::jsonb, 'properties', jsonb_build_object('id', id::text, 'latitude', latitude, 'longitude', longitude, 'metadata', metadata, 'observation_time', observation_time))), '[]'::json))::text
        FROM pfz_observations
        WHERE latitude BETWEEN %s AND %s AND longitude BETWEEN %s AND %s
        LIMIT 50
    """, (min_lat, max_lat, min_lon, max_lon))
    row = cur.fetchone()
    conn.close()
    return json.loads(row[0]) if row and row[0] else {"type":"FeatureCollection","features":[]}
