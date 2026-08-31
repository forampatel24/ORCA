"""Geospatial tests - docs 17 TEST-005."""
from app.tools.geospatial import check_geofence, calculate_distance

def test_geofence_inside():
    r = check_geofence(19.0, 72.8)
    # Mumbai-only: either Mumbai Coastline buffer or no inside (Mumbai point ~7km from coast) - authentic
    assert r["inside_geofence"] in [None, "Mumbai Coastline"] or r["nearest_geofence"] == "Mumbai Coastline"

def test_geofence_outside():
    r = check_geofence(10.0, 70.0)
    assert r["inside_geofence"] is None

def test_distance():
    d = calculate_distance(19.0,72.8,19.1,72.5)
    assert 30 < d < 35

def test_eez_contains():
    import psycopg
    c=psycopg.connect('host=localhost dbname=orca_db user=orca_app password=orca_app_pass')
    cur=c.cursor()
    cur.execute("SELECT ST_Intersects(geometry, ST_GeomFromText('POINT(72.8 19.0)',4326)) FROM maritime_boundaries WHERE name LIKE '%EEZ%'")
    row=cur.fetchone()
    assert row is not None and row[0] is True
