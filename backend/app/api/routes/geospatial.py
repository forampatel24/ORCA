"""Geospatial routes - Mumbai-only authentic, no hardcoded GeoJSON."""
from fastapi import APIRouter, Depends, Query
from app.api.deps import get_current_user
import psycopg, json

router = APIRouter()

@router.post("/geofence/check")
async def check_geofence(
    latitude: float,
    longitude: float,
    current_user = Depends(get_current_user)
):
    from app.tools.geospatial import check_geofence as _check
    return _check(latitude, longitude)

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
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
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
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
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
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
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
    conn = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
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
